"""Formulario del período de una extracción ([002] AC-1.1, AC-1.3 a AC-1.6, AC-1.20).

La validación la hace ``dominio.extraccion.periodo.validar_periodo`` (RN-01 a RN-04). Los campos
son ``<input type="date">`` (D-25): el calendario se abre con el ícono del campo y la fecha se
escribe con el teclado (D-27); el navegador agrega las barras y
envía ``AAAA-MM-DD``; sin selector de fecha, se escribe ``dd/mm/aaaa`` como antes.
"""

from django import forms

from dominio.extraccion.periodo import ErrorPeriodo, parsear_fecha, validar_periodo
from dominio.mensajes import mensaje
from dominio.periodos import error_de_fecha
from quini6.fechas import ZONA, FechaConCalendario, hoy_buenos_aires, regla, regla_fecha

__all__ = ["ZONA", "FechaConCalendario", "PeriodoForm", "hoy_buenos_aires"]

#: [003] AC-4.5, FR-012: mensaje junto a cada campo de fecha (clave del catálogo si falta).
_FALTA = {"inicio": "fecha.falta_inicio", "fin": "fecha.falta_fin"}
#: Clave del catálogo de cada error de [002] RN-01 a RN-04 (mismo texto, contracts/mensajes.md).
_CLAVE_DE_CODIGO = {
    "INICIO_POSTERIOR": "ext.inicio_posterior",
    "FIN_FUTURA": "ext.fin_futura",
    "PERIODO_LARGO": "ext.periodo_largo",
}


def _campo(etiqueta: str) -> forms.CharField:
    return forms.CharField(
        label=etiqueta,
        required=False,
        max_length=20,
        widget=FechaConCalendario(attrs={"placeholder": "dd/mm/aaaa", "autocomplete": "off"}),
    )


class PeriodoForm(forms.Form):
    inicio = _campo("Fecha de inicio")
    fin = _campo("Fecha de finalización")

    def __init__(self, *args, hoy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.hoy = hoy
        self.periodo = None
        #: [003] contracts/api.md: (campo, clave del catálogo, valores) de cada error, para la API.
        self.errores_catalogo: list[tuple[str, str, dict]] = []
        maximo = (hoy or hoy_buenos_aires()).isoformat()  # el calendario no ofrece días futuros
        for campo in ("inicio", "fin"):
            self.fields[campo].widget.attrs["max"] = maximo
            # [003] FR-033, R-13: reglas de la validación previa (el servidor las repite).
            self.fields[campo].reglas_previas = [
                regla("requerido", _FALTA[campo]),
                regla_fecha(),
            ]
        self.fields["fin"].reglas_previas += [
            regla("max", "ext.fin_futura", valor=maximo),
            regla("fin_no_anterior_a", "fecha.fin_anterior", campo=self["inicio"].auto_id),
        ]

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

    def _registrar(self, campo: str | None, clave: str, valores: dict, texto: str) -> None:
        self.add_error(campo, texto)
        self.errores_catalogo.append((campo or "", clave, valores))

    def _agregar(self, error: ErrorPeriodo):
        if error.codigo == "FECHA_INVALIDA":
            # [003] AC-4.5: el mensaje concreto (falta, no existe o formato) junto al campo.
            clave, valores = error_de_fecha(self.data.get(error.campo), _FALTA[error.campo])
            self._registrar(error.campo, clave, valores, mensaje(clave, **valores))
            return
        self._registrar(error.campo, _CLAVE_DE_CODIGO[error.codigo], {}, error.texto)
        if error.codigo == "INICIO_POSTERIOR":
            # [003] AC-4.5: además del resumen general de [002], el mensaje junto al fin.
            valores = {"fecha": _dd_mm_aaaa(self.data.get("inicio"))}
            self._registrar(
                "fin", "fecha.fin_anterior", valores, mensaje("fecha.fin_anterior", **valores)
            )


def _dd_mm_aaaa(texto: str | None) -> str:
    fecha = parsear_fecha(texto)
    return fecha.strftime("%d/%m/%Y") if fecha else (texto or "")
