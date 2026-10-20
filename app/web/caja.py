from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app import container
from app.errors import ReglaNegocioError
from app.web.seguridad import id_supervisor, login_required

bp = Blueprint("caja", __name__)


def _ejecutar(accion, mensaje_ok, mensaje_error):
    try:
        accion()
        flash(f"✔ {mensaje_ok}", "success")
    except ReglaNegocioError as exc:
        flash(f"❌ {exc}", "danger")
    except Exception:
        current_app.logger.exception(mensaje_error)
        flash(f"❌ {mensaje_error}", "danger")


@bp.route("/panel/caja")
@login_required
def panel():
    return render_template("privado/caja.html", **container.caja_service().panel(id_supervisor()))


@bp.route("/editar_caja/<int:id_caja>")
@login_required
def editar(id_caja):
    return render_template("privado/caja.html", **container.caja_service().panel(id_supervisor(), id_caja))


@bp.route("/registrar_caja", methods=["POST"])
@login_required
def registrar():
    _ejecutar(lambda: container.caja_service().registrar(id_supervisor(), request.form),
              "Recaudación registrada correctamente.", "No se pudo registrar la recaudación.")
    return redirect(url_for("caja.panel"))


@bp.route("/actualizar_caja", methods=["POST"])
@login_required
def actualizar():
    _ejecutar(lambda: container.caja_service().actualizar(id_supervisor(), request.form),
              "Recaudación actualizada correctamente.", "No se pudo actualizar la recaudación.")
    return redirect(url_for("caja.panel"))


@bp.route("/eliminar_caja/<int:id_caja>")
@login_required
def eliminar(id_caja):
    _ejecutar(lambda: container.caja_service().eliminar(id_supervisor(), id_caja),
              "Recaudación eliminada.", "No se pudo eliminar la recaudación.")
    return redirect(url_for("caja.panel"))
