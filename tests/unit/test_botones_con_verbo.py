"""[003] HU-11: botones con verbo inicial en infinitivo, nunca "Aceptar" ni "OK" (AC-11.2, FR-035;
contracts/mensajes.md § 1.3).

Recorre las plantillas y reúne el texto de cada botón: ``<button>``, enlaces con el estilo de botón
(``class="boton…"`` o ``{% clases "boton" %}``) y los ``{% include "ui/_boton.html" … %}``.
Los textos que vienen del catálogo (``{% msg "clave" %}`` o ``{% msg "clave" as nombre %}``) se
resuelven con ``dominio.mensajes``.
"""

import re

from dominio.mensajes import MENSAJES
from tests.textos_visibles import plantillas

VERBOS = {
    # Lista de T112.
    "Ingresar",
    "Crear",
    "Registrar",
    "Iniciar",
    "Consultar",
    "Eliminar",
    "Cancelar",
    "Guardar",
    "Descargar",
    "Cargar",
    "Publicar",
    "Ver",
    "Volver",
    "Limpiar",
    "Mostrar",
    "Ocultar",
    "Reintentar",
    "Cerrar",
    "Salir",
    "Abrir",
    "Modificar",
    "Corregir",
    "Resolver",
    "Observar",
    "Quitar",
    "Buscar",
    # Verbos en infinitivo que ya usan los botones aprobados de [001] y [002].
    "Filtrar",
    "Agregar",
    "Revisar",
    "Editar",
    "Marcar",
    "Poner",
}
PROHIBIDOS = {"Aceptar", "OK", "Ok"}

_MSG = re.compile(r"""\{%\s*msg\s+["']([\w.]+)["'][^%]*%\}""")
_MSG_AS = re.compile(r"""\{%\s*msg\s+["']([\w.]+)["'][^%]*\bas\s+(\w+)\s*%\}""")
_BOTON = re.compile(r"<button\b[^>]*>(.*?)</button>", re.S)
_ENLACE_BOTON = re.compile(
    r"""<a\b[^>]*class="[^"]*(?:\bboton\b|\{%\s*clases\s+['"]boton['"])[^"]*"[^>]*>(.*?)</a>""",
    re.S,
)
_INCLUDE_BOTON = re.compile(r"""\{%\s*include\s+["']ui/_boton\.html["']\s+with\s+([^%]*)%\}""")
_TEXTO_ARG = re.compile(r"""\btexto=(?:"([^"]*)"|'([^']*)'|([\w.]+))""")


def _resolver(contenido: str, fragmento: str, alias: dict[str, str]) -> str:
    fragmento = _MSG.sub(lambda m: MENSAJES[m.group(1)], fragmento)
    fragmento = re.sub(r"<svg\b.*?</svg>", " ", fragmento, flags=re.S)
    fragmento = re.sub(r'<span class="visualmente-oculto">.*?</span>', " ", fragmento, flags=re.S)
    fragmento = re.sub(r"\{%\s*icono[^%]*%\}", " ", fragmento)
    # Un {% if %}…{% else %}…{% endif %} con dos textos: se revisan los dos.
    fragmento = re.sub(r"\{%\s*(if|elif|else|endif)[^%]*%\}", " | ", fragmento)
    fragmento = re.sub(r"\{\{\s*(\w+)\s*\}\}", lambda m: alias.get(m.group(1), " "), fragmento)
    fragmento = re.sub(r"\{%.*?%\}|\{\{.*?\}\}|<[^>]+>", " ", fragmento, flags=re.S)
    return fragmento


def textos_de_botones(contenido: str) -> list[str]:
    alias = {nombre: MENSAJES[clave] for clave, nombre in _MSG_AS.findall(contenido)}
    textos = []
    for patron in (_BOTON, _ENLACE_BOTON):
        for m in patron.finditer(contenido):
            apertura = m.group(0).split(">", 1)[0]
            if "aria-expanded" in apertura or "aria-haspopup" in apertura:
                continue  # despliegan ("Menú", cuenta, calendario): no son acciones
            textos += _resolver(contenido, m.group(1), alias).split("|")
    for m in _INCLUDE_BOTON.finditer(contenido):
        arg = _TEXTO_ARG.search(m.group(1))
        if not arg:
            continue
        literal = arg.group(1) or arg.group(2)
        if literal is not None:
            textos.append(literal)
        elif arg.group(3) in alias:
            textos.append(alias[arg.group(3)])
    return [re.sub(r"\s+", " ", t).strip() for t in textos if t.strip()]


def test_resolucion_de_textos():
    contenido = (
        '{% msg "admin.crear" as crear %}<button type="submit">{% icono "plus" %}Guardar</button>'
        '{% include "ui/_boton.html" with texto=crear %}'
        '<a class="boton" href="/">{% if a %}Ver más{% else %}Volver{% endif %}</a>'
    )
    assert textos_de_botones(contenido) == ["Guardar", "Ver más", "Volver", "Cargar sorteo"]


def test_ac_11_2_botones_empiezan_con_un_verbo_permitido():
    malos = {}
    for ruta in plantillas():
        for texto in textos_de_botones(ruta.read_text(encoding="utf-8")):
            primera = texto.split()[0].strip("¿¡")
            if primera in PROHIBIDOS or primera not in VERBOS:
                malos.setdefault(ruta.name, []).append(texto)
    assert malos == {}
