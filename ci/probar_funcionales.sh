#!/bin/sh
# Espera a que la app responda en localhost:5000 y corre las pruebas funcionales.
for i in $(seq 1 60); do
  python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/login', timeout=3)" 2>/dev/null && break
  sleep 2
done
mkdir -p reports
python -m pytest tests/functional -v --junitxml=reports/funcionales.xml
