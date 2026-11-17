"""Comparación de una jugada con los resultados oficiales (contracts/dominio.md).

RN-28 a RN-33 y RN-49 a RN-54, con las decisiones P-02 y P-04 (Clarifications 13/11/2026).
Funciones puras: no importan Django. El importe es siempre el individual publicado; nunca
se divide un pozo ni se estima un valor (RN-27).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

from dominio.numeros import conjunto_premio_extra
from dominio.tipos import (
    FECHA_VIGENCIA_REGLAS,
    MODALIDADES_PREMIO_EXTRA,
    NOMBRE_CATEGORIA,
    ORDEN_MODALIDADES,
    BloquePremiosVista,
    DatosConcurso,
    EstadoBloque,
    Modalidad,
    Numeros,
)

AVISO_EN_REVISION = "AVISO_EN_REVISION"
AVISO_ACIERTOS_SUPERAN_CATEGORIA = "AVISO_ACIERTOS_SUPERAN_CATEGORIA"

TEXTO_AVISO = {
    AVISO_EN_REVISION: "Información en revisión: el resultado podría cambiar",
    AVISO_ACIERTOS_SUPERAN_CATEGORIA: (
        "Los aciertos de tu jugada superan la categoría ganadora publicada. "
        "Verificá los números y el concurso de tu jugada."
    ),
}


class EstadoValidacion(Enum):
    RESULTADO_PENDIENTE = "Resultado pendiente"
    PENDIENTE_VALIDACION = "Pendiente de validación"
    PUBLICADO = "Publicado"
    EN_REVISION = "Información en revisión"

    @property
    def publicado(self) -> bool:
        return self in (EstadoValidacion.PUBLICADO, EstadoValidacion.EN_REVISION)

    @property
    def texto(self) -> str:
        return self.value


class Elegibilidad(Enum):
    PARTICIPA = "Participa"
    EXCLUIDA = "Excluida"


class ResultadoPremio(Enum):
    CON_PREMIO = "Con premio"
    SIN_PREMIO = "Sin premio"
    PENDIENTE_DETERMINACION = "Premio pendiente de determinación"


class EstadoResumido(Enum):
    CON_PREMIO = "Con premio"
    CON_PREMIO_IMPORTE_PENDIENTE = "Con premio — información de premios pendiente de publicación"
    PENDIENTE_DETERMINACION = "Premio pendiente de determinación"
    RESULTADO_PENDIENTE = "Resultado pendiente"
    SIN_PREMIO = "Sin premio"

    @property
    def texto(self) -> str:
        return self.value


@dataclass(frozen=True)
class ResultadoModalidad:
    modalidad: Modalidad
    estado_validacion: EstadoValidacion
    aciertos: int | None = None
    numeros_acertados: Numeros | None = None
    elegibilidad: Elegibilidad | None = None
    excluida_por: Modalidad | None = None
    resultado_premio: ResultadoPremio | None = None
    categoria: str | None = None
    importe: Decimal | None = None
    importe_pendiente: bool = False
    avisos: frozenset[str] = field(default_factory=frozenset)
    conjunto: Numeros | None = None  # solo Premio Extra (AC-5.24, AC-5.26)
    numeros_oficiales: Numeros | None = None  # números de la extracción comparada

    @property
    def publicado(self) -> bool:
        return self.estado_validacion.publicado

    @property
    def texto_resultado(self) -> str | None:
        """ "{n} aciertos — Sin premio", "Con premio — {categoría}" o "Premio pendiente…"."""
        if self.resultado_premio is ResultadoPremio.CON_PREMIO:
            return f"Con premio — {self.categoria}"
        if self.resultado_premio is ResultadoPremio.SIN_PREMIO:
            return f"{self.aciertos} aciertos — Sin premio"
        if self.resultado_premio is ResultadoPremio.PENDIENTE_DETERMINACION:
            return ResultadoPremio.PENDIENTE_DETERMINACION.value
        return None

    @property
    def textos_avisos(self) -> list[str]:
        return [
            TEXTO_AVISO[a]
            for a in (AVISO_EN_REVISION, AVISO_ACIERTOS_SUPERAN_CATEGORIA)
            if a in self.avisos
        ]


_ESTADO = {
    EstadoBloque.SIN_CARGAR: EstadoValidacion.RESULTADO_PENDIENTE,
    EstadoBloque.BORRADOR: EstadoValidacion.PENDIENTE_VALIDACION,
    EstadoBloque.OBSERVADO: EstadoValidacion.PENDIENTE_VALIDACION,
    EstadoBloque.PUBLICADO: EstadoValidacion.PUBLICADO,
    EstadoBloque.EN_REVISION: EstadoValidacion.EN_REVISION,
}


def _estado_premio_extra(estados: Iterable[EstadoBloque]) -> EstadoValidacion:
    """RN-29.1 para Premio Extra: depende de las tres extracciones de su conjunto."""
    estados = list(estados)
    if any(e is EstadoBloque.SIN_CARGAR for e in estados):
        return EstadoValidacion.RESULTADO_PENDIENTE
    if any(e in (EstadoBloque.BORRADOR, EstadoBloque.OBSERVADO) for e in estados):
        return EstadoValidacion.PENDIENTE_VALIDACION
    if any(e is EstadoBloque.EN_REVISION for e in estados):
        return EstadoValidacion.EN_REVISION
    return EstadoValidacion.PUBLICADO


def _categoria_fija(modalidad: Modalidad, aciertos: int) -> str | None:
    """RN-49 a RN-51: código de la categoría alcanzada, o ``None``."""
    if modalidad in (Modalidad.PRIMER_SORTEO, Modalidad.LA_SEGUNDA):
        return {6: "PRIMER", 5: "SEGUNDO", 4: "TERCER"}.get(aciertos)
    if modalidad is Modalidad.REVANCHA:
        return "UNICO" if aciertos == 6 else None
    return None


def _categoria_ganadora(premios: BloquePremiosVista) -> tuple[int | None, bool]:
    """Categoría ganadora publicada y si el extracto informó "sin ganadores"."""
    if not premios.estado.publicado:
        return None, False
    return premios.aciertos_categoria_ganadora, bool(premios.sin_ganadores)


def _decidir_variable(aciertos: int, categoria: int | None, sin_ganadores: bool, extra: bool):
    """RN-52 (Siempre Sale) y RN-31 (Premio Extra) con la precedencia de P-02.

    Devuelve ``(resultado, aviso_superan)``.
    """
    superada = sin_ganadores or (categoria is not None and aciertos > categoria)
    if aciertos == 6 and not superada:
        return ResultadoPremio.CON_PREMIO, False  # (a)
    if superada and (aciertos == 6 or not sin_ganadores):
        return ResultadoPremio.PENDIENTE_DETERMINACION, True  # (e), incluido P-02
    if extra and (aciertos <= 3 or sin_ganadores):
        return ResultadoPremio.SIN_PREMIO, False  # RN-31 (c)
    if categoria is None:
        return ResultadoPremio.PENDIENTE_DETERMINACION, False  # (d)
    if aciertos == categoria:
        return ResultadoPremio.CON_PREMIO, False  # (b)
    return ResultadoPremio.SIN_PREMIO, False  # (c)


def _importe(premios: BloquePremiosVista, codigo: str) -> tuple[Decimal | None, bool]:
    """RN-27: solo el importe individual publicado; si no, "pendiente de publicación"."""
    if premios.estado.publicado:
        cat = premios.categoria(codigo)
        if cat is not None and cat.importe_individual is not None:
            return cat.importe_individual, False
    return None, True


def _avisos_revision(*estados: EstadoBloque) -> set[str]:
    return {AVISO_EN_REVISION} if any(e is EstadoBloque.EN_REVISION for e in estados) else set()


def _comparar_extraccion(
    jugada: Numeros, modalidad: Modalidad, concurso: DatosConcurso
) -> ResultadoModalidad:
    bloque = concurso.bloque_numeros(modalidad)
    estado = _ESTADO[bloque.estado]
    if not estado.publicado or bloque.numeros is None:
        return ResultadoModalidad(modalidad, estado)
    premios = concurso.bloque_premios(modalidad)
    acertados = frozenset(jugada) & frozenset(bloque.numeros)
    aciertos = len(acertados)
    avisos = _avisos_revision(bloque.estado, premios.estado)
    codigo = None
    categoria = None
    if concurso.fecha_sorteo < FECHA_VIGENCIA_REGLAS:
        resultado = ResultadoPremio.PENDIENTE_DETERMINACION  # RN-33
    elif modalidad is Modalidad.SIEMPRE_SALE:
        ganadora, _ = _categoria_ganadora(premios)
        resultado, superan = _decidir_variable(aciertos, ganadora, False, extra=False)
        if superan:
            avisos.add(AVISO_ACIERTOS_SUPERAN_CATEGORIA)
        if resultado is ResultadoPremio.CON_PREMIO:
            codigo = "GANADORA"
            categoria = f"{modalidad.nombre} ({aciertos} aciertos)"
    else:
        codigo = _categoria_fija(modalidad, aciertos)
        if codigo is None:
            resultado = ResultadoPremio.SIN_PREMIO
        else:
            resultado = ResultadoPremio.CON_PREMIO
            categoria = NOMBRE_CATEGORIA[codigo]
    importe, pendiente = None, False
    if resultado is ResultadoPremio.CON_PREMIO:
        importe, pendiente = _importe(premios, codigo)
    return ResultadoModalidad(
        modalidad=modalidad,
        estado_validacion=estado,
        aciertos=aciertos,
        numeros_acertados=acertados,
        resultado_premio=resultado,
        categoria=categoria,
        importe=importe,
        importe_pendiente=pendiente,
        avisos=frozenset(avisos),
        numeros_oficiales=frozenset(bloque.numeros),
    )


def _comparar_premio_extra(jugada: Numeros, concurso: DatosConcurso) -> ResultadoModalidad:
    modalidad = Modalidad.PREMIO_EXTRA
    bloques = [concurso.bloque_numeros(m) for m in MODALIDADES_PREMIO_EXTRA]
    estado = _estado_premio_extra(b.estado for b in bloques)
    if not estado.publicado or any(b.numeros is None for b in bloques):
        return ResultadoModalidad(modalidad, estado)
    premios = concurso.bloque_premios(modalidad)
    conjunto = conjunto_premio_extra(*(b.numeros for b in bloques))
    acertados = frozenset(jugada) & conjunto
    aciertos = len(acertados)
    avisos = _avisos_revision(*(b.estado for b in bloques), premios.estado)
    base = {
        "modalidad": modalidad,
        "estado_validacion": estado,
        "aciertos": aciertos,
        "numeros_acertados": acertados,
        "conjunto": conjunto,
        "numeros_oficiales": conjunto,
    }
    if concurso.fecha_sorteo < FECHA_VIGENCIA_REGLAS:
        return ResultadoModalidad(
            **base,
            resultado_premio=ResultadoPremio.PENDIENTE_DETERMINACION,
            avisos=frozenset(avisos),
        )
    for m, bloque in zip(MODALIDADES_PREMIO_EXTRA, bloques, strict=True):
        if len(frozenset(jugada) & bloque.numeros) == 6:  # RN-53
            return ResultadoModalidad(
                **base,
                elegibilidad=Elegibilidad.EXCLUIDA,
                excluida_por=m,
                avisos=frozenset(avisos),
            )
    ganadora, sin_ganadores = _categoria_ganadora(premios)
    resultado, superan = _decidir_variable(aciertos, ganadora, sin_ganadores, extra=True)
    if superan:
        avisos.add(AVISO_ACIERTOS_SUPERAN_CATEGORIA)
    categoria = None
    importe, pendiente = None, False
    if resultado is ResultadoPremio.CON_PREMIO:
        categoria = f"{modalidad.nombre} ({aciertos} aciertos)"
        importe, pendiente = _importe(premios, "GANADORA")
    return ResultadoModalidad(
        **base,
        elegibilidad=Elegibilidad.PARTICIPA,
        resultado_premio=resultado,
        categoria=categoria,
        importe=importe,
        importe_pendiente=pendiente,
        avisos=frozenset(avisos),
    )


def comparar_jugada(jugada: Numeros, concurso: DatosConcurso) -> list[ResultadoModalidad]:
    """Un resultado por modalidad aplicable, en el orden de AC-5.31."""
    resultados = []
    for modalidad in ORDEN_MODALIDADES:
        if modalidad not in concurso.modalidades:
            continue
        if modalidad.tiene_extraccion_propia:
            resultados.append(_comparar_extraccion(frozenset(jugada), modalidad, concurso))
        else:
            resultados.append(_comparar_premio_extra(frozenset(jugada), concurso))
    return resultados


def resumir_jugada(resultados: Sequence[ResultadoModalidad]) -> EstadoResumido:
    """Estado resumido del historial con la precedencia de P-04 (AC-5.13)."""
    if not resultados:
        return EstadoResumido.RESULTADO_PENDIENTE
    con_premio = [r for r in resultados if r.resultado_premio is ResultadoPremio.CON_PREMIO]
    if con_premio:
        if all(not r.importe_pendiente for r in con_premio):
            return EstadoResumido.CON_PREMIO
        return EstadoResumido.CON_PREMIO_IMPORTE_PENDIENTE
    if any(r.resultado_premio is ResultadoPremio.PENDIENTE_DETERMINACION for r in resultados):
        return EstadoResumido.PENDIENTE_DETERMINACION
    if any(not r.publicado for r in resultados):
        return EstadoResumido.RESULTADO_PENDIENTE
    return EstadoResumido.SIN_PREMIO


def _datos_rn29(r: ResultadoModalidad) -> tuple:
    """Los cinco datos de RN-29 que, si cambian, se informan como "Actualizado por…"."""
    return (
        r.estado_validacion.publicado,
        r.aciertos,
        r.elegibilidad,
        r.resultado_premio,
        r.categoria,
        r.importe,
        r.importe_pendiente,
    )


def cambio_por_correccion(
    jugada: Numeros, historial_de_versiones: Sequence[tuple[date, DatosConcurso, DatosConcurso]]
) -> dict[Modalidad, date | None]:
    """RN-32 y P-03: para cada modalidad, la fecha de la corrección publicada más reciente que
    cambió alguno de los cinco datos de RN-29, o ``None``.

    ``historial_de_versiones`` es una secuencia de ``(fecha_correccion, antes, despues)``:
    los datos publicados vigentes justo antes y justo después de cada corrección.
    """
    fechas: dict[Modalidad, date | None] = {}
    for fecha, antes, despues in historial_de_versiones:
        previos = {r.modalidad: r for r in comparar_jugada(jugada, antes)}
        nuevos = {r.modalidad: r for r in comparar_jugada(jugada, despues)}
        for modalidad, nuevo in nuevos.items():
            previo = previos.get(modalidad)
            if previo is None or _datos_rn29(previo) != _datos_rn29(nuevo):
                actual = fechas.get(modalidad)
                if actual is None or fecha > actual:
                    fechas[modalidad] = fecha
    return {
        m: fechas.get(m) for m in ORDEN_MODALIDADES if m in _modalidades(historial_de_versiones)
    }


def _modalidades(historial) -> set[Modalidad]:
    modalidades: set[Modalidad] = set()
    for _fecha, antes, despues in historial:
        modalidades |= set(antes.modalidades) | set(despues.modalidades)
    return modalidades
