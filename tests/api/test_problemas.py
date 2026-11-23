"""[003] R-16: errores de la API en formato Problem Details (RFC 9457)."""

import pytest

from tests.api.conftest import token_csrf

pytestmark = pytest.mark.urls("tests.api.urls_prueba")


def _es_problema(respuesta, estado):
    assert respuesta.status_code == estado
    assert respuesta["Content-Type"].startswith("application/problem+json")
    datos = respuesta.json()
    assert {"type", "title", "status", "detail"} <= set(datos)
    assert datos["status"] == estado
    return datos


def test_validacion_422_con_errores_por_campo(visitante):
    token = token_csrf(visitante)
    respuesta = visitante.post(
        "/api/v1/_prueba/validacion/",
        data={"numero": "no-es-numero"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )
    datos = _es_problema(respuesta, 422)
    assert datos["errores"] and {"campo", "codigo", "mensaje"} <= set(datos["errores"][0])


def test_mutacion_sin_csrf_es_403(usuario):
    respuesta = usuario.post(
        "/api/v1/_prueba/validacion/", data={"numero": 1}, content_type="application/json"
    )
    _es_problema(respuesta, 403)


def test_401_sin_sesion(visitante):
    _es_problema(visitante.get("/api/v1/_prueba/usuario/"), 401)


def test_403_sin_permiso(usuario):
    _es_problema(usuario.get("/api/v1/_prueba/administrador/"), 403)


def test_404_con_el_mismo_formato(visitante):
    _es_problema(visitante.get("/api/v1/_prueba/inexistente/"), 404)
