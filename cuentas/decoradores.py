"""Control de acceso en el servidor (R-05, contracts/rutas.md "Niveles de acceso").

Los tres decoradores se aplican a todos los métodos (GET y POST) de la vista.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render

SIN_PERMISO = "No tenés permisos para acceder a esta sección"


def no_store(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        respuesta = vista(request, *args, **kwargs)
        respuesta["Cache-Control"] = "no-store"
        return respuesta

    return envoltura


def sesion_requerida(vista):
    return no_store(login_required(vista))


def administrador_requerido(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not getattr(request.user, "es_administrador", False):
            return render(request, "403.html", {"mensaje": SIN_PERMISO}, status=403)
        return vista(request, *args, **kwargs)

    return no_store(envoltura)
