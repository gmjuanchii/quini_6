"""Vistas de la extracción histórica ([002] contracts/rutas.md).

Todas usan ``administrador_requerido`` en GET y POST, que agrega ``Cache-Control: no-store``
(NFR-004). Las vistas cargan datos, delegan en el dominio y en los servicios, y renderizan.
"""

import json

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.cache import patch_vary_headers
from django.views.decorators.http import require_http_methods

from cuentas.decoradores import administrador_requerido
from dominio import periodos
from dominio.extraccion.etiqueta import EtiquetaEstado, desde_slug
from dominio.mensajes import mensaje
from extracciones import consultas, forms, servicios
from extracciones.forms import PeriodoForm
from extracciones.models import Extraccion
from quini6 import tablas
from quini6.formulario_pendiente import con_pendiente, reanudable
from quini6.idempotencia import con_idempotencia
from quini6.templatetags.formato_ar import fecha_hora_ar


class _RedireccionVerOtra(HttpResponseRedirect):
    status_code = 303


_INICIO = "/administracion/extracciones/"


def _url(extraccion) -> str:
    return f"/administracion/extracciones/{extraccion.pk}/"


def _acciones(extraccion) -> list[dict]:
    """[003] AC-2.1, AC-2.6: opciones del menú ⋮ de una fila ("Eliminar" solo si terminó)."""
    acciones = [{"texto": mensaje("ext.ver_detalle"), "href": _url(extraccion)}]
    if consultas.puede_descargar(extraccion):
        acciones.append(
            {
                "texto": mensaje("ext.boton_descargar"),
                "href": f"{_url(extraccion)}csv/",
                "icono": "download",
            }
        )
    if not extraccion.en_curso:
        acciones.append(
            {
                "texto": mensaje("ext.eliminar"),
                "href": f"{_url(extraccion)}eliminar/",
                "icono": "trash-2",
                "destructivo": True,
                "confirmar": True,
            }
        )
    return acciones


def _atajos() -> list[periodos.Atajo]:
    """[003] RN-04: "Año en curso" y "Año anterior" con la fecha de hoy en Buenos Aires."""
    return periodos.atajos(forms.hoy_buenos_aires(), "extraccion", None)


def _formulario_vacio(request) -> PeriodoForm:
    """[003] AC-4.4: ``?atajo=<clave>`` (sin scripts) precarga las dos fechas."""
    atajo = periodos.buscar(_atajos(), request.GET.get("atajo"))
    if atajo is None:
        return PeriodoForm()
    return PeriodoForm(initial={"inicio": atajo.desde, "fin": atajo.hasta})


#: [003] RN-05: nombres únicos de las columnas del listado ("Fecha" = inicio, [002] D-24).
_COLUMNAS = [
    ("fecha", "Fecha"),
    ("ejecutada_por", "Ejecutada por"),
    ("periodo", "Período"),
    ("estado", "Estado"),
]


def _contexto_pantalla(request, form, en_curso, error_inicio=None) -> dict:
    filtro = desde_slug(request.GET.get("estado"))  # [003] AC-1.4: inválido → sin filtro
    # [003] AC-9.1, AC-9.2, RN-07: orden y página en la dirección; se conservan entre sí.
    orden = tablas.orden_valido(
        request.GET.get("orden"), consultas.COLUMNAS_ORDEN, consultas.ORDEN_PREDETERMINADO
    )
    pagina = consultas.listado_extracciones(filtro, orden, request.GET.get("pagina"))
    _con_acciones(pagina.elementos)
    parametros = tablas.parametros_de(
        {"estado": filtro.slug if filtro else "", "orden": orden if orden != "-fecha" else ""}
    )
    return {
        "atajos": _atajos(),
        "form": form,
        "en_curso": en_curso,
        "avance": consultas.avance(en_curso) if en_curso else None,
        "extracciones": pagina.elementos,
        "pagina": pagina,
        "parametros": parametros,
        "encabezados": tablas.encabezados(
            parametros, _COLUMNAS, orden, ordenables=consultas.COLUMNAS_ORDEN
        ),
        "filtro": filtro,
        "orden": orden,
        "etiquetas": list(EtiquetaEstado),
        "error_inicio": error_inicio,
    }


