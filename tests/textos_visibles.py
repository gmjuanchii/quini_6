"""Texto visible de las plantillas, para las pruebas de lenguaje ([003] HU-11, AC-11.1 a AC-11.3).

Aproximación estática: se quitan los comentarios, las etiquetas de plantilla y de HTML y los valores
de atributos que no se muestran (``class``, ``id``, ``href``, ``name``…); se conservan los atributos
que sí se leen (``aria-label``, ``title``, ``placeholder``, ``alt``) y el texto entre etiquetas.
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PLANTILLAS = RAIZ / "templates"
SCRIPTS = RAIZ / "static" / "js"

_COMENTARIOS = [
    re.compile(r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", re.S),
    re.compile(r"\{#.*?#\}", re.S),
    re.compile(r"<!--.*?-->", re.S),
]
_BLOQUES_OCULTOS = re.compile(r"<(script|style|svg)\b.*?</\1>", re.S | re.I)
_ATRIBUTOS_LEIDOS = re.compile(r'\b(aria-label|title|placeholder|alt)="([^"]*)"')
_ETIQUETA_PLANTILLA = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.S)
_ETIQUETA_HTML = re.compile(r"<[^>]+>")


def texto_visible(fuente: str) -> str:
    for patron in _COMENTARIOS:
        fuente = patron.sub(" ", fuente)
    fuente = _BLOQUES_OCULTOS.sub(" ", fuente)
    leidos = " ".join(valor for _, valor in _ATRIBUTOS_LEIDOS.findall(fuente))
    fuente = _ETIQUETA_PLANTILLA.sub(" 0 ", fuente)  # una variable cuenta como un valor
    fuente = _ETIQUETA_HTML.sub(" ", fuente)
    return re.sub(r"\s+", " ", f"{fuente} {_ETIQUETA_PLANTILLA.sub(' ', leidos)}").strip()


def plantillas() -> list[Path]:
    return sorted(p for p in PLANTILLAS.rglob("*.html") if "iconos" not in p.parts)


_CADENA_JS = re.compile(r"""(["'])((?:\\.|(?!\1).)*)\1""")
_COMENTARIO_JS = re.compile(r"/\*.*?\*/|(?<![:\"'])//[^\n]*", re.S)


def cadenas_js(fuente: str) -> list[str]:
    """Cadenas literales de un script, sin comentarios, que pueden ser textos visibles: las que
    tienen un espacio (las demás son nombres, selectores CSS o claves)."""
    cadenas = [m.group(2) for m in _CADENA_JS.finditer(_COMENTARIO_JS.sub(" ", fuente))]
    return [c for c in cadenas if " " in c.strip()]
