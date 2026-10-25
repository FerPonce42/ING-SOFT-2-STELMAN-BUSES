"""Issue #5 - Pruebas de repositorio: bus_repository con conexión falsa (sin base de datos real)."""
import unittest
from unittest.mock import MagicMock

import pymysql

from app.errors import IntegridadError
from app.repositories.bus_repository import BusRepository


class BusRepositoryBase(unittest.TestCase):
    """Prepara una conexión y un cursor falsos que usan todas las pruebas."""

    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = BusRepository(self.conn)

    def tearDown(self):
        self.conn = self.cur = self.repo = None

    def sql_ejecutado(self):
        return self.cur.execute.call_args[0][0]

    def params_ejecutados(self):
        return self.cur.execute.call_args[0][1]


class ModelosTest(BusRepositoryBase):
    def test_devuelve_los_modelos_como_lista(self):
        self.cur.fetchall.return_value = (
            {"id": 1, "modelo_nombre": "Sprinter", "marca_nombre": "Mercedes"},
            {"id": 2, "modelo_nombre": "Hiace", "marca_nombre": "Toyota"},
        )
        modelos = self.repo.modelos()
        self.assertEqual(len(modelos), 2)
        self.assertEqual(modelos[0]["modelo_nombre"], "Sprinter")

    def test_sin_modelos_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = ()
        self.assertEqual(self.repo.modelos(), [])

    def test_une_modelo_con_marca_y_ordena_por_marca_y_modelo(self):
        self.cur.fetchall.return_value = ()
        self.repo.modelos()
        sql = self.sql_ejecutado()
        self.assertIn("FROM modelo_bus mb", sql)
        self.assertIn("JOIN marca_bus ma", sql)
        self.assertIn("ORDER BY ma.nombre, mb.nombre", sql)

    def test_no_envia_parametros(self):
        self.cur.fetchall.return_value = ()
        self.repo.modelos()
        self.assertEqual(self.params_ejecutados(), ())


class BusesDeRutaTest(BusRepositoryBase):
    def test_devuelve_los_buses_de_la_ruta(self):
        self.cur.fetchall.return_value = (
            {"id_bus": 1, "placa": "ABC-123"},
            {"id_bus": 2, "placa": "XYZ-789"},
        )
        buses = self.repo.buses_de_ruta(4)
        self.assertEqual([b["placa"] for b in buses], ["ABC-123", "XYZ-789"])

    def test_ruta_sin_buses_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = ()
        self.assertEqual(self.repo.buses_de_ruta(4), [])

    def test_envia_el_id_de_ruta_como_parametro(self):
        self.cur.fetchall.return_value = ()
        self.repo.buses_de_ruta(4)
        self.assertEqual(self.params_ejecutados(), (4,))

    def test_solo_trae_buses_no_desasignados_ordenados_por_placa(self):
        self.cur.fetchall.return_value = ()
        self.repo.buses_de_ruta(4)
        sql = self.sql_ejecutado()
        self.assertIn("br.id_ruta = %s", sql)
        self.assertIn("br.fecha_desasignacion IS NULL", sql)
        self.assertIn("ORDER BY b.placa", sql)

    def test_la_revision_sale_de_la_tabla_mantenimiento(self):
        self.cur.fetchall.return_value = ()
        self.repo.buses_de_ruta(4)
        self.assertIn("MAX(mt.fecha)", self.sql_ejecutado())
        self.assertIn("FROM mantenimiento mt", self.sql_ejecutado())


class BusesParaSeleccionTest(BusRepositoryBase):
    def test_devuelve_id_y_placa_de_los_buses(self):
        self.cur.fetchall.return_value = ({"id_bus": 1, "placa": "ABC-123"},)
        self.assertEqual(self.repo.buses_para_seleccion(4), [{"id_bus": 1, "placa": "ABC-123"}])

    def test_sin_buses_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = ()
        self.assertEqual(self.repo.buses_para_seleccion(4), [])

    def test_envia_el_id_de_ruta_como_parametro(self):
        self.cur.fetchall.return_value = ()
        self.repo.buses_para_seleccion(4)
        self.assertEqual(self.params_ejecutados(), (4,))

    def test_incluye_desasignados_desde_hoy_y_ordena_por_placa(self):
        self.cur.fetchall.return_value = ()
        self.repo.buses_para_seleccion(4)
        sql = self.sql_ejecutado()
        self.assertIn("br.fecha_desasignacion IS NULL OR br.fecha_desasignacion >= CURDATE()", sql)
        self.assertIn("ORDER BY b.placa", sql)


class ObtenerBasicoTest(BusRepositoryBase):
    def test_bus_existente_devuelve_id_y_placa(self):
        self.cur.fetchone.return_value = {"id_bus": 7, "placa": "ABC-123"}
        self.assertEqual(self.repo.obtener_basico(7), {"id_bus": 7, "placa": "ABC-123"})

    def test_bus_inexistente_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.obtener_basico(999))

    def test_envia_el_id_del_bus_como_parametro(self):
        self.cur.fetchone.return_value = None
        self.repo.obtener_basico(7)
        self.assertEqual(self.params_ejecutados(), (7,))
        self.assertIn("WHERE id_bus = %s", self.sql_ejecutado())


