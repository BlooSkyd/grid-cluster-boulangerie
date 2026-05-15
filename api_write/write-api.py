from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import time
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="API Écriture Commandes")

class Commande(BaseModel):
    ref_id_pain: int
    qte: int

logger = logging.getLogger("write-api")
KAFKA_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092")
TOPIC = os.environ.get("TOPIC", "commandes")

# Lazily created singleton producer. Avoid creating the producer at import-time
_producer = None

def get_producer(max_retries: int = 5, retry_backoff: float = 2.0) -> KafkaProducer:
    global _producer
    if _producer is not None:
        return _producer

    servers = [s.strip() for s in KAFKA_SERVERS.split(",") if s.strip()]
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting to connect to Kafka brokers {servers} (attempt {attempt})")
            _producer = KafkaProducer(
                bootstrap_servers=servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            # force metadata fetch to detect connection issues early
            _producer.bootstrap_connected()
            logger.info("Connected to Kafka brokers")
            return _producer
        except NoBrokersAvailable as e:
            last_exc = e
            logger.warning(f"No Kafka brokers available (attempt {attempt}): {e}")
            if attempt < max_retries:
                time.sleep(retry_backoff)
    # If we reach here, re-raise the last exception to let caller handle it
    raise last_exc

@app.post("/commande")
def create_commande(commande: Commande):
    if commande.qte <= 0:
        raise HTTPException(status_code=422, detail="qte doit être un entier strictement positif")

    else:
        payload = commande.dict()
        event = {"operation": "create", "entity": "commande", "data": payload}
        try:
            prod = get_producer()
            prod.send(TOPIC, event)
            prod.flush()
        except NoBrokersAvailable:
            raise HTTPException(status_code=503, detail="Kafka brokers not available")
        return {"message": f"Événement de création de commande envoyé pour ref_id_pain '{commande.ref_id_pain}'", "ref_id_pain": commande.ref_id_pain, "qte":commande.qte}