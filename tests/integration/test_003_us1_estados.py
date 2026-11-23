"""[003] HU-01: etiqueta de estado, explicación, destaque y filtro (AC-1.1 a AC-1.5)."""

import re
from datetime import datetime, timedelta

import pytest
from django.utils import timezone

from dominio.mensajes import MENSAJES
from tests.extraccion_estados import CASOS, crear_extraccion

pytestmark = pytest.mark.django_db

LISTADO = "/administracion/extracciones/"
ETIQUETAS = ("en_curso", "finalizada", "con_advertencias", "sin_sorteos", "con_error")


@pytest.fixture
def extracciones(admin):
    base = timezone.make_aware(datetime(2026, 11, 1, 9, 0))
    return {
        etiqueta: crear_extraccion(admin, etiqueta, iniciada_en=base + timedelta(hours=i))
        for i, etiqueta in enumerate(CASOS)
    }


def _html(respuesta) -> str:
    assert respuesta.status_code == 200
    return respuesta.content.decode()


def _tabla(html: str) -> str:
    return html.split("<table", 1)[1].split("</table>", 1)[0]


def _filas(html: str) -> list[str]:
    cuerpo = _tabla(html).split("<tbody", 1)[1].split("</tbody>", 1)[0]
    return re.findall(r"<tr\b.*?</tr>", cuerpo, flags=re.S)


def test_ac_1_1_cada_fila_con_texto_icono_y_explicacion(cliente_admin, extracciones):
    html = _html(cliente_admin.get(LISTADO))
    tabla = _tabla(html)
    for etiqueta in ETIQUETAS:
        assert MENSAJES[f"etiqueta.{etiqueta}"] in tabla, etiqueta
        assert MENSAJES[f"etiqueta.{etiqueta}.explicacion"] in tabla, etiqueta
    insignias = re.findall(r"<span[^>]*data-insignia-estado.*?</span>\s*</span>", tabla, re.S)
    assert len(insignias) == len(CASOS)
    for insignia in insignias:
        assert "<svg" in insignia
        assert re.search(r'aria-describedby="explicacion-[^"]+"', insignia)


def test_ac_1_1_el_listado_ya_no_muestra_el_texto_largo(cliente_admin, extracciones):
    tabla = _tabla(_html(cliente_admin.get(LISTADO)))
    assert MENSAJES["ext.con_advertencias"] not in tabla


def test_ac_1_3_destaca_las_que_requieren_revision(cliente_admin, extracciones):
    filas = _filas(_html(cliente_admin.get(LISTADO)))
    marcadas = [f for f in filas if "data-requiere-revision" in f]
    assert len(marcadas) == 2
    assert all("Requiere revisión" in f for f in marcadas)
    finalizada = MENSAJES["etiqueta.finalizada"]
    assert not any("data-requiere-revision" in f for f in filas if f">{finalizada}<" in f)


def test_ac_1_4_filtro_por_estado(cliente_admin, extracciones):
    html = _html(cliente_admin.get(LISTADO + "?estado=con-advertencias"))
    filas = _filas(html)
    assert len(filas) == 1
    assert MENSAJES["etiqueta.con_advertencias"] in filas[0]
    assert MENSAJES["ext.filtro_aplicado"].format(filtro="Con advertencias") in html
    assert MENSAJES["ext.filtro_todos"] in html


def test_ac_1_4_todos_los_estados_y_filtro_invalido(cliente_admin, extracciones):
    prefijo_filtro = MENSAJES["ext.filtro_aplicado"].split("{")[0]
    for consulta in ("", "?estado=", "?estado=desconocido"):
        html = _html(cliente_admin.get(LISTADO + consulta))
        assert len(_filas(html)) == len(CASOS)
        assert prefijo_filtro not in html


def test_ac_1_5_el_detalle_muestra_la_misma_etiqueta_y_el_resultado(cliente_admin, extracciones):
    html = _html(cliente_admin.get(f"{LISTADO}{extracciones['con-error'].pk}/"))
    assert MENSAJES["etiqueta.con_error"] in html
    assert MENSAJES["etiqueta.con_error.explicacion"] in html
    assert MENSAJES["ext.con_advertencias"] in html  # resultado global de [002] RN-33
