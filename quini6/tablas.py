"""Tablas ordenables y paginadas ([003] AC-7.5, AC-9.1, AC-9.2, RN-07).

Los encabezados ordenables y la paginación son **enlaces** con parámetros en la dirección: sin
scripts funcionan igual (NFR-007) y el servidor decide el orden en cada pedido. Solo presentación:
ninguna función de este módulo cambia los datos ni las reglas de negocio (NFR-009).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from urllib.parse import urlencode

from django.core.paginator import Paginator


def _pares(parametros) -> list[tuple[str, str]]:
    if hasattr(parametros, "lists"):  # QueryDict: conserva los valores repetidos
        return [(k, v) for k, valores in parametros.lists() for v in valores]
    return [(k, str(v)) for k, v in dict(parametros).items()]


def con_parametros(parametros, **cambios) -> str:
    """``?a=1&b=2`` con ``cambios`` aplicados; un cambio ``None`` o ``""`` quita el parámetro.

    Nunca conserva la marca ``_interfaz`` de los formularios POST ([003] R-20): los enlaces son GET.
    """
    pares = [
        (k, v)
        for k, v in _pares(parametros)
        if k not in cambios and k != "_interfaz" and v != ""
    ]
    pares += [(k, str(v)) for k, v in cambios.items() if v not in (None, "")]
    return "?" + urlencode(pares) if pares else "?"


def orden_valido(valor: str | None, columnas: Iterable[str], por_defecto: str) -> str:
    """``valor`` si es ``col`` o ``-col`` de una columna conocida; si no, ``por_defecto``."""
    valor = (valor or "").strip()
    return valor if valor.lstrip("-") in set(columnas) and valor.count("-") <= 1 else por_defecto


@dataclass(frozen=True)
class Encabezado:
    texto: str
    columna: str
    href: str | None = None
    sentido: str | None = None  # "ascending" | "descending" | None (no ordenada)
    alineacion: str = ""  # "derecha" para cifras

    @property
    def ordenable(self) -> bool:
        return self.href is not None


def encabezados(
    parametros,
    columnas: list[tuple[str, str] | tuple[str, str, str]],
    orden: str,
    ordenables: Iterable[str] | None = None,
) -> list[Encabezado]:
    """Encabezados de una tabla. ``columnas``: ``(columna, texto[, alineacion])``.

    La columna ordenada ofrece el sentido contrario; las demás empiezan en ascendente. Cambiar el
    orden vuelve a la primera página (``pagina`` se quita) y conserva los demás parámetros.
    """
    actual, descendente = orden.lstrip("-"), orden.startswith("-")
    permitidas = set(ordenables) if ordenables is not None else {c[0] for c in columnas}
    resultado = []
    for columna, texto, *resto in columnas:
        alineacion = resto[0] if resto else ""
        if columna not in permitidas:
            resultado.append(Encabezado(texto, columna, alineacion=alineacion))
            continue
        if columna == actual:
            sentido = "descending" if descendente else "ascending"
            siguiente = columna if descendente else f"-{columna}"
        else:
            sentido, siguiente = None, columna
        href = con_parametros(parametros, orden=siguiente, pagina=None)
        resultado.append(Encabezado(texto, columna, href, sentido, alineacion))
    return resultado


@dataclass(frozen=True)
class Pagina:
    """``data-model.md`` § 5: ``Pagina<T>`` (elementos, pagina, paginas, total, orden, filtro)."""

    elementos: list
    pagina: int
    paginas: int
    total: int
    orden: str = ""
    filtro: object = None
    tiene_anterior: bool = False
    tiene_siguiente: bool = False


TAMANO_PAGINA = 20  # RN-07


def paginar(elementos, numero, orden: str = "", filtro=None, tamano: int = TAMANO_PAGINA) -> Pagina:
    """Página ``numero`` (1 si no es un entero; fuera de rango → la última con datos, AC-9.2)."""
    paginador = Paginator(elementos, tamano)
    try:
        pedido = int(numero)
    except (TypeError, ValueError):
        pedido = 1
    pagina = paginador.get_page(max(pedido, 1))
    return Pagina(
        elementos=list(pagina.object_list),
        pagina=pagina.number,
        paginas=paginador.num_pages,
        total=paginador.count,
        orden=orden,
        filtro=filtro,
        tiene_anterior=pagina.has_previous(),
        tiene_siguiente=pagina.has_next(),
    )


def parametros_de(valores: Mapping[str, object]) -> dict[str, str]:
    """Diccionario de parámetros sin los vacíos (para armar los enlaces de una consulta válida)."""
    return {k: str(v) for k, v in valores.items() if v not in (None, "")}
