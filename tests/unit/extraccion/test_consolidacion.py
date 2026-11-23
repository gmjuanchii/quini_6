"""[002] RN-07, RN-12, RN-18, RN-22, RN-23, RN-27 a RN-30, RN-32, I-03: consolidación
(T023, T048, T075, T095; Clarifications 20/11/2026)."""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from dominio.extraccion.clasificacion import clasificar
from dominio.extraccion.consolidacion import consolidar, revisar_correlatividad
from dominio.extraccion.tipos import (
    CALCULO_POZO,
    CALCULO_POZO_EXTRA,
    CALCULO_VACANTE,
    NO_CORRESPONDE,
    NO_DISPONIBLE,
    SIN_DETERMINAR,
    EstadoPozo,
    EstadoSorteo,
    Fuente,
    Modalidad,
    Observacion,
    ResultadoIntento,
    TipoDiscrepancia,
    Valor,
)
from extracciones.fuentes.fichas import FICHAS
from tests.unit.extraccion.ayudas import (
    cambiar_categoria,
    cambiar_numeros,
    datos_reales,
    intento,
    quitar_categoria,
    quitar_modalidad,
)

M = Modalidad
F1, F2, F3 = Fuente.F1, Fuente.F2, Fuente.F3


def solo_f2(datos=None):
    return consolidar(3426, [intento(datos or datos_reales(F2))], FICHAS)


def cat(sorteo, modalidad, codigo):
    return sorteo.modalidades[modalidad].categorias[codigo]


# -- Una sola fuente (T023) ------------------------------------------------------------


def test_rn_32_dato_de_una_sola_fuente_queda_sin_corroborar():
    s = solo_f2()
    numeros = s.modalidades[M.PRIMER_SORTEO].numeros
    assert numeros.dato == Valor(frozenset({1, 2, 10, 13, 38, 39}))
    assert numeros.fuentes == (F2,) and numeros.sin_corroborar
    assert s.sin_corroborar


def test_dato_no_informado_no_disponible_sin_fuentes():
    datos = cambiar_categoria(datos_reales(F2), M.PRIMER_SORTEO, "SEGUNDO", ganadores=NO_DISPONIBLE)
    ganadores = cat(solo_f2(datos), M.PRIMER_SORTEO, "SEGUNDO").ganadores
    assert ganadores.dato is NO_DISPONIBLE and ganadores.fuentes == ()


def test_siempre_las_cinco_modalidades_y_sus_categorias_esperadas():
    s = solo_f2()
    assert list(s.modalidades) == list(Modalidad)
    assert list(s.modalidades[M.LA_SEGUNDA].categorias) == ["PRIMER", "SEGUNDO", "TERCER"]
    assert list(s.modalidades[M.REVANCHA].categorias) == ["UNICO"]


def test_ac_3_17_numeros_de_pozo_extra_son_la_union_de_las_tres_extracciones():
    """[002] RN-12, D-19: unión de Tradicional, La Segunda y Revancha, marcada como calculada."""
    numeros = solo_f2().modalidades[M.PREMIO_EXTRA].numeros
    union = {1, 2, 10, 13, 38, 39} | {11, 17, 19, 21, 27, 28} | {1, 16, 27, 33, 37, 40}
    assert numeros.dato == Valor(frozenset(union))
    assert numeros.calculo == CALCULO_POZO_EXTRA
    assert numeros.fuentes == () and not numeros.sin_corroborar


def test_ac_3_17_numeros_de_pozo_extra_no_disponibles_si_falta_una_extraccion():
    s = solo_f2(cambiar_numeros(datos_reales(F2), M.REVANCHA, None))
    assert s.modalidades[M.PREMIO_EXTRA].numeros.dato is NO_DISPONIBLE


