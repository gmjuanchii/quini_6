"""Lectura de los catálogos de mensajes de las specs ([003] R-13, contracts/mensajes.md).

Regla (contracts/mensajes.md, "Formato verificable"): una clave por fila; el texto es la celda
"Ahora" (§ 2 y § 3 de [003]) o "Texto" (§ 4 de [003] y catálogos de [001] y [002]) hasta la primera
marca ✓, † o ‡, o la celda completa si no tiene marca.
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO_001 = RAIZ / "specs" / "001-quini6-mvp" / "contracts" / "mensajes.md"
CATALOGO_002 = RAIZ / "specs" / "002-extraccion-historica-csv" / "contracts" / "mensajes.md"
CATALOGO_003 = RAIZ / "specs" / "003-modernizacion-ui-ux" / "contracts" / "mensajes.md"

_MARCA = re.compile(r"\s*[✓†‡].*$")
_CLAVE = re.compile(r"^`([a-z0-9_]+(?:\.[a-z0-9_]+)+)`")


def _celdas(linea: str) -> list[str]:
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def _texto(celda: str) -> str:
    return _MARCA.sub("", celda).strip()


def leer_tabla(ruta: Path, columna: int | None = None) -> dict[str, str]:
    """Devuelve ``clave → texto`` de las tablas cuya primera celda es una clave entre comillas.

    ``columna`` fija el índice de la celda del texto; si es ``None`` se usa la última celda
    antes de "Origen" según el encabezado de cada tabla.
    """
    resultado: dict[str, str] = {}
    indice_texto = columna
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if not linea.startswith("|"):
            continue
        celdas = _celdas(linea)
        if celdas and celdas[0] == "Clave":
            if columna is None:
                encabezados = [c.lower() for c in celdas]
                if "ahora" in encabezados:
                    indice_texto = encabezados.index("ahora")
                else:
                    indice_texto = 1
            continue
        coincidencia = _CLAVE.match(celdas[0]) if celdas else None
        if not coincidencia or indice_texto is None or len(celdas) <= indice_texto:
            continue
        clave = coincidencia.group(1)
        if clave not in resultado:  # las tablas de "heredados" repiten claves
            resultado[clave] = _texto(celdas[indice_texto])
    return resultado


def catalogo_esperado() -> dict[str, str]:
    """Catálogo vigente: [001] y [002], con lo que [003] reescribe o agrega encima."""
    esperado: dict[str, str] = {}
    esperado.update(leer_tabla(CATALOGO_001))
    esperado.update(leer_tabla(CATALOGO_002))
    esperado.update(leer_tabla(CATALOGO_003))
    return esperado
