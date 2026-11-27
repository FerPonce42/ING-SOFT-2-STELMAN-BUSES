#!/usr/bin/env bash
# Escaneo de seguridad automatizado con OWASP ZAP (baseline) contra la app de Stelman Buses.
# Requisito: la app debe estar arriba con "docker compose up -d --build".
# Uso:  bash pruebas_seguridad/zap_baseline.sh
# En Jenkins se ejecuta como una etapa del pipeline (ver docs/readme/maricielo.md).

set -u
cd "$(dirname "$0")/.."

OBJETIVO="${ZAP_OBJETIVO:-http://web:5000}"   # nombre del servicio web dentro de la red de docker compose
SALIDA="reports/zap"
IMAGEN="ghcr.io/zaproxy/zaproxy:stable"

mkdir -p "$SALIDA"
chmod 777 "$SALIDA"   # ZAP escribe como otro usuario dentro del contenedor

# Red de docker compose donde corre el servicio "web"
ID_WEB="$(docker compose ps -q web)"
if [ -z "$ID_WEB" ]; then
  echo "ERROR: el servicio web no esta arriba. Ejecuta primero: docker compose up -d --build"
  exit 1
fi
RED="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' "$ID_WEB" | awk '{print $1}')"

# Ruta absoluta (en Git Bash de Windows usa formato C:/...)
RUTA="$(pwd -W 2>/dev/null || pwd)"

echo "Escaneando $OBJETIVO en la red $RED ..."
MSYS_NO_PATHCONV=1 docker run --rm --network "$RED" \
  -v "$RUTA/$SALIDA:/zap/wrk:rw" \
  "$IMAGEN" zap-baseline.py \
  -t "$OBJETIVO" \
  -r zap_baseline.html \
  -J zap_baseline.json \
  -w zap_baseline.md
CODIGO=$?

# zap-baseline: 0 = sin alertas, 1 = hay FAIL, 2 = solo WARN, otro = error del escaneo
echo "Codigo de salida de ZAP: $CODIGO"
echo "Reportes en $SALIDA (zap_baseline.html, .json, .md)"
if [ "$CODIGO" -eq 0 ] || [ "$CODIGO" -eq 2 ]; then
  exit 0
fi
exit 1
