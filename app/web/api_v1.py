import base64
from datetime import date, datetime
from functools import wraps
import hashlib
import hmac
import json
import time

from flask import Blueprint, Response, current_app, jsonify, request

from app import container
from app.errors import CredencialesInvalidasError

bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


def _secret_key() -> bytes:
    return str(current_app.config.get("SECRET_KEY", "stelman-buses-api-secret")).encode("utf-8")


def generar_token(cuenta: dict) -> str:
    payload = {
        "id": cuenta["id"],
        "usuario": cuenta["usuario"],
        "rol": cuenta.get("rol"),
        "exp": int(time.time()) + 3600,
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    b64_payload = base64.urlsafe_b64encode(raw).decode("utf-8")
    firma = hmac.new(_secret_key(), b64_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{firma}"


def verificar_token(token: str):
    try:
        b64_payload, firma = token.split(".", 1)
        firma_esperada = hmac.new(_secret_key(), b64_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(firma, firma_esperada):
            return None
        datos = json.loads(base64.urlsafe_b64decode(b64_payload).decode("utf-8"))
        if datos.get("exp", 0) <= int(time.time()):
            return None
        return datos
    except Exception:
        return None


def token_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "", 1).strip() if auth_header else ""
        datos_token = verificar_token(token) if token else None
        if not datos_token:
            return jsonify({"error": "Token inválido o ausente"}), 401
        request.usuario_api = datos_token
        return f(*args, **kwargs)
    return decorador


def _serializar_fila(fila: dict) -> dict:
    resultado = {}
    for clave, valor in dict(fila).items():
        if isinstance(valor, (date, datetime)):
            resultado[clave] = valor.isoformat()
        else:
            resultado[clave] = valor
    return resultado


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    usuario = data.get("usuario")
    password = data.get("password") if "password" in data else data.get("clave")

    if not usuario or not password:
        return jsonify({"error": "Usuario y contraseña requeridos"}), 401

    try:
        cuenta = container.auth_service().autenticar(usuario, password)
    except CredencialesInvalidasError:
        return jsonify({"error": "Credenciales inválidas"}), 401

    return jsonify({"token": generar_token(cuenta)}), 200


@bp.route("/choferes", methods=["GET"])
@token_requerido
def listar_choferes():
    datos = container.chofer_service().panel(request.usuario_api["id"])
    choferes = [_serializar_fila(c) for c in datos["choferes"]]
    return jsonify(choferes), 200


@bp.route("/openapi.json", methods=["GET"])
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "Stelman Buses API",
            "version": "1.0.0",
            "description": "API REST v1 para autenticación y gestión de flota de Stelman Buses",
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {"type": "http", "scheme": "bearer"}
            }
        },
        "paths": {
            "/api/v1/login": {
                "post": {
                    "summary": "Autenticación de supervisor y emisión de token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "usuario": {"type": "string", "example": "aperez_sup"},
                                        "password": {"type": "string", "example": "stelman123"},
                                    },
                                    "required": ["usuario", "password"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Token generado correctamente"},
                        "401": {"description": "Credenciales inválidas"},
                    },
                }
            },
            "/api/v1/choferes": {
                "get": {
                    "summary": "Listar choferes asignados a la ruta del supervisor",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Lista de choferes"},
                        "401": {"description": "Token inválido o ausente"},
                    },
                }
            },
            "/api/v1/buses": {
                "get": {
                    "summary": "Listar buses de la flota",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Lista de buses"},
                        "401": {"description": "Token inválido o ausente"},
                    },
                }
            },
            "/api/v1/caja": {
                "get": {
                    "summary": "Listar recaudaciones de caja",
                    "security": [{"bearerAuth": []}],
                    "responses": {
                        "200": {"description": "Lista de recaudaciones"},
                        "401": {"description": "Token inválido o ausente"},
                    },
                }
            },
        },
    }
    return jsonify(spec), 200


@bp.route("/docs", methods=["GET"])
def swagger_ui():
    html = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Stelman Buses - Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: '/api/v1/openapi.json', dom_id: '#swagger-ui' });
  </script>
</body>
</html>"""
    return Response(html, mimetype="text/html")