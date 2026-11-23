"""[003] HU-12: tema claro, oscuro o según el dispositivo (FR-036, AC-12.1 a AC-12.3, NFR-008,
R-14; data-model § 4)."""

import re

import pytest
from django.test import Client

from cuentas.models import Usuario
from dominio.mensajes import MENSAJES

pytestmark = pytest.mark.django_db

RUTA = "/preferencias/tema/"
COOKIE = "quini6_tema"


def _data_theme(contenido: str) -> str | None:
    html = re.search(r"<html\b[^>]*>", contenido).group(0)
    m = re.search(r'data-theme="([^"]*)"', html)
    return m.group(1) if m else None


@pytest.mark.parametrize("tema", ["claro", "oscuro"])
def test_ac_12_2_elegir_un_tema_fija_la_cookie(client, tema):
    r = client.post(RUTA, {"tema": tema, "next": "/estadisticas/"})
    assert r.status_code == 303 and r["Location"] == "/estadisticas/"
    cookie = r.cookies[COOKIE]
    assert cookie.value == tema
    assert cookie["path"] == "/"
    assert cookie["samesite"] == "Lax"
    assert int(cookie["max-age"]) == 400 * 24 * 60 * 60
    assert not cookie["httponly"]


def test_ac_12_1_segun_el_dispositivo_borra_la_cookie(client):
    client.cookies[COOKIE] = "oscuro"
    r = client.post(RUTA, {"tema": "dispositivo", "next": "/resultados/"})
    assert r.status_code == 303
    assert r.cookies[COOKIE].value == "" and int(r.cookies[COOKIE]["max-age"]) == 0


def test_tema_invalido_se_ignora(client):
    client.cookies[COOKIE] = "claro"
    r = client.post(RUTA, {"tema": "violeta", "next": "/resultados/"})
    assert r.status_code == 303
    assert COOKIE not in r.cookies  # no cambia la preferencia


@pytest.mark.parametrize("siguiente", ["https://otro.sitio/", "//otro.sitio/", "", None])
def test_next_externo_o_ausente_vuelve_al_inicio(client, siguiente):
    datos = {"tema": "oscuro"}
    if siguiente is not None:
        datos["next"] = siguiente
    r = client.post(RUTA, datos)
    assert r.status_code == 303 and r["Location"] == "/"


def test_sin_csrf_403():
    cliente = Client(enforce_csrf_checks=True)
    assert cliente.post(RUTA, {"tema": "oscuro"}).status_code == 403


def test_solo_post(client):
    assert client.get(RUTA).status_code == 405


@pytest.mark.parametrize(("cookie", "esperado"), [("claro", "claro"), ("oscuro", "oscuro")])
def test_ac_12_3_html_con_el_tema_elegido(client, cookie, esperado):
    client.cookies[COOKIE] = cookie
    assert _data_theme(client.get("/resultados/").content.decode()) == esperado


@pytest.mark.parametrize("cookie", [None, "violeta", "dispositivo"])
def test_ac_12_1_sin_cookie_o_invalida_segun_el_dispositivo(client, cookie):
    if cookie:
        client.cookies[COOKIE] = cookie
    assert _data_theme(client.get("/resultados/").content.decode()) is None


def test_visitante_y_usuaria_por_igual(client, cliente_a):
    for cliente in (client, cliente_a):
        cliente.cookies[COOKIE] = "oscuro"
        assert _data_theme(cliente.get("/estadisticas/").content.decode()) == "oscuro"
        assert cliente.post(RUTA, {"tema": "claro", "next": "/"}).status_code == 303


def test_nfr_008_no_se_guarda_en_el_servidor(cliente_a, usuario_a):
    antes = {k: v for k, v in cliente_a.session.items()}
    actualizado = Usuario.objects.get(pk=usuario_a.pk)
    cliente_a.post(RUTA, {"tema": "oscuro", "next": "/"})
    assert dict(cliente_a.session.items()) == antes
    despues = Usuario.objects.get(pk=usuario_a.pk)
    assert [getattr(despues, f.attname) for f in Usuario._meta.fields] == [
        getattr(actualizado, f.attname) for f in Usuario._meta.fields
    ]


def test_ac_12_2_selector_en_el_pie_para_visitantes(client):
    contenido = client.get("/resultados/").content.decode()
    pie = re.search(r"<footer\b.*?</footer>", contenido, re.S).group(0)
    accion = re.escape(f"{RUTA}?_interfaz=django")  # [003] R-20
    formulario = re.search(rf'<form\b[^>]*action="{accion}"[^>]*>(.*?)</form>', pie, re.S)
    assert formulario and 'method="post"' in formulario.group(0)
    cuerpo = formulario.group(1)
    assert "csrfmiddlewaretoken" in cuerpo
    assert MENSAJES["tema.titulo"] in cuerpo
    for valor, clave in (
        ("claro", "tema.claro"),
        ("oscuro", "tema.oscuro"),
        ("dispositivo", "tema.dispositivo"),
    ):
        assert re.search(rf'<input\b[^>]*type="radio"[^>]*value="{valor}"', cuerpo), valor
        assert MENSAJES[clave] in cuerpo
    assert re.search(r'<input\b[^>]*value="dispositivo"[^>]*checked', cuerpo)  # sin cookie
    assert MENSAJES["tema.guardar"] in cuerpo
    assert 'name="next" value="/resultados/"' in cuerpo
