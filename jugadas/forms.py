"""Formulario de jugada (R-10). El servidor valida todo con ``dominio/``; el selector de
JavaScript es solo una mejora progresiva."""

from django import forms

from dominio.importes import ErrorImporte, mensaje_error_costo, parsear_pesos
from dominio.numeros import mensaje_error, validar_jugada
from jugadas import servicios

ELEGI_CONCURSO = "Elegí el concurso de tu jugada"
OPCIONES_NUMEROS = [(f"{n:02d}", f"{n:02d}") for n in range(46)]


class SelectConcurso(forms.Select):
    """Agrega a cada opción las modalidades del concurso para la vista previa (AC-4.6)."""

    def __init__(self, *args, modalidades_por_numero=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.modalidades_por_numero = modalidades_por_numero or {}

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        opcion = super().create_option(name, value, label, selected, index, subindex, attrs)
        modalidades = self.modalidades_por_numero.get(str(value))
        if modalidades:
            opcion["attrs"]["data-modalidades"] = ", ".join(modalidades)
        return opcion


class NumerosLibres(forms.MultipleChoiceField):
    """Acepta cualquier valor: la validación de rango y repetidos la hace el dominio."""

    def valid_value(self, value):
        return True


class JugadaForm(forms.Form):
    concurso = forms.CharField(label="Concurso", required=False)
    numeros = NumerosLibres(
        label="Elegí seis números",
        choices=OPCIONES_NUMEROS,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    numero_escrito = forms.CharField(
        label="Escribí un número",
        required=False,
        max_length=4,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "off"}),
    )
    costo = forms.CharField(
        label="Costo de la jugada (en pesos)",
        required=False,
        help_text="Por ejemplo, 1500,50",
        widget=forms.TextInput(attrs={"inputmode": "decimal", "autocomplete": "off"}),
    )
    confirmar_duplicado = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, concurso_actual=None, **kwargs):
        super().__init__(*args, **kwargs)
        disponibles = list(servicios.concursos_disponibles())
        if concurso_actual is not None and concurso_actual.pk not in {c.pk for c in disponibles}:
            disponibles.insert(0, concurso_actual)
        self.disponibles = disponibles
        modalidades = {
            str(c.numero): [mc.modalidad_enum.nombre for mc in _ordenadas(c)] for c in disponibles
        }
        self.modalidades_por_numero = modalidades
        self.fields["concurso"].widget = SelectConcurso(
            choices=[("", "Elegí un concurso")]
            + [
                (str(c.numero), f"Concurso N.º {c.numero} — {c.fecha_sorteo:%d/%m/%Y}")
                for c in disponibles
            ],
            modalidades_por_numero=modalidades,
        )

    def modalidades_elegidas(self) -> list[str]:
        valor = self["concurso"].value()
        return self.modalidades_por_numero.get(str(valor or ""), [])

    def clean_concurso(self):
        valor = (self.cleaned_data.get("concurso") or "").strip()
        if not valor:
            raise forms.ValidationError(ELEGI_CONCURSO)
        resultado = servicios.resolver_concurso(valor)
        if isinstance(resultado, servicios.ErrorJugada):
            raise forms.ValidationError(resultado.mensaje)
        return resultado

    def clean_costo(self):
        valor = parsear_pesos(self.cleaned_data.get("costo") or "")
        if isinstance(valor, ErrorImporte):
            raise forms.ValidationError(mensaje_error_costo(valor))
        return valor

    def clean(self):
        datos = super().clean()
        valores = list(self.data.getlist(self.add_prefix("numeros")))
        escrito = (datos.get("numero_escrito") or "").strip()
        if escrito:
            valores.append(escrito)
        resultado = validar_jugada(valores)
        if isinstance(resultado, list):
            for error in resultado:
                self.add_error("numeros", mensaje_error(error))
        else:
            datos["numeros_validos"] = resultado
        datos["confirmar_duplicado"] = datos.get("confirmar_duplicado") == "1"
        return datos


def _ordenadas(concurso):
    from dominio.tipos import ORDEN_MODALIDADES

    orden = {m.value: i for i, m in enumerate(ORDEN_MODALIDADES)}
    return sorted(concurso.modalidades.all(), key=lambda mc: orden[mc.modalidad])
