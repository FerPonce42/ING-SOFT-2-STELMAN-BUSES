# Stelman Buses

Sistema de gestión de flota (buses, choferes, incidencias, caja) para supervisores de ruta.
Flask + MariaDB. Se levanta con un solo comando, sin XAMPP.

## Levantarlo

Requisito: Docker Desktop.

```bash
docker compose up --build
```

- App: http://localhost:5000
- Usuario de prueba: `aperez_sup` / `stelman123` (solo desarrollo, lo crea `db/02_seed_dev.sql`)
- BD para DBeaver/Workbench: `localhost:3307`, usuario `stelman`, clave `stelman`

Los scripts de `db/` solo se ejecutan la **primera vez** (volumen vacío). Si cambias el esquema
y quieres recargarlo desde cero: `docker compose down -v && docker compose up --build`.

## Estructura (y cómo repartirse el trabajo)

```
app/
  web/            # controladores (Blueprints): reciben el request, llaman al servicio, devuelven HTML
  services/       # reglas de negocio y validaciones (sin SQL, sin Flask) -> lo que se testea con mocks
  repositories/   # todo el SQL, una clase por agregado
  templates/ static/
  container.py    # arma servicios con la conexión del request
db/               # 01_schema.sql (dump), 02_seed_dev.sql (datos de desarrollo)
tests/services/   # pruebas unitarias con unittest.mock (sin BD)
tests/integration/# flujo completo contra BD real
```

| Módulo     | web/           | services/            | repositories/               |
|------------|----------------|----------------------|-----------------------------|
| Acceso     | auth.py        | auth_service.py      | cuenta_repository.py        |
| Dashboard / rutas / sitio público | panel.py, publico.py | ruta_service.py | ruta_repository.py |
| Buses      | buses.py       | bus_service.py       | bus_repository.py           |
| Choferes   | personal.py    | chofer_service.py    | chofer_repository.py        |
| Incidencias| incidencias.py | incidencia_service.py| incidencia_repository.py    |
| Caja       | caja.py        | caja_service.py      | caja_repository.py          |
| Reportes   | reportes.py    | reporte_service.py   | esquema_repository.py       |

Cada fila es independiente: dos personas pueden trabajar en filas distintas sin tocar los mismos archivos.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest                                  # unitarias (no necesitan BD)
RUN_INTEGRATION=1 pytest                # + integración (BD corriendo: docker compose up db)
```

Para integración fuera de Docker: `DB_HOST=127.0.0.1 DB_PORT=3307 RUN_INTEGRATION=1 pytest`.

## Variables de entorno

`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`, `ALMACEN_POR_DEFECTO`
(ver `.env.example`; docker-compose ya trae valores de desarrollo).

## Deuda técnica conocida

- Las eliminaciones siguen siendo enlaces GET (`/eliminar_...`); lo correcto es POST + token CSRF.
- Registrar mantenimientos de buses (tabla `mantenimiento`) aún no tiene pantalla; hoy solo se muestra el último.
- No hay gestión de supervisores/cuentas ni asignación de supervisor a ruta desde la app (se hace en BD).
