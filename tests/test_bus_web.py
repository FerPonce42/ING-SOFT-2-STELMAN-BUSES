import inspect
from unittest.mock import MagicMock

import pytest

from app import container, create_app
from app.errors import ReglaNegocioError
from app.web import buses


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as test_client:
        with test_client.session_transaction() as sess:
            sess["usuario"] = "supervisor_test"
            sess["id"] = 1
        yield test_client


# ---------- Refactor Issue #44: métodos HTTP explícitos ----------
def test_ruta_desasignar_declara_methods_explicitamente():
    # Arrange
    fuente = inspect.getsource(buses.desasignar)

    # Act & Assert
    assert 'methods=["GET"]' in fuente


def test_ruta_desasignar_rechaza_post(client):
    # Act
    respuesta = client.post("/panel/buses/eliminar/10")

    # Assert
    assert respuesta.status_code == 405


# ---------- Flujo de desasignación ----------
def test_ruta_desasignar_ejecuta_servicio_y_redirige(client, monkeypatch):
    # Arrange
    servicio_mock = MagicMock()
    monkeypatch.setattr(container, "bus_service", lambda: servicio_mock)

    # Act
    respuesta = client.get("/panel/buses/eliminar/10")

    # Assert
    servicio_mock.desasignar.assert_called_once_with(1, 10)
    assert respuesta.status_code == 302


def test_ruta_desasignar_maneja_regla_negocio_error(client, monkeypatch):
    # Arrange
    servicio_mock = MagicMock()
    servicio_mock.desasignar.side_effect = ReglaNegocioError("El bus no pertenece a tu ruta.")
    monkeypatch.setattr(container, "bus_service", lambda: servicio_mock)

    # Act
    respuesta = client.get("/panel/buses/eliminar/10")

    # Assert
    servicio_mock.desasignar.assert_called_once_with(1, 10)
    assert respuesta.status_code == 302


# ---------- Flujo de registro y acceso ----------
def test_ruta_panel_post_registra_bus_y_redirige(client, monkeypatch):
    # Arrange
    servicio_mock = MagicMock()
    monkeypatch.setattr(container, "bus_service", lambda: servicio_mock)
    datos_form = {"placa": "ABC-123", "anio": "2022", "id_modelo_bus": "2"}

    # Act
    respuesta = client.post("/panel/buses", data=datos_form)

    # Assert
    servicio_mock.registrar.assert_called_once_with(1, "ABC-123", "2022", "2")
    assert respuesta.status_code == 302


def test_ruta_panel_sin_sesion_redirige_al_login():
    # Arrange
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Act
    with app.test_client() as anon_client:
        respuesta = anon_client.get("/panel/buses")

    # Assert
    assert respuesta.status_code == 302