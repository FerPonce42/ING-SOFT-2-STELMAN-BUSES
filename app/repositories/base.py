import pymysql

from app.errors import IntegridadError


class BaseRepository:
    """Acceso a datos: aquí vive el SQL y nada más (sin reglas de negocio)."""

    def __init__(self, conn):
        self.conn = conn

    def _all(self, sql, params=()):
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())

    def _one(self, sql, params=()):
        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def _exec(self, sql, params=()):
        """Ejecuta INSERT/UPDATE/DELETE y devuelve el lastrowid."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.lastrowid
        except pymysql.err.IntegrityError as exc:
            raise IntegridadError(exc.args[0], str(exc)) from exc

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
