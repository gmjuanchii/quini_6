"""Mis jugadas en la API v1 ([003] contracts/api.md § Mis jugadas, pantalla 3, T189).

Las mismas reglas que ``jugadas/views.py``: siempre filtrado por ``usuario=request.user`` (una
jugada ajena o inexistente responde ``404`` idéntico, Const. IV), la misma validación
(``JugadaForm``), los mismos servicios y los mismos avisos en la sesión (FR-043).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from django.contrib import messages
from django.http import HttpResponse, QueryDict
from ninja import Router, Schema, Status

from dominio.comparacion import (
    Elegibilidad,
    cambio_por_correccion,
    comparar_jugada,
    resumir_jugada,
)
from dominio.mensajes import MENSAJES
from jugadas import servicios
from jugadas.forms import JugadaForm
from jugadas.models import Jugada
from jugadas.views import CLASE_RESUMEN, _modalidades, _prefetch_jugadas
from quini6 import idempotencia
from quini6.api_base import FechaHora, ProblemaAPI, nivel
from resultados import consultas

router = Router(tags=["Mis jugadas"])

_CLAVE_DE_TEXTO = {texto: clave for clave, texto in MENSAJES.items()}
#: Nombre del campo en la API ← nombre en ``JugadaForm``.
_CAMPOS = {"concurso": "sorteo", "numeros": "numeros", "costo": "costo", "__all__": ""}


class SorteoBreve(Schema):
    numero: int
    fecha: date


class EstadoJugada(Schema):
    texto: str
    clase: str


class JugadaResumen(Schema):
    id: int
    sorteo: SorteoBreve
    numeros: list[int]
    costo: str
    modalidades: list[str]
    estado: EstadoJugada
    modificable: bool


class ModalidadBreve(Schema):
    slug: str
    nombre: str


class CodigoComparacion(Schema):
    codigo: str
    texto: str | None


class ComparacionModalidad(Schema):
    modalidad: ModalidadBreve
    publicado: bool
    estado_validacion: CodigoComparacion
    aciertos: int | None
    numeros_acertados: list[int] | None
    numeros_oficiales: list[int] | None
    conjunto: list[int] | None
    elegibilidad: Literal["participa", "excluida"] | None
    excluida_por: str | None
    resultado_premio: CodigoComparacion | None
    categoria: str | None
    importe: str | None
    importe_pendiente: bool
    avisos: list[str]
    actualizado_el: date | None


class JugadaDTO(JugadaResumen):
    creada_en: FechaHora
    modificada_en: FechaHora | None
    comparacion: list[ComparacionModalidad]
    resumen: EstadoJugada


class SorteoDisponible(Schema):
    numero: int
    fecha: date
    modalidades: list[ModalidadBreve]


class GuardarJugada(Schema):
    sorteo: str = ""
    numeros: list[str] = []
    costo: str = ""
    confirmar_duplicado: bool = False


# -- Conversión ---------------------------------------------------------------------------------


def _ordenados(valores) -> list[int] | None:
    return sorted(valores) if valores is not None else None


def _resumen(resultados) -> dict:
    estado = resumir_jugada(resultados)
    return {"texto": estado.texto, "clase": CLASE_RESUMEN[estado]}


def _comparacion(jugada: Jugada, cache: dict | None = None):
    if cache is not None and jugada.concurso_id in cache:
        datos = cache[jugada.concurso_id]
    else:
        datos = consultas.datos_concurso(jugada.concurso)
        if cache is not None:
            cache[jugada.concurso_id] = datos
    return comparar_jugada(jugada.numeros, datos)


def resumen_dto(jugada: Jugada, cache: dict | None = None) -> dict:
    return {
        "id": jugada.pk,
        "sorteo": {"numero": jugada.concurso.numero, "fecha": jugada.concurso.fecha_sorteo},
        "numeros": jugada.numeros_ordenados,
        "costo": f"{jugada.costo:.2f}",
        "modalidades": _modalidades(jugada.concurso),
        "estado": _resumen(_comparacion(jugada, cache)),
        "modificable": servicios.es_modificable(jugada),
    }


def _comparacion_dto(r, actualizado) -> dict:
    return {
        "modalidad": {"slug": r.modalidad.slug, "nombre": r.modalidad.nombre},
        "publicado": r.publicado,
        "estado_validacion": {
            "codigo": r.estado_validacion.name,
            "texto": r.estado_validacion.texto,
        },
        "aciertos": r.aciertos,
        "numeros_acertados": _ordenados(r.numeros_acertados),
        "numeros_oficiales": _ordenados(r.numeros_oficiales),
        "conjunto": _ordenados(r.conjunto),
        "elegibilidad": (
            None
            if r.elegibilidad is None
            else ("excluida" if r.elegibilidad is Elegibilidad.EXCLUIDA else "participa")
        ),
        "excluida_por": r.excluida_por.nombre if r.excluida_por else None,
        "resultado_premio": (
            {"codigo": r.resultado_premio.name, "texto": r.texto_resultado}
            if r.resultado_premio
            else None
        ),
        "categoria": r.categoria,
        "importe": f"{r.importe:.2f}" if isinstance(r.importe, Decimal) else None,
        "importe_pendiente": r.importe_pendiente,
        "avisos": r.textos_avisos,
        "actualizado_el": actualizado,
    }


def jugada_dto(jugada: Jugada) -> dict:
    resultados = _comparacion(jugada)
    actualizaciones = cambio_por_correccion(
        jugada.numeros, consultas.historial_versiones(jugada.concurso)
    )
    return {
        **resumen_dto(jugada),
        "creada_en": jugada.creada_en,
        "modificada_en": jugada.modificada_en if jugada.modificada_en != jugada.creada_en else None,
        "comparacion": [_comparacion_dto(r, actualizaciones.get(r.modalidad)) for r in resultados],
        "resumen": _resumen(resultados),
    }


# -- Operaciones --------------------------------------------------------------------------------


def _propia(request, id_: int) -> Jugada:
    """Const. IV: solo las jugadas de la persona; ajena o inexistente → el mismo 404."""
    jugada = _prefetch_jugadas(Jugada.objects.filter(pk=id_, usuario=request.user)).first()
    if jugada is None:
        raise ProblemaAPI(404, "jugada.no_existe", tipo="no-encontrado")
    return jugada


def _form(datos: GuardarJugada, concurso_actual=None) -> JugadaForm:
    entrada = QueryDict(mutable=True)
    entrada["concurso"] = datos.sorteo
    entrada.setlist("numeros", list(datos.numeros))
    entrada["costo"] = datos.costo
    entrada["confirmar_duplicado"] = "1" if datos.confirmar_duplicado else ""
    return JugadaForm(entrada, concurso_actual=concurso_actual)


def _invalido(form: JugadaForm) -> ProblemaAPI:
    errores = [
        {
            "campo": _CAMPOS.get(campo, campo),
            "codigo": _CLAVE_DE_TEXTO.get(str(texto), "api.dato_invalido"),
            "mensaje": str(texto),
        }
        for campo, lista in form.errors.items()
        for texto in lista
    ]
    return ProblemaAPI(422, "api.detalle_validacion", tipo="validacion", errores=errores)


def _guardar(request, form: JugadaForm, jugada: Jugada | None = None):
    datos = form.cleaned_data
    argumentos = (datos["concurso"], datos["numeros_validos"], datos["costo"])
    if jugada is None:
        resultado = servicios.registrar_jugada(
            request.user, *argumentos, datos["confirmar_duplicado"]
        )
    else:
        resultado = servicios.editar_jugada(jugada, *argumentos, datos["confirmar_duplicado"])
    if isinstance(resultado, servicios.ErrorJugada):
        if resultado.codigo == "REQUIERE_CONFIRMACION":
            raise ProblemaAPI(409, "jugada.duplicada", tipo="conflicto", confirmar=True)
        if resultado.codigo == "FIJA":
            raise ProblemaAPI(409, "jugada.fija", tipo="conflicto")
        texto = resultado.mensaje
        raise ProblemaAPI(
            422,
            "api.detalle_validacion",
            tipo="validacion",
            errores=[
                {
                    "campo": "sorteo",
                    "codigo": _CLAVE_DE_TEXTO.get(texto, "api.dato_invalido"),
                    "mensaje": texto,
                }
            ],
        )
    return resultado


@router.get("/jugadas/", response=list[JugadaResumen])
@nivel("U")
def listar(request):
    """[001] AC-4.x, AC-5.x: de la más reciente a la más antigua, con su estado resumido."""
    jugadas = _prefetch_jugadas(
        Jugada.objects.filter(usuario=request.user).order_by(
            "-concurso__fecha_sorteo", "-creada_en"
        )
    )
    cache: dict = {}
    return [resumen_dto(j, cache) for j in jugadas]


@router.get("/jugadas/sorteos-disponibles/", response=list[SorteoDisponible])
@nivel("U")
def sorteos_disponibles(request):
    """[001] AC-4.7, AC-4.8, RN-07."""
    from jugadas.forms import _ordenadas

    return [
        {
            "numero": c.numero,
            "fecha": c.fecha_sorteo,
            "modalidades": [
                {"slug": mc.modalidad_enum.slug, "nombre": mc.modalidad_enum.nombre}
                for mc in _ordenadas(c)
            ],
        }
        for c in servicios.concursos_disponibles()
    ]


@router.post("/jugadas/", response={201: JugadaDTO})
@nivel("U", ruta_pendiente="/mis-jugadas/nueva/")
def registrar(request, datos: GuardarJugada):
    """[001] AC-4.1 a AC-4.9, RN-06, RN-07. ⟳ ``Idempotency-Key``."""
    clave, anterior = idempotencia.anterior_api(request, "jugada.registrar")
    if anterior is not None:
        return Status(201, jugada_dto(_propia(request, int(anterior["resultado"]))))
    form = _form(datos)
    if not form.is_valid():
        raise _invalido(form)
    jugada = _guardar(request, form)
    messages.success(request, MENSAJES["jugada.registrada"])
    if clave is not None:
        idempotencia.registrar(request, clave, "jugada.registrar", str(jugada.pk))
    return Status(201, jugada_dto(_propia(request, jugada.pk)))


@router.get("/jugadas/{id}/", response=JugadaDTO)
@nivel("U")
def detalle(request, id: int):
    """[001] AC-5.x: comparación por sorteo y modalidad, calculada en cada consulta."""
    return jugada_dto(_propia(request, id))


@router.put("/jugadas/{id}/", response=JugadaDTO)
@nivel("U", ruta_pendiente="/mis-jugadas/{id}/editar/")
def modificar(request, id: int, datos: GuardarJugada):
    """[001] AC-4.10, RN-08. ⟳ ``Idempotency-Key``."""
    clave, anterior = idempotencia.anterior_api(request, "jugada.editar")
    jugada = _propia(request, id)
    if anterior is not None:
        return jugada_dto(jugada)
    if not servicios.es_modificable(jugada):
        raise ProblemaAPI(409, "jugada.fija", tipo="conflicto")
    form = _form(datos, concurso_actual=jugada.concurso)
    if not form.is_valid():
        raise _invalido(form)
    _guardar(request, form, jugada)
    messages.success(request, MENSAJES["jugada.actualizada"])
    if clave is not None:
        idempotencia.registrar(request, clave, "jugada.editar", str(jugada.pk))
    return jugada_dto(_propia(request, id))


@router.delete("/jugadas/{id}/")
@nivel("U")
def eliminar(request, id: int):
    """[001] AC-4.11, RN-08. ⟳ ``Idempotency-Key`` (repetir → 204 sin efecto)."""
    clave, anterior = idempotencia.anterior_api(request, "jugada.eliminar")
    if anterior is not None:
        return HttpResponse(status=204)
    jugada = _propia(request, id)
    if not servicios.es_modificable(jugada):
        raise ProblemaAPI(409, "jugada.fija", tipo="conflicto")
    resultado = servicios.eliminar_jugada(jugada)
    if resultado is not None:
        raise ProblemaAPI(409, "jugada.fija", tipo="conflicto")
    messages.success(request, MENSAJES["jugada.eliminada"])
    if clave is not None:
        idempotencia.registrar(request, clave, "jugada.eliminar", str(id))
    return HttpResponse(status=204)
