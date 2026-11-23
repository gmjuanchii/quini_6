"""[003] HU-11: lenguaje de interfaz uniforme (AC-11.1, AC-11.3, SC-007, D-01, D-04, RN-10;
contracts/mensajes.md § 1.5).

Busca en el catálogo, en el texto visible de las plantillas y en las cadenas de los scripts las
formas prohibidas: voseo, tuteo o posesivos de segunda persona, "concurso" y "extracción" suelta
(fuera de "Extracción histórica" y de los textos de estado de [002]).
"""

import re

import pytest

from dominio.mensajes import MENSAJES
from tests.textos_visibles import SCRIPTS, cadenas_js, plantillas, texto_visible

VOSEO = re.compile(
    r"\b(tenés|podés|querés|elegís|buscás|ingresá|elegí|creá|corregí|verificá|intentá|registrá|"
    r"registraste|iniciá|escribí|volvé|indicaste|hiciste|indicá)\b",
    re.I,
)
SEGUNDA_PERSONA = re.compile(r"\b(tus?|te)\b", re.I)
CONCURSO = re.compile(r"\bconcursos?\b", re.I)
EXTRACCION = re.compile(r"\bextracci[oó]n(es)?\b", re.I)
#: "extracción" permitida: el nombre de la sección y los textos de estado de [002].
EXTRACCION_PERMITIDA = re.compile(
    r"extracci[oó]n(es)? hist[oó]rica|extracci[oó]n finalizada|extracci[oó]n en curso|"
    r"(la|una|otra|cada|esta|esa|de la|del|iniciar|eliminar) extracci[oó]n|"
    r"(hay|las) extracciones|extracciones (anteriores|terminadas)|"
    r"extracci[oó]n del \{fecha_hora\}|extracci[oó]n del \d",
    re.I,
)


#: Textos aprobados de [002] que usan "extracciones" por números sorteados (RN-10); cambiarlos
#: exige la aprobación del responsable (Const. I). Pendiente informado el 21/11/2026.
EXCEPCIONES_PENDIENTES = {"obs.premio_extra_no_coincide"}


def prohibidas(texto: str) -> list[str]:
    encontradas = [
        m.group(0) for p in (VOSEO, SEGUNDA_PERSONA, CONCURSO) for m in p.finditer(texto)
    ]
    limpio = EXTRACCION_PERMITIDA.sub(" ", texto)
    encontradas += [m.group(0) for m in EXTRACCION.finditer(limpio)]
    return encontradas


def test_el_detector_encuentra_las_formas_prohibidas():
    assert prohibidas("Elegí tu concurso") == ["Elegí", "tu", "concurso"]
    assert prohibidas("Extracción histórica de sorteos") == []
    assert prohibidas("Ver la extracción del 21/11/2026 12:15") == []
    assert prohibidas("Extracción de números") == ["Extracción"]


@pytest.mark.parametrize("clave", sorted(set(MENSAJES) - EXCEPCIONES_PENDIENTES))
def test_ac_11_1_catalogo_sin_formas_prohibidas(clave):
    assert prohibidas(MENSAJES[clave]) == [], clave


def test_ac_11_1_plantillas_sin_formas_prohibidas():
    apariciones = {}
    for ruta in plantillas():
        encontradas = prohibidas(texto_visible(ruta.read_text(encoding="utf-8")))
        if encontradas:
            apariciones[str(ruta.relative_to(ruta.parents[1]))] = encontradas
    assert apariciones == {}


def test_ac_11_1_scripts_sin_formas_prohibidas():
    apariciones = {}
    for ruta in sorted(SCRIPTS.glob("*.js")):
        encontradas = [
            p for c in cadenas_js(ruta.read_text(encoding="utf-8")) for p in prohibidas(c)
        ]
        if encontradas:
            apariciones[ruta.name] = encontradas
    assert apariciones == {}
