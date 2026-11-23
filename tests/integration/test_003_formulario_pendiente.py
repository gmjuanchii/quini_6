"""[003] FR-032, R-12: formulario pendiente al vencer la sesión (data-model § 3)."""

import html
import re
import secrets
import time
from datetime import date
from unittest import mock

import pytest
from django.core import signing
from django.test import Client

from dominio.mensajes import MENSAJES
from jugadas.models import Jugada
from quini6 import formulario_pendiente
from tests.fabricas import CLAVE, crear_concurso, crear_usuario

pytestmark = pytest.mark.django_db

NUEVA = "/mis-jugadas/nueva/"
DATOS = {
    "concurso": "9001",
    "numeros": ["03", "08", "14", "21", "32", "40"],
    "costo": "1500,50",
    "csrfmiddlewaretoken": "token-csrf",
    "clave_idempotencia": "8d5e0c4e-0000-4000-8000-000000000000",
}


@pytest.fixture
def concurso(db):
    return crear_concurso(9001, date(2099, 3, 2))


def _pendiente(contenido: str) -> str:
    m = re.search(r'<input type="hidden" name="pendiente" value="([^"]+)"', contenido)
    assert m, "falta el campo oculto «pendiente»"
    return html.unescape(m.group(1))


def _post_sin_sesion(ruta=NUEVA, datos=DATOS):
    return Client().post(ruta, datos)


def _ingresar(cliente, correo, pendiente, siguiente=NUEVA):
    return cliente.post(
        "/ingresar/",
        {"email": correo, "password": CLAVE, "next": siguiente, "pendiente": pendiente},
    )


def test_post_sin_sesion_muestra_ingresar_con_lo_escrito_firmado(concurso):
    respuesta = _post_sin_sesion()
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-store"
    assert MENSAJES["cuenta.sesion_vencida"] in contenido
    assert 'name="password"' in contenido  # es la pantalla "Ingresar"
    datos = signing.loads(_pendiente(contenido), salt=formulario_pendiente.SAL)
    assert datos["ruta"] == NUEVA
    assert datos["campos"]["numeros"] == DATOS["numeros"]
    assert datos["campos"]["costo"] == ["1500,50"]
    assert not {"csrfmiddlewaretoken", "clave_idempotencia"} & set(datos["campos"])
    assert not Jugada.objects.exists()


def test_el_token_nunca_lleva_contrasenas():
    token = formulario_pendiente.firmar(
        NUEVA, _querydict({"costo": "1", "password": "x", "nueva_contrasena": "y"})
    )
    assert set(signing.loads(token, salt=formulario_pendiente.SAL)["campos"]) == {"costo"}


def _querydict(datos):
    from django.http import QueryDict

    q = QueryDict(mutable=True)
    for k, v in datos.items():
        q.setlist(k, v if isinstance(v, list) else [v])
    return q


def test_al_ingresar_se_muestra_el_formulario_precargado_sin_registrar(concurso):
    crear_usuario("ana@prueba.local")
    pendiente = _pendiente(_post_sin_sesion().content.decode())
    cliente = Client()
    respuesta = _ingresar(cliente, "ana@prueba.local", pendiente)
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-store"
    assert 'id="form-jugada"' in contenido
    for numero in DATOS["numeros"]:
        assert re.search(rf'<input[^>]*value="{numero}"[^>]*checked', contenido), numero
    assert 'value="1500,50"' in contenido
    assert re.search(r'<option value="9001"[^>]*selected', contenido)
    assert not Jugada.objects.exists()  # nada se envía solo
    assert cliente.get("/mis-jugadas/").status_code == 200  # quedó la sesión iniciada


def test_con_otra_cuenta_la_jugada_queda_para_esa_cuenta(concurso):
    crear_usuario("ana@prueba.local")
    beto = crear_usuario("beto@prueba.local")
    pendiente = _pendiente(_post_sin_sesion().content.decode())
    cliente = Client()
    _ingresar(cliente, "beto@prueba.local", pendiente)
    datos = {k: v for k, v in DATOS.items() if k not in ("csrfmiddlewaretoken",)}
    cliente.post(NUEVA, datos)
    assert list(Jugada.objects.values_list("usuario", flat=True)) == [beto.pk]


@pytest.mark.parametrize("caso", ["alterado", "vencido", "grande"])
def test_token_invalido_se_ignora_y_el_formulario_queda_vacio(concurso, caso):
    crear_usuario("ana@prueba.local")
    pendiente = _pendiente(_post_sin_sesion().content.decode())
    cliente = Client()
    if caso == "alterado":
        pendiente = pendiente[:-3] + ("aaa" if not pendiente.endswith("aaa") else "bbb")
        respuesta = _ingresar(cliente, "ana@prueba.local", pendiente)
    elif caso == "vencido":
        ahora = time.time()
        with mock.patch("django.core.signing.time.time", return_value=ahora + 61 * 60):
            respuesta = _ingresar(cliente, "ana@prueba.local", pendiente)
    else:
        respuesta = _ingresar(cliente, "ana@prueba.local", "x" * (9 * 1024))
    assert respuesta.status_code == 302 and respuesta["Location"] == NUEVA
    contenido = cliente.get(NUEVA).content.decode()
    assert not re.search(r'value="03"[^>]*checked', contenido)
    assert not Jugada.objects.exists()


def test_mayor_a_8_kb_no_se_firma():
    grande = _querydict({"motivo": secrets.token_urlsafe(12000)})  # no se comprime
    assert formulario_pendiente.firmar(NUEVA, grande) is None


def test_vista_de_administracion_e_ingreso_sin_permisos(db):
    crear_usuario("ana@prueba.local")
    respuesta = Client().post(
        "/administracion/concursos/nuevo/", {"numero": "3300", "fecha_sorteo": "02/03/2025"}
    )
    assert respuesta.status_code == 200
    pendiente = _pendiente(respuesta.content.decode())
    final = _ingresar(Client(), "ana@prueba.local", pendiente, "/administracion/concursos/nuevo/")
    assert final.status_code == 403
    assert MENSAJES["admin.sin_permiso"] in final.content.decode()


def test_administracion_reanuda_para_quien_tiene_permisos(db):
    crear_usuario("admin@prueba.local", admin=True)
    respuesta = Client().post(
        "/administracion/concursos/nuevo/",
        {"numero": "3300", "fecha_sorteo": "2025-03-02", "modalidades": ["PRIMER_SORTEO"]},
    )
    pendiente = _pendiente(respuesta.content.decode())
    final = _ingresar(Client(), "admin@prueba.local", pendiente, "/administracion/concursos/nuevo/")
    contenido = final.content.decode()
    assert final.status_code == 200
    assert 'value="3300"' in contenido
    assert re.search(r'value="PRIMER_SORTEO"[^>]*checked', contenido)


def test_get_sin_sesion_sigue_redirigiendo(db):
    respuesta = Client().get(NUEVA)
    assert respuesta.status_code == 302 and respuesta["Location"].startswith("/ingresar/")


def test_formularios_de_eliminacion_no_se_reanudan(db):
    respuesta = Client().post("/mis-jugadas/1/eliminar/", {})
    assert respuesta.status_code == 302 and respuesta["Location"].startswith("/ingresar/")
