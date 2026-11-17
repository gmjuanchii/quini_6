"""RN-40 a RN-47: frecuencias de aparición (SC-006)."""

from datetime import date
from decimal import Decimal

from dominio.estadisticas import ErrorPeriodo, Frecuencias, SinSorteos, calcular_frecuencias

S1 = (date(2025, 1, 5), frozenset({1, 2, 3, 4, 5, 6}))
S2 = (date(2025, 1, 8), frozenset({1, 2, 3, 10, 11, 12}))
S3 = (date(2025, 1, 12), frozenset({1, 20, 21, 22, 23, 45}))
S4 = (date(2025, 1, 15), frozenset({0, 2, 30, 31, 32, 45}))


def test_siempre_46_numeros():
    r = calcular_frecuencias([S1], 0, None, None)
    assert isinstance(r, Frecuencias)
    assert [f.numero for f in r.numeros] == list(range(46))
    assert r.numero(44).frecuencia == 0
    assert r.numero(44).porcentaje == Decimal("0.00")


def test_resumen_del_periodo():
    r = calcular_frecuencias([S3, S1, S2], 2, None, None)
    assert r.cantidad_sorteos == 3
    assert r.primera_fecha == date(2025, 1, 5)
    assert r.ultima_fecha == date(2025, 1, 12)
    assert r.concursos_sin_informacion == 2


def test_porcentaje_dos_decimales():
    r = calcular_frecuencias([S1, S2, S3], 0, None, None)
    assert r.numero(2).porcentaje == Decimal("66.67")
    assert r.numero(1).porcentaje == Decimal("100.00")
    assert r.numero(4).porcentaje == Decimal("33.33")
    assert isinstance(r.numero(4).porcentaje, Decimal)


def test_sin_sorteos():
    r = calcular_frecuencias([], 3, None, None)
    assert isinstance(r, SinSorteos)
    assert r.concursos_sin_informacion == 3


def test_periodo_invalido():
    r = calcular_frecuencias([S1], 0, date(2025, 2, 1), date(2025, 1, 1))
    assert isinstance(r, ErrorPeriodo)


def test_filtra_por_periodo():
    r = calcular_frecuencias([S1, S2, S3, S4], 0, date(2025, 1, 8), date(2025, 1, 12))
    assert r.cantidad_sorteos == 2


class TestConteoManual:
    """SC-006: tres combinaciones de modalidad y período contadas a mano."""

    def test_caso_1_todo_el_periodo(self):
        r = calcular_frecuencias([S1, S2, S3, S4], 0, None, None)
        # 01 aparece en S1, S2 y S3; 02 en S1, S2 y S4; 45 en S3 y S4; 00 solo en S4.
        assert (r.numero(1).frecuencia, r.numero(2).frecuencia) == (3, 3)
        assert (r.numero(45).frecuencia, r.numero(0).frecuencia) == (2, 1)
        assert r.numero(1).porcentaje == Decimal("75.00")
        assert r.numero(0).porcentaje == Decimal("25.00")
        assert sum(f.frecuencia for f in r.numeros) == 24

    def test_caso_2_desde(self):
        r = calcular_frecuencias([S1, S2, S3, S4], 0, date(2025, 1, 10), None)
        # Solo S3 y S4.
        assert r.cantidad_sorteos == 2
        assert r.numero(45).frecuencia == 2
        assert r.numero(1).frecuencia == 1
        assert r.numero(3).frecuencia == 0
        assert r.numero(45).porcentaje == Decimal("100.00")

    def test_caso_3_hasta(self):
        r = calcular_frecuencias([S1, S2, S3, S4], 0, None, date(2025, 1, 8))
        # Solo S1 y S2.
        assert r.cantidad_sorteos == 2
        assert r.numero(3).frecuencia == 2
        assert r.numero(4).frecuencia == 1
        assert r.numero(45).frecuencia == 0
        assert r.numero(4).porcentaje == Decimal("50.00")
