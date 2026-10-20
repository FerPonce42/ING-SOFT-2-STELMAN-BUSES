from .base import BaseRepository

# Un bus "pertenece" al supervisor si está en su ruta activa y no fue desasignado.
_BUS_DE_SUPERVISOR = """
    FROM bus b
    JOIN bus_ruta br ON br.id_bus = b.id_bus
    JOIN supervisor_ruta sr ON sr.id_ruta = br.id_ruta
    WHERE b.id_bus = %s
      AND sr.id_empleado = %s AND sr.fecha_fin IS NULL
      AND br.fecha_desasignacion IS NULL
"""


class BusRepository(BaseRepository):
    def modelos(self):
        return self._all(
            """
            SELECT mb.id_modelo_bus AS id, mb.nombre AS modelo_nombre, ma.nombre AS marca_nombre
            FROM modelo_bus mb
            JOIN marca_bus ma ON ma.id_marca_bus = mb.id_marca_bus
            ORDER BY ma.nombre, mb.nombre
            """
        )

    def buses_de_ruta(self, id_ruta):
        """Buses activos de la ruta. La última revisión sale de `mantenimiento`."""
        return self._all(
            """
            SELECT b.id_bus, b.placa, m.nombre AS modelo, ma.nombre AS marca,
                   b.año_fabricacion AS año,
                   (SELECT MAX(mt.fecha) FROM mantenimiento mt
                    WHERE mt.id_bus = b.id_bus) AS revision
            FROM bus b
            JOIN modelo_bus m ON m.id_modelo_bus = b.id_modelo_bus
            JOIN marca_bus ma ON ma.id_marca_bus = m.id_marca_bus
            JOIN bus_ruta br ON br.id_bus = b.id_bus
            WHERE br.id_ruta = %s AND br.fecha_desasignacion IS NULL
            ORDER BY b.placa
            """,
            (id_ruta,),
        )

    def buses_para_seleccion(self, id_ruta):
        """Buses para <select> de formularios (activos o desasignados desde hoy)."""
        return self._all(
            """
            SELECT b.id_bus, b.placa
            FROM bus b JOIN bus_ruta br ON br.id_bus = b.id_bus
            WHERE br.id_ruta = %s
              AND (br.fecha_desasignacion IS NULL OR br.fecha_desasignacion >= CURDATE())
            ORDER BY b.placa
            """,
            (id_ruta,),
        )

    def obtener_basico(self, id_bus):
        return self._one("SELECT id_bus, placa FROM bus WHERE id_bus = %s", (id_bus,))

    def obtener_de_supervisor(self, id_bus, id_supervisor):
        return self._one(
            "SELECT b.id_bus, b.placa, b.año_fabricacion, b.id_modelo_bus " + _BUS_DE_SUPERVISOR,
            (id_bus, id_supervisor),
        )

    def existe_placa(self, placa, excluir_id_bus=None):
        row = self._one(
            "SELECT id_bus FROM bus WHERE placa = %s AND id_bus <> %s",
            (placa, excluir_id_bus or 0),
        )
        return row is not None

    def crear(self, placa, anio, id_modelo_bus, id_almacen):
        return self._exec(
            "INSERT INTO bus (placa, año_fabricacion, id_modelo_bus, id_almacen) VALUES (%s, %s, %s, %s)",
            (placa, anio, id_modelo_bus, id_almacen),
        )

    def asignar_a_ruta(self, id_bus, id_ruta):
        return self._exec(
            "INSERT INTO bus_ruta (id_bus, id_ruta, fecha_asignacion) VALUES (%s, %s, NOW())",
            (id_bus, id_ruta),
        )

    def actualizar(self, id_bus, placa, anio, id_modelo_bus):
        self._exec(
            "UPDATE bus SET placa = %s, año_fabricacion = %s, id_modelo_bus = %s WHERE id_bus = %s",
            (placa, anio, id_modelo_bus, id_bus),
        )

    def desasignar(self, id_bus):
        self._exec(
            "UPDATE bus_ruta SET fecha_desasignacion = NOW() WHERE id_bus = %s AND fecha_desasignacion IS NULL",
            (id_bus,),
        )
