from datetime import date

from app.errors import ReglaNegocioError
from app.services import validaciones as v

ANIO_MINIMO = 1950


class BusService:
    def __init__(self, buses, rutas, id_almacen_por_defecto=1):
        self.buses = buses
        self.rutas = rutas  # RutaService
        self.id_almacen = id_almacen_por_defecto

    @staticmethod
    def anio_maximo():
        return date.today().year + 1

    def _validar_datos(self, placa, anio, id_modelo):
        placa = v.texto_requerido(placa, "La placa", maximo=20).upper()
        anio = v.entero(anio, "El año")
        if not ANIO_MINIMO <= anio <= self.anio_maximo():
            raise ReglaNegocioError(f"El año debe estar entre {ANIO_MINIMO} y {self.anio_maximo()}.")
        return placa, anio, v.entero(id_modelo, "El modelo")

    def panel(self, id_supervisor, id_editar=None):
        id_ruta = self.rutas.ruta_activa(id_supervisor)
        datos = {"id_ruta": id_ruta, "buses": [], "modelos": [], "bus_a_editar": None,
                 "error_edicion": None, "anio_maximo": self.anio_maximo()}
        if not id_ruta:
            return datos
        datos["modelos"] = self.buses.modelos()
        datos["buses"] = self.buses.buses_de_ruta(id_ruta)
        if id_editar:
            datos["bus_a_editar"] = self.buses.obtener_de_supervisor(id_editar, id_supervisor)
            if not datos["bus_a_editar"]:
                datos["error_edicion"] = "El bus solicitado no existe o no está en tu ruta activa."
        return datos

    def registrar(self, id_supervisor, placa, anio, id_modelo):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        placa, anio, id_modelo = self._validar_datos(placa, anio, id_modelo)
        if self.buses.existe_placa(placa):
            raise ReglaNegocioError("Esa placa ya está registrada.")
        try:
            id_bus = self.buses.crear(placa, anio, id_modelo, self.id_almacen)
            self.buses.asignar_a_ruta(id_bus, id_ruta)
            self.buses.commit()
        except Exception:
            self.buses.rollback()
            raise
        return id_bus

    def editar(self, id_supervisor, id_bus, placa, anio, id_modelo):
        if not self.buses.obtener_de_supervisor(id_bus, id_supervisor):
            raise ReglaNegocioError("Intento de editar un bus que no está asignado a tu ruta.")
        placa, anio, id_modelo = self._validar_datos(placa, anio, id_modelo)
        if self.buses.existe_placa(placa, excluir_id_bus=id_bus):
            raise ReglaNegocioError("Esa placa ya pertenece a otro bus.")
        try:
            self.buses.actualizar(id_bus, placa, anio, id_modelo)
            self.buses.commit()
        except Exception:
            self.buses.rollback()
            raise

    def desasignar(self, id_supervisor, id_bus):
        if not self.buses.obtener_de_supervisor(id_bus, id_supervisor):
            raise ReglaNegocioError("Acceso denegado: el bus no está asignado a tu ruta activa.")
        try:
            self.buses.desasignar(id_bus)
            self.buses.commit()
        except Exception:
            self.buses.rollback()
            raise
