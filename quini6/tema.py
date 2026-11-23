"""Preferencia de tema claro, oscuro o según el dispositivo ([003] HU-12, FR-036, R-14).

La preferencia vive solo en la cookie ``quini6_tema`` del navegador (data-model § 4): el servidor la
lee para escribir ``data-theme`` en ``<html>`` antes de enviar la página (sin destello de tema
equivocado, NFR-004) y no la registra en la base ni en la sesión (NFR-008).
"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

COOKIE = "quini6_tema"
TEMAS = ("claro", "oscuro")
DISPOSITIVO = "dispositivo"
DURACION = 400 * 24 * 60 * 60  # 400 días (data-model § 4)


class _Redireccion(HttpResponseRedirect):
    status_code = 303


def tema_de(request) -> str:
    """``claro``, ``oscuro`` o ``dispositivo`` (sin cookie o con un valor inválido)."""
    valor = request.COOKIES.get(COOKIE, "")
    return valor if valor in TEMAS else DISPOSITIVO


def tema(request) -> dict:
    """Procesador de contexto: ``tema_actual`` para ``<html data-theme>`` y el selector."""
    return {"tema_actual": tema_de(request)}


def _destino(request) -> str:
    siguiente = request.POST.get("next") or ""
    seguro = url_has_allowed_host_and_scheme(
        siguiente, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    )
    return siguiente if siguiente and seguro and siguiente.startswith("/") else "/"


@require_POST
def preferencia_tema(request):
    """``POST /preferencias/tema/`` (funciona sin scripts): fija o borra la cookie y vuelve a la
    página con 303. Un valor desconocido no cambia nada (AC-12.2)."""
    respuesta = _Redireccion(_destino(request))
    elegido = request.POST.get("tema", "")
    if elegido in TEMAS:
        respuesta.set_cookie(
            COOKIE,
            elegido,
            max_age=DURACION,
            path="/",
            samesite="Lax",
            httponly=False,  # el selector la cambia sin recargar (R-14)
            secure=settings.SESSION_COOKIE_SECURE,
        )
    elif elegido == DISPOSITIVO:
        respuesta.delete_cookie(COOKIE, path="/", samesite="Lax")
    return respuesta
