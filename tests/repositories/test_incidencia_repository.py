import unittest
from unittest.mock import MagicMock

from app.repositories.incidencia_repository import IncidenciaRepository


class TestIncidenciaRepository(unittest.TestCase):
    def setUp(self):
        self.conn = MagicMock()
        self.cursor = self.conn.cursor.return_value.__enter__.return_value
        self.repo = IncidenciaRepository(self.conn)

    def tearDown(self):
        self.conn.reset_mock()

    def test_tipos_disciplinaria_consulta_y_devuelve_filas(self):
        self.cursor.fetchall.return_value = [{"id_tipo_disciplinaria": 2}]
        resultado = self.repo.tipos_disciplinaria()
        self.assertEqual(resultado, [{"id_tipo_disciplinaria": 2}])
        self.cursor.execute.assert_called_once_with(
            "SELECT * FROM tipo_disciplinaria ORDER BY nombre_falta", ()
        )

    def test_listar_disciplinarias_filtra_por_ruta_y_ordena_fecha(self):
        self.cursor.fetchall.return_value = [{"id_incidencia": 1}]
        resultado = self.repo.listar_disciplinarias(4)
        sql, params = self.cursor.execute.call_args.args
        self.assertIn("FROM incidencia i", sql)
        self.assertIn("WHERE i.id_ruta = %s ORDER BY i.fecha DESC", sql)
        self.assertEqual(params, (4,))
        self.assertEqual(resultado, [{"id_incidencia": 1}])

    def test_obtener_disciplinaria_filtra_por_incidencia_y_ruta(self):
        self.cursor.fetchone.return_value = {"id_incidencia": 3}
        resultado = self.repo.obtener_disciplinaria(3, 4)
        sql, params = self.cursor.execute.call_args.args
        self.assertIn("WHERE i.id_incidencia = %s AND i.id_ruta = %s", sql)
        self.assertEqual(params, (3, 4))
        self.assertEqual(resultado, {"id_incidencia": 3})

    def test_crear_disciplinaria_inserta_base_y_detalle_y_devuelve_id(self):
        self.repo._crear_base = MagicMock(return_value=12)
        self.repo._exec = MagicMock(return_value=12)
        resultado = self.repo.crear_disciplinaria(4, "2026-01-15", "Retraso", "Pendiente", 2, 5, "Aviso")
        self.assertEqual(resultado, 12)
        self.repo._crear_base.assert_called_once_with("2026-01-15", "Retraso", "Pendiente", 2, 4)
        self.repo._exec.assert_called_once_with(
            "INSERT INTO incidencia_disciplinaria (id_incidencia, id_tipo_disciplinaria, sancion) VALUES (%s, %s, %s)",
            (12, 5, "Aviso")
        )

    def test_actualizar_disciplinaria_actualiza_base_y_detalle(self):
        self.repo._actualizar_base = MagicMock()
        self.repo._exec = MagicMock()
        self.repo.actualizar_disciplinaria(12, "2026-01-15", "Retraso", "Resuelta", 2, 5, "Aviso")
        self.repo._actualizar_base.assert_called_once_with(12, "2026-01-15", "Retraso", "Resuelta", 2)
        self.repo._exec.assert_called_once_with(
            "UPDATE incidencia_disciplinaria SET id_tipo_disciplinaria = %s, sancion = %s WHERE id_incidencia = %s",
            (5, "Aviso", 12)
        )

    def test_eliminar_disciplinaria_elimina_detalle_y_base(self):
        self.repo._exec = MagicMock()
        self.repo.eliminar_disciplinaria(12)
        self.assertEqual(self.repo._exec.call_count, 2)
        self.assertEqual(self.repo._exec.call_args_list[0].args,
            ("DELETE FROM incidencia_disciplinaria WHERE id_incidencia = %s", (12,)))
        self.assertEqual(self.repo._exec.call_args_list[1].args,
            ("DELETE FROM incidencia WHERE id_incidencia = %s", (12,)))

    def test_listar_operativas_filtra_por_ruta_y_ordena_fecha(self):
        self.cursor.fetchall.return_value = []
        resultado = self.repo.listar_operativas(4)
        sql, params = self.cursor.execute.call_args.args
        self.assertIn("FROM incidencia i", sql)
        self.assertIn("WHERE i.id_ruta = %s ORDER BY i.fecha DESC", sql)
        self.assertEqual(params, (4,))
        self.assertEqual(resultado, [])

    def test_obtener_operativa_filtra_por_incidencia_y_ruta(self):
        self.cursor.fetchone.return_value = {"id_incidencia": 8}
        resultado = self.repo.obtener_operativa(8, 4)
        sql, params = self.cursor.execute.call_args.args
        self.assertIn("WHERE i.id_incidencia = %s AND i.id_ruta = %s", sql)
        self.assertEqual(params, (8, 4))
        self.assertEqual(resultado, {"id_incidencia": 8})

    def test_crear_operativa_inserta_base_y_detalle_y_devuelve_id(self):
        self.repo._crear_base = MagicMock(return_value=15)
        self.repo._exec = MagicMock(return_value=15)
        resultado = self.repo.crear_operativa(4, "2026-01-15", "Choque", "Pendiente", 2, "Grave", 100, 1)
        self.assertEqual(resultado, 15)
        self.repo._crear_base.assert_called_once_with("2026-01-15", "Choque", "Pendiente", 2, 4)
        self.repo._exec.assert_called_once_with(
            "INSERT INTO incidencia_operativa (id_incidencia, gravedad, costo, requiere_seguro) VALUES (%s, %s, %s, %s)",
            (15, "Grave", 100, 1)
        )

    def test_actualizar_operativa_actualiza_base_y_detalle(self):
        self.repo._actualizar_base = MagicMock()
        self.repo._exec = MagicMock()
        self.repo.actualizar_operativa(15, "2026-01-15", "Choque", "Resuelta", 2, "Grave", 100, 1)
        self.repo._actualizar_base.assert_called_once_with(15, "2026-01-15", "Choque", "Resuelta", 2)
        self.repo._exec.assert_called_once_with(
            "UPDATE incidencia_operativa SET gravedad = %s, costo = %s, requiere_seguro = %s WHERE id_incidencia = %s",
            ("Grave", 100, 1, 15)
        )

    def test_eliminar_operativa_elimina_detalle_y_base(self):
        self.repo._exec = MagicMock()
        self.repo.eliminar_operativa(15)
        self.assertEqual(self.repo._exec.call_count, 2)
        self.assertEqual(self.repo._exec.call_args_list[0].args,
            ("DELETE FROM incidencia_operativa WHERE id_incidencia = %s", (15,)))
        self.assertEqual(self.repo._exec.call_args_list[1].args,
            ("DELETE FROM incidencia WHERE id_incidencia = %s", (15,)))

    def test_listados_aceptan_resultados_vacios(self):
        self.cursor.fetchall.return_value = []
        self.assertEqual(self.repo.listar_disciplinarias(99), [])
        self.cursor.reset_mock()
        self.cursor.fetchall.return_value = []
        self.assertEqual(self.repo.listar_operativas(99), [])

    def test_listado_usa_fetchall_y_obtener_usa_fetchone(self):
        self.cursor.fetchall.return_value = [{"id": 1}]
        self.repo.tipos_disciplinaria()
        self.cursor.fetchall.assert_called_once()
        self.cursor.reset_mock()
        self.cursor.fetchone.return_value = {"id": 1}
        self.repo.obtener_operativa(1, 2)
        self.cursor.fetchone.assert_called_once()


if __name__ == "__main__":
    unittest.main()
