Simple local infra (Kafka + Postgres master/slave + sync)

Quick run

1. Build and start everything (single VM):

```bash
docker-compose up --build -d
```

2. Write a pain (POST will produce to Kafka):

```bash
curl -X POST http://localhost:8001/pains -H 'Content-Type: application/json' -d '{"nom":"Baguette Test","cuisson":"Normale","prix":1.5,"poids":250}'
```

3. Read via read API (reads from slave DB):

```bash
curl http://localhost:8002/pains
```

What was added

- Docker Compose: added Zookeeper + 3 Kafka brokers, `sync` service; adjusted Postgres master/slave wiring.
- `api_write`: now publishes create/delete events to Kafka (topic `pains`).
- `sync/`: consumer that reads events and updates master Postgres.
- `postgres/setup-slave.sh`: helper to bootstrap standby with `pg_basebackup`.

Notes

- This setup keeps things minimal for a single small VM. Tune JVM/heap and Postgres memory for production.
- The `sync` consumer creates the Kafka topic if missing.
Projet GRID EPISEN SI ING3

Clement Taurand Wartelle
Adrien Dos Santos

Description: Dans un cluster conteneurisé réaliser le schéma d'archi donné en consigne