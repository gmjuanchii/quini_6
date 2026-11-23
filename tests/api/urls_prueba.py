"""URLs solo para pruebas: una API con las mismas reglas de quini6.api y operaciones de ejemplo.

Se activa con ``@pytest.mark.urls("tests.api.urls_prueba")``.
"""

from django.http import Http404
from django.urls import include, path
from ninja import Router, Schema

from quini6.api import crear_api, nivel

api_prueba = crear_api(urls_namespace="api_prueba", docs_url=None)
rutas = Router()


class Entrada(Schema):
    numero: int


@rutas.post("/validacion/")
@nivel("P")
def validacion(request, datos: Entrada):
    return {"numero": datos.numero}


@rutas.get("/usuario/")
@nivel("U")
def solo_usuario(request):
    return {"ok": True}


@rutas.get("/administrador/")
@nivel("A")
def solo_administrador(request):
    return {"ok": True}


@rutas.get("/inexistente/")
@nivel("P")
def inexistente(request):
    raise Http404


api_prueba.add_router("", rutas)

urlpatterns = [
    path("api/v1/_prueba/", api_prueba.urls),
    path("", include("quini6.urls")),
]
