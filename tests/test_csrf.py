import os
import re
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("SECRET_KEY", "clave-pruebas-csrf")
os.environ.setdefault("DB_PASSWORD", "clave-db-pruebas")

from app import create_app
from app.config import Config
from app.errors import CredencialesInvalidasError


class ConfigPruebasCsrf(Config):
    TESTING = True
    SECRET_KEY = "clave-pruebas-csrf"


class TestProteccionCsrf(unittest.TestCase):

    def setUp(self):
        self.app = create_app(ConfigPruebasCsrf)
        self.client = self.app.test_client()

    def _servicio_que_rechaza(self):
        servicio = MagicMock()
        servicio.autenticar.side_effect = CredencialesInvalidasError("Credenciales inválidas")
        return servicio

    def test_formulario_login_incluye_token_csrf(self):
        # Arrange
        ruta = "/login"

        # Act
        respuesta = self.client.get(ruta)

        # Assert
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('name="csrf_token"', respuesta.get_data(as_text=True))

    @patch("app.web.auth.container.auth_service")
    def test_post_sin_token_es_rechazado_con_400(self, mock_auth):
        # Arrange
        mock_auth.return_value = self._servicio_que_rechaza()
        datos = {"usuario": "aperez_sup", "password": "x"}

        # Act
        respuesta = self.client.post("/login", data=datos)

        # Assert
        self.assertEqual(respuesta.status_code, 400)

    @patch("app.web.auth.container.auth_service")
    def test_post_con_token_valido_es_aceptado(self, mock_auth):
        # Arrange
        mock_auth.return_value = self._servicio_que_rechaza()
        html = self.client.get("/login").get_data(as_text=True)
        token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
        datos = {"usuario": "aperez_sup", "password": "x", "csrf_token": token}

        # Act
        respuesta = self.client.post("/login", data=datos)

        # Assert
        self.assertEqual(respuesta.status_code, 200)


if __name__ == "__main__":
    unittest.main()