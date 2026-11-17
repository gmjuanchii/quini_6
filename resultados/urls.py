from django.urls import path

from resultados import views_publicas as v

urlpatterns = [
    path("", v.inicio, name="inicio"),
    path("resultados/", v.resultados, name="resultados"),
    path("resultados/buscar/", v.buscar, name="resultados_buscar"),
    path("resultados/<int:numero>/", v.detalle, name="resultados_detalle"),
]
