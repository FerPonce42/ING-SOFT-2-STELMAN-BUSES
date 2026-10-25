from unittest.mock import Mock

import pytest

from app.errors import IntegridadError, ReglaNegocioError
from app.services.chofer_service import ChoferService

FORM = {"nombre": "Luis", "apellido": "Rojas", "dni": "123", "fecha_nacimiento": "1990-05-01",
        "correo": "", "telefono": "", "sueldo": "1500", "fecha_ingreso": "2025-01-10",
        "nro_licencia": "L-1", "fecha_primera_licencia": "2012-03-04", "id_tipo_licencia": "1"}


@pytest.fixture()
def choferes():
    repo = Mock()
    repo.listar_de_ruta.return_value = [{"id_empleado": 1}, {"id_empleado": 2}]
    return repo


@pytest.fixture()
def servicio(choferes):
    rutas = Mock()
    rutas.exigir_ruta_activa.return_value = 3
    rutas.ruta_activa.return_value = 3
    return ChoferService(choferes, rutas)


def test_registrar_normaliza_y_confirma(servicio, choferes):
    servicio.registrar(1, FORM)
    datos = choferes.crear.call_args.args[0]
    assert datos["correo"] is None and datos["telefono"] is None  # vacíos -> NULL
    assert str(datos["sueldo"]) == "1500" and datos["id_tipo_licencia"] == 1
    choferes.commit.assert_called_once()


@pytest.mark.parametrize("campo,valor", [
    ("nombre", ""), ("dni", "  "), ("sueldo", "-5"), ("sueldo", "abc"),
    ("fecha_nacimiento", "01/05/1990"), ("fecha_primera_licencia", "2999-01-01"),
    ("id_tipo_licencia", "x"),
])
def test_registrar_rechaza_datos_invalidos(servicio, choferes, campo, valor):
    with pytest.raises(ReglaNegocioError):
        servicio.registrar(1, {**FORM, campo: valor})
    choferes.crear.assert_not_called()


def test_registrar_traduce_duplicados_a_mensaje_claro(servicio, choferes):
    choferes.crear.side_effect = IntegridadError(1062)
    with pytest.raises(ReglaNegocioError, match="Ya existe"):
        servicio.registrar(1, FORM)
    choferes.rollback.assert_called_once()


def test_eliminar_con_historial_explica_por_que_no(servicio, choferes):
    choferes.eliminar.side_effect = IntegridadError(1451)
    with pytest.raises(ReglaNegocioError, match="No se puede eliminar"):
        servicio.eliminar(1, "1")
    choferes.rollback.assert_called_once()
    choferes.commit.assert_not_called()


def test_no_gestiona_choferes_fuera_de_su_ruta(servicio, choferes):
    with pytest.raises(ReglaNegocioError, match="no está disponible"):
        servicio.eliminar(1, "999")
    choferes.eliminar.assert_not_called()


def test_actualizar_llama_al_repositorio_con_el_id_correcto(servicio, choferes):
    servicio.actualizar(1, "2", FORM)
    assert choferes.actualizar.call_args.args[0] == 2
    choferes.commit.assert_called_once()


import unittest
import datetime
from unittest.mock import MagicMock
from app.errors import ReglaNegocioError, IntegridadError
from app.services.chofer_service import ChoferService

class ChoferServiceCoberturaTest(unittest.TestCase):
    def setUp(self):
        self.choferes_mock = MagicMock()
        self.rutas_mock = MagicMock()
        self.servicio = ChoferService(self.choferes_mock, self.rutas_mock)

    def tearDown(self):
        self.choferes_mock = self.rutas_mock = self.servicio = None

    # 1. panel con chofer a editar
    def test_panel_con_id_editar_formatea_fechas_iso(self):
        self.rutas_mock.ruta_activa.return_value = 1
        self.choferes_mock.obtener.return_value = {
            "fecha_nacimiento": datetime.date(1990, 1, 1),
            "fecha_primera_licencia": datetime.date(2010, 1, 1)
        }
        res = self.servicio.panel(1, id_editar=2)
        self.assertEqual(res["editar_personal"]["fecha_nacimiento"], "1990-01-01")

    # 2. _exigir_gestionable
    def test_exigir_gestionable_chofer_no_disponible_lanza_error(self):
        self.rutas_mock.exigir_ruta_activa.return_value = 1
        self.choferes_mock.listar_de_ruta.return_value = [{"id_empleado": 99}]
        with self.assertRaisesRegex(ReglaNegocioError, "no está disponible"):
            self.servicio._exigir_gestionable(1, 2)

    def test_exigir_gestionable_chofer_disponible_no_lanza_error(self):
        self.rutas_mock.exigir_ruta_activa.return_value = 1
        self.choferes_mock.listar_de_ruta.return_value = [{"id_empleado": 2}]
        self.servicio._exigir_gestionable(1, 2)  # Si pasa sin lanzar error, es exitoso

   # 3. _guardar con error duplicado vs otro error
    def test_guardar_error_duplicado_lanza_regla_negocio(self):
        operacion = MagicMock()
        # 1062 es el código de MySQL para duplicados
        operacion.side_effect = IntegridadError(1062) 
        
        with self.assertRaisesRegex(ReglaNegocioError, "Mensaje duplicado"):
            self.servicio._guardar(operacion, "Mensaje duplicado")

    def test_guardar_error_integridad_no_duplicado_lanza_integridad_error(self):
        operacion = MagicMock()
        # Cualquier código distinto a 1062 (ej. 9999) simula un error de integridad distinto
        operacion.side_effect = IntegridadError(9999) 
        
        with self.assertRaises(IntegridadError):
            self.servicio._guardar(operacion, "Mensaje duplicado")

    def test_guardar_error_generico_lanza_excepcion(self):
        operacion = MagicMock()
        operacion.side_effect = Exception("Falla base de datos")
        
        with self.assertRaises(Exception):
            self.servicio._guardar(operacion, "Mensaje duplicado")

    # 4. eliminar con registro en uso vs generico
    def test_eliminar_registro_en_uso_lanza_regla_negocio(self):
        self.rutas_mock.exigir_ruta_activa.return_value = 1
        self.choferes_mock.listar_de_ruta.return_value = [{"id_empleado": 2}]
        # 1451 es el código de MySQL para restricción de llave foránea (en uso)
        self.choferes_mock.eliminar.side_effect = IntegridadError(1451)
        
        with self.assertRaisesRegex(ReglaNegocioError, "No se puede eliminar"):
            self.servicio.eliminar(1, 2)

    def test_eliminar_error_generico_lanza_excepcion(self):
        self.rutas_mock.exigir_ruta_activa.return_value = 1
        self.choferes_mock.listar_de_ruta.return_value = [{"id_empleado": 2}]
        self.choferes_mock.eliminar.side_effect = Exception("Error fatal")
        
        with self.assertRaises(Exception):
            self.servicio.eliminar(1, 2)