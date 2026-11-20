import os


def _requerida(nombre):
    valor = os.environ.get(nombre)
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. "
            "Copia .env.example a .env y complétala."
        )
    return valor


class Config:
    SECRET_KEY = _requerida("SECRET_KEY")

    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.environ.get("DB_PORT", "3306"))
    DB_USER = os.environ.get("DB_USER", "stelman")
    DB_PASSWORD = _requerida("DB_PASSWORD")
    DB_NAME = os.environ.get("DB_NAME", "bd_stelman_buses")

    # Almacén donde se registran los buses nuevos (la BD exige uno).
    ALMACEN_POR_DEFECTO = int(os.environ.get("ALMACEN_POR_DEFECTO", "1"))