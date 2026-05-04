#!/bin/bash
set -e

echo "Waiting for master (db_master) to be ready..."
until pg_isready -h db_master -U user; do
	sleep 1
done

export PGPASSWORD=${PGPASSWORD:-replicapass}

if [ -z "$(ls -A /var/lib/postgresql/data 2>/dev/null)" ]; then
	echo "No data directory found, performing base backup from master..."
	rm -rf /var/lib/postgresql/data/*
	pg_basebackup -h db_master -D /var/lib/postgresql/data -U replication_user -vP -R
	chown -R postgres:postgres /var/lib/postgresql/data
	chmod 700 /var/lib/postgresql/data
fi

echo "Starting postgres (slave)..."
exec postgres
