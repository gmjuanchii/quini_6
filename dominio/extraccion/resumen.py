"""Resumen de una extracción ([002] RN-10, RN-33, I-05, I-10). No importa Django.

Devuelve un diccionario con valores simples (fechas ISO), listo para guardarse en JSON
([002] data-model.md → "Resumen guardado").
"""

from __future__ import annotations

from collections.abc import Iterable

from dominio.extraccion.clasificacion import es_hueco
from dominio.extraccion.consolidacion import datos_consolidados
from dominio.extraccion.identificacion import Identificacion
from dominio.extraccion.tipos import (
    EstadoExtraccion,
    EstadoSorteo,
    Fuente,
    ResultadoIntento,
    SorteoConsolidado,
    Valor,
)


def aportados_por(sorteo: SorteoConsolidado) -> set[Fuente]:
    """I-05: fuentes que respaldan al menos un dato del consolidado."""
    return {f for _, dato in datos_consolidados(sorteo) for f in dato.fuentes}


def resumir(
    identificacion: Identificacion,
    sorteos: Iterable[SorteoConsolidado],
    fuentes: Iterable[Fuente],
) -> dict:
    sorteos = sorted(sorteos, key=lambda s: s.numero)
    fuentes = list(fuentes)
    por_estado = {estado.value: 0 for estado in EstadoSorteo}
    for sorteo in sorteos:
        por_estado[sorteo.estado.value] += 1

    resumen_fuentes = []
    for fuente in fuentes:
        intentos = {r.value: 0 for r in ResultadoIntento}
        aportados = 0
        cubiertos = 0
        no_reconocidos = 0
        for sorteo in sorteos:
            resultado = sorteo.resultados.get(fuente)
            if resultado is None:
                continue
            intentos[resultado.value] += 1
            if resultado is not ResultadoIntento.FUERA_DE_COBERTURA:
                cubiertos += 1
                if resultado is ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA:
                    no_reconocidos += 1
            if fuente in aportados_por(sorteo):
                aportados += 1
        resumen_fuentes.append(
            {
                "fuente": fuente.value,
                "nombre": fuente.nombre,
                "aportados": aportados,
                "intentos": intentos,
                "fallidos": {
                    clave: n
                    for clave, n in intentos.items()
                    if n and ResultadoIntento(clave).es_fallido
                },
                # RN-10, AC-2.10: cubre al menos un sorteo y no reconoció ninguno.
                "requiere_mantenimiento": cubiertos > 0 and no_reconocidos == cubiertos,
            }
        )

    huecos = [
        s.numero
        for s in sorteos
        if s.estado is EstadoSorteo.NO_RECUPERADO
        and not s.error_inesperado
        and not any(r.aporta_datos for r in s.resultados.values())
        and es_hueco(s.resultados)
    ]
    a_revisar = [
        {
            "numero": s.numero,
            "fecha": s.fecha.dato.v.isoformat() if isinstance(s.fecha.dato, Valor) else None,
            "estado": s.estado.value,
            "motivos": list(s.motivos),
        }
        for s in sorteos
        if s.estado is not EstadoSorteo.RECUPERADO
    ]
    resultado = (
        EstadoExtraccion.FINALIZADA
        if sorteos and all(s.estado is EstadoSorteo.RECUPERADO for s in sorteos)
        else EstadoExtraccion.CON_ADVERTENCIAS
    )
    cobertura = identificacion.cobertura_desde
    return {
        "identificados": identificacion.total,
        "por_estado": por_estado,
        "fuentes": resumen_fuentes,
        "huecos": huecos,
        "cobertura_desde": cobertura.isoformat() if cobertura else None,
        "a_revisar": a_revisar,
        "resultado": resultado.value,
    }
