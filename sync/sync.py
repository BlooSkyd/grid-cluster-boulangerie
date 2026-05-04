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

def get_db_conn():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "db_master"),
        port=int(os.environ.get("DB_PORT", 5432)),
        user=os.environ.get("DB_USER", "user"),
        password=os.environ.get("DB_PASSWORD", "pass"),
        dbname=os.environ.get("DB_NAME", "boulangerie"),
    )

def process_event(ev):
    op = ev.get("operation")
    if op == "create":
        data = ev.get("data", {})
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO pains (nom, cuisson, prix, poids) VALUES (%s,%s,%s,%s)",
            (data.get("nom"), data.get("cuisson"), data.get("prix"), data.get("poids")),
        )
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Inserted pain %s", data.get("nom"))
    elif op == "delete":
        pid = ev.get("id")
        if pid is None:
            logging.warning("Delete event without id")
            return
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM pains WHERE id = %s", (pid,))
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Deleted id %s", pid)
    elif op == "update":
        data = ev.get("data", {})
        pid = data.get("id")
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE pains SET nom=%s, cuisson=%s, prix=%s, poids=%s WHERE id=%s",
            (data.get("nom"), data.get("cuisson"), data.get("prix"), data.get("poids"), pid),
        )
        conn.commit()
        cur.close()
        conn.close()
        logging.info("Updated id %s", pid)
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
