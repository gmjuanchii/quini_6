"""[003] FR-033, FR-034, SC-010: todos los formularios validan antes de enviar (con las mismas
reglas que el servidor) y muestran el estado de trabajo de su botón principal."""

import re

import pytest

from tests.textos_visibles import plantillas

pytestmark = pytest.mark.django_db

#: Formularios que no son de carga de datos: el selector de tema (se aplica al instante), "Salir" y
#: el filtro de estado de Extracción histórica (se aplica al elegir).
EXENTOS = (
    '{% accion_formulario "/preferencias/tema/" %}',
    '{% accion_formulario "/salir/" %}',
    'id="filtro-estado"',
)
_FORMULARIO = re.compile(r"<form\b[^>]*>.*?</form>", re.S)


def _formularios():
    for ruta in plantillas():
        for m in _FORMULARIO.finditer(ruta.read_text(encoding="utf-8")):
            if not any(e in m.group(0) for e in EXENTOS):
                yield ruta.relative_to(ruta.parents[1]).as_posix(), m.group(0)


def test_fr_033_034_cada_formulario_con_validacion_previa_y_estado_de_trabajo():
    faltan = []
    for ruta, formulario in _formularios():
        apertura = formulario.split(">", 1)[0]
        for atributo in ("novalidate", "data-validar-formulario", "data-trabajando"):
            if atributo not in apertura:
                faltan.append(f"{ruta}: {atributo}")
    assert faltan == []


def test_fr_034_botones_de_envio_con_texto_de_trabajo():
    faltan = []
    for ruta, formulario in _formularios():
        botones = re.findall(r"<button\b[^>]*>", formulario)
        envios = [b for b in botones if 'type="button"' not in b]
        incluidos = re.findall(r'\{%\s*include\s+"ui/_boton\.html"[^%]*%\}', formulario)
        for boton in envios:
            if "data-texto-trabajando" not in boton:
                faltan.append(f"{ruta}: {boton[:90]}")
        for incluido in incluidos:
            if "href=" in incluido or 'tipo="button"' in incluido:
                continue
            if "texto_trabajando=" not in incluido:
                faltan.append(f"{ruta}: {incluido[:90]}")
    assert faltan == []


@pytest.mark.parametrize(
    ("ruta", "perfil"),
    [
        ("/ingresar/", "client"),
        ("/registrarse/", "client"),
        ("/mis-jugadas/nueva/", "cliente_a"),
        ("/administracion/concursos/nuevo/", "cliente_admin"),
        ("/administracion/extracciones/", "cliente_admin"),
        ("/estadisticas/", "client"),
        ("/resultados/", "client"),
    ],
)
def test_sc_010_cada_campo_obligatorio_tiene_sus_reglas(request, ruta, perfil):
    contenido = request.getfixturevalue(perfil).get(ruta).content.decode()
    obligatorios = re.findall(r"<(?:input|select|textarea)\b[^>]*\brequired\b[^>]*>", contenido)
    sin_reglas = [c for c in obligatorios if "data-validar=" not in c]
    assert sin_reglas == []


#: [003] AC-14.4: el único POST de Django que va a Next.js a propósito (reabre el formulario).
SIN_MARCA = ("data-volver-formulario",)


def test_fr_044_todo_formulario_post_lleva_la_marca_de_django():
    """[003] R-20, FR-044: todo formulario POST de Django se envía con ``?_interfaz=django``
    (``{% accion_formulario %}``), así el enrutador lo entrega a Django aunque su ruta ya la
    atienda Next.js (formulario abierto antes de una conmutación o después de una reversa)."""
    faltan = []
    for ruta in plantillas():
        for m in _FORMULARIO.finditer(ruta.read_text(encoding="utf-8")):
            apertura = m.group(0).split(">", 1)[0]
            if 'method="post"' not in apertura.lower() or any(e in apertura for e in SIN_MARCA):
                continue
            if "{% accion_formulario" not in apertura and "accion_inicio" not in apertura:
                faltan.append(f"{ruta.name}: {apertura[:90]}")
            if "hx-post=" in apertura and 'hx-post="{{ accion_inicio }}"' not in apertura:
                faltan.append(f"{ruta.name}: hx-post sin la marca")
    assert faltan == []


@pytest.mark.parametrize(
    ("ruta", "perfil", "accion"),
    [
        ("/ingresar/", "client", "/ingresar/?_interfaz=django"),
        ("/mis-jugadas/nueva/", "cliente_a", "/mis-jugadas/nueva/?_interfaz=django"),
        (
            "/administracion/extracciones/?estado=con-error",
            "cliente_admin",
            "/administracion/extracciones/?estado=con-error&amp;_interfaz=django",
        ),
    ],
)
def test_fr_044_la_marca_conserva_los_parametros(request, ruta, perfil, accion):
    contenido = request.getfixturevalue(perfil).get(ruta).content.decode()
    assert f'action="{accion}"' in contenido
