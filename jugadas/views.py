"""Jugadas personales (US4) y su comparación con los resultados oficiales (US5).

Toda consulta se filtra por la cuenta en sesión: una jugada ajena responde igual que una
inexistente (RN-36, AC-4.12).
"""

from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from cuentas.decoradores import sesion_requerida
from dominio.comparacion import (
    EstadoResumido,
    cambio_por_correccion,
    comparar_jugada,
    resumir_jugada,
)
from jugadas import servicios
from jugadas.forms import JugadaForm
from jugadas.models import Jugada
from resultados import consultas
from resultados.models import VersionPremios

NO_EXISTE = "La jugada no existe o no está disponible"


def _prefetch_jugadas(qs):
    return qs.select_related("concurso").prefetch_related(
        "concurso__modalidades__versiones_numeros",
        Prefetch(
            "concurso__modalidades__versiones_premios",
            queryset=VersionPremios.objects.prefetch_related("categorias"),
        ),
    )


def _jugada_propia(request, id_: int):
    jugada = _prefetch_jugadas(Jugada.objects.filter(pk=id_, usuario=request.user)).first()
    if jugada is None:
        return None, render(request, "jugadas/no_existe.html", {"mensaje": NO_EXISTE}, status=404)
    return jugada, None


def _modalidades(concurso) -> list[str]:
    return [mc.modalidad_enum.nombre for mc in consultas._modalidades(concurso)]


CLASE_RESUMEN = {
    EstadoResumido.CON_PREMIO: "estado--con-premio",
    EstadoResumido.CON_PREMIO_IMPORTE_PENDIENTE: "estado--con-premio",
    EstadoResumido.PENDIENTE_DETERMINACION: "estado--pendiente",
    EstadoResumido.RESULTADO_PENDIENTE: "estado--pendiente",
    EstadoResumido.SIN_PREMIO: "estado--sin-premio",
}


def _comparacion(jugada, cache: dict | None = None):
    """Compara la jugada con los datos publicados vigentes de su concurso (RN-32).

    ``cache`` evita recalcular ``DatosConcurso`` para cada jugada del mismo concurso (NFR-004).
    """
    if cache is not None and jugada.concurso_id in cache:
        datos = cache[jugada.concurso_id]
    else:
        datos = consultas.datos_concurso(jugada.concurso)
        if cache is not None:
            cache[jugada.concurso_id] = datos
    return comparar_jugada(jugada.numeros, datos)


def _resumen(resultados) -> dict:
    estado = resumir_jugada(resultados)
    return {"texto": estado.texto, "clase": CLASE_RESUMEN[estado]}


@sesion_requerida
def lista(request):
    jugadas = _prefetch_jugadas(
        Jugada.objects.filter(usuario=request.user).order_by(
            "-concurso__fecha_sorteo", "-creada_en"
        )
    )
    cache: dict = {}
    filas = [
        {
            "jugada": j,
            "modalidades": _modalidades(j.concurso),
            "estado": _resumen(_comparacion(j, cache)),
        }
        for j in jugadas
    ]
    return render(request, "jugadas/lista.html", {"filas": filas})


def _render_formulario(request, form, jugada=None, duplicado=False, error_concurso=None):
    return render(
        request,
        "jugadas/formulario.html",
        {
            "form": form,
            "jugada": jugada,
            "duplicado": duplicado,
            "error_concurso": error_concurso,
            "modalidades": form.modalidades_elegidas(),
        },
    )


