from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from kafka import KafkaProducer
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="API Écriture Commandes")

class Commande(BaseModel):
    ref_id: int
    qte: int

KAFKA_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092") # a revoir les broker ne sont pas tous utilisé
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS.split(","),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

@app.post("/commandes")
def create_commande(commande: Commande):
    if commande.qte <= 0:
        raise HTTPException(status_code=422, detail="qte doit être un entier strictement positif")

    else:
        payload = commande.dict()
        event = {"operation": "create", "entity": "commande", "data": payload}
        producer.send("commandes", event)
        producer.flush()
        return {"message": f"Événement de création de commande envoyé pour ref_id '{commande.ref_id}'", "ref_id": commande.ref_id}

@app.post("/pains")
def create_pain(pain: Pain):
    pid = str(uuid.uuid4())
    payload = pain.dict()
    payload["id"] = pid
    event = {"operation": "create", "data": payload}
    producer.send("pains", event)
    producer.flush()
    return {"message": f"Événement envoyé pour '{pain.nom}'", "id": pid}

