# Projet GRID EPISEN SI ING3
**Authors:**
- Clement Taurand Wartelle
- Adrien Dos Santos

**Description:**
> Dans un cluster conteneurisé réaliser le schéma d'archi donné en consigne
> Simple local infra (Kafka + Postgres master/slave + sync)

## Quick run

**1. Build and start everything (single VM):**
```bash
docker-compose up --build -d
```

**2. Write a commandes (POST will produce to Kafka):**
```bash
curl -X POST http://localhost:8001/commande -H 'Content-Type: application/json' -d '{"ref_id":4,"qte":2}'
```
Check topic content (inside container):
```bash
/usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic commandes --from-beginning
```

**3. Read via read API (reads from slave DB):**
Get top 3 best sales
```bash
curl http://localhost:8002/top
```
Get info of precise bread (use `%20` if you want to have a space, name not case-sensitive)
```bash
curl http://localhost:8002/search/{name}
```
## Informations
**Architecture:**

![Technical architecture schema](./architecture.svg)


**Data model:**

![Data model schema](./data-model.svg)