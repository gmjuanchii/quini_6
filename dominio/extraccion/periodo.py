"""Validación del período de una extracción ([002] RN-01 a RN-04, I-01).

Errores como valores: ``validar_periodo`` devuelve un ``Periodo`` o la lista de errores.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta

FECHA_INVALIDA = "Ingresá una fecha válida (dd/mm/aaaa)"
INICIO_POSTERIOR = "La fecha de inicio no puede ser posterior a la fecha de finalización"
FIN_FUTURA = "La fecha de finalización no puede ser posterior a hoy"
PERIODO_LARGO = "El período no puede superar los 12 meses"

_FECHA = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")
#: Valor que envía el selector de fecha del navegador (``<input type="date">``, [002] D-25).
_FECHA_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


@dataclass(frozen=True)
class Periodo:
    """Período inclusivo ([002] RN-01)."""

    desde: date
    hasta: date

    def contiene(self, fecha: date) -> bool:
        return self.desde <= fecha <= self.hasta


@dataclass(frozen=True)
class ErrorPeriodo:
    """Códigos: FECHA_INVALIDA (con ``campo``), INICIO_POSTERIOR, FIN_FUTURA, PERIODO_LARGO.

    ``campo`` es ``"inicio"``, ``"fin"`` o ``None`` (error general del período).
    """

    codigo: str
    campo: str | None
    texto: str


def parsear_fecha(texto: str | None) -> date | None:
    """``dd/mm/aaaa`` o ``AAAA-MM-DD`` → ``date``; ``None`` si está vacía o no es válida.

    [002] RN-02. ``AAAA-MM-DD`` es lo que envía el selector de fecha del navegador (D-25).
    """
    texto = (texto or "").strip()
    if coincidencia := _FECHA_ISO.match(texto):
        anio, mes, dia = (int(g) for g in coincidencia.groups())
    elif coincidencia := _FECHA.match(texto):
        dia, mes, anio = (int(g) for g in coincidencia.groups())
    else:
        return None
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None


def mismo_dia_anio_siguiente(fecha: date) -> date:
    """La misma fecha del año siguiente; del 29/02 da el 01/03 ([002] I-01)."""
    try:
        return fecha.replace(year=fecha.year + 1)
    except ValueError:
        return date(fecha.year + 1, 2, 28) + timedelta(days=1)


def validar_periodo(
    inicio_texto: str | None, fin_texto: str | None, hoy: date
) -> Periodo | list[ErrorPeriodo]:
    """[002] RN-01 a RN-04. ``hoy`` es la fecha local de Buenos Aires."""
    desde = parsear_fecha(inicio_texto)
    hasta = parsear_fecha(fin_texto)
    errores: list[ErrorPeriodo] = []
    if desde is None:
        errores.append(ErrorPeriodo("FECHA_INVALIDA", "inicio", FECHA_INVALIDA))
    if hasta is None:
        errores.append(ErrorPeriodo("FECHA_INVALIDA", "fin", FECHA_INVALIDA))
    if errores:
        return errores
    if desde > hasta:
        errores.append(ErrorPeriodo("INICIO_POSTERIOR", None, INICIO_POSTERIOR))
    if hasta > hoy:
        errores.append(ErrorPeriodo("FIN_FUTURA", "fin", FIN_FUTURA))
    if desde <= hasta and hasta >= mismo_dia_anio_siguiente(desde):
        errores.append(ErrorPeriodo("PERIODO_LARGO", None, PERIODO_LARGO))
    return errores or Periodo(desde, hasta)
