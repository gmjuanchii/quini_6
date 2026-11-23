"""Formularios de cuentas: solo correo y contraseña (RN-39).

[003] HU-06, HU-11: textos del catálogo único; reglas previas (FR-033) que el servidor repite.
"""

from django import forms

from dominio.mensajes import MENSAJES
from quini6.fechas import regla

CORREO_INVALIDO = MENSAJES["cuenta.correo_invalido"]
CONTRASENA_CORTA = MENSAJES["cuenta.contrasena_corta"]


def _correo() -> forms.EmailField:
    campo = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        error_messages={"required": MENSAJES["cuenta.falta_correo"], "invalid": CORREO_INVALIDO},
        widget=forms.EmailInput(attrs={"autocomplete": "email", "spellcheck": "false"}),
    )
    campo.reglas_previas = [regla("correo", "cuenta.correo_invalido")]  # AC-6.4
    return campo


def _contrasena(autocompletar: str, **extra) -> forms.CharField:
    return forms.CharField(
        label="Contraseña",
        strip=False,
        error_messages={"required": MENSAJES["cuenta.falta_contrasena"]},
        widget=forms.PasswordInput(attrs={"autocomplete": autocompletar}),  # AC-6.5
        **extra,
    )


class RegistroForm(forms.Form):
    email = _correo()
    password = _contrasena("new-password", help_text="Al menos 8 caracteres.")

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError(CONTRASENA_CORTA)
        return password


class IngresoForm(forms.Form):
    """El formato del correo se valida igual que en el navegador; un correo bien escrito que no
    existe recibe el mismo mensaje que una contraseña incorrecta ([001] AC-3.5)."""

    email = _correo()
    password = _contrasena("current-password")
