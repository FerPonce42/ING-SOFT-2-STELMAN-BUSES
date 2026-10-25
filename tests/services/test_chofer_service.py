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

class PanelChoferServiceTest(unittest.TestCase):
    def setUp(self):
        # Preparamos los mocks para reemplazar los repositorios
        self.choferes_mock = Mock()
        self.rutas_mock = Mock()
        self.servicio = ChoferService(self.choferes_mock, self.rutas_mock)

    def tearDown(self):
        self.choferes_mock = self.rutas_mock = self.servicio = None

    def test_panel_sin_ruta_activa_devuelve_datos_vacios(self):
        # Simular que el supervisor no tiene ruta activa
        self.rutas_mock.ruta_activa.return_value = None
        
        # Ejecutar
        resultado = self.servicio.panel(1)
        
        # Verificar
        self.assertEqual(resultado["choferes"], [])
        self.assertIsNone(resultado["editar_personal"])

    def test_panel_con_id_editar_formatea_fechas_iso(self):
        # Simular que tiene ruta y que se pidió editar un chofer
        self.rutas_mock.ruta_activa.return_value = 5
        self.choferes_mock.obtener.return_value = {
            "fecha_nacimiento": datetime.date(1990, 5, 1),
            "fecha_primera_licencia": datetime.date(2012, 3, 4)
        }
        
        # Ejecutar
        resultado = self.servicio.panel(1, id_editar=2)
        
        # Verificar que el servicio llamó al mock y convirtió las fechas a texto ISO
        self.choferes_mock.obtener.assert_called_once_with(2)
        self.assertEqual(resultado["editar_personal"]["fecha_nacimiento"], "1990-05-01")
        self.assertEqual(resultado["editar_personal"]["fecha_primera_licencia"], "2012-03-04")