class ObtenerDeSupervisorTest(BusRepositoryBase):
    def test_bus_del_supervisor_devuelve_la_fila(self):
        fila = {"id_bus": 7, "placa": "ABC-123", "año_fabricacion": 2020, "id_modelo_bus": 2}
        self.cur.fetchone.return_value = fila
        self.assertEqual(self.repo.obtener_de_supervisor(7, 10), fila)

    def test_bus_ajeno_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.obtener_de_supervisor(7, 10))

    def test_envia_id_de_bus_y_id_de_supervisor_en_ese_orden(self):
        self.cur.fetchone.return_value = None
        self.repo.obtener_de_supervisor(7, 10)
        self.assertEqual(self.params_ejecutados(), (7, 10))

    def test_exige_ruta_activa_del_supervisor_y_bus_no_desasignado(self):
        self.cur.fetchone.return_value = None
        self.repo.obtener_de_supervisor(7, 10)
        sql = self.sql_ejecutado()
        self.assertIn("JOIN supervisor_ruta sr", sql)
        self.assertIn("sr.fecha_fin IS NULL", sql)
        self.assertIn("br.fecha_desasignacion IS NULL", sql)


class ExistePlacaTest(BusRepositoryBase):
    def test_placa_registrada_devuelve_true(self):
        self.cur.fetchone.return_value = {"id_bus": 3}
        self.assertTrue(self.repo.existe_placa("ABC-123"))

    def test_placa_libre_devuelve_false(self):
        self.cur.fetchone.return_value = None
        self.assertFalse(self.repo.existe_placa("ABC-123"))

    def test_sin_excluir_envia_cero_como_id_excluido(self):
        self.cur.fetchone.return_value = None
        self.repo.existe_placa("ABC-123")
        self.assertEqual(self.params_ejecutados(), ("ABC-123", 0))

    def test_excluyendo_un_bus_envia_su_id(self):
        self.cur.fetchone.return_value = None
        self.repo.existe_placa("ABC-123", excluir_id_bus=4)
        self.assertEqual(self.params_ejecutados(), ("ABC-123", 4))

    def test_consulta_por_placa_distinta_del_bus_excluido(self):
        self.cur.fetchone.return_value = None
        self.repo.existe_placa("ABC-123")
        self.assertIn("placa = %s AND id_bus <> %s", self.sql_ejecutado())


class CrearTest(BusRepositoryBase):
    def test_devuelve_el_id_del_bus_creado(self):
        self.cur.lastrowid = 42
        self.assertEqual(self.repo.crear("ABC-123", 2024, 2, 5), 42)

    def test_inserta_en_bus_con_los_valores_en_orden(self):
        self.cur.lastrowid = 42
        self.repo.crear("ABC-123", 2024, 2, 5)
        self.assertIn("INSERT INTO bus (placa, año_fabricacion, id_modelo_bus, id_almacen)", self.sql_ejecutado())
        self.assertEqual(self.params_ejecutados(), ("ABC-123", 2024, 2, 5))

    def test_placa_duplicada_lanza_integridad_error_1062(self):
        self.cur.execute.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")
        with self.assertRaises(IntegridadError) as ctx:
            self.repo.crear("ABC-123", 2024, 2, 5)
        self.assertTrue(ctx.exception.duplicado)


class AsignarARutaTest(BusRepositoryBase):
    def test_devuelve_el_id_de_la_asignacion(self):
        self.cur.lastrowid = 9
        self.assertEqual(self.repo.asignar_a_ruta(42, 3), 9)

    def test_inserta_en_bus_ruta_con_bus_y_ruta_en_orden(self):
        self.cur.lastrowid = 9
        self.repo.asignar_a_ruta(42, 3)
        self.assertIn("INSERT INTO bus_ruta (id_bus, id_ruta, fecha_asignacion)", self.sql_ejecutado())
        self.assertIn("NOW()", self.sql_ejecutado())
        self.assertEqual(self.params_ejecutados(), (42, 3))


class ActualizarTest(BusRepositoryBase):
    def test_actualiza_el_bus_y_no_devuelve_valor(self):
        self.assertIsNone(self.repo.actualizar(4, "ABC-123", 2024, 2))

    def test_envia_los_valores_y_el_id_del_bus_al_final(self):
        self.repo.actualizar(4, "ABC-123", 2024, 2)
        self.assertIn("UPDATE bus SET placa = %s, año_fabricacion = %s, id_modelo_bus = %s", self.sql_ejecutado())
        self.assertIn("WHERE id_bus = %s", self.sql_ejecutado())
        self.assertEqual(self.params_ejecutados(), ("ABC-123", 2024, 2, 4))

    def test_placa_duplicada_lanza_integridad_error_1062(self):
        self.cur.execute.side_effect = pymysql.err.IntegrityError(1062, "Duplicate entry")
        with self.assertRaises(IntegridadError) as ctx:
            self.repo.actualizar(4, "ABC-123", 2024, 2)
        self.assertEqual(ctx.exception.codigo, 1062)


class DesasignarTest(BusRepositoryBase):
    def test_desasigna_el_bus_y_no_devuelve_valor(self):
        self.assertIsNone(self.repo.desasignar(4))

    def test_marca_la_fecha_solo_en_asignaciones_vigentes(self):
        self.repo.desasignar(4)
        sql = self.sql_ejecutado()
        self.assertIn("UPDATE bus_ruta SET fecha_desasignacion = NOW()", sql)
        self.assertIn("id_bus = %s AND fecha_desasignacion IS NULL", sql)

    def test_envia_el_id_del_bus_como_parametro(self):
        self.repo.desasignar(4)
        self.assertEqual(self.params_ejecutados(), (4,))


if __name__ == "__main__":
    unittest.main()
