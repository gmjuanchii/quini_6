"""Lectura de resultados para el público, el dominio y las comparaciones.

Estados derivados de data-model.md (RN-16, RN-19, RN-20, RN-25, RN-07). La información
no publicada (Borrador u Observado) nunca sale de este módulo con sus valores (RN-17, SC-003).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from django.db.models import Prefetch, Q
from django.utils import timezone

from dominio.numeros import conjunto_premio_extra
from dominio.tipos import (
    ACIERTOS_CATEGORIA,
    MODALIDADES_PREMIO_EXTRA,
    ORDEN_MODALIDADES,
    BloqueNumerosVista,
    BloquePremiosVista,
    CategoriaPublicada,
    DatosConcurso,
    EstadoBloque,
    Modalidad,
    nombre_categoria,
)
from resultados.models import (
    ESTADOS_EN_TRABAJO,
    Concurso,
    EstadoVersion,
    ModalidadConcurso,
    VersionNumeros,
    VersionPremios,
)

NUMEROS = "numeros"
PREMIOS = "premios"
BLOQUES = (NUMEROS, PREMIOS)

PREFETCH_CONCURSO = (
    "modalidades__versiones_numeros",
    Prefetch(
        "modalidades__versiones_premios",
        queryset=VersionPremios.objects.prefetch_related("categorias"),
    ),
)


def con_versiones(qs):
    """Precarga modalidades, versiones y categorías para no consultar por modalidad (NFR-004)."""
    return qs.prefetch_related(*PREFETCH_CONCURSO)


def cargar_concurso(numero: int) -> Concurso | None:
    return con_versiones(Concurso.objects.filter(numero=numero)).first()


def _versiones(mc: ModalidadConcurso, bloque: str) -> list:
    if bloque == NUMEROS:
        return list(mc.versiones_numeros.all())
    return list(mc.versiones_premios.all())


def _modalidades(concurso: Concurso) -> list[ModalidadConcurso]:
    orden = {m.value: i for i, m in enumerate(ORDEN_MODALIDADES)}
    return sorted(concurso.modalidades.all(), key=lambda mc: orden[mc.modalidad])


def _en_revision(mc: ModalidadConcurso, bloque: str) -> bool:
    return bool(getattr(mc, f"{bloque}_en_revision"))


def version_vigente(mc: ModalidadConcurso, bloque: str):
    """La versión ``PUBLICADA`` del bloque, o ``None``."""
    for version in _versiones(mc, bloque):
        if version.estado == EstadoVersion.PUBLICADA:
            return version
    return None


def version_en_trabajo(mc: ModalidadConcurso, bloque: str):
    """La versión en ``BORRADOR`` u ``OBSERVADO`` del bloque, o ``None``."""
    for version in _versiones(mc, bloque):
        if version.estado in ESTADOS_EN_TRABAJO:
            return version
    return None


def estado_bloque(mc: ModalidadConcurso, bloque: str) -> EstadoBloque:
    """Estado RN-16 visto por el administrador (data-model.md)."""
    if version_vigente(mc, bloque) is not None:
        return EstadoBloque.EN_REVISION if _en_revision(mc, bloque) else EstadoBloque.PUBLICADO
    trabajo = version_en_trabajo(mc, bloque)
    if trabajo is None:
        return EstadoBloque.SIN_CARGAR
    if trabajo.estado == EstadoVersion.OBSERVADO:
        return EstadoBloque.OBSERVADO
    return EstadoBloque.BORRADOR


def correccion_en_preparacion(mc: ModalidadConcurso, bloque: str) -> bool:
    return version_vigente(mc, bloque) is not None and version_en_trabajo(mc, bloque) is not None


def fecha_ultima_correccion(mc: ModalidadConcurso, bloque: str) -> date | None:
    """Fecha local de la última corrección que llegó a publicarse (RN-24, D-13 = A)."""
    fechas = [
        v.publicada_en
        for v in _versiones(mc, bloque)
        if v.es_correccion
        and v.publicada_en is not None
        and v.estado in (EstadoVersion.PUBLICADA, EstadoVersion.REEMPLAZADA)
    ]
    if not fechas:
        return None
    return timezone.localtime(max(fechas)).date()


def _elementos(concurso: Concurso) -> list[tuple[ModalidadConcurso, str]]:
    elementos = []
    for mc in _modalidades(concurso):
        if mc.modalidad_enum.tiene_extraccion_propia:
            elementos.append((mc, NUMEROS))
        elementos.append((mc, PREMIOS))
    return elementos


def completitud(concurso: Concurso) -> str:
    """RN-19: ``SIN_RESULTADOS``, ``INCOMPLETO`` o ``COMPLETO``."""
    elementos = _elementos(concurso)
    publicados = [version_vigente(mc, b) is not None for mc, b in elementos]
    if not elementos or not any(publicados):
        return "SIN_RESULTADOS"
    if all(publicados):
        return "COMPLETO"
    return "INCOMPLETO"


TEXTO_COMPLETITUD = {
    "SIN_RESULTADOS": "Resultados pendientes",
    "INCOMPLETO": "Incompleto",
    "COMPLETO": "Completo",
}


def tiene_publicaciones(concurso: Concurso) -> bool:
    return any(version_vigente(mc, b) is not None for mc, b in _elementos(concurso))


def admite_jugadas(concurso: Concurso) -> bool:
    """RN-07 y RN-08: ninguna ``VersionNumeros`` publicada o reemplazada."""
    cerradas = (EstadoVersion.PUBLICADA, EstadoVersion.REEMPLAZADA)
    for mc in concurso.modalidades.all():
        for version in mc.versiones_numeros.all():
            if version.estado in cerradas:
                return False
    return True


def _q_publicado() -> Q:
    return Q(modalidades__versiones_numeros__estado=EstadoVersion.PUBLICADA) | Q(
        modalidades__versiones_premios__estado=EstadoVersion.PUBLICADA
    )


def ultimos_resultados() -> tuple[Concurso | None, Concurso | None]:
    """RN-25: (concurso de "últimos resultados", concurso actual pendiente)."""
    orden = ("-fecha_sorteo", "-numero")
    ultimos = Concurso.objects.filter(_q_publicado()).distinct().order_by(*orden).first()
    mas_reciente = Concurso.objects.order_by(*orden).first()
    pendiente = None
    if mas_reciente is not None and (
        ultimos is None
        or (mas_reciente.fecha_sorteo, mas_reciente.numero) > (ultimos.fecha_sorteo, ultimos.numero)
    ):
        pendiente = mas_reciente
    if ultimos is not None:
        ultimos = cargar_concurso(ultimos.numero)
    if pendiente is not None:
        pendiente = cargar_concurso(pendiente.numero)
    return ultimos, pendiente


# --- Datos para el dominio -------------------------------------------------------------


def _vista_numeros(estado: EstadoBloque, version) -> BloqueNumerosVista:
    if estado.publicado and version is not None:
        return BloqueNumerosVista(estado, version.numeros)
    return BloqueNumerosVista(estado, None)


def _vista_premios(estado: EstadoBloque, version) -> BloquePremiosVista:
    if not (estado.publicado and version is not None):
        return BloquePremiosVista(estado)
    categorias = tuple(
        CategoriaPublicada(
            codigo=c.categoria,
            ganadores=c.ganadores,
            importe_categoria=c.importe_categoria,
            importe_individual=c.importe_individual,
            pozo_vacante_acumulado=c.pozo_vacante_acumulado,
        )
        for c in version.categorias.all()
    )
    return BloquePremiosVista(
        estado=estado,
        categorias=categorias,
        aciertos_categoria_ganadora=version.aciertos_categoria_ganadora,
        sin_ganadores=version.sin_ganadores,
    )


def datos_concurso(concurso: Concurso) -> DatosConcurso:
    """Solo valores publicados vigentes; ``numeros`` es ``None`` si no están publicados."""
    numeros: dict[Modalidad, BloqueNumerosVista] = {}
    premios: dict[Modalidad, BloquePremiosVista] = {}
    modalidades = set()
    for mc in _modalidades(concurso):
        modalidad = mc.modalidad_enum
        modalidades.add(modalidad)
        if modalidad.tiene_extraccion_propia:
            numeros[modalidad] = _vista_numeros(
                estado_bloque(mc, NUMEROS), version_vigente(mc, NUMEROS)
            )
        premios[modalidad] = _vista_premios(
            estado_bloque(mc, PREMIOS), version_vigente(mc, PREMIOS)
        )
    return DatosConcurso(
        fecha_sorteo=concurso.fecha_sorteo,
        modalidades=frozenset(modalidades),
        numeros=numeros,
        premios=premios,
    )


# --- Vista pública -----------------------------------------------------------------------


@dataclass
class CategoriaVista:
    codigo: str
    nombre: str
    condicion: str
    ganadores: int | None
    importe_categoria: object
    importe_individual: object
    pozo_vacante_acumulado: object


@dataclass
class ModalidadPublica:
    modalidad: Modalidad
    nombre: str
    estado_numeros: EstadoBloque
    numeros: list[int] | None = None
    fuente_numeros: tuple[str, date | None] | None = None
    revision_numeros: bool = False
    corregido_numeros: date | None = None
    conjunto: list[int] | None = None  # solo Premio Extra
    estado_premios: EstadoBloque = EstadoBloque.SIN_CARGAR
    categorias: list[CategoriaVista] = field(default_factory=list)
    aciertos_categoria_ganadora: int | None = None
    sin_ganadores: bool = False
    fuente_premios: tuple[str, date | None] | None = None
    revision_premios: bool = False
    corregido_premios: date | None = None

    @property
    def es_premio_extra(self) -> bool:
        return self.modalidad is Modalidad.PREMIO_EXTRA

    @property
    def numeros_publicados(self) -> bool:
        return self.estado_numeros.publicado

    @property
    def premios_publicados(self) -> bool:
        return self.estado_premios.publicado

    @property
    def texto_estado_numeros(self) -> str:
        return texto_estado_publico(self.estado_numeros)


@dataclass
class VistaConcurso:
    concurso: Concurso
    completitud: str
    modalidades: list[ModalidadPublica]

    @property
    def texto_completitud(self) -> str:
        return TEXTO_COMPLETITUD[self.completitud]

    def modalidad(self, modalidad: Modalidad) -> ModalidadPublica | None:
        for m in self.modalidades:
            if m.modalidad is modalidad:
                return m
        return None


def texto_estado_publico(estado: EstadoBloque) -> str:
    """RN-20."""
    if estado is EstadoBloque.SIN_CARGAR:
        return "Resultado pendiente"
    if estado in (EstadoBloque.BORRADOR, EstadoBloque.OBSERVADO):
        return "Pendiente de validación"
    if estado is EstadoBloque.EN_REVISION:
        return "Información en revisión"
    return "Publicado"


def estado_premio_extra(estados: list[EstadoBloque]) -> EstadoBloque:
    """RN-20: estado del conjunto de Premio Extra a partir de sus tres extracciones."""
    if any(e is EstadoBloque.SIN_CARGAR for e in estados):
        return EstadoBloque.SIN_CARGAR
    if any(e in (EstadoBloque.BORRADOR, EstadoBloque.OBSERVADO) for e in estados):
        return EstadoBloque.BORRADOR
    if any(e is EstadoBloque.EN_REVISION for e in estados):
        return EstadoBloque.EN_REVISION
    return EstadoBloque.PUBLICADO


def _condicion(codigo: str, version) -> str:
    """Cantidad de aciertos o condición que define la categoría (AC-1.7)."""
    if codigo in ACIERTOS_CATEGORIA:
        return f"{ACIERTOS_CATEGORIA[codigo]} aciertos"
    if version.sin_ganadores:
        return "Sin ganadores"
    if version.aciertos_categoria_ganadora is not None:
        return f"{version.aciertos_categoria_ganadora} aciertos"
    return "Categoría ganadora no publicada"


def _fuente(version) -> tuple[str, date | None] | None:
    if version is None:
        return None
    return (version.fuente_descripcion, version.fuente_fecha_consulta)


def vista_publica_concurso(concurso: Concurso) -> VistaConcurso:
    por_modalidad = {mc.modalidad_enum: mc for mc in _modalidades(concurso)}
    resultado: list[ModalidadPublica] = []
    for modalidad in ORDEN_MODALIDADES:
        mc = por_modalidad.get(modalidad)
        if mc is None:
            continue
        vista = ModalidadPublica(
            modalidad=modalidad, nombre=modalidad.nombre, estado_numeros=EstadoBloque.SIN_CARGAR
        )
        if modalidad.tiene_extraccion_propia:
            vista.estado_numeros = estado_bloque(mc, NUMEROS)
            if vista.estado_numeros.publicado:
                version = version_vigente(mc, NUMEROS)
                vista.numeros = sorted(version.numeros)
                vista.fuente_numeros = _fuente(version)
                vista.revision_numeros = vista.estado_numeros is EstadoBloque.EN_REVISION
                vista.corregido_numeros = fecha_ultima_correccion(mc, NUMEROS)
        else:
            estados = []
            conjuntos = []
            for m in MODALIDADES_PREMIO_EXTRA:
                otro = por_modalidad.get(m)
                estado = estado_bloque(otro, NUMEROS) if otro else EstadoBloque.SIN_CARGAR
                estados.append(estado)
                if estado.publicado:
                    conjuntos.append(version_vigente(otro, NUMEROS).numeros)
            vista.estado_numeros = estado_premio_extra(estados)
            if vista.estado_numeros.publicado and len(conjuntos) == 3:
                vista.conjunto = sorted(conjunto_premio_extra(*conjuntos))
                vista.revision_numeros = vista.estado_numeros is EstadoBloque.EN_REVISION
                fechas = [
                    fecha_ultima_correccion(por_modalidad[m], NUMEROS)
                    for m in MODALIDADES_PREMIO_EXTRA
                ]
                fechas = [f for f in fechas if f]
                vista.corregido_numeros = max(fechas) if fechas else None

        vista.estado_premios = estado_bloque(mc, PREMIOS)
        if vista.estado_premios.publicado:
            version = version_vigente(mc, PREMIOS)
            vista.fuente_premios = _fuente(version)
            vista.revision_premios = vista.estado_premios is EstadoBloque.EN_REVISION
            vista.corregido_premios = fecha_ultima_correccion(mc, PREMIOS)
            vista.aciertos_categoria_ganadora = version.aciertos_categoria_ganadora
            vista.sin_ganadores = version.sin_ganadores
            orden_cat = {c: i for i, c in enumerate(modalidad.categorias)}
            for cat in sorted(version.categorias.all(), key=lambda c: orden_cat[c.categoria]):
                vista.categorias.append(
                    CategoriaVista(
                        codigo=cat.categoria,
                        nombre=nombre_categoria(
                            modalidad, cat.categoria, version.aciertos_categoria_ganadora
                        ),
                        condicion=_condicion(cat.categoria, version),
                        ganadores=cat.ganadores,
                        importe_categoria=cat.importe_categoria,
                        importe_individual=cat.importe_individual,
                        pozo_vacante_acumulado=cat.pozo_vacante_acumulado,
                    )
                )
        resultado.append(vista)
    return VistaConcurso(
        concurso=concurso, completitud=completitud(concurso), modalidades=resultado
    )


def modalidad_concurso(concurso: Concurso, modalidad: Modalidad) -> ModalidadConcurso | None:
    for mc in concurso.modalidades.all():
        if mc.modalidad == modalidad.value:
            return mc
    return None


# --- Historial (US7) ---------------------------------------------------------------------


def historial_cambios(concurso: Concurso):
    """Entradas de ``RegistroCambio`` de un concurso, de la más reciente a la más antigua."""
    from resultados.models import RegistroCambio

    return list(
        RegistroCambio.objects.filter(concurso=concurso)
        .select_related("autor")
        .order_by("-fecha_hora", "-id")
    )


def _vigente_en(versiones: list, momento, inclusive: bool):
    """La versión que estaba publicada en ``momento`` (justo antes si no es ``inclusive``)."""
    for v in versiones:
        if v.publicada_en is None:
            continue
        publicada = v.publicada_en <= momento if inclusive else v.publicada_en < momento
        if v.reemplazada_en is None:
            vigente = True
        else:
            vigente = v.reemplazada_en > momento if inclusive else v.reemplazada_en >= momento
        if publicada and vigente:
            return v
    return None


def _datos_en(concurso: Concurso, momento, inclusive: bool) -> DatosConcurso:
    numeros: dict[Modalidad, BloqueNumerosVista] = {}
    premios: dict[Modalidad, BloquePremiosVista] = {}
    modalidades = set()
    for mc in _modalidades(concurso):
        modalidad = mc.modalidad_enum
        modalidades.add(modalidad)
        if modalidad.tiene_extraccion_propia:
            v = _vigente_en(_versiones(mc, NUMEROS), momento, inclusive)
            numeros[modalidad] = _vista_numeros(
                EstadoBloque.PUBLICADO if v else EstadoBloque.SIN_CARGAR, v
            )
        v = _vigente_en(_versiones(mc, PREMIOS), momento, inclusive)
        premios[modalidad] = _vista_premios(
            EstadoBloque.PUBLICADO if v else EstadoBloque.SIN_CARGAR, v
        )
    return DatosConcurso(concurso.fecha_sorteo, frozenset(modalidades), numeros, premios)


def historial_versiones(concurso: Concurso) -> list[tuple[date, DatosConcurso, DatosConcurso]]:
    """Datos publicados vigentes justo antes y justo después de cada corrección publicada,
    en orden cronológico (insumo de ``dominio.comparacion.cambio_por_correccion``, P-03)."""
    momentos = set()
    for mc in _modalidades(concurso):
        for bloque in BLOQUES:
            for v in _versiones(mc, bloque):
                if (
                    v.es_correccion
                    and v.publicada_en is not None
                    and v.estado in (EstadoVersion.PUBLICADA, EstadoVersion.REEMPLAZADA)
                ):
                    momentos.add(v.publicada_en)
    return [
        (
            timezone.localtime(m).date(),
            _datos_en(concurso, m, inclusive=False),
            _datos_en(concurso, m, inclusive=True),
        )
        for m in sorted(momentos)
    ]


# --- Estadísticas (US6) ------------------------------------------------------------------


def _filtro_periodo(prefijo: str, desde: date | None, hasta: date | None) -> dict:
    filtro = {}
    if desde is not None:
        filtro[f"{prefijo}fecha_sorteo__gte"] = desde
    if hasta is not None:
        filtro[f"{prefijo}fecha_sorteo__lte"] = hasta
    return filtro


def sorteos_publicados(modalidad: Modalidad, desde: date | None, hasta: date | None):
    """RN-41: solo números ``PUBLICADA`` vigentes (incluidos los que están en revisión) de
    concursos donde la modalidad es aplicable. Nunca Borrador ni Observado."""
    versiones = VersionNumeros.objects.filter(
        estado=EstadoVersion.PUBLICADA,
        modalidad_concurso__modalidad=modalidad.value,
        **_filtro_periodo("modalidad_concurso__concurso__", desde, hasta),
    ).select_related("modalidad_concurso__concurso")
    return [(v.modalidad_concurso.concurso.fecha_sorteo, v.numeros) for v in versiones]


def concursos_sin_informacion(modalidad: Modalidad, desde: date | None, hasta: date | None) -> int:
    """RN-45: concursos del período con la modalidad aplicable y sin números publicados."""
    return (
        ModalidadConcurso.objects.filter(
            modalidad=modalidad.value, **_filtro_periodo("concurso__", desde, hasta)
        )
        .exclude(versiones_numeros__estado=EstadoVersion.PUBLICADA)
        .count()
    )
