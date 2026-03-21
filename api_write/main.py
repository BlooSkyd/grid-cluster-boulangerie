from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import sys
import codecs

app = FastAPI(title="API Écriture Pains")

class Pain(BaseModel):
    nom: str
    cuisson: str
    prix: float
    poids: int

def get_conn():
    return psycopg2.connect("host=db_master dbname=boulangerie user=user password=pass")

@app.post("/pains")
def create_pain(pain: Pain):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pains (nom, cuisson, prix, poids) VALUES (%s, %s, %s, %s)",
        (pain.nom, pain.cuisson, pain.prix, pain.poids)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"Le pain '{pain.nom}' a été ajouté."}

@app.delete("/pains/{pain_id}")
def delete_pain(pain_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM pains WHERE id = %s", (pain_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Pain supprimé avec succès."}