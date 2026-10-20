from functools import wraps

from flask import redirect, session, url_for


def login_required(vista):
    @wraps(vista)
    def envuelta(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("auth.login"))
        return vista(*args, **kwargs)

    return envuelta


def id_supervisor():
    return session["id"]
