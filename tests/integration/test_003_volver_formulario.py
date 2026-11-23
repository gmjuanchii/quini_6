"""[003] AC-14.4, R-12: "Volver al formulario" cuando el formulario pendiente vive en Next.js.

Mientras "Ingresar" siga en Django y el formulario esté en una ruta de ``QUINI6_RUTAS_NEXT``, tras
ingresar Django responde una página breve con un único botón que envía el token por POST a esa
ruta (sin la marca ``?_interfaz=django``, así el enrutador la entrega a Next.js). Nada se registra.
"""

import html
import re
from datetime import date

import pytest
from django.test import Client, override_settings

from dominio.mensajes import MENSAJES
from jugadas.models import Jugada
from tests.fabricas import CLAVE, crear_concurso, crear_usuario
from tests.integration.test_003_formulario_pendiente import DATOS, NUEVA, _pendiente

pytestmark = pytest.mark.django_db

RUTAS_NEXT = ["/mis-jugadas/", "/mis-jugadas/*"]


@pytest.fixture
def concurso(db):
    return crear_concurso(9001, date(2099, 3, 2))


def _token():
    return _pendiente(Client().post(NUEVA, DATOS).content.decode())


def _ingresar(cliente, token):
    crear_usuario("ana@prueba.local")
    return cliente.post(
        "/ingresar/",
        {"email": "ana@prueba.local", "password": CLAVE, "next": NUEVA, "pendiente": token},
    )


@override_settings(QUINI6_RUTAS_NEXT=RUTAS_NEXT)
def test_ac_14_4_ruta_de_next_responde_volver_al_formulario(concurso):
    token = _token()
    cliente = Client()
    respuesta = _ingresar(cliente, token)
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-store"
    assert MENSAJES["cuenta.volver_formulario_texto"] in contenido
    formulario = re.search(r"<form\b[^>]*data-volver-formulario[^>]*>.*?</form>", contenido, re.S)
    assert formulario, "falta el formulario"
    apertura = formulario.group(0).split(">", 1)[0]
    assert 'method="post"' in apertura
    assert f'action="{NUEVA}"' in apertura  # sin ?_interfaz=django: lo atiende Next.js
    assert "csrfmiddlewaretoken" in formulario.group(0)
    oculto = re.search(r'name="pendiente" value="([^"]+)"', formulario.group(0))
    assert oculto and html.unescape(oculto.group(1)) == token
    assert MENSAJES["cuenta.volver_formulario"] in formulario.group(0)
    assert 'id="form-jugada"' not in contenido  # no es el formulario de Django
    assert not Jugada.objects.exists()
    assert cliente.get("/mis-jugadas/").status_code == 200  # la sesión quedó iniciada


@override_settings(QUINI6_RUTAS_NEXT=["/administracion/extracciones/*"])
def test_ruta_que_no_es_de_next_mantiene_el_formulario_precargado(concurso):
    respuesta = _ingresar(Client(), _token())
    contenido = respuesta.content.decode()
    assert 'id="form-jugada"' in contenido
    assert MENSAJES["cuenta.volver_formulario_texto"] not in contenido
    assert not Jugada.objects.exists()


@override_settings(QUINI6_RUTAS_NEXT=RUTAS_NEXT)
def test_token_alterado_no_ofrece_volver_y_redirige_como_siempre(concurso):
    token = _token()
    alterado = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    respuesta = _ingresar(Client(), alterado)
    assert respuesta.status_code == 302
    assert respuesta["Location"] == NUEVA


def test_r_12_post_con_solo_el_pendiente_muestra_ingresar_sin_errores(concurso):
    """[003] R-12: el botón "Ingresar" de un formulario de Next.js con la sesión vencida envía solo
    el ``pendiente``; Django muestra su formulario vacío, sin mensajes de error, con el token."""
    token = _token()
    respuesta = Client().post("/ingresar/?next=/mis-jugadas/nueva/", {"pendiente": token})
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    oculto = re.search(r'name="pendiente" value="([^"]+)"', contenido)
    assert oculto and html.unescape(oculto.group(1)) == token
    assert 'aria-invalid="true"' not in contenido
    assert not Jugada.objects.exists()
