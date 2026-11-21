"""Ayudas para armar datos de fuentes en las pruebas unitarias de la extracción."""

from dataclasses import replace
from datetime import date

from dominio.extraccion.normalizacion import normalizar
from dominio.extraccion.tipos import DatosFuente, Fuente, Modalidad, ResultadoIntento
from extracciones.fuentes import f1, f2, f3
from extracciones.fuentes.fichas import FICHAS
from tests.extraccion_falsos import leer

FECHAS = {3426: date(2026, 11, 15), 3427: date(2026, 11, 18)}
_INTERPRETES = {Fuente.F1: f1, Fuente.F2: f2, Fuente.F3: f3}


def datos_reales(fuente: Fuente, numero: int = 3426) -> DatosFuente:
    """DatosFuente normalizado a partir de la copia real de la página."""
    html = leer(f"{fuente.value.lower()}/sorteo-{numero}.html")
    pagina = _INTERPRETES[fuente].interpretar_sorteo(html)
    return normalizar(pagina, FICHAS[fuente], numero, FECHAS.get(numero)).datos


def intento(datos: DatosFuente, resultado=ResultadoIntento.OBTENIDO):
    return (datos.fuente, resultado, datos)


def cambiar_categoria(datos: DatosFuente, modalidad: Modalidad, codigo: str, **campos):
    md = datos.modalidades[modalidad]
    categorias = dict(md.categorias)
    categorias[codigo] = replace(categorias[codigo], **campos)
    modalidades = dict(datos.modalidades)
    modalidades[modalidad] = replace(md, categorias=categorias)
    return replace(datos, modalidades=modalidades)


def quitar_categoria(datos: DatosFuente, modalidad: Modalidad, codigo: str):
    md = datos.modalidades[modalidad]
    categorias = {c: v for c, v in md.categorias.items() if c != codigo}
    modalidades = dict(datos.modalidades)
    modalidades[modalidad] = replace(md, categorias=categorias)
    return replace(datos, modalidades=modalidades)


def quitar_modalidad(datos: DatosFuente, modalidad: Modalidad):
    return replace(
        datos, modalidades={m: v for m, v in datos.modalidades.items() if m != modalidad}
    )


def cambiar_numeros(datos: DatosFuente, modalidad: Modalidad, numeros):
    modalidades = dict(datos.modalidades)
    modalidades[modalidad] = replace(modalidades[modalidad], numeros=numeros)
    return replace(datos, modalidades=modalidades)
