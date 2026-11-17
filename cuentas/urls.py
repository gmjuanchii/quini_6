from django.urls import path

from cuentas import views

urlpatterns = [
    path("registrarse/", views.registrarse, name="registrarse"),
    path("ingresar/", views.ingresar, name="ingresar"),
    path("salir/", views.salir, name="salir"),
]
