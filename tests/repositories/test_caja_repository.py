"""Issue #14 - Pruebas de repositorio de caja con conexión falsa (sin base de datos real)."""
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pymysql

from app.errors import IntegridadError
from app.repositories.caja_repository import CajaRepository


class CajaRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = CajaRepository(self.conn)

    def tearDown(self):
        self.conn = self.cur = self.repo = None

    def sql_ejecutado(self):
        return self.cur.execute.call_args[0][0]

    def params_ejecutados(self):
        return self.cur.execute.call_args[0][1]

    # listar_de_ruta

    def test_listar_de_ruta_devuelve_las_filas_como_lista(self):
        self.cur.fetchall.return_value = (
            {"id_caja": 2, "monto_recaudado": Decimal("80.00")},
            {"id_caja": 1, "monto_recaudado": Decimal("350.50")},
        )
        filas = self.repo.listar_de_ruta(3)
        self.assertEqual([f["id_caja"] for f in filas], [2, 1])
        self.assertIsInstance(filas, list)

    def test_listar_de_ruta_envia_el_id_de_la_ruta_como_parametro(self):
        self.cur.fetchall.return_value = ()
        self.repo.listar_de_ruta(3)
        self.assertEqual(self.params_ejecutados(), (3,))

    def test_listar_de_ruta_filtra_por_ruta_y_ordena_por_fecha_descendente(self):
        self.cur.fetchall.return_value = ()
        self.repo.listar_de_ruta(3)
        sql = self.sql_ejecutado()
        self.assertIn("FROM caja c", sql)
        self.assertIn("WHERE c.id_ruta = %s", sql)
        self.assertIn("ORDER BY c.fecha DESC", sql)

    def test_listar_de_ruta_une_con_empleado_y_bus(self):
        self.cur.fetchall.return_value = ()
        self.repo.listar_de_ruta(3)
        sql = self.sql_ejecutado()
        self.assertIn("JOIN empleado e ON e.id_empleado = c.id_empleado", sql)
        self.assertIn("JOIN bus b ON b.id_bus = c.id_bus", sql)

    def test_listar_de_ruta_sin_cajas_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = ()
        self.assertEqual(self.repo.listar_de_ruta(99), [])

    # obtener

    def test_obtener_existente_devuelve_la_fila(self):
        fila = {"id_caja": 5, "id_ruta": 3, "monto_recaudado": Decimal("120.50")}
        self.cur.fetchone.return_value = fila
        self.assertEqual(self.repo.obtener(5, 3), fila)

    def test_obtener_envia_id_caja_e_id_ruta_en_ese_orden(self):
        self.cur.fetchone.return_value = None
        self.repo.obtener(5, 3)
        self.assertEqual(self.params_ejecutados(), (5, 3))

    def test_obtener_filtra_por_caja_y_por_ruta(self):
        self.cur.fetchone.return_value = None
        self.repo.obtener(5, 3)
        self.assertIn("WHERE id_caja = %s AND id_ruta = %s", self.sql_ejecutado())

    def test_obtener_inexistente_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.obtener(999, 3))

    # crear

    def test_crear_devuelve_el_id_generado(self):
        self.cur.lastrowid = 42
        id_caja = self.repo.crear(1, 3, 2, datetime(2026, 2, 1), Decimal("120.50"), "Sin novedades")
        self.assertEqual(id_caja, 42)

    def test_crear_envia_los_parametros_en_el_orden_del_insert(self):
        fecha = datetime(2026, 2, 1)
        self.repo.crear(1, 3, 2, fecha, Decimal("120.50"), "Sin novedades")
        self.assertEqual(
            self.params_ejecutados(),
            (1, 3, 2, fecha, Decimal("120.50"), "Sin novedades"),
        )

    def test_crear_usa_un_insert_en_la_tabla_caja(self):
        self.repo.crear(1, 3, 2, datetime(2026, 2, 1), Decimal("10"), None)
        sql = self.sql_ejecutado()
        self.assertIn("INSERT INTO caja", sql)
        self.assertIn("(id_empleado, id_ruta, id_bus, fecha, monto_recaudado, observacion)", sql)

    def test_crear_acepta_observacion_nula(self):
        self.repo.crear(1, 3, 2, datetime(2026, 2, 1), Decimal("10"), None)
        self.assertIsNone(self.params_ejecutados()[5])

    def test_crear_con_bus_inexistente_lanza_integridad_error(self):
        causa = pymysql.err.IntegrityError(1452, "a foreign key constraint fails")
        self.cur.execute.side_effect = causa
        with self.assertRaises(IntegridadError) as ctx:
            self.repo.crear(1, 3, 999, datetime(2026, 2, 1), Decimal("10"), None)
        self.assertEqual(ctx.exception.codigo, 1452)
        self.assertFalse(ctx.exception.duplicado)
        self.assertFalse(ctx.exception.registro_en_uso)
        self.assertIs(ctx.exception.__cause__, causa)

    # actualizar

    def test_actualizar_envia_los_parametros_en_el_orden_del_update(self):
        fecha = datetime(2026, 2, 2)
        self.repo.actualizar(5, fecha, Decimal("99.90"), "Corregido", 1, 2)
        self.assertEqual(
            self.params_ejecutados(),
            (fecha, Decimal("99.90"), "Corregido", 1, 2, 5),
        )

    def test_actualizar_usa_un_update_filtrado_por_id_caja(self):
        self.repo.actualizar(5, datetime(2026, 2, 2), Decimal("99.90"), None, 1, 2)
        sql = self.sql_ejecutado()
        self.assertIn("UPDATE caja SET", sql)
        self.assertIn("WHERE id_caja = %s", sql)

    def test_actualizar_no_devuelve_valor(self):
        self.assertIsNone(self.repo.actualizar(5, datetime(2026, 2, 2), Decimal("1"), None, 1, 2))

    def test_actualizar_con_chofer_inexistente_lanza_integridad_error(self):
        self.cur.execute.side_effect = pymysql.err.IntegrityError(1452, "fk falla")
        with self.assertRaises(IntegridadError) as ctx:
            self.repo.actualizar(5, datetime(2026, 2, 2), Decimal("1"), None, 999, 2)
        self.assertEqual(ctx.exception.codigo, 1452)

    # eliminar

    def test_eliminar_envia_solo_el_id_de_la_caja(self):
        self.repo.eliminar(5)
        self.assertEqual(self.params_ejecutados(), (5,))

    def test_eliminar_usa_un_delete_filtrado_por_id_caja(self):
        self.repo.eliminar(5)
        self.assertEqual(self.sql_ejecutado(), "DELETE FROM caja WHERE id_caja = %s")

    def test_eliminar_no_devuelve_valor(self):
        self.assertIsNone(self.repo.eliminar(5))

    def test_error_de_bd_que_no_es_de_integridad_pasa_sin_traducir(self):
        self.cur.execute.side_effect = pymysql.err.OperationalError(2003, "sin conexion")
        with self.assertRaises(pymysql.err.OperationalError):
            self.repo.eliminar(5)

    # transacción

    def test_commit_confirma_la_transaccion_una_vez(self):
        self.repo.commit()
        self.conn.commit.assert_called_once_with()

    def test_rollback_deshace_la_transaccion_una_vez(self):
        self.repo.rollback()
        self.conn.rollback.assert_called_once_with()
