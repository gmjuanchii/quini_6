"""Rutas del proyecto. Solo las de contracts/rutas.md (sin django.contrib.admin, R-05b)."""

from django.urls import include, path

from quini6.api import api
from quini6.tema import preferencia_tema

urlpatterns = [
    path("api/v1/", api.urls),  # [003] R-16
    path("preferencias/tema/", preferencia_tema, name="preferencia_tema"),  # [003] R-14
    path("", include("resultados.urls")),
    path("", include("cuentas.urls")),
    path("", include("jugadas.urls")),
    path("", include("estadisticas.urls")),
    path("", include("resultados.urls_admin")),
    path("", include("extracciones.urls")),
]
