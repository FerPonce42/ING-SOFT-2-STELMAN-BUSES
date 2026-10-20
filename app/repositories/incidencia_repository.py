from .base import BaseRepository

_SELECT_DISCIPLINARIA = """
    SELECT i.id_incidencia, i.fecha, i.descripcion, i.estado, i.id_bus, b.placa,
           d.id_tipo_disciplinaria, td.nombre_falta AS tipo_disciplinaria, d.sancion
    FROM incidencia i
    JOIN incidencia_disciplinaria d ON d.id_incidencia = i.id_incidencia
    JOIN tipo_disciplinaria td ON td.id_tipo_disciplinaria = d.id_tipo_disciplinaria
    JOIN bus b ON b.id_bus = i.id_bus
"""
_SELECT_OPERATIVA = """
    SELECT i.id_incidencia, i.fecha, i.descripcion, i.estado, i.id_bus, b.placa,
           o.gravedad, o.costo, o.requiere_seguro
    FROM incidencia i
    JOIN incidencia_operativa o ON o.id_incidencia = i.id_incidencia
    JOIN bus b ON b.id_bus = i.id_bus
"""


class IncidenciaRepository(BaseRepository):
    # ---------- base (tabla incidencia) ----------
    def _crear_base(self, fecha, descripcion, estado, id_bus, id_ruta):
        return self._exec(
            "INSERT INTO incidencia (fecha, descripcion, estado, id_bus, id_ruta) VALUES (%s, %s, %s, %s, %s)",
            (fecha, descripcion, estado, id_bus, id_ruta),
        )

    def _actualizar_base(self, id_incidencia, fecha, descripcion, estado, id_bus):
        self._exec(
            "UPDATE incidencia SET fecha = %s, descripcion = %s, estado = %s, id_bus = %s WHERE id_incidencia = %s",
            (fecha, descripcion, estado, id_bus, id_incidencia),
        )

    # ---------- disciplinarias ----------
    def tipos_disciplinaria(self):
        return self._all("SELECT * FROM tipo_disciplinaria ORDER BY nombre_falta")

    def listar_disciplinarias(self, id_ruta):
        return self._all(_SELECT_DISCIPLINARIA + " WHERE i.id_ruta = %s ORDER BY i.fecha DESC", (id_ruta,))

    def obtener_disciplinaria(self, id_incidencia, id_ruta):
        return self._one(
            _SELECT_DISCIPLINARIA + " WHERE i.id_incidencia = %s AND i.id_ruta = %s",
            (id_incidencia, id_ruta),
        )

    def crear_disciplinaria(self, id_ruta, fecha, descripcion, estado, id_bus, id_tipo, sancion):
        id_incidencia = self._crear_base(fecha, descripcion, estado, id_bus, id_ruta)
        self._exec(
            "INSERT INTO incidencia_disciplinaria (id_incidencia, id_tipo_disciplinaria, sancion) VALUES (%s, %s, %s)",
            (id_incidencia, id_tipo, sancion),
        )
        return id_incidencia

    def actualizar_disciplinaria(self, id_incidencia, fecha, descripcion, estado, id_bus, id_tipo, sancion):
        self._actualizar_base(id_incidencia, fecha, descripcion, estado, id_bus)
        self._exec(
            "UPDATE incidencia_disciplinaria SET id_tipo_disciplinaria = %s, sancion = %s WHERE id_incidencia = %s",
            (id_tipo, sancion, id_incidencia),
        )

    def eliminar_disciplinaria(self, id_incidencia):
        self._exec("DELETE FROM incidencia_disciplinaria WHERE id_incidencia = %s", (id_incidencia,))
        self._exec("DELETE FROM incidencia WHERE id_incidencia = %s", (id_incidencia,))

    # ---------- operativas ----------
    def listar_operativas(self, id_ruta):
        return self._all(_SELECT_OPERATIVA + " WHERE i.id_ruta = %s ORDER BY i.fecha DESC", (id_ruta,))

    def obtener_operativa(self, id_incidencia, id_ruta):
        return self._one(
            _SELECT_OPERATIVA + " WHERE i.id_incidencia = %s AND i.id_ruta = %s",
            (id_incidencia, id_ruta),
        )

    def crear_operativa(self, id_ruta, fecha, descripcion, estado, id_bus, gravedad, costo, requiere_seguro):
        id_incidencia = self._crear_base(fecha, descripcion, estado, id_bus, id_ruta)
        self._exec(
            "INSERT INTO incidencia_operativa (id_incidencia, gravedad, costo, requiere_seguro) VALUES (%s, %s, %s, %s)",
            (id_incidencia, gravedad, costo, requiere_seguro),
        )
        return id_incidencia

    def actualizar_operativa(self, id_incidencia, fecha, descripcion, estado, id_bus, gravedad, costo, requiere_seguro):
        self._actualizar_base(id_incidencia, fecha, descripcion, estado, id_bus)
        self._exec(
            "UPDATE incidencia_operativa SET gravedad = %s, costo = %s, requiere_seguro = %s WHERE id_incidencia = %s",
            (gravedad, costo, requiere_seguro, id_incidencia),
        )

    def eliminar_operativa(self, id_incidencia):
        self._exec("DELETE FROM incidencia_operativa WHERE id_incidencia = %s", (id_incidencia,))
        self._exec("DELETE FROM incidencia WHERE id_incidencia = %s", (id_incidencia,))
