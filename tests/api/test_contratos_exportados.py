"""[003] R-13, R-16: los contratos de contratos/ coinciden con lo que genera el código."""

import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from quini6.management.commands.exportar_contratos import RUTA, generar


def test_los_contratos_versionados_estan_al_dia():
    call_command("exportar_contratos", "--verificar")


def test_verificar_falla_si_un_contrato_difiere(tmp_path, monkeypatch):
    for nombre, contenido in generar().items():
        (tmp_path / nombre).write_text(contenido, encoding="utf-8")
    datos = json.loads((tmp_path / "mensajes.json").read_text(encoding="utf-8"))
    datos["nav.menu"] = "Otro texto"
    (tmp_path / "mensajes.json").write_text(json.dumps(datos), encoding="utf-8")
    monkeypatch.setattr("quini6.management.commands.exportar_contratos.RUTA", tmp_path)
    with pytest.raises(CommandError):
        call_command("exportar_contratos", "--verificar")


def test_genera_los_tres_archivos():
    assert set(generar()) == {"openapi.json", "mensajes.json", "formatos-casos.json"}
    assert RUTA.name == "contratos"


def test_los_esquemas_de_la_api_tienen_nombres_unicos():
    """Django Ninja nombra cada esquema por su clase: dos clases con el mismo nombre en módulos
    distintos se pisarían en contratos/openapi.json ([003] R-16)."""
    import inspect

    from ninja import Schema

    from quini6.api import api

    modulos = {
        inspect.getmodule(operacion.view_func)
        for _, router in api._routers
        for vista in router.path_operations.values()
        for operacion in vista.operations
    }
    vistos: dict[str, str] = {}
    repetidos = []
    for modulo in modulos:
        for nombre, objeto in vars(modulo).items():
            propia = inspect.isclass(objeto) and objeto.__module__ == modulo.__name__
            if not propia or not issubclass(objeto, Schema):
                continue
            if nombre in vistos and vistos[nombre] != modulo.__name__:
                repetidos.append((nombre, vistos[nombre], modulo.__name__))
            vistos[nombre] = modulo.__name__
    assert not repetidos, repetidos