def test_ac_3_4_vacante_con_importe_individual_cero():
    """[002] RN-18, D-16: vacante → importe individual 0,00 calculado."""
    primer = cat(solo_f2(), M.PRIMER_SORTEO, "PRIMER")
    assert primer.pozo_destinado.dato == Valor(Decimal("1100000000"))
    assert primer.importe_individual.dato == Valor(Decimal("0.00"))
    assert primer.importe_individual.calculo == CALCULO_VACANTE


def test_ac_3_5_pozo_calculado_importe_individual_por_ganadores():
    """[002] RN-18, D-16: 18 × 3.013.912 = 54.250.416, marcado como calculado."""
    segundo = cat(solo_f2(), M.PRIMER_SORTEO, "SEGUNDO")
    assert segundo.importe_individual.dato == Valor(Decimal("3013912"))
    assert segundo.pozo_destinado.dato == Valor(Decimal("54250416"))
    assert segundo.pozo_destinado.calculo == CALCULO_POZO
    assert not segundo.pozo_destinado.sin_corroborar


def test_estado_del_pozo_sin_acumulacion_ni_importe_trasladado():
    s = solo_f2()
    primer = cat(s, M.PRIMER_SORTEO, "PRIMER")
    assert not hasattr(primer, "se_acumula") and not hasattr(primer, "importe_trasladado")  # D-22
    assert primer.estado_pozo is EstadoPozo.VACANTE
    assert cat(s, M.PRIMER_SORTEO, "SEGUNDO").estado_pozo is EstadoPozo.CON_GANADORES


def test_rn_25_reglas_no_verificadas():
    antes = replace(datos_reales(F2), fecha=date(2024, 6, 17))
    desde = replace(datos_reales(F2), fecha=date(2024, 6, 18))
    assert consolidar(3426, [intento(antes)], FICHAS).reglas_no_verificadas
    assert not consolidar(3426, [intento(desde)], FICHAS).reglas_no_verificadas


def test_sin_datos_de_ninguna_fuente():
    s = consolidar(3426, [(F2, ResultadoIntento.NO_DISPONIBLE, None)], FICHAS)
    assert s.fecha.dato is NO_DISPONIBLE
    assert not any(m.informada for m in s.modalidades.values())


# -- Historia 3 (T048) -------------------------------------------------------------------


def test_rn_23_numero_mayor_con_fecha_anterior():
    a = solo_f2(replace(datos_reales(F2), numero=3425, fecha=date(2026, 11, 15)))
    a = replace(a, numero=3425)
    b = replace(solo_f2(replace(datos_reales(F2), fecha=date(2026, 11, 11))), numero=3426)
    revisados = revisar_correlatividad([a, b])
    textos_a = [o.texto for o in revisados[0].observaciones if o.es_inconsistencia]
    textos_b = [o.texto for o in revisados[1].observaciones if o.es_inconsistencia]
    assert textos_a == ["El número y la fecha no son correlativos con el sorteo N.º 3426"]
    assert textos_b == ["El número y la fecha no son correlativos con el sorteo N.º 3425"]


def test_rn_23_correlativos_sin_observacion():
    a = replace(solo_f2(replace(datos_reales(F2), fecha=date(2026, 11, 11))), numero=3425)
    b = solo_f2()
    assert revisar_correlatividad([a, b]) == [a, b]


def test_ac_3_12_modalidad_no_informada_por_ninguna_fuente():
    s = solo_f2(quitar_modalidad(datos_reales(F2), M.REVANCHA))
    assert not s.modalidades[M.REVANCHA].informada
    assert s.modalidades[M.REVANCHA].categorias == {}


def test_ac_3_6_pozo_de_categoria_con_ganadores_no_es_discrepancia():
    s = consolidar(3426, [intento(datos_reales(F2)), intento(datos_reales(F3))], FICHAS)
    pozo = cat(s, M.PRIMER_SORTEO, "SEGUNDO").pozo_destinado
    assert pozo.calculo == CALCULO_POZO and pozo.discrepancia is None


