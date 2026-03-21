#!/bin/bash
set -e

# Création de l'utilisateur de réplication
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER replication_user WITH REPLICATION PASSWORD 'replicapass';
EOSQL

# Exécution du script de création de table et peuplage
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init_data.sql

# Configuration des droits d'accès pour le Slave
echo "host replication replication_user 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"