from flask import Blueprint, render_template, session

from app import container
from app.web.seguridad import id_supervisor, login_required

bp = Blueprint("panel", __name__)


@bp.route("/panel")
@login_required
def dashboard():
    kpis = container.ruta_service().dashboard(id_supervisor())
    return render_template("privado/dashboard.html", nombre_supervisor=session["usuario"],
                           tipo_supervisor=session["rol"], **kpis)
