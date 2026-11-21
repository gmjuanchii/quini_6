"""[002] RN-31, I-09, I-10: clasificación de un sorteo (T024, T076)."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

from dominio.extraccion.clasificacion import clasificar, requiere_respaldo
from dominio.extraccion.consolidacion import (
    consolidar,
    datos_consolidados,
    revisar_correlatividad,
)
from dominio.extraccion.normalizacion import normalizar
from dominio.extraccion.tipos import (
    NO_DISPONIBLE,
    EstadoSorteo,
    Fuente,
    Modalidad,
    ResultadoIntento,
    Valor,
)
from extracciones.fuentes import f3
from extracciones.fuentes.fichas import FICHAS
from tests.extraccion_falsos import leer
from tests.unit.extraccion.ayudas import (
    cambiar_categoria,
    datos_reales,
    intento,
    quitar_modalidad,
)

M = Modalidad
F1, F2, F3 = Fuente.F1, Fuente.F2, Fuente.F3
R = ResultadoIntento


def estado(*intentos, numero=3426):
    return clasificar(consolidar(numero, intentos, FICHAS))


def test_recuperado_con_una_fuente_completa():
    assert estado(intento(datos_reales(F2))) == (EstadoSorteo.RECUPERADO, ())


def test_no_recuperado_con_el_motivo_de_cada_fuente():
    resultado = estado(
        (F1, R.NO_DISPONIBLE, None), (F2, R.NO_DISPONIBLE_O_NO_ENCONTRADO, None),
        (F3, R.ESTRUCTURA_NO_RECONOCIDA, None),
    )  # fmt: skip
    assert resultado == (
        EstadoSorteo.NO_RECUPERADO,
        (  # en el orden de prioridad de RN-07
            "numerosganadores.com.ar: No disponible o no encontrado",
            "quiniya.com.ar: Estructura no reconocida",
            "quini-6-resultados.com.ar: No disponible",
        ),
    )


def test_i_10_hueco_cuando_todas_las_que_lo_cubren_no_lo_encuentran():
    resultado = estado(
        (F1, R.FUERA_DE_COBERTURA, None), (F2, R.NO_DISPONIBLE_O_NO_ENCONTRADO, None),
        (F3, R.NO_ENCONTRADO, None),
    )  # fmt: skip
    assert resultado == (
        EstadoSorteo.NO_RECUPERADO,
        ("Ninguna fuente informa este número de sorteo",),
    )


def test_i_10_con_una_fuente_no_disponible_no_es_hueco():
    _, motivos = estado((F2, R.NO_DISPONIBLE_O_NO_ENCONTRADO, None), (F3, R.NO_DISPONIBLE, None))
    assert "Ninguna fuente informa este número de sorteo" not in motivos


def test_con_inconsistencias_por_discrepancia_y_motivo():
    f3 = cambiar_categoria(
        datos_reales(F3), M.LA_SEGUNDA, "TERCER", importe_individual=Valor(Decimal("5547.85"))
    )
    est, motivos = estado(intento(datos_reales(F2)), intento(f3))
    assert est is EstadoSorteo.CON_INCONSISTENCIAS
    assert motivos == ("La Segunda: Tercer Premio: importe individual: Valor distinto",)


def test_con_inconsistencias_por_observacion_de_inconsistencia():
    s = consolidar(3426, [intento(datos_reales(F2))], FICHAS)
    a = replace(s, numero=3425)
    b = replace(s, numero=3426, fecha=replace(s.fecha, dato=Valor(date(2026, 11, 1))))
    revisados = revisar_correlatividad([a, b])
    assert clasificar(revisados[0])[0] is EstadoSorteo.CON_INCONSISTENCIAS


def test_parcial_si_falta_un_dato_esperado():
    f2 = cambiar_categoria(datos_reales(F2), M.PRIMER_SORTEO, "SEGUNDO", ganadores=NO_DISPONIBLE,
                           importe_individual=NO_DISPONIBLE)  # fmt: skip
    est, motivos = estado(intento(f2, R.INCOMPLETO))
    assert est is EstadoSorteo.PARCIAL
    assert motivos == ("Falta: Tradicional: Segundo Premio: ganadores",)


def test_ac_3_6_pozo_de_categoria_con_ganadores_no_es_esperado():
    assert estado(intento(datos_reales(F2)))[0] is EstadoSorteo.RECUPERADO


def test_ac_3_8_importe_invalido_impide_recuperado():
    pagina = f3.interpretar_sorteo(leer("f3/sorteo-3398.html"))
    r = normalizar(pagina, FICHAS[F3], 3398)
    est, motivos = clasificar(consolidar(3398, [(F3, r.resultado, r.datos)], FICHAS))
    assert est is EstadoSorteo.PARCIAL
    assert "Tradicional: Segundo Premio: importe individual" in motivos[0]


def test_ac_3_12_modalidad_no_informada_impide_recuperado():
    est, motivos = estado(intento(quitar_modalidad(datos_reales(F2), M.REVANCHA), R.INCOMPLETO))
    assert est is EstadoSorteo.PARCIAL
    assert "Revancha: No informada por las fuentes" in motivos[0]


def test_combina_y_sin_corroborar_no_cambian_el_estado():
    s = consolidar(3426, [intento(datos_reales(F2))], FICHAS)
    assert s.sin_corroborar
    assert clasificar(replace(s, combina_fuentes=True))[0] is EstadoSorteo.RECUPERADO


def test_ac_4_7_combina_fuentes_sin_diferencias_puede_quedar_recuperado():
    s = consolidar(
        3426,
        [intento(datos_reales(F1)), intento(datos_reales(F2)), intento(datos_reales(F3))],
        FICHAS,
    )
    assert s.combina_fuentes  # el pozo de Pozo Extra solo lo publica F1 (I-03)
    assert clasificar(s)[0] is EstadoSorteo.RECUPERADO


def test_ac_4_5_diferencia_menor_al_1_por_ciento_no_deja_con_inconsistencias():
    """[002] RN-30, D-17: en el 3427 F1 publica centavos que F2 omite; redondeados coinciden."""
    s = consolidar(3427, [intento(datos_reales(F1, 3427)), intento(datos_reales(F2, 3427))], FICHAS)
    assert not any(d.discrepancia for _, d in datos_consolidados(s))
    assert clasificar(s) == (EstadoSorteo.RECUPERADO, ())


def test_ac_2_11_respaldo_solo_si_falta_un_dato_esperado():
    """[002] RN-09: F1 se consulta solo si con F2 y F3 falta algo o el sorteo no se recuperó."""
    completo = consolidar(3426, [intento(datos_reales(F2)), intento(datos_reales(F3))], FICHAS)
    assert not requiere_respaldo(completo)
    sin_revancha = quitar_modalidad(datos_reales(F2), M.REVANCHA)
    assert requiere_respaldo(consolidar(3426, [intento(sin_revancha, R.INCOMPLETO)], FICHAS))
    assert requiere_respaldo(consolidar(3426, [(F2, R.NO_DISPONIBLE, None)], FICHAS))


def test_i_09_error_inesperado():
    s = replace(consolidar(3426, [], FICHAS), error_inesperado=True)
    assert clasificar(s) == (
        EstadoSorteo.NO_RECUPERADO,
        ("Error inesperado al procesar el sorteo",),
    )
