"""Issue #2 - Pruebas de repositorio con conexión falsa (sin base de datos real)."""
import unittest
from unittest.mock import MagicMock

import pymysql

from app.errors import IntegridadError
from app.repositories.base import BaseRepository
from app.repositories.cuenta_repository import CuentaRepository
from app.repositories.ruta_repository import RutaRepository


class RepositorioConConexionFalsa(unittest.TestCase):
    """Prepara una conexión y un cursor falsos que usan todas las pruebas."""

    clase_repositorio = BaseRepository

    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = self.clase_repositorio(self.conn)

    def tearDown(self):
        self.conn = self.cur = self.repo = None

    def sql_ejecutado(self):
        return self.cur.execute.call_args[0][0]

    def params_ejecutados(self):
        return self.cur.execute.call_args[0][1]


class BaseRepositoryTest(RepositorioConConexionFalsa):
    def test_all_devuelve_las_filas_como_lista(self):
        self.cur.fetchall.return_value = ({"id": 1}, {"id": 2})
        filas = self.repo._all("SELECT * FROM t WHERE x = %s", (5,))
        self.assertEqual(filas, [{"id": 1}, {"id": 2}])
        self.cur.execute.assert_called_once_with("SELECT * FROM t WHERE x = %s", (5,))

    def test_all_sin_resultados_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = ()
        self.assertEqual(self.repo._all("SELECT 1"), [])

    def test_all_sin_params_usa_tupla_vacia(self):
        self.cur.fetchall.return_value = []
        self.repo._all("SELECT 1")
        self.cur.execute.assert_called_once_with("SELECT 1", ())

    def test_one_devuelve_la_primera_fila(self):
        self.cur.fetchone.return_value = {"id": 7}
        self.assertEqual(self.repo._one("SELECT * FROM t WHERE id = %s", (7,)), {"id": 7})

    def test_one_sin_resultado_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo._one("SELECT * FROM t WHERE id = %s", (99,)))

    def test_exec_devuelve_el_lastrowid(self):
        self.cur.lastrowid = 42
        self.assertEqual(self.repo._exec("INSERT INTO t VALUES (%s)", (1,)), 42)
        self.cur.execute.assert_called_once_with("INSERT INTO t VALUES (%s)", (1,))

    def test_exec_traduce_duplicado_1062_a_integridad_error(self):
        original = pymysql.err.IntegrityError(1062, "Duplicate entry")
        self.cur.execute.side_effect = original
        with self.assertRaises(IntegridadError) as ctx:
            self.repo._exec("INSERT INTO t VALUES (%s)", (1,))
        self.assertEqual(ctx.exception.codigo, 1062)
        self.assertTrue(ctx.exception.duplicado)
        self.assertIs(ctx.exception.__cause__, original)

    def test_exec_traduce_registro_en_uso_1451_a_integridad_error(self):
        self.cur.execute.side_effect = pymysql.err.IntegrityError(1451, "Cannot delete")
        with self.assertRaises(IntegridadError) as ctx:
            self.repo._exec("DELETE FROM t WHERE id = %s", (1,))
        self.assertEqual(ctx.exception.codigo, 1451)
        self.assertTrue(ctx.exception.registro_en_uso)

    def test_exec_no_traduce_otros_errores_de_base_de_datos(self):
        self.cur.execute.side_effect = pymysql.err.OperationalError(2003, "Sin conexión")
        with self.assertRaises(pymysql.err.OperationalError):
            self.repo._exec("INSERT INTO t VALUES (%s)", (1,))

    def test_commit_confirma_en_la_conexion(self):
        self.repo.commit()
        self.conn.commit.assert_called_once_with()

    def test_rollback_deshace_en_la_conexion(self):
        self.repo.rollback()
        self.conn.rollback.assert_called_once_with()


