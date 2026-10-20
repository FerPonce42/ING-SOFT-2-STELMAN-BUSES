from .base import BaseRepository


class EsquemaRepository(BaseRepository):
    """Metadatos de la BD para el reporte de documentación en Excel."""

    def nombre_bd(self):
        row = self._one("SELECT DATABASE() AS nombre")
        return row["nombre"]

    def tablas(self):
        # Solo tablas base; los nombres vienen del propio servidor.
        return [r["TABLE_NAME"] for r in self._all(
            """
            SELECT TABLE_NAME FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """
        )]

    def ddl(self, tabla):
        row = self._one(f"SHOW CREATE TABLE `{tabla}`")
        return row["Create Table"]

    def columnas(self, tabla):
        return self._all(
            """
            SELECT COLUMN_NAME, COLUMN_KEY FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
            """,
            (tabla,),
        )

    def claves_foraneas(self, tabla):
        return self._all(
            """
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
              AND REFERENCED_TABLE_NAME IS NOT NULL
            """,
            (tabla,),
        )

    def contar(self, tabla):
        return self._one(f"SELECT COUNT(*) AS c FROM `{tabla}`")["c"]

    def filas(self, tabla, limite=1000):
        return self._all(f"SELECT * FROM `{tabla}` LIMIT {int(limite)}")
