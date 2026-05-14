# Utilisation d'une image Python légère
FROM python:3.11-slim

# Installation des dépendances système pour psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python
RUN pip install --no-cache-dir fastapi uvicorn psycopg2-binary

# Copie du code source
COPY read-api.py .

# Exposition du port
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "read-api:app", "--host", "0.0.0.0", "--port", "8000"]