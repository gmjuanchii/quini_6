"""[003] RN-04, data-model § 2: atajos de período calculados con la fecha de hoy."""

from datetime import date

import pytest

from dominio.periodos import Atajo, atajos, error_de_fecha


def _por_clave(lista: list[Atajo]) -> dict[str, tuple[date, date]]:
    return {a.clave: (a.desde, a.hasta) for a in lista}


def test_ejemplo_de_la_spec_21_11_2026():
    resultado = _por_clave(atajos(date(2026, 11, 21), "extraccion", None))
    assert resultado == {
        "anio_en_curso": (date(2026, 1, 1), date(2026, 11, 21)),
        "anio_anterior": (date(2025, 1, 1), date(2025, 12, 31)),
    }


def test_el_01_01_el_inicio_es_igual_al_fin():
    resultado = _por_clave(atajos(date(2026, 1, 1), "extraccion", None))
    assert resultado["anio_en_curso"] == (date(2026, 1, 1), date(2026, 1, 1))


def test_la_extraccion_nunca_ofrece_todo_el_historial():
    claves = [a.clave for a in atajos(date(2026, 11, 21), "extraccion", date(2014, 12, 17))]
    assert claves == ["anio_en_curso", "anio_anterior"]


def test_estadisticas_con_todo_el_historial():
    resultado = atajos(date(2026, 11, 21), "estadisticas", date(2025, 3, 2))
    assert [a.clave for a in resultado] == ["anio_en_curso", "anio_anterior", "todo_el_historial"]
    assert _por_clave(resultado)["todo_el_historial"] == (date(2025, 3, 2), date(2026, 11, 21))


def test_estadisticas_sin_sorteos_publicados_omite_todo_el_historial():
    claves = [a.clave for a in atajos(date(2026, 11, 21), "estadisticas", None)]
    assert claves == ["anio_en_curso", "anio_anterior"]


def test_cada_atajo_tiene_su_texto_del_catalogo():
    from dominio.mensajes import MENSAJES

    for atajo in atajos(date(2026, 11, 21), "estadisticas", date(2025, 3, 2)):
        assert MENSAJES[atajo.clave_texto]


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("31/02/2025", ("fecha.inexistente", {"fecha": "31/02/2025"})),
        ("29/02/2025", ("fecha.inexistente", {"fecha": "29/02/2025"})),
        ("2025-02-31", ("fecha.inexistente", {"fecha": "31/02/2025"})),
        ("1/2/2025", None),
        ("29/02/2024", None),
        ("2024-02-29", None),
        ("ayer", ("gral.fecha_invalida", {})),
        ("01-01-2025", ("gral.fecha_invalida", {})),
        ("", None),
    ],
)
def test_error_de_fecha_ac_4_5(texto, esperado):
    assert error_de_fecha(texto) == esperado


def test_error_de_fecha_vacia_obligatoria():
    assert error_de_fecha("  ", "fecha.falta_inicio") == ("fecha.falta_inicio", {})
