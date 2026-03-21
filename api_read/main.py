from fastapi import FastAPI
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="API Lecture Pains")

def get_conn():
    # Connexion au SLAVE (Lecture seule)
    return psycopg2.connect("host=db_slave dbname=boulangerie user=user password=pass")

@app.get("/pains")
def get_all_pains():
    conn = get_conn()
    # RealDictCursor permet d'avoir les noms des colonnes dans la réponse JSON
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM pains ORDER BY id DESC")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

@app.get("/pains/search")
def search_pains(nom: str):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM pains WHERE nom ILIKE %s", (f'%{nom}%',))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results