"""Intérprete de F2, numerosganadores.com.ar ([002] R-04, contracts/fuentes.md → F2).

Solo extrae textos: no interpreta valores ni lanza excepciones ante HTML inesperado.
Selectores relevados el 19/11/2026.
"""

from __future__ import annotations

import re

from dominio.extraccion.tipos import (
    BloqueCrudo,
    FilaPremioCruda,
    NoReconocida,
    PaginaCruda,
    ReferenciaListado,
)
from extracciones.fuentes.html import analizar

_ENCABEZADO = re.compile(
    r"Fecha del sorteo:\s*(?P<fecha>[^;]+);\s*N[úu]mero de sorteo:\s*(?P<numero>\S+)", re.I
)
_LISTADO = re.compile(r"Sorteo\s+(\d+)\s+(\d{1,2}/\d{1,2}/\d{4})", re.I)
_RUTA_SORTEO = re.compile(r"^/sorteos/\d+$")


def interpretar_sorteo(html: str) -> PaginaCruda | NoReconocida:
    raiz = analizar(html)
    encabezado = None
    for parrafo in raiz.buscar_todos("p", clase="lead"):
        encabezado = _ENCABEZADO.search(parrafo.texto())
        if encabezado:
            break
    if encabezado is None:
        return NoReconocida("Sin «Fecha del sorteo; Número de sorteo»")

    bloques = []
    for tarjeta in raiz.buscar_todos("div", clase="card"):
        titulo = tarjeta.buscar("h3", clase="card-title")
        if titulo is None:
            continue
        contenedor_numeros = tarjeta.buscar("p", clase="h2")
        numeros = None
        if contenedor_numeros is not None:
            numeros = tuple(
                texto
                for texto in (b.texto() for b in contenedor_numeros.buscar_todos("span", "badge"))
                if texto
            )
        tabla = tarjeta.buscar("table")
        filas = None
        if tabla is not None:
            filas = tuple(
                FilaPremioCruda(*(c.texto() for c in celdas[:3]))
                for celdas in (f.celdas() for f in tabla.filas())
                if len(celdas) >= 3 and all(c.etiqueta == "td" for c in celdas)
            )
        bloques.append(BloqueCrudo(titulo.texto(), numeros, filas))
    return PaginaCruda(
        numero_texto=encabezado.group("numero").strip(),
        fecha_texto=encabezado.group("fecha").strip(),
        bloques=tuple(bloques),
    )


def interpretar_listado(html: str) -> list[ReferenciaListado]:
    raiz = analizar(html)
    referencias = []
    for enlace in raiz.buscar_todos("a"):
        if not _RUTA_SORTEO.match(enlace.attr("href")):
            continue
        coincidencia = _LISTADO.search(enlace.texto())
        if coincidencia:
            referencias.append(ReferenciaListado(coincidencia.group(1), coincidencia.group(2)))
    return referencias
