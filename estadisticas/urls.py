from django.urls import path

from estadisticas import views

urlpatterns = [
    path("estadisticas/", views.index, name="estadisticas"),
]
