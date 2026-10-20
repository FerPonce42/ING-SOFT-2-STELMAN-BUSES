from .base import BaseRepository

_CAMPOS_LISTA = """
    e.id_empleado, e.nombre, e.apellido, e.nro_identificacion AS dni,
    ch.nro_licencia, tl.categoria, ch.fecha_primera_licencia,
    TIMESTAMPDIFF(YEAR, ch.fecha_primera_licencia, CURDATE()) AS anos_experiencia
"""
_JOINS = """
    FROM empleado e
    JOIN chofer ch ON ch.id_empleado = e.id_empleado
    JOIN tipo_licencia tl ON tl.id_tipo_licencia = ch.id_tipo_licencia
"""


class ChoferRepository(BaseRepository):
    def listar_de_ruta(self, id_ruta):
        """Choferes que trabajan en buses de la ruta + los que aún no tienen bus."""
        return self._all(
            f"""
            (SELECT {_CAMPOS_LISTA} {_JOINS}
             WHERE e.id_empleado IN (
                 SELECT ab.id_empleado
                 FROM asignacion_bus ab
                 JOIN bus_ruta br ON br.id_bus = ab.id_bus
                 WHERE br.id_ruta = %s))
            UNION
            (SELECT {_CAMPOS_LISTA} {_JOINS}
             WHERE e.id_empleado NOT IN (SELECT id_empleado FROM asignacion_bus))
            ORDER BY apellido, nombre
            """,
            (id_ruta,),
        )

    def obtener(self, id_empleado):
        return self._one(
            f"""
            SELECT e.id_empleado, e.nombre, e.apellido, e.nro_identificacion AS dni,
                   e.telefono, e.correo_electronico, e.fecha_nacimiento, e.sueldo,
                   ch.nro_licencia, ch.fecha_primera_licencia, ch.id_tipo_licencia
            {_JOINS}
            WHERE e.id_empleado = %s
            """,
            (id_empleado,),
        )

    def tipos_licencia(self):
        return self._all("SELECT * FROM tipo_licencia ORDER BY categoria")

    def crear(self, d):
        id_empleado = self._exec(
            """
            INSERT INTO empleado (nro_identificacion, nombre, apellido, fecha_nacimiento,
                                  correo_electronico, sueldo, telefono, fecha_ingreso, tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Chofer')
            """,
            (d["dni"], d["nombre"], d["apellido"], d["fecha_nacimiento"],
             d["correo"], d["sueldo"], d["telefono"], d["fecha_ingreso"]),
        )
        self._exec(
            """
            INSERT INTO chofer (id_empleado, nro_licencia, fecha_primera_licencia, id_tipo_licencia)
            VALUES (%s, %s, %s, %s)
            """,
            (id_empleado, d["nro_licencia"], d["fecha_primera_licencia"], d["id_tipo_licencia"]),
        )
        return id_empleado

    def actualizar(self, id_empleado, d):
        self._exec(
            """
            UPDATE empleado
            SET nro_identificacion = %s, nombre = %s, apellido = %s, fecha_nacimiento = %s,
                correo_electronico = %s, sueldo = %s, telefono = %s
            WHERE id_empleado = %s
            """,
            (d["dni"], d["nombre"], d["apellido"], d["fecha_nacimiento"],
             d["correo"], d["sueldo"], d["telefono"], id_empleado),
        )
        self._exec(
            """
            UPDATE chofer
            SET nro_licencia = %s, fecha_primera_licencia = %s, id_tipo_licencia = %s
            WHERE id_empleado = %s
            """,
            (d["nro_licencia"], d["fecha_primera_licencia"], d["id_tipo_licencia"], id_empleado),
        )

    def eliminar(self, id_empleado):
        self._exec("DELETE FROM chofer WHERE id_empleado = %s", (id_empleado,))
        self._exec("DELETE FROM empleado WHERE id_empleado = %s", (id_empleado,))
