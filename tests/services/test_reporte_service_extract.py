"""Pruebas de los métodos extraídos de ReporteService.documentacion_excel (Práctica 07, #47)."""
import unittest

from openpyxl import Workbook

from app.services import reporte_service
from app.services.reporte_service import RELLENO_ALERTA


def _fk(columna, tabla, destino):
    return {"COLUMN_NAME": columna, "REFERENCED_TABLE_NAME": tabla, "REFERENCED_COLUMN_NAME": destino}


class TextoFkTest(unittest.TestCase):
    def test_une_las_relaciones_con_coma(self):
        fks = [_fk("id_ruta", "ruta", "id"), _fk("id_chofer", "chofer", "id")]
        self.assertEqual(
            reporte_service._texto_fk(fks), "id_ruta → ruta.id, id_chofer → chofer.id"
        )

    def test_sin_relaciones_devuelve_guion(self):
        self.assertEqual(reporte_service._texto_fk([]), "—")


class EstadoTablaTest(unittest.TestCase):
    def test_con_pk_es_ok(self):
        self.assertEqual(reporte_service._estado_tabla(["id"]), "OK")

    def test_sin_pk_es_alerta(self):
        self.assertEqual(reporte_service._estado_tabla([]), "⚠ Sin PK")


class ErdTextualTest(unittest.TestCase):
    def test_escribe_una_linea_por_relacion(self):
        hoja = Workbook().active
        reporte_service._llenar_erd(hoja, [("bus", "id_ruta", "ruta", "id")])
        self.assertEqual(hoja["A3"].value, "bus.id_ruta  →  ruta.id")

    def test_sin_relaciones_lo_indica(self):
        hoja = Workbook().active
        reporte_service._llenar_erd(hoja, [])
        self.assertEqual(hoja["A3"].value, "No se detectaron relaciones (FK).")


class ResaltarSinPkTest(unittest.TestCase):
    def test_pinta_solo_las_filas_sin_pk(self):
        hoja = Workbook().active
        hoja.append(["#", "Tabla", "Atributos", "Registros", "PK", "FK", "Estado", "Link"])
        hoja.append([1, "ruta", 2, 1, "id", "—", "OK", ""])
        hoja.append([2, "log", 1, 1, "—", "—", "⚠ Sin PK", ""])
        reporte_service._resaltar_sin_pk(hoja)
        self.assertNotEqual(hoja["A2"].fill.fgColor.rgb, RELLENO_ALERTA.fgColor.rgb)
        self.assertEqual(hoja["A3"].fill.fgColor.rgb, RELLENO_ALERTA.fgColor.rgb)


if __name__ == "__main__":
    unittest.main()
