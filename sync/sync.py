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
TOPIC = os.environ.get("TOPIC", "pains")

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
        # Création d'un pain
        if entity == "pain" or (data.get("nom") is not None and entity is None):
            for host in (os.environ.get("DB_HOST", "db_master"), os.environ.get("DB_SLAVE_HOST", "db_slave")):
                try:
                    conn = get_db_conn(host)
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO pains (nom, cuisson, prix, poids) VALUES (%s,%s,%s,%s)",
                        (data.get("nom"), data.get("cuisson"), data.get("prix"), data.get("poids")),
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    logging.info("Inserted pain %s into %s", data.get("nom"), host)
                except Exception as e:
                    logging.exception("Failed insert on %s: %s", host, e)

        # Création d'une commande (événement explicitement fourni avec entity='commande')
        if entity == "commande":
            # data attendu: {"ref_id": <int>, "qte": <int>} ; on enregistre sur le master et on met à jour la compta sur la slave
            try:
                ref_id = int(data.get("ref_id"))
            except Exception:
                ref_id = None
            try:
                qte = int(data.get("qte", 0))
            except Exception:
                qte = 0

            if ref_id is None or qte <= 0:
                logging.warning("Commande create: ref_id manquant ou qte invalide %s", data)
            else:
                nom_pain = None
                prix_unit = 0.0
                # Récupérer prix unitaire depuis le master et insérer la commande
                connm = None
                curm = None
                try:
                    connm = get_db_conn(os.environ.get("DB_HOST", "db_master"))
                    curm = connm.cursor()
                    curm.execute("SELECT nom, prix FROM pains WHERE id = %s", (ref_id,))
                    row = curm.fetchone()
                    if row:
                        nom_pain, prix_unit = row[0], float(row[1])
                    # Insérer la commande sur le master
                    curm.execute("INSERT INTO commandes (ref_id, qte) VALUES (%s, %s)", (ref_id, qte))
                    connm.commit()
                    logging.info("Inserted commande ref=%s qte=%s on master", ref_id, qte)
                except Exception as e:
                    logging.exception("Failed to insert commande on master: %s", e)
                finally:
                    if curm:
                        curm.close()
                    if connm:
                        connm.close()

                # Mettre à jour la table compta sur la slave en upsert
                conn_s = None
                curs = None
                try:
                    conn_s = get_db_conn(os.environ.get("DB_SLAVE_HOST", "db_slave"))
                    curs = conn_s.cursor()
                    add_total = qte * prix_unit
                    # Utilise ON CONFLICT pour créer ou mettre à jour l'agrégat
                    curs.execute(
                        "INSERT INTO compta (ref_id, nom, prix_total, nb_cmd) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT (ref_id) DO UPDATE SET prix_total = compta.prix_total + EXCLUDED.prix_total, nb_cmd = compta.nb_cmd + EXCLUDED.nb_cmd",
                        (ref_id, nom_pain or 'unknown', add_total, qte),
                    )
                    conn_s.commit()
                    logging.info("Updated compta on slave for ref=%s add_total=%s qte=%s", ref_id, add_total, qte)
                except Exception as e:
                    logging.exception("Failed to update compta on slave: %s", e)
                finally:
                    if curs:
                        curs.close()
                    if conn_s:
                        conn_s.close()
    elif op == "delete":
        pid = ev.get("id")
        name = ev.get("nom") or (ev.get("data") or {}).get("nom")
        if pid is None and not name:
            logging.warning("Delete event without id or name")
            return
        for host in (os.environ.get("DB_HOST", "db_master"), os.environ.get("DB_SLAVE_HOST", "db_slave")):
            try:
                conn = get_db_conn(host)
                cur = conn.cursor()
                if pid is not None:
                    cur.execute("DELETE FROM pains WHERE id = %s", (pid,))
                else:
                    cur.execute("DELETE FROM pains WHERE nom = %s", (name,))
                conn.commit()
                cur.close()
                conn.close()
                logging.info("Deleted on %s id=%s name=%s", host, pid, name)
            except Exception as e:
                logging.exception("Failed delete on %s: %s", host, e)
    elif op == "update":
        data = ev.get("data", {})
        pid = data.get("id")
        name = data.get("nom")
        for host in (os.environ.get("DB_HOST", "db_master"), os.environ.get("DB_SLAVE_HOST", "db_slave")):
            try:
                conn = get_db_conn(host)
                cur = conn.cursor()
                if pid is not None:
                    cur.execute(
                        "UPDATE pains SET nom=%s, cuisson=%s, prix=%s, poids=%s WHERE id=%s",
                        (data.get("nom"), data.get("cuisson"), data.get("prix"), data.get("poids"), pid),
                    )
                else:
                    cur.execute(
                        "UPDATE pains SET cuisson=%s, prix=%s, poids=%s WHERE nom=%s",
                        (data.get("cuisson"), data.get("prix"), data.get("poids"), name),
                    )
                conn.commit()
                cur.close()
                conn.close()
                logging.info("Updated on %s id=%s name=%s", host, pid, name)
            except Exception as e:
                logging.exception("Failed update on %s: %s", host, e)
    else:
        logging.warning("Unknown operation %s", op)

def main():
    while True:
        try:
            ensure_topic()
            break
        except Exception as e:
            logging.info("Kafka not ready yet: %s", e)
            time.sleep(2)

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
