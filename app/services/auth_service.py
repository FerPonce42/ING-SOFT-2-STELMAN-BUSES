from werkzeug.security import check_password_hash

from app.errors import CredencialesInvalidasError


class AuthService:
    def __init__(self, cuentas):
        self.cuentas = cuentas

    def autenticar(self, usuario, clave):
        cuenta = self.cuentas.por_usuario((usuario or "").strip())
        if (
            not cuenta
            or not cuenta["estado_cuenta"]
            or not check_password_hash(cuenta["password_hash"], clave or "")
        ):
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos")
        return {
            "id": cuenta["id_empleado"],
            "usuario": cuenta["nombre_usuario"],
            "rol": cuenta["nombre_cargo"],
        }
