"""[003] R-31, FR-043, AC-14.3: avisos compartidos entre Django y Next.js (contracts/api.md § 2).

Los avisos siguen siendo los mensajes de Django en la sesión: ``GET /api/v1/avisos/`` los entrega
y los marca como leídos; ``POST /api/v1/avisos/`` agrega uno, solo por clave del catálogo.
"""

import pytest
from django.contrib import messages
from django.urls import path

from dominio.mensajes import mensaje
from quini6.urls import urlpatterns as _urls_del_sitio
from tests.api.conftest import token_csrf
from tests.fabricas import crear_usuario


def _agregar_mensajes(request):
    """Vista auxiliar: deja mensajes de Django como lo hace una vista HTML antes de redirigir."""
    from django.http import HttpResponse

    messages.success(request, mensaje("jugada.registrada"))
    messages.error(request, mensaje("ext.no_existe"))
    messages.warning(request, "Advertencia")
    messages.info(request, "Información")
    return HttpResponse("ok")


urlpatterns = [
    path("_prueba/mensajes/", _agregar_mensajes),
    *_urls_del_sitio,
]


def _post(cliente, datos, con_csrf=True):
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)} if con_csrf else {}
    return cliente.post("/api/v1/avisos/", data=datos, content_type="application/json", **extra)


@pytest.mark.urls("tests.api.test_avisos")
def test_get_entrega_los_mensajes_pendientes_y_los_marca_como_leidos(visitante):
    visitante.get("/_prueba/mensajes/")
    respuesta = visitante.get("/api/v1/avisos/")
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-store"
    assert respuesta.json() == [
        {"tipo": "exito", "texto": mensaje("jugada.registrada")},
        {"tipo": "error", "texto": mensaje("ext.no_existe")},
        {"tipo": "advertencia", "texto": "Advertencia"},
        {"tipo": "info", "texto": "Información"},
    ]
    assert visitante.get("/api/v1/avisos/").json() == []


def test_get_sin_avisos_devuelve_lista_vacia(visitante):
    respuesta = visitante.get("/api/v1/avisos/")
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_post_agrega_un_aviso_que_luego_muestra_una_plantilla_de_django(db):
    from django.test import Client

    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(crear_usuario("ana@avisos.local"))
    respuesta = _post(
        cliente,
        {"tipo": "exito", "clave": "ext.eliminada", "valores": {"fecha_hora": "21/11/2026 10:30"}},
    )
    assert respuesta.status_code == 204
    assert respuesta["Cache-Control"] == "no-store"
    contenido = cliente.get("/resultados/").content.decode()
    assert mensaje("ext.eliminada", fecha_hora="21/11/2026 10:30") in contenido
    assert mensaje("ext.eliminada", fecha_hora="21/11/2026 10:30") not in (
        cliente.get("/resultados/").content.decode()
    )


def test_post_y_get_conservan_el_tipo(visitante):
    respuesta = _post(visitante, {"tipo": "advertencia", "clave": "jugada.registrada"})
    assert respuesta.status_code == 204
    assert visitante.get("/api/v1/avisos/").json() == [
        {"tipo": "advertencia", "texto": mensaje("jugada.registrada")}
    ]


@pytest.mark.parametrize(
    "datos",
    [
        {"tipo": "exito", "clave": "no.existe"},
        {"tipo": "exito", "texto": "Texto libre"},
        {"tipo": "otro", "clave": "jugada.registrada"},
        {"tipo": "exito", "clave": "ext.eliminada"},  # faltan sus variables
        {"tipo": "exito", "clave": "ext.eliminada", "valores": {"fecha_hora": 3}},
    ],
)
def test_post_solo_acepta_claves_del_catalogo_con_sus_variables(visitante, datos):
    respuesta = _post(visitante, datos)
    assert respuesta.status_code == 422
    assert respuesta["Content-Type"].startswith("application/problem+json")
    assert visitante.get("/api/v1/avisos/").json() == []


def test_post_sin_csrf_es_403(visitante):
    respuesta = _post(visitante, {"tipo": "exito", "clave": "jugada.registrada"}, con_csrf=False)
    assert respuesta.status_code == 403
    assert visitante.get("/api/v1/avisos/").json() == []
