#!/usr/bin/env bash
# Pruebas de API con Postman + Newman contra la app (docker compose).
# Requisito: la app debe estar arriba con "docker compose up -d --build".
# Uso:  bash pruebas_api/newman_run.sh
set -u
cd "$(dirname "$0")/.."

OBJETIVO="${API_OBJETIVO:-http://web:5000}"   # servicio web dentro de la red de docker compose
SALIDA="reports/newman"
IMAGEN="postman/newman:alpine"

mkdir -p "$SALIDA"
chmod 777 "$SALIDA"

ID_WEB="$(docker compose ps -q web)"
if [ -z "$ID_WEB" ]; then
  echo "ERROR: el servicio web no esta arriba. Ejecuta primero: docker compose up -d --build"
  exit 1
fi
RED="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$ID_WEB" | awk '{print $1}')"
RUTA="$(pwd -W 2>/dev/null || pwd)"

echo "Ejecutando la coleccion contra $OBJETIVO en la red $RED ..."
MSYS_NO_PATHCONV=1 docker run --rm --network "$RED" \
  -v "$RUTA:/etc/newman:rw" \
  "$IMAGEN" run pruebas_api/stelman_api.postman_collection.json \
  -e pruebas_api/stelman_local.postman_environment.json \
  --env-var "baseUrl=$OBJETIVO" \
  --reporters cli,junit \
  --reporter-junit-export "$SALIDA/newman.xml"
CODIGO=$?

echo "Codigo de salida de Newman: $CODIGO"
echo "Reporte JUnit en $SALIDA/newman.xml"
exit "$CODIGO"
