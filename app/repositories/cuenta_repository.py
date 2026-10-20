from .base import BaseRepository


class CuentaRepository(BaseRepository):
    def por_usuario(self, nombre_usuario):
        """Cuenta de un supervisor (solo ellos entran al panel), con su cargo."""
        return self._one(
            """
            SELECT c.id_cuenta, c.nombre_usuario, c.password_hash,
                   c.estado_cuenta, c.id_empleado, ts.nombre_cargo
            FROM cuenta_usuario c
            JOIN supervisor s ON s.id_empleado = c.id_empleado
            JOIN tipo_supervisor ts ON ts.id_tipo_supervisor = s.id_tipo_supervisor
            WHERE c.nombre_usuario = %s
            """,
            (nombre_usuario,),
        )
