from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.errors import ReglaNegocioError
from app.services.ruta_service import ESTADOS_ABIERTOS, RutaService


@pytest.fixture()
def repo():
    return Mock()


def test_exigir_ruta_activa_falla_sin_asignacion(repo):
    repo.ruta_activa_de_supervisor.return_value = None
    with pytest.raises(ReglaNegocioError, match="ruta activa"):
        RutaService(repo).exigir_ruta_activa(1)


def test_dashboard_con_ruta_calcula_kpis(repo):
    repo.ruta_activa_de_supervisor.return_value = 1
    repo.obtener.return_value = {"codigo_ruta": "EX-101"}
    repo.contar_buses_activos.return_value = 4
    repo.recaudacion_de_hoy.return_value = Decimal("1234.5")
    repo.contar_incidencias_abiertas.return_value = 2
    kpis = RutaService(repo).dashboard(1)
    assert kpis["kpi_buses"] == 4 and kpis["kpi_recaudacion"] == "S/. 1,234.50" and kpis["kpi_incidencias"] == 2
    assert "EX-101" in kpis["mensaje_ruta"]
    repo.contar_incidencias_abiertas.assert_called_once_with(ESTADOS_ABIERTOS)


def test_dashboard_sin_ruta_muestra_ceros(repo):
    repo.ruta_activa_de_supervisor.return_value = None
    repo.contar_incidencias_abiertas.return_value = 0
    kpis = RutaService(repo).dashboard(1)
    assert kpis["kpi_buses"] == 0 and kpis["kpi_recaudacion"] == "S/. 0.00"
    repo.contar_buses_activos.assert_not_called()


def test_detalle_publico_convierte_coordenadas_a_float(repo):
    repo.obtener_por_codigo.return_value = {"id_ruta": 1, "codigo_ruta": "EX-101"}
    repo.paraderos_de_ruta.return_value = [{"nombre": "A", "lat": Decimal("-16.40904"), "lng": Decimal("-71.53745")}]
    detalle = RutaService(repo).detalle_publico("EX-101")
    assert detalle["paraderos"][0]["lat"] == -16.40904 and isinstance(detalle["paraderos"][0]["lng"], float)


def test_detalle_publico_de_ruta_inexistente_devuelve_none(repo):
    repo.obtener_por_codigo.return_value = None
    assert RutaService(repo).detalle_publico("X") is None
