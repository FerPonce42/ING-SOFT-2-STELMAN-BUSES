# Guía del equipo – Lab 05 (Pruebas unitarias y dobles de prueba)

Curso: Ingeniería de Software II (D.Sc. Edgar Sarmiento). Equipo: Fernando Ponce (líder), Ruth Benique, Nicol Rocha, Arnolsmith Tacca, Iair Suico, Maricielo Luna.

## 1. Qué hay que hacer, en una frase

Cada integrante elige un módulo del proyecto y escribe pruebas automáticas para tres capas: **dominio** (reglas puras), **repositorio** (el SQL) y **servicios** (con dobles/mocks en lugar de la BD real). Todo se trabaja con commits ligados a issues en la rama `development`, y al final se entregan el repo, un reporte de ejecución y un reporte de cobertura.

Las tres capas ya existen en el código:

| Capa del PDF | Dónde vive en el proyecto | Qué se prueba |
|---|---|---|
| Dominio | `app/services/validaciones.py` y las constantes/reglas de cada `*_service.py` (estados, gravedades, año mínimo del bus, etc.) | Que las reglas acepten lo válido y rechacen lo inválido (`ReglaNegocioError`). Sin BD. |
| Repositorio | `app/repositories/*.py` | Que cada método mande el SQL y los parámetros correctos, usando una conexión falsa (`MagicMock`). |
| Servicios de aplicación | `app/services/*_service.py` | Que el servicio llame bien a su repositorio (mock), haga commit/rollback y lance los errores esperados. |

## 2. Reparto (propuesto, el líder puede cambiarlo)

Cada persona crea **solo sus archivos** de prueba, así git no genera conflictos. Si el archivo de servicio ya existe (auth, bus, caja), se **amplía**, no se reemplaza.

| Integrante | Módulo | Dominio | Repositorio | Servicio |
|---|---|---|---|---|
| Fernando Ponce | Acceso + Rutas | `tests/domain/test_acceso_rutas.py` | `tests/repositories/test_cuenta_ruta_repository.py` | `tests/services/test_auth_service.py` (existe) y `test_ruta_service.py` |
| Ruth Benique | Buses | `tests/domain/test_buses.py` | `tests/repositories/test_bus_repository.py` | `tests/services/test_bus_service.py` (existe) |
| Nicol Rocha | Choferes | `tests/domain/test_choferes.py` | `tests/repositories/test_chofer_repository.py` | `tests/services/test_chofer_service.py` |
| Arnolsmith Tacca | Incidencias | `tests/domain/test_incidencias.py` | `tests/repositories/test_incidencia_repository.py` | `tests/services/test_incidencia_service.py` |
| Iair Suico | Caja | `tests/domain/test_caja.py` | `tests/repositories/test_caja_repository.py` | `tests/services/test_caja_service.py` (existe) |
| Maricielo Luna | Reportes | `tests/domain/test_reportes.py` | `tests/repositories/test_esquema_repository.py` | `tests/services/test_reporte_service.py` |

Archivos de código que **no** se tocan salvo que una prueba falle por un error real (y en ese caso, avisar al líder): todo `app/web/`, `app/templates/`, `app/static/`, `db/`.

## 3. Preparar tu computadora (una sola vez)

```bash
git clone <URL-del-repo>
cd ING-SOFT-2-STELMAN-BUSES
git checkout development
python -m venv .venv
.venv\Scripts\activate          # Windows   (Linux/Mac: source .venv/bin/activate)
pip install -r requirements-dev.txt
pytest                          # debe terminar en verde
```

No necesitas Docker ni la base de datos para las pruebas unitarias.

## 4. Flujo de trabajo para cada tarea

1. En GitHub Project, mueve tu tarea de TO-DO a **IN PROGRESS** (el issue queda abierto).
2. `git checkout development` y `git pull`.
3. Escribe la prueba primero (TDD): ejecútala y verifica que falla o que pasa por la razón correcta; arregla lo mínimo; refactoriza una vez.
4. Commit con mensaje descriptivo y el número del issue: `Agrega pruebas de validación de fecha. Fix #12`.
5. `git pull --rebase` y luego `git push origin development`.
6. Si algo falló en la validación del líder, tu tarea pasa a **FIX VALIDATION**; al terminar, a **DONE** y cierra el issue.

Buen mensaje de commit: dice qué hiciste en infinitivo o presente, corto, sin "cambios", "arreglos" ni "wip".

