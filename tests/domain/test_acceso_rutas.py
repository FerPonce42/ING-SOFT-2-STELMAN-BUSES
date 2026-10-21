"""Issue #1 - Pruebas de dominio: textos, fechas y errores compartidos."""
import unittest
from datetime import date, datetime

from app.errors import IntegridadError, ReglaNegocioError
from app.services import validaciones


class TextoRequeridoTest(unittest.TestCase):
    def setUp(self):
        self.etiqueta = "El nombre"
        self.maximo = 5

    def tearDown(self):
        self.etiqueta = None
        self.maximo = None

    def test_vacio_lanza_error_con_la_etiqueta(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.texto_requerido("", self.etiqueta)
        self.assertEqual(str(ctx.exception), "El nombre es obligatorio.")

    def test_none_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.texto_requerido(None, self.etiqueta)

    def test_solo_espacios_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.texto_requerido("    ", self.etiqueta)

    def test_supera_el_maximo_lanza_error_con_el_limite(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.texto_requerido("abcdef", self.etiqueta, self.maximo)
        self.assertEqual(str(ctx.exception), "El nombre no puede superar 5 caracteres.")

    def test_justo_en_el_maximo_es_valido(self):
        self.assertEqual(validaciones.texto_requerido("abcde", self.etiqueta, self.maximo), "abcde")

    def test_recorta_espacios_de_los_extremos(self):
        self.assertEqual(validaciones.texto_requerido("  hola  ", self.etiqueta), "hola")

    def test_maximo_se_mide_despues_de_recortar(self):
        self.assertEqual(validaciones.texto_requerido("  abcde  ", self.etiqueta, self.maximo), "abcde")


class TextoOpcionalTest(unittest.TestCase):
    def test_vacio_devuelve_none(self):
        self.assertIsNone(validaciones.texto_opcional(""))

    def test_none_devuelve_none(self):
        self.assertIsNone(validaciones.texto_opcional(None))

    def test_solo_espacios_devuelve_none(self):
        self.assertIsNone(validaciones.texto_opcional("   "))

    def test_con_texto_lo_devuelve_recortado(self):
        self.assertEqual(validaciones.texto_opcional("  hola "), "hola")


class AFechaIsoTest(unittest.TestCase):
    def setUp(self):
        self.dia = date(2026, 10, 21)
        self.momento = datetime(2026, 10, 21, 14, 30, 5)

    def tearDown(self):
        self.dia = None
        self.momento = None

    def test_datetime_devuelve_solo_la_fecha_iso(self):
        self.assertEqual(validaciones.a_fecha_iso(self.momento), "2026-10-21")

    def test_date_devuelve_fecha_iso(self):
        self.assertEqual(validaciones.a_fecha_iso(self.dia), "2026-10-21")

    def test_texto_se_devuelve_sin_cambios(self):
        self.assertEqual(validaciones.a_fecha_iso("2026-10-21"), "2026-10-21")

    def test_none_se_devuelve_sin_cambios(self):
        self.assertIsNone(validaciones.a_fecha_iso(None))


class IntegridadErrorTest(unittest.TestCase):
    def setUp(self):
        self.en_uso = IntegridadError(1451, "fila referenciada")
        self.duplicado = IntegridadError(1062, "entrada duplicada")
        self.otro = IntegridadError(1048, "columna nula")

    def tearDown(self):
        self.en_uso = self.duplicado = self.otro = None

    def test_codigo_1451_es_registro_en_uso(self):
        self.assertTrue(self.en_uso.registro_en_uso)
        self.assertFalse(self.en_uso.duplicado)

    def test_codigo_1062_es_duplicado(self):
        self.assertTrue(self.duplicado.duplicado)
        self.assertFalse(self.duplicado.registro_en_uso)

    def test_otro_codigo_no_es_ninguno_de_los_dos(self):
        self.assertFalse(self.otro.registro_en_uso)
        self.assertFalse(self.otro.duplicado)

    def test_conserva_codigo_y_mensaje(self):
        self.assertEqual(self.en_uso.codigo, 1451)
        self.assertEqual(str(self.en_uso), "fila referenciada")


if __name__ == "__main__":
    unittest.main()
