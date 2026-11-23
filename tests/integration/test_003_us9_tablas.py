"""[003] HU-09: listado de extracciones ordenable, paginado y con fila clicable (AC-9.1, AC-9.2,
AC-9.4, RN-07, FR-027; data-model § 2)."""

import html
import re
from datetime import date, datetime, timedelta

import pytest
from django.utils import timezone

from dominio.mensajes import MENSAJES, mensaje
from extracciones.models import Extraccion
from tests.extraccion_estados import crear_extraccion

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"


def _muchas(admin, cantidad: int) -> list[Extraccion]:
    """``cantidad`` extracciones finalizadas, una por día hacia atrás desde el 21/11/2026."""
    base = timezone.make_aware(datetime(2026, 11, 21, 10, 0))
    return Extraccion.objects.bulk_create(
        Extraccion(
            creada_por=admin,
            desde=date(2020, 1, 1) + timedelta(days=i),
            hasta=date(2020, 1, 1) + timedelta(days=i + 10),
            estado="FINALIZADA",
            iniciada_en=base - timedelta(days=i),
            finalizada_en=base - timedelta(days=i) + timedelta(minutes=2),
            resumen={"identificados": 0, "por_estado": {}, "fuentes": [], "huecos": []},
        )
        for i in range(cantidad)
    )


def _ids(contenido: str) -> list[int]:
    return [int(x) for x in re.findall(r'<tr id="fila-extraccion-(\d+)"', contenido)]


def _get(cliente, **params) -> str:
    respuesta = cliente.get(INICIO, params)
    assert respuesta.status_code == 200
    return respuesta.content.decode()


def _paginacion(contenido: str) -> str | None:
    m = re.search(r'<nav\b[^>]*aria-label="Paginación"[^>]*>(.*?)</nav>', contenido, re.S)
    return m.group(1) if m else None


def _texto(fragmento: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def test_ac_9_2_veinte_por_pagina_con_pagina_actual_y_total(cliente_admin, admin):
    _muchas(admin, 300)
    contenido = _get(cliente_admin)
    assert len(_ids(contenido)) == 20
    nav = _paginacion(contenido)
    assert nav and mensaje("pag.pagina", n=1, m=15) in _texto(nav)
    assert 'aria-disabled="true"' in nav  # "Anterior" en la primera página
    assert MENSAJES["pag.anterior"] in nav and MENSAJES["pag.siguiente"] in nav


def test_ac_9_2_fuera_de_rango_va_a_la_ultima(cliente_admin, admin):
    _muchas(admin, 300)
    contenido = _get(cliente_admin, pagina="99")
    assert len(_ids(contenido)) == 20
    assert mensaje("pag.pagina", n=15, m=15) in _texto(_paginacion(contenido))
    assert mensaje("pag.pagina", n=1, m=15) in _texto(_paginacion(_get(cliente_admin, pagina="x")))


def test_rn_07_filtro_y_orden_se_conservan_al_paginar(cliente_admin, admin):
    _muchas(admin, 45)
    contenido = _get(cliente_admin, estado="finalizada", orden="periodo", pagina="2")
    enlaces = [html.unescape(h) for h in re.findall(r'href="([^"]+)"', _paginacion(contenido))]
    assert enlaces, "faltan los enlaces de paginación"
    for enlace in enlaces:
        assert "estado=finalizada" in enlace and "orden=periodo" in enlace
    assert {"pagina=1", "pagina=3"} <= {p for e in enlaces for p in e.split("&")}


def test_ac_9_2_con_una_sola_extraccion_no_hay_paginacion(cliente_admin, admin):
    crear_extraccion(admin, "finalizada")
    assert _paginacion(_get(cliente_admin)) is None


@pytest.fixture
def tres(admin):
    """Tres extracciones con fecha, período y estado distintos (data-model § 2)."""
    hora = timezone.make_aware
    a = crear_extraccion(
        admin, "finalizada", hora(datetime(2026, 11, 20, 9)), date(2025, 1, 1), date(2025, 3, 1)
    )
    b = crear_extraccion(
        admin, "con-error", hora(datetime(2026, 11, 18, 9)), date(2024, 1, 1), date(2024, 2, 1)
    )
    c = crear_extraccion(
        admin, "sin-sorteos", hora(datetime(2026, 11, 19, 9)), date(2025, 1, 1), date(2025, 2, 1)
    )
    return a, b, c


@pytest.mark.parametrize(
    ("orden", "esperado", "columna", "sentido"),
    [
        ("-fecha", "abc→acb", "Fecha", "descending"),
        ("fecha", "abc→bca", "Fecha", "ascending"),
        ("periodo", "abc→bca", "Período", "ascending"),
        ("-periodo", "abc→acb", "Período", "descending"),
        ("estado", "abc→bca", "Estado", "ascending"),
        ("-estado", "abc→acb", "Estado", "descending"),
        ("cualquiera", "abc→acb", "Fecha", "descending"),
    ],
)
def test_ac_9_1_orden_por_columna(cliente_admin, tres, orden, esperado, columna, sentido):
    nombres = dict(zip("abc", tres, strict=True))
    contenido = _get(cliente_admin, orden=orden)
    assert _ids(contenido) == [nombres[x].pk for x in esperado.split("→")[1]]
    encabezado = re.search(rf'<th\b[^>]*aria-sort="{sentido}"[^>]*>(.*?)</th>', contenido, re.S)
    assert encabezado and _texto(encabezado.group(1)).startswith(columna)
    assert contenido.count("aria-sort=") == 1


def test_ac_9_1_desempate_por_id_descendente(cliente_admin, admin):
    momento = timezone.make_aware(datetime(2026, 11, 20, 9))
    primera = crear_extraccion(admin, "finalizada", momento)
    segunda = crear_extraccion(admin, "finalizada", momento)
    assert _ids(_get(cliente_admin, orden="fecha")) == [segunda.pk, primera.pk]


def test_ac_9_4_fila_entera_abre_el_detalle_salvo_el_menu(cliente_admin, admin):
    extraccion = crear_extraccion(admin, "finalizada")
    contenido = _get(cliente_admin)
    fila = re.search(
        rf'<tr id="fila-extraccion-{extraccion.pk}"[^>]*>(.*?)</tr>', contenido, re.S
    ).group(0)
    assert "fila-enlace" in fila.split(">", 1)[0]
    enlace = re.search(r"<a\b[^>]*data-enlace-fila[^>]*>(.*?)</a>", fila, re.S)
    assert enlace and _texto(enlace.group(1)) == MENSAJES["ext.ver_detalle"]
    assert f'href="{INICIO}{extraccion.pk}/"' in enlace.group(0)
    assert "<details" in fila  # el ⋮ sigue disponible por encima del enlace de la fila


def test_fr_027_tabla_apilable_con_rotulos(cliente_admin, admin):
    crear_extraccion(admin, "finalizada")
    contenido = _get(cliente_admin)
    tabla = re.search(r"<table\b[^>]*>", contenido).group(0)
    assert "apilable" in tabla
    rotulos = re.findall(r'<td\b[^>]*data-rotulo="([^"]+)"', contenido)
    assert {"Fecha", "Período", "Estado"} <= set(rotulos)
