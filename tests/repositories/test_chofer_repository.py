import unittest
from unittest.mock import MagicMock
from app.repositories.chofer_repository import ChoferRepository

class ChoferRepositoryTest(unittest.TestCase):
    def setUp(self):
        # Simulamos la conexión a la base de datos (conexión falsa)
        self.conn = MagicMock()
        self.cur = self.conn.cursor.return_value.__enter__.return_value
        self.repo = ChoferRepository(self.conn)

    def tearDown(self):
        self.conn = self.cur = self.repo = None

    def test_obtener_sin_resultado_devuelve_none(self):
        # Preparamos el mock para simular que no existe el empleado en la DB
        self.cur.fetchone.return_value = None
        
        # Ejecutamos el método real y verificamos
        self.assertIsNone(self.repo.obtener(999))
        
    def test_listar_de_ruta_sin_resultados_devuelve_lista_vacia(self):
        # Preparamos el mock para devolver 0 registros
        self.cur.fetchall.return_value = []
        
        # Ejecutamos el método real para la ruta 1
        self.assertEqual(self.repo.listar_de_ruta(1), [])

    def test_tipos_licencia_sin_resultados_devuelve_lista_vacia(self):
        # Preparamos el mock para devolver 0 registros
        self.cur.fetchall.return_value = []
        
        self.assertEqual(self.repo.tipos_licencia(), [])