"""Ayudas de accesibilidad para formularios (NFR-003)."""

from django import template

from quini6.templatetags.ui import reglas

register = template.Library()


@register.filter
def widget_accesible(campo):
    """Control con ``aria-describedby`` hacia su ayuda y su error, y sus reglas previas."""
    ids = []
    if campo.help_text:
        ids.append(f"{campo.auto_id}_ayuda")
    attrs = {}
    if campo.errors:
        ids.append(f"{campo.auto_id}_error")
        attrs["aria-invalid"] = "true"
    if ids:
        attrs["aria-describedby"] = " ".join(ids)
    if datos := reglas(campo):  # [003] FR-033: reglas de la validación previa
        attrs["data-validar"] = datos
    return campo.as_widget(attrs=attrs)
