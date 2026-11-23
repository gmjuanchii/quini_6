"""Filtros de plantilla de la interfaz ([003] R-04, R-05, R-11, R-13).

- ``{% msg "clave" var=valor %}``: texto del catálogo único (dominio/mensajes.py).
- ``{% clases "componente" variante="…" tamano="…" extra="…" %}``: clases de ui/variantes.json.
- ``{% icono "nombre" clase="size-5" %}``: SVG de la lista cerrada (contracts/componentes.md § 2).
- ``{% marca "logotipo" clase="…" %}``: logotipo o isotipo de ui/marca, en línea (RN-08).
- ``{{ texto|sin_flecha }}``: quita la "← " inicial (la flecha la pone el icono de BackLink).
- ``{% campo_idempotencia %}``: campo oculto ``clave_idempotencia`` (FR-031).
- ``{% accion_formulario %}`` / ``{% accion_formulario "/ruta/" %}``: ``action`` de un formulario
  POST con la marca ``?_interfaz=django`` (el enrutador lo entrega a Django, R-20, FR-044).
- ``{{ campo|reglas }}``: ``data-validar`` de un campo de Django (validación previa, FR-033).
- ``{% campo_fecha campo %}`` / ``{% campo_fecha nombre=… id=… etiqueta=… %}``: DateField (FR-010).
- ``{% periodo desde hasta atajos=… %}``: DateRangePicker con atajos (FR-011, RN-04).
"""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path

from django import template
from django.conf import settings
from django.http import QueryDict
from django.utils.html import format_html
from django.utils.module_loading import import_string
from django.utils.safestring import mark_safe

from dominio.mensajes import mensaje
from quini6.enrutamiento import MARCA_DJANGO, VALOR_MARCA_DJANGO
from quini6.fechas import regla_fecha, valor_iso
from quini6.idempotencia import nueva_clave
from quini6.tablas import con_parametros

register = template.Library()

_RUTA_ICONOS = Path(settings.BASE_DIR) / "templates" / "ui" / "iconos"


@register.simple_tag
def msg(clave: str, **valores) -> str:
    """Texto visible por su clave; Django escapa el resultado (autoescape)."""
    return mensaje(clave, **valores)


@cache
def _variantes() -> dict:
    ruta = Path(settings.BASE_DIR) / "ui" / "variantes.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


@register.simple_tag
def clases(componente: str, variante: str = "", tamano: str = "", extra: str = "") -> str:
    """Clases de un componente: base + variante + tamaño + extra (sin duplicados)."""
    try:
        definicion = _variantes()[componente]
    except KeyError as error:
        raise template.TemplateSyntaxError(f"Componente desconocido: {componente}") from error
    partes = [definicion["base"]]
    if variante:
        if variante not in definicion["variantes"]:
            raise template.TemplateSyntaxError(f"Variante desconocida de {componente}: {variante}")
        partes.append(definicion["variantes"][variante])
    tamanos = definicion.get("tamanos") or {}
    if tamanos:
        elegido = tamano or "md"
        if elegido not in tamanos:
            raise template.TemplateSyntaxError(f"Tamaño desconocido de {componente}: {elegido}")
        partes.append(tamanos[elegido])
    if extra:
        partes.append(extra)
    vistas: list[str] = []
    for clase in " ".join(partes).split():
        if clase not in vistas:
            vistas.append(clase)
    return " ".join(vistas)


@cache
def _svg(nombre: str) -> str:
    ruta = _RUTA_ICONOS / f"{nombre}.svg"
    if not re.fullmatch(r"[a-z0-9-]+", nombre) or not ruta.is_file():
        raise template.TemplateSyntaxError(f"Icono fuera de la lista cerrada: {nombre}")
    return ruta.read_text(encoding="utf-8").strip()


@register.simple_tag
def icono(nombre: str, clase: str = "size-5 shrink-0") -> str:
    """SVG decorativo: siempre ``aria-hidden`` y ``focusable="false"`` (AC-13.5)."""
    svg = _svg(nombre)
    atributos = format_html(' class="{}" aria-hidden="true" focusable="false"', clase)
    return mark_safe(svg.replace("<svg", "<svg" + atributos, 1))  # noqa: S308 (SVG propio)


