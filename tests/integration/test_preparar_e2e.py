"""[003] R-23, T032, T097: datos deterministas para los recorridos E2E."""

import io
import json

import pytest
from django.core.management import CommandError, call_command

from cuentas.models import Usuario
from extracciones.models import Extraccion
from quini6.management.commands import preparar_e2e
from resultados.models import Concurso


@pytest.fixture
def credenciales(tmp_path, monkeypatch):
    ruta = tmp_path / ".credenciales.json"
    monkeypatch.setattr(preparar_e2e, "CREDENCIALES", ruta)
    return ruta


@pytest.mark.django_db(transaction=True)
def test_se_niega_sin_debug_y_e2e(settings, credenciales):
    settings.DEBUG, settings.QUINI6_E2E = False, False
    with pytest.raises(CommandError):
        call_command("preparar_e2e")
    assert not credenciales.exists()


@pytest.mark.django_db(transaction=True)
def test_vacio_solo_crea_las_cuentas(settings, credenciales):
    """T097: ``--vacio`` deja la base sin sorteos, jugadas ni extracciones (HU-08)."""
    settings.DEBUG, settings.QUINI6_E2E = True, True
    call_command("preparar_e2e", "--vacio", stdout=io.StringIO())
    assert Concurso.objects.count() == 0
    assert Extraccion.objects.count() == 0
    datos = json.loads(credenciales.read_text(encoding="utf-8"))
    assert {"admin", "usuaria", "sinjugadas"} <= set(datos)
    assert Usuario.objects.filter(email=datos["admin"]["correo"], es_administrador=True).exists()
