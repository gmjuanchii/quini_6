"""[003] HU-03: avance en vivo, aviso al terminar y mensaje ante error (AC-3.1 a AC-3.4, R-10)."""

import json
from datetime import date

import pytest

from dominio.mensajes import MENSAJES, mensaje
from extracciones.models import Extraccion
from tests.extraccion_estados import crear_extraccion

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
HTMX = {"HTTP_HX_REQUEST": "true"}


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: date(2026, 11, 19))


def _detalle(cliente, extraccion, **extra):
    return cliente.get(f"{INICIO}{extraccion.pk}/", **extra)


def test_fragmento_en_curso_identificando_con_sondeo(cliente_admin, admin):
    extraccion = crear_extraccion(admin, "en-curso")
    respuesta = _detalle(cliente_admin, extraccion, **HTMX)
    html = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "<html" not in html
    assert 'id="avance-extraccion"' in html
    assert 'hx-trigger="every 3s"' in html
    assert MENSAJES["ext.identificando"] in html
    assert "HX-Request" in respuesta["Vary"]
    assert respuesta["Cache-Control"] == "no-store"
    assert "HX-Trigger" not in respuesta


def test_fragmento_en_curso_con_total(cliente_admin, admin):
    extraccion = crear_extraccion(admin, "en-curso")
    Extraccion.objects.filter(pk=extraccion.pk).update(numero_desde=3422, numero_hasta=3426)
    html = _detalle(cliente_admin, extraccion, **HTMX).content.decode()
    assert mensaje("ext.avance", n=0, m=5) in html
    assert "<progress" in html


@pytest.mark.parametrize(
    ("etiqueta", "clave", "tipo", "n"),
    [
        ("finalizada", "ext.termino_finalizada", "success", None),
        ("con-advertencias", "ext.termino_advertencias", "warning", 1),
        ("con-error", "ext.termino_error", "error", 1),
        ("sin-sorteos", "ext.termino_sin_sorteos", "info", None),
    ],
)
def test_fragmento_final_sin_sondeo_y_con_aviso(cliente_admin, admin, etiqueta, clave, tipo, n):
    extraccion = crear_extraccion(admin, etiqueta)
    respuesta = _detalle(cliente_admin, extraccion, **HTMX)
    html = respuesta.content.decode()
    assert 'id="avance-extraccion"' in html
    assert "hx-trigger" not in html
    aviso = json.loads(respuesta["HX-Trigger"])["aviso"]
    texto = mensaje(clave, n=n) if n is not None else MENSAJES[clave]
    assert aviso == {"tipo": tipo, "texto": texto, "enlace": f"{INICIO}{extraccion.pk}/"}


def test_la_fila_en_curso_del_listado_se_actualiza_igual(cliente_admin, admin):
    extraccion = crear_extraccion(admin, "en-curso")
    html = cliente_admin.get(INICIO).content.decode()
    assert f'hx-get="{INICIO}{extraccion.pk}/?fila=1"' in html
    respuesta = cliente_admin.get(f"{INICIO}{extraccion.pk}/?fila=1", **HTMX)
    fila = respuesta.content.decode()
    assert fila.lstrip().startswith("<tr")
    assert 'hx-trigger="every 3s"' in fila


def test_la_fila_terminada_ya_no_sondea(cliente_admin, admin):
    extraccion = crear_extraccion(admin, "finalizada")
    fila = cliente_admin.get(f"{INICIO}{extraccion.pk}/?fila=1", **HTMX).content.decode()
    assert "hx-trigger" not in fila
    assert MENSAJES["etiqueta.finalizada"] in fila


def test_ac_3_4_ninguna_fuente_respondio(cliente_admin, admin):
    extraccion = crear_extraccion(admin, "con-error")
    resumen = dict(extraccion.resumen)
    resumen["fuentes"] = [
        {"fuente": "F2", "nombre": "F2", "aportados": 0, "fallidos": {}},
        {"fuente": "F3", "nombre": "F3", "aportados": 0, "fallidos": {}},
    ]
    Extraccion.objects.filter(pk=extraccion.pk).update(resumen=resumen)
    html = _detalle(cliente_admin, extraccion).content.decode()
    assert MENSAJES["ext.ninguna_fuente"] in html


def test_ac_3_1_inicio_con_htmx_se_queda_en_el_listado(cliente_admin):
    respuesta = cliente_admin.post(INICIO, {"inicio": "01/11/2026", "fin": "15/11/2026"}, **HTMX)
    html = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "<html" not in html
    assert MENSAJES["etiqueta.en_curso"] in html
    assert 'id="avance-extraccion"' in html


def test_ac_3_1_inicio_sin_scripts_va_al_detalle(cliente_admin):
    respuesta = cliente_admin.post(INICIO, {"inicio": "01/11/2026", "fin": "15/11/2026"})
    assert respuesta.status_code == 303
    assert respuesta["Location"].startswith(INICIO)


def test_ac_3_1_boton_con_estado_de_trabajo(cliente_admin):
    html = cliente_admin.get(INICIO).content.decode()
    assert f'data-texto-trabajando="{MENSAJES["ext.boton_iniciar_trabajando"]}"' in html
    assert "data-trabajando" in html
