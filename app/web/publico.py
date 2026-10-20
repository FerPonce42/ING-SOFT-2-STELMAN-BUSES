from flask import Blueprint, abort, render_template, request

from app import container

bp = Blueprint("publico", __name__)


@bp.route("/")
def index():
    return render_template("publico/index.html")


@bp.route("/rutas")
def rutas():
    return render_template("publico/rutas.html", rutas=container.ruta_service().listar_publicas())


@bp.route("/ruta/<string:codigo>")
def detalle_ruta(codigo):
    detalle = container.ruta_service().detalle_publico(codigo)
    if not detalle:
        abort(404)
    return render_template("publico/ruta_detalle.html", ruta=detalle["ruta"],
                           codigo=detalle["ruta"]["codigo_ruta"], paraderos_coords=detalle["paraderos"])


@bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        return render_template("publico/contacto.html", enviado=True, nombre=request.form.get("nombre"))
    return render_template("publico/contacto.html")
