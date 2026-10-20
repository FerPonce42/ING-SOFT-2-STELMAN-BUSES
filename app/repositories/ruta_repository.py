from .base import BaseRepository

_PARADERO_POR_ORDEN = """
    (SELECT p.nombre_paradero
     FROM recorrido rc JOIN paradero p ON p.id_paradero = rc.id_paradero
     WHERE rc.id_ruta = r.id_ruta
     ORDER BY rc.orden_paradero {orden} LIMIT 1)
"""


class RutaRepository(BaseRepository):
    def ruta_activa_de_supervisor(self, id_empleado):
        row = self._one(
            "SELECT id_ruta FROM supervisor_ruta WHERE id_empleado = %s AND fecha_fin IS NULL",
            (id_empleado,),
        )
        return row["id_ruta"] if row else None

    def obtener(self, id_ruta):
        return self._one("SELECT * FROM ruta WHERE id_ruta = %s", (id_ruta,))

    def obtener_por_codigo(self, codigo_ruta):
        return self._one("SELECT * FROM ruta WHERE codigo_ruta = %s", (codigo_ruta,))

    def listar_publicas(self):
        return self._all(
            f"""
            SELECT r.id_ruta, r.codigo_ruta, r.color, r.distancia, r.duracion_estimada,
                   {_PARADERO_POR_ORDEN.format(orden="ASC")} AS origen,
                   {_PARADERO_POR_ORDEN.format(orden="DESC")} AS destino
            FROM ruta r
            ORDER BY r.codigo_ruta
            """
        )

    def paraderos_de_ruta(self, id_ruta):
        return self._all(
            """
            SELECT p.nombre_paradero AS nombre, p.latitud AS lat, p.longitud AS lng,
                   p.direccion_referencia AS referencia, rc.orden_paradero AS orden
            FROM recorrido rc
            JOIN paradero p ON p.id_paradero = rc.id_paradero
            WHERE rc.id_ruta = %s
            ORDER BY rc.orden_paradero
            """,
            (id_ruta,),
        )

    # ---- KPIs del dashboard ----
    def contar_buses_activos(self, id_ruta):
        row = self._one(
            """
            SELECT COUNT(*) AS total FROM bus_ruta
            WHERE id_ruta = %s AND fecha_desasignacion IS NULL
            """,
            (id_ruta,),
        )
        return row["total"]

    def recaudacion_de_hoy(self, id_ruta):
        row = self._one(
            """
            SELECT COALESCE(SUM(monto_recaudado), 0) AS total FROM caja
            WHERE id_ruta = %s AND DATE(fecha) = CURDATE()
            """,
            (id_ruta,),
        )
        return row["total"]

    def contar_incidencias_abiertas(self, estados_abiertos):
        marcas = ", ".join(["%s"] * len(estados_abiertos))
        row = self._one(
            f"SELECT COUNT(*) AS total FROM incidencia WHERE estado IN ({marcas})",
            tuple(estados_abiertos),
        )
        return row["total"]
