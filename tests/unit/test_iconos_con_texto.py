"""[003] HU-13: los iconos nunca reemplazan al texto (AC-13.5, NFR-003; componentes.md § 2).

En las plantillas, todo ``{% icono %}`` dentro de un ``<button>``, ``<a>`` o ``<summary>`` convive
con texto visible o con un nombre accesible (``aria-label`` o texto ``visualmente-oculto``). El ⋮
del menú de acciones es el único sin texto visible, y siempre con nombre accesible.
"""

import re

from tests.textos_visibles import plantillas

_CONTROL = re.compile(r"<(button|a|summary)\b([^>]*)>(.*?)</\1>", re.S)


def _tiene_texto(contenido: str) -> bool:
    sin_iconos = re.sub(r"\{%\s*icono[^%]*%\}", " ", contenido)
    if re.search(r"\{%\s*msg\b|\{\{.*?\}\}", sin_iconos):
        return True  # texto del catálogo o de una variable
    visible = re.sub(r"\{%.*?%\}|<[^>]+>", " ", sin_iconos, flags=re.S)
    return bool(visible.strip())


def controles_con_icono_sin_nombre(fuente: str) -> list[str]:
    malos = []
    for m in _CONTROL.finditer(fuente):
        atributos, contenido = m.group(2), m.group(3)
        if "{% icono" not in contenido:
            continue
        if "aria-label=" in atributos or "visualmente-oculto" in contenido:
            continue
        if not _tiene_texto(contenido):
            malos.append(m.group(0)[:120])
    return malos


def test_el_detector():
    assert controles_con_icono_sin_nombre('<button>{% icono "x" %}</button>')
    assert not controles_con_icono_sin_nombre('<button>{% icono "x" %}Cerrar</button>')
    assert not controles_con_icono_sin_nombre('<a aria-label="Menú">{% icono "menu" %}</a>')
    assert not controles_con_icono_sin_nombre(
        '<button>{% icono "calendar" %}<span class="visualmente-oculto">Abrir</span></button>'
    )


def test_ac_13_5_iconos_siempre_con_texto_o_nombre_accesible():
    malos = {}
    for ruta in plantillas():
        encontrados = controles_con_icono_sin_nombre(ruta.read_text(encoding="utf-8"))
        if encontrados:
            malos[ruta.name] = encontrados
    assert malos == {}
