"""Rutas del proyecto. Solo las de contracts/rutas.md (sin django.contrib.admin, R-05b)."""

from django.urls import include, path

urlpatterns = [
    path("", include("resultados.urls")),
    path("", include("cuentas.urls")),
    path("", include("jugadas.urls")),
    path("", include("estadisticas.urls")),
    path("", include("resultados.urls_admin")),
]
