# Pruebas de rendimiento con JMeter — Stelman Buses

**Responsable:** Tacca Chambilla, Arnolsmith Anderson (Arleondo)  
**Rama de trabajo:** `feature/jmeter-jenkins-integracion`  
**Issues asociados:** `#59` (endpoint `GET /api/v1/caja`) y `#60` (JMeter integrado con Jenkins)

---

## 1. Qué hace

Mide el rendimiento de la API de caja de Stelman Buses con **Apache JMeter**. El plan `pruebas_rendimiento/plan_api_caja.jmx` simula usuarios concurrentes que primero inician sesión en `POST /api/v1/login`, extraen el token y luego consultan `GET /api/v1/caja`. Cada petición valida que la respuesta sea HTTP 200. El endpoint `GET /api/v1/caja` también es parte de esta entrega y está en `app/web/api_v1.py`.

El plan está parametrizado, así que el mismo archivo sirve en local y en Jenkins:

| Parámetro | Valor por defecto | Uso |
| :--- | :--- | :--- |
| `host` | `localhost` | Servidor de la aplicación (en Jenkins: `web`) |
| `port` | `5000` | Puerto de la aplicación |
| `threads` | `500` | Usuarios concurrentes (en Jenkins: `100`) |
| `rampup` | `10` | Segundos para levantar todos los usuarios |
| `usuario`, `clave` | — | Credenciales del login; en Jenkins vienen de la credencial `jmeter-api-credentials`, nunca del repositorio |

## 2. Cómo se ejecuta

**En Jenkins:** es la etapa `9. Pruebas de Rendimiento (JMeter)` del `Jenkinsfile`. Corre JMeter sin ventana (modo `-n`) dentro de un contenedor `alpine/jmeter`, conectado a la red del despliegue, y publica el reporte HTML como artefacto en `reports/jmeter/`.

**En local** (con la aplicación arriba con `docker compose up -d --build`):

```bash
jmeter -n -t pruebas_rendimiento/plan_api_caja.jmx \
  -Jhost=localhost -Jport=5000 \
  -Jusuario=aperez_sup -Jclave=stelman123 \
  -Jthreads=100 -Jrampup=10 \
  -l resultados.jtl -e -o reporte_html
```

## 3. Resultado

Pruebas con 100, 300 y 500 usuarios (tiempos en milisegundos). Los resultados completos están en `pruebas_rendimiento/resultados_*_usuarios.csv`.

| Usuarios | Muestras | Promedio login | Promedio listar caja | Error % | Rendimiento (peticiones/s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 100 | 200 | 91 ms | 32 ms | 0 % | 20.0 |
| 300 | 600 | 103 ms | 47 ms | 0 % | 59.9 |
| 500 | 1000 | 1581 ms | 1874 ms | 0 % | 63.6 |

Con 100 y 300 usuarios la API responde en menos de 110 ms de promedio. Con 500 usuarios el tiempo de respuesta sube a cerca de 1.7 s de promedio, pero no hubo ningún error: todas las peticiones terminaron con HTTP 200.
