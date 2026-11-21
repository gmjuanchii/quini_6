"""[002] RN-01 a RN-04, I-01: validación del período (T019)."""

from datetime import date

import pytest

from dominio.extraccion.periodo import (
    FECHA_INVALIDA,
    FIN_FUTURA,
    INICIO_POSTERIOR,
    PERIODO_LARGO,
    Periodo,
    mismo_dia_anio_siguiente,
    validar_periodo,
)

HOY = date(2026, 11, 19)


def codigos(resultado):
    return [(e.codigo, e.campo) for e in resultado]


def test_ac_1_3_inicio_posterior():
    resultado = validar_periodo("15/11/2026", "01/11/2026", HOY)
    assert codigos(resultado) == [("INICIO_POSTERIOR", None)]
    assert resultado[0].texto == INICIO_POSTERIOR


@pytest.mark.parametrize("inicio, fin, campo", [
    ("", "01/11/2026", "inicio"),
    ("31/02/2026", "01/11/2026", "inicio"),
    ("01/11/2026", "", "fin"),
    ("01/11/2026", "15-11-2026", "fin"),
    ("01/11/2026", "2026-02-30", "fin"),
])  # fmt: skip
def test_ac_1_4_fecha_vacia_o_invalida_junto_al_campo(inicio, fin, campo):
    resultado = validar_periodo(inicio, fin, HOY)
    assert codigos(resultado) == [("FECHA_INVALIDA", campo)]
    assert resultado[0].texto == FECHA_INVALIDA == "Ingresá una fecha válida (dd/mm/aaaa)"


def test_ac_1_5_fin_posterior_a_hoy():
    resultado = validar_periodo("01/11/2026", "20/11/2026", HOY)
    assert codigos(resultado) == [("FIN_FUTURA", "fin")]
    assert resultado[0].texto == FIN_FUTURA


def test_ac_1_6_periodo_de_mas_de_12_meses():
    resultado = validar_periodo("01/01/2026", "01/01/2027", date(2027, 6, 1))
    assert codigos(resultado) == [("PERIODO_LARGO", None)]
    assert resultado[0].texto == PERIODO_LARGO


def test_ac_1_6_un_anio_calendario_es_valido():
    assert validar_periodo("01/01/2026", "31/12/2026", date(2027, 1, 5)) == Periodo(
        date(2026, 1, 1), date(2026, 12, 31)
    )


def test_rn_01_periodo_de_un_solo_dia():
    assert validar_periodo("15/11/2026", "15/11/2026", HOY) == Periodo(
        date(2026, 11, 15), date(2026, 11, 15)
    )


def test_i_01_veintinueve_de_febrero():
    assert mismo_dia_anio_siguiente(date(2024, 2, 29)) == date(2025, 3, 1)
    assert isinstance(validar_periodo("29/02/2024", "28/02/2025", HOY), Periodo)
    assert codigos(validar_periodo("29/02/2024", "01/03/2025", HOY)) == [("PERIODO_LARGO", None)]


def test_periodo_contiene_los_extremos():
    periodo = Periodo(date(2026, 11, 1), date(2026, 11, 15))
    assert periodo.contiene(date(2026, 11, 1)) and periodo.contiene(date(2026, 11, 15))
    assert not periodo.contiene(date(2026, 10, 31))


def test_d_25_acepta_la_fecha_del_selector_del_navegador():
    """AC-1.20: ``<input type="date">`` envía AAAA-MM-DD; dd/mm/aaaa se sigue aceptando."""
    assert validar_periodo("2026-11-01", "15/11/2026", HOY) == Periodo(
        date(2026, 11, 1), date(2026, 11, 15)
    )
