"""Fechas de los formularios ([003] HU-04, R-07): "hoy" en Buenos Aires y el campo de fecha.

El servidor genera siempre ``<input type="date">`` (sin scripts es el calendario del navegador);
``static/js/ui.js`` lo convierte en un campo de texto ``dd/mm/aaaa`` con el calendario propio.
El dominio acepta los dos formatos ([002] RN-02, D-25).
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django import forms

from dominio.extraccion.periodo import parsear_fecha
from dominio.mensajes import MENSAJES

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")


def hoy_buenos_aires() -> date:
    return datetime.now(ZONA).date()


def valor_iso(valor) -> str:
    """Valor para ``<input type="date">``: una fecha válida en ``AAAA-MM-DD``; un texto que no es
    fecha se deja tal cual (el navegador lo descarta, el mensaje junto al campo lo explica)."""
    if isinstance(valor, date):
        return valor.isoformat()
    texto = "" if valor is None else str(valor).strip()
    fecha = parsear_fecha(texto)
    return fecha.isoformat() if fecha else texto


class FechaConCalendario(forms.TextInput):
    """``<input type="date">`` que conserva la fecha ingresada al volver a mostrar el formulario
    ([002] D-25, AC-1.3, AC-1.4; [003] FR-010)."""

    input_type = "date"

    def format_value(self, value):
        return valor_iso(value) or None


def regla(nombre: str, clave: str, **extra) -> dict:
    """Regla de la validación previa ([003] FR-033, R-13) con su texto del catálogo ya resuelto.

    Los textos con variables (``{fecha}``) se entregan sin completar: los completa el navegador
    con el valor que corresponda, igual que lo hace el servidor al repetir la validación.
    """
    return {"regla": nombre, "texto": MENSAJES[clave], **extra}


def regla_fecha() -> dict:
    """Formato y existencia de la fecha: ``gral.fecha_invalida`` o ``fecha.inexistente``."""
    return regla("fecha", "gral.fecha_invalida", texto_inexistente=MENSAJES["fecha.inexistente"])
