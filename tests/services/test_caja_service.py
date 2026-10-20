from unittest.mock import Mock

import pytest

from app.errors import ReglaNegocioError
from app.services.caja_service import CajaService

FORM = {"fecha": "2026-02-01", "monto": "120.50", "observacion": "", "id_empleado": "1", "id_bus": "2"}


@pytest.fixture()
def cajas():
    return Mock()


@pytest.fixture()
def servicio(cajas):
    rutas = Mock()
    rutas.exigir_ruta_activa.return_value = 3
    rutas.ruta_activa.return_value = 3
    return CajaService(cajas, Mock(), Mock(), rutas)


def test_registrar_guarda_en_la_ruta_del_supervisor(servicio, cajas):
    servicio.registrar(1, FORM)
    id_emp, id_ruta, id_bus, fecha, monto, obs = cajas.crear.call_args.args
    assert (id_emp, id_ruta, id_bus, obs) == (1, 3, 2, None)
    assert str(monto) == "120.50" and fecha.isoformat() == "2026-02-01"
    cajas.commit.assert_called_once()


@pytest.mark.parametrize("monto", ["0", "-10", "abc", ""])
def test_registrar_rechaza_montos_invalidos(servicio, cajas, monto):
    with pytest.raises(ReglaNegocioError):
        servicio.registrar(1, {**FORM, "monto": monto})
    cajas.crear.assert_not_called()


def test_registrar_rechaza_fecha_futura(servicio):
    with pytest.raises(ReglaNegocioError, match="fuera del rango"):
        servicio.registrar(1, {**FORM, "fecha": "2999-01-01"})


def test_no_edita_ni_borra_cajas_de_otra_ruta(servicio, cajas):
    cajas.obtener.return_value = None
    with pytest.raises(ReglaNegocioError):
        servicio.actualizar(1, {**FORM, "id_caja": "5"})
    with pytest.raises(ReglaNegocioError):
        servicio.eliminar(1, 5)
    cajas.actualizar.assert_not_called()
    cajas.eliminar.assert_not_called()


def test_panel_entrega_la_fecha_lista_para_el_input_date(servicio, cajas):
    import datetime
    cajas.obtener.return_value = {"id_caja": 5, "fecha": datetime.datetime(2026, 9, 6, 14, 15)}
    assert servicio.panel(1, id_editar=5)["editar_caja"]["fecha"] == "2026-09-06"