@administrador_requerido
@reanudable("extraccion.iniciar")
@require_http_methods(["GET", "POST"])
@con_idempotencia("extraccion.iniciar")
def inicio(request):
    """Formulario o avance propio, y "Extracciones anteriores" (AC-1.1, AC-1.11, AC-1.14).

    [003] AC-3.1, FR-004: con ``HX-Request`` el inicio responde la pantalla actualizada (la fila
    nueva "En curso" y su avance) sin cambiar de página; sin scripts, 303 al detalle como en [002].
    [003] RN-03, AC-3.5: un período idéntico a otro en curso no se inicia.
    """
    en_curso = servicios.extraccion_en_curso(request.user)
    form = None
    error_inicio = None
    if request.method == "POST":
        if en_curso is not None and not _es_htmx(request):
            return _RedireccionVerOtra(_url(en_curso))  # AC-1.11: no se inicia otra
        form = PeriodoForm(request.POST)
        if en_curso is None and form.is_valid():
            resultado = servicios.iniciar_extraccion(request.user, form.periodo)
            if isinstance(resultado, servicios.ErrorInicio):
                error_inicio = resultado
            elif not _es_htmx(request):
                return _RedireccionVerOtra(_url(resultado))
            else:
                en_curso, form = resultado, None
        elif en_curso is not None:
            form = None
    elif en_curso is None and getattr(request, "reanudar", None):
        form = PeriodoForm(initial=con_pendiente(request, {}, PeriodoForm))  # [003] FR-032
    elif en_curso is None:
        form = _formulario_vacio(request)
    contexto = _contexto_pantalla(request, form, en_curso, error_inicio)
    if _es_htmx(request) and request.method == "POST":
        respuesta = render(request, "extracciones/_pantalla.html", contexto)
    else:
        respuesta = render(request, "extracciones/inicio.html", contexto)
    patch_vary_headers(respuesta, ["HX-Request"])
    return respuesta


def _aviso_final(avance: dict) -> str:
    return json.dumps({"aviso": avance["aviso_final"]}, ensure_ascii=False)


@administrador_requerido
@require_http_methods(["GET"])
def extraccion(request, id):
    """Detalle de una extracción. [003] R-10: con ``HX-Request`` responde solo el avance (o la fila
    del listado con ``?fila=1``) y, si terminó, el aviso final en la cabecera ``HX-Trigger``."""
    objeto = consultas.obtener_extraccion(id)
    if _es_htmx(request):
        avance = consultas.avance(objeto)
        if request.GET.get("fila"):
            objeto.etiqueta = avance["etiqueta"]
            _con_acciones([objeto])
            respuesta = render(request, "extracciones/_fila.html", {"e": objeto})
        else:
            respuesta = render(
                request, "extracciones/_avance.html", {"extraccion": objeto, "avance": avance}
            )
        if not avance["en_curso"]:
            respuesta["HX-Trigger"] = _aviso_final(avance)
        patch_vary_headers(respuesta, ["HX-Request"])
        return respuesta
    respuesta = render(request, "extracciones/extraccion.html", consultas.datos_pagina(objeto))
    patch_vary_headers(respuesta, ["HX-Request"])
    return respuesta


@administrador_requerido
@require_http_methods(["GET"])
def sorteo(request, id, numero):
    datos = consultas.detalle_sorteo(consultas.obtener_extraccion(id), numero)
    return render(request, "extracciones/sorteo.html", datos)


def _con_acciones(extracciones):
    for extraccion in extracciones:
        extraccion.acciones = _acciones(extraccion)
        extraccion.nombre_acciones = mensaje(
            "ext.acciones", fecha_hora=fecha_hora_ar(extraccion.iniciada_en)
        )
    return extracciones


def _es_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


@administrador_requerido
@require_http_methods(["GET", "POST"])
@con_idempotencia("extraccion.eliminar")
def eliminar(request, id):
    """Confirmación (GET) y eliminación (POST) de una extracción terminada.

    [002] AC-1.18, AC-1.19. [003] AC-2.3 a AC-2.5: con ``HX-Request`` responde solo el contenido
    del diálogo; sin scripts, la página aparte. Si ya no existe, avisa y vuelve al listado.
    """
    extraccion = Extraccion.objects.select_related("creada_por").filter(pk=id).first()
    if extraccion is None:
        messages.error(request, mensaje("ext.no_existe"))
        return _RedireccionVerOtra(_INICIO)
    if extraccion.en_curso:
        messages.error(request, servicios.NO_ELIMINABLE_EN_CURSO)
        return _RedireccionVerOtra(_INICIO)
    if request.method == "POST":
        momento = fecha_hora_ar(extraccion.iniciada_en)
        error = servicios.eliminar_extraccion(extraccion)
        if error is not None:
            messages.error(request, error)
        else:
            messages.success(request, mensaje("ext.eliminada", fecha_hora=momento))
        return _RedireccionVerOtra(_INICIO)
    plantilla = (
        "extracciones/_eliminar_contenido.html"
        if _es_htmx(request)
        else ("extracciones/eliminar.html")
    )
    respuesta = render(request, plantilla, {"extraccion": extraccion})
    patch_vary_headers(respuesta, ["HX-Request"])
    return respuesta


@administrador_requerido
@require_http_methods(["GET"])
def descargar_csv(request, id):
    """AC-5.1, AC-5.10: siempre el mismo archivo guardado, en UTF-8 sin BOM."""
    nombre, contenido = consultas.archivo(consultas.obtener_extraccion(id))
    respuesta = HttpResponse(contenido.encode("utf-8"), content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta
