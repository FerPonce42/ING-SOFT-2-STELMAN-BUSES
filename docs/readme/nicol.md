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

---

## 3. Análisis Estático con SonarQube en CI/CD

Dentro del pipeline en Jenkins, la etapa de calidad de código ejecuta `pytest` con cobertura en formato XML (`coverage.xml`) y envía los resultados a **SonarQube** (`sonar-scanner`) para auditar:

- **Bugs y vulnerabilidades:** Detección estática de fallos de lógica, manejo inseguro de credenciales o tokens y excepciones sin controlar.
- **Code Smells y deuda técnica:** Cumplimiento de convenciones de estilo, complejidad ciclomática y duplicación de código en los módulos `app/` y `tests/`.
- **Cobertura de pruebas (Code Coverage):** Verificación de líneas y ramas cubiertas por la suite unitaria antes de aprobar el *Quality Gate* y continuar hacia el despliegue.
