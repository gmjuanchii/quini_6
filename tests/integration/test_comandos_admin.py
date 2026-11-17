"""contracts/comandos.md: otorgar_admin y quitar_admin (RN-37)."""

from io import StringIO

import pytest
from django.core.management import CommandError, call_command

from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db


def test_otorgar_admin():
    usuario = crear_usuario("ana@prueba.local")
    salida = StringIO()
    call_command("otorgar_admin", "ANA@prueba.local", stdout=salida)
    usuario.refresh_from_db()
    assert usuario.es_administrador is True
    assert "Se otorgó el permiso de administrador a ana@prueba.local." in salida.getvalue()


def test_quitar_admin():
    usuario = crear_usuario("ana@prueba.local", admin=True)
    salida = StringIO()
    call_command("quitar_admin", "ana@prueba.local", stdout=salida)
    usuario.refresh_from_db()
    assert usuario.es_administrador is False
    assert "Se quitó el permiso de administrador a ana@prueba.local." in salida.getvalue()


@pytest.mark.parametrize("comando", ["otorgar_admin", "quitar_admin"])
def test_correo_inexistente(comando):
    with pytest.raises(CommandError) as error:
        call_command(comando, "nadie@prueba.local")
    assert str(error.value) == "No existe una cuenta con el correo nadie@prueba.local."
    assert error.value.returncode == 1
