"""Issue #4 - Pruebas de dominio: reglas del bus."""
import unittest
from datetime import date
from unittest.mock import Mock

from app.errors import ReglaNegocioError
from app.services import validaciones
from app.services.bus_service import ANIO_MINIMO, BusService


class AnioMaximoTest(unittest.TestCase):
    def test_anio_maximo_es_el_anio_actual_mas_uno(self):
        self.assertEqual(BusService.anio_maximo(), date.today().year + 1)

    def test_anio_minimo_es_1950(self):
        self.assertEqual(ANIO_MINIMO, 1950)


class ValidarAnioTest(unittest.TestCase):
    def setUp(self):
        self.servicio = BusService(Mock(), Mock())
        self.placa = "ABC-123"
        self.modelo = "2"

    def tearDown(self):
        self.servicio = self.placa = self.modelo = None

    def test_anio_minimo_1950_es_valido(self):
        _, anio, _ = self.servicio._validar_datos(self.placa, "1950", self.modelo)
        self.assertEqual(anio, 1950)

    def test_anio_actual_es_valido(self):
        _, anio, _ = self.servicio._validar_datos(self.placa, str(date.today().year), self.modelo)
        self.assertEqual(anio, date.today().year)

    def test_anio_maximo_actual_mas_uno_es_valido(self):
        maximo = date.today().year + 1
        _, anio, _ = self.servicio._validar_datos(self.placa, str(maximo), self.modelo)
        self.assertEqual(anio, maximo)

    def test_anio_menor_a_1950_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(self.placa, "1949", self.modelo)

    def test_anio_mayor_al_maximo_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(self.placa, str(date.today().year + 2), self.modelo)

    def test_error_de_rango_informa_los_limites(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._validar_datos(self.placa, "1949", self.modelo)
        esperado = f"El año debe estar entre 1950 y {date.today().year + 1}."
        self.assertEqual(str(ctx.exception), esperado)

    def test_anio_como_entero_es_valido(self):
        _, anio, _ = self.servicio._validar_datos(self.placa, 2020, self.modelo)
        self.assertEqual(anio, 2020)


class ValidarPlacaTest(unittest.TestCase):
    def setUp(self):
        self.servicio = BusService(Mock(), Mock())
        self.anio = "2024"
        self.modelo = "2"

    def tearDown(self):
        self.servicio = self.anio = self.modelo = None

    def test_placa_vacia_lanza_error(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._validar_datos("", self.anio, self.modelo)
        self.assertEqual(str(ctx.exception), "La placa es obligatorio.")

    def test_placa_none_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(None, self.anio, self.modelo)

    def test_placa_solo_espacios_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos("     ", self.anio, self.modelo)

    def test_placa_de_21_caracteres_lanza_error(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._validar_datos("A" * 21, self.anio, self.modelo)
        self.assertEqual(str(ctx.exception), "La placa no puede superar 20 caracteres.")

    def test_placa_de_20_caracteres_es_valida(self):
        placa, _, _ = self.servicio._validar_datos("A" * 20, self.anio, self.modelo)
        self.assertEqual(placa, "A" * 20)

    def test_placa_se_convierte_a_mayusculas(self):
        placa, _, _ = self.servicio._validar_datos("abc-123", self.anio, self.modelo)
        self.assertEqual(placa, "ABC-123")

    def test_placa_se_recorta_antes_de_convertir(self):
        placa, _, _ = self.servicio._validar_datos("  abc-123  ", self.anio, self.modelo)
        self.assertEqual(placa, "ABC-123")


class ValidarNoNumericosTest(unittest.TestCase):
    def setUp(self):
        self.servicio = BusService(Mock(), Mock())
        self.placa = "ABC-123"

    def tearDown(self):
        self.servicio = self.placa = None

    def test_anio_con_texto_lanza_error(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._validar_datos(self.placa, "abc", "2")
        self.assertEqual(str(ctx.exception), "El año no es válido.")

    def test_anio_vacio_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(self.placa, "", "2")

    def test_anio_none_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(self.placa, None, "2")

    def test_modelo_con_texto_lanza_error(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._validar_datos(self.placa, "2024", "xyz")
        self.assertEqual(str(ctx.exception), "El modelo no es válido.")

    def test_modelo_vacio_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(self.placa, "2024", "")

    def test_modelo_none_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            self.servicio._validar_datos(self.placa, "2024", None)

    def test_datos_validos_devuelven_placa_anio_y_modelo_normalizados(self):
        resultado = self.servicio._validar_datos(" abc-123 ", "2024", "2")
        self.assertEqual(resultado, ("ABC-123", 2024, 2))


class EnteroTest(unittest.TestCase):
    def setUp(self):
        self.etiqueta = "El año"

    def tearDown(self):
        self.etiqueta = None

    def test_texto_numerico_se_convierte_a_entero(self):
        self.assertEqual(validaciones.entero("2024", self.etiqueta), 2024)

    def test_entero_se_devuelve_igual(self):
        self.assertEqual(validaciones.entero(7, self.etiqueta), 7)

    def test_texto_no_numerico_lanza_error_con_la_etiqueta(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.entero("abc", self.etiqueta)
        self.assertEqual(str(ctx.exception), "El año no es válido.")

    def test_vacio_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.entero("", self.etiqueta)

    def test_none_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.entero(None, self.etiqueta)


if __name__ == "__main__":
    unittest.main()
