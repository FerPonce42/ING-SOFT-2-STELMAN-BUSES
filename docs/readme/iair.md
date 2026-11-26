# Documentación — Pruebas Funcionales (Selenium) y Gestión de Issues

Responsable: **Iair Alejandro Suico Cornejo** (`@iairalejandro`)

Issues asociados: `#62` (pruebas funcionales en Jenkins) y `#63` (issues automáticos ante fallos del pipeline).

\---

## 1\. Capturas de la aplicación

Esta sección muestra las funcionalidades de Stelman Buses, tomadas con la aplicación en ejecución en `http://localhost:5000`. Las imágenes están en `docs/readme/img/`.

|Pantalla|Captura|
|-|-|
|Inicio de sesión|!\[Login](img/login.png)|
|Panel principal del supervisor|!\[Panel](img/panel.png)|
|Módulo Buses|!\[Buses](img/buses.png)|
|Módulo Choferes|!\[Choferes](img/choferes.png)|
|Módulo Caja (registrar recaudación)|!\[Caja](img/caja.png)|
|Módulo Incidencias|!\[Incidencias](img/incidencias.png)|
|Reportes (exportar documentación en Excel)|!\[Reportes](img/reportes.png)|

\---

## 2\. Pruebas funcionales con Selenium

Las pruebas automatizan un navegador real (Chrome) que inicia sesión como supervisor y recorre cada módulo igual que lo haría una persona. Están escritas con `unittest` y se ejecutan con `pytest`. Los casos se diseñaron con clases de equivalencia y valores límite, y cada método de prueba cubre un solo caso (`test\_cpNN\_...`).

Hay 44 casos en total, repartidos así:

|Archivo|Módulo|Casos|
|-|-|:-:|
|`tests/functional/test\_acceso\_rutas.py`|Inicio de sesión y rutas protegidas|8|
|`tests/functional/test\_buses.py`|Buses|10|
|`tests/functional/test\_caja.py`|Caja (registrar recaudación)|4|
|`tests/functional/test\_choferes.py`|Choferes|3|
|`tests/functional/test\_incidencias.py`|Incidencias disciplinarias y operativas|11|
|`tests/functional/test\_reportes.py`|Reportes (exportar Excel)|8|

El archivo `tests/functional/conftest.py` concentra la configuración común. Cuando existe la variable `STELMAN\_HEADLESS=1`, todos los navegadores se abren sin ventana, algo necesario porque Jenkins no tiene pantalla. También define el `driver` que usa `test\_caja.py`, con la sesión iniciada y el formulario de caja a la vista.

Un detalle técnico que costó resolver: los campos `<input type="date">` no se pueden llenar con `send\_keys` de forma fiable en Chrome, porque el texto se interpreta según el idioma del navegador. Por eso las fechas se asignan directamente con JavaScript, y así la prueba funciona igual en cualquier navegador.

### Ejecución en local

Con la aplicación levantada (`docker compose up --build`), desde la raíz del repositorio:

```
py -m pip install selenium pytest
py -m pytest tests/functional -v
```

Para ejecutarlas sin ventana, como lo hace Jenkins:

```
set STELMAN\_HEADLESS=1
py -m pytest tests/functional -v
```

Resultado de la última ejecución local: **44 pasaron, 0 fallaron, 5 min 10 s**

!\[Resultado de pytest](img/resultado\_pytest.png)

\---

## 3\. Integración con Jenkins (etapa 6)

El `Jenkinsfile` tiene una etapa `6. Pruebas Funcionales (Selenium)` que corre después del despliegue con Docker, porque necesita la aplicación ya levantada.

Como Jenkins corre dentro de un contenedor y no tiene navegador, la etapa construye una imagen aparte (`Dockerfile.selenium`) con Python, Chromium y las dependencias de pruebas. Ese contenedor comparte la red del contenedor `web`, así que las pruebas acceden a la aplicación en `localhost:5000` sin cambiar ninguna URL. Antes de empezar, el script `ci/probar\_funcionales.sh` espera a que la aplicación responda y luego ejecuta `pytest tests/functional`.

El reporte `reports/funcionales.xml` se copia fuera del contenedor y se publica con `junit`, de modo que el resultado queda visible en el historial de cada ejecución. Si alguna prueba falla, la etapa falla y el pipeline se marca como fallido.

\---

## 4\. Gestión de issues automática

Cuando cualquier etapa del pipeline falla, el bloque `post { failure }` del `Jenkinsfile` ejecuta `ci/crear\_issue\_fallo.py`. El script usa solo la biblioteca estándar de Python y llama a la API de GitHub para crear un issue en el repositorio con:

* el nombre de la etapa que falló y el número de build,
* la rama y el commit,
* el enlace al log de la consola de Jenkins,
* la mención a todos los integrantes del equipo, de modo que GitHub les envía la notificación.

El token de GitHub no está en el repositorio. Se guarda en Jenkins como credencial de tipo *Secret text* con el identificador `github-token`, y el pipeline lo entrega al script mediante la variable `GITHUB\_TOKEN`. Si además se define `SLACK\_WEBHOOK\_URL`, el script envía el aviso también a Slack.

Para el seguimiento, el issue creado se puede agregar al GitHub Project para su seguimiento, por lo que aparece en la columna inicial del tablero y sigue el mismo flujo que el resto de tareas (TO-DO, CURRENT ITERATION, IN PROGRESS, FIX VALIDATION y DONE).

\---

## 5\. Trazabilidad

|Entrega|Issue|Pull request|
|-|-|-|
|Pruebas funcionales con Selenium en modo headless|#62|#66|
|Etapa de Selenium en Jenkins e issue automático ante fallos|#62, #63|#71|



