import os
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("SECRET_KEY", "clave-pruebas-personal")
os.environ.setdefault("DB_PASSWORD", "clave-db-pruebas")

from app import create_app
from app.config import Config
from app.errors import ReglaNegocioError


class ConfigPruebas(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "clave-pruebas-personal"


class TestPersonalRutas(unittest.TestCase):

    def setUp(self):
        self.app = create_app(ConfigPruebas)
        self.client = self.app.test_client()

    def _iniciar_sesion(self, id_usuario=1, usuario="aperez_sup"):
        with self.client.session_transaction() as sess:
            sess["id"] = id_usuario
            sess["usuario"] = usuario
            sess["nombre"] = "Supervisor Prueba"
            sess["rol"] = "supervisor"

    def test_inicio_sin_sesion_redirige_a_login(self):
        # Arrange
        ruta = "/panel/personal"

        # Act
        respuesta = self.client.get(ruta)

        # Assert
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/login", respuesta.headers["Location"])

    def test_inicio_con_sesion_carga_panel_personal(self):
        # Arrange
        self._iniciar_sesion()

        # Act
        respuesta = self.client.get("/panel/personal")

        # Assert
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"Panel de Personal", respuesta.data)

    @patch("app.web.personal.container.chofer_service")
    def test_choferes_lista_datos_del_supervisor(self, mock_chofer_service):
        # Arrange
        self._iniciar_sesion(id_usuario=3)
        servicio = MagicMock()
        servicio.panel.return_value = {
            "choferes": [],
            "id_ruta": 10,
            "tipos_licencia": [],
            "editar_personal": None,
        }
        mock_chofer_service.return_value = servicio

        # Act
        respuesta = self.client.get("/panel/personal/choferes")

        # Assert
        self.assertEqual(respuesta.status_code, 200)
        servicio.panel.assert_called_once_with(3, None)
        self.assertIn(b"Ruta ID: 10", respuesta.data)

    @patch("app.web.personal.container.chofer_service")
    def test_choferes_elimina_y_redirige(self, mock_chofer_service):
        # Arrange
        self._iniciar_sesion(id_usuario=3)
        servicio = MagicMock()
        mock_chofer_service.return_value = servicio

        # Act
        respuesta = self.client.get("/panel/personal/choferes?eliminar=8")

        # Assert
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/panel/personal/choferes", respuesta.headers["Location"])
        servicio.eliminar.assert_called_once_with(3, "8")

    @patch("app.web.personal.container.chofer_service")
    def test_registrar_chofer_exitoso_redirige(self, mock_chofer_service):
        # Arrange
        self._iniciar_sesion(id_usuario=3)
        servicio = MagicMock()
        mock_chofer_service.return_value = servicio
        datos_form = {"nombre": "Carlos", "apellido": "Perez", "dni": "12345678"}

        # Act
        respuesta = self.client.post("/registrar_personal_chofer", data=datos_form)

        # Assert
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/panel/personal/choferes", respuesta.headers["Location"])
        servicio.registrar.assert_called_once()

    @patch("app.web.personal.container.chofer_service")
    def test_registrar_chofer_error_negocio_redirige_con_alerta(self, mock_chofer_service):
        # Arrange
        self._iniciar_sesion(id_usuario=3)
        servicio = MagicMock()
        servicio.registrar.side_effect = ReglaNegocioError("DNI duplicado")
        mock_chofer_service.return_value = servicio

        # Act
        respuesta = self.client.post(
            "/registrar_personal_chofer",
            data={"dni": "12345678"},
            follow_redirects=True,
        )

        # Assert
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"DNI duplicado", respuesta.data)

    @patch("app.web.personal.container.chofer_service")
    def test_actualizar_chofer_exitoso_redirige(self, mock_chofer_service):
        # Arrange
        self._iniciar_sesion(id_usuario=3)
        servicio = MagicMock()
        mock_chofer_service.return_value = servicio
        datos_form = {"id_empleado": "12", "nombre": "Carlos"}

        # Act
        respuesta = self.client.post("/actualizar_personal_chofer", data=datos_form)

        # Assert
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn("/panel/personal/choferes", respuesta.headers["Location"])
        servicio.actualizar.assert_called_once()


if __name__ == "__main__":
    unittest.main()
