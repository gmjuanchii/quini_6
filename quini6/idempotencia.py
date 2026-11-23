"""Reintentos sin duplicar el efecto ([003] FR-031, R-11, data-model § 3).

Cada formulario que crea o elimina algo lleva un campo oculto ``clave_idempotencia`` (UUID v4); en
la API, la cabecera ``Idempotency-Key``. Las últimas claves usadas se guardan en la sesión del
servidor (vence con ella) junto con el resultado: un reintento con la misma clave recibe el mismo
resultado sin volver a ejecutar la acción.
"""

from __future__ import annotations

import uuid
from functools import wraps

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils import timezone

MAX_CLAVES = 50
_CLAVE_SESION = "claves_idempotencia"


class _RedireccionVerOtra(HttpResponseRedirect):
    status_code = 303


def nueva_clave() -> str:
    return str(uuid.uuid4())


def clave_del_pedido(request) -> str | None:
    clave = request.POST.get("clave_idempotencia") or request.headers.get("Idempotency-Key")
    return clave.strip() if clave and clave.strip() else None


def buscar(request, clave: str) -> dict | None:
    for entrada in request.session.get(_CLAVE_SESION, []):
        if entrada["clave"] == clave:
            return entrada
    return None


def registrar(request, clave: str, accion: str, resultado: str) -> None:
    entradas = [e for e in request.session.get(_CLAVE_SESION, []) if e["clave"] != clave]
    entradas.append(
        {
            "clave": clave,
            "accion": accion,
            "resultado": resultado,
            "usada_en": timezone.now().isoformat(),
        }
    )
    request.session[_CLAVE_SESION] = entradas[-MAX_CLAVES:]


def con_idempotencia(accion: str):
    """Decorador para vistas POST que responden con una redirección.

    Ante una clave ya usada con la misma acción, devuelve el mismo 303 sin ejecutar la vista; con
    otra acción, 400. Sin clave, la vista se procesa normalmente.
    """

    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if request.method != "POST":
                return vista(request, *args, **kwargs)
            clave = clave_del_pedido(request)
            if clave is None:
                return vista(request, *args, **kwargs)
            anterior = buscar(request, clave)
            if anterior is not None:
                if anterior["accion"] != accion:
                    return HttpResponseBadRequest("Clave de idempotencia usada con otra acción")
                return _RedireccionVerOtra(anterior["resultado"])
            respuesta = vista(request, *args, **kwargs)
            if 300 <= respuesta.status_code < 400 and respuesta.get("Location"):
                registrar(request, clave, accion, respuesta["Location"])
            return respuesta

        return envoltura

    return decorador


# -- API v1 (cabecera Idempotency-Key, contracts/api.md § 1) ------------------------------


def anterior_api(request, accion: str) -> tuple[str | None, dict | None]:
    """Clave de la cabecera y su uso anterior con la misma ``accion`` (``None`` si es nueva).

    Una clave ya usada con otra acción se rechaza con 422 (data-model § 3).
    """
    from quini6.api_base import ProblemaAPI, error_de_campo

    clave = (request.headers.get("Idempotency-Key") or "").strip() or None
    if clave is None:
        return None, None
    anterior = buscar(request, clave)
    if anterior is not None and anterior["accion"] != accion:
        raise ProblemaAPI(
            422,
            "api.detalle_validacion",
            tipo="validacion",
            errores=[error_de_campo("Idempotency-Key", "api.dato_invalido")],
        )
    return clave, anterior
