from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app import container
from app.errors import CredencialesInvalidasError

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            cuenta = container.auth_service().autenticar(
                request.form.get("usuario"), request.form.get("password"))
        except CredencialesInvalidasError as exc:
            flash(f"❌ {exc}", "danger")
        else:
            session.clear()  # evita reutilizar una sesión previa
            session.update(id=cuenta["id"], rol=cuenta["rol"], usuario=cuenta["usuario"])
            flash("✅ Bienvenido al sistema", "success")
            return redirect(url_for("panel.dashboard"))
    return render_template("autenticacion/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))
