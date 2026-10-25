import unittest
from unittest.mock import MagicMock
from app.errors import ReglaNegocioError
from app.services.chofer_service import ChoferService
from app.services import validaciones

class ValidarChoferTest(unittest.TestCase):
    def setUp(self):
        self.service = ChoferService(MagicMock(), MagicMock())
        self.chofer_data = {
            "nombre": "Juan",
            "apellido": "Perez",
            "dni": "12345678",
            "licencia": "A-12345",
            "fecha_nacimiento": "1990-01-01",
            "primera_licencia": "2010-01-01"
        }

    def tearDown(self):
        self.service = None
        self.chofer_data = None

    def test_validar_nombre_excede_100_caracteres_lanza_error(self):
        self.chofer_data["nombre"] = "A" * 101
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)

    def test_validar_apellido_excede_100_caracteres_lanza_error(self):
        self.chofer_data["apellido"] = "A" * 101
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)

    def test_validar_dni_excede_50_caracteres_lanza_error(self):
        self.chofer_data["dni"] = "1" * 51
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)

    def test_validar_licencia_excede_50_caracteres_lanza_error(self):
        self.chofer_data["licencia"] = "L" * 51
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)

    def test_validar_fecha_nacimiento_menor_1940_lanza_error(self):
        self.chofer_data["fecha_nacimiento"] = "1939-12-31"
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)

    def test_validar_fecha_nacimiento_futura_lanza_error(self):
        self.chofer_data["fecha_nacimiento"] = "2100-01-01"
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)

    def test_validar_primera_licencia_menor_1950_lanza_error(self):
        self.chofer_data["primera_licencia"] = "1949-12-31"
        with self.assertRaises(ReglaNegocioError):
            self.service._validar(self.chofer_data)


class ValidacionesDecimalTest(unittest.TestCase):
    def test_decimal_invalido_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.decimal("texto_no_numero", "Sueldo")
            
    def test_decimal_negativo_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.decimal("-10.5", "Sueldo", minimo=0)
            
    def test_decimal_igual_al_minimo_sin_permitir_igual_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.decimal("0.0", "Sueldo", minimo=0, permitir_igual=False)