def test_ac_3_6_sin_importe_individual_el_pozo_no_se_calcula():
    f2 = cambiar_categoria(
        datos_reales(F2), M.PRIMER_SORTEO, "SEGUNDO", importe_individual=NO_DISPONIBLE
    )
    pozo = cat(solo_f2(f2), M.PRIMER_SORTEO, "SEGUNDO").pozo_destinado
    assert pozo.dato is NO_DISPONIBLE and pozo.calculo is None


# -- Historia 4 (T075) -------------------------------------------------------------------


def test_ac_4_1_valor_distinto():
    f2 = cambiar_categoria(
        datos_reales(F2), M.LA_SEGUNDA, "TERCER", importe_individual=Valor(Decimal("5015"))
    )
    f3 = cambiar_categoria(
        datos_reales(F3), M.LA_SEGUNDA, "TERCER", importe_individual=Valor(Decimal("5547.85"))
    )
    dato = cat(consolidar(3426, [intento(f2), intento(f3)], FICHAS), M.LA_SEGUNDA, "TERCER")
    importe = dato.importe_individual
    assert importe.dato is SIN_DETERMINAR
    assert importe.discrepancia.tipo is TipoDiscrepancia.VALOR_DISTINTO
    assert importe.discrepancia.valores == ((F2, Decimal("5015")), (F3, Decimal("5547.85")))


def test_ac_4_2_omision():
    f3 = quitar_categoria(datos_reales(F3), M.PRIMER_SORTEO, "PRIMER")
    s = consolidar(
        3426, [intento(datos_reales(F2)), intento(f3, ResultadoIntento.INCOMPLETO)], FICHAS
    )
    ganadores = cat(s, M.PRIMER_SORTEO, "PRIMER").ganadores
    assert ganadores.discrepancia.tipo is TipoDiscrepancia.OMISION
    assert ganadores.discrepancia.valores == ((F2, 0), (F3, None))


def test_ac_4_3_dato_no_publicado_por_diseno_no_es_omision():
    """F1 no publica los aciertos de Premio Extra y ninguna publica su pozo (D-30)."""
    s = consolidar(
        3426,
        [intento(datos_reales(F1)), intento(datos_reales(F2)), intento(datos_reales(F3))],
        FICHAS,
    )
    extra = cat(s, M.PREMIO_EXTRA, "GANADORA")
    assert extra.aciertos.dato == Valor(6) and extra.aciertos.discrepancia is None
    assert extra.pozo_destinado.calculo == CALCULO_POZO
    assert extra.pozo_destinado.discrepancia is None and not extra.pozo_destinado.sin_corroborar


def test_ac_4_4_fechas_distintas_prevalece_la_fuente_prioritaria():
    """[002] RN-07, D-14: se muestra la fecha de F2 y la diferencia sigue siendo discrepancia."""
    f3 = replace(datos_reales(F3), fecha=date(2026, 11, 16))
    s = consolidar(3426, [intento(datos_reales(F2)), intento(f3)], FICHAS)
    assert s.fecha.dato == Valor(date(2026, 11, 15)) and s.fecha.fuentes == (F2,)
    assert s.fecha.discrepancia.valores == ((F2, date(2026, 11, 15)), (F3, date(2026, 11, 16)))


def _importes(pozo_f2, pozo_f3):
    """Pozo de la vacante de Tradicional (Primer Premio) según F2 y F3."""
    f2 = cambiar_categoria(
        datos_reales(F2), M.PRIMER_SORTEO, "PRIMER", pozo_destinado=Valor(Decimal(pozo_f2))
    )
    f3 = cambiar_categoria(
        datos_reales(F3), M.PRIMER_SORTEO, "PRIMER", pozo_destinado=Valor(Decimal(pozo_f3))
    )
    s = consolidar(3426, [intento(f3), intento(f2)], FICHAS)
    return cat(s, M.PRIMER_SORTEO, "PRIMER").pozo_destinado


@pytest.mark.parametrize("f2, f3", [
    ("657151589", "657151588.80"),  # sorteo 3232 (ejemplo del responsable)
    ("756099026", "756099025.92"),  # sorteo 3233 (ejemplo del responsable)
])  # fmt: skip
def test_ac_4_5_diferencia_menor_a_un_peso_no_hay_diferencia(f2, f3):
    """[002] RN-30, D-28: difieren en menos de $ 1,00 y el importe prioritario no tiene
    centavos, así que no hay discrepancia ni nota."""
    pozo = _importes(f2, f3)
    assert pozo.dato == Valor(Decimal(f2))
    assert pozo.discrepancia is None and pozo.diferencia_tolerada is None
    assert pozo.fuentes == (F2, F3) and not pozo.sin_corroborar


def test_ac_4_5_sin_centavos_distintos_menos_del_1_por_ciento_dejan_nota():
    pozo = _importes("1000000", "1000500.40")
    assert pozo.dato == Valor(Decimal("1000000")) and pozo.discrepancia is None
    assert pozo.diferencia_tolerada.tipo is TipoDiscrepancia.CENTAVOS
    assert pozo.diferencia_tolerada.valores == (
        (F2, Decimal("1000000")),
        (F3, Decimal("1000500.40")),
    )


def test_d_28_el_valor_prioritario_pierde_los_centavos_con_nota():
    """[002] RN-30, D-28: se quitan (no se redondean) y, como el valor no es el publicado,
    queda la nota informativa."""
    pozo = _importes("12060.50", "12060")
    assert pozo.dato == Valor(Decimal("12060")) and pozo.discrepancia is None
    assert pozo.diferencia_tolerada.tipo is TipoDiscrepancia.CENTAVOS
    assert pozo.fuentes == (F2, F3)
    assert _importes("12060.99", "12061.40").dato == Valor(Decimal("12060"))  # < $ 1,00


def test_d_28_diferencia_de_un_peso_ya_no_es_coincidencia():
    pozo = _importes("12060", "12061")
    assert pozo.dato == Valor(Decimal("12060"))
    assert pozo.diferencia_tolerada.tipo is TipoDiscrepancia.CENTAVOS  # tolerada: < 1 %


def test_rn_30_desde_el_1_por_ciento_es_valor_distinto_y_sin_determinar():
    pozo = _importes("10000", "10100")
    assert pozo.dato is SIN_DETERMINAR
    assert pozo.discrepancia.tipo is TipoDiscrepancia.VALOR_DISTINTO
    assert _importes("10000", "10100.99").dato is SIN_DETERMINAR  # sin centavos: 10.100 (1 %)
    assert _importes("10000", "10099.99").discrepancia is None  # sin centavos: 10.099


def test_ac_4_6_coincidencia_con_la_lista_de_fuentes():
    s = consolidar(3426, [intento(datos_reales(F2)), intento(datos_reales(F3))], FICHAS)
    ganadores = cat(s, M.PRIMER_SORTEO, "SEGUNDO").ganadores
    assert ganadores.dato == Valor(18)
    assert ganadores.fuentes == (F2, F3) and not ganadores.sin_corroborar


def test_ac_3_2_numeros_en_distinto_orden_sin_discrepancia():
    s = consolidar(3426, [intento(datos_reales(F1)), intento(datos_reales(F2))], FICHAS)
    numeros = s.modalidades[M.PRIMER_SORTEO].numeros
    assert numeros.discrepancia is None and numeros.fuentes == (F2, F1)  # orden de RN-07


def test_ac_4_7_numeros_de_una_fuente_y_premios_de_otra_combina():
    solo_numeros = datos_reales(F2)
    solo_numeros = replace(
        solo_numeros,
        modalidades={m: replace(md, categorias={}) for m, md in solo_numeros.modalidades.items()},
    )
    solo_premios = datos_reales(F3)
    for m in solo_premios.modalidades:
        solo_premios = cambiar_numeros(solo_premios, m, None)
    s = consolidar(
        3426,
        [intento(solo_numeros, ResultadoIntento.INCOMPLETO),
         intento(solo_premios, ResultadoIntento.INCOMPLETO)],
        FICHAS,
    )  # fmt: skip
    assert s.combina_fuentes


def test_i_03_una_fuente_completa_y_otra_parcial_no_combina():
    parcial = quitar_modalidad(datos_reales(F3), M.REVANCHA)
    s = consolidar(
        3426,
        [intento(datos_reales(F2)), intento(parcial, ResultadoIntento.INCOMPLETO)],
        FICHAS,
    )
    assert not s.combina_fuentes


def test_ac_4_8_dato_de_una_sola_fuente_sin_corroborar():
    s = consolidar(
        3426,
        [intento(datos_reales(F2)), (F3, ResultadoIntento.NO_ENCONTRADO, None)],
        FICHAS,
    )
    assert s.sin_corroborar
    assert s.resultados == {F2: ResultadoIntento.OBTENIDO, F3: ResultadoIntento.NO_ENCONTRADO}


def test_ac_4_9_ganadores_en_conflicto_prevalece_la_fuente_prioritaria():
    """[002] RN-07, D-14: F2 informa la vacante y F3 un ganador. Valen los ganadores de F2, la
    diferencia es discrepancia y los importes de F3 (otro concepto, RN-17) no se comparan."""
    f3 = cambiar_categoria(datos_reales(F3), M.PRIMER_SORTEO, "PRIMER", ganadores=Valor(1),
                           importe_individual=Valor(Decimal("1100000000")),
                           pozo_destinado=NO_DISPONIBLE)  # fmt: skip
    s = consolidar(3426, [intento(datos_reales(F2)), intento(f3)], FICHAS)
    primer = cat(s, M.PRIMER_SORTEO, "PRIMER")
    assert primer.ganadores.dato == Valor(0) and primer.ganadores.fuentes == (F2,)
    assert primer.ganadores.discrepancia.tipo is TipoDiscrepancia.VALOR_DISTINTO
    assert primer.estado_pozo is EstadoPozo.VACANTE
    assert primer.pozo_destinado.dato == Valor(Decimal("1100000000"))
    assert primer.pozo_destinado.fuentes == (F2,) and primer.pozo_destinado.discrepancia is None
    assert primer.importe_individual.dato == Valor(Decimal("0.00"))


def test_rn_07_el_orden_de_los_intentos_no_cambia_el_resultado():
    f2 = cambiar_categoria(
        datos_reales(F2), M.LA_SEGUNDA, "TERCER", importe_individual=Valor(Decimal("5015"))
    )
    f3 = datos_reales(F3)
    assert consolidar(3426, [intento(f2), intento(f3)], FICHAS) == consolidar(
        3426, [intento(f3), intento(f2)], FICHAS
    )


# -- Desempate con la tercera fuente (D-21, Clarifications 20/11/2026) -------------------


def _tres(f2, f3, f1):
    return consolidar(3426, [intento(f2), intento(f3), intento(f1)], FICHAS)


def test_d_21_ganadores_desempatados_por_la_tercera_fuente():
    """Como en el sorteo 3235: numerosganadores informa vacante y quiniya y quini-6-resultados
    coinciden en los ganadores (18 en estos datos de prueba)."""
    f2 = cambiar_categoria(datos_reales(F2), M.PRIMER_SORTEO, "SEGUNDO", ganadores=Valor(0),
                           pozo_destinado=Valor(Decimal("3013912")),
                           importe_individual=NO_CORRESPONDE)  # fmt: skip
    s = _tres(f2, datos_reales(F3), datos_reales(F1))
    segundo = cat(s, M.PRIMER_SORTEO, "SEGUNDO")
    assert segundo.ganadores.dato == Valor(18) and segundo.ganadores.fuentes == (F3, F1)
    assert segundo.ganadores.discrepancia is None
    assert segundo.ganadores.diferencia_tolerada.tipo is TipoDiscrepancia.MAYORIA
    assert segundo.ganadores.diferencia_tolerada.valores == ((F2, 0), (F3, 18), (F1, 18))
    # Los importes solo se comparan entre las fuentes que coinciden en los ganadores (AC-4.9).
    assert segundo.importe_individual.dato == Valor(Decimal("3013912"))
    assert segundo.pozo_destinado.calculo == CALCULO_POZO
    assert clasificar(s)[0] is EstadoSorteo.RECUPERADO


