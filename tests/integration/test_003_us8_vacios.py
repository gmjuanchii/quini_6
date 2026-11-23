"""[003] HU-08: estados vacíos que orientan (AC-8.1 a AC-8.4, FR-025, FR-026, RN-06)."""

import html
import re
from datetime import date

import pytest

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Modalidad
from tests.extraccion_estados import crear_extraccion
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db


def _vacio(contenido: str) -> dict:
    """El estado vacío de la página: variante, icono, título, texto y enlaces."""
    m = re.search(
        r'<div\b[^>]*data-estado-vacio="([\w_]+)"[^>]*data-icono-vacio="([\w-]+)"[^>]*>(.*?)'
        r"<!-- /estado-vacio -->",
        contenido,
        re.S,
    )
    assert m, "no hay estado vacío"
    cuerpo = m.group(3)
    titulo = re.search(r"<h2\b[^>]*>(.*?)</h2>", cuerpo, re.S)
    enlaces = re.findall(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>', cuerpo, re.S)
    return {
        "variante": m.group(1),
        "icono": m.group(2),
        "titulo": _texto(titulo.group(1)) if titulo else "",
        "texto": _texto(cuerpo),
        "enlaces": {_texto(t): html.unescape(h) for h, t in enlaces},
    }


def _texto(fragmento: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def test_ac_8_2_mis_jugadas_sin_jugadas(cliente_a):
    vacio = _vacio(cliente_a.get("/mis-jugadas/").content.decode())
    assert vacio["variante"] == "sin_datos" and vacio["icono"] == "ticket"
    assert vacio["titulo"] == MENSAJES["vacio.jugadas.titulo"]
    assert MENSAJES["vacio.jugadas.explicacion"] in vacio["texto"]
    assert vacio["enlaces"] == {MENSAJES["vacio.jugadas.accion"]: "/mis-jugadas/nueva/"}


@pytest.mark.parametrize("perfil", ["visitante", "usuario"])
def test_ac_8_4_resultados_sin_sorteos_sin_accesos(client, cliente_a, perfil):
    cliente = client if perfil == "visitante" else cliente_a
    contenido = cliente.get("/resultados/").content.decode()
    vacio = _vacio(contenido)
    assert vacio["variante"] == "sin_datos"
    assert vacio["titulo"] == MENSAJES["vacio.resultados.titulo"]
    assert MENSAJES["vacio.resultados.explicacion"] in vacio["texto"]
    assert vacio["enlaces"] == {}
    assert MENSAJES["vacio.resultados_nota_admin"] not in contenido
    assert contenido.count("data-estado-vacio=") == 1  # un único estado vacío


def test_ac_8_4_resultados_sin_sorteos_con_accesos_de_administracion(cliente_admin):
    vacio = _vacio(cliente_admin.get("/resultados/").content.decode())
    assert vacio["enlaces"] == {
        MENSAJES["vacio.resultados.accion_cargar"]: "/administracion/concursos/nuevo/",
        MENSAJES["vacio.resultados.accion_extraccion"]: "/administracion/extracciones/",
    }
    assert MENSAJES["vacio.resultados_nota_admin"] in vacio["texto"]


def test_ac_8_1_extraccion_historica_sin_extracciones(cliente_admin):
    vacio = _vacio(cliente_admin.get("/administracion/extracciones/").content.decode())
    assert vacio["variante"] == "sin_datos"
    assert vacio["titulo"] == MENSAJES["vacio.extracciones.titulo"]
    assert MENSAJES["vacio.extracciones.explicacion"] in vacio["texto"]


def test_ac_8_3_filtro_de_extracciones_sin_resultados(cliente_admin, admin):
    crear_extraccion(admin, "finalizada")
    contenido = cliente_admin.get("/administracion/extracciones/?estado=con-advertencias")
    vacio = _vacio(contenido.content.decode())
    assert vacio["variante"] == "sin_resultados" and vacio["icono"] == "filter-x"
    assert vacio["titulo"] == MENSAJES["vacio.filtro.titulo"]
    filtro = MENSAJES["etiqueta.con_advertencias"]
    assert mensaje("vacio.filtro.explicacion", filtro=filtro) in vacio["texto"]
    assert vacio["enlaces"] == {MENSAJES["vacio.filtro.accion"]: "/administracion/extracciones/"}


@pytest.mark.parametrize("parametros", [{"numero": "9999"}, {"fecha": "01/01/2020"}])
def test_ac_8_3_busqueda_sin_coincidencias(client, parametros):
    crear_concurso(3300, date(2025, 3, 2))
    vacio = _vacio(client.get("/resultados/buscar/", parametros).content.decode())
    assert vacio["variante"] == "sin_resultados"
    assert vacio["titulo"] == MENSAJES["vacio.filtro.titulo"]
    assert vacio["enlaces"] == {MENSAJES["vacio.filtro.accion"]: "/resultados/"}
    assert ("9999" if "numero" in parametros else "01/01/2020") in vacio["texto"]


def test_ac_8_1_estadisticas_sin_sorteos(client):
    vacio = _vacio(client.get("/estadisticas/").content.decode())
    assert vacio["icono"] == "chart-column"
    assert vacio["titulo"] == mensaje("est.sin_sorteos", modalidad="Tradicional – Primer Sorteo")
    assert MENSAJES["vacio.estadisticas.explicacion"] in vacio["texto"]


def test_estadisticas_con_datos_no_muestra_vacio(client):
    c = crear_concurso(1, date(2025, 1, 1), modalidades=[Modalidad.PRIMER_SORTEO])
    cargar_numeros(c, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
    assert "data-estado-vacio" not in client.get("/estadisticas/").content.decode()


def test_administracion_de_sorteos_sin_sorteos(cliente_admin):
    vacio = _vacio(cliente_admin.get("/administracion/concursos/").content.decode())
    assert vacio["titulo"] == MENSAJES["admin.sin_concursos"]
    assert vacio["enlaces"] == {
        MENSAJES["vacio.resultados.accion_cargar"]: "/administracion/concursos/nuevo/"
    }


def test_fr_026_sin_cuadros_punteados_viejos(cliente_a, cliente_admin, client):
    for cliente, ruta in [
        (cliente_a, "/mis-jugadas/"),
        (client, "/resultados/"),
        (cliente_admin, "/administracion/extracciones/"),
        (client, "/estadisticas/"),
    ]:
        assert 'class="vacio"' not in cliente.get(ruta).content.decode()
