"""Formularios de administración de resultados (US2, US7). Textos en es-AR."""

from django import forms

from dominio.importes import ErrorImporte, mensaje_error_importe, parsear_pesos
from dominio.numeros import mensaje_error_extraccion, validar_extraccion
from dominio.tipos import ORDEN_MODALIDADES, Modalidad, nombre_categoria

FORMATO_FECHA = ["%d/%m/%Y"]
FECHA_INVALIDA = "Ingresá una fecha válida con el formato dd/mm/aaaa."
CAMPOS_PREMIO = (
    ("ganadores", "Ganadores"),
    ("importe_categoria", "Importe destinado a la categoría"),
    ("importe_individual", "Importe individual por ganador"),
    ("pozo_vacante_acumulado", "Pozo vacante o acumulado"),
)


class _CampoFecha(forms.DateField):
    def __init__(self, **kwargs):
        kwargs.setdefault("input_formats", FORMATO_FECHA)
        kwargs.setdefault("error_messages", {"invalid": FECHA_INVALIDA, "required": FECHA_INVALIDA})
        kwargs.setdefault(
            "widget",
            forms.DateInput(
                format="%d/%m/%Y", attrs={"placeholder": "dd/mm/aaaa", "inputmode": "numeric"}
            ),
        )
        super().__init__(**kwargs)