@cache
def _svg_marca(nombre: str) -> str:
    ruta = Path(settings.BASE_DIR) / "ui" / "marca" / f"{nombre}.svg"
    if nombre not in {"logotipo", "isotipo"}:
        raise template.TemplateSyntaxError(f"Marca desconocida: {nombre}")
    svg = ruta.read_text(encoding="utf-8").strip()
    # En línea es decorativa: el nombre accesible lo da el enlace (nav.logotipo).
    return re.sub(r'\s(role|aria-label)="[^"]*"', "", svg)


@register.simple_tag
def marca(nombre: str, clase: str = "") -> str:
    """Logotipo o isotipo en línea, con ``currentColor`` del tema (RN-08, AC-12.4)."""
    atributos = format_html(' class="{}" aria-hidden="true" focusable="false"', clase)
    return mark_safe(_svg_marca(nombre).replace("<svg", "<svg" + atributos, 1))  # noqa: S308


@register.filter
def sin_flecha(texto: str) -> str:
    return str(texto).removeprefix("← ")


@register.filter
def pregunta_y_accion(texto: str) -> tuple[str, str]:
    """ "¿Todavía sin cuenta? Crear cuenta" → ("¿Todavía sin cuenta?", "Crear cuenta") (AC-6.7)."""
    pregunta, _, accion = str(texto).partition("? ")
    return (f"{pregunta}?", accion) if accion else ("", pregunta)


#: [003] RN-09: nivel de un mensaje de Django → variante del Callout, rol y tipo de Toast.
_AVISOS = {
    "success": {"variante": "success", "rol": "status", "tipo": "success"},
    "info": {"variante": "info", "rol": "status", "tipo": "info"},
    "warning": {"variante": "warning", "rol": "status", "tipo": "warning"},
    "error": {"variante": "danger", "rol": "alert", "tipo": "error"},
}


@register.filter
def aviso_de(mensaje_django) -> dict:
    """Cómo se presenta un mensaje de Django (``messages``) según su nivel ([003] AC-10.3)."""
    return _AVISOS.get(getattr(mensaje_django, "level_tag", ""), _AVISOS["info"])


@register.simple_tag
def url_con(parametros, **cambios) -> str:
    """``{% url_con request.GET pagina=2 %}``: la consulta actual con un parámetro reemplazado
    (``None`` o vacío lo quita), conservando filtro y orden ([003] RN-07, AC-9.2)."""
    if hasattr(parametros, "GET"):
        parametros = parametros.GET
    return con_parametros(parametros, **cambios)


@register.simple_tag(takes_context=True)
def accion_formulario(context, *partes) -> str:
    """Dirección de envío de un formulario POST de Django con ``?_interfaz=django`` ([003] R-20).

    ``partes`` se concatenan (``{% accion_formulario "/a/" pk "/eliminar/" %}``); sin partes, la
    dirección actual con sus parámetros (como ``action=""``). Así, un formulario abierto antes de
    conmutar su pantalla a Next.js, o después de una reversa, se envía igual a Django.
    """
    ruta = "".join(str(p) for p in partes)
    if ruta:
        base, _, consulta = ruta.partition("?")
        parametros = QueryDict(consulta, mutable=True)
    else:
        request = context.get("request")
        base = request.path if request is not None else ""
        parametros = request.GET.copy() if request is not None else QueryDict(mutable=True)
    parametros[MARCA_DJANGO] = VALOR_MARCA_DJANGO
    return f"{base}?{parametros.urlencode()}"


@register.simple_tag
def campo_idempotencia() -> str:
    """Campo oculto con una clave nueva por formulario mostrado ([003] R-11)."""
    return format_html('<input type="hidden" name="clave_idempotencia" value="{}">', nueva_clave())


