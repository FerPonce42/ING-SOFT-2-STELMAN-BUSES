from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from datetime import date

from app import container
from app.errors import ReglaNegocioError
from app.web.seguridad import id_supervisor, login_required

bp = Blueprint("incidencias", __name__)


def _ejecutar(accion, mensaje_ok, mensaje_error):
    try:
        accion()
        flash(f"✔ {mensaje_ok}", "success")
    except ReglaNegocioError as exc:
        flash(f"❌ {exc}", "danger")
    except Exception:
        current_app.logger.exception(mensaje_error)
        flash(f"❌ {mensaje_error}", "danger")


@bp.route("/panel/incidencias")
@login_required
def inicio():
    return render_template("privado/incidencias.html")


# ---------- disciplinarias ----------
@bp.route("/panel/incidencias/disciplinarias")
@login_required
def disciplinarias():
    datos = container.incidencia_service().panel_disciplinarias(
        id_supervisor(), request.args.get("editar", type=int))
    return render_template("privado/incidencias_disciplinarias.html",
                           hoy=date.today().isoformat(), **datos)


@bp.route("/registrar_incidencia_disciplinaria", methods=["POST"])
@login_required
def registrar_disciplinaria():
    _ejecutar(lambda: container.incidencia_service().registrar_disciplinaria(id_supervisor(), request.form),
              "Incidencia disciplinaria registrada.", "No se pudo registrar la incidencia.")
    return redirect(url_for("incidencias.disciplinarias"))


@bp.route("/actualizar_incidencia_disciplinaria", methods=["POST"])
@login_required
def actualizar_disciplinaria():
    _ejecutar(lambda: container.incidencia_service().actualizar_disciplinaria(id_supervisor(), request.form),
              "Incidencia disciplinaria actualizada.", "No se pudo actualizar la incidencia.")
    return redirect(url_for("incidencias.disciplinarias"))


@bp.route("/eliminar_incidencia_disciplinaria/<int:id_incidencia>")
@login_required
def eliminar_disciplinaria(id_incidencia):
    _ejecutar(lambda: container.incidencia_service().eliminar_disciplinaria(id_supervisor(), id_incidencia),
              "Incidencia disciplinaria eliminada.", "No se pudo eliminar la incidencia.")
    return redirect(url_for("incidencias.disciplinarias"))


# ---------- operativas ----------
@bp.route("/panel/incidencias/operativas")
@login_required
def operativas():
    datos = container.incidencia_service().panel_operativas(
        id_supervisor(), request.args.get("editar", type=int))
    return render_template("privado/incidencias_operativas.html",
                           hoy=date.today().isoformat(), **datos)


@bp.route("/registrar_incidencia_operativa", methods=["POST"])
@login_required
def registrar_operativa():
    _ejecutar(lambda: container.incidencia_service().registrar_operativa(id_supervisor(), request.form),
              "Incidencia operativa registrada.", "No se pudo registrar la incidencia.")
    return redirect(url_for("incidencias.operativas"))


@bp.route("/actualizar_incidencia_operativa", methods=["POST"])
@login_required
def actualizar_operativa():
    _ejecutar(lambda: container.incidencia_service().actualizar_operativa(id_supervisor(), request.form),
              "Incidencia operativa actualizada.", "No se pudo actualizar la incidencia.")
    return redirect(url_for("incidencias.operativas"))


@bp.route("/eliminar_incidencia_operativa/<int:id_incidencia>")
@login_required
def eliminar_operativa(id_incidencia):
    _ejecutar(lambda: container.incidencia_service().eliminar_operativa(id_supervisor(), id_incidencia),
              "Incidencia operativa eliminada.", "No se pudo eliminar la incidencia.")
    return redirect(url_for("incidencias.operativas"))
