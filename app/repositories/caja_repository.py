from .base import BaseRepository


class CajaRepository(BaseRepository):
    def listar_de_ruta(self, id_ruta):
        return self._all(
            """
            SELECT c.id_caja, c.fecha, c.monto_recaudado, c.observacion,
                   e.id_empleado, e.nombre, e.apellido, b.id_bus, b.placa
            FROM caja c
            JOIN empleado e ON e.id_empleado = c.id_empleado
            JOIN bus b ON b.id_bus = c.id_bus
            WHERE c.id_ruta = %s
            ORDER BY c.fecha DESC
            """,
            (id_ruta,),
        )

    def obtener(self, id_caja, id_ruta):
        return self._one(
            "SELECT * FROM caja WHERE id_caja = %s AND id_ruta = %s", (id_caja, id_ruta)
        )

    def crear(self, id_empleado, id_ruta, id_bus, fecha, monto, observacion):
        return self._exec(
            """
            INSERT INTO caja (id_empleado, id_ruta, id_bus, fecha, monto_recaudado, observacion)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id_empleado, id_ruta, id_bus, fecha, monto, observacion),
        )

    def actualizar(self, id_caja, fecha, monto, observacion, id_empleado, id_bus):
        self._exec(
            """
            UPDATE caja SET fecha = %s, monto_recaudado = %s, observacion = %s,
                            id_empleado = %s, id_bus = %s
            WHERE id_caja = %s
            """,
            (fecha, monto, observacion, id_empleado, id_bus, id_caja),
        )

    def eliminar(self, id_caja):
        self._exec("DELETE FROM caja WHERE id_caja = %s", (id_caja,))
