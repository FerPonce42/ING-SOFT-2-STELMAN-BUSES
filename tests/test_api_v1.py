from datetime import date
import time
from unittest.mock import MagicMock

import pytest

from app import container, create_app
from app.errors import CredencialesInvalidasError
from app.web.api_v1 import generar_token, verificar_token


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    return flask_app


@pytest.fixture
def client(app):
    with app.test_client() as test_client:
        yield test_client


def test_login_exitoso_retorna_token_y_200(app, client, monkeypatch):
    auth_mock = MagicMock()
    auth_mock.autenticar.return_value = {"id": 7, "usuario": "aperez_sup", "rol": "supervisor"}
    monkeypatch.setattr(container, "auth_service", lambda: auth_mock)

    res = client.post("/api/v1/login", json={"usuario": "aperez_sup", "password": "stelman123"})

    assert res.status_code == 200
    body = res.get_json()
    assert "token" in body
    with app.app_context():
        payload = verificar_token(body["token"])
    assert payload["id"] == 7
    assert payload["usuario"] == "aperez_sup"
    auth_mock.autenticar.assert_called_once_with("aperez_sup", "stelman123")


def test_login_credenciales_invalidas_retorna_401(client, monkeypatch):
    auth_mock = MagicMock()
    auth_mock.autenticar.side_effect = CredencialesInvalidasError("Credenciales incorrectas")
    monkeypatch.setattr(container, "auth_service", lambda: auth_mock)

    res = client.post("/api/v1/login", json={"usuario": "aperez_sup", "password": "incorrecta"})

    assert res.status_code == 401
    assert res.get_json() == {"error": "Credenciales inválidas"}


def test_login_campos_faltantes_retorna_401(client, monkeypatch):
    auth_mock = MagicMock()
    monkeypatch.setattr(container, "auth_service", lambda: auth_mock)

    res = client.post("/api/v1/login", json={"usuario": "aperez_sup"})

    assert res.status_code == 401
    assert res.get_json() == {"error": "Usuario y contraseña requeridos"}
    auth_mock.autenticar.assert_not_called()


def test_listar_choferes_sin_token_retorna_401(client):
    res = client.get("/api/v1/choferes")

    assert res.status_code == 401
    assert res.get_json() == {"error": "Token inválido o ausente"}


def test_listar_choferes_token_invalido_retorna_401(client):
    res = client.get("/api/v1/choferes", headers={"Authorization": "Bearer token.falso"})

    assert res.status_code == 401
    assert res.get_json() == {"error": "Token inválido o ausente"}


def test_listar_choferes_token_expirado_retorna_401(app, client, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1000)
    with app.app_context():
        token = generar_token({"id": 1, "usuario": "aperez_sup", "rol": "supervisor"})

    monkeypatch.setattr(time, "time", lambda: 5000)
    res = client.get("/api/v1/choferes", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 401
    assert res.get_json() == {"error": "Token inválido o ausente"}


def test_listar_choferes_con_token_valido_retorna_lista_y_200(app, client, monkeypatch):
    chofer_mock = MagicMock()
    chofer_mock.panel.return_value = {
        "choferes": [
            {
                "id": 10,
                "nombre": "Carlos Diaz",
                "licencia": "A-IIIc",
                "fecha_ingreso": date(2025, 4, 15),
            }
        ]
    }
    monkeypatch.setattr(container, "chofer_service", lambda: chofer_mock)

    with app.app_context():
        token = generar_token({"id": 3, "usuario": "aperez_sup", "rol": "supervisor"})

    res = client.get("/api/v1/choferes", headers={"Authorization": f"Bearer {token}"})

    assert res.status_code == 200
    assert res.get_json() == [
        {
            "id": 10,
            "nombre": "Carlos Diaz",
            "licencia": "A-IIIc",
            "fecha_ingreso": "2025-04-15",
        }
    ]
    chofer_mock.panel.assert_called_once_with(3)


def test_openapi_spec_retorna_200_y_rutas_documentadas(client):
    res = client.get("/api/v1/openapi.json")

    assert res.status_code == 200
    spec = res.get_json()
    assert spec["openapi"] == "3.0.3"
    assert "/api/v1/login" in spec["paths"]
    assert "/api/v1/choferes" in spec["paths"]


def test_swagger_docs_retorna_html_200(client):
    res = client.get("/api/v1/docs")

    assert res.status_code == 200
    assert "text/html" in res.content_type
    html = res.get_data(as_text=True)
    assert "SwaggerUIBundle" in html
    assert "/api/v1/openapi.json" in html


def test_listar_caja_sin_token_retorna_401(client):
    response = client.get("/api/v1/caja")

    assert response.status_code == 401


def test_listar_caja_con_token_valido_retorna_200(client, app, monkeypatch):
    caja_mock = MagicMock()
    caja_mock.panel.return_value = {
        "cajas": [
            {
                "id_caja": 21,
                "fecha": date(2026, 11, 26),
                "monto_recaudado": 125.50
            }
        ]
    }

    monkeypatch.setattr(
        container,
        "caja_service",
        lambda: caja_mock
    )

    with app.app_context():
        token = generar_token({
            "id": 3,
            "usuario": "supervisor",
            "rol": "supervisor"
        })

    response = client.get(
        "/api/v1/caja",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json == [
        {
            "id_caja": 21,
            "fecha": "2026-11-26",
            "monto_recaudado": 125.50
        }
    ]

    caja_mock.panel.assert_called_once_with(3)
