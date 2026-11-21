"""[002] RN-16, RN-17: importes publicados por las fuentes (T046). Nunca ``float``."""

from decimal import Decimal

import pytest

from dominio.extraccion.normalizacion import (
    ErrorImporteFuente,
    corregir_importe_mal_cargado,
    parsear_importe_fuente,
)


@pytest.mark.parametrize("texto, esperado", [
    ("$ 1.100.000.000", Decimal("1100000000")),
    ("3.013.912", Decimal("3013912")),
    ("12.060,13", Decimal("12060.13")),
    ("5.547,85", Decimal("5547.85")),
    ("$\xa012.060", Decimal("12060")),
    ("1.288.186,97 ", Decimal("1288186.97")),
])  # fmt: skip
def test_formato_argentino(texto, esperado):
    resultado = parsear_importe_fuente(texto)
    assert resultado == esperado
    assert isinstance(resultado, Decimal)


def test_sin_decimales_no_recibe_centavos_estimados():
    assert parsear_importe_fuente("12.060").as_tuple().exponent == 0


@pytest.mark.parametrize("texto", ["494,443,71", "abc", "", "1.00.000", "12,345"])
def test_formato_no_reconocido_conserva_el_texto_original(texto):
    resultado = parsear_importe_fuente(texto)
    assert isinstance(resultado, ErrorImporteFuente)
    assert resultado.texto == texto.strip()


@pytest.mark.parametrize("texto, esperado", [
    ("55 millones de pesos", Decimal("55000000")),
    ("1,5 millones de pesos", Decimal("1500000")),
    ("1 millón de pesos", None),
])  # fmt: skip
def test_millones_solo_con_permiso(texto, esperado):
    assert isinstance(parsear_importe_fuente(texto), ErrorImporteFuente)
    resultado = parsear_importe_fuente(texto, permite_millones=True)
    if esperado is None:
        assert isinstance(resultado, ErrorImporteFuente)
    else:
        assert resultado == esperado and isinstance(resultado, Decimal)


def test_negativo_es_error():
    assert parsear_importe_fuente("-1.000").codigo == "NEGATIVO"


@pytest.mark.parametrize("texto, esperado", [
    ("410.1156,25", Decimal("410115.63")),  # ejemplo del responsable (D-18)
    ("$ 410.1156,25", Decimal("410115.63")),
    ("1.410.1156,2", Decimal("1410115.62")),
    ("410.1156", Decimal("410115.60")),
    ("4101156,25", None),  # sin puntos: no es la forma corregible
    ("494,443,71", None),  # RN-16: sigue sin reconocerse
    ("410.11567,25", None),
    ("12.060,13", None),  # formato válido: no se corrige
    ("1.278.143,114", Decimal("1278143.11")),  # sorteo 3250 (D-20)
    ("$ 1.278.143,115", Decimal("1278143.12")),  # mitad hacia arriba
    ("6407,9749", Decimal("6407.97")),  # cuatro decimales, sin separador de miles
    ("410.1156,254", Decimal("410115.63")),  # D-18 y D-20 a la vez
    ("1.27.143,114", None),  # la parte entera sigue siendo inválida
])  # fmt: skip
def test_ac_3_16_correccion_de_importe_mal_cargado(texto, esperado):
    """[002] RN-16: cuatro dígitos en el último grupo → coma un lugar a la izquierda (D-18);
    tres o más decimales (D-20). Siempre redondeo a centavos, mitad hacia arriba."""
    assert corregir_importe_mal_cargado(texto) == esperado
