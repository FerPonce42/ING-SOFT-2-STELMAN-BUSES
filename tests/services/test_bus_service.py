from datetime import date
from unittest.mock import Mock

import pytest

from app.errors import ReglaNegocioError
from app.services.bus_service import BusService


@pytest.fixture()
def buses():
    repo = Mock()
    repo.existe_placa.return_value = False
    repo.crear.return_value = 10
    return repo


@pytest.fixture()
def rutas():
    svc = Mock()
    svc.exigir_ruta_activa.return_value = 3
    svc.ruta_activa.return_value = 3
    return svc


@pytest.fixture()
def servicio(buses, rutas):
    return BusService(buses, rutas, id_almacen_por_defecto=5)


def test_registrar_crea_bus_lo_asigna_a_la_ruta_y_confirma(servicio, buses):
    assert servicio.registrar(1, " abc-123 ", "2024", "2") == 10
    buses.crear.assert_called_once_with("ABC-123", 2024, 2, 5)
    buses.asignar_a_ruta.assert_called_once_with(10, 3)
    buses.commit.assert_called_once()
    buses.rollback.assert_not_called()


def test_registrar_hace_rollback_si_falla_la_asignacion(servicio, buses):
    buses.asignar_a_ruta.side_effect = RuntimeError("fallo BD")
    with pytest.raises(RuntimeError):
        servicio.registrar(1, "ABC-123", "2024", "2")
    buses.rollback.assert_called_once()
    buses.commit.assert_not_called()


def test_registrar_rechaza_placa_duplicada(servicio, buses):
    buses.existe_placa.return_value = True
    with pytest.raises(ReglaNegocioError, match="ya está registrada"):
        servicio.registrar(1, "ABC-123", "2024", "2")
    buses.crear.assert_not_called()


def test_registrar_sin_ruta_activa_no_toca_la_bd(servicio, buses, rutas):
    rutas.exigir_ruta_activa.side_effect = ReglaNegocioError("No tienes una ruta activa asignada.")
    with pytest.raises(ReglaNegocioError, match="ruta activa"):
        servicio.registrar(1, "ABC-123", "2024", "2")
    buses.existe_placa.assert_not_called()


@pytest.mark.parametrize("anio", ["1949", "abc", "", str(date.today().year + 2)])
def test_registrar_valida_el_anio(servicio, anio):
    with pytest.raises(ReglaNegocioError):
        servicio.registrar(1, "ABC-123", anio, "2")


def test_registrar_exige_placa(servicio):
    with pytest.raises(ReglaNegocioError, match="placa"):
        servicio.registrar(1, "   ", "2024", "2")


def test_editar_bus_ajeno_es_rechazado(servicio, buses):
    buses.obtener_de_supervisor.return_value = None
    with pytest.raises(ReglaNegocioError, match="no está asignado"):
        servicio.editar(1, 99, "ABC-123", "2024", "2")
    buses.actualizar.assert_not_called()


def test_editar_permite_conservar_su_propia_placa(servicio, buses):
    buses.obtener_de_supervisor.return_value = {"id_bus": 4}
    servicio.editar(1, 4, "abc-123", "2024", "2")
    buses.existe_placa.assert_called_once_with("ABC-123", excluir_id_bus=4)
    buses.actualizar.assert_called_once_with(4, "ABC-123", 2024, 2)
    buses.commit.assert_called_once()


def test_desasignar_solo_si_el_bus_es_del_supervisor(servicio, buses):
    buses.obtener_de_supervisor.return_value = None
    with pytest.raises(ReglaNegocioError, match="Acceso denegado"):
        servicio.desasignar(1, 99)
    buses.desasignar.assert_not_called()


def test_panel_sin_ruta_devuelve_listas_vacias(servicio, rutas, buses):
    rutas.ruta_activa.return_value = None
    datos = servicio.panel(1)
    assert datos["buses"] == [] and datos["modelos"] == [] and datos["id_ruta"] is None
    buses.buses_de_ruta.assert_not_called()


def test_panel_avisa_si_el_bus_a_editar_no_esta_en_la_ruta(servicio, buses):
    buses.obtener_de_supervisor.return_value = None
    assert "no existe" in servicio.panel(1, id_editar=99)["error_edicion"]
