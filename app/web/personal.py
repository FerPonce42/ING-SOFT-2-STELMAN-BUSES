from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app import container
from app.errors import ReglaNegocioError
from app.web.seguridad import id_supervisor, login_required

bp = Blueprint("personal", __name__)


def _ejecutar(accion, mensaje_ok, mensaje_error):
    try:
        accion()
        flash(f"✔ {mensaje_ok}", "success")
    except ReglaNegocioError as exc:
        flash(f"❌ {exc}", "danger")
    except Exception:
        current_app.logger.exception(mensaje_error)
        flash(f"❌ {mensaje_error}", "danger")


@bp.route("/panel/personal")
@login_required
def inicio():
    return render_template("privado/personal.html")


@bp.route("/panel/personal/choferes")
@login_required
def choferes():
    servicio = container.chofer_service()
    if "eliminar" in request.args:
        _ejecutar(lambda: servicio.eliminar(id_supervisor(), request.args["eliminar"]),
                  "Registro eliminado.", "No se pudo eliminar el chofer.")
        return redirect(url_for("personal.choferes"))

    datos = servicio.panel(id_supervisor(), request.args.get("editar", type=int))
    return render_template("privado/personal_choferes.html",
                           choferes_existentes=datos["choferes"], id_ruta=datos["id_ruta"],
                           tipos_licencia=datos["tipos_licencia"], editar_personal=datos["editar_personal"])


@bp.route("/registrar_personal_chofer", methods=["POST"])
@login_required
def registrar_chofer():
    _ejecutar(lambda: container.chofer_service().registrar(id_supervisor(), request.form),
              "Chofer registrado correctamente.", "No se pudo registrar el chofer.")
    return redirect(url_for("personal.choferes"))


@bp.route("/actualizar_personal_chofer", methods=["POST"])
@login_required
def actualizar_chofer():
    _ejecutar(lambda: container.chofer_service().actualizar(
                  id_supervisor(), request.form.get("id_empleado"), request.form),
              "Datos del chofer actualizados.", "No se pudo actualizar el chofer.")
    return redirect(url_for("personal.choferes"))
