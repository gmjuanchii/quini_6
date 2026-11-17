"""RN-01 a RN-03, RN-14 y RN-31: números de jugadas y extracciones."""

import pytest

from dominio.numeros import (
    ErrorNumero,
    conjunto_premio_extra,
    formatear,
    misma_combinacion,
    parsear_numero,
    validar_extraccion,
    validar_jugada,
)


class TestParsearNumero:
    def test_dos_digitos(self):
        assert parsear_numero("07") == 7

    def test_limites(self):
        assert parsear_numero("00") == 0
        assert parsear_numero("45") == 45

    @pytest.mark.parametrize("texto", ["46", "-1", "100"])
    def test_fuera_de_rango(self, texto):
        assert parsear_numero(texto) == ErrorNumero("FUERA_DE_RANGO")

    @pytest.mark.parametrize("texto", ["abc", "", "  ", "4.5", "7a"])
    def test_no_numerico(self, texto):
        assert parsear_numero(texto) == ErrorNumero("NO_NUMERICO")


@pytest.mark.parametrize("validar", [validar_jugada, validar_extraccion])
class TestValidar:
    def test_faltan(self, validar):
        assert validar(["01", "02", "03", "04"]) == [ErrorNumero("FALTAN_N", cantidad=2)]

    def test_sobran(self, validar):
        assert validar(["01", "02", "03", "04", "05", "06", "07"]) == [ErrorNumero("SOBRAN")]

    def test_repetido(self, validar):
        errores = validar(["07", "07", "01", "02", "03", "04"])
        assert ErrorNumero("REPETIDO", numero=7) in errores

    def test_fuera_de_rango(self, validar):
        errores = validar(["46", "01", "02", "03", "04", "05"])
        assert ErrorNumero("FUERA_DE_RANGO") in errores

    def test_no_numerico(self, validar):
        errores = validar(["abc", "01", "02", "03", "04", "05"])
        assert ErrorNumero("NO_NUMERICO") in errores

    def test_validos(self, validar):
        resultado = validar(["07", "01", 45, "00", "12", "33"])
        assert resultado == frozenset({0, 1, 7, 12, 33, 45})
        assert isinstance(resultado, frozenset)


def test_formatear():
    assert formatear(7) == "07"
    assert formatear(45) == "45"
    assert formatear(0) == "00"


def test_misma_combinacion_sin_importar_orden():
    assert misma_combinacion(frozenset({1, 2, 3, 4, 5, 6}), frozenset({6, 5, 4, 3, 2, 1}))
    assert not misma_combinacion(frozenset({1, 2, 3, 4, 5, 6}), frozenset({1, 2, 3, 4, 5, 7}))


class TestConjuntoPremioExtra:
    """AC-5.26 y AC-5.28: unión sin repetidos de Primer Sorteo, La Segunda y Revancha."""

    def test_ejemplo_1(self):
        conjunto = conjunto_premio_extra(
            frozenset({3, 8, 14, 21, 32, 40}),
            frozenset({3, 8, 14, 21, 32, 41}),
            frozenset({3, 8, 14, 21, 33, 41}),
        )
        assert conjunto == frozenset({3, 8, 14, 21, 32, 33, 40, 41})
        assert len(conjunto) == 8

    def test_ejemplo_2(self):
        conjunto = conjunto_premio_extra(
            frozenset({1, 7, 12, 19, 30, 45}),
            frozenset({1, 7, 12, 20, 30, 45}),
            frozenset({1, 7, 12, 19, 28, 44}),
        )
        assert conjunto == frozenset({1, 7, 12, 19, 20, 28, 30, 44, 45})
        assert len(conjunto) == 9

    def test_ejemplo_3(self):
        conjunto = conjunto_premio_extra(
            frozenset({2, 9, 16, 25, 34, 45}),
            frozenset({2, 11, 16, 23, 35, 42}),
            frozenset({5, 9, 18, 23, 31, 42}),
        )
        assert conjunto == frozenset({2, 5, 9, 11, 16, 18, 23, 25, 31, 34, 35, 42, 45})
        assert len(conjunto) == 13

    def test_solo_recibe_tres_extracciones(self):
        with pytest.raises(TypeError):
            conjunto_premio_extra(frozenset(), frozenset(), frozenset(), frozenset())  # type: ignore[call-arg]
