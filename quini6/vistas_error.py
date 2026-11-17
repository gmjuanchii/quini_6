"""Manejadores de error en español (NFR-001, NFR-008). No agregan rutas."""

from django.shortcuts import render

FORMULARIO_VENCIDO = (
    "No pudimos procesar el formulario porque venció. Volvé a cargar la página e intentá de nuevo."
)


def csrf_fallido(request, reason=""):
    """Reemplaza la página técnica de Django ante un token CSRF ausente o inválido."""
    return render(
        request,
        "403.html",
        {"mensaje": FORMULARIO_VENCIDO, "titulo": "Formulario vencido"},
        status=403,
    )
