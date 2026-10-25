import unittest
from unittest.mock import MagicMock
from app.repositories.chofer_repository import ChoferRepository

class ChoferRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = ChoferRepository(self.conn)

    def tearDown(self):
        self.conn = self.cur = self.repo = None

    # --- tipos_licencia ---
    def test_tipos_licencia_vacio_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = []
        self.assertEqual(self.repo.tipos_licencia(), [])

    def test_tipos_licencia_con_datos_devuelve_lista_y_verifica_sql(self):
        self.cur.fetchall.return_value = [{"id_tipo_licencia": 1, "categoria": "A"}]
        res = self.repo.tipos_licencia()
        self.assertEqual(res, [{"id_tipo_licencia": 1, "categoria": "A"}])
        args = self.cur.execute.call_args[0]
        self.assertIn("SELECT * FROM tipo_licencia", args[0])

    # --- obtener ---
    def test_obtener_sin_resultado_devuelve_none(self):
        self.cur.fetchone.return_value = None
        self.assertIsNone(self.repo.obtener(999))

    def test_obtener_con_datos_devuelve_diccionario_y_verifica_sql(self):
        self.cur.fetchone.return_value = {"id_empleado": 1, "nombre": "Juan"}
        res = self.repo.obtener(1)
        self.assertEqual(res, {"id_empleado": 1, "nombre": "Juan"})
        args = self.cur.execute.call_args[0]
        self.assertIn("WHERE e.id_empleado = %s", args[0])
        self.assertEqual(args[1], (1,))

    # --- listar_de_ruta ---
    def test_listar_de_ruta_sin_resultados_devuelve_lista_vacia(self):
        self.cur.fetchall.return_value = []
        self.assertEqual(self.repo.listar_de_ruta(5), [])

    def test_listar_de_ruta_con_datos_devuelve_lista_y_verifica_sql(self):
        self.cur.fetchall.return_value = [{"id_empleado": 1}]
        res = self.repo.listar_de_ruta(5)
        self.assertEqual(res, [{"id_empleado": 1}])
        args = self.cur.execute.call_args[0]
        self.assertIn("WHERE br.id_ruta = %s", args[0])
        self.assertEqual(args[1], (5,))

    # --- crear ---
    def test_crear_ejecuta_dos_inserts_verifica_parametros_y_devuelve_id(self):
        self.cur.lastrowid = 10
        datos = {
            "dni": "123", "nombre": "N", "apellido": "A", "fecha_nacimiento": "1990-01-01",
            "correo": "c@c.com", "sueldo": 100, "telefono": "123", "fecha_ingreso": "2020-01-01",
            "nro_licencia": "L-1", "fecha_primera_licencia": "2010-01-01", "id_tipo_licencia": 1
        }
        res = self.repo.crear(datos)
        
        self.assertEqual(res, 10)
        self.assertEqual(self.cur.execute.call_count, 2)
        
        # Verificar INSERT en empleado
        args_emp = self.cur.execute.call_args_list[0][0]
        self.assertIn("INSERT INTO empleado", args_emp[0])
        self.assertEqual(args_emp[1], ("123", "N", "A", "1990-01-01", "c@c.com", 100, "123", "2020-01-01"))
        
        # Verificar INSERT en chofer
        args_chof = self.cur.execute.call_args_list[1][0]
        self.assertIn("INSERT INTO chofer", args_chof[0])
        self.assertEqual(args_chof[1], (10, "L-1", "2010-01-01", 1))

    # --- actualizar ---
    def test_actualizar_ejecuta_dos_updates_y_verifica_parametros(self):
        datos = {
            "dni": "123", "nombre": "N", "apellido": "A", "fecha_nacimiento": "1990-01-01",
            "correo": "c@c.com", "sueldo": 100, "telefono": "123",
            "nro_licencia": "L-1", "fecha_primera_licencia": "2010-01-01", "id_tipo_licencia": 1
        }
        self.repo.actualizar(10, datos)
        
        self.assertEqual(self.cur.execute.call_count, 2)
        args_emp = self.cur.execute.call_args_list[0][0]
        self.assertIn("UPDATE empleado", args_emp[0])
        self.assertEqual(args_emp[1], ("123", "N", "A", "1990-01-01", "c@c.com", 100, "123", 10))

    # --- eliminar ---
    def test_eliminar_ejecuta_dos_deletes_y_verifica_parametros(self):
        self.repo.eliminar(10)
        
        self.assertEqual(self.cur.execute.call_count, 2)
        args_chof = self.cur.execute.call_args_list[0][0]
        self.assertIn("DELETE FROM chofer", args_chof[0])
        self.assertEqual(args_chof[1], (10,))
        
        args_emp = self.cur.execute.call_args_list[1][0]
        self.assertIn("DELETE FROM empleado", args_emp[0])
        self.assertEqual(args_emp[1], (10,))