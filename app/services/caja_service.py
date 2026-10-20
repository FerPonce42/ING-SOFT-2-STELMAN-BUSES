from datetime import date

from app.errors import ReglaNegocioError
from app.services import validaciones as v


class CajaService:
    def __init__(self, cajas, choferes, buses, rutas):
        self.cajas = cajas
        self.choferes = choferes  # ChoferRepository: quienes recaudan ahora son los choferes
        self.buses = buses        # BusRepository
        self.rutas = rutas        # RutaService

    def panel(self, id_supervisor, id_editar=None):
        id_ruta = self.rutas.ruta_activa(id_supervisor)
        datos = {"id_ruta": id_ruta, "cajas": [], "empleados": [], "buses": [],
                 "editar_caja": None, "hoy": date.today().isoformat()}
        if not id_ruta:
            return datos
        datos["cajas"] = self.cajas.listar_de_ruta(id_ruta)
        datos["empleados"] = self.choferes.listar_de_ruta(id_ruta)
        datos["buses"] = self.buses.buses_para_seleccion(id_ruta)
        if id_editar:
            fila = self.cajas.obtener(id_editar, id_ruta)
            if fila:
                fila["fecha"] = v.a_fecha_iso(fila["fecha"])
            datos["editar_caja"] = fila
        return datos

    def _datos(self, form):
        return {
            "fecha": v.fecha(form.get("fecha")),
            "monto": v.decimal(form.get("monto"), "El monto", permitir_igual=False),
            "observacion": v.texto_opcional(form.get("observacion")),
            "id_empleado": v.entero(form.get("id_empleado"), "El chofer"),
            "id_bus": v.entero(form.get("id_bus"), "El bus"),
        }

    def _transaccion(self, operacion):
        try:
            operacion()
            self.cajas.commit()
        except Exception:
            self.cajas.rollback()
            raise

    def registrar(self, id_supervisor, form):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        d = self._datos(form)
        self._transaccion(lambda: self.cajas.crear(
            d["id_empleado"], id_ruta, d["id_bus"], d["fecha"], d["monto"], d["observacion"]))

    def actualizar(self, id_supervisor, form):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        id_caja = v.entero(form.get("id_caja"), "La recaudación")
        if not self.cajas.obtener(id_caja, id_ruta):
            raise ReglaNegocioError("La recaudación no existe o no pertenece a tu ruta.")
        d = self._datos(form)
        self._transaccion(lambda: self.cajas.actualizar(
            id_caja, d["fecha"], d["monto"], d["observacion"], d["id_empleado"], d["id_bus"]))

    def eliminar(self, id_supervisor, id_caja):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        if not self.cajas.obtener(id_caja, id_ruta):
            raise ReglaNegocioError("La recaudación no existe o no pertenece a tu ruta.")
        self._transaccion(lambda: self.cajas.eliminar(id_caja))
