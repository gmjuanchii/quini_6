"""[003] R-12, AC-14.4: ``POST /api/v1/formularios/pendiente/`` devuelve lo escrito de un token
válido para que Next.js reabra su formulario precargado, sin registrar nada."""

import pytest
from django.http import QueryDict
from django.test import Client

from jugadas.models import Jugada
from quini6.formulario_pendiente import firmar
from tests.api.conftest import token_csrf
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

API = "/api/v1/formularios/pendiente/"
RUTA = "/mis-jugadas/nueva/"


@pytest.fixture
def ana(db):
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(crear_usuario("ana@pendiente.local"))
    return cliente


def _token():
    datos = QueryDict(mutable=True)
    datos.setlist("numeros", ["03", "08"])
    datos["costo"] = "100"
    datos["password"] = "secreta"
    return firmar(RUTA, datos)


def _post(cliente, cuerpo):
    return cliente.post(
        API, cuerpo, content_type="application/json", HTTP_X_CSRFTOKEN=token_csrf(cliente)
    )


def test_devuelve_lo_escrito_sin_contrasenas_ni_registrar(ana):
    respuesta = _post(ana, {"pendiente": _token(), "ruta": RUTA})
    assert respuesta.status_code == 200
    assert respuesta.json() == {"ruta": RUTA, "campos": {"numeros": ["03", "08"], "costo": ["100"]}}
    assert respuesta["Cache-Control"] == "no-store"
    assert not Jugada.objects.exists()


@pytest.mark.parametrize("pendiente", ["", "alterado", None])
def test_token_invalido_422(ana, pendiente):
    token = _token()[:-3] + "xyz" if pendiente is None else pendiente
    assert _post(ana, {"pendiente": token, "ruta": RUTA}).status_code == 422


def test_ruta_distinta_422(ana):
    assert _post(ana, {"pendiente": _token(), "ruta": "/mis-jugadas/9/editar/"}).status_code == 422


def test_sin_sesion_401(visitante):
    assert _post(visitante, {"pendiente": _token(), "ruta": RUTA}).status_code == 401
