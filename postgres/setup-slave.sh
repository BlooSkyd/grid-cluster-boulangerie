#!/bin/bash
set -e

# Initialise la base master (création de tables et peuplement)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-entrypoint-initdb.d/init_slavee.sql

echo "Slave init complete"