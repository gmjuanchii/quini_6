"""Estadísticas descriptivas de frecuencia (RN-40 a RN-47).

Solo cuentan apariciones: no clasifican, no predicen ni recomiendan números (RN-47).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dominio.tipos import Numeros

NUMEROS_POSIBLES = range(46)
PERIODO_INVALIDO = "La fecha desde no puede ser posterior a la fecha hasta. Corregí el período."


@dataclass(frozen=True)
class FrecuenciaNumero:
    numero: int
    frecuencia: int
    porcentaje: Decimal


@dataclass(frozen=True)
class Frecuencias:
    cantidad_sorteos: int
    primera_fecha: date
    ultima_fecha: date
    concursos_sin_informacion: int
    numeros: tuple[FrecuenciaNumero, ...]

    def numero(self, n: int) -> FrecuenciaNumero:
        return self.numeros[n]

    @property
    def frecuencia_maxima(self) -> int:
        return max((f.frecuencia for f in self.numeros), default=0)


@dataclass(frozen=True)
class SinSorteos:
    concursos_sin_informacion: int = 0


@dataclass(frozen=True)
class ErrorPeriodo:
    mensaje: str = PERIODO_INVALIDO


def _porcentaje(frecuencia: int, total: int) -> Decimal:
    return (Decimal(frecuencia) * Decimal(100) / Decimal(total)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calcular_frecuencias(
    sorteos: Iterable[tuple[date, Numeros]],
    concursos_sin_informacion: int,
    desde: date | None,
    hasta: date | None,
) -> Frecuencias | SinSorteos | ErrorPeriodo:
    if desde is not None and hasta is not None and desde > hasta:
        return ErrorPeriodo()
    considerados = [
        (fecha, frozenset(numeros))
        for fecha, numeros in sorteos
        if (desde is None or fecha >= desde) and (hasta is None or fecha <= hasta)
    ]
    if not considerados:
        return SinSorteos(concursos_sin_informacion)
    total = len(considerados)
    conteo = dict.fromkeys(NUMEROS_POSIBLES, 0)
    for _fecha, numeros in considerados:
        for n in numeros:
            conteo[n] += 1
    fechas = [fecha for fecha, _ in considerados]
    return Frecuencias(
        cantidad_sorteos=total,
        primera_fecha=min(fechas),
        ultima_fecha=max(fechas),
        concursos_sin_informacion=concursos_sin_informacion,
        numeros=tuple(
            FrecuenciaNumero(n, conteo[n], _porcentaje(conteo[n], total)) for n in NUMEROS_POSIBLES
        ),
    )
