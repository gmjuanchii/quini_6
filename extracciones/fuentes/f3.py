"""Intérprete de F3, quiniya.com.ar ([002] R-04, contracts/fuentes.md → F3).

Solo extrae textos. El bloque ``application/ld+json`` se lee con ``json`` y solo se coteja el
número del sorteo con el del HTML (decisión del responsable del 19/11/2026): si difieren, la
página no se reconoce; si el bloque falta o no se puede leer, no es un error.
Selectores relevados el 19/11/2026.
"""

from __future__ import annotations

import json
import re

from dominio.extraccion.tipos import (
    BloqueCrudo,
    FilaPremioCruda,
    NoReconocida,
    PaginaCruda,
    ReferenciaListado,
)
from extracciones.fuentes.html import Nodo, analizar, bloques_de_datos

_TITULO = re.compile(r"Sorteo\s+(\d+)\b", re.I)
_SORTEADO = re.compile(r"Sorteado el\s+(.+)$", re.I)
_TARJETA = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})\s*#(\d+)")
_RUTA_SORTEO = re.compile(r"^/sorteos/(\d+)$")
_MIGA = re.compile(r"^Sorteo\s+(\d+)$", re.I)


def _numero_del_bloque_de_datos(raiz: Nodo) -> str | None:
    """Número del último elemento "Sorteo N" del ``BreadcrumbList``, o ``None``."""
    for texto in bloques_de_datos(raiz):
        try:
            datos = json.loads(texto)
        except ValueError:
            continue
        numero = None
        pendientes = [datos]
        while pendientes:
            actual = pendientes.pop(0)
            if isinstance(actual, dict):
                nombre = actual.get("name")
                if isinstance(nombre, str) and _MIGA.match(nombre.strip()):
                    numero = _MIGA.match(nombre.strip()).group(1)
                pendientes.extend(actual.values())
            elif isinstance(actual, list):
                pendientes.extend(actual)
        if numero is not None:
            return numero
    return None


def interpretar_sorteo(html: str) -> PaginaCruda | NoReconocida:
    raiz = analizar(html)
    titulo = raiz.buscar("h1")
    numero = _TITULO.search(titulo.texto()) if titulo else None
    fecha = None
    for parrafo in raiz.buscar_todos("p"):
        fecha = _SORTEADO.search(parrafo.texto())
        if fecha:
            break
    if numero is None or fecha is None:
        return NoReconocida("Sin título «Sorteo N» o sin «Sorteado el …»")
    numero_texto = numero.group(1)
    numero_datos = _numero_del_bloque_de_datos(raiz)
    if numero_datos is not None and numero_datos != numero_texto:
        return NoReconocida("El bloque de datos no coincide con el HTML")

    bloques = []
    for numeros in raiz.buscar_todos("div", clase="draw-numbers"):
        if numeros.tiene_clase("draw-numbers--compact"):
            continue
        contenedor = numeros.ancestro("div", clase="shadow")
        rotulo = contenedor.buscar("h2") if contenedor else None
        if rotulo is None:
            continue
        textos = tuple(t for t in (b.texto() for b in numeros.buscar_todos("span", "bolilla")) if t)
        tabla = contenedor.buscar("table")
        filas = None
        if tabla is not None:
            filas = tuple(
                FilaPremioCruda(*(c.texto() for c in celdas[:3]))
                for celdas in (f.celdas() for f in tabla.filas())
                if len(celdas) >= 3 and celdas[1].etiqueta == "td"
            )
        bloques.append(BloqueCrudo(rotulo.texto(), textos, filas))
    return PaginaCruda(numero_texto, fecha.group(1).strip(), tuple(bloques))


def interpretar_listado(html: str) -> list[ReferenciaListado]:
    raiz = analizar(html)
    referencias: dict[str, ReferenciaListado] = {}
    for titulo in raiz.buscar_todos("h3"):
        coincidencia = _TARJETA.search(titulo.texto())
        if coincidencia:
            referencias[coincidencia.group(2)] = ReferenciaListado(
                coincidencia.group(2), coincidencia.group(1)
            )
    for tabla in raiz.buscar_todos("table"):
        for fila in tabla.filas():
            encabezado = fila.buscar("th")
            enlace = fila.buscar("a")
            if encabezado is None or enlace is None:
                continue
            ruta = _RUTA_SORTEO.match(enlace.attr("href"))
            if ruta and ruta.group(1) not in referencias:
                referencias[ruta.group(1)] = ReferenciaListado(ruta.group(1), encabezado.texto())
    return list(referencias.values())