class CuentaRepositoryTest(RepositorioConConexionFalsa):
    clase_repositorio = CuentaRepository

    def test_por_usuario_devuelve_la_cuenta_encontrada(self):
        cuenta = {"id_cuenta": 1, "nombre_usuario": "admin", "nombre_cargo": "General"}
        self.cur.fetchone.return_value = cuenta
        self.assertEqual(self.repo.por_usuario("admin"), cuenta)

    def test_por_usuario_envia_el_nombre_como_parametro(self):
        self.cur.fetchone.return_value = None
        self.repo.por_usuario("admin")
        self.assertEqual(self.params_ejecutados(), ("admin",))
        self.assertIn("cuenta_usuario", self.sql_ejecutado())

    def test_por_usuario_inexistente_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.por_usuario("nadie"))


class RutaRepositoryTest(RepositorioConConexionFalsa):
    clase_repositorio = RutaRepository

    def test_ruta_activa_devuelve_el_id_de_la_ruta(self):
        self.cur.fetchone.return_value = {"id_ruta": 3}
        self.assertEqual(self.repo.ruta_activa_de_supervisor(10), 3)
        self.assertEqual(self.params_ejecutados(), (10,))

    def test_ruta_activa_sin_asignacion_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.ruta_activa_de_supervisor(10))

    def test_obtener_devuelve_la_ruta_por_id(self):
        self.cur.fetchone.return_value = {"id_ruta": 4, "codigo_ruta": "R-4"}
        self.assertEqual(self.repo.obtener(4)["codigo_ruta"], "R-4")
        self.assertEqual(self.params_ejecutados(), (4,))

    def test_obtener_inexistente_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.obtener(999))

    def test_obtener_por_codigo_devuelve_la_ruta(self):
        self.cur.fetchone.return_value = {"id_ruta": 4, "codigo_ruta": "R-4"}
        self.assertEqual(self.repo.obtener_por_codigo("R-4")["id_ruta"], 4)
        self.assertEqual(self.params_ejecutados(), ("R-4",))

    def test_obtener_por_codigo_inexistente_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.obtener_por_codigo("X"))

    def test_listar_publicas_devuelve_las_rutas_ordenadas_por_codigo(self):
        self.cur.fetchall.return_value = [{"codigo_ruta": "R-1"}, {"codigo_ruta": "R-2"}]
        self.assertEqual(len(self.repo.listar_publicas()), 2)
        sql = self.sql_ejecutado()
        self.assertIn("ORDER BY r.codigo_ruta", sql)
        self.assertIn("AS origen", sql)
        self.assertIn("AS destino", sql)

    def test_paraderos_de_ruta_devuelve_los_paraderos(self):
        self.cur.fetchall.return_value = [{"nombre": "A", "orden": 1}, {"nombre": "B", "orden": 2}]
        paraderos = self.repo.paraderos_de_ruta(4)
        self.assertEqual([p["nombre"] for p in paraderos], ["A", "B"])
        self.assertEqual(self.params_ejecutados(), (4,))

    def test_contar_buses_activos_devuelve_el_total(self):
        self.cur.fetchone.return_value = {"total": 5}
        self.assertEqual(self.repo.contar_buses_activos(4), 5)
        self.assertEqual(self.params_ejecutados(), (4,))

    def test_recaudacion_de_hoy_devuelve_el_total(self):
        self.cur.fetchone.return_value = {"total": 150.5}
        self.assertEqual(self.repo.recaudacion_de_hoy(4), 150.5)
        self.assertEqual(self.params_ejecutados(), (4,))

    def test_contar_incidencias_abiertas_arma_un_marcador_por_estado(self):
        self.cur.fetchone.return_value = {"total": 2}
        total = self.repo.contar_incidencias_abiertas(["Pendiente", "En proceso", "Reportada"])
        self.assertEqual(total, 2)
        self.assertIn("IN (%s, %s, %s)", self.sql_ejecutado())
        self.assertEqual(self.params_ejecutados(), ("Pendiente", "En proceso", "Reportada"))


if __name__ == "__main__":
    unittest.main()
