from flask import Blueprint, render_template, send_file

from app import container
from app.web.seguridad import login_required

bp = Blueprint("reportes", __name__)


@bp.route("/panel/reportes")
@login_required
def inicio():
    return render_template("privado/reportes.html")


@bp.route("/exportar_excel")
@login_required  # antes era público: exponía toda la BD a cualquiera
def exportar():
    servicio = container.reporte_service()
    return send_file(
        servicio.documentacion_excel(),
        download_name=servicio.nombre_archivo(),
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
