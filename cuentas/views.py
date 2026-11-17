"""Registro, ingreso y salida (FR-015 a FR-018, AC-3.1 a AC-3.10)."""

from urllib.parse import quote

from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from cuentas import servicios
from cuentas.decoradores import no_store, sesion_requerida
from cuentas.forms import IngresoForm, RegistroForm

DESTINO_PREDETERMINADO = "/mis-jugadas/"
CORREO_EXISTENTE = "Ya existe una cuenta con este correo electrónico. Iniciá sesión."
CREDENCIALES = "Correo electrónico o contraseña incorrectos"


def _next(request) -> str:
    """Destino validado (FR-017): solo rutas de este mismo sitio."""
    destino = request.POST.get("next") or request.GET.get("next") or ""
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return destino
    return ""


def _contexto(request, form, **extra):
    destino = _next(request)
    return {
        "form": form,
        "next": destino,
        "next_codificado": quote(destino, safe="/") if destino else "",
        **extra,
    }


@no_store
@require_http_methods(["GET", "POST"])
def registrarse(request):
    form = RegistroForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        resultado = servicios.registrar(form.cleaned_data["email"], form.cleaned_data["password"])
        if isinstance(resultado, servicios.ErrorRegistro):
            error = CORREO_EXISTENTE
        else:
            login(request, resultado, backend="django.contrib.auth.backends.ModelBackend")
            return redirect(_next(request) or DESTINO_PREDETERMINADO)
    return render(request, "cuentas/registrarse.html", _contexto(request, form, error=error))


@no_store
@require_http_methods(["GET", "POST"])
def ingresar(request):
    form = IngresoForm(request.POST or None)
    error = None
    if request.method == "POST" and form.is_valid():
        ingreso = servicios.ingresar(
            request, form.cleaned_data["email"], form.cleaned_data["password"]
        )
        if ingreso.ok:
            return redirect(_next(request) or DESTINO_PREDETERMINADO)
        if ingreso.resultado == "BLOQUEADO":
            hora = timezone.localtime(ingreso.hasta).strftime("%H:%M")
            error = (
                "Por seguridad, bloqueamos el acceso por 15 minutos. "
                f"Podés volver a intentar a las {hora}."
            )
        else:
            error = CREDENCIALES
    return render(request, "cuentas/ingresar.html", _contexto(request, form, error=error))


@sesion_requerida
@require_POST
def salir(request):
    logout(request)
    return redirect("/resultados/")
