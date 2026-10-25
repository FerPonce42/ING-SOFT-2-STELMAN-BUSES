import unittest
from unittest.mock import MagicMock

from app.repositories.esquema_repository import EsquemaRepository


class EsquemaRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = EsquemaRepository(self.conn)

    def tearDown(self):
        self.conn = self.cur = self.repo = None

    def _sql(self):
        return self.cur.execute.call_args[0][0]

    def _params(self):
        return self.cur.execute.call_args[0][1]

    # nombre_bd
    def test_nombre_bd_devuelve_el_nombre_de_la_base(self):
        self.cur.fetchone.return_value = {"nombre": "stelman_db"}
        self.assertEqual(self.repo.nombre_bd(), "stelman_db")

    def test_nombre_bd_consulta_database(self):
        self.cur.fetchone.return_value = {"nombre": "stelman_db"}
        self.repo.nombre_bd()
        self.assertIn("SELECT DATABASE()", self._sql())

    # tablas
    def test_tablas_devuelve_solo_los_nombres(self):
        self.cur.fetchall.return_value = [{"TABLE_NAME": "bus"}, {"TABLE_NAME": "chofer"}]
        self.assertEqual(self.repo.tablas(), ["bus", "chofer"])

    def test_tablas_sin_resultados_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = []
        self.assertEqual(self.repo.tablas(), [])

    def test_tablas_filtra_solo_tablas_base_de_la_bd_actual(self):
        self.cur.fetchall.return_value = []
        self.repo.tablas()
        self.assertIn("BASE TABLE", self._sql())
        self.assertIn("TABLE_SCHEMA = DATABASE()", self._sql())

    # ddl
    def test_ddl_devuelve_el_create_table(self):
        self.cur.fetchone.return_value = {"Create Table": "CREATE TABLE `bus` (...)"}
        self.assertEqual(self.repo.ddl("bus"), "CREATE TABLE `bus` (...)")

    def test_ddl_consulta_show_create_table_con_la_tabla_entre_comillas(self):
        self.cur.fetchone.return_value = {"Create Table": "x"}
        self.repo.ddl("bus")
        self.assertEqual(self._sql(), "SHOW CREATE TABLE `bus`")

    # columnas
    def test_columnas_devuelve_las_filas_del_cursor(self):
        filas = [{"COLUMN_NAME": "id", "COLUMN_KEY": "PRI"}, {"COLUMN_NAME": "placa", "COLUMN_KEY": ""}]
        self.cur.fetchall.return_value = filas
        self.assertEqual(self.repo.columnas("bus"), filas)

    def test_columnas_envia_la_tabla_como_parametro(self):
        self.cur.fetchall.return_value = []
        self.repo.columnas("bus")
        self.assertEqual(self._params(), ("bus",))
        self.assertIn("%s", self._sql())

    def test_columnas_ordena_por_posicion_ordinal(self):
        self.cur.fetchall.return_value = []
        self.repo.columnas("bus")
        self.assertIn("ORDER BY ORDINAL_POSITION", self._sql())

    # claves_foraneas
    def test_claves_foraneas_devuelve_las_filas_del_cursor(self):
        filas = [{"COLUMN_NAME": "id_ruta", "REFERENCED_TABLE_NAME": "ruta", "REFERENCED_COLUMN_NAME": "id"}]
        self.cur.fetchall.return_value = filas
        self.assertEqual(self.repo.claves_foraneas("bus"), filas)

    def test_claves_foraneas_tabla_sin_fk_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = []
        self.assertEqual(self.repo.claves_foraneas("ruta"), [])

    def test_claves_foraneas_envia_la_tabla_como_parametro(self):
        self.cur.fetchall.return_value = []
        self.repo.claves_foraneas("bus")
        self.assertEqual(self._params(), ("bus",))
        self.assertIn("REFERENCED_TABLE_NAME IS NOT NULL", self._sql())

    # contar
    def test_contar_devuelve_el_total_de_registros(self):
        self.cur.fetchone.return_value = {"c": 42}
        self.assertEqual(self.repo.contar("bus"), 42)

    def test_contar_tabla_vacia_devuelve_cero(self):
        self.cur.fetchone.return_value = {"c": 0}
        self.assertEqual(self.repo.contar("bus"), 0)

    def test_contar_consulta_count_sobre_la_tabla(self):
        self.cur.fetchone.return_value = {"c": 1}
        self.repo.contar("bus")
        self.assertEqual(self._sql(), "SELECT COUNT(*) AS c FROM `bus`")

    # filas
    def test_filas_devuelve_las_filas_como_lista(self):
        filas = [{"id": 1}, {"id": 2}]
        self.cur.fetchall.return_value = filas
        self.assertEqual(self.repo.filas("bus"), filas)

    def test_filas_tabla_vacia_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = []
        self.assertEqual(self.repo.filas("bus"), [])

    def test_filas_usa_limite_1000_por_defecto(self):
        self.cur.fetchall.return_value = []
        self.repo.filas("bus")
        self.assertEqual(self._sql(), "SELECT * FROM `bus` LIMIT 1000")

    def test_filas_respeta_el_limite_indicado(self):
        self.cur.fetchall.return_value = []
        self.repo.filas("bus", limite=5)
        self.assertEqual(self._sql(), "SELECT * FROM `bus` LIMIT 5")

    def test_filas_convierte_el_limite_a_entero(self):
        self.cur.fetchall.return_value = []
        self.repo.filas("bus", limite="7")
        self.assertTrue(self._sql().endswith("LIMIT 7"))

    def test_filas_rechaza_un_limite_no_numerico_sin_ejecutar_sql(self):
        with self.assertRaises(ValueError):
            self.repo.filas("bus", limite="1; DROP TABLE bus")
        self.cur.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
