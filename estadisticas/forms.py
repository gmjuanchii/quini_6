"""Formulario de estadísticas (RN-42, RN-46, contracts/rutas.md)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from django import forms

from dominio.tipos import Modalidad

MODALIDADES = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
)
PREDETERMINADA = Modalidad.PRIMER_SORTEO
FECHA_INVALIDA = "Ingresá una fecha válida con el formato dd/mm/aaaa."
NUMERO_INVALIDO = "Ingresá un número entre 00 y 45"
PREMIO_EXTRA_NO = (
    "Premio Extra no se ofrece en las estadísticas porque no es una extracción independiente. "
    "Se muestra Tradicional – Primer Sorteo."
)


@dataclass(frozen=True)
class Consulta:
    modalidad: Modalidad = PREDETERMINADA
    desde: date | None = None
    hasta: date | None = None
    numero: int | None = None

    @property
    def valores_ocultos(self) -> dict:
        return {
            "anterior_modalidad": self.modalidad.value,
            "anterior_desde": self.desde.strftime("%d/%m/%Y") if self.desde else "",
            "anterior_hasta": self.hasta.strftime("%d/%m/%Y") if self.hasta else "",
            "anterior_numero": f"{self.numero:02d}" if self.numero is not None else "",
        }


def _fecha(texto: str) -> date | None:
    texto = (texto or "").strip()
    if not texto:
        return None
    return datetime.strptime(texto, "%d/%m/%Y").date()


def _numero(texto: str) -> int | None:
    texto = (texto or "").strip()
    if not texto:
        return None
    if not texto.isdigit() or int(texto) > 45:
        raise ValueError(NUMERO_INVALIDO)
    return int(texto)


class EstadisticasForm(forms.Form):
    modalidad = forms.ChoiceField(
        label="Modalidad",
        required=False,
        choices=[(m.value, m.nombre) for m in MODALIDADES],
    )
    desde = forms.CharField(label="Desde (dd/mm/aaaa)", required=False)
    hasta = forms.CharField(label="Hasta (dd/mm/aaaa)", required=False)
    numero = forms.CharField(label="Consultar un número (00 a 45)", required=False, max_length=2)
    anterior_modalidad = forms.CharField(required=False, widget=forms.HiddenInput)
    anterior_desde = forms.CharField(required=False, widget=forms.HiddenInput)
    anterior_hasta = forms.CharField(required=False, widget=forms.HiddenInput)
    anterior_numero = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, datos):
        super().__init__(datos)
        self.errores: list[str] = []
        self.avisos: list[str] = []

    @staticmethod
    def _modalidad(valor: str) -> Modalidad | None:
        for m in MODALIDADES:
            if m.value == valor:
                return m
        return None

    def _leer(self, prefijo: str) -> tuple[Consulta, list[str]]:
        errores = []
        valor = (self.data.get(f"{prefijo}modalidad") or "").strip()
        modalidad = self._modalidad(valor) or PREDETERMINADA
        try:
            desde = _fecha(self.data.get(f"{prefijo}desde"))
        except ValueError:
            desde, errores = None, [*errores, FECHA_INVALIDA]
        try:
            hasta = _fecha(self.data.get(f"{prefijo}hasta"))
        except ValueError:
            hasta, errores = None, [*errores, FECHA_INVALIDA]
        try:
            numero = _numero(self.data.get(f"{prefijo}numero"))
        except ValueError:
            numero, errores = None, [*errores, NUMERO_INVALIDO]
        if desde and hasta and desde > hasta:
            errores.append("PERIODO_INVALIDO")
        return Consulta(modalidad, desde, hasta, numero), errores

    def consulta_actual(self) -> tuple[Consulta, list[str]]:
        if (self.data.get("modalidad") or "") == Modalidad.PREMIO_EXTRA.value:
            self.avisos.append(PREMIO_EXTRA_NO)
        return self._leer("")

    def consulta_anterior(self) -> Consulta:
        """La consulta que se estaba mostrando; si es inválida o falta, la predeterminada."""
        consulta, errores = self._leer("anterior_")
        return Consulta() if errores else consulta