def test_d_21_dato_invalido_de_la_fuente_que_pierde_el_desempate_es_informativo():
    """Como en el sorteo 3308: numerosganadores publica Siempre Sale con 0 aciertos y 0
    ganadores (observación de inconsistencia); las otras dos coinciden (1 ganador en estos datos
    de prueba)."""
    invalida = Observacion(
        codigo="obs.siempre_sale_invalida", texto="Siempre Sale inválida", fuente=F2,
        es_inconsistencia=True, modalidad=M.SIEMPRE_SALE,
    )  # fmt: skip
    f2 = cambiar_categoria(datos_reales(F2), M.SIEMPRE_SALE, "GANADORA", aciertos=Valor(0),
                           ganadores=Valor(0), importe_individual=NO_CORRESPONDE)  # fmt: skip
    f2 = replace(f2, observaciones=(invalida,))
    s = _tres(f2, datos_reales(F3), datos_reales(F1))
    ganadora = cat(s, M.SIEMPRE_SALE, "GANADORA")
    assert ganadora.ganadores.dato == Valor(1) and ganadora.aciertos.dato == Valor(6)
    assert ganadora.importe_individual.dato == Valor(Decimal("486704052"))
    observacion = next(o for o in s.observaciones if o.codigo == "obs.siempre_sale_invalida")
    assert not observacion.es_inconsistencia and observacion.informativa
    assert clasificar(s)[0] is EstadoSorteo.RECUPERADO


def test_d_21_sin_mayoria_vale_la_regla_anterior():
    """Tres valores distintos: vale numerosganadores y la diferencia es inconsistencia."""
    f2 = cambiar_categoria(datos_reales(F2), M.PRIMER_SORTEO, "TERCER", ganadores=Valor(870))
    f1 = cambiar_categoria(datos_reales(F1), M.PRIMER_SORTEO, "TERCER", ganadores=Valor(872))
    ganadores = cat(_tres(f2, datos_reales(F3), f1), M.PRIMER_SORTEO, "TERCER").ganadores
    assert ganadores.dato == Valor(870) and ganadores.fuentes == (F2,)
    assert ganadores.discrepancia.tipo is TipoDiscrepancia.VALOR_DISTINTO
    assert ganadores.diferencia_tolerada is None


def test_d_21_importes_de_la_mayoria_coinciden_por_menos_de_un_peso():
    f2 = cambiar_categoria(datos_reales(F2), M.PRIMER_SORTEO, "TERCER",
                           importe_individual=Valor(Decimal("20000")))  # fmt: skip
    f1 = cambiar_categoria(datos_reales(F1), M.PRIMER_SORTEO, "TERCER",
                           importe_individual=Valor(Decimal("18685.70")))  # fmt: skip
    importe = cat(_tres(f2, datos_reales(F3), f1), M.PRIMER_SORTEO, "TERCER").importe_individual
    assert importe.dato == Valor(Decimal("18685"))  # 18.685,56 y 18.685,70 → 18.685 (D-28)
    assert importe.fuentes == (F3, F1) and importe.discrepancia is None


