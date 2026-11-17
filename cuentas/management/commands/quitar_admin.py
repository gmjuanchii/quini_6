"""Quita el permiso de administrador a una cuenta existente (contracts/comandos.md, RN-37)."""

from django.core.management.base import BaseCommand, CommandError

from cuentas.models import Usuario, UsuarioManager


class Command(BaseCommand):
    help = "Quita el permiso de administrador a la cuenta con el correo indicado."

    def add_arguments(self, parser):
        parser.add_argument("correo")

    def handle(self, *args, **opciones):
        correo = UsuarioManager.normalizar(opciones["correo"])
        usuario = Usuario.objects.filter(email=correo).first()
        if usuario is None:
            raise CommandError(f"No existe una cuenta con el correo {correo}.", returncode=1)
        usuario.es_administrador = False
        usuario.save(update_fields=["es_administrador"])
        self.stdout.write(f"Se quitó el permiso de administrador a {correo}.")
