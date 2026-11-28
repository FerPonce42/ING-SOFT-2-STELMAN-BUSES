# Pruebas de seguridad y de API

## Pruebas de seguridad con OWASP ZAP (#53)

**Qué hace:** escanea la aplicación web con OWASP ZAP (modo *baseline*) y guarda un reporte. Corre solo, sin una intervención manual, como una etapa del pipeline de Jenkins en cada commit.

**Cómo funciona:**
1. Se levanta la app con `docker compose up -d --build`.
2. El script `pruebas_seguridad/zap_baseline.sh` lanza el contenedor oficial de ZAP (`ghcr.io/zaproxy/zaproxy:stable`) dentro de la misma red de Docker que la app y la escanea en `http://web:5000`.
3. Los reportes se guardan en `reports/zap/` (`zap_baseline.html`, `.json` y `.md`) y Jenkins los archiva como artefactos.
4. El script termina con éxito si ZAP no falla; las advertencias (código 2) no rompen el pipeline.

**Etapa en el pipeline:** `Pruebas de seguridad (OWASP ZAP)` (archivo `pruebas_seguridad/stage_zap.groovy`).

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

Se armó una colección en Postman que prueba la API `/api/v1` y se ejecuta con Newman desde la terminal. Así no hay que abrir Postman a mano y puede correr sola en Jenkins.

**Qué revisa la colección** (8 requests y 28 pruebas):

| Request | Código HTTP | Tiempo | Valor de negocio |
|---|---|---|---|
| `POST /api/v1/login` con datos correctos | 200 | menos de 2 s | devuelve un token |
| `POST /api/v1/login` con clave incorrecta | 401 | menos de 2 s | no devuelve token |
| `GET /api/v1/buses` | 200 con token, 401 sin token | menos de 2 s | la placa no está vacía ni repetida, y el año es válido |
| `GET /api/v1/choferes` | 200 con token, 401 sin token | menos de 2 s | el nombre no está vacío y no hay ids repetidos |
| `GET /api/v1/caja` | 200 con token, 401 sin token | menos de 2 s | el monto es mayor o igual a 0 y cada recaudación tiene fecha |

**Cómo funciona:**
1. Primero se hace el login y el token se guarda solo en una variable.
2. Las demás requests usan ese token en la cabecera `Authorization: Bearer`.
3. Cada una también se prueba sin token para comprobar que responde 401.

**Archivos** (carpeta `pruebas_api/`):
- `stelman_api.postman_collection.json`: la colección.
- `stelman_local.postman_environment.json`: las variables (`baseUrl`, `usuario` y `password`).
- `newman_run.sh`: corre Newman con Docker, dentro de la misma red que la app.
- `stage_newman.groovy`: la etapa `Pruebas de API (Postman + Newman)` para el Jenkinsfile.

**Cómo correrlo a mano:**
```bash
docker compose up -d --build
bash pruebas_api/newman_run.sh
```
El resultado queda en `reports/newman/newman.xml` y la etapa de Jenkins lo publica como reporte de pruebas.

**Resultado:** la colección se ejecutó contra la API real (login, buses, choferes y caja) y pasaron las 28 pruebas.

**Pendiente:** ver correr las etapas 7 (ZAP) y 8 (Newman) dentro de Jenkins.
