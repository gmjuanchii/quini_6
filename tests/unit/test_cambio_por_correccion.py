"""RN-32 y P-03: "Actualizado por corrección…" solo si cambió alguno de los datos de RN-29."""

from datetime import date

from dominio.comparacion import cambio_por_correccion
from dominio.tipos import (
    ORDEN_MODALIDADES,
    BloqueNumerosVista,
    DatosConcurso,
    EstadoBloque,
)

PS, LS, RV, SS, PE = ORDEN_MODALIDADES
JUGADA = frozenset({1, 2, 3, 4, 5, 6})
FECHA = date(2025, 3, 2)


def _datos(**numeros):
    nombres = {"ps": PS, "ls": LS, "rv": RV, "ss": SS}
    return DatosConcurso(
        fecha_sorteo=FECHA,
        modalidades=frozenset(ORDEN_MODALIDADES),
        numeros={
            nombres[k]: BloqueNumerosVista(EstadoBloque.PUBLICADO, frozenset(v))
            for k, v in numeros.items()
        },
    )


BASE = {
    "ps": {40, 41, 42, 43, 44, 45},
    "ls": {30, 31, 32, 33, 34, 35},
    "rv": {20, 21, 22, 23, 24, 25},
    "ss": {10, 11, 12, 13, 14, 15},
}


def _con(**cambios):
    return _datos(**{**BASE, **cambios})


def test_correccion_que_cambia_aciertos():
    historial = [(date(2025, 3, 5), _con(), _con(ps={1, 41, 42, 43, 44, 45}))]
    resultado = cambio_por_correccion(JUGADA, historial)
    assert resultado[PS] == date(2025, 3, 5)
    assert resultado[LS] is None


def test_correccion_que_no_cambia_ningun_dato():
    """Cambia un número oficial que la jugada no tiene: aciertos y resultado iguales."""
    historial = [(date(2025, 3, 5), _con(), _con(ps={39, 41, 42, 43, 44, 45}))]
    assert cambio_por_correccion(JUGADA, historial)[PS] is None


def test_varias_correcciones_toma_la_mas_reciente_con_cambio():
    paso1 = _con(ps={1, 2, 3, 4, 44, 45})
    paso2 = _con(ps={1, 2, 3, 4, 5, 45})
    paso3 = _con(ps={1, 2, 3, 4, 5, 44})  # 5 aciertos otra vez: sin cambio
    historial = [
        (date(2025, 3, 5), _con(), paso1),
        (date(2025, 3, 8), paso1, paso2),
        (date(2025, 3, 9), paso2, paso3),
    ]
    assert cambio_por_correccion(JUGADA, historial)[PS] == date(2025, 3, 8)


def test_correccion_en_revancha_altera_premio_extra():
    """La corrección de Revancha suma números al conjunto de Premio Extra."""
    antes = _con(ps={1, 2, 3, 40, 41, 42}, ls={4, 5, 30, 31, 32, 33})
    despues = _con(ps={1, 2, 3, 40, 41, 42}, ls={4, 5, 30, 31, 32, 33}, rv={6, 21, 22, 23, 24, 25})
    resultado = cambio_por_correccion(JUGADA, [(date(2025, 3, 5), antes, despues)])
    assert resultado[RV] == date(2025, 3, 5)
    assert resultado[PE] == date(2025, 3, 5)
    assert resultado[PS] is None


def test_sin_correcciones():
    assert cambio_por_correccion(JUGADA, []) == {}
