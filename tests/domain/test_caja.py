"""Issue #13 - Pruebas de dominio: reglas de recaudación (monto, fecha, chofer y bus)."""
import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock

from app.errors import ReglaNegocioError
from app.services import validaciones
from app.services.caja_service import CajaService


class DatosDeRecaudacionTest(unittest.TestCase):
    """CajaService._datos: valida y convierte el formulario de una recaudación."""

    def setUp(self):
        self.servicio = CajaService(Mock(), Mock(), Mock(), Mock())
        self.form = {"fecha": "2026-02-01", "monto": "120.50", "observacion": "",
                     "id_empleado": "1", "id_bus": "2"}

    def tearDown(self):
        self.servicio = None
        self.form = None

    def test_formulario_valido_devuelve_los_datos_convertidos(self):
        self.assertEqual(self.servicio._datos(self.form), {
            "fecha": date(2026, 2, 1), "monto": Decimal("120.50"), "observacion": None,
            "id_empleado": 1, "id_bus": 2})

    def test_monto_cero_se_rechaza(self):
        self.form["monto"] = "0"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._datos(self.form)
        self.assertEqual(str(ctx.exception), "El monto debe ser mayor que 0.")

    def test_monto_negativo_se_rechaza(self):
        self.form["monto"] = "-10"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._datos(self.form)
        self.assertEqual(str(ctx.exception), "El monto debe ser mayor que 0.")

    def test_monto_mayor_que_cero_se_acepta(self):
        self.form["monto"] = "0.01"
        self.assertEqual(self.servicio._datos(self.form)["monto"], Decimal("0.01"))

    def test_monto_con_letras_se_rechaza(self):
        self.form["monto"] = "abc"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._datos(self.form)
        self.assertEqual(str(ctx.exception), "El monto no es un número válido.")

    def test_monto_vacio_se_rechaza(self):
        self.form["monto"] = ""
        with self.assertRaises(ReglaNegocioError):
            self.servicio._datos(self.form)

    def test_monto_ausente_se_rechaza(self):
        del self.form["monto"]
        with self.assertRaises(ReglaNegocioError):
            self.servicio._datos(self.form)

    def test_chofer_no_entero_se_rechaza(self):
        self.form["id_empleado"] = "abc"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._datos(self.form)
        self.assertEqual(str(ctx.exception), "El chofer no es válido.")

    def test_chofer_ausente_se_rechaza(self):
        del self.form["id_empleado"]
        with self.assertRaises(ReglaNegocioError):
            self.servicio._datos(self.form)

    def test_bus_no_entero_se_rechaza(self):
        self.form["id_bus"] = "x"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio._datos(self.form)
        self.assertEqual(str(ctx.exception), "El bus no es válido.")

    def test_bus_decimal_se_rechaza(self):
        self.form["id_bus"] = "2.5"
        with self.assertRaises(ReglaNegocioError):
            self.servicio._datos(self.form)

    def test_observacion_se_recorta_y_si_queda_vacia_es_none(self):
        self.form["observacion"] = "  Sin novedades  "
        self.assertEqual(self.servicio._datos(self.form)["observacion"], "Sin novedades")
        self.form["observacion"] = "   "
        self.assertIsNone(self.servicio._datos(self.form)["observacion"])

    def test_fecha_invalida_del_formulario_se_rechaza(self):
        self.form["fecha"] = "01/02/2026"
        with self.assertRaises(ReglaNegocioError):
            self.servicio._datos(self.form)


class FechaDeRecaudacionTest(unittest.TestCase):
    """validaciones.fecha tal como la usa Caja: formato AAAA-MM-DD, desde 2000 hasta hoy."""

    def setUp(self):
        self.hoy = date.today()

    def tearDown(self):
        self.hoy = None

    def test_fecha_valida_devuelve_un_date(self):
        self.assertEqual(validaciones.fecha("2026-02-01"), date(2026, 2, 1))

    def test_fecha_recorta_espacios(self):
        self.assertEqual(validaciones.fecha("  2026-02-01  "), date(2026, 2, 1))

    def test_hoy_es_valido(self):
        self.assertEqual(validaciones.fecha(self.hoy.isoformat()), self.hoy)

    def test_primer_dia_permitido_es_valido(self):
        self.assertEqual(validaciones.fecha("2000-01-01"), date(2000, 1, 1))

    def test_formato_invalido_lanza_error(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.fecha("01/02/2026")
        self.assertEqual(str(ctx.exception), "La fecha es inválida. Usa el formato AAAA-MM-DD.")

    def test_fecha_inexistente_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.fecha("2026-02-30")

    def test_vacia_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.fecha("")

    def test_none_lanza_error(self):
        with self.assertRaises(ReglaNegocioError):
            validaciones.fecha(None)

    def test_fecha_futura_lanza_error_con_el_rango(self):
        manana = (self.hoy + timedelta(days=1)).isoformat()
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.fecha(manana)
        self.assertEqual(
            str(ctx.exception),
            "La fecha está fuera del rango permitido (2000-01-01 hasta hoy).",
        )

    def test_fecha_anterior_al_minimo_lanza_error(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.fecha("1999-12-31")
        self.assertIn("fuera del rango permitido", str(ctx.exception))

    def test_permitir_futuro_acepta_fechas_futuras(self):
        futura = self.hoy + timedelta(days=30)
        self.assertEqual(validaciones.fecha(futura.isoformat(), permitir_futuro=True), futura)

    def test_etiqueta_personalizada_aparece_en_el_mensaje(self):
        with self.assertRaises(ReglaNegocioError) as ctx:
            validaciones.fecha("xx", etiqueta="La fecha de cobro")
        self.assertTrue(str(ctx.exception).startswith("La fecha de cobro es inválida."))
