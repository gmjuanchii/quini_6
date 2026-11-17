"""Rutas de administración de contracts/rutas.md."""

from django.urls import path, register_converter

from dominio.tipos import Modalidad
from resultados import views_admin as v


class ModalidadConverter:
    regex = "primer-sorteo|la-segunda|revancha|siempre-sale|premio-extra"

    def to_python(self, valor: str) -> Modalidad:
        return Modalidad.desde_slug(valor)

    def to_url(self, valor) -> str:
        return valor.slug if isinstance(valor, Modalidad) else str(valor)


class BloqueConverter:
    regex = "numeros|premios"

    def to_python(self, valor: str) -> str:
        return valor

    def to_url(self, valor: str) -> str:
        return valor


register_converter(ModalidadConverter, "modalidad")
register_converter(BloqueConverter, "bloque")

P = "administracion/concursos/"
B = P + "<int:numero>/<modalidad:modalidad>/<bloque:bloque>/"

urlpatterns = [
    path(P, v.listado, name="admin_listado"),
    path(P + "nuevo/", v.nuevo, name="admin_nuevo"),
    path(P + "<int:numero>/", v.panel, name="admin_panel"),
    path(P + "<int:numero>/modificar/", v.modificar, name="admin_modificar"),
    path(P + "<int:numero>/historial/", v.historial, name="admin_historial"),
    path(P + "<int:numero>/<modalidad:modalidad>/numeros/", v.numeros, name="admin_numeros"),
    path(P + "<int:numero>/<modalidad:modalidad>/premios/", v.premios, name="admin_premios"),
    path(B + "observar/", v.observar, name="admin_observar"),
    path(B + "resolver/", v.resolver, name="admin_resolver"),
    path(B + "publicar/", v.publicar, name="admin_publicar"),
    path(B + "revision/", v.revision, name="admin_revision"),
    path(B + "quitar-revision/", v.quitar_revision, name="admin_quitar_revision"),
    path(B + "corregir/", v.corregir, name="admin_corregir"),
]
