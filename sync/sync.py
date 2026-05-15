#!/usr/bin/env python3
import os
import time
import json
import logging
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import psycopg2

logging.basicConfig(level=logging.INFO)

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092")
TOPIC = os.environ.get("TOPIC", "commandes")

def ensure_topic():
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP.split(","))
    topics = admin.list_topics()
    if TOPIC not in topics:
        topic = NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)
        try:
            admin.create_topics([topic])
            logging.info("Created topic %s", TOPIC)
        except Exception as e:
            logging.warning("Topic creation issue: %s", e)
    admin.close()

def get_db_conn(host):
    return psycopg2.connect(
        host=host,
        port=int(os.environ.get("DB_PORT", 5432)),
        user=os.environ.get("DB_USER", "user"),
        password=os.environ.get("DB_PASSWORD", "pass"),
        dbname=os.environ.get("DB_NAME", "boulangerie"),
    )

def process_event(ev):
    op = ev.get("operation")
    entity = ev.get("entity")
    if op == "create":
        data = ev.get("data", {})

        # Création d'une commande (événement explicitement fourni avec entity='commande')
        if entity == "commande":
            # data attendu: {"ref_id_pain": <int>, "qte": <int>} ; on enregistre sur le master et on met à jour la compta sur la slave
            try:
                ref_id_pain = int(data.get("ref_id_pain"))
            except Exception:
                logging.warning(f"Exception when casting ref_id_pain ({data.get('ref_id_pain')}) to int(), input class: {data.get('ref_id_pain').__class__}")
                ref_id_pain = None
            try:
                qte = int(data.get("qte", 0))
            except Exception:
                logging.warning(f"Exception when casting qte ({data.get('qte')}) to int(), input class: {data.get('qte').__class__}")
                qte = 0

            if ref_id_pain is None or qte <= 0:
                logging.warning("Commande create: ref_id_pain manquant ou qte invalide %s", data)
            else:
                nom_pain = None
                prix_unit = 0.0
                # Récupérer prix unitaire depuis le master et insérer la commande
                conn_master = None
                cursor_master = None
                try:
                    conn_master = get_db_conn(os.environ.get("DB_HOST", "db_master"))
                    cursor_master = conn_master.cursor()
                    cursor_master.execute("SELECT nom, prix FROM pains WHERE id_pain = %s", (ref_id_pain,))
                    row = cursor_master.fetchone()
                    if row:
                        nom_pain, prix_unit = row[0], float(row[1])
                    # Insérer la commande sur le master
                    cursor_master.execute("INSERT INTO commandes (ref_id_pain, qte) VALUES (%s, %s)", (ref_id_pain, qte))
                    conn_master.commit()
                    cursor_master.close()
                    conn_master.close()
                    logging.info("Inserted commande ref=%s qte=%s on master", ref_id_pain, qte)
                except Exception as e:
                    logging.exception("Failed to insert commande on master: %s", e)
                finally:
                    if cursor_master:
                        cursor_master.close()
                    if conn_master:
                        conn_master.close()

                # Mettre à jour la table compta sur la slave en upsert
                try:
                    conn_slave = get_db_conn(os.environ.get("DB_SLAVE_HOST", "db_slave"))
                    cursor_slave = conn_slave.cursor()
                    add_total = qte * prix_unit
                    # Utilise ON CONFLICT pour créer ou mettre à jour l'agrégat
                    cursor_slave.execute(
                        "INSERT INTO compta (ref_id_pain, nom, prix_total, nb_cmd) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT (ref_id_pain) DO UPDATE SET prix_total = compta.prix_total + EXCLUDED.prix_total, nb_cmd = compta.nb_cmd + EXCLUDED.nb_cmd",
                        (ref_id_pain, nom_pain or 'unknown', add_total, qte),
                    )
                    conn_slave.commit()
                    cursor_slave.close()
                    conn_slave.close()
                    logging.info("Updated compta on slave for ref=%s add_total=%s", ref_id_pain, add_total)
                except Exception as e:
                    logging.exception("Failed to update compta on slave: %s", e)
    else:
        logging.warning("Unknown operation %s", op)

def wipe_and_sync_slave():
    """Truncate `compta` on slave and rebuild it from master aggregated data."""
    logging.info("#"*50)
    logging.info("# START - Wipe and sync slave")
    logging.info("#"*50)
    try:
        conn_master = get_db_conn(os.environ.get("DB_HOST", "db_master"))
        cur_master = conn_master.cursor()
        # Aggregate ventes per pain from master commandes joined with pains
        cur_master.execute(
            """
            SELECT p.id_pain, p.nom, COALESCE(SUM(c.qte * p.prix),0) AS prix_total, COALESCE(SUM(c.qte),0) AS nb_cmd
            FROM pains p
            LEFT JOIN commandes c ON c.ref_id_pain = p.id_pain
            GROUP BY p.id_pain, p.nom
            """
        )
        rows = cur_master.fetchall()
        cur_master.close()
        conn_master.close()

        conn_slave = get_db_conn(os.environ.get("DB_SLAVE_HOST", "db_slave"))
        cur_slave = conn_slave.cursor()
        # Clear compta then insert aggregated rows
        cur_slave.execute("TRUNCATE TABLE compta")
        for r in rows:
            ref_id_pain, nom, prix_total, nb_cmd = r
            cur_slave.execute(
                "INSERT INTO compta (ref_id_pain, nom, prix_total, nb_cmd) VALUES (%s, %s, %s, %s)",
                (ref_id_pain, nom or 'unknown', prix_total, nb_cmd),
            )
        conn_slave.commit()
        cur_slave.close()
        conn_slave.close()
        logging.info("Wiped and synced compta on slave (%d rows)", len(rows))
        logging.info("#"*50)
        logging.info("# OK - Wiping and syncing slave over and completed")
        logging.info("#"*50)
    except Exception as e:
        logging.exception("Failed initial wipe_and_sync_slave: %s", e)

def main():
    while True:
        try:
            ensure_topic()
            break
        except Exception as e:
            logging.info("Kafka not ready yet: %s", e)
            time.sleep(5)
    # Initial full sync: wipe slave compta and rebuild from master
    wipe_and_sync_slave()
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP.split(","),
        auto_offset_reset="earliest",
        group_id="sync-group",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    logging.info("Started consumer on %s", TOPIC)
    for msg in consumer:
        try:
            ev = msg.value
            process_event(ev)
        except Exception as e:
            logging.exception("Error processing message: %s", e)

if __name__ == "__main__":
    main()

# TODO :
"""
Ajouter une logique de wipall de slave afin de synchro from scratch depuis master
"""