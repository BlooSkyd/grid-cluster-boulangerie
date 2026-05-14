from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
from kafka import KafkaProducer
import uuid

app = FastAPI(title="API Écriture Pains (producer)")

class Pain(BaseModel):
    nom: str
    cuisson: str
    prix: float
    poids: int

KAFKA_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka1:9092")
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVERS.split(","),
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

@app.post("/pains")
def create_pain(pain: Pain):
    pid = str(uuid.uuid4())
    payload = pain.dict()
    payload["id"] = pid
    event = {"operation": "create", "data": payload}
    producer.send("pains", event)
    producer.flush()
    return {"message": f"Événement envoyé pour '{pain.nom}'", "id": pid}


@app.delete("/pains/{pain_id}")
def delete_pain(pain_id: str):
    # delete by UUID
    event = {"operation": "delete", "id": pain_id}
    producer.send("pains", event)
    producer.flush()
    return {"message": "Événement de suppression envoyé."}