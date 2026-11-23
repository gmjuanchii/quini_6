"""[003] R-11, FR-031: un reintento con la misma clave no repite el efecto."""

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from quini6.idempotencia import MAX_CLAVES, con_idempotencia, nueva_clave

pytestmark = pytest.mark.django_db

EJECUCIONES: list[str] = []


class _Redireccion303(HttpResponseRedirect):
    status_code = 303


@con_idempotencia("prueba.crear")
def _vista(request):
    EJECUCIONES.append(request.POST.get("dato", ""))
    return _Redireccion303(f"/creado/{len(EJECUCIONES)}/")


@con_idempotencia("prueba.otra")
def _otra_vista(request):
    EJECUCIONES.append("otra")
    return _Redireccion303("/otra/")


@pytest.fixture(autouse=True)
def _limpiar():
    EJECUCIONES.clear()


@pytest.fixture
def sesion():
    request = RequestFactory().get("/")
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    return request.session


def _post(sesion, vista=_vista, **datos):
    request = RequestFactory().post("/", data=datos)
    request.session = sesion
    return vista(request)


def test_misma_clave_ejecuta_una_sola_vez(sesion):
    clave = nueva_clave()
    primera = _post(sesion, clave_idempotencia=clave, dato="a")
    segunda = _post(sesion, clave_idempotencia=clave, dato="a")
    assert EJECUCIONES == ["a"]
    assert primera.status_code == segunda.status_code == 303
    assert primera["Location"] == segunda["Location"] == "/creado/1/"


def test_clave_en_cabecera(sesion):
    clave = nueva_clave()
    for _ in range(2):
        request = RequestFactory().post("/", data={"dato": "b"}, HTTP_IDEMPOTENCY_KEY=clave)
        request.session = sesion
        _vista(request)
    assert EJECUCIONES == ["b"]


def test_misma_clave_con_otra_accion_se_rechaza(sesion):
    clave = nueva_clave()
    _post(sesion, clave_idempotencia=clave)
    respuesta = _post(sesion, vista=_otra_vista, clave_idempotencia=clave)
    assert respuesta.status_code == 400
    assert EJECUCIONES == [""]


def test_sin_clave_se_procesa_normalmente(sesion):
    _post(sesion, dato="x")
    _post(sesion, dato="x")
    assert EJECUCIONES == ["x", "x"]


def test_la_sesion_guarda_como_maximo_50_claves(sesion):
    assert MAX_CLAVES == 50
    for _ in range(MAX_CLAVES + 5):
        _post(sesion, clave_idempotencia=nueva_clave())
    entradas = sesion["claves_idempotencia"]
    assert len(entradas) == MAX_CLAVES
    assert set(entradas[0]) == {"clave", "accion", "resultado", "usada_en"}


def test_get_no_se_ve_afectado(sesion):
    request = RequestFactory().get("/")
    request.session = sesion
    _vista(request)
    assert len(EJECUCIONES) == 1
