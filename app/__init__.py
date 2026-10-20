from datetime import datetime

from flask import Flask, request

from app import db
from app.config import Config


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)

    from app.web import auth, buses, caja, incidencias, panel, personal, publico, reportes

    for modulo in (publico, auth, panel, buses, personal, incidencias, caja, reportes):
        app.register_blueprint(modulo.bp)

    @app.context_processor
    def variables_globales():
        datos = {"current_year": datetime.now().year, "rutas_publicas": []}
        if request.blueprint == "publico":  # el menú público lista las rutas de la BD
            from app import container
            try:
                datos["rutas_publicas"] = container.ruta_service().listar_publicas()
            except Exception:
                app.logger.exception("No se pudieron cargar las rutas del menú")
        return datos

    return app
