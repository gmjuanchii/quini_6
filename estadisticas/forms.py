"""Formulario de estadísticas (RN-42, RN-46, contracts/rutas.md)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from django import forms

from dominio.extraccion.periodo import parsear_fecha
from dominio.mensajes import MENSAJES, mensaje
from dominio.periodos import error_de_fecha
from dominio.tipos import Modalidad

MODALIDADES = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
)
PREDETERMINADA = Modalidad.PRIMER_SORTEO
FECHA_INVALIDA = MENSAJES["gral.fecha_invalida"]
NUMERO_INVALIDO = MENSAJES["jugada.fuera_de_rango"]  # [003] AC-7.6
PREMIO_EXTRA_NO = (
    "Premio Extra no se ofrece en las estadísticas porque no tiene números sorteados propios. "
    "Se muestra Tradicional – Primer Sorteo."
)
#: [003] AC-7.5: orden de la tabla (solo presentación, NFR-009); inválido → por número ascendente.
COLUMNAS_ORDEN = ("numero", "frecuencia")
ORDEN_PREDETERMINADO = "numero"


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
    """``dd/mm/aaaa`` o, sin scripts, ``AAAA-MM-DD`` del calendario del navegador ([003] R-07)."""
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        fecha = parsear_fecha(texto) if "-" in texto else None
        if fecha is None:
            raise
        return fecha


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
    # [003] AC-7.3: etiquetas breves; el formato y el rango van en la ayuda asociada.
    desde = forms.CharField(label="Desde", required=False)
    hasta = forms.CharField(label="Hasta", required=False)
    numero = forms.CharField(
        label="Número", required=False, max_length=2, help_text=MENSAJES["est.numero_ayuda"]
    )
    anterior_modalidad = forms.CharField(required=False, widget=forms.HiddenInput)
    anterior_desde = forms.CharField(required=False, widget=forms.HiddenInput)
    anterior_hasta = forms.CharField(required=False, widget=forms.HiddenInput)
    anterior_numero = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, datos):
        super().__init__(datos)
        self.errores: list[str] = []
        self.avisos: list[str] = []
        #: [003] AC-4.5, FR-012: mensaje concreto junto a cada campo (además del resumen).
        self.errores_campo: dict[str, str] = {}
        #: [003] contracts/api.md: clave del catálogo de cada error de campo (para la API).
        self.claves_campo: dict[str, str] = {}

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
        consulta, errores = self._leer("")
        self._errores_por_campo(consulta, errores)
        return consulta, errores

    def _errores_por_campo(self, consulta: Consulta, errores: list[str]) -> None:
        for nombre in ("desde", "hasta"):
            texto = self.data.get(nombre)
            try:
                _fecha(texto)
            except ValueError:
                clave, valores = error_de_fecha(texto) or ("gral.fecha_invalida", {})
                self.errores_campo[nombre] = mensaje(clave, **valores)
                self.claves_campo[nombre] = clave
        if NUMERO_INVALIDO in errores:
            self.errores_campo["numero"] = NUMERO_INVALIDO
            self.claves_campo["numero"] = "jugada.fuera_de_rango"
        if "PERIODO_INVALIDO" in errores:
            desde = consulta.desde.strftime("%d/%m/%Y") if consulta.desde else ""
            self.errores_campo["hasta"] = mensaje("fecha.fin_anterior", fecha=desde)
            self.claves_campo["hasta"] = "fecha.fin_anterior"

    def consulta_anterior(self) -> Consulta:
        """La consulta que se estaba mostrando; si es inválida o falta, la predeterminada."""
        consulta, errores = self._leer("anterior_")
        return Consulta() if errores else consulta
