"""Rutas de la extracción histórica ([002] contracts/rutas.md). Todas de nivel Admin."""

from django.urls import path

from extracciones import views

urlpatterns = [
    path("administracion/extracciones/", views.inicio),
    path("administracion/extracciones/<int:id>/", views.extraccion),
    path("administracion/extracciones/<int:id>/sorteos/<int:numero>/", views.sorteo),
    path("administracion/extracciones/<int:id>/eliminar/", views.eliminar),  # D-24
    path("administracion/extracciones/<int:id>/csv/", views.descargar_csv),
]
