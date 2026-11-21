"""Clasificación de un sorteo ([002] RN-31, I-09, I-10). No importa Django."""

from __future__ import annotations

from dataclasses import replace

from dominio.extraccion.consolidacion import datos_consolidados
from dominio.extraccion.normalizacion import OBS_FALTA
from dominio.extraccion.tipos import (
    MODALIDADES_PROPIAS,
    ORDEN_FUENTES,
    EstadoSorteo,
    Fuente,
    Modalidad,
    ResultadoIntento,
    SorteoConsolidado,
    Valor,
    categorias_esperadas,
    nombre_categoria,
    nombre_modalidad,
)
from dominio.tipos import ORDEN_MODALIDADES

MOTIVO_SIN_FUENTE = "Ninguna fuente informa este número de sorteo"  # obs.sin_fuente
MOTIVO_ERROR_INESPERADO = "Error inesperado al procesar el sorteo"  # motivo.error_inesperado
NO_INFORMADA = "No informada por las fuentes"  # modalidad.no_informada

_CAMPOS_LEGIBLES = {
    "numeros": "números",
    "aciertos": "aciertos",
    "ganadores": "ganadores",
    "pozo_destinado": "pozo destinado",
    "importe_individual": "importe individual",
}

_HUECO = (ResultadoIntento.NO_ENCONTRADO, ResultadoIntento.NO_DISPONIBLE_O_NO_ENCONTRADO)


def describir_dato(clave: str) -> str:
    """``PRIMER_SORTEO.PRIMER.ganadores`` → ``Tradicional: Primer Premio: ganadores``."""
    if clave == "fecha":
        return "Fecha"
    partes = clave.split(".")
    texto = [nombre_modalidad(Modalidad(partes[0]))]
    if len(partes) == 3:
        texto.append(nombre_categoria(partes[1]))
    texto.append(_CAMPOS_LEGIBLES[partes[-1]])
    return ": ".join(texto)


def es_hueco(resultados: dict[Fuente, ResultadoIntento]) -> bool:
    """I-10: todas las fuentes que lo cubren respondieron "No encontrado" o "No disponible o no
    encontrado". Si alguna quedó "No disponible" o "Estructura no reconocida", no es hueco."""
    cubren = [r for r in resultados.values() if not r.no_consultada]
    return all(r in _HUECO for r in cubren)


def _texto_observacion(observacion) -> str:
    if observacion.fuente is not None:
        return f"{observacion.fuente.nombre}: {observacion.texto}"
    return observacion.texto


def faltantes(sorteo: SorteoConsolidado) -> list[str]:
    """Datos esperados que faltan ([002] RN-31). El pozo de una categoría con ganadores y los
    aciertos no son datos esperados (AC-3.6)."""
    faltan: list[str] = []
    if not isinstance(sorteo.fecha.dato, Valor):
        faltan.append("fecha")
    for modalidad in ORDEN_MODALIDADES:
        mc = sorteo.modalidades.get(modalidad)
        if mc is None or not mc.informada:
            faltan.append(f"{nombre_modalidad(modalidad)}: {NO_INFORMADA}")
            continue
        if modalidad in MODALIDADES_PROPIAS and not isinstance(mc.numeros.dato, Valor):
            faltan.append(f"{nombre_modalidad(modalidad)}: números")
        for codigo in categorias_esperadas(modalidad):
            nombre = f"{nombre_modalidad(modalidad)}: {nombre_categoria(codigo)}"
            cat = mc.categorias.get(codigo)
            ganadores = cat.ganadores.dato if cat else None
            if not isinstance(ganadores, Valor):
                faltan.append(f"{nombre}: ganadores")
            elif ganadores.v == 0 and not isinstance(cat.pozo_destinado.dato, Valor):
                faltan.append(f"{nombre}: pozo destinado")
            elif ganadores.v > 0 and not isinstance(cat.importe_individual.dato, Valor):
                faltan.append(f"{nombre}: importe individual")
    return faltan


def clasificar(sorteo: SorteoConsolidado) -> tuple[EstadoSorteo, tuple[str, ...]]:
    """[002] RN-31: precedencia No recuperado → Con inconsistencias → Recuperado parcialmente →
    Recuperado. "Combina fuentes" y "Sin corroborar" no cambian el estado."""
    if sorteo.error_inesperado:
        return EstadoSorteo.NO_RECUPERADO, (MOTIVO_ERROR_INESPERADO,)
    if not any(r.aporta_datos for r in sorteo.resultados.values()):
        if es_hueco(sorteo.resultados):
            return EstadoSorteo.NO_RECUPERADO, (MOTIVO_SIN_FUENTE,)
        motivos = tuple(
            f"{fuente.nombre}: {sorteo.resultados[fuente].texto}"
            for fuente in ORDEN_FUENTES
            if fuente in sorteo.resultados
        )
        return EstadoSorteo.NO_RECUPERADO, motivos

    inconsistencias = [
        f"{describir_dato(clave)}: {dato.discrepancia.tipo.texto}"
        for clave, dato in datos_consolidados(sorteo)
        if dato.discrepancia is not None
    ]
    inconsistencias += [_texto_observacion(o) for o in sorteo.observaciones if o.es_inconsistencia]
    if inconsistencias:
        return EstadoSorteo.CON_INCONSISTENCIAS, tuple(inconsistencias)

    faltan = faltantes(sorteo)
    if faltan:
        return EstadoSorteo.PARCIAL, (OBS_FALTA.format(lista="; ".join(faltan)),)
    return EstadoSorteo.RECUPERADO, ()


def aplicar_clasificacion(sorteo: SorteoConsolidado) -> SorteoConsolidado:
    estado, motivos = clasificar(sorteo)
    return replace(sorteo, estado=estado, motivos=motivos)


def requiere_respaldo(sorteo: SorteoConsolidado) -> bool:
    """[002] RN-09, AC-2.11, D-21: se consultan las fuentes de respaldo si, con las prioritarias,
    el sorteo quedó "No recuperado", le falta algún dato esperado, las fuentes difieren en algún
    dato o una fuente publicó un dato inválido (observación de inconsistencia)."""
    if not any(r.aporta_datos for r in sorteo.resultados.values()):
        return True
    if any(d.discrepancia is not None for _, d in datos_consolidados(sorteo)):
        return True
    if any(o.es_inconsistencia and o.fuente is not None for o in sorteo.observaciones):
        return True
    return bool(faltantes(sorteo))
