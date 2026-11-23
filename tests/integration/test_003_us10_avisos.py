"""[003] HU-10: avisos importantes que se noten (AC-10.2, AC-10.3, RN-09, FR-029)."""

import re

import pytest
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.template.loader import render_to_string
from django.test import RequestFactory

from dominio.mensajes import MENSAJES

pytestmark = pytest.mark.django_db

#: RN-09: nivel de Django → (variante del Callout, icono, rol, tipo de Toast).
CASOS = {
    messages.SUCCESS: ("success", "circle-check", "status", "success"),
    messages.INFO: ("info", "info", "status", "info"),
    messages.WARNING: ("warning", "triangle-alert", "status", "warning"),
    messages.ERROR: ("danger", "circle-x", "alert", "error"),
}


def _pagina_con_mensajes() -> str:
    request = RequestFactory().get("/resultados/")
    request.session = SessionStore()
    request.user = AnonymousUser()
    request._messages = FallbackStorage(request)
    for nivel in CASOS:
        messages.add_message(request, nivel, f"Texto de nivel {nivel}")
    return render_to_string("base.html", request=request)


def _avisos_en_main(contenido: str) -> dict[str, str]:
    main = re.search(r"<main\b.*?</main>", contenido, re.S).group(0)
    avisos = re.findall(r'(<div\b[^>]*data-aviso="[^"]+"[^>]*>.*?</div>\s*</div>)', main, re.S)
    return {re.search(r'data-aviso="([^"]+)"', a).group(1): a for a in avisos}


def test_rn_09_cada_tipo_con_su_variante_icono_y_rol(db):
    avisos = _avisos_en_main(_pagina_con_mensajes())
    assert set(avisos) == {"success", "info", "warning", "error"}
    for nivel, (variante, icono, rol, tipo) in CASOS.items():
        aviso = avisos[tipo]
        apertura = aviso.split(">", 1)[0]
        assert f'role="{rol}"' in apertura, tipo
        assert f"bg-{variante}-soft" in apertura or (
            variante == "info" and "bg-info-soft" in apertura
        ), tipo
        assert f"Texto de nivel {nivel}" in aviso
        icono_svg = (
            open(f"templates/ui/iconos/{icono}.svg", encoding="utf-8").read().split(">", 1)[1][:60]
        )
        assert icono_svg in aviso, (tipo, icono)


def test_rn_09_misma_ubicacion_al_comienzo_del_contenido(db):
    contenido = _pagina_con_mensajes()
    main = re.search(r"<main\b.*?</main>", contenido, re.S).group(0)
    region = re.search(r"<div\b[^>]*data-mensajes[^>]*>", main)
    assert region and region.start() < 200  # primero dentro de <main>


def test_ac_10_3_region_de_toasts_anunciada(client):
    contenido = client.get("/resultados/").content.decode()
    assert 'aria-live="polite"' in contenido and 'aria-live="assertive"' in contenido
    assert MENSAJES["aviso.cerrar"] in contenido


def test_ac_10_2_pie_legal_legible(client):
    contenido = client.get("/estadisticas/").content.decode()
    pie = re.search(r"<footer\b.*?</footer>", contenido, re.S).group(0)
    parrafo = re.search(r"<p\b[^>]*data-pie-legal[^>]*>(.*?)</p>", pie, re.S)
    assert parrafo and MENSAJES["pie.legal"] in parrafo.group(1)
    clases = re.search(r'class="([^"]*)"', parrafo.group(0)).group(1).split()
    assert "text-sm" in clases and "text-muted-foreground" in clases
    assert "italic" not in clases


def test_sin_mensajes_no_hay_region_vacia_con_rol(client):
    main = re.search(r"<main\b.*?</main>", client.get("/resultados/").content.decode(), re.S)
    assert "data-aviso=" not in main.group(0)
