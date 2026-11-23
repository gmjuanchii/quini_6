"""[003] T198: ingresar, salir y crear cuenta en la API v1 (contracts/api.md § Sesión y cuentas).

Los mismos servicios y mensajes que las vistas HTML ([001] AC-3.1 a AC-3.8, R-04): credenciales
incorrectas sin revelar si el correo existe (FR-020), bloqueo tras 5 fallos, ``pendiente``
([003] R-12), ``Idempotency-Key`` y CSRF en todas.
"""

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.http import QueryDict
from django.test import Client

from dominio.mensajes import MENSAJES
from quini6.formulario_pendiente import firmar
from tests.api.conftest import token_csrf
from tests.fabricas import CLAVE, crear_usuario

pytestmark = pytest.mark.django_db


@pytest.fixture
def cliente(db):
    return Client(enforce_csrf_checks=True)


def _post(cliente, ruta, datos, clave=None, csrf=True):
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)} if csrf else {}
    if clave:
        extra["HTTP_IDEMPOTENCY_KEY"] = clave
    return cliente.post(ruta, datos, content_type="application/json", **extra)


def test_ingresar_fija_la_sesion(cliente):
    crear_usuario("ana@cuentas.local")
    respuesta = _post(
        cliente, "/api/v1/sesion/", {"correo": "ana@cuentas.local", "contrasena": CLAVE}
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["correo"] == "ana@cuentas.local"
    assert respuesta.json()["reanudar"] is None
    assert "sessionid" in respuesta.cookies
    assert cliente.get("/api/v1/sesion/").json()["correo"] == "ana@cuentas.local"


def test_credenciales_incorrectas_sin_revelar_si_existe(cliente):
    crear_usuario("ana@cuentas.local")
    mala = _post(cliente, "/api/v1/sesion/", {"correo": "ana@cuentas.local", "contrasena": "x" * 9})
    inexistente = _post(
        cliente, "/api/v1/sesion/", {"correo": "no@cuentas.local", "contrasena": "x" * 9}
    )
    assert mala.status_code == inexistente.status_code == 422
    assert (
        mala.json()["detail"]
        == inexistente.json()["detail"]
        == MENSAJES["cuenta.credenciales_incorrectas"]
    )


def test_bloqueo_tras_cinco_fallos(cliente):
    crear_usuario("ana@cuentas.local")
    for _ in range(5):
        _post(cliente, "/api/v1/sesion/", {"correo": "ana@cuentas.local", "contrasena": "y" * 9})
    respuesta = _post(
        cliente, "/api/v1/sesion/", {"correo": "ana@cuentas.local", "contrasena": CLAVE}
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"].startswith(MENSAJES["cuenta.bloqueada"].split("{")[0])


def test_errores_por_campo(cliente):
    respuesta = _post(cliente, "/api/v1/sesion/", {"correo": "", "contrasena": ""})
    errores = {(e["campo"], e["mensaje"]) for e in respuesta.json()["errores"]}
    assert errores == {
        ("correo", MENSAJES["cuenta.falta_correo"]),
        ("contrasena", MENSAJES["cuenta.falta_contrasena"]),
    }


def test_ingresar_con_pendiente_devuelve_lo_escrito(cliente):
    crear_usuario("ana@cuentas.local")
    datos = QueryDict(mutable=True)
    datos["costo"] = "100"
    token = firmar("/mis-jugadas/nueva/", datos)
    respuesta = _post(
        cliente,
        "/api/v1/sesion/",
        {"correo": "ana@cuentas.local", "contrasena": CLAVE, "pendiente": token},
    )
    assert respuesta.json()["reanudar"] == {
        "ruta": "/mis-jugadas/nueva/",
        "campos": {"costo": ["100"]},
    }


def test_salir(cliente):
    cliente.force_login(crear_usuario("ana@cuentas.local"))
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)}
    assert cliente.delete("/api/v1/sesion/", **extra).status_code == 204
    assert cliente.get("/api/v1/sesion/").json()["correo"] is None


def test_crear_cuenta_ingresa_e_idempotencia(cliente):
    clave = str(uuid.uuid4())
    datos = {"correo": "nueva@cuentas.local", "contrasena": "contraseña-larga"}
    respuesta = _post(cliente, "/api/v1/cuentas/", datos, clave)
    assert respuesta.status_code == 201
    assert respuesta.json()["correo"] == "nueva@cuentas.local"
    assert _post(cliente, "/api/v1/cuentas/", datos, clave).status_code == 201
    assert get_user_model().objects.filter(email="nueva@cuentas.local").count() == 1


def test_crear_cuenta_errores(cliente):
    crear_usuario("ana@cuentas.local")
    existente = _post(
        cliente, "/api/v1/cuentas/", {"correo": "ana@cuentas.local", "contrasena": "x" * 9}
    )
    assert existente.status_code == 422
    assert existente.json()["detail"] == MENSAJES["cuenta.correo_existente"]
    corta = _post(cliente, "/api/v1/cuentas/", {"correo": "b@cuentas.local", "contrasena": "corta"})
    assert ("contrasena", MENSAJES["cuenta.contrasena_corta"]) in {
        (e["campo"], e["mensaje"]) for e in corta.json()["errores"]
    }


def test_todas_exigen_csrf(cliente):
    crear_usuario("ana@cuentas.local")
    datos = {"correo": "ana@cuentas.local", "contrasena": CLAVE}
    assert _post(cliente, "/api/v1/sesion/", datos, csrf=False).status_code == 403
    assert _post(cliente, "/api/v1/cuentas/", datos, csrf=False).status_code == 403
