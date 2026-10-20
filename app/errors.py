class ReglaNegocioError(Exception):
    """Error esperado: el mensaje se puede mostrar tal cual al usuario."""


class CredencialesInvalidasError(ReglaNegocioError):
    pass


class IntegridadError(Exception):
    """La BD rechazó la operación por una restricción (FK o UNIQUE)."""

    def __init__(self, codigo, mensaje=""):
        super().__init__(mensaje)
        self.codigo = codigo

    @property
    def registro_en_uso(self):
        return self.codigo == 1451  # fila referenciada por otra tabla

    @property
    def duplicado(self):
        return self.codigo == 1062
