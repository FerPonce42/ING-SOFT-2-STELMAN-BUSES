import unittest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.errors import IntegridadError, ReglaNegocioError
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


class CajaServiceConMocksTest(unittest.TestCase):
    """Issue #15 - casos que faltaban: panel, transacciones y validaciones de registrar/actualizar/eliminar."""

    NO_EXISTE = "La recaudación no existe o no pertenece a tu ruta."

    def setUp(self):
        self.cajas = Mock()
        self.choferes = Mock()
        self.buses = Mock()
        self.rutas = Mock()
        self.rutas.ruta_activa.return_value = 3
        self.rutas.exigir_ruta_activa.return_value = 3
        self.servicio = CajaService(self.cajas, self.choferes, self.buses, self.rutas)
        self.form = {"fecha": "2026-02-01", "monto": "120.50", "observacion": "",
                     "id_empleado": "1", "id_bus": "2"}

    def tearDown(self):
        self.cajas = self.choferes = self.buses = self.rutas = None
        self.servicio = self.form = None

    def sin_ruta_activa(self):
        self.rutas.ruta_activa.return_value = None
        self.rutas.exigir_ruta_activa.side_effect = ReglaNegocioError("No tienes una ruta activa.")

    # panel

    def test_panel_sin_ruta_activa_devuelve_datos_vacios(self):
        self.rutas.ruta_activa.return_value = None
        datos = self.servicio.panel(1)
        self.assertIsNone(datos["id_ruta"])
        self.assertEqual((datos["cajas"], datos["empleados"], datos["buses"]), ([], [], []))
        self.assertIsNone(datos["editar_caja"])

    def test_panel_sin_ruta_activa_no_consulta_repositorios(self):
        self.rutas.ruta_activa.return_value = None
        self.servicio.panel(1)
        self.cajas.listar_de_ruta.assert_not_called()
        self.choferes.listar_de_ruta.assert_not_called()
        self.buses.buses_para_seleccion.assert_not_called()

    def test_panel_con_ruta_carga_cajas_choferes_y_buses_de_esa_ruta(self):
        self.cajas.listar_de_ruta.return_value = [{"id_caja": 1}]
        self.choferes.listar_de_ruta.return_value = [{"id_empleado": 1}]
        self.buses.buses_para_seleccion.return_value = [{"id_bus": 2}]
        datos = self.servicio.panel(1)
        self.assertEqual(datos["id_ruta"], 3)
        self.assertEqual(datos["cajas"], [{"id_caja": 1}])
        self.assertEqual(datos["empleados"], [{"id_empleado": 1}])
        self.assertEqual(datos["buses"], [{"id_bus": 2}])
        self.cajas.listar_de_ruta.assert_called_once_with(3)
        self.choferes.listar_de_ruta.assert_called_once_with(3)
        self.buses.buses_para_seleccion.assert_called_once_with(3)

    def test_panel_entrega_la_fecha_de_hoy_en_formato_iso(self):
        self.assertEqual(self.servicio.panel(1)["hoy"], date.today().isoformat())

    def test_panel_sin_id_editar_no_busca_ninguna_caja(self):
        datos = self.servicio.panel(1)
        self.assertIsNone(datos["editar_caja"])
        self.cajas.obtener.assert_not_called()

    def test_panel_con_id_editar_inexistente_deja_editar_caja_en_none(self):
        self.cajas.obtener.return_value = None
        datos = self.servicio.panel(1, id_editar=5)
        self.assertIsNone(datos["editar_caja"])
        self.cajas.obtener.assert_called_once_with(5, 3)

    def test_panel_con_recaudacion_a_editar_convierte_la_fecha_a_texto_iso(self):
        self.cajas.obtener.return_value = {"id_caja": 5, "fecha": datetime(2026, 9, 6, 14, 15)}
        datos = self.servicio.panel(1, id_editar=5)
        self.assertEqual(datos["editar_caja"]["fecha"], "2026-09-06")
        self.cajas.obtener.assert_called_once_with(5, 3)

    def test_panel_con_fecha_tipo_date_tambien_la_convierte_a_texto_iso(self):
        self.cajas.obtener.return_value = {"id_caja": 5, "fecha": date(2026, 9, 6)}
        self.assertEqual(self.servicio.panel(1, id_editar=5)["editar_caja"]["fecha"], "2026-09-06")

    # registrar

    def test_registrar_sin_ruta_activa_lanza_error_y_no_guarda(self):
        self.sin_ruta_activa()
        with self.assertRaises(ReglaNegocioError):
            self.servicio.registrar(1, self.form)
        self.cajas.crear.assert_not_called()
        self.cajas.commit.assert_not_called()

    def test_registrar_recorta_la_observacion(self):
        self.form["observacion"] = "  Sin novedades  "
        self.servicio.registrar(1, self.form)
        self.assertEqual(self.cajas.crear.call_args.args[5], "Sin novedades")

    def test_registrar_conserva_los_decimales_del_monto(self):
        self.servicio.registrar(1, self.form)
        self.assertEqual(self.cajas.crear.call_args.args[4], Decimal("120.50"))

    def test_registrar_con_chofer_invalido_lanza_error_y_no_guarda(self):
        self.form["id_empleado"] = "abc"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio.registrar(1, self.form)
        self.assertEqual(str(ctx.exception), "El chofer no es válido.")
        self.cajas.crear.assert_not_called()

    def test_registrar_con_bus_vacio_lanza_error_y_no_guarda(self):
        self.form["id_bus"] = ""
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio.registrar(1, self.form)
        self.assertEqual(str(ctx.exception), "El bus no es válido.")
        self.cajas.crear.assert_not_called()

    def test_registrar_con_fecha_de_formato_invalido_lanza_error(self):
        self.form["fecha"] = "01/02/2026"
        with self.assertRaises(ReglaNegocioError):
            self.servicio.registrar(1, self.form)
        self.cajas.crear.assert_not_called()

    def test_registrar_con_datos_invalidos_no_abre_transaccion(self):
        self.form["monto"] = "0"
        with self.assertRaises(ReglaNegocioError):
            self.servicio.registrar(1, self.form)
        self.cajas.commit.assert_not_called()
        self.cajas.rollback.assert_not_called()

    def test_registrar_si_falla_la_bd_hace_rollback_y_relanza_el_error(self):
        self.cajas.crear.side_effect = IntegridadError(1452, "fk falla")
        with self.assertRaises(IntegridadError):
            self.servicio.registrar(1, self.form)
        self.cajas.rollback.assert_called_once_with()
        self.cajas.commit.assert_not_called()

    # actualizar

    def test_actualizar_guarda_los_datos_nuevos_y_confirma(self):
        self.cajas.obtener.return_value = {"id_caja": 5}
        self.form.update({"id_caja": "5", "monto": "99.90", "observacion": " Corregido "})
        self.servicio.actualizar(1, self.form)
        self.cajas.obtener.assert_called_once_with(5, 3)
        self.cajas.actualizar.assert_called_once_with(
            5, date(2026, 2, 1), Decimal("99.90"), "Corregido", 1, 2)
        self.cajas.commit.assert_called_once_with()

    def test_actualizar_con_id_caja_invalido_lanza_error_sin_consultar(self):
        self.form["id_caja"] = "abc"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio.actualizar(1, self.form)
        self.assertEqual(str(ctx.exception), "La recaudación no es válido.")
        self.cajas.obtener.assert_not_called()

    def test_actualizar_caja_de_otra_ruta_lanza_el_mensaje_esperado(self):
        self.cajas.obtener.return_value = None
        self.form["id_caja"] = "5"
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio.actualizar(1, self.form)
        self.assertEqual(str(ctx.exception), self.NO_EXISTE)

    def test_actualizar_con_monto_invalido_no_modifica_la_caja(self):
        self.cajas.obtener.return_value = {"id_caja": 5}
        self.form.update({"id_caja": "5", "monto": "-5"})
        with self.assertRaises(ReglaNegocioError):
            self.servicio.actualizar(1, self.form)
        self.cajas.actualizar.assert_not_called()
        self.cajas.commit.assert_not_called()

    def test_actualizar_sin_ruta_activa_lanza_error_y_no_consulta(self):
        self.sin_ruta_activa()
        self.form["id_caja"] = "5"
        with self.assertRaises(ReglaNegocioError):
            self.servicio.actualizar(1, self.form)
        self.cajas.obtener.assert_not_called()

    def test_actualizar_si_falla_la_bd_hace_rollback_y_relanza_el_error(self):
        self.cajas.obtener.return_value = {"id_caja": 5}
        self.cajas.actualizar.side_effect = RuntimeError("bd caida")
        self.form["id_caja"] = "5"
        with self.assertRaises(RuntimeError):
            self.servicio.actualizar(1, self.form)
        self.cajas.rollback.assert_called_once_with()
        self.cajas.commit.assert_not_called()

    # eliminar

    def test_eliminar_caja_propia_la_borra_y_confirma(self):
        self.cajas.obtener.return_value = {"id_caja": 5}
        self.servicio.eliminar(1, 5)
        self.cajas.obtener.assert_called_once_with(5, 3)
        self.cajas.eliminar.assert_called_once_with(5)
        self.cajas.commit.assert_called_once_with()

    def test_eliminar_caja_inexistente_lanza_el_mensaje_esperado(self):
        self.cajas.obtener.return_value = None
        with self.assertRaises(ReglaNegocioError) as ctx:
            self.servicio.eliminar(1, 5)
        self.assertEqual(str(ctx.exception), self.NO_EXISTE)

    def test_eliminar_sin_ruta_activa_lanza_error_y_no_borra(self):
        self.sin_ruta_activa()
        with self.assertRaises(ReglaNegocioError):
            self.servicio.eliminar(1, 5)
        self.cajas.eliminar.assert_not_called()

    def test_eliminar_si_falla_la_bd_hace_rollback_y_relanza_el_error(self):
        self.cajas.obtener.return_value = {"id_caja": 5}
        self.cajas.eliminar.side_effect = IntegridadError(1451, "fila en uso")
        with self.assertRaises(IntegridadError):
            self.servicio.eliminar(1, 5)
        self.cajas.rollback.assert_called_once_with()
        self.cajas.commit.assert_not_called()
