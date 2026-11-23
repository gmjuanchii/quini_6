"""Resultados en la API v1 ([003] contracts/api.md § Resultados, pantalla 4, T195).

Lectura pública con las mismas consultas que ``resultados/views_publicas.py``
(``consultas.vista_publica_concurso``): solo lo publicado (vigente o en revisión); nada en borrador
u observado se expone (Const. VIII). Respuestas con ``Cache-Control: no-cache`` (los resultados
pueden corregirse).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from ninja import Router, Schema

from dominio.comparacion import EstadoValidacion
from dominio.extraccion.periodo import parsear_fecha
from dominio.mensajes import mensaje
from dominio.periodos import error_de_fecha
from dominio.tipos import EstadoBloque
from quini6.api_base import ProblemaAPI, error_de_campo, nivel
from resultados import consultas
from resultados.models import Concurso

router = Router(tags=["Resultados"])

#: RN-20: el estado público (nunca "Borrador" ni "Observado": ambos son "Pendiente de validación").
_ESTADO_PUBLICO = {
    EstadoBloque.SIN_CARGAR: EstadoValidacion.RESULTADO_PENDIENTE,
    EstadoBloque.BORRADOR: EstadoValidacion.PENDIENTE_VALIDACION,
    EstadoBloque.OBSERVADO: EstadoValidacion.PENDIENTE_VALIDACION,
    EstadoBloque.EN_REVISION: EstadoValidacion.EN_REVISION,
    EstadoBloque.PUBLICADO: EstadoValidacion.PUBLICADO,
}


class EstadoPublico(Schema):
    codigo: str
    texto: str


class SorteoResumen(Schema):
    numero: int
    fecha: date
    completitud: EstadoPublico


class FuentePublica(Schema):
    descripcion: str
    fecha_consulta: date | None


class CategoriaPublica(Schema):
    codigo: str
    nombre: str
    condicion: str
    ganadores: int | None
    importe_categoria: str | None
    importe_individual: str | None
    pozo_vacante_acumulado: str | None


class ModalidadPublica(Schema):
    slug: str
    nombre: str
    es_premio_extra: bool
    estado_numeros: EstadoPublico
    numeros: list[int] | None
    conjunto: list[int] | None
    fuente_numeros: FuentePublica | None
    revision_numeros: bool
    corregido_numeros: date | None
    estado_premios: EstadoPublico
    categorias: list[CategoriaPublica]
    sin_ganadores: bool
    fuente_premios: FuentePublica | None
    revision_premios: bool
    corregido_premios: date | None


class SorteoPublico(SorteoResumen):
    admite_jugadas: bool
    modalidades: list[ModalidadPublica]


class Ultimos(Schema):
    ultimo: SorteoPublico | None
    pendiente: SorteoResumen | None


class PaginaSorteos(Schema):
    elementos: list[SorteoResumen]
    pagina: int
    paginas: int
    total: int
    mensaje: str | None = None
    redirigir: str | None = None


def _importe(valor) -> str | None:
    return f"{valor:.2f}" if isinstance(valor, Decimal) else None


def _estado(estado: EstadoBloque) -> dict:
    publico = _ESTADO_PUBLICO[estado]
    return {"codigo": publico.name, "texto": consultas.texto_estado_publico(estado)}


def _fuente(fuente) -> dict | None:
    if fuente is None:
        return None
    descripcion, fecha = fuente
    return {"descripcion": descripcion, "fecha_consulta": fecha}


def resumen_dto(concurso: Concurso) -> dict:
    codigo = consultas.completitud(concurso)
    return {
        "numero": concurso.numero,
        "fecha": concurso.fecha_sorteo,
        "completitud": {"codigo": codigo, "texto": consultas.TEXTO_COMPLETITUD[codigo]},
    }


def publico_dto(concurso: Concurso) -> dict:
    vista = consultas.vista_publica_concurso(concurso)
    return {
        **resumen_dto(concurso),
        "admite_jugadas": consultas.admite_jugadas(concurso),
        "modalidades": [
            {
                "slug": m.modalidad.slug,
                "nombre": m.nombre,
                "es_premio_extra": m.es_premio_extra,
                "estado_numeros": _estado(m.estado_numeros),
                "numeros": m.numeros if m.numeros_publicados else None,
                "conjunto": m.conjunto if m.numeros_publicados else None,
                "fuente_numeros": _fuente(m.fuente_numeros),
                "revision_numeros": m.revision_numeros,
                "corregido_numeros": m.corregido_numeros,
                "estado_premios": _estado(m.estado_premios),
                "categorias": [
                    {
                        "codigo": c.codigo,
                        "nombre": c.nombre,
                        "condicion": c.condicion,
                        "ganadores": c.ganadores,
                        "importe_categoria": _importe(c.importe_categoria),
                        "importe_individual": _importe(c.importe_individual),
                        "pozo_vacante_acumulado": _importe(c.pozo_vacante_acumulado),
                    }
                    for c in (m.categorias if m.premios_publicados else [])
                ],
                "sin_ganadores": m.sin_ganadores if m.premios_publicados else False,
                "fuente_premios": _fuente(m.fuente_premios),
                "revision_premios": m.revision_premios,
                "corregido_premios": m.corregido_premios,
            }
            for m in vista.modalidades
        ],
    }


def _pagina(concursos, **extra) -> dict:
    elementos = [resumen_dto(c) for c in concursos]
    return {"elementos": elementos, "pagina": 1, "paginas": 1, "total": len(elementos), **extra}


@router.get("/sorteos/ultimo/", response=Ultimos)
@nivel("P")
def ultimo(request):
    """[001] RN-25: últimos resultados publicados y, si hay, el sorteo actual pendiente."""
    ultimos, pendiente = consultas.ultimos_resultados()
    return {
        "ultimo": publico_dto(ultimos) if ultimos else None,
        "pendiente": resumen_dto(pendiente) if pendiente else None,
    }


@router.get("/sorteos/", response=PaginaSorteos)
@nivel("P")
def listar(request, pagina: str = "1"):
    """Todos los sorteos en una sola página, como el listado HTML (contracts/api.md)."""
    concursos = consultas.con_versiones(Concurso.objects.order_by("-fecha_sorteo", "-numero"))
    return _pagina(concursos)


@router.get("/sorteos/buscar/", response=PaginaSorteos)
@nivel("P")
def buscar(request, numero: str = "", fecha: str = ""):
    """[001] AC-1.x: por número (si existe, ``redirigir``) o por fecha."""
    numero, fecha = numero.strip(), fecha.strip()
    if numero:
        if not numero.isdigit():
            raise ProblemaAPI(
                422,
                "api.detalle_validacion",
                tipo="validacion",
                errores=[error_de_campo("numero", "admin.numero_sorteo_invalido")],
            )
        if Concurso.objects.filter(numero=int(numero)).exists():
            return _pagina([], redirigir=f"/resultados/{int(numero)}/")
        return _pagina([], mensaje=mensaje("resultados.concurso_inexistente", N=int(numero)))
    if fecha:
        try:
            dia = datetime.strptime(fecha, "%d/%m/%Y").date()
        except ValueError:
            dia = parsear_fecha(fecha) if "-" in fecha else None
        if dia is None:
            clave, valores = error_de_fecha(fecha) or ("gral.fecha_invalida", {})
            raise ProblemaAPI(
                422,
                "gral.fecha_invalida",
                tipo="validacion",
                errores=[error_de_campo("fecha", clave, **valores)],
            )
        concursos = list(
            consultas.con_versiones(Concurso.objects.filter(fecha_sorteo=dia).order_by("-numero"))
        )
        if not concursos:
            texto = mensaje("resultados.fecha_sin_concursos", fecha=dia.strftime("%d/%m/%Y"))
            return _pagina([], mensaje=texto)
        return _pagina(concursos)
    return _pagina([], redirigir="/resultados/")


@router.get("/sorteos/{numero}/", response=SorteoPublico)
@nivel("P")
def detalle(request, numero: int):
    concurso = consultas.cargar_concurso(numero)
    if concurso is None:
        raise ProblemaAPI(404, "gral.pagina_inexistente", tipo="no-encontrado")
    return publico_dto(concurso)
