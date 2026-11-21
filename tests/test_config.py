import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

RUTA_CONFIG = Path(__file__).resolve().parents[1] / "app" / "config.py"


def cargar_config():
    """Carga app/config.py desde cero, leyendo el entorno actual."""
    spec = importlib.util.spec_from_file_location("config_bajo_prueba", RUTA_CONFIG)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.Config


class TestConfigCredenciales(unittest.TestCase):

    def test_falta_secret_key_lanza_error(self):
        # Arrange
        entorno = {"DB_PASSWORD": "clave-db"}
        with patch.dict(os.environ, entorno, clear=True):
            # Act + Assert
            with self.assertRaises(RuntimeError) as ctx:
                cargar_config()
            self.assertIn("SECRET_KEY", str(ctx.exception))

    def test_falta_db_password_lanza_error(self):
        # Arrange
        entorno = {"SECRET_KEY": "clave-secreta"}
        with patch.dict(os.environ, entorno, clear=True):
            # Act + Assert
            with self.assertRaises(RuntimeError) as ctx:
                cargar_config()
            self.assertIn("DB_PASSWORD", str(ctx.exception))

    def test_con_variables_definidas_carga_los_valores(self):
        # Arrange
        entorno = {"SECRET_KEY": "clave-secreta", "DB_PASSWORD": "clave-db"}
        with patch.dict(os.environ, entorno, clear=True):
            # Act
            config = cargar_config()
            # Assert
            self.assertEqual(config.SECRET_KEY, "clave-secreta")
            self.assertEqual(config.DB_PASSWORD, "clave-db")


if __name__ == "__main__":
    unittest.main()