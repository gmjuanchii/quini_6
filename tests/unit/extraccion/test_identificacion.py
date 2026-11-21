"""[002] RN-05, R-06, I-02: identificación de los sorteos del período (T020).

La función ``fecha_de`` es falsa: devuelve las fechas de un "mundo" de sorteos y registra los
números pedidos. Ninguna fecha se deduce del calendario.
"""

from datetime import date, timedelta

from dominio.extraccion.identificacion import (
    Identificacion,
    Referencia,
    SinSorteos,
    identificar_sorteos,
)
from dominio.extraccion.periodo import Periodo
from dominio.extraccion.tipos import Fuente

PRIMER = (2211, date(2014, 12, 17))
NOVIEMBRE = {
    # Como en el listado real de F2, también figuran sorteos anteriores al período.
    3416: date(2026, 10, 11),
    3417: date(2026, 10, 14),
    3418: date(2026, 10, 18),
    3419: date(2026, 10, 21),
    3420: date(2026, 10, 25),
    3421: date(2026, 10, 28),
    3422: date(2026, 11, 1),
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
    3426: date(2026, 11, 15),
    3427: date(2026, 11, 18),
}


class Mundo:
    def __init__(self, fechas: dict[int, list[date]]):
        self.fechas = fechas
        self.pedidos: list[int] = []

    def __call__(self, numero):
        self.pedidos.append(numero)
        return self.fechas.get(numero, [])


def refs(sorteos, fuente=Fuente.F2):
    return [Referencia(n, f, fuente) for n, f in sorteos.items()]


def mundo_regular(desde_numero, desde_fecha, hasta_numero, saltos=(3, 4)):
    """Sorteos correlativos alternando 3 y 4 días (los días los fija el "mundo", no la regla)."""
    fechas, fecha = {}, desde_fecha
    for i, numero in enumerate(range(desde_numero, hasta_numero + 1)):
        fechas[numero] = [fecha]
        fecha += timedelta(days=saltos[i % 2])
    return fechas


def test_ac_1_7_incluye_el_primer_y_el_ultimo_dia():
    resultado = identificar_sorteos(
        Periodo(date(2026, 11, 1), date(2026, 11, 15)), refs(NOVIEMBRE), Mundo({}), PRIMER
    )
    assert resultado == Identificacion(3422, 3426, None)
    assert resultado.total == 5


def test_ac_1_10_periodo_sin_sorteos():
    resultado = identificar_sorteos(
        Periodo(date(2026, 11, 5), date(2026, 11, 7)), refs(NOVIEMBRE), Mundo({}), PRIMER
    )
    assert isinstance(resultado, SinSorteos)


def test_ac_1_16_hueco_en_la_numeracion_queda_identificado():
    sin_3423 = {n: f for n, f in NOVIEMBRE.items() if n != 3423}
    mundo = Mundo({})
    resultado = identificar_sorteos(
        Periodo(date(2026, 11, 1), date(2026, 11, 15)), refs(sin_3423), mundo, PRIMER
    )
    assert resultado == Identificacion(3422, 3426, None)


def test_ac_1_17_periodo_anterior_a_la_cobertura():
    mundo = Mundo(mundo_regular(2211, date(2014, 12, 17), 2300))
    resultado = identificar_sorteos(
        Periodo(date(2014, 6, 1), date(2014, 12, 31)), refs(NOVIEMBRE), mundo, PRIMER
    )
    assert isinstance(resultado, Identificacion)
    assert resultado.numero_desde == 2211
    assert resultado.cobertura_desde == date(2014, 12, 17)
    assert mundo.fechas[resultado.numero_hasta][0] <= date(2014, 12, 31)
    assert mundo.fechas[resultado.numero_hasta + 1][0] > date(2014, 12, 31)


def test_periodo_totalmente_anterior_a_la_cobertura():
    resultado = identificar_sorteos(
        Periodo(date(2014, 1, 1), date(2014, 6, 30)), refs(NOVIEMBRE), Mundo({}), PRIMER
    )
    assert resultado == SinSorteos(date(2014, 12, 17))


def test_sorteo_especial_en_un_dia_no_habitual_se_incluye():
    especial = {**NOVIEMBRE, 3424: date(2026, 11, 6)}  # viernes: no es un día habitual
    resultado = identificar_sorteos(
        Periodo(date(2026, 11, 5), date(2026, 11, 7)), refs(especial), Mundo({}), PRIMER
    )
    assert resultado == Identificacion(3424, 3424, None)


def test_numero_con_fecha_fuera_del_periodo_se_excluye():
    resultado = identificar_sorteos(
        Periodo(date(2026, 11, 2), date(2026, 11, 14)), refs(NOVIEMBRE), Mundo({}), PRIMER
    )
    assert resultado == Identificacion(3423, 3425, None)


def test_i_02_se_incluye_si_alguna_fuente_informa_una_fecha_del_periodo():
    referencias = refs(NOVIEMBRE) + [Referencia(3426, date(2026, 11, 16), Fuente.F3)]
    resultado = identificar_sorteos(
        Periodo(date(2026, 11, 16), date(2026, 11, 17)), referencias, Mundo({}), PRIMER
    )
    assert resultado == Identificacion(3426, 3426, None)


def test_periodo_mas_antiguo_que_los_listados_pide_fechas_por_numero():
    fechas = mundo_regular(3000, date(2022, 6, 1), 3427)
    mundo = Mundo(fechas)
    recientes = {n: fs[0] for n, fs in fechas.items() if n >= 3408}
    resultado = identificar_sorteos(
        Periodo(date(2024, 3, 1), date(2024, 3, 31)), refs(recientes), mundo, PRIMER
    )
    en_marzo = sorted(
        n for n, fs in fechas.items() if date(2024, 3, 1) <= fs[0] <= date(2024, 3, 31)
    )
    assert resultado == Identificacion(en_marzo[0], en_marzo[-1], None)
    assert len(mundo.pedidos) < 60  # pocas consultas fuera del período


def test_las_fechas_no_se_deducen_del_calendario():
    """Si ninguna fuente informa fechas para los números del período, no hay sorteos."""
    resultado = identificar_sorteos(
        Periodo(date(2024, 3, 1), date(2024, 3, 31)), refs(NOVIEMBRE), Mundo({}), PRIMER
    )
    assert isinstance(resultado, SinSorteos)
