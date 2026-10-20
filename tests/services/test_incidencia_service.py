from unittest.mock import Mock

import pytest

from app.errors import ReglaNegocioError
from app.services.incidencia_service import IncidenciaService

DISC = {"fecha": "2026-01-15", "descripcion": "Retraso", "estado": "Pendiente", "id_bus": "1",
        "id_tipo_disciplinaria": "2", "sancion": "Amonestación"}
OPER = {"fecha": "2026-01-15", "descripcion": "Choque", "estado": "En revision", "id_bus": "1",
        "gravedad": "Leve", "costo": "", "requiere_seguro": "on"}


@pytest.fixture()
def repo():
    return Mock()


@pytest.fixture()
def servicio(repo):
    rutas = Mock()
    rutas.exigir_ruta_activa.return_value = 3
    rutas.ruta_activa.return_value = 3
    return IncidenciaService(repo, Mock(), rutas)


def test_registrar_disciplinaria_asocia_la_incidencia_a_la_ruta(servicio, repo):
    servicio.registrar_disciplinaria(1, DISC)
    args = repo.crear_disciplinaria.call_args.args
    assert args[0] == 3 and args[4] == 1 and args[5] == 2   # ruta, bus, tipo
    repo.commit.assert_called_once()


@pytest.mark.parametrize("cambio", [
    {"fecha": "2999-01-01"}, {"fecha": "1999-12-31"}, {"fecha": "hoy"},
    {"estado": "Inventado"}, {"descripcion": ""}, {"sancion": ""}, {"id_tipo_disciplinaria": ""},
])
def test_registrar_disciplinaria_valida(servicio, repo, cambio):
    with pytest.raises(ReglaNegocioError):
        servicio.registrar_disciplinaria(1, {**DISC, **cambio})
    repo.crear_disciplinaria.assert_not_called()


def test_operativa_sin_costo_se_guarda_en_cero_y_con_seguro(servicio, repo):
    servicio.registrar_operativa(1, OPER)
    args = repo.crear_operativa.call_args.args
    assert str(args[6]) == "0" and args[7] == 1


def test_operativa_rechaza_gravedad_desconocida(servicio, repo):
    with pytest.raises(ReglaNegocioError, match="gravedad"):
        servicio.registrar_operativa(1, {**OPER, "gravedad": "Catastrófica"})


def test_no_actualiza_ni_elimina_incidencias_de_otra_ruta(servicio, repo):
    repo.obtener_disciplinaria.return_value = None
    with pytest.raises(ReglaNegocioError, match="no pertenece"):
        servicio.actualizar_disciplinaria(1, {**DISC, "id_incidencia": "9"})
    with pytest.raises(ReglaNegocioError, match="no pertenece"):
        servicio.eliminar_disciplinaria(1, 9)
    repo.actualizar_disciplinaria.assert_not_called()
    repo.eliminar_disciplinaria.assert_not_called()


def test_rollback_si_falla_la_escritura(servicio, repo):
    repo.crear_operativa.side_effect = RuntimeError("fallo")
    with pytest.raises(RuntimeError):
        servicio.registrar_operativa(1, OPER)
    repo.rollback.assert_called_once()
    repo.commit.assert_not_called()


def test_panel_conserva_el_bus_desasignado_en_el_select(servicio, repo):
    import datetime
    servicio.buses.buses_para_seleccion.return_value = [{"id_bus": 1, "placa": "A"}]
    repo.obtener_operativa.return_value = {"id_bus": 8, "placa": "Z", "fecha": datetime.datetime(2026, 1, 2, 9, 30)}
    datos = servicio.panel_operativas(1, id_editar=5)
    assert {"id_bus": 8, "placa": "Z"} in datos["buses"]
    assert datos["editar_incidencia"]["fecha"] == "2026-01-02"  # el <input type=date> no acepta datetime
