"""Identificación de los sorteos del período ([002] RN-05, R-06, I-02).

Las fechas nunca se deducen del calendario: la estimación de dos sorteos por semana solo elige
qué número pedir, y la pertenencia al período la decide siempre la fecha que informan las
fuentes. Se asume la correlatividad entre número y fecha (RN-23) para buscar los bordes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date

from dominio.extraccion.periodo import Periodo
from dominio.extraccion.tipos import Fuente

#: Números consecutivos sin fecha que se prueban antes de considerar que no hay más sorteos.
MAX_HUECO = 5
SORTEOS_POR_SEMANA = 2


@dataclass(frozen=True)
class Referencia:
    """Fila de un listado ya interpretada: (número, fecha, fuente)."""

    numero: int
    fecha: date
    fuente: Fuente


@dataclass(frozen=True)
class Identificacion:
    numero_desde: int
    numero_hasta: int
    cobertura_desde: date | None = None

    @property
    def total(self) -> int:
        return self.numero_hasta - self.numero_desde + 1


@dataclass(frozen=True)
class SinSorteos:
    """Ningún sorteo con fecha informada dentro del período ([002] AC-1.10)."""

    cobertura_desde: date | None = None


def identificar_sorteos(
    periodo: Periodo,
    referencias: Iterable[Referencia],
    fecha_de: Callable[[int], Iterable[date]],
    primer_cubierto: tuple[int, date],
) -> Identificacion | SinSorteos:
    """[002] RN-05: primer y último número con fecha informada dentro del período.

    ``fecha_de(numero)`` devuelve las fechas que informan las fuentes para ese número (vacía si
    ninguna). Solo se llama para números que no figuran en las referencias.
    """
    primer_numero, primer_fecha = primer_cubierto
    cobertura = primer_fecha if periodo.desde < primer_fecha else None
    if periodo.hasta < primer_fecha:
        return SinSorteos(cobertura)

    conocidas: dict[int, set[date]] = {}
    for ref in referencias:
        conocidas.setdefault(ref.numero, set()).add(ref.fecha)
    ultimo_conocido = max(conocidas) if conocidas else None
    consultadas: dict[int, set[date]] = {}

    def fechas(numero: int) -> set[date]:
        if numero < primer_numero:
            return set()
        if numero in conocidas:
            return conocidas[numero]
        if ultimo_conocido is not None and numero > ultimo_conocido:
            return set()  # los listados muestran el último sorteo: no hay posteriores
        if numero not in consultadas:
            consultadas[numero] = set(fecha_de(numero))
        return consultadas[numero]

    def estimar(objetivo: date) -> int:
        if conocidas:
            base_numero, base_fecha = min(
                ((n, min(fs)) for n, fs in conocidas.items()),
                key=lambda par: abs((par[1] - objetivo).days),
            )
        else:
            base_numero, base_fecha = primer_numero, primer_fecha
        dias = (objetivo - base_fecha).days
        return max(primer_numero, base_numero + round(dias * SORTEOS_POR_SEMANA / 7))

    def llega_al_inicio(numero: int) -> bool | None:
        fs = fechas(numero)
        return any(f >= periodo.desde for f in fs) if fs else None

    def pasa_el_fin(numero: int) -> bool | None:
        fs = fechas(numero)
        return all(f > periodo.hasta for f in fs) if fs else None

    # Sin listados, el último sorteo publicado se estima con holgura: la búsqueda siempre termina.
    tope = ultimo_conocido if ultimo_conocido is not None else estimar(periodo.hasta) + 200
    inicio = _primer_verdadero(llega_al_inicio, estimar(periodo.desde), primer_numero, tope)
    desde = _siguiente_con_fecha(inicio, fechas)
    if desde is None or not any(periodo.contiene(f) for f in fechas(desde)):
        return SinSorteos(cobertura)

    fin = _primer_verdadero(pasa_el_fin, max(desde, estimar(periodo.hasta)), primer_numero, tope)
    hasta = fin - 1
    while hasta > desde and not fechas(hasta):
        hasta -= 1  # un hueco en el borde no se incluye: no se sabe si es del período
    if hasta < desde or not any(periodo.contiene(f) for f in fechas(hasta)):
        return SinSorteos(cobertura)
    return Identificacion(desde, hasta, cobertura)


def _siguiente_con_fecha(numero: int, fechas) -> int | None:
    for candidato in range(numero, numero + MAX_HUECO):
        if fechas(candidato):
            return candidato
    return None


def _primer_verdadero(predicado, inicio: int, minimo: int, tope: int) -> int:
    """Menor número ``>= minimo`` cuyo predicado es verdadero (falso…falso verdadero…verdadero).

    Un número sin fecha toma el valor del siguiente con fecha; ``MAX_HUECO`` números seguidos
    sin fecha cuentan como verdadero (se sigue buscando hacia abajo). Los números mayores que
    ``tope`` (el último sorteo publicado) son verdaderos.
    """

    def valor(numero: int) -> bool:
        if numero < minimo:
            return False
        for candidato in range(numero, numero + MAX_HUECO):
            if candidato > tope:
                return True
            resultado = predicado(candidato)
            if resultado is not None:
                return resultado
        return True

    n = max(minimo, inicio)
    if valor(n):
        alto, paso = n, 1
        while True:
            bajo = alto - paso
            if bajo < minimo:
                bajo = minimo - 1
                break
            if not valor(bajo):
                break
            alto, paso = bajo, paso * 2
    else:
        bajo, paso = n, 1
        while True:
            alto = min(bajo + paso, tope + 1)
            if valor(alto):
                break
            bajo, paso = alto, paso * 2
    while alto - bajo > 1:
        medio = (alto + bajo) // 2
        if valor(medio):
            alto = medio
        else:
            bajo = medio
    return alto
