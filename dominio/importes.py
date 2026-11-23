"""Importes en pesos argentinos (RN-09, RN-43, NFR-007, R-08).

Siempre ``decimal.Decimal``; un ``float`` lanza ``TypeError``. La coma es el separador
decimal; el punto solo se acepta como separador de miles en grupos de tres dígitos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from dominio.mensajes import MENSAJES

_CENTAVOS = Decimal("0.01")
_IMPORTE = re.compile(r"^(?P<entero>\d+|\d{1,3}(?:\.\d{3})+)(?:,(?P<decimales>\d+))?$")


@dataclass(frozen=True)
class ErrorImporte:
    """Códigos: VACIO, NEGATIVO, NO_NUMERICO, DEMASIADOS_DECIMALES."""

    codigo: str


def _rechazar_float(valor: object) -> None:
    if isinstance(valor, float):
        raise TypeError("Los importes se manejan con Decimal, nunca con float.")


def parsear_pesos(texto: str) -> Decimal | ErrorImporte:
    """``"1.500,50"`` → ``Decimal("1500.50")``. Hasta dos decimales y mayor o igual a cero."""
    _rechazar_float(texto)
    if not isinstance(texto, str):
        raise TypeError("parsear_pesos recibe un texto.")
    limpio = texto.strip()
    if not limpio:
        return ErrorImporte("VACIO")
    negativo = limpio.startswith("-")
    if negativo:
        limpio = limpio[1:].strip()
    coincidencia = _IMPORTE.match(limpio)
    if not coincidencia:
        return ErrorImporte("NO_NUMERICO")
    decimales = coincidencia.group("decimales")
    if decimales is not None and len(decimales) > 2:
        return ErrorImporte("DEMASIADOS_DECIMALES")
    if negativo:
        return ErrorImporte("NEGATIVO")
    entero = coincidencia.group("entero").replace(".", "")
    return Decimal(f"{entero}.{decimales}" if decimales else entero)


def _formatear_decimal(valor: Decimal) -> str:
    redondeado = valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
    signo = "-" if redondeado < 0 else ""
    entero, decimales = f"{abs(redondeado):.2f}".split(".")
    grupos = []
    while len(entero) > 3:
        grupos.insert(0, entero[-3:])
        entero = entero[:-3]
    grupos.insert(0, entero)
    return f"{signo}{'.'.join(grupos)},{decimales}"


def formatear_pesos(valor: Decimal) -> str:
    """``Decimal("1234567.5")`` → ``"$ 1.234.567,50"``."""
    _rechazar_float(valor)
    if not isinstance(valor, Decimal):
        valor = Decimal(valor)
    return f"$ {_formatear_decimal(valor)}"


def formatear_porcentaje(valor: Decimal) -> str:
    """``Decimal("12.5")`` → ``"12,50 %"``, con redondeo ROUND_HALF_UP (RN-43)."""
    _rechazar_float(valor)
    if not isinstance(valor, Decimal):
        valor = Decimal(valor)
    return f"{_formatear_decimal(valor)} %"


def a_texto_decimal(valor: Decimal | None) -> str | None:
    """Representación sin pérdida para guardar en JSON (``"1500.50"``)."""
    if valor is None:
        return None
    _rechazar_float(valor)
    return str(valor)


def mensaje_error_costo(error: ErrorImporte) -> str:
    """Textos de AC-4.16."""
    if error.codigo == "VACIO":
        return MENSAJES["jugada.costo_vacio"]
    return MENSAJES["jugada.costo_invalido"]


def mensaje_error_importe(error: ErrorImporte) -> str:
    """Texto de un importe de premios inválido en la carga administrativa."""
    if error.codigo == "NEGATIVO":
        return "El importe no puede ser negativo"
    return MENSAJES["jugada.importe_formato"]
