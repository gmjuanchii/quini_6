from django.urls import path

from jugadas import views

urlpatterns = [
    path("mis-jugadas/", views.lista, name="jugadas_lista"),
    path("mis-jugadas/nueva/", views.nueva, name="jugadas_nueva"),
    path("mis-jugadas/<int:id>/", views.detalle, name="jugadas_detalle"),
    path("mis-jugadas/<int:id>/editar/", views.editar, name="jugadas_editar"),
    path("mis-jugadas/<int:id>/eliminar/", views.eliminar, name="jugadas_eliminar"),
]
