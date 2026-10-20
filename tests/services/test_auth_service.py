from unittest.mock import Mock

import pytest
from werkzeug.security import generate_password_hash

from app.errors import CredencialesInvalidasError
from app.services.auth_service import AuthService


def cuenta(**cambios):
    base = {"id_cuenta": 1, "nombre_usuario": "ana", "password_hash": generate_password_hash("secreta"),
            "estado_cuenta": 1, "id_empleado": 7, "nombre_cargo": "Controlador de Ruta"}
    return {**base, **cambios}


def servicio(fila):
    repo = Mock()
    repo.por_usuario.return_value = fila
    return AuthService(repo), repo


def test_credenciales_correctas_devuelven_datos_de_sesion():
    svc, repo = servicio(cuenta())
    assert svc.autenticar(" ana ", "secreta") == {"id": 7, "usuario": "ana", "rol": "Controlador de Ruta"}
    repo.por_usuario.assert_called_once_with("ana")


@pytest.mark.parametrize("fila,clave", [
    (None, "secreta"),                       # usuario inexistente
    (cuenta(), "equivocada"),                # clave incorrecta
    (cuenta(estado_cuenta=0), "secreta"),    # cuenta deshabilitada
    (cuenta(password_hash="hash_falso"), "secreta"),  # hash inválido no debe reventar
    (cuenta(), None),                        # clave vacía
])
def test_credenciales_invalidas(fila, clave):
    svc, _ = servicio(fila)
    with pytest.raises(CredencialesInvalidasError):
        svc.autenticar("ana", clave)