class ConcursoForm(forms.Form):
    numero = forms.IntegerField(
        label="Número de concurso",
        min_value=1,
        error_messages={
            "required": "Ingresá el número de concurso.",
            "invalid": "Ingresá un número de concurso válido.",
            "min_value": "Ingresá un número de concurso válido.",
        },
        widget=forms.TextInput(attrs={"inputmode": "numeric"}),
    )
    fecha_sorteo = _CampoFecha(label="Fecha del sorteo")
    modalidades = forms.MultipleChoiceField(
        label="Modalidades aplicables",
        choices=[(m.value, m.nombre) for m in ORDEN_MODALIDADES],
        widget=forms.CheckboxSelectMultiple,
        error_messages={
            "required": "Elegí al menos una modalidad aplicable.",
            "invalid_choice": "Elegí modalidades válidas.",
        },
    )

    def __init__(self, *args, modificar: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        if modificar:
            del self.fields["numero"]

    def clean_modalidades(self):
        return [Modalidad(v) for v in self.cleaned_data["modalidades"]]


class _FuenteMixin(forms.Form):
    fuente_descripcion = forms.CharField(
        label="Fuente (descripción)",
        required=False,
        max_length=300,
        help_text="Por ejemplo: Extracto oficial del concurso N.º 3215.",
        error_messages={"max_length": "La descripción no puede superar los 300 caracteres."},
    )
    fuente_fecha_consulta = _CampoFecha(label="Fecha de consulta de la fuente", required=False)
    motivo_correccion = forms.CharField(
        label="Motivo de la corrección", required=False, widget=forms.Textarea(attrs={"rows": 2})
    )

    def __init__(self, *args, es_correccion: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.es_correccion = es_correccion
        if not es_correccion:
            del self.fields["motivo_correccion"]

    def clean(self):
        datos = super().clean()
        if self.es_correccion:
            if not (datos.get("motivo_correccion") or "").strip():
                self.add_error("motivo_correccion", "Indicá el motivo de la corrección.")
            if not (datos.get("fuente_descripcion") or "").strip():
                self.add_error("fuente_descripcion", "Indicá la fuente de la corrección.")
            if not datos.get("fuente_fecha_consulta") and "fuente_fecha_consulta" not in (
                self.errors
            ):
                self.add_error("fuente_fecha_consulta", "Indicá la fecha de consulta de la fuente.")
        return datos


class NumerosForm(_FuenteMixin):
    field_order = [
        "n1",
        "n2",
        "n3",
        "n4",
        "n5",
        "n6",
        "fuente_descripcion",
        "fuente_fecha_consulta",
        "motivo_correccion",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 7):
            self.fields[f"n{i}"] = forms.CharField(
                label=f"Número {i}",
                required=False,
                max_length=3,
                widget=forms.TextInput(
                    attrs={"inputmode": "numeric", "size": 3, "autocomplete": "off"}
                ),
            )
        self.order_fields(self.field_order)

    def campos_numeros(self):
        return [self[f"n{i}"] for i in range(1, 7)]

    def clean(self):
        datos = super().clean()
        valores = [(datos.get(f"n{i}") or "").strip() for i in range(1, 7)]
        valores = [v for v in valores if v != ""]
        resultado = validar_extraccion(valores)
        if isinstance(resultado, list):
            for error in resultado:
                texto = mensaje_error_extraccion(error)
                if texto not in self.non_field_errors():
                    self.add_error(None, texto)
        else:
            datos["numeros"] = resultado
        return datos


def _parsear_ganadores(texto: str):
    texto = (texto or "").strip()
    if texto == "":
        return None
    if texto.isdigit():
        return int(texto)
    raise forms.ValidationError("Ingresá una cantidad de ganadores válida (0 o más).")


class PremiosForm(_FuenteMixin):
    def __init__(self, *args, modalidad: Modalidad, **kwargs):
        super().__init__(*args, **kwargs)
        self.modalidad = modalidad
        self.filas = []
        for codigo in modalidad.categorias:
            campos = []
            for sufijo, rotulo in CAMPOS_PREMIO:
                nombre = f"{codigo}_{sufijo}"
                self.fields[nombre] = forms.CharField(
                    label=rotulo,
                    required=False,
                    widget=forms.TextInput(attrs={"inputmode": "decimal", "autocomplete": "off"}),
                )
                campos.append(nombre)
            self.filas.append((codigo, campos))
        if modalidad is Modalidad.SIEMPRE_SALE:
            self.fields["aciertos_categoria_ganadora"] = forms.ChoiceField(
                label="Cantidad de aciertos de la categoría ganadora",
                required=False,
                choices=[("", "No publicada")]
                + [(str(n), f"{n} aciertos") for n in range(6, -1, -1)],
            )
        elif modalidad is Modalidad.PREMIO_EXTRA:
            self.fields["aciertos_categoria_ganadora"] = forms.ChoiceField(
                label="Cantidad de aciertos de la categoría ganadora",
                required=False,
                choices=[
                    ("", "No publicada"),
                    ("6", "6 aciertos"),
                    ("5", "5 aciertos"),
                    ("4", "4 aciertos"),
                    ("SIN", "Sin ganadores"),
                ],
            )

    def filas_vista(self):
        aciertos = None
        if self.is_bound:
            valor = self.data.get("aciertos_categoria_ganadora")
            aciertos = int(valor) if valor and valor.isdigit() else None
        else:
            valor = self.initial.get("aciertos_categoria_ganadora")
            aciertos = int(valor) if valor not in (None, "", "SIN") else None
        return [
            {
                "codigo": codigo,
                "nombre": nombre_categoria(self.modalidad, codigo, aciertos)
                if codigo != "GANADORA"
                else "Categoría ganadora",
                "campos": [self[c] for c in campos],
            }
            for codigo, campos in self.filas
        ]

    def clean(self):
        datos = super().clean()
        por_categoria = {}
        for codigo, campos in self.filas:
            fila = {}
            for nombre in campos:
                sufijo = nombre[len(codigo) + 1 :]
                texto = (self.data.get(self.add_prefix(nombre)) or "").strip()
                try:
                    if sufijo == "ganadores":
                        if texto.startswith("-"):
                            raise forms.ValidationError(
                                "La cantidad de ganadores no puede ser negativa."
                            )
                        fila[sufijo] = _parsear_ganadores(texto)
                    elif texto == "":
                        fila[sufijo] = None
                    else:
                        valor = parsear_pesos(texto)
                        if isinstance(valor, ErrorImporte):
                            raise forms.ValidationError(mensaje_error_importe(valor))
                        fila[sufijo] = valor
                except forms.ValidationError as error:
                    self.add_error(nombre, error)
            por_categoria[codigo] = fila
        datos["datos_por_categoria"] = por_categoria
        valor = datos.get("aciertos_categoria_ganadora") or ""
        datos["sin_ganadores"] = valor == "SIN"
        datos["aciertos"] = int(valor) if valor.isdigit() else None
        return datos


class MotivoForm(forms.Form):
    motivo = forms.CharField(
        label="Motivo",
        widget=forms.Textarea(attrs={"rows": 2}),
        error_messages={"required": "Indicá el motivo."},
    )


class CorreccionForm(MotivoForm):
    fuente_descripcion = forms.CharField(
        label="Fuente de la corrección (descripción)",
        max_length=300,
        error_messages={"required": "Indicá la fuente de la corrección."},
    )
    fuente_fecha_consulta = _CampoFecha(label="Fecha de consulta de la fuente")


class PublicarForm(forms.Form):
    confirmar_advertencias = forms.BooleanField(
        label="Revisé las advertencias y confirmo que la información es correcta",
        required=False,
    )
    cotejo = forms.BooleanField(
        label="Confirmo que cotejé esta información con la fuente oficial", required=False
    )
