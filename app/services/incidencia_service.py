from app.errors import ReglaNegocioError
from app.services import validaciones as v

ESTADOS = ("Pendiente", "En revision", "Resuelta", "Cancelada")
GRAVEDADES = ("Leve", "Moderada", "Grave")


class IncidenciaService:
    def __init__(self, incidencias, buses, rutas):
        self.incidencias = incidencias
        self.buses = buses    # BusRepository (solo para el <select> de buses)
        self.rutas = rutas    # RutaService

    # ---------- utilidades ----------
    def _estado(self, valor):
        if valor not in ESTADOS:
            raise ReglaNegocioError("El estado seleccionado no es válido.")
        return valor

    def _base(self, form):
        return {
            "fecha": v.fecha(form.get("fecha")),
            "descripcion": v.texto_requerido(form.get("descripcion"), "La descripción", 500),
            "estado": self._estado(form.get("estado")),
            "id_bus": v.entero(form.get("id_bus"), "El bus"),
        }

    def _transaccion(self, operacion):
        try:
            operacion()
            self.incidencias.commit()
        except Exception:
            self.incidencias.rollback()
            raise

    def _panel(self, id_supervisor, listar, obtener, id_editar):
        id_ruta = self.rutas.ruta_activa(id_supervisor)
        datos = {"id_ruta": id_ruta, "incidencias": [], "buses": [], "editar_incidencia": None,
                 "estados": ESTADOS}
        if not id_ruta:
            return datos
        datos["incidencias"] = listar(id_ruta)
        datos["buses"] = self.buses.buses_para_seleccion(id_ruta)
        if id_editar:
            fila = obtener(id_editar, id_ruta)
            if fila:
                fila["fecha"] = v.a_fecha_iso(fila["fecha"])
                # Si el bus fue desasignado, lo mantenemos en el <select> para no perder el valor.
                if not any(b["id_bus"] == fila["id_bus"] for b in datos["buses"]):
                    datos["buses"].append({"id_bus": fila["id_bus"], "placa": fila["placa"]})
            datos["editar_incidencia"] = fila
        return datos

    # ---------- disciplinarias ----------
    def panel_disciplinarias(self, id_supervisor, id_editar=None):
        datos = self._panel(id_supervisor, self.incidencias.listar_disciplinarias,
                            self.incidencias.obtener_disciplinaria, id_editar)
        datos["tipos_disciplinaria"] = self.incidencias.tipos_disciplinaria()
        return datos

    def registrar_disciplinaria(self, id_supervisor, form):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        b = self._base(form)
        id_tipo = v.entero(form.get("id_tipo_disciplinaria"), "El tipo de falta")
        sancion = v.texto_requerido(form.get("sancion"), "La sanción", 255)
        self._transaccion(lambda: self.incidencias.crear_disciplinaria(
            id_ruta, b["fecha"], b["descripcion"], b["estado"], b["id_bus"], id_tipo, sancion))

    def actualizar_disciplinaria(self, id_supervisor, form):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        id_incidencia = v.entero(form.get("id_incidencia"), "La incidencia")
        if not self.incidencias.obtener_disciplinaria(id_incidencia, id_ruta):
            raise ReglaNegocioError("La incidencia no existe o no pertenece a tu ruta.")
        b = self._base(form)
        id_tipo = v.entero(form.get("id_tipo_disciplinaria"), "El tipo de falta")
        sancion = v.texto_requerido(form.get("sancion"), "La sanción", 255)
        self._transaccion(lambda: self.incidencias.actualizar_disciplinaria(
            id_incidencia, b["fecha"], b["descripcion"], b["estado"], b["id_bus"], id_tipo, sancion))

    def eliminar_disciplinaria(self, id_supervisor, id_incidencia):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        if not self.incidencias.obtener_disciplinaria(id_incidencia, id_ruta):
            raise ReglaNegocioError("La incidencia no existe o no pertenece a tu ruta.")
        self._transaccion(lambda: self.incidencias.eliminar_disciplinaria(id_incidencia))

    # ---------- operativas ----------
    def panel_operativas(self, id_supervisor, id_editar=None):
        return self._panel(id_supervisor, self.incidencias.listar_operativas,
                           self.incidencias.obtener_operativa, id_editar)

    def _datos_operativa(self, form):
        gravedad = form.get("gravedad")
        if gravedad not in GRAVEDADES:
            raise ReglaNegocioError("La gravedad seleccionada no es válida.")
        costo = v.decimal(form.get("costo") or 0, "El costo")
        requiere_seguro = 1 if form.get("requiere_seguro") == "on" else 0
        return gravedad, costo, requiere_seguro

    def registrar_operativa(self, id_supervisor, form):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        b = self._base(form)
        gravedad, costo, seguro = self._datos_operativa(form)
        self._transaccion(lambda: self.incidencias.crear_operativa(
            id_ruta, b["fecha"], b["descripcion"], b["estado"], b["id_bus"], gravedad, costo, seguro))

    def actualizar_operativa(self, id_supervisor, form):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        id_incidencia = v.entero(form.get("id_incidencia"), "La incidencia")
        if not self.incidencias.obtener_operativa(id_incidencia, id_ruta):
            raise ReglaNegocioError("La incidencia no existe o no pertenece a tu ruta.")
        b = self._base(form)
        gravedad, costo, seguro = self._datos_operativa(form)
        self._transaccion(lambda: self.incidencias.actualizar_operativa(
            id_incidencia, b["fecha"], b["descripcion"], b["estado"], b["id_bus"], gravedad, costo, seguro))

    def eliminar_operativa(self, id_supervisor, id_incidencia):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        if not self.incidencias.obtener_operativa(id_incidencia, id_ruta):
            raise ReglaNegocioError("La incidencia no existe o no pertenece a tu ruta.")
        self._transaccion(lambda: self.incidencias.eliminar_operativa(id_incidencia))
