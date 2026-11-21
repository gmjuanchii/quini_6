"""Intérprete de F1, quini-6-resultados.com.ar ([002] R-04, contracts/fuentes.md → F1).

Solo extrae textos. F1 presenta cada modalidad en dos bloques: los números (``h3.verdeyblanco``
y ``p.numeros``) y los premios (una tabla con filas ``tr.verde`` que abren cada bloque). El pozo
de Premio Extra viene entre paréntesis en su rótulo. Selectores relevados el 19/11/2026.
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

_ENCABEZADO = re.compile(r"Sorteo\s+Nro\.?\s*(?P<numero>\S+)\s+del\s+d[ií]a\s+(?P<fecha>.+)$", re.I)
_ROTULO_CON_POZO = re.compile(r"^(?P<rotulo>.*?)\s*\((?P<pozo>[^)]*)\)\s*$")
_LISTADO = re.compile(r"Sorteo\s+(\d+)\s+del\s+(\d{1,2}-\d{1,2}-\d{4})", re.I)
_RUTA_SORTEO = re.compile(r"/quini6/sorteo-\d+-del-dia-\d{2}-\d{2}-\d{4}\.htm$")


def interpretar_sorteo(html: str) -> PaginaCruda | NoReconocida:
    raiz = analizar(html)
    encabezado = None
    for titulo in raiz.buscar_todos("h2"):
        encabezado = _ENCABEZADO.search(titulo.texto())
        if encabezado:
            break
    if encabezado is None:
        return NoReconocida("Sin «Sorteo Nro. N del dia …»")

    bloques: list[BloqueCrudo] = []
    for titulo in raiz.buscar_todos("h3", clase="verdeyblanco"):
        texto = titulo.texto()
        pozo = None
        con_pozo = _ROTULO_CON_POZO.match(texto)
        if con_pozo:
            texto, pozo = con_pozo.group("rotulo"), con_pozo.group("pozo")
        siguiente = titulo.siguiente_elemento()
        numeros = None
        if siguiente is not None and siguiente.etiqueta == "p" and siguiente.tiene_clase("numeros"):
            numeros = (siguiente.texto(),)
        bloques.append(BloqueCrudo(texto, numeros, None, pozo))

    for tabla in raiz.buscar_todos("table"):
        rotulo = None
        filas: list[FilaPremioCruda] = []
        for fila in tabla.filas():
            etiqueta = fila.buscar("span", clase="lblSorteo")
            if fila.tiene_clase("verde") and etiqueta is not None:
                if rotulo is not None:
                    bloques.append(BloqueCrudo(rotulo, None, tuple(filas)))
                rotulo, filas = etiqueta.texto(), []
                continue
            celdas = fila.celdas()
            if rotulo is not None and len(celdas) >= 3:
                filas.append(FilaPremioCruda(*(c.texto() for c in celdas[:3])))
        if rotulo is not None:
            bloques.append(BloqueCrudo(rotulo, None, tuple(filas)))

    return PaginaCruda(
        numero_texto=encabezado.group("numero"),
        fecha_texto=encabezado.group("fecha").strip(),
        bloques=tuple(bloques),
    )


def interpretar_listado(html: str) -> list[ReferenciaListado]:
    raiz = analizar(html)
    referencias = []
    for enlace in raiz.buscar_todos("a"):
        if not _RUTA_SORTEO.search(enlace.attr("href")):
            continue
        coincidencia = _LISTADO.search(enlace.texto())
        if coincidencia:
            referencias.append(ReferenciaListado(coincidencia.group(1), coincidencia.group(2)))
    return referencias
