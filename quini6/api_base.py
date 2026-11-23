"""Base común de la API v1 ([003] R-16, contracts/api.md § 1).

- ``crear_api``: instancia de Django Ninja con errores en formato Problem Details (RFC 9457).
- ``nivel("P" | "U" | "A")``: mismas reglas de acceso que las vistas HTML (cuentas/decoradores.py),
  CSRF obligatorio en los métodos que modifican y ``Cache-Control`` según el nivel.
- ``ProblemaAPI``: error como respuesta, con clave del catálogo y errores por campo.

Las operaciones son tan delgadas como las vistas HTML: consultas → dominio → servicios → respuesta.
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import wraps
from typing import Annotated

from django.conf import settings
from django.http import Http404, HttpResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.utils import timezone
from ninja import NinjaAPI
from ninja.decorators import decorate_view
from ninja.errors import HttpError, ValidationError
from pydantic import PlainSerializer

from dominio.mensajes import mensaje
from quini6.fechas import ZONA

#: contracts/api.md § 1: fecha y hora ISO 8601 en la hora de Buenos Aires (``-03:00``).
FechaHora = Annotated[
    datetime,
    PlainSerializer(lambda d: timezone.localtime(d, ZONA).isoformat(), return_type=str),
]

TIPO_BASE = "https://quini6.local/problemas/"
NIVELES = {"P", "U", "A"}
_METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS", "TRACE"}
_UBICACIONES = {"body", "query", "path", "form", "header", "cookie", "payload", "datos"}


def problema(
    estado: int,
    tipo: str,
    titulo: str,
    detalle: str,
    errores: list[dict] | None = None,
    **extensiones,
) -> HttpResponse:
    """Respuesta ``application/problem+json`` con los textos ya resueltos del catálogo."""
    cuerpo = {"type": TIPO_BASE + tipo, "title": titulo, "status": estado, "detail": detalle}
    if errores is not None:
        cuerpo["errores"] = errores
    cuerpo.update({k: v for k, v in extensiones.items() if v is not None})
    respuesta = HttpResponse(
        json.dumps(cuerpo, ensure_ascii=False),
        status=estado,
        content_type="application/problem+json; charset=utf-8",
    )
    respuesta["Cache-Control"] = "no-store"
    return respuesta


class ProblemaAPI(Exception):
    """Error de una operación con claves del catálogo (se convierte en Problem Details)."""

    def __init__(
        self,
        estado: int,
        clave_detalle: str,
        *,
        tipo: str = "error",
        clave_titulo: str | None = None,
        errores: list[dict] | None = None,
        valores: dict | None = None,
        **extensiones,
    ):
        super().__init__(clave_detalle)
        self.estado = estado
        self.tipo = tipo
        self.clave_titulo = clave_titulo
        self.clave_detalle = clave_detalle
        self.errores = errores
        self.valores = valores or {}
        self.extensiones = extensiones


def error_de_campo(campo: str, clave: str, **valores) -> dict:
    return {"campo": campo, "codigo": clave, "mensaje": mensaje(clave, **valores)}


def _campo(ubicacion) -> str:
    partes = [str(p) for p in ubicacion if str(p) not in _UBICACIONES]
    return partes[-1] if partes else ""


_TITULOS_POR_ESTADO = {
    401: "api.titulo_sin_sesion",
    403: "api.titulo_sin_permiso",
    404: "api.titulo_no_encontrado",
    409: "api.titulo_conflicto",
    422: "api.titulo_validacion",
}


def crear_api(urls_namespace: str = "api", docs_url: str | None = "/docs") -> NinjaAPI:
    api = NinjaAPI(
        title="QUINI_6 API",
        version="1",
        description="API v1 de QUINI_6 ([003] contracts/api.md).",
        urls_namespace=urls_namespace,
        docs_url=docs_url if settings.DEBUG else None,
    )

    @api.exception_handler(ValidationError)
    def _validacion(request, exc: ValidationError):
        errores = [
            {
                "campo": _campo(e.get("loc", ())),
                "codigo": e.get("type", "invalido"),
                "mensaje": mensaje("api.dato_invalido"),
            }
            for e in exc.errors
        ]
        return problema(
            422,
            "validacion",
            mensaje("api.titulo_validacion"),
            mensaje("api.detalle_validacion"),
            errores,
        )

    @api.exception_handler(Http404)
    def _no_encontrado(request, exc):
        return problema(
            404,
            "no-encontrado",
            mensaje("api.titulo_no_encontrado"),
            mensaje("api.detalle_no_encontrado"),
        )

    @api.exception_handler(HttpError)
    def _http(request, exc: HttpError):
        clave = _TITULOS_POR_ESTADO.get(exc.status_code, "api.titulo_conflicto")
        return problema(exc.status_code, "error", mensaje(clave), str(exc))

    @api.exception_handler(ProblemaAPI)
    def _problema(request, exc: ProblemaAPI):
        titulo = exc.clave_titulo or _TITULOS_POR_ESTADO.get(exc.estado, "api.titulo_conflicto")
        return problema(
            exc.estado,
            exc.tipo,
            mensaje(titulo),
            mensaje(exc.clave_detalle, **exc.valores),
            exc.errores,
            **exc.extensiones,
        )

    return api


def _csrf_rechazado(request) -> bool:
    def _vista(*args, **kwargs):  # sin csrf_exempt: el middleware verifica de verdad
        return None

    return CsrfViewMiddleware(lambda r: None).process_view(request, _vista, (), {}) is not None


def _pendiente(request, ruta: str, kwargs: dict) -> str | None:
    """[003] R-12: token ``pendiente`` con lo enviado en el cuerpo JSON (sin contraseñas)."""
    from django.http import QueryDict

    from quini6.formulario_pendiente import firmar

    try:
        cuerpo = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        cuerpo = {}
    datos = QueryDict(mutable=True)
    for nombre, valor in cuerpo.items() if isinstance(cuerpo, dict) else []:
        for v in valor if isinstance(valor, list) else [valor]:
            datos.appendlist(nombre, "" if v is None else str(v))
    return firmar(ruta.format(**kwargs), datos)


def rechazo_de_acceso(request, codigo: str, pendiente: str | None = None) -> HttpResponse | None:
    """``401``/``403`` si la persona no tiene el nivel ``codigo``; ``None`` si puede seguir.

    La usan ``nivel`` y las operaciones cuyo nivel depende de un parámetro (atajos de período).
    """
    if codigo in {"U", "A"} and not request.user.is_authenticated:
        return problema(
            401,
            "sin-sesion",
            mensaje("api.titulo_sin_sesion"),
            mensaje("api.detalle_sin_sesion"),
            pendiente=pendiente,
        )
    if codigo == "A" and not getattr(request.user, "es_administrador", False):
        return problema(
            403, "sin-permiso", mensaje("api.titulo_sin_permiso"), mensaje("admin.sin_permiso")
        )
    return None


def nivel(codigo: str, *, sin_cache: bool | None = None, ruta_pendiente: str | None = None):
    """Nivel de acceso de una operación: P público, U usuario registrado, A administrador.

    ``ruta_pendiente``: ruta HTML del formulario (con ``{parámetros}`` de la operación); sin sesión,
    el ``401`` lleva ``pendiente`` firmado con lo enviado para reanudarlo tras ingresar (R-12).

    Uso (debajo del decorador de la ruta)::

        @router.get("/sesion/")
        @nivel("P", sin_cache=True)
        def sesion(request): ...
    """
    if codigo not in NIVELES:
        raise ValueError(f"Nivel desconocido: {codigo}")
    privada = codigo in {"U", "A"} if sin_cache is None else sin_cache

    def decorador_vista(run):
        @wraps(run)
        def envoltura(request, *args, **kwargs):
            if request.method not in _METODOS_SEGUROS and _csrf_rechazado(request):
                return problema(
                    403, "csrf", mensaje("api.titulo_csrf"), mensaje("gral.csrf_vencido")
                )
            pendiente = None
            if (
                ruta_pendiente
                and request.method not in _METODOS_SEGUROS
                and not request.user.is_authenticated
            ):
                pendiente = _pendiente(request, ruta_pendiente, kwargs)
            rechazo = rechazo_de_acceso(request, codigo, pendiente=pendiente)
            if rechazo is not None:
                return rechazo
            respuesta = run(request, *args, **kwargs)
            if not respuesta.has_header("Cache-Control"):
                respuesta["Cache-Control"] = "no-store" if privada else "no-cache"
            return respuesta

        return envoltura

    def decorador(funcion):
        funcion.nivel_quini6 = codigo
        return decorate_view(decorador_vista)(funcion)

    return decorador