def _guardar(request, form, jugada=None):
    """Devuelve una respuesta si terminó (éxito o jugada fija) o ``None`` para re-renderizar."""
    datos = form.cleaned_data
    if jugada is None:
        resultado = servicios.registrar_jugada(
            request.user,
            datos["concurso"],
            datos["numeros_validos"],
            datos["costo"],
            datos["confirmar_duplicado"],
        )
    else:
        resultado = servicios.editar_jugada(
            jugada,
            datos["concurso"],
            datos["numeros_validos"],
            datos["costo"],
            datos["confirmar_duplicado"],
        )
    if isinstance(resultado, servicios.ErrorJugada):
        if resultado.codigo == "REQUIERE_CONFIRMACION":
            return "duplicado"
        if resultado.codigo == "FIJA":
            messages.error(request, resultado.mensaje)
            return redirect(f"/mis-jugadas/{jugada.pk}/")
        form.add_error("concurso", resultado.mensaje)
        return None
    if jugada is None:
        messages.success(request, "Jugada registrada")
        return redirect("/mis-jugadas/")
    messages.success(request, "Jugada actualizada")
    return redirect("/mis-jugadas/")


@sesion_requerida
@require_http_methods(["GET", "POST"])
def nueva(request):
    error_concurso = None
    inicial = {}
    if request.method == "GET" and request.GET.get("concurso"):
        resultado = servicios.resolver_concurso(request.GET["concurso"])
        if isinstance(resultado, servicios.ErrorJugada):
            error_concurso = resultado.mensaje
        else:
            inicial["concurso"] = str(resultado.numero)
    form = JugadaForm(request.POST or None, initial=inicial)
    if request.method == "POST" and form.is_valid():
        respuesta = _guardar(request, form)
        if respuesta == "duplicado":
            return _render_formulario(request, form, duplicado=True)
        if respuesta is not None:
            return respuesta
    return _render_formulario(request, form, error_concurso=error_concurso)


@sesion_requerida
def detalle(request, id: int):
    jugada, error = _jugada_propia(request, id)
    if error:
        return error
    resultados = _comparacion(jugada)
    actualizaciones = cambio_por_correccion(
        jugada.numeros, consultas.historial_versiones(jugada.concurso)
    )
    return render(
        request,
        "jugadas/detalle.html",
        {
            "jugada": jugada,
            "modalidades": _modalidades(jugada.concurso),
            "modificable": servicios.es_modificable(jugada),
            "fija": servicios.FIJA,
            "comparacion": [
                {"r": r, "actualizado": actualizaciones.get(r.modalidad)} for r in resultados
            ],
            "resumen": _resumen(resultados),
        },
    )


@sesion_requerida
@require_http_methods(["GET", "POST"])
def editar(request, id: int):
    jugada, error = _jugada_propia(request, id)
    if error:
        return error
    if not servicios.es_modificable(jugada):
        messages.error(request, servicios.FIJA)
        return redirect(f"/mis-jugadas/{jugada.pk}/")
    inicial = {
        "concurso": str(jugada.concurso.numero),
        "numeros": [f"{n:02d}" for n in jugada.numeros_ordenados],
        "costo": f"{jugada.costo:.2f}".replace(".", ","),
    }
    form = JugadaForm(request.POST or None, initial=inicial, concurso_actual=jugada.concurso)
    if request.method == "POST" and form.is_valid():
        respuesta = _guardar(request, form, jugada)
        if respuesta == "duplicado":
            return _render_formulario(request, form, jugada=jugada, duplicado=True)
        if respuesta is not None:
            return respuesta
    return _render_formulario(request, form, jugada=jugada)


@sesion_requerida
@require_http_methods(["GET", "POST"])
def eliminar(request, id: int):
    jugada, error = _jugada_propia(request, id)
    if error:
        return error
    if not servicios.es_modificable(jugada):
        messages.error(request, servicios.FIJA)
        return redirect(f"/mis-jugadas/{jugada.pk}/")
    if request.method == "POST":
        resultado = servicios.eliminar_jugada(jugada)
        if resultado is not None:
            messages.error(request, resultado.mensaje)
            return redirect(f"/mis-jugadas/{jugada.pk}/")
        messages.success(request, "Jugada eliminada")
        return redirect("/mis-jugadas/")
    return render(request, "jugadas/eliminar.html", {"jugada": jugada})
