import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-cambiar-en-produccion")

    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "stelman")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "stelman")
    DB_NAME = os.environ.get("DB_NAME", "bd_stelman_buses")

    # Almacén donde se registran los buses nuevos (la BD exige uno).
    ALMACEN_POR_DEFECTO = int(os.environ.get("ALMACEN_POR_DEFECTO", "1"))
