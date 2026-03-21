curl -X POST "http://localhost:8001/pains" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data-binary '{"nom": "Boule tradition", "cuisson": "Bien cuite", "prix": 4.0, "poids": 1250}'