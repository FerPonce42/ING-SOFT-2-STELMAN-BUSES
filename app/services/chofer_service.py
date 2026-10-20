from datetime import date

from app.errors import IntegridadError, ReglaNegocioError
from app.services import validaciones as v


class ChoferService:
    def __init__(self, choferes, rutas):
        self.choferes = choferes
        self.rutas = rutas  # RutaService

    # ---- lectura ----
    def panel(self, id_supervisor, id_editar=None):
        id_ruta = self.rutas.ruta_activa(id_supervisor)
        datos = {"id_ruta": id_ruta, "choferes": [], "tipos_licencia": [], "editar_personal": None}
        if not id_ruta:
            return datos
        datos["choferes"] = self.choferes.listar_de_ruta(id_ruta)
        datos["tipos_licencia"] = self.choferes.tipos_licencia()
        if id_editar:
            editar = self.choferes.obtener(id_editar)
            if editar:
                editar["fecha_nacimiento"] = v.a_fecha_iso(editar["fecha_nacimiento"])
                editar["fecha_primera_licencia"] = v.a_fecha_iso(editar["fecha_primera_licencia"])
            datos["editar_personal"] = editar
        return datos

    # ---- reglas ----
    def _validar(self, form):
        return {
            "nombre": v.texto_requerido(form.get("nombre"), "El nombre", 100),
            "apellido": v.texto_requerido(form.get("apellido"), "El apellido", 100),
            "dni": v.texto_requerido(form.get("dni"), "El DNI", 50),
            "fecha_nacimiento": v.fecha(form.get("fecha_nacimiento"), "La fecha de nacimiento", minimo=date(1940, 1, 1)),
            "correo": v.texto_opcional(form.get("correo")),
            "telefono": v.texto_opcional(form.get("telefono")),
            "sueldo": v.decimal(form.get("sueldo"), "El sueldo"),
            "nro_licencia": v.texto_requerido(form.get("nro_licencia"), "El número de licencia", 50),
            "fecha_primera_licencia": v.fecha(form.get("fecha_primera_licencia"), "La fecha de primera licencia", minimo=date(1950, 1, 1)),
            "id_tipo_licencia": v.entero(form.get("id_tipo_licencia"), "El tipo de licencia"),
        }

    def _exigir_gestionable(self, id_supervisor, id_empleado):
        id_ruta = self.rutas.exigir_ruta_activa(id_supervisor)
        if not any(c["id_empleado"] == id_empleado for c in self.choferes.listar_de_ruta(id_ruta)):
            raise ReglaNegocioError("Ese chofer no está disponible para tu ruta.")

    def _guardar(self, operacion, error_duplicado):
        try:
            operacion()
            self.choferes.commit()
        except IntegridadError as exc:
            self.choferes.rollback()
            if exc.duplicado:
                raise ReglaNegocioError(error_duplicado)
            raise
        except Exception:
            self.choferes.rollback()
            raise

    # ---- casos de uso ----
    def registrar(self, id_supervisor, form):
        self.rutas.exigir_ruta_activa(id_supervisor)
        d = dict(self._validar(form), fecha_ingreso=v.fecha(form.get("fecha_ingreso"), "La fecha de ingreso"))
        self._guardar(lambda: self.choferes.crear(d),
                      "Ya existe un empleado con ese DNI o una licencia con ese número.")

    def actualizar(self, id_supervisor, id_empleado, form):
        id_empleado = v.entero(id_empleado, "El chofer")
        self._exigir_gestionable(id_supervisor, id_empleado)
        d = self._validar(form)
        self._guardar(lambda: self.choferes.actualizar(id_empleado, d),
                      "Ya existe un empleado con ese DNI o una licencia con ese número.")

    def eliminar(self, id_supervisor, id_empleado):
        id_empleado = v.entero(id_empleado, "El chofer")
        self._exigir_gestionable(id_supervisor, id_empleado)
        try:
            self.choferes.eliminar(id_empleado)
            self.choferes.commit()
        except IntegridadError as exc:
            self.choferes.rollback()
            if exc.registro_en_uso:
                raise ReglaNegocioError(
                    "No se puede eliminar: el chofer tiene buses asignados, recaudaciones o incidencias registradas."
                )
            raise
        except Exception:
            self.choferes.rollback()
            raise
