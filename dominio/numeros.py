"""Números de jugadas y extracciones (RN-01 a RN-03, RN-14, RN-31).

Los errores se devuelven como valores (``ErrorNumero``), no como excepciones.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Numeros

MINIMO = 0
MAXIMO = 45
CANTIDAD = 6

_ENTERO = re.compile(r"^[+-]?\d+$")


@dataclass(frozen=True)
class ErrorNumero:
    """Códigos: FUERA_DE_RANGO, NO_NUMERICO, FALTAN_N, SOBRAN, REPETIDO."""

    codigo: str
    numero: int | None = None
    cantidad: int | None = None


def parsear_numero(texto: str | int) -> int | ErrorNumero:
    """Convierte ``"07"`` en 7. Rechaza valores no numéricos o fuera de 00 a 45 (AC-4.4)."""
    if isinstance(texto, bool):
        return ErrorNumero("NO_NUMERICO")
    if isinstance(texto, int):
        valor = texto
    else:
        limpio = str(texto).strip()
        if not _ENTERO.match(limpio):
            return ErrorNumero("NO_NUMERICO")
        valor = int(limpio)
    if valor < MINIMO or valor > MAXIMO:
        return ErrorNumero("FUERA_DE_RANGO")
    return valor


def _validar_seis(valores: Iterable[str | int]) -> Numeros | list[ErrorNumero]:
    lista = list(valores)
    errores: list[ErrorNumero] = []
    validos: list[int] = []
    for valor in lista:
        resultado = parsear_numero(valor)
        if isinstance(resultado, ErrorNumero):
            if resultado not in errores:
                errores.append(resultado)
        else:
            validos.append(resultado)

    vistos: set[int] = set()
    for numero in validos:
        if numero in vistos:
            error = ErrorNumero("REPETIDO", numero=numero)
            if error not in errores:
                errores.append(error)
        vistos.add(numero)

    if len(lista) < CANTIDAD:
        errores.append(ErrorNumero("FALTAN_N", cantidad=CANTIDAD - len(lista)))
    elif len(lista) > CANTIDAD:
        errores.append(ErrorNumero("SOBRAN"))

    if errores:
        return errores
    return frozenset(validos)


def validar_jugada(valores: Iterable[str | int]) -> Numeros | list[ErrorNumero]:
    """Exactamente seis números distintos de 00 a 45 (RN-01 a RN-03; AC-4.2 a AC-4.5)."""
    return _validar_seis(valores)


def validar_extraccion(valores: Iterable[str | int]) -> Numeros | list[ErrorNumero]:
    """Seis números distintos de 00 a 45 de una extracción (RN-14; AC-2.3)."""
    return _validar_seis(valores)


def formatear(n: int) -> str:
    """RN-01: siempre con dos dígitos."""
    return f"{int(n):02d}"


def misma_combinacion(a: Iterable[int], b: Iterable[int]) -> bool:
    """RN-06: los mismos seis números, sin importar el orden."""
    return frozenset(a) == frozenset(b)


def conjunto_premio_extra(
    primer_sorteo: Numeros, la_segunda: Numeros, revancha: Numeros
) -> Numeros:
    """RN-31: unión sin repetidos de las tres extracciones. Nunca incluye Siempre Sale."""
    return frozenset(primer_sorteo) | frozenset(la_segunda) | frozenset(revancha)


def mensaje_error(error: ErrorNumero) -> str:
    """Texto visible de cada error (contracts/mensajes.md, "Jugadas")."""
    if error.codigo == "FALTAN_N":
        return mensaje("jugada.faltan", n=error.cantidad)
    if error.codigo == "SOBRAN":
        return MENSAJES["jugada.exactamente_seis"]
    if error.codigo == "REPETIDO":
        return mensaje("jugada.repetido", nn=formatear(error.numero or 0))
    return MENSAJES["jugada.fuera_de_rango"]


def mensaje_error_extraccion(error: ErrorNumero) -> str:
    """Texto visible de cada error al cargar una extracción (AC-2.3)."""
    if error.codigo == "FALTAN_N":
        return f"Faltan {error.cantidad} números: los números sorteados son exactamente seis"
    if error.codigo == "SOBRAN":
        return "Los números sorteados son exactamente seis"
    if error.codigo == "REPETIDO":
        return mensaje("admin.numero_repetido", nn=formatear(error.numero or 0))
    return MENSAJES["admin.numeros_rango"]
