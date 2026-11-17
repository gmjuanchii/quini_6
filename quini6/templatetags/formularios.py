"""Ayudas de accesibilidad para formularios (NFR-003)."""

from django import template

register = template.Library()


@register.filter
def widget_accesible(campo):
    """Renderiza el control con ``aria-describedby`` hacia su ayuda y su error."""
    ids = []
    if campo.help_text:
        ids.append(f"{campo.auto_id}_ayuda")
    attrs = {}
    if campo.errors:
        ids.append(f"{campo.auto_id}_error")
        attrs["aria-invalid"] = "true"
    if ids:
        attrs["aria-describedby"] = " ".join(ids)
    return campo.as_widget(attrs=attrs)
