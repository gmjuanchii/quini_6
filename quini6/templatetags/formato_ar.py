"""Filtros de formato argentino (R-09, Const. VII). Delegan en ``dominio/``."""

from datetime import date, datetime
from decimal import Decimal

from django import template
from django.utils import timezone

from dominio.importes import formatear_pesos, formatear_porcentaje
from dominio.numeros import formatear

register = template.Library()


def _local(valor: datetime) -> datetime:
    if timezone.is_aware(valor):
        return timezone.localtime(valor)
    return valor


@register.filter
def fecha_ar(valor):
    """``dd/mm/aaaa`` en la hora local de Buenos Aires."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, datetime):
        valor = _local(valor)
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return valor


@register.filter
def fecha_hora_ar(valor):
    """``dd/mm/aaaa HH:MM`` en la hora local de Buenos Aires."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, datetime):
        return _local(valor).strftime("%d/%m/%Y %H:%M")
    return fecha_ar(valor)


@register.filter
def pesos(valor):
    """``$ 1.234,56``; con ``None`` devuelve cadena vacía."""
    if valor is None or valor == "":
        return ""
    if isinstance(valor, str):
        valor = Decimal(valor)
    return formatear_pesos(valor)


@register.filter
def dos_digitos(valor):
    """``7`` → ``07``."""
    if valor is None or valor == "":
        return ""
    return formatear(int(valor))


@register.filter
def porcentaje_ar(valor):
    """``Decimal("12.5")`` → ``12,50 %``."""
    if valor is None or valor == "":
        return ""
    return formatear_porcentaje(valor)


@register.filter
def cantidad_ar(valor):
    """``1500`` → ``1.500`` (cantidades enteras, [003] contracts/formatos.md)."""
    if valor is None or valor == "":
        return ""
    return f"{int(valor):,}".replace(",", ".")


@register.filter
def ordenados(valor):
    """Números en orden ascendente (Supuestos de la spec)."""
    if not valor:
        return []
    return sorted(valor)
