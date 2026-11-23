"""[003] contracts/formatos.md: los filtros de Django producen la salida de la tabla compartida."""

import json
from datetime import date, datetime
from decimal import Decimal

import pytest
from django.conf import settings

from quini6.templatetags.formato_ar import (
    cantidad_ar,
    dos_digitos,
    fecha_ar,
    fecha_hora_ar,
    pesos,
    porcentaje_ar,
)

CASOS = json.loads(
    (settings.BASE_DIR / "contratos" / "formatos-casos.json").read_text(encoding="utf-8")
)


def _formatear(tipo: str, entrada: str) -> str:
    if tipo == "fecha":
        return fecha_ar(date.fromisoformat(entrada))
    if tipo == "fecha_hora":
        return fecha_hora_ar(datetime.fromisoformat(entrada.replace("Z", "+00:00")))
    if tipo == "importe":
        return pesos(entrada)
    if tipo == "porcentaje":
        return porcentaje_ar(Decimal(entrada))
    if tipo == "bolilla":
        return dos_digitos(int(entrada))
    if tipo == "cantidad":
        return cantidad_ar(int(entrada))
    raise AssertionError(f"Tipo de caso desconocido: {tipo}")


def test_hay_casos():
    assert len(CASOS) >= 10


@pytest.mark.parametrize("caso", CASOS, ids=lambda c: f"{c['tipo']}:{c['entrada']}")
def test_cada_caso_da_la_salida_esperada(caso):
    assert _formatear(caso["tipo"], caso["entrada"]) == caso["salida"]
