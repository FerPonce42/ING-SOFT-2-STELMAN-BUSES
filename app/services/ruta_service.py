from app.errors import ReglaNegocioError

ESTADOS_ABIERTOS = ("Pendiente", "En revision")


class RutaService:
    def __init__(self, rutas):
        self.rutas = rutas

    # ---- contexto del supervisor ----
    def ruta_activa(self, id_supervisor):
        return self.rutas.ruta_activa_de_supervisor(id_supervisor)

    def exigir_ruta_activa(self, id_supervisor):
        id_ruta = self.ruta_activa(id_supervisor)
        if not id_ruta:
            raise ReglaNegocioError("No tienes una ruta activa asignada.")
        return id_ruta

    # ---- dashboard ----
    def dashboard(self, id_supervisor):
        id_ruta = self.ruta_activa(id_supervisor)
        kpis = {
            "kpi_buses": 0,
            "kpi_recaudacion": "S/. 0.00",
            "kpi_incidencias": self.rutas.contar_incidencias_abiertas(ESTADOS_ABIERTOS),
            "mensaje_ruta": "🚫 No tienes una ruta activa asignada. Los KPIs de Ruta se muestran en 0.",
        }
        if id_ruta:
            ruta = self.rutas.obtener(id_ruta)
            kpis["kpi_buses"] = self.rutas.contar_buses_activos(id_ruta)
            kpis["kpi_recaudacion"] = f"S/. {self.rutas.recaudacion_de_hoy(id_ruta):,.2f}"
            kpis["mensaje_ruta"] = f"✅ Administrando la Ruta: {ruta['codigo_ruta']} (ID: {id_ruta})"
        return kpis

    # ---- sitio público ----
    def listar_publicas(self):
        return self.rutas.listar_publicas()

    def detalle_publico(self, codigo_ruta):
        ruta = self.rutas.obtener_por_codigo(codigo_ruta)
        if not ruta:
            return None
        paraderos = [
            {**p, "lat": float(p["lat"]), "lng": float(p["lng"])}
            for p in self.rutas.paraderos_de_ruta(ruta["id_ruta"])
        ]
        return {"ruta": ruta, "paraderos": paraderos}