## 5. Cómo escribir una prueba (con setUp/tearDown, como pide la rúbrica)

Usamos clases `unittest.TestCase`. `pytest` las corre igual y `coverage` las mide igual. Cada prueba sigue el patrón **Inicializar, Ejecutar, Verificar**.

**Dominio** (`tests/domain/`):

```python
import unittest

from app.errors import ReglaNegocioError
from app.services import validaciones as v


class TextoRequeridoTest(unittest.TestCase):
    def setUp(self):
        self.etiqueta = "La placa"

    def test_texto_vacio_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            v.texto_requerido("   ", self.etiqueta)

    def test_recorta_espacios(self):
        self.assertEqual(v.texto_requerido("  abc ", self.etiqueta), "abc")
```

**Repositorio** (`tests/repositories/`): la conexión es falsa, así que no se toca ninguna BD.

```python
import unittest
from unittest.mock import MagicMock

from app.repositories.base import BaseRepository


class BaseRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = BaseRepository(self.conn)

    def test_all_devuelve_lista_de_filas(self):
        self.cur.fetchall.return_value = ({"id": 1},)
        self.assertEqual(self.repo._all("SELECT 1"), [{"id": 1}])
        self.cur.execute.assert_called_once_with("SELECT 1", ())
```

**Servicio con dobles** (`tests/services/`): el repositorio es un `Mock`.

```python
import unittest
from unittest.mock import Mock

from app.services.bus_service import BusService


class BusServiceTest(unittest.TestCase):
    def setUp(self):
        self.buses = Mock()
        self.buses.existe_placa.return_value = False
        self.buses.crear.return_value = 10
        self.rutas = Mock()
        self.rutas.exigir_ruta_activa.return_value = 3
        self.servicio = BusService(self.buses, self.rutas, id_almacen_por_defecto=5)

    def test_registrar_confirma_la_transaccion(self):
        self.assertEqual(self.servicio.registrar(1, "abc-123", "2024", "2"), 10)
        self.buses.commit.assert_called_once()
```

Cada prueba que escribas también va en la tabla de casos (ver `docs/PLANTILLA_CASOS_DE_PRUEBA.md`).

## 6. Reportes (los corre el líder al final, pero cualquiera puede probar)

```bash
pytest -v --junitxml=reports/reporte_ejecucion.xml     # ¿pasó o falló cada prueba?
coverage run -m pytest                                  # mide qué código ejecutaron las pruebas
coverage report                                         # tabla en la terminal
coverage html                                           # reporte navegable en htmlcov/index.html
```

Para el entregable se guarda una captura de la terminal de `pytest -v` (reporte de ejecución) y de `htmlcov/index.html` (reporte de cobertura).

## 7. Checklist del PDF

| # | Requisito del PDF | Estado |
|---|---|---|
| 1 | Proyecto web en lenguaje orientado a objetos | Listo (Python/Flask) |
| 2 | Repo en GitHub con ramas `main` y `development` | `development`: líder |
| 3 | Framework xUnit importado | Listo (`unittest` + `pytest`) |
| 4 | Herramienta de cobertura importada | Listo (`coverage` en `requirements-dev.txt`) |
| 5 | Framework de mocking importado | Listo (`unittest.mock`) |
| 6 | Código y pruebas separados | Listo (`app/` y `tests/`) |
| 7 | GitHub Project con plantilla Kanban | Líder |
| 8 | Columnas TO-DO, CURRENT ITERATION, IN PROGRESS, FIX VALIDATION, DONE | Líder |
| 9 | Tareas con nombre, descripción, responsable, etiqueta (`unit test`/`enhancement`) y duración | Líder |
| 10 | Tareas asignadas y convertidas en Issues | Líder |
| 11 | Entorno local configurado | Cada uno |
| 12 | Pruebas de dominio con tabla de casos y TDD | Cada uno |
| 13 | Pruebas de repositorio | Cada uno |
| 14 | Pruebas de servicios con mocks | Cada uno |
| 15 | Refactorización | Cada uno |
| 16 | Commits descriptivos con `Fix #n` en `development` | Cada uno |
| 17 | Tareas a DONE e issues cerrados | Cada uno |
| 18 | Reporte de ejecución | Líder |
| 19 | Reporte de cobertura | Líder |
| 20 | Entrega: repo + reportes | Líder |
