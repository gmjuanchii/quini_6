"""[003] HU-02: menú de acciones y confirmación de eliminación (AC-2.1 a AC-2.6, FR-007 a 009)."""

import re

import pytest
from django.contrib.messages import get_messages

from dominio.mensajes import MENSAJES, mensaje
from extracciones.models import Extraccion
from quini6.idempotencia import nueva_clave
from quini6.templatetags.formato_ar import fecha_ar, fecha_hora_ar
from tests.extraccion_estados import crear_extraccion

pytestmark = pytest.mark.django_db

LISTADO = "/administracion/extracciones/"


@pytest.fixture
def terminada(admin):
    return crear_extraccion(admin, "con-advertencias")


def _url(extraccion) -> str:
    return f"{LISTADO}{extraccion.pk}/eliminar/"


def _mensajes(respuesta) -> list[str]:
    return [str(m) for m in get_messages(respuesta.wsgi_request)]


def test_ac_2_3_con_htmx_solo_el_contenido_del_dialogo(cliente_admin, terminada):
    respuesta = cliente_admin.get(_url(terminada), HTTP_HX_REQUEST="true")
    html = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "<html" not in html
    confirmar = mensaje(
        "ext.eliminar_confirmar",
        fecha_hora=fecha_hora_ar(terminada.iniciada_en),
        desde=fecha_ar(terminada.desde),
        hasta=fecha_ar(terminada.hasta),
    )
    assert confirmar in html
    assert MENSAJES["ext.eliminar_consecuencias"] in html
    cancelar = re.search(r"<(?:a|button)[^>]*data-cancelar[^>]*>", html)
    assert cancelar and "autofocus" in cancelar.group(0)
    eliminar = re.search(r'<button[^>]*type="submit"[^>]*>', html)
    assert eliminar and "bg-destructive" in eliminar.group(0)
    assert respuesta["Vary"] and "HX-Request" in respuesta["Vary"]


def test_ac_2_3_sin_htmx_la_pagina_completa(cliente_admin, terminada):
    html = cliente_admin.get(_url(terminada)).content.decode()
    assert "<html" in html
    assert MENSAJES["ext.eliminar_consecuencias"] in html


def test_ac_2_5_eliminar_y_aviso_con_fecha_y_hora(cliente_admin, terminada):
    momento = fecha_hora_ar(terminada.iniciada_en)
    respuesta = cliente_admin.post(_url(terminada))
    assert respuesta.status_code == 303
    assert respuesta["Location"] == LISTADO
    assert not Extraccion.objects.filter(pk=terminada.pk).exists()
    assert mensaje("ext.eliminada", fecha_hora=momento) in _mensajes(respuesta)


def test_ac_2_5_reintento_con_la_misma_clave_un_solo_efecto(cliente_admin, terminada):
    clave = nueva_clave()
    primera = cliente_admin.post(_url(terminada), {"clave_idempotencia": clave})
    segunda = cliente_admin.post(_url(terminada), {"clave_idempotencia": clave})
    assert primera.status_code == segunda.status_code == 303
    assert primera["Location"] == segunda["Location"]


@pytest.mark.parametrize("metodo", ["get", "post"])
def test_casos_limite_extraccion_que_ya_no_existe(cliente_admin, metodo):
    respuesta = getattr(cliente_admin, metodo)(f"{LISTADO}999999/eliminar/")
    assert respuesta.status_code == 303
    assert respuesta["Location"] == LISTADO
    assert MENSAJES["ext.no_existe"] in _mensajes(respuesta)


def test_ac_2_6_en_curso_sin_eliminar_en_el_menu(cliente_admin, admin):
    en_curso = crear_extraccion(admin, "en-curso")
    html = cliente_admin.get(LISTADO).content.decode()
    assert f'href="{_url(en_curso)}"' not in html


def test_ac_2_1_menu_con_nombre_accesible_y_opciones_de_su_fila(cliente_admin, terminada):
    html = cliente_admin.get(LISTADO).content.decode()
    nombre = mensaje("ext.acciones", fecha_hora=fecha_hora_ar(terminada.iniciada_en))
    assert f'aria-label="{nombre}"' in html
    assert f'href="{_url(terminada)}"' in html
    assert f'href="/administracion/extracciones/{terminada.pk}/"' in html


def test_fragmento_sin_permiso_responde_403_completo(client, usuario_a, terminada):
    client.force_login(usuario_a)
    respuesta = client.get(_url(terminada), HTTP_HX_REQUEST="true")
    assert respuesta.status_code == 403
    assert "<html" in respuesta.content.decode()
