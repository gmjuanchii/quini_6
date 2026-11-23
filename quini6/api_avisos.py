"""Avisos compartidos entre Django y Next.js ([003] R-31, FR-043, contracts/api.md § 2).

Los avisos son los mensajes de Django guardados en la sesión (sin almacenamiento nuevo). Next.js los
lee al mostrar cada página (``GET``, que los marca como leídos, igual que una plantilla) y sus
Server Actions agregan el suyo antes de redirigir (``POST``, solo por clave del catálogo, nunca
texto libre). Nada se guarda en el navegador (NFR-008).
"""

from string import Formatter
from typing import Literal

from django.contrib import messages
from django.http import HttpResponse
from ninja import Router, Schema

from dominio.mensajes import MENSAJES, mensaje
from quini6.api_base import ProblemaAPI, error_de_campo, nivel

router = Router(tags=["Avisos"])

TipoAviso = Literal["exito", "info", "advertencia", "error"]

#: Nivel de un mensaje de Django ↔ tipo de aviso de la API (RN-09).
_NIVEL_A_TIPO = {
    messages.SUCCESS: "exito",
    messages.INFO: "info",
    messages.DEBUG: "info",
    messages.WARNING: "advertencia",
    messages.ERROR: "error",
}
_TIPO_A_NIVEL = {
    "exito": messages.SUCCESS,
    "info": messages.INFO,
    "advertencia": messages.WARNING,
    "error": messages.ERROR,
}


class Aviso(Schema):
    tipo: TipoAviso
    texto: str


class NuevoAviso(Schema):
    tipo: TipoAviso
    clave: str
    valores: dict[str, str] = {}


def _variables(texto: str) -> set[str]:
    """Variables que pide un texto del catálogo (``{fecha_hora}`` → ``fecha_hora``)."""
    return {nombre for _, nombre, _, _ in Formatter().parse(texto) if nombre}


@router.get("/avisos/", response=list[Aviso])
@nivel("P", sin_cache=True)
def leer_avisos(request):
    """Entrega los avisos pendientes de la sesión y los marca como leídos."""
    return [
        {"tipo": _NIVEL_A_TIPO.get(m.level, "info"), "texto": str(m)}
        for m in messages.get_messages(request)
    ]


@router.post("/avisos/")
@nivel("P", sin_cache=True)
def agregar_aviso(request, datos: NuevoAviso):
    """Agrega un aviso del catálogo con sus variables; lo muestra la aplicación de destino."""
    if datos.clave not in MENSAJES:
        raise ProblemaAPI(
            422,
            "api.detalle_validacion",
            tipo="validacion",
            errores=[error_de_campo("clave", "api.dato_invalido")],
        )
    if _variables(MENSAJES[datos.clave]) != set(datos.valores):
        raise ProblemaAPI(
            422,
            "api.detalle_validacion",
            tipo="validacion",
            errores=[error_de_campo("valores", "api.dato_invalido")],
        )
    texto = mensaje(datos.clave, **datos.valores)
    messages.add_message(request, _TIPO_A_NIVEL[datos.tipo], texto)
    return HttpResponse(status=204)
