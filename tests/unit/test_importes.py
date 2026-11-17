"""RN-09, RN-43 y NFR-007: importes en pesos con Decimal."""

from decimal import Decimal

import pytest

from dominio.importes import (
    ErrorImporte,
    formatear_pesos,
    formatear_porcentaje,
    parsear_pesos,
)


class TestParsearPesos:
    @pytest.mark.parametrize(
        ("texto", "esperado"),
        [
            ("1500,50", Decimal("1500.50")),
            ("1.500,50", Decimal("1500.50")),
            ("1500", Decimal("1500")),
            ("0", Decimal("0")),
            ("1.234.567,5", Decimal("1234567.5")),
            (" 25,00 ", Decimal("25.00")),
        ],
    )
    def test_validos(self, texto, esperado):
        assert parsear_pesos(texto) == esperado

    def test_vacio(self):
        assert parsear_pesos("") == ErrorImporte("VACIO")
        assert parsear_pesos("   ") == ErrorImporte("VACIO")

    def test_negativo(self):
        assert parsear_pesos("-1") == ErrorImporte("NEGATIVO")

    @pytest.mark.parametrize("texto", ["abc", "1500.50", "1.50.0", "1,2,3", "12.34"])
    def test_no_numerico(self, texto):
        assert parsear_pesos(texto) == ErrorImporte("NO_NUMERICO")

    def test_demasiados_decimales(self):
        assert parsear_pesos("10,505") == ErrorImporte("DEMASIADOS_DECIMALES")


class TestFormatear:
    def test_pesos(self):
        assert formatear_pesos(Decimal("1500.50")) == "$ 1.500,50"
        assert formatear_pesos(Decimal("1234567.5")) == "$ 1.234.567,50"
        assert formatear_pesos(Decimal("0")) == "$ 0,00"
        assert formatear_pesos(Decimal("999")) == "$ 999,00"

    def test_porcentaje(self):
        assert formatear_porcentaje(Decimal("12.5")) == "12,50 %"
        assert formatear_porcentaje(Decimal("33.335")) == "33,34 %"  # ROUND_HALF_UP
        assert formatear_porcentaje(Decimal("100")) == "100,00 %"


@pytest.mark.parametrize("funcion", [parsear_pesos, formatear_pesos, formatear_porcentaje])
def test_float_lanza_type_error(funcion):
    with pytest.raises(TypeError):
        funcion(1500.5)
