"""Árbol mínimo de HTML sobre ``html.parser`` ([002] R-04, NFR-010).

El HTML de las fuentes es un dato no confiable: no se ejecuta JavaScript, no se siguen enlaces
y nunca se lanza una excepción ante HTML malformado. No importa Django.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from html.parser import HTMLParser

_VACIAS = frozenset("area base br col embed hr img input link meta param source track wbr".split())
#: Etiquetas que se cierran solas al abrir otra igual o un contenedor de la tabla.
_CIERRE_IMPLICITO = {
    "p": {"p", "div", "table", "h1", "h2", "h3", "h4", "ul", "ol"},
    "li": {"li"},
    "tr": {"tr"},
    "td": {"td", "th", "tr"},
    "th": {"td", "th", "tr"},
    "option": {"option"},
}
_SIN_TEXTO = frozenset({"script", "style", "template", "noscript"})
_ESPACIOS = re.compile(r"\s+")


class Nodo:
    __slots__ = ("etiqueta", "atributos", "hijos", "padre")

    def __init__(self, etiqueta: str, atributos: dict[str, str] | None = None, padre=None):
        self.etiqueta = etiqueta
        self.atributos = atributos or {}
        self.hijos: list[Nodo | str] = []
        self.padre: Nodo | None = padre

    # -- atributos ---------------------------------------------------------
    def attr(self, nombre: str, defecto: str = "") -> str:
        return self.atributos.get(nombre, defecto) or defecto

    @property
    def clases(self) -> frozenset[str]:
        return frozenset(self.attr("class").split())

    def tiene_clase(self, clase: str) -> bool:
        return clase in self.clases

    # -- recorrido ---------------------------------------------------------
    @property
    def elementos(self) -> list[Nodo]:
        return [h for h in self.hijos if isinstance(h, Nodo)]

    def descendientes(self) -> Iterator[Nodo]:
        for hijo in self.elementos:
            yield hijo
            yield from hijo.descendientes()

    def buscar_todos(
        self, etiqueta: str | None = None, clase: str | None = None, id: str | None = None
    ) -> list[Nodo]:
        return [n for n in self.descendientes() if _coincide(n, etiqueta, clase, id)]

    def buscar(
        self, etiqueta: str | None = None, clase: str | None = None, id: str | None = None
    ) -> Nodo | None:
        for nodo in self.descendientes():
            if _coincide(nodo, etiqueta, clase, id):
                return nodo
        return None

    def ancestro(self, etiqueta: str | None = None, clase: str | None = None) -> Nodo | None:
        actual = self.padre
        while actual is not None:
            if _coincide(actual, etiqueta, clase, None):
                return actual
            actual = actual.padre
        return None

    def siguiente_elemento(self) -> Nodo | None:
        if self.padre is None:
            return None
        hermanos = self.padre.elementos
        for i, hermano in enumerate(hermanos):
            if hermano is self:
                return hermanos[i + 1] if i + 1 < len(hermanos) else None
        return None

    # -- texto ---------------------------------------------------------------
    def texto_crudo(self) -> str:
        """Texto sin normalizar, incluido el de ``<script>`` (para bloques de datos)."""
        partes: list[str] = []
        for hijo in self.hijos:
            partes.append(hijo if isinstance(hijo, str) else hijo.texto_crudo())
        return "".join(partes)

    def texto(self) -> str:
        """Texto visible con espacios normalizados; ``<br>`` cuenta como espacio."""
        return _ESPACIOS.sub(" ", self._texto()).strip()

    def _texto(self) -> str:
        if self.etiqueta in _SIN_TEXTO:
            return ""
        if self.etiqueta == "br":
            return " "
        partes: list[str] = []
        for hijo in self.hijos:
            partes.append(hijo if isinstance(hijo, str) else " " + hijo._texto() + " ")
        return "".join(partes)

    # -- tablas --------------------------------------------------------------
    def filas(self) -> list[Nodo]:
        """Filas ``<tr>`` de una tabla, sin entrar en tablas anidadas."""
        resultado: list[Nodo] = []

        def recorrer(nodo: Nodo):
            for hijo in nodo.elementos:
                if hijo.etiqueta == "tr":
                    resultado.append(hijo)
                elif hijo.etiqueta != "table":
                    recorrer(hijo)

        recorrer(self)
        return resultado

    def celdas(self) -> list[Nodo]:
        return [h for h in self.elementos if h.etiqueta in ("td", "th")]

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuración
        return f"<Nodo {self.etiqueta} {self.atributos}>"


def _coincide(nodo: Nodo, etiqueta, clase, id) -> bool:
    if etiqueta is not None and nodo.etiqueta != etiqueta:
        return False
    if clase is not None and not nodo.tiene_clase(clase):
        return False
    if id is not None and nodo.attr("id") != id:
        return False
    return True


class _Constructor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raiz = Nodo("#documento")
        self.actual = self.raiz

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        cerrables = {t for t, abiertos in _CIERRE_IMPLICITO.items() if tag in abiertos}
        while self.actual is not self.raiz and self.actual.etiqueta in cerrables:
            # <td> dentro de otra <td> de la misma fila, <p> dentro de <p>, etc.
            if self.actual.etiqueta in ("td", "th") and tag not in ("td", "th", "tr"):
                break
            self.actual = self.actual.padre
        nodo = Nodo(tag, {k.lower(): (v or "") for k, v in attrs}, self.actual)
        self.actual.hijos.append(nodo)
        if tag not in _VACIAS:
            self.actual = nodo

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        nodo = Nodo(tag, {k.lower(): (v or "") for k, v in attrs}, self.actual)
        self.actual.hijos.append(nodo)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _VACIAS:
            return
        nodo = self.actual
        while nodo is not self.raiz and nodo.etiqueta != tag:
            nodo = nodo.padre
        if nodo is self.raiz:
            return  # cierre sin apertura: se ignora
        self.actual = nodo.padre

    def handle_data(self, data):
        if data:
            self.actual.hijos.append(data)


def analizar(html: str) -> Nodo:
    """Devuelve la raíz del árbol. Nunca lanza una excepción por HTML malformado."""
    constructor = _Constructor()
    try:
        constructor.feed(html or "")
        constructor.close()
    except Exception:  # noqa: BLE001 - HTML no confiable: se conserva lo leído hasta el error
        pass
    return constructor.raiz


def bloques_de_datos(raiz: Nodo, tipo: str = "application/ld+json") -> list[str]:
    """Texto crudo de los bloques ``<script type=…>`` de datos, sin ejecutarlos."""
    return [
        nodo.texto_crudo()
        for nodo in raiz.buscar_todos("script")
        if nodo.attr("type").strip().lower() == tipo
    ]