#: Controles de una sola entrada a los que se les agrega "requerido" con el texto del formulario.
_ENTRADAS_SIMPLES = {"text", "date", "email", "password", "number"}


def _reglas(campo) -> list[dict]:
    """Reglas previas de un campo: las que declara el formulario (``campo.field.reglas_previas``),
    el formato de fecha si el control es de fecha y "requerido" con el mismo texto que usa el
    servidor ([003] FR-033, R-13). Ninguna regla existe solo en el navegador."""
    lista = [dict(r) for r in getattr(campo.field, "reglas_previas", None) or []]
    nombres = {r["regla"] for r in lista}
    tipo = getattr(campo.field.widget, "input_type", "")
    if tipo == "date" and "fecha" not in nombres:
        lista.append(regla_fecha())
    texto_requerido = campo.field.error_messages.get("required")
    if campo.field.required and tipo in _ENTRADAS_SIMPLES and "requerido" not in nombres:
        if texto_requerido:
            lista.insert(0, {"regla": "requerido", "texto": str(texto_requerido)})
    return lista


@register.simple_tag
def reglas_de(formulario: str, nombre: str) -> str:
    """``data-validar`` de un campo de un formulario de Django por su ruta, para los campos escritos
    a mano en una plantilla (p. ej. ``resultados.forms.MotivoForm`` y ``motivo``): las mismas reglas
    y textos que valida el servidor ([003] FR-033)."""
    return reglas(import_string(formulario)()[nombre])


@register.filter
def reglas(campo) -> str:
    """``data-validar`` (JSON) de un campo de formulario de Django; vacío si no tiene reglas."""
    lista = _reglas(campo)
    return json.dumps(lista, ensure_ascii=False) if lista else ""


def _datos_fecha(campo=None, **opciones) -> dict:
    """Datos de un DateField desde un campo de Django o desde valores sueltos (formularios
    escritos a mano, como Estadísticas o la búsqueda de resultados)."""
    if campo is not None:
        atributos = campo.field.widget.attrs
        datos = {
            "nombre": campo.html_name,
            "id": campo.auto_id,
            "etiqueta": campo.label,
            "valor": valor_iso(campo.value()),
            "min": atributos.get("min", ""),
            "max": atributos.get("max", ""),
            "ayuda": campo.help_text,
            "error": " ".join(str(e) for e in campo.errors),
            "reglas": _reglas(campo),
        }
    else:
        datos = {"nombre": "", "id": "", "etiqueta": "", "valor": "", "min": "", "max": ""}
        datos.update({"ayuda": "", "error": "", "reglas": [regla_fecha()]})
    datos.update(opciones)
    datos["valor"] = valor_iso(datos.get("valor"))
    if not isinstance(datos.get("reglas"), str):
        datos["reglas"] = json.dumps(datos["reglas"], ensure_ascii=False) if datos["reglas"] else ""
    return datos


@register.inclusion_tag("ui/_campo_fecha.html")
def campo_fecha(campo=None, **opciones) -> dict:
    """DateField ([003] contracts/componentes.md, AC-4.1, AC-4.2, AC-4.6, AC-4.7, FR-010)."""
    return {"f": _datos_fecha(campo, **opciones)}


@register.inclusion_tag("ui/_periodo.html")
def periodo(desde, hasta, atajos=(), parametros="", leyenda="") -> dict:
    """DateRangePicker: dos DateField, un calendario de rango y los atajos de RN-04 como enlaces
    ``?atajo=<clave>`` (más ``parametros`` de la dirección, p. ej. ``&modalidad=…``)."""
    campos = []
    for campo in (desde, hasta):
        datos = dict(campo) if isinstance(campo, dict) else _datos_fecha(campo)
        campos.append({**_datos_fecha(**datos), "en_periodo": True})
    return {
        "desde": campos[0],
        "hasta": campos[1],
        "atajos": atajos,
        "parametros": parametros,
        "leyenda": leyenda or mensaje("fecha.periodo"),
        "min": campos[0]["min"] or campos[1]["min"],
        "max": campos[1]["max"] or campos[0]["max"],
    }
