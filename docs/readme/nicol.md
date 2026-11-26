# Documentación Técnica — API REST, Pruebas Unitarias y SonarQube

Responsable: **Nicol Fernanda Rocha Alvis** (`@NicolFer`)

---

## 1. Servicios REST v1 y Documentación Swagger

Se implementó el Blueprint `api_v1` en `app/web/api_v1.py` (registrado en `app/__init__.py` con exención de CSRF para clientes externos) bajo el prefijo `/api/v1`.

### Documentación OpenAPI / Swagger

- **Interfaz interactiva (Swagger UI):** `GET /api/v1/docs`
- **Especificación OpenAPI 3.0.3:** `GET /api/v1/openapi.json`

### Endpoints implementados

| Método | Ruta | Autenticación | Descripción | Respuestas |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/login` | Pública | Valida `usuario` y `password` en formato JSON mediante `AuthService` y emite un token Bearer firmado con HMAC-SHA256 (`exp` de 1 hora). | `200 OK` (`{"token": "..."}`), `401 Unauthorized` |
| `GET` | `/api/v1/choferes` | `Bearer <token>` | Devuelve en formato JSON la lista de choferes asignados a la ruta del supervisor autenticado usando `ChoferService.panel()`. | `200 OK` (`[...]`), `401 Unauthorized` |

---

## 2. Pruebas Unitarias (`pytest` + `mocking`)

Las pruebas unitarias validan la lógica de negocio, repositorios y endpoints REST sin depender de una instancia activa de MariaDB ni contenedores Docker, aislando dependencias con `unittest.mock` (`MagicMock`) y `monkeypatch`.

### Suites principales

- `tests/test_api_v1.py`: Pruebas de los endpoints `POST /api/v1/login`, `GET /api/v1/choferes`, verificación/expiración de tokens HMAC, `/api/v1/openapi.json` y `/api/v1/docs`.
- `tests/services/test_chofer_service.py`: Reglas de negocio del módulo de choferes.
- `tests/repositories/test_chofer_repository.py`: Consultas y mapeo de datos de choferes con conexión mockeada.

### Ejecución local y cobertura

```bash
# Ejecutar solo las pruebas unitarias de la API v1
python -m pytest tests/test_api_v1.py -v

# Ejecutar toda la suite unitaria (excluyendo Selenium) con reporte de cobertura
python -m pytest --ignore=tests/functional --cov=app --cov-report=xml --cov-report=term-missing
```

Resultado de ejecución: **440 pruebas aprobadas** (`12 skipped` correspondientes a integración con BD).

---

## 3. Análisis Estático con SonarQube e Integración en Jenkins

### Configuración del proyecto (`sonar-project.properties`)

Se configuró el archivo `sonar-project.properties` en la raíz del repositorio para analizar el paquete `app` e integrar el reporte de cobertura de Python (`coverage.xml`):

```properties
sonar.projectKey=stelman-buses
sonar.projectName=STELMAN-BUSES
sonar.projectVersion=1.0
sonar.sources=app
sonar.tests=tests
sonar.test.inclusions=tests/**
sonar.python.version=3.12
sonar.python.coverage.reportPaths=coverage.xml
sonar.sourceEncoding=UTF-8
```

### Integración en el Pipeline CI/CD (`Jenkinsfile`)

Etapa configurada para ejecutarse en Jenkins tras las pruebas unitarias, generando el reporte XML de cobertura y validando el *Quality Gate* en SonarQube:

```groovy
stage('SonarQube Analysis') {
    steps {
        withSonarQubeEnv('SonarQube') {
            sh '''
                python -m coverage run -m pytest --ignore=tests/functional
                python -m coverage xml
                sonar-scanner
            '''
        }
    }
}

stage('Quality Gate') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

### Resultados del Análisis Estático (SonarQube)

| Métrica | Resultado | Calificación / Estado |
| :--- | :--- | :--- |
| **Quality Gate** | **Passed** (`OK`) | Aprobado |
| **Security (Vulnerabilities)** | **0** abiertas | `A` |
| **Reliability (Bugs)** | **0** abiertos | `A` |
| **Maintainability (Code Smells)** | **0** abiertos | `A` |
| **Security Hotspots** | **0** | `A` |
| **Coverage (Cobertura de código)** | **88.0%** (943 / 1,071 líneas) | Supera umbral mínimo (80%) |
| **Duplications (Duplicación)** | **0.8%** (en 8.4k líneas) | Óptimo (< 3%) |
