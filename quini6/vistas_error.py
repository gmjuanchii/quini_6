"""Manejadores de error en español (NFR-001, NFR-008). No agregan rutas."""

from django.shortcuts import render

from dominio.mensajes import MENSAJES

FORMULARIO_VENCIDO = MENSAJES["gral.csrf_vencido"]


def csrf_fallido(request, reason=""):
    """Reemplaza la página técnica de Django ante un token CSRF ausente o inválido."""
    return render(
        request,
        "403.html",
        {"mensaje": FORMULARIO_VENCIDO, "titulo": MENSAJES["api.titulo_csrf"]},
        status=403,
    )
