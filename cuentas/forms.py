"""Formularios de cuentas: solo correo y contraseña (RN-39)."""

from django import forms

CORREO_INVALIDO = "Ingresá un correo electrónico válido."
CONTRASENA_CORTA = "La contraseña debe tener al menos 8 caracteres."


class RegistroForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        max_length=254,
        error_messages={"required": CORREO_INVALIDO, "invalid": CORREO_INVALIDO},
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        error_messages={"required": CONTRASENA_CORTA},
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Al menos 8 caracteres.",
    )

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError(CONTRASENA_CORTA)
        return password


class IngresoForm(forms.Form):
    email = forms.CharField(
        label="Correo electrónico",
        error_messages={"required": "Ingresá tu correo electrónico."},
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        error_messages={"required": "Ingresá tu contraseña."},
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