def test_ac_4_12_sorteo_2918_pozo_resuelto_por_dos_de_tres():
    """[002] RN-30, D-21, D-28 (sorteo 2918, Revancha): 47.930.930,50 y 47.930.930,00 difieren
    en menos de $ 1,00, así que coinciden frente a los 74.669.257,73 de quiniya."""
    valores = {F2: "47930930.50", F3: "74669257.73", F1: "47930930.00"}
    f2, f3, f1 = (
        cambiar_categoria(datos_reales(f), M.PRIMER_SORTEO, "PRIMER",
                          pozo_destinado=Valor(Decimal(valores[f])))
        for f in (F2, F3, F1)
    )  # fmt: skip
    pozo = cat(_tres(f2, f3, f1), M.PRIMER_SORTEO, "PRIMER").pozo_destinado
    assert pozo.dato == Valor(Decimal("47930930")) and pozo.discrepancia is None
    assert pozo.fuentes == (F2, F1)
    assert pozo.diferencia_tolerada.tipo is TipoDiscrepancia.MAYORIA
    assert pozo.diferencia_tolerada.valores == tuple((f, Decimal(valores[f])) for f in (F2, F3, F1))


def test_d_28_tres_fuentes_que_coinciden_no_se_desempatan():
    valores = {F2: "1000000", F3: "1000000.40", F1: "999999.80"}
    f2, f3, f1 = (
        cambiar_categoria(datos_reales(f), M.PRIMER_SORTEO, "PRIMER",
                          pozo_destinado=Valor(Decimal(valores[f])))
        for f in (F2, F3, F1)
    )  # fmt: skip
    pozo = cat(_tres(f2, f3, f1), M.PRIMER_SORTEO, "PRIMER").pozo_destinado
    assert pozo.dato == Valor(Decimal("1000000")) and pozo.fuentes == (F2, F3, F1)
    assert pozo.diferencia_tolerada is None and pozo.discrepancia is None


def test_d_21_coincidencia_de_dos_frente_a_una_omision():
    f3 = quitar_categoria(datos_reales(F3), M.PRIMER_SORTEO, "PRIMER")
    s = consolidar(
        3426,
        [intento(datos_reales(F2)), intento(f3, ResultadoIntento.INCOMPLETO),
         intento(datos_reales(F1))],
        FICHAS,
    )  # fmt: skip
    ganadores = cat(s, M.PRIMER_SORTEO, "PRIMER").ganadores
    assert ganadores.dato == Valor(0) and ganadores.discrepancia is None
    assert ganadores.diferencia_tolerada.valores == ((F2, 0), (F3, None), (F1, 0))


# -- Valores inválidos y pozo de Pozo Extra (D-29, D-30) --------------------------------


def _siempre_sale_invalida(fuente):
    """Como en el sorteo 3425: 5 aciertos y 0 ganadores, y el importe leído como pozo."""
    invalida = Observacion(
        codigo="obs.siempre_sale_invalida", texto="Siempre Sale inválida", fuente=fuente,
        es_inconsistencia=True, modalidad=M.SIEMPRE_SALE,
    )  # fmt: skip
    datos = cambiar_categoria(datos_reales(fuente), M.SIEMPRE_SALE, "GANADORA",
                              aciertos=Valor(5), ganadores=Valor(0),
                              pozo_destinado=Valor(Decimal("56785482")),
                              importe_individual=NO_CORRESPONDE)  # fmt: skip
    return replace(datos, observaciones=(invalida,))


