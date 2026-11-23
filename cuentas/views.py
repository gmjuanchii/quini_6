"""Registro, ingreso y salida (FR-015 a FR-018, AC-3.1 a AC-3.10)."""

from urllib.parse import quote

from django.contrib.auth import login, logout
from django.http import QueryDict
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods, require_POST

from cuentas import servicios
from cuentas.decoradores import no_store, sesion_requerida
from cuentas.forms import IngresoForm, RegistroForm
from dominio.mensajes import MENSAJES, mensaje
from quini6 import formulario_pendiente
from quini6.enrutamiento import es_de_next
from quini6.idempotencia import con_idempotencia

DESTINO_PREDETERMINADO = "/mis-jugadas/"
#: [003] HU-11: textos del catálogo (la plantilla agrega el enlace "Ingresar" al correo existente).
CORREO_EXISTENTE = MENSAJES["cuenta.correo_existente"]
CREDENCIALES = MENSAJES["cuenta.credenciales_incorrectas"]


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
@con_idempotencia("cuenta.crear")  # [003] FR-031
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
    # [003] R-12, AC-14.4: un formulario de Next.js con la sesión vencida llega con solo el
    # ``pendiente`` (sin correo ni contraseña): se muestra "Ingresar" sin errores, con el token.
    solo_pendiente = request.method == "POST" and "email" not in request.POST
    form = IngresoForm(None if solo_pendiente else (request.POST or None))
    error = None
    if request.method == "POST" and not solo_pendiente and form.is_valid():
        ingreso = servicios.ingresar(
            request, form.cleaned_data["email"], form.cleaned_data["password"]
        )
        if ingreso.ok:
            reanudado = _reanudar(request)
            if reanudado is not None:
                return reanudado
            return redirect(_next(request) or DESTINO_PREDETERMINADO)
        if ingreso.resultado == "BLOQUEADO":
            hora = timezone.localtime(ingreso.hasta).strftime("%H:%M")
            error = mensaje("cuenta.bloqueada", hora=hora)
        else:
            error = CREDENCIALES
    pendiente = request.POST.get("pendiente") if request.method == "POST" else None
    contexto = _contexto(request, form, error=error, pendiente=pendiente)
    return render(request, "cuentas/ingresar.html", contexto)


def _reanudar(request):
    """[003] FR-032, R-12: con un formulario pendiente válido, responde su vista en modo
    "reanudar" (como GET, con lo escrito como valores iniciales). La vista vuelve a verificar los
    permisos con la cuenta que acaba de ingresar y no registra nada; la persona revisa y envía.

    Si la ruta del token la atiende Next.js ([003] AC-14.4), responde "Volver al formulario": un
    único botón que envía el token por POST a esa ruta, donde Next.js muestra el formulario
    precargado. Ese POST solo reabre el formulario; nunca registra nada."""
    token = request.POST.get("pendiente")
    ruta = formulario_pendiente.ruta_de(token)
    if ruta is not None and es_de_next(ruta):
        respuesta = render(
            request, "cuentas/volver_formulario.html", {"ruta": ruta, "pendiente": token}
        )
        respuesta["Cache-Control"] = "no-store"
        return respuesta
    pendiente = formulario_pendiente.leer(token)
    if pendiente is None:
        return None
    request.method = "GET"
    request.GET = QueryDict()
    request.POST = QueryDict()
    request.reanudar = pendiente.campos
    request.path = request.path_info = pendiente.ruta
    respuesta = pendiente.vista(request, *pendiente.args, **pendiente.kwargs)
    respuesta["Cache-Control"] = "no-store"
    return respuesta


@sesion_requerida
@require_POST
def salir(request):
    logout(request)
    return redirect("/resultados/")
