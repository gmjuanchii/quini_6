"""[002] R-08: ida y vuelta entre los tipos del dominio y JSON (T015)."""

import json
from datetime import date
from decimal import Decimal

from dominio.extraccion.clasificacion import aplicar_clasificacion
from dominio.extraccion.consolidacion import consolidar
from dominio.extraccion.tipos import (
    NO_CORRESPONDE,
    NO_DISPONIBLE,
    SIN_DETERMINAR,
    SIN_GANADORES,
    Fuente,
    Modalidad,
    Valor,
)
from extracciones.fuentes.fichas import FICHAS
from extracciones.serializacion import (
    dato_a_json,
    dato_de_json,
    datos_fuente_a_json,
    datos_fuente_de_json,
    sorteo_a_json,
    sorteo_de_json,
)
from tests.unit.extraccion.ayudas import cambiar_categoria, datos_reales, intento


def ida_y_vuelta(dato):
    return dato_de_json(json.loads(json.dumps(dato_a_json(dato))))


def test_decimal_sin_perdida():
    assert ida_y_vuelta(Valor(Decimal("1100000000.00"))) == Valor(Decimal("1100000000.00"))
    assert dato_a_json(Valor(Decimal("1100000000.00")))["valor"] == "1100000000.00"


def test_cero_es_distinto_de_los_estados_sin_valor():
    assert ida_y_vuelta(Valor(0)) == Valor(0)
    for estado in (NO_DISPONIBLE, NO_CORRESPONDE, SIN_DETERMINAR):
        assert ida_y_vuelta(estado) is estado
        assert ida_y_vuelta(estado) != Valor(0)


def test_otros_tipos_de_valor():
    for valor in (date(2026, 11, 15), frozenset({1, 45}), True, SIN_GANADORES, 18):
        assert ida_y_vuelta(Valor(valor)) == Valor(valor)


def _sin_float(objeto):
    if isinstance(objeto, float):
        raise AssertionError("float en el JSON")
    if isinstance(objeto, dict):
        for v in objeto.values():
            _sin_float(v)
    if isinstance(objeto, list):
        for v in objeto:
            _sin_float(v)


def test_datos_de_una_fuente_ida_y_vuelta_sin_float():
    datos = datos_reales(Fuente.F1)
    como_json = json.loads(json.dumps(datos_fuente_a_json(datos)))
    _sin_float(como_json)
    assert datos_fuente_de_json(como_json) == datos


def test_sorteo_consolidado_ida_y_vuelta_con_discrepancias():
    f3 = cambiar_categoria(
        datos_reales(Fuente.F3),
        Modalidad.LA_SEGUNDA,
        "TERCER",
        importe_individual=Valor(Decimal("5547.85")),
    )
    s = aplicar_clasificacion(
        consolidar(3426, [intento(datos_reales(Fuente.F2)), intento(f3)], FICHAS)
    )
    como_json = json.loads(json.dumps(sorteo_a_json(s)))
    _sin_float(como_json)
    assert sorteo_de_json(como_json) == s
