# Pruebas de seguridad y de API

## Pruebas de seguridad con OWASP ZAP (#53)

**Qué hace:** escanea la aplicación web con OWASP ZAP (modo *baseline*) y guarda un reporte. Corre solo, sin intervención manual, como una etapa del pipeline de Jenkins en cada commit.

**Cómo funciona:**
1. Se levanta la app con `docker compose up -d --build`.
2. El script `pruebas_seguridad/zap_baseline.sh` lanza el contenedor oficial de ZAP (`ghcr.io/zaproxy/zaproxy:stable`) dentro de la misma red de Docker que la app y la escanea en `http://web:5000`.
3. Los reportes se guardan en `reports/zap/` (`zap_baseline.html`, `.json` y `.md`) y Jenkins los archiva como artefactos.
4. El script termina con éxito si ZAP no falla; las advertencias (código 2) no rompen el pipeline.

**Etapa en el pipeline:** `Pruebas de seguridad (OWASP ZAP)` del Jenkinsfile.

**Cómo ejecutarlo a mano:**
```bash
docker compose up -d --build
bash pruebas_seguridad/zap_baseline.sh
```

**Resultado del primer escaneo (18 endpoints):**

| Riesgo | Alertas |
|---|---|
| Alto | 0 |
| Medio | 2 (falta Content Security Policy y cabecera anti-clickjacking) |
| Bajo | 7 |
| Informativo | 4 |

El escaneo es sin sesión iniciada, por lo que no recorre el panel privado.

## Pruebas de API con Postman y Newman (#54)

(Pendiente: se completa cuando esté lista la colección y la API de Nicol.)
