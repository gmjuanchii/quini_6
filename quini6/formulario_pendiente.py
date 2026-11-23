"""Formulario pendiente al vencer la sesión ([003] FR-032, R-12; data-model § 3).

Si un POST llega a una vista privada con formulario sin sesión válida, el servidor responde
"Ingresar" con un campo oculto ``pendiente``: un token firmado (``TimestampSigner``, sal propia,
comprimido) con la ruta destino y lo enviado, **sin** el token CSRF, la clave de idempotencia ni
contraseñas. Tras ingresar, la vista destino se muestra en modo "reanudar": su formulario con esos
valores iniciales, para revisarlo y enviarlo. Nada se envía solo y el token no se guarda en el
navegador ni en el servidor (NFR-008).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django import forms
from django.core import signing
from django.urls import Resolver404, resolve

SAL = "quini6.formulario_pendiente"
VIGENCIA_SEGUNDOS = 60 * 60  # 60 min
TAMANO_MAXIMO = 8 * 1024  # 8 KB
_EXCLUIDOS = {"csrfmiddlewaretoken", "clave_idempotencia", "pendiente", "next"}

#: Vistas reanudables por nombre (data-model § 3, "Vistas reanudables").
REANUDABLES: dict[str, object] = {}


def _excluido(nombre: str) -> bool:
    minusculas = nombre.lower()
    return nombre in _EXCLUIDOS or "password" in minusculas or "contrasena" in minusculas


def firmar(ruta: str, post) -> str | None:
    """Token con la ruta y los campos enviados; ``None`` si supera los 8 KB."""
    campos = {k: post.getlist(k) for k in post if not _excluido(k)}
    token = signing.dumps({"ruta": ruta, "campos": campos}, salt=SAL, compress=True)
    return token if len(token) <= TAMANO_MAXIMO else None


@dataclass(frozen=True)
class FormularioPendiente:
    ruta: str
    campos: dict[str, list[str]]
    vista: object
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)


def ruta_de(token: str | None) -> str | None:
    """Ruta destino de un token válido (firma y vigencia), sin exigir que Django la atienda.

    La usa "Volver al formulario" ([003] AC-14.4), cuando el formulario vive en Next.js.
    """
    if not token or len(token) > TAMANO_MAXIMO:
        return None
    try:
        ruta = str(signing.loads(token, salt=SAL, max_age=VIGENCIA_SEGUNDOS)["ruta"])
    except (signing.BadSignature, KeyError, TypeError, ValueError):
        return None
    return ruta if ruta.startswith("/") and not ruta.startswith("//") else None


def contenido(token: str | None) -> tuple[str, dict[str, list[str]]] | None:
    """Ruta y campos de un token válido (firma, vigencia y tamaño), sin exigir que Django atienda la
    ruta: lo usa Next.js para reabrir su propio formulario ([003] AC-14.4)."""
    ruta = ruta_de(token)
    if ruta is None:
        return None
    datos = signing.loads(token, salt=SAL, max_age=VIGENCIA_SEGUNDOS)
    try:
        campos = {str(k): [str(v) for v in valores] for k, valores in dict(datos["campos"]).items()}
    except (KeyError, TypeError, ValueError):
        return None
    return ruta, campos


def leer(token: str | None) -> FormularioPendiente | None:
    """El formulario pendiente del token, o ``None`` si falta, está alterado, venció, es muy grande
    o su ruta no es de una vista reanudable (en todos esos casos se ignora)."""
    if not token or len(token) > TAMANO_MAXIMO:
        return None
    try:
        datos = signing.loads(token, salt=SAL, max_age=VIGENCIA_SEGUNDOS)
        ruta = str(datos["ruta"])
        campos = {str(k): [str(v) for v in valores] for k, valores in dict(datos["campos"]).items()}
        coincidencia = resolve(ruta)
    except (signing.BadSignature, KeyError, TypeError, ValueError, Resolver404):
        return None
    if not getattr(coincidencia.func, "reanudable", None):
        return None
    return FormularioPendiente(
        ruta, campos, coincidencia.func, coincidencia.args, coincidencia.kwargs
    )


def reanudable(nombre: str):
    """Marca una vista con formulario como reanudable. Va **debajo** de ``sesion_requerida`` o
    ``administrador_requerido``, que así reconocen la marca y conservan lo escrito."""

    def decorador(vista):
        vista.reanudable = nombre
        REANUDABLES[nombre] = vista
        return vista

    return decorador


def con_pendiente(request, inicial: dict | None = None, formulario=None) -> dict:
    """Valores iniciales de un formulario en modo "reanudar": los del token sobre ``inicial``.

    Los campos de opción múltiple (``MultipleChoiceField``) reciben la lista; los demás, el primer
    valor. Fuera del modo "reanudar", devuelve ``inicial`` sin cambios.
    """
    resultado = dict(inicial or {})
    campos = getattr(request, "reanudar", None)
    if not campos:
        return resultado
    declarados = getattr(formulario, "base_fields", {}) if formulario is not None else {}
    for nombre, valores in campos.items():
        if isinstance(declarados.get(nombre), forms.MultipleChoiceField):
            resultado[nombre] = list(valores)
        elif valores:
            resultado[nombre] = valores[0]
    return resultado
