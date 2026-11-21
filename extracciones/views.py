"""Vistas de la extracción histórica ([002] contracts/rutas.md).

Todas usan ``administrador_requerido`` en GET y POST, que agrega ``Cache-Control: no-store``
(NFR-004). Las vistas cargan datos, delegan en el dominio y en los servicios, y renderizan.
"""

from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from cuentas.decoradores import administrador_requerido
from extracciones import consultas, servicios
from extracciones.forms import PeriodoForm


class _RedireccionVerOtra(HttpResponseRedirect):
    status_code = 303


_INICIO = "/administracion/extracciones/"


def _url(extraccion) -> str:
    return f"/administracion/extracciones/{extraccion.pk}/"


@administrador_requerido
@require_http_methods(["GET", "POST"])
def inicio(request):
    """Formulario o avance propio, y "Extracciones anteriores" (AC-1.1, AC-1.11, AC-1.14)."""
    en_curso = servicios.extraccion_en_curso(request.user)
    form = None
    if request.method == "POST":
        if en_curso is not None:
            return _RedireccionVerOtra(_url(en_curso))  # AC-1.11: no se inicia otra
        form = PeriodoForm(request.POST)
        if form.is_valid():
            extraccion = servicios.iniciar_extraccion(request.user, form.periodo)
            return _RedireccionVerOtra(_url(extraccion))
    elif en_curso is None:
        form = PeriodoForm()
    contexto = {
        "form": form,
        "en_curso": en_curso,
        "avance": consultas.avance(en_curso) if en_curso else None,
        "extracciones": consultas.listado_extracciones(),
    }
    return render(request, "extracciones/inicio.html", contexto)


@administrador_requerido
@require_http_methods(["GET"])
def extraccion(request, id):
    datos = consultas.datos_pagina(consultas.obtener_extraccion(id))
    return render(request, "extracciones/extraccion.html", datos)


@administrador_requerido
@require_http_methods(["GET"])
def sorteo(request, id, numero):
    datos = consultas.detalle_sorteo(consultas.obtener_extraccion(id), numero)
    return render(request, "extracciones/sorteo.html", datos)


@administrador_requerido
@require_http_methods(["GET", "POST"])
def eliminar(request, id):
    """Confirmación (GET) y eliminación (POST) de una extracción terminada (AC-1.18, AC-1.19)."""
    extraccion = consultas.obtener_extraccion(id)
    if extraccion.en_curso:
        messages.error(request, servicios.NO_ELIMINABLE_EN_CURSO)
        return _RedireccionVerOtra(_INICIO)
    if request.method == "POST":
        error = servicios.eliminar_extraccion(extraccion)
        if error is not None:
            messages.error(request, error)
        else:
            messages.success(request, "Extracción eliminada")
        return _RedireccionVerOtra(_INICIO)
    return render(request, "extracciones/eliminar.html", {"extraccion": extraccion})


@administrador_requerido
@require_http_methods(["GET"])
def descargar_csv(request, id):
    """AC-5.1, AC-5.10: siempre el mismo archivo guardado, en UTF-8 sin BOM."""
    nombre, contenido = consultas.archivo(consultas.obtener_extraccion(id))
    respuesta = HttpResponse(contenido.encode("utf-8"), content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta
