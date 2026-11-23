"""Control de acceso en el servidor (R-05, contracts/rutas.md "Niveles de acceso").

Los tres decoradores se aplican a todos los métodos (GET y POST) de la vista.

[003] FR-032, R-12: un POST sin sesión a una vista ``@reanudable`` no pierde lo escrito: se responde
"Ingresar" con el aviso ``cuenta.sesion_vencida`` y el formulario pendiente firmado (200, no-store).
Los GET sin sesión siguen redirigiendo al ingreso como antes.
"""

from functools import wraps
from urllib.parse import quote

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render

from cuentas.forms import IngresoForm
from dominio.mensajes import MENSAJES
from quini6 import formulario_pendiente

SIN_PERMISO = MENSAJES["admin.sin_permiso"]


def no_store(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        respuesta = vista(request, *args, **kwargs)
        respuesta["Cache-Control"] = "no-store"
        return respuesta

    return envoltura


def _sin_sesion(request, vista):
    """Sin sesión: "Ingresar" con el formulario pendiente (POST a una vista reanudable) o la
    redirección al ingreso de siempre."""
    if request.method == "POST" and getattr(vista, "reanudable", None):
        ruta = request.path
        token = formulario_pendiente.firmar(ruta, request.POST)
        contexto = {
            "form": IngresoForm(),
            "next": ruta,
            "next_codificado": quote(ruta, safe="/"),
            "pendiente": token,
            "aviso_sesion": MENSAJES["cuenta.sesion_vencida"],
        }
        return render(request, "cuentas/ingresar.html", contexto)
    return redirect_to_login(request.get_full_path())


def sesion_requerida(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _sin_sesion(request, vista)
        return vista(request, *args, **kwargs)

    return no_store(envoltura)


def administrador_requerido(vista):
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _sin_sesion(request, vista)
        if not getattr(request.user, "es_administrador", False):
            return render(request, "403.html", {"mensaje": SIN_PERMISO}, status=403)
        return vista(request, *args, **kwargs)

    return no_store(envoltura)
