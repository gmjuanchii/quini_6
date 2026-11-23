"""Extracción histórica en la API v1 ([003] contracts/api.md § "Extracción histórica", T174).

Operaciones delgadas (consultas → dominio → servicios), con los mismos datos, permisos y mensajes
que las vistas HTML de ``extracciones/views.py`` (NFR-009). Todas son de nivel A.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from django.contrib import messages
from django.http import HttpResponse
from ninja import Router, Schema, Status

from dominio.extraccion.etiqueta import EtiquetaEstado, desde_slug
from dominio.extraccion.tipos import EstadoDato, Valor
from dominio.mensajes import mensaje
from dominio.tipos import ORDEN_MODALIDADES
from extracciones import consultas, servicios
from extracciones.forms import PeriodoForm
from extracciones.models import Extraccion as ModeloExtraccion
from extracciones.serializacion import sorteo_de_json
from quini6 import idempotencia, tablas
from quini6.api_base import FechaHora, ProblemaAPI, error_de_campo, nivel
from quini6.templatetags.formato_ar import fecha_ar, fecha_hora_ar

router = Router(tags=["Extracción histórica"])

_INICIO = "/administracion/extracciones/"


# -- DTO (contracts/api.md § "DTO de la pantalla 1") --------------------------------------


class Etiqueta(Schema):
    valor: Literal["en_curso", "finalizada", "con_advertencias", "sin_sorteos", "con_error"]
    slug: str
    texto: str
    explicacion: str
    variante: Literal["info", "success", "warning", "neutral", "danger"]
    requiere_revision: bool


class AvisoFinal(Schema):
    tipo: Literal["success", "warning", "error", "info"]
    texto: str
    enlace: str


class AvanceDatos(Schema):
    en_curso: bool
    identificando: bool
    procesados: int
    total: int | None
    etiqueta: Etiqueta
    aviso_final: AvisoFinal | None


class ExtraccionResumen(Schema):
    id: int
    iniciada_en: FechaHora
    desde: date
    hasta: date
    creada_por: str
    etiqueta: Etiqueta
    en_curso: bool
    avance: AvanceDatos
    eliminable: bool
    descargable: bool
    url_csv: str | None
    nombre_acciones: str


class PaginaExtracciones(Schema):
    elementos: list[ExtraccionResumen]
    pagina: int
    paginas: int
    total: int
    orden: str
    filtro: str | None
    tiene_anterior: bool
    tiene_siguiente: bool
    en_curso_propia: ExtraccionResumen | None


class IniciarExtraccion(Schema):
    inicio: str = ""
    fin: str = ""


class Fallido(Schema):
    texto: str
    cantidad: int


class FuenteResumen(Schema):
    fuente: str
    nombre: str
    aportados: int
    fallidos: list[Fallido]
    requiere_mantenimiento: bool


class SorteoARevisar(Schema):
    numero: int
    fecha: date | None
    estado: str
    estado_texto: str
    motivos: list[str]


class ResumenExtraccion(Schema):
    identificados: int
    recuperados: int
    parciales: int
    inconsistencias: int
    no_recuperados: int
    fuentes: list[FuenteResumen]
    huecos: list[int]
    cobertura_desde: date | None
    a_revisar: list[SorteoARevisar]


class SorteoDeLaExtraccion(Schema):
    numero: int
    fecha: date | None
    estado: str
    estado_texto: str


class Extraccion(ExtraccionResumen):
    finalizada_en: FechaHora | None
    estado_texto: str
    ninguna_fuente: bool
    resumen: ResumenExtraccion | None
    sorteos: list[SorteoDeLaExtraccion]


TipoDato = Literal["entero", "importe", "fecha", "numeros", "texto"]


class Dato(Schema):
    """[002] ``Dato`` con estado explícito: un dato desconocido nunca es ``null``→0."""

    estado: Literal["valor", "no_disponible", "no_corresponde", "sin_determinar"]
    tipo: TipoDato | None
    valor: int | str | list[int] | None
    texto: str | None


class ValorDeFuente(Schema):
    fuente: str
    valor: Dato


class Diferencia(Schema):
    tipo: str
    valores: list[ValorDeFuente]


class DatoConsolidado(Dato):
    fuentes: list[str]
    sin_corroborar: bool
    discrepancia: Diferencia | None
    diferencia_tolerada: Diferencia | None
    calculo: str | None


class DatoConRotulo(DatoConsolidado):
    rotulo: str


class Categoria(Schema):
    nombre: str
    estado_pozo: str
    datos: list[DatoConRotulo]


class ModalidadExtraida(Schema):
    nombre: str
    informada: bool
    propia: bool
    numeros: DatoConsolidado
    categorias: list[Categoria]


class IntentoFuente(Schema):
    nombre: str
    resultado: str
    url: str
    consultado_en: FechaHora | None
    observaciones: list[str]


class Observacion(Schema):
    fuente: str | None
    texto: str


class SorteoExtraido(Schema):
    numero: int
    fecha: DatoConsolidado
    estado: str
    estado_texto: str
    motivos: list[str]
    combina_fuentes: bool
    sin_corroborar: bool
    reglas_no_verificadas: bool
    fuentes: list[IntentoFuente]
    modalidades: list[ModalidadExtraida]
    observaciones: list[Observacion]


# -- Conversión ---------------------------------------------------------------------------------


def etiqueta_dto(etiqueta: EtiquetaEstado) -> dict:
    return {
        "valor": etiqueta.value,
        "slug": etiqueta.slug,
        "texto": mensaje(etiqueta.clave_texto),
        "explicacion": mensaje(etiqueta.clave_explicacion),
        "variante": etiqueta.variante,
        "requiere_revision": etiqueta.requiere_revision,
    }


def _avance_dto(avance: dict) -> dict:
    return {**avance, "etiqueta": etiqueta_dto(avance["etiqueta"])}


def _url_csv(extraccion: ModeloExtraccion) -> str | None:
    if not consultas.puede_descargar(extraccion):
        return None
    return f"{_INICIO}{extraccion.pk}/csv/"


def resumen_dto(extraccion: ModeloExtraccion) -> dict:
    avance = consultas.avance(extraccion)
    return {
        "id": extraccion.pk,
        "iniciada_en": extraccion.iniciada_en,
        "desde": extraccion.desde,
        "hasta": extraccion.hasta,
        "creada_por": extraccion.creada_por.email,
        "etiqueta": etiqueta_dto(avance["etiqueta"]),
        "en_curso": extraccion.en_curso,
        "avance": _avance_dto(avance),
        "eliminable": not extraccion.en_curso,
        "descargable": consultas.puede_descargar(extraccion),
        "url_csv": _url_csv(extraccion),
        "nombre_acciones": mensaje(
            "ext.acciones", fecha_hora=fecha_hora_ar(extraccion.iniciada_en)
        ),
    }


def _resumen_extraccion(resumen: dict | None, original: dict | None) -> dict | None:
    if resumen is None:
        return None
    return {
        **{k: resumen[k] for k in ("identificados", "recuperados", "parciales")},
        "inconsistencias": resumen["inconsistencias"],
        "no_recuperados": resumen["no_recuperados"],
        "fuentes": [
            {
                "fuente": f.get("fuente", ""),
                "nombre": f.get("nombre", ""),
                "aportados": f.get("aportados", 0),
                "fallidos": f["fallidos"],
                "requiere_mantenimiento": bool(f.get("requiere_mantenimiento")),
            }
            for f in resumen["fuentes"]
        ],
        "huecos": resumen["huecos"],
        "cobertura_desde": (original or {}).get("cobertura_desde"),
        "a_revisar": [
            {
                "numero": s["numero"],
                "fecha": s["fecha"],
                "estado": s["estado"],
                "estado_texto": s["estado_texto"],
                "motivos": list(s.get("motivos", [])),
            }
            for s in resumen["a_revisar"]
        ],
    }


def _valor_dto(v) -> dict:
    """``Dato`` con valor: la API usa formatos de máquina (importe como cadena decimal)."""
    if isinstance(v, bool):
        return {"estado": "valor", "tipo": "texto", "valor": "Sí" if v else "No", "texto": None}
    if isinstance(v, int):
        return {"estado": "valor", "tipo": "entero", "valor": v, "texto": None}
    if isinstance(v, Decimal):
        return {"estado": "valor", "tipo": "importe", "valor": f"{v:.2f}", "texto": None}
    if isinstance(v, date):
        return {"estado": "valor", "tipo": "fecha", "valor": v.isoformat(), "texto": None}
    if isinstance(v, frozenset | set):
        return {"estado": "valor", "tipo": "numeros", "valor": sorted(v), "texto": None}
    return {"estado": "valor", "tipo": "texto", "valor": str(v), "texto": None}


_ESTADO_DATO = {
    EstadoDato.NO_DISPONIBLE: "no_disponible",
    EstadoDato.NO_CORRESPONDE: "no_corresponde",
    EstadoDato.SIN_DETERMINAR: "sin_determinar",
}


def _estado_dto(estado: EstadoDato) -> dict:
    return {"estado": _ESTADO_DATO[estado], "tipo": None, "valor": None, "texto": estado.texto}


def dato_dto(dato) -> dict:
    if isinstance(dato, Valor):
        return _valor_dto(dato.v)
    if isinstance(dato, EstadoDato):
        return _estado_dto(dato)
    return _estado_dto(EstadoDato.NO_DISPONIBLE)


def _diferencia_dto(diferencia) -> dict | None:
    if diferencia is None:
        return None
    return {
        "tipo": diferencia.tipo.texto,
        "valores": [
            {
                "fuente": fuente.nombre,
                "valor": _estado_dto(EstadoDato.NO_DISPONIBLE) if v is None else _valor_dto(v),
            }
            for fuente, v in diferencia.valores
        ],
    }


def consolidado_dto(d) -> dict:
    return {
        **dato_dto(d.dato),
        "fuentes": [f.nombre for f in d.fuentes],
        "sin_corroborar": d.sin_corroborar,
        "discrepancia": _diferencia_dto(d.discrepancia),
        "diferencia_tolerada": _diferencia_dto(d.diferencia_tolerada),
        "calculo": d.calculo if isinstance(d.dato, Valor) else None,
    }


# -- Operaciones --------------------------------------------------------------------------------


def _obtener(id_extraccion: int) -> ModeloExtraccion:
    consulta = ModeloExtraccion.objects.select_related("creada_por")
    extraccion = consulta.filter(pk=id_extraccion).first()
    if extraccion is None:
        raise ProblemaAPI(404, "ext.no_existe", tipo="no-encontrado")
    return extraccion


@router.get("/extracciones/", response=PaginaExtracciones)
@nivel("A")
def listar(request, estado: str = "", orden: str = "", pagina: str = "1"):
    """[003] AC-1.4, AC-9.1, AC-9.2, RN-07: filtro, orden y página como en la vista HTML."""
    filtro = desde_slug(estado)
    orden = tablas.orden_valido(orden, consultas.COLUMNAS_ORDEN, consultas.ORDEN_PREDETERMINADO)
    resultado = consultas.listado_extracciones(filtro, orden, pagina)
    propia = servicios.extraccion_en_curso(request.user)
    return {
        "elementos": [resumen_dto(e) for e in resultado.elementos],
        "pagina": resultado.pagina,
        "paginas": resultado.paginas,
        "total": resultado.total,
        "orden": resultado.orden,
        "filtro": filtro.slug if filtro else None,
        "tiene_anterior": resultado.tiene_anterior,
        "tiene_siguiente": resultado.tiene_siguiente,
        "en_curso_propia": resumen_dto(propia) if propia else None,
    }


def _conflicto(clave: str, existente: ModeloExtraccion, **valores) -> ProblemaAPI:
    return ProblemaAPI(
        409,
        clave,
        tipo="conflicto",
        valores=valores,
        existente={"id": existente.pk, "url": f"{_INICIO}{existente.pk}/"},
    )


@router.post("/extracciones/", response={201: ExtraccionResumen})
@nivel("A", ruta_pendiente=_INICIO)
def iniciar(request, datos: IniciarExtraccion):
    """[002] AC-1.1 a AC-1.6, AC-1.11; [003] RN-03, AC-3.5. ⟳ ``Idempotency-Key``."""
    clave, anterior = idempotencia.anterior_api(request, "extraccion.iniciar")
    if anterior is not None:
        extraccion = ModeloExtraccion.objects.filter(pk=int(anterior["resultado"])).first()
        if extraccion is not None:
            return Status(201, resumen_dto(extraccion))
    propia = servicios.extraccion_en_curso(request.user)
    if propia is not None:
        raise _conflicto("ext.en_curso", propia)
    form = PeriodoForm({"inicio": datos.inicio, "fin": datos.fin})
    if not form.is_valid():
        raise ProblemaAPI(
            422,
            "api.detalle_validacion",
            tipo="validacion",
            errores=[error_de_campo(c, k, **v) for c, k, v in form.errores_catalogo],
        )
    resultado = servicios.iniciar_extraccion(request.user, form.periodo)
    if isinstance(resultado, servicios.ErrorInicio):
        existente = resultado.existente
        raise _conflicto(
            resultado.clave,
            existente,
            desde=fecha_ar(existente.desde),
            hasta=fecha_ar(existente.hasta),
        )
    if clave is not None:
        idempotencia.registrar(request, clave, "extraccion.iniciar", str(resultado.pk))
    return Status(201, resumen_dto(resultado))


@router.get("/extracciones/{id}/", response=Extraccion)
@nivel("A")
def detalle(request, id: int):
    """[002] AC-1.7 a AC-1.10; [003] AC-1.2, AC-3.4."""
    extraccion = _obtener(id)
    datos = consultas.datos_pagina(extraccion)
    return {
        **resumen_dto(extraccion),
        "finalizada_en": extraccion.finalizada_en,
        "estado_texto": datos["estado_texto"],
        "ninguna_fuente": datos["ninguna_fuente"],
        "resumen": _resumen_extraccion(datos["resumen"], extraccion.resumen),
        "sorteos": [
            {
                "numero": s.numero,
                "fecha": s.fecha,
                "estado": s.estado,
                "estado_texto": s.estado_enum.texto,
            }
            for s in extraccion.sorteos.order_by("numero")
        ],
    }


@router.get("/extracciones/{id}/avance/", response=AvanceDatos)
@nivel("A")
def avance(request, id: int):
    """[003] R-10: se consulta cada 3 s mientras ``en_curso``."""
    return _avance_dto(consultas.avance(_obtener(id)))


@router.get("/extracciones/{id}/sorteos/{numero}/", response=SorteoExtraido)
@nivel("A")
def sorteo(request, id: int, numero: int):
    """[002] AC-2.x: intentos por fuente y datos consolidados con su estado y su cálculo.

    Los textos y el orden salen de ``consultas.detalle_sorteo`` (los mismos de la vista HTML); los
    valores, del sorteo consolidado en formato de máquina (importes como cadena decimal).
    """
    extraccion = _obtener(id)
    datos = consultas.detalle_sorteo(extraccion, numero)
    consolidado = sorteo_de_json(extraccion.sorteos.get(numero=numero).consolidado)
    modalidades = [
        consolidado.modalidades[m] for m in ORDEN_MODALIDADES if m in consolidado.modalidades
    ]
    return {
        "numero": datos["numero"],
        "fecha": consolidado_dto(consolidado.fecha),
        "estado": consolidado.estado.value,
        "estado_texto": datos["estado_texto"],
        "motivos": datos["motivos"],
        "combina_fuentes": datos["combina_fuentes"],
        "sin_corroborar": datos["sin_corroborar"],
        "reglas_no_verificadas": datos["reglas_no_verificadas"],
        "fuentes": [
            {k: f[k] for k in ("nombre", "resultado", "url", "consultado_en", "observaciones")}
            for f in datos["fuentes"]
        ],
        "modalidades": [
            {
                "nombre": pantalla["nombre"],
                "informada": pantalla["informada"],
                "propia": pantalla["propia"],
                "numeros": consolidado_dto(mc.numeros),
                "categorias": [
                    {
                        "nombre": cat_pantalla["nombre"],
                        "estado_pozo": cat_pantalla["estado_pozo"],
                        "datos": [
                            {"rotulo": rotulo, **consolidado_dto(getattr(cat, campo))}
                            for campo, rotulo in consultas.CAMPOS_PREMIO
                        ],
                    }
                    for cat_pantalla, cat in zip(
                        pantalla["categorias"], mc.categorias.values(), strict=True
                    )
                ],
            }
            for pantalla, mc in zip(datos["modalidades"], modalidades, strict=True)
        ],
        "observaciones": datos["observaciones"],
    }


@router.delete("/extracciones/{id}/")
@nivel("A")
def eliminar(request, id: int):
    """[002] AC-1.18, AC-1.19; [003] AC-2.5. ⟳ ``Idempotency-Key`` (repetir → 204 sin efecto)."""
    clave, anterior = idempotencia.anterior_api(request, "extraccion.eliminar")
    if anterior is not None:
        return HttpResponse(status=204)
    extraccion = _obtener(id)
    if extraccion.en_curso:
        raise ProblemaAPI(409, "ext.eliminar_en_curso", tipo="conflicto")
    momento = fecha_hora_ar(extraccion.iniciada_en)
    error = servicios.eliminar_extraccion(extraccion)
    if error is not None:
        raise ProblemaAPI(409, "ext.eliminar_en_curso", tipo="conflicto")
    messages.success(request, mensaje("ext.eliminada", fecha_hora=momento))  # FR-043
    if clave is not None:
        idempotencia.registrar(request, clave, "extraccion.eliminar", str(id))
    return HttpResponse(status=204)