def test_ac_4_13_sorteo_3425_dos_fuentes_invalidas_no_ganan_por_mayoria():
    """[002] RN-07, RN-26, D-29: el 0 de numerosganadores y quiniya viola RN-26 y se descarta;
    quedan los 6 ganadores de quini-6-resultados, sin corroborar."""
    f1 = cambiar_categoria(datos_reales(F1), M.SIEMPRE_SALE, "GANADORA", aciertos=Valor(5),
                           ganadores=Valor(6), pozo_destinado=NO_DISPONIBLE,
                           importe_individual=Valor(Decimal("56785482")))  # fmt: skip
    s = _tres(_siempre_sale_invalida(F2), _siempre_sale_invalida(F3), f1)
    ganadora = cat(s, M.SIEMPRE_SALE, "GANADORA")
    assert ganadora.ganadores.dato == Valor(6) and ganadora.ganadores.fuentes == (F1,)
    assert ganadora.ganadores.sin_corroborar
    assert ganadora.ganadores.diferencia_tolerada is None
    assert ganadora.ganadores.discrepancia is None
    assert ganadora.aciertos.dato == Valor(5) and ganadora.aciertos.fuentes == (F2, F3, F1)
    # Los importes de las fuentes descartadas no se usan (RN-17): su concepto era otro.
    assert ganadora.importe_individual.dato == Valor(Decimal("56785482"))
    assert ganadora.importe_individual.fuentes == (F1,)
    assert ganadora.pozo_destinado.dato == Valor(Decimal("340712892"))
    assert ganadora.pozo_destinado.calculo == CALCULO_POZO
    assert ganadora.estado_pozo is EstadoPozo.CON_GANADORES
    invalidas = [o for o in s.observaciones if o.codigo == "obs.siempre_sale_invalida"]
    assert len(invalidas) == 2
    assert all(o.informativa and not o.es_inconsistencia for o in invalidas)
    assert s.sin_corroborar
    assert clasificar(s)[0] is EstadoSorteo.RECUPERADO


def test_d_29_sin_valor_valido_el_dato_queda_no_disponible_y_es_inconsistencia():
    s = consolidar(
        3426,
        [intento(_siempre_sale_invalida(F2)), intento(_siempre_sale_invalida(F3))],
        FICHAS,
    )
    ganadora = cat(s, M.SIEMPRE_SALE, "GANADORA")
    assert ganadora.ganadores.dato is NO_DISPONIBLE  # nunca el 0 inválido
    assert ganadora.pozo_destinado.dato is NO_DISPONIBLE
    assert ganadora.estado_pozo is EstadoPozo.PENDIENTE
    invalidas = [o for o in s.observaciones if o.codigo == "obs.siempre_sale_invalida"]
    assert invalidas and all(o.es_inconsistencia for o in invalidas)
    assert clasificar(s)[0] is EstadoSorteo.CON_INCONSISTENCIAS


def test_d_29_aciertos_invalidos_de_premio_extra_no_se_comparan():
    f2 = cambiar_categoria(datos_reales(F2), M.PREMIO_EXTRA, "GANADORA", aciertos=Valor(3))
    s = consolidar(3426, [intento(f2), intento(datos_reales(F3))], FICHAS)
    aciertos = cat(s, M.PREMIO_EXTRA, "GANADORA").aciertos
    assert aciertos.dato == Valor(6) and aciertos.fuentes == (F3,)
    assert aciertos.discrepancia is None


def test_ac_4_14_sorteo_3425_pozo_de_pozo_extra_calculado_y_corroborado():
    """[002] RN-17, RN-18, D-30: el pozo de Pozo Extra es importe individual × ganadores, con
    los datos en que coinciden las fuentes; F1 ya no aporta el texto fijo de 55 millones."""
    importes = {F2: "259067", F3: "259067", F1: "259067.36"}
    f2, f3, f1 = (
        cambiar_categoria(datos_reales(f), M.PREMIO_EXTRA, "GANADORA", ganadores=Valor(772),
                          importe_individual=Valor(Decimal(importes[f])))
        for f in (F2, F3, F1)
    )  # fmt: skip
    ganadora = cat(_tres(f2, f3, f1), M.PREMIO_EXTRA, "GANADORA")
    assert ganadora.importe_individual.dato == Valor(Decimal("259067"))
    assert ganadora.pozo_destinado.dato == Valor(Decimal("199999724"))  # 772 × 259.067
    assert ganadora.pozo_destinado.calculo == CALCULO_POZO
    assert not ganadora.pozo_destinado.sin_corroborar
