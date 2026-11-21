"""Formulario del período de una extracción ([002] AC-1.1, AC-1.3 a AC-1.6, AC-1.20).

La validación la hace ``dominio.extraccion.periodo.validar_periodo`` (RN-01 a RN-04). Los campos
son ``<input type="date">`` (D-25): el calendario se abre con el ícono del campo y la fecha se
escribe con el teclado (D-27); el navegador agrega las barras y
envía ``AAAA-MM-DD``; sin selector de fecha, se escribe ``dd/mm/aaaa`` como antes.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from django import forms

from dominio.extraccion.periodo import ErrorPeriodo, parsear_fecha, validar_periodo

ZONA = ZoneInfo("America/Argentina/Buenos_Aires")


def hoy_buenos_aires():
    return datetime.now(ZONA).date()


class FechaConCalendario(forms.TextInput):
    """``<input type="date">`` que conserva la fecha ingresada al volver a mostrar el formulario.

    El selector de fecha solo muestra valores ``AAAA-MM-DD``: una fecha válida escrita como
    ``dd/mm/aaaa`` se convierte; un texto inválido se deja tal cual (AC-1.3, AC-1.4).
    """

    input_type = "date"

    def format_value(self, value):
        fecha = parsear_fecha(value) if isinstance(value, str) else None
        return fecha.isoformat() if fecha else super().format_value(value)


def _campo(etiqueta: str) -> forms.CharField:
    return forms.CharField(
        label=etiqueta,
        required=False,
        max_length=20,
        widget=FechaConCalendario(
            attrs={"placeholder": "dd/mm/aaaa", "autocomplete": "off"}
        ),
    )


class PeriodoForm(forms.Form):
    inicio = _campo("Fecha de inicio")
    fin = _campo("Fecha de finalización")

    def __init__(self, *args, hoy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hoy = hoy
        self.periodo = None
        maximo = (hoy or hoy_buenos_aires()).isoformat()  # el calendario no ofrece días futuros
        for campo in ("inicio", "fin"):
            self.fields[campo].widget.attrs["max"] = maximo

    def clean(self):
        datos = super().clean()
        resultado = validar_periodo(
            datos.get("inicio"), datos.get("fin"), self.hoy or hoy_buenos_aires()
        )
        if isinstance(resultado, list):
            for error in resultado:
                self._agregar(error)
        else:
            self.periodo = resultado
        return datos

    def _agregar(self, error: ErrorPeriodo):
        self.add_error(error.campo, error.texto)
