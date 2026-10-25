import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.errors import ReglaNegocioError
from app.services.incidencia_service import IncidenciaService, ESTADOS, GRAVEDADES


class TestIncidenciasDominio(unittest.TestCase):
    def setUp(self):
        self.repo = Mock()
        self.buses = Mock()
        self.rutas = Mock()
        self.servicio = IncidenciaService(self.repo, self.buses, self.rutas)

    def tearDown(self):
        self.repo.reset_mock()
        self.buses.reset_mock()
        self.rutas.reset_mock()

    def test_estados_contiene_los_estados_validos(self):
        self.assertEqual(ESTADOS, ("Pendiente", "En revision", "Resuelta", "Cancelada"))

    def test_gravedades_contiene_las_gravedades_validas(self):
        self.assertEqual(GRAVEDADES, ("Leve", "Moderada", "Grave"))

    def test_estado_acepta_valor_valido(self):
        self.assertEqual(self.servicio._estado("Pendiente"), "Pendiente")

    def test_estado_rechaza_valor_invalido(self):
        with self.assertRaisesRegex(ReglaNegocioError, "estado"):
            self.servicio._estado("Inventado")

    def test_datos_operativa_acepta_gravedad_valida(self):
        gravedad, costo, seguro = self.servicio._datos_operativa(
            {"gravedad": "Grave", "costo": "25.50", "requiere_seguro": "on"}
        )
        self.assertEqual(gravedad, "Grave")
        self.assertEqual(costo, Decimal("25.50"))
        self.assertEqual(seguro, 1)

    def test_datos_operativa_rechaza_gravedad_invalida(self):
        with self.assertRaisesRegex(ReglaNegocioError, "gravedad"):
            self.servicio._datos_operativa({"gravedad": "Extrema", "costo": "0"})

    def test_datos_operativa_convierte_costo_vacio_en_cero(self):
        _, costo, _ = self.servicio._datos_operativa(
            {"gravedad": "Leve", "costo": "", "requiere_seguro": ""}
        )
        self.assertEqual(costo, Decimal("0"))

    def test_datos_operativa_rechaza_costo_negativo(self):
        with self.assertRaisesRegex(ReglaNegocioError, "costo"):
            self.servicio._datos_operativa(
                {"gravedad": "Leve", "costo": "-1", "requiere_seguro": ""}
            )

    def test_datos_operativa_activa_seguro_solo_con_on(self):
        for valor, esperado in (("on", 1), ("1", 0), ("true", 0), ("", 0), (None, 0)):
            with self.subTest(valor=valor):
                _, _, seguro = self.servicio._datos_operativa(
                    {"gravedad": "Leve", "costo": "0", "requiere_seguro": valor}
                )
                self.assertEqual(seguro, esperado)

    def test_base_convierte_fecha_y_bus_y_conserva_datos(self):
        datos = self.servicio._base({
            "fecha": "2026-01-15", "descripcion": "  Choque  ",
            "estado": "Pendiente", "id_bus": "7"
        })
        self.assertEqual(datos["fecha"], date(2026, 1, 15))
        self.assertEqual(datos["descripcion"], "Choque")
        self.assertEqual(datos["estado"], "Pendiente")
        self.assertEqual(datos["id_bus"], 7)

    def test_base_rechaza_descripcion_vacia(self):
        with self.assertRaisesRegex(ReglaNegocioError, "descripción"):
            self.servicio._base({
                "fecha": "2026-01-15", "descripcion": " ",
                "estado": "Pendiente", "id_bus": "7"
            })

    def test_base_rechaza_descripcion_mayor_a_500_caracteres(self):
        with self.assertRaisesRegex(ReglaNegocioError, "500"):
            self.servicio._base({
                "fecha": "2026-01-15", "descripcion": "x" * 501,
                "estado": "Pendiente", "id_bus": "7"
            })

    def test_base_rechaza_bus_no_entero(self):
        with self.assertRaisesRegex(ReglaNegocioError, "bus"):
            self.servicio._base({
                "fecha": "2026-01-15", "descripcion": "Choque",
                "estado": "Pendiente", "id_bus": "abc"
            })


if __name__ == "__main__":
    unittest.main()
