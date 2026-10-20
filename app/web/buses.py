from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app import container
from app.errors import ReglaNegocioError
from app.web.seguridad import id_supervisor, login_required

bp = Blueprint("buses", __name__)


@bp.route("/panel/buses", methods=["GET", "POST"])
@login_required
def panel():
    servicio = container.bus_service()
    if request.method == "POST":
        try:
            if request.form.get("id_bus_editado"):
                servicio.editar(id_supervisor(), int(request.form["id_bus_editado"]),
                                request.form.get("placa"), request.form.get("anio"),
                                request.form.get("id_modelo_bus"))
                flash("✔️ Bus editado correctamente.", "success")
            else:
                servicio.registrar(id_supervisor(), request.form.get("placa"),
                                   request.form.get("anio"), request.form.get("id_modelo_bus"))
                flash("✔️ Bus registrado y asignado a tu ruta correctamente.", "success")
        except ReglaNegocioError as exc:
            flash(f"❌ {exc}", "danger")
        except Exception:
            current_app.logger.exception("Error guardando bus")
            flash("❌ No se pudo guardar el bus. Revisa los datos e inténtalo de nuevo.", "danger")
        return redirect(url_for("buses.panel"))

    datos = servicio.panel(id_supervisor(), request.args.get("id_editar", type=int))
    if not datos["id_ruta"]:
        flash("🚫 No tienes rutas activas asignadas. No se muestran buses ni se permite el registro/edición.", "warning")
    if datos["error_edicion"]:
        flash(f"❌ {datos['error_edicion']}", "danger")
    return render_template("privado/buses.html", **datos)


@bp.route("/panel/buses/eliminar/<int:id_bus>")
@login_required
def desasignar(id_bus):
    try:
        container.bus_service().desasignar(id_supervisor(), id_bus)
        flash("✔️ Bus desasignado de tu ruta correctamente.", "success")
    except ReglaNegocioError as exc:
        flash(f"❌ {exc}", "danger")
    except Exception:
        current_app.logger.exception("Error desasignando bus")
        flash("❌ Error al intentar desasignar el bus.", "danger")
    return redirect(url_for("buses.panel"))
