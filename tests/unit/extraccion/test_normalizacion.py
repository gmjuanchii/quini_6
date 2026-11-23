"""[002] RN-10 a RN-26: normalización y validación de lo que informa una fuente (T022, T047).

Las páginas se toman de las copias reales y se editan con ``cambiar`` para provocar cada caso.
"""

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from dominio.extraccion.normalizacion import normalizar, parsear_fecha_fuente
from dominio.extraccion.tipos import (
    NO_CORRESPONDE,
    NO_DISPONIBLE,
    BloqueCrudo,
    FilaPremioCruda,
    Fuente,
    Modalidad,
    PaginaCruda,
    ResultadoIntento,
    Valor,
)
from extracciones.fuentes import f1, f2, f3
from extracciones.fuentes.fichas import FICHAS
from tests.extraccion_falsos import leer

F1, F2, F3 = FICHAS[Fuente.F1], FICHAS[Fuente.F2], FICHAS[Fuente.F3]
M = Modalidad
FECHA = date(2026, 11, 15)


def pagina_f2(numero=3426) -> PaginaCruda:
    return f2.interpretar_sorteo(leer(f"f2/sorteo-{numero}.html"))


def cambiar(pagina: PaginaCruda, de: str, **cambios) -> PaginaCruda:
    bloques = tuple(replace(b, **cambios) if b.rotulo == de else b for b in pagina.bloques)
    return replace(pagina, bloques=bloques)


def quitar(pagina: PaginaCruda, rotulo: str) -> PaginaCruda:
    return replace(pagina, bloques=tuple(b for b in pagina.bloques if b.rotulo != rotulo))


def textos(resultado):
    return [o.texto for o in resultado.observaciones]


def categoria(resultado, modalidad, codigo):
    return resultado.datos.modalidades[modalidad].categorias[codigo]


# -- Base (T022) ---------------------------------------------------------------------


def test_pagina_completa_obtenida_con_las_cinco_modalidades():
    r = normalizar(pagina_f2(), F2, 3426)
    assert r.resultado is ResultadoIntento.OBTENIDO
    assert set(r.datos.modalidades) == set(Modalidad)
    assert r.datos.modalidades[M.PRIMER_SORTEO].numeros == frozenset({1, 2, 10, 13, 38, 39})
    assert r.datos.fecha == FECHA and r.datos.numero == 3426


@pytest.mark.parametrize("numero_texto, fecha_texto", [
    (None, "15/11/2026"), ("3426", None), ("tres mil", "15/11/2026"), ("3426", "31/02/2026"),
])  # fmt: skip
def test_rn_10_numero_o_fecha_irreconocibles(numero_texto, fecha_texto):
    pagina = replace(pagina_f2(), numero_texto=numero_texto, fecha_texto=fecha_texto)
    r = normalizar(pagina, F2, 3426)
    assert r.resultado is ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA
    assert r.datos is None


def test_pagina_de_otro_numero_no_se_reconoce():
    r = normalizar(pagina_f2(), F2, 3425)
    assert r.resultado is ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA


def test_ac_3_4_vacante_es_pozo_destinado_y_no_corresponde_el_individual():
    cat = categoria(normalizar(pagina_f2(), F2, 3426), M.PRIMER_SORTEO, "PRIMER")
    assert cat.ganadores == Valor(0)
    assert cat.pozo_destinado == Valor(Decimal("1100000000"))
    assert cat.importe_individual is NO_CORRESPONDE


def test_ac_3_5_con_ganadores_es_importe_individual_y_el_pozo_no_disponible():
    cat = categoria(normalizar(pagina_f2(), F2, 3426), M.PRIMER_SORTEO, "SEGUNDO")
    assert cat.ganadores == Valor(18)
    assert cat.importe_individual == Valor(Decimal("3013912"))
    assert cat.pozo_destinado is NO_DISPONIBLE  # nunca 18 × 3.013.912 (RN-18)


def test_ac_3_7_ganadores_no_disponibles():
    filas = (FilaPremioCruda("6", "", "1.100.000.000"),) + pagina_f2().bloques[0].filas_premios[1:]
    r = normalizar(cambiar(pagina_f2(), "TRADICIONAL", filas_premios=filas), F2, 3426)
    cat = categoria(r, M.PRIMER_SORTEO, "PRIMER")
    assert cat.ganadores is NO_DISPONIBLE
    assert cat.pozo_destinado is NO_DISPONIBLE and cat.importe_individual is NO_DISPONIBLE
    assert r.resultado is ResultadoIntento.INCOMPLETO
    assert any("pozo o premio individual" in t for t in textos(r))


def test_ac_2_5_bloque_faltante_es_incompleto_e_indica_que_falta():
    r = normalizar(quitar(pagina_f2(), "REVANCHA"), F2, 3426)
    assert r.resultado is ResultadoIntento.INCOMPLETO
    assert M.REVANCHA not in r.datos.modalidades
    assert "Falta: Revancha" in textos(r)


# -- Historia 3 (T047) --------------------------------------------------------------


@pytest.mark.parametrize("ficha, rotulo", [
    (F1, "SORTEO TRADICIONAL"), (F2, "TRADICIONAL"), (F3, "Tradicional Primer Sorteo"),
    (F2, "  tradicional "),
])  # fmt: skip
def test_ac_3_1_rotulos_equivalentes(ficha, rotulo):
    assert ficha.rotulos[" ".join(rotulo.split()).casefold()] is M.PRIMER_SORTEO


def test_ac_3_1_revancha_de_f1_nunca_es_la_segunda():
    assert F1.rotulos["la segunda del quini 6 revancha"] is M.REVANCHA
    assert F1.rotulos["la segunda del quini 6"] is M.LA_SEGUNDA


def test_rotulo_desconocido_no_se_asigna_por_parecido():
    r = normalizar(cambiar(pagina_f2(), "REVANCHA", rotulo="REVANCHA ESPECIAL"), F2, 3426)
    assert r.resultado is ResultadoIntento.INCOMPLETO
    assert M.REVANCHA not in r.datos.modalidades
    assert (
        "Rótulo no reconocido: «REVANCHA ESPECIAL». Ese bloque no se asignó a ninguna modalidad."
        in textos(r)
    )  # noqa: E501


def test_ac_3_2_numeros_en_distinto_orden_son_el_mismo_conjunto():
    de_f2 = normalizar(pagina_f2(), F2, 3426).datos.modalidades[M.PRIMER_SORTEO].numeros
    pagina1 = f1.interpretar_sorteo(leer("f1/sorteo-3426.html"))
    de_f1 = normalizar(pagina1, F1, 3426, FECHA).datos.modalidades[M.PRIMER_SORTEO].numeros
    assert de_f1 == de_f2 == frozenset({1, 2, 10, 13, 38, 39})


def test_ac_3_3_premio_extra_sin_numeros_propios():
    r = normalizar(pagina_f2(), F2, 3426)
    assert r.datos.modalidades[M.PREMIO_EXTRA].numeros is None
    assert (
        "Los números de Premio Extra de la fuente no coinciden con sus extracciones"
        not in textos(r)
    )


def test_ac_3_13_premio_extra_que_no_coincide_con_la_union():
    r = normalizar(cambiar(pagina_f2(), "POZO EXTRA", numeros_textos=("01", "02", "03")), F2, 3426)
    observacion = [o for o in r.observaciones if o.codigo == "obs.premio_extra_no_coincide"]
    assert observacion and observacion[0].es_inconsistencia


def test_ac_3_13_premio_extra_con_repetidos_en_f2_coincide_como_conjunto():
    pagina = pagina_f2()
    extra = tuple(
        n for b in pagina.bloques[:3] for n in b.numeros_textos
    )  # 18 números con repetidos
    r = normalizar(cambiar(pagina, "POZO EXTRA", numeros_textos=extra), F2, 3426)
    assert not [o for o in r.observaciones if o.codigo == "obs.premio_extra_no_coincide"]


def test_ac_3_8_importe_invalido():
    """[002] RN-16: «1,234,567» no tiene ninguna de las formas corregibles (D-32 exige dos
    decimales después de la última coma)."""
    filas = (FilaPremioCruda("5", "17", "1,234,567"),)
    r = normalizar(cambiar(pagina_f2(), "SIEMPRE SALE", filas_premios=filas), F2, 3426)
    cat = categoria(r, M.SIEMPRE_SALE, "GANADORA")
    assert cat.importe_individual is NO_DISPONIBLE
    assert cat.texto_original == "1,234,567"
    assert "Importe con formato no reconocido: «1,234,567»" in textos(r)
    assert r.resultado is ResultadoIntento.INCOMPLETO


@pytest.mark.parametrize("fuente, ficha, interprete", [("f2", F2, f2), ("f3", F3, f3)])
def test_ac_3_20_comas_en_todos_los_separadores_se_corrigen(fuente, ficha, interprete):
    """[002] RN-16, D-32: sorteo 3398 (09/08/2026), Tradicional, Segundo Premio: las fuentes
    publican «494,443,71» → $ 494.443,71, con nota informativa y sin "Falta: … importe
    individual"."""
    pagina = interprete.interpretar_sorteo(leer(f"{fuente}/sorteo-3398.html"))
    r = normalizar(pagina, ficha, 3398)
    cat = categoria(r, M.PRIMER_SORTEO, "SEGUNDO")
    assert cat.importe_individual == Valor(Decimal("494443.71"))
    assert cat.texto_original is None
    assert "Importe corregido: «494,443,71» → $ 494.443,71" in textos(r)
    assert not any(o.codigo == "obs.importe_invalido" for o in r.observaciones)
    assert not any("importe individual" in t and t.startswith("Falta") for t in textos(r))


def test_ac_3_16_importe_mal_cargado_se_corrige_con_nota_informativa():
    """[002] RN-16, D-18: «410.1156,25» → $ 410.115,63, sin cambiar el resultado del intento."""
    filas = (FilaPremioCruda("5", "17", "$ 410.1156,25"),)
    r = normalizar(cambiar(pagina_f2(), "SIEMPRE SALE", filas_premios=filas), F2, 3426)
    cat = categoria(r, M.SIEMPRE_SALE, "GANADORA")
    assert cat.importe_individual == Valor(Decimal("410115.63"))
    assert cat.texto_original is None
    obs = [o for o in r.observaciones if o.codigo == "obs.importe_corregido"]
    assert obs[0].texto == "Importe corregido: «$ 410.1156,25» → $ 410.115,63"
    assert obs[0].informativa and not obs[0].es_inconsistencia
    assert r.resultado is ResultadoIntento.OBTENIDO


def test_d_20_importe_con_tres_decimales_se_redondea_con_nota_informativa():
    """[002] RN-16, D-20: sorteo 3250, «1.278.143,114» → $ 1.278.143,11."""
    filas = (FilaPremioCruda("5", "17", "1.278.143,114"),)
    r = normalizar(cambiar(pagina_f2(), "SIEMPRE SALE", filas_premios=filas), F2, 3426)
    assert categoria(r, M.SIEMPRE_SALE, "GANADORA").importe_individual == Valor(
        Decimal("1278143.11")
    )
    assert "Importe corregido: «1.278.143,114» → $ 1.278.143,11" in textos(r)
    assert not any(o.codigo == "obs.importe_invalido" for o in r.observaciones)
    assert r.resultado is ResultadoIntento.OBTENIDO


def test_ac_3_19_puntos_de_miles_mal_puestos_se_reagrupan_con_nota_informativa():
    """[002] RN-16, D-31: sorteo 3383, «1.0867.330» → $ 10.867.330,00 (Segundo Premio)."""
    filas = (FilaPremioCruda("5", "21", "1.0867.330"),)
    r = normalizar(cambiar(pagina_f2(), "SIEMPRE SALE", filas_premios=filas), F2, 3426)
    cat = categoria(r, M.SIEMPRE_SALE, "GANADORA")
    assert cat.importe_individual == Valor(Decimal("10867330"))
    assert cat.texto_original is None
    assert "Importe corregido: «1.0867.330» → $ 10.867.330,00" in textos(r)
    assert not any(o.codigo == "obs.importe_invalido" for o in r.observaciones)
    assert r.resultado is ResultadoIntento.OBTENIDO


def test_ac_3_19_vacante_con_puntos_mal_puestos_es_su_pozo():
    """[002] RN-16, RN-17, D-31: sorteo 3415, Revancha vacante «2.57.2821.792»."""
    filas = (FilaPremioCruda("6", "0", "2.57.2821.792"),)
    r = normalizar(cambiar(pagina_f2(), "REVANCHA", filas_premios=filas), F2, 3426)
    cat = categoria(r, M.REVANCHA, "UNICO")
    assert cat.pozo_destinado == Valor(Decimal("2572821792"))
    assert "Importe corregido: «2.57.2821.792» → $ 2.572.821.792,00" in textos(r)


@pytest.mark.parametrize("numeros, esperado", [
    (("02", "01", "39", "13", "10", "10"), "Tradicional: la fuente repite el número 10. No se usan."),  # noqa: E501
    (("02", "01", "39", "13", "10", "46"), "Tradicional: la fuente publica «46», fuera de 00 a 45. No se usan."),  # noqa: E501
    (("02", "01", "39", "13", "10"), "Tradicional: la fuente publica 5 números en lugar de seis. No se usan."),  # noqa: E501
])  # fmt: skip
def test_ac_3_9_numeros_invalidos_se_descartan_sin_corregir(numeros, esperado):
    r = normalizar(cambiar(pagina_f2(), "TRADICIONAL", numeros_textos=numeros), F2, 3426)
    assert r.datos.modalidades[M.PRIMER_SORTEO].numeros is None
    assert r.datos.modalidades[M.PRIMER_SORTEO].numeros_descartados
    assert esperado in textos(r)
    assert r.resultado is ResultadoIntento.INCOMPLETO


def test_ac_3_10_siempre_sale_con_5_aciertos_y_17_ganadores():
    cat = categoria(normalizar(pagina_f2(3427), F2, 3427), M.SIEMPRE_SALE, "GANADORA")
    assert cat.aciertos == Valor(5) and cat.ganadores == Valor(17)


def _con_fila_extra(pagina, fecha_texto):
    filas = pagina.bloques[0].filas_premios + (FilaPremioCruda("3", "5000", "1.000"),)
    return replace(cambiar(pagina, "TRADICIONAL", filas_premios=filas), fecha_texto=fecha_texto)


def test_rn_25_antes_del_18_06_2024_categoria_de_n_aciertos():
    r = normalizar(_con_fila_extra(pagina_f2(), "17/06/2024"), F2, 3426)
    cat = categoria(r, M.PRIMER_SORTEO, "ACIERTOS_3")
    assert cat.aciertos == Valor(3) and cat.ganadores == Valor(5000)


def test_rn_25_desde_el_18_06_2024_categoria_fuera_del_catalogo():
    r = normalizar(_con_fila_extra(pagina_f2(), "18/06/2024"), F2, 3426)
    assert "ACIERTOS_3" not in r.datos.modalidades[M.PRIMER_SORTEO].categorias
    assert any(o.codigo == "obs.categoria_fuera_catalogo" for o in r.observaciones)


def test_ac_3_14_cero_ganadores_y_cero_pesos_no_corresponde():
    filas = (FilaPremioCruda("6", "Vacante", "0,00"),) + pagina_f2().bloques[0].filas_premios[1:]
    r = normalizar(cambiar(pagina_f2(), "TRADICIONAL", filas_premios=filas), F2, 3426)
    cat = categoria(r, M.PRIMER_SORTEO, "PRIMER")
    assert cat.importe_individual is NO_CORRESPONDE
    assert cat.pozo_destinado is NO_DISPONIBLE  # nunca un pozo de $ 0 inventado


def test_d_22_sin_dato_de_acumulacion():
    cat = categoria(normalizar(pagina_f2(), F2, 3426), M.PRIMER_SORTEO, "PRIMER")
    assert not hasattr(cat, "se_acumula")


def test_d_30_texto_fijo_de_f1_se_ignora():
    """[002] RN-17, D-30: "55 millones de pesos" es fijo en F1 (igual de 2024 a 2026)."""
    pagina = f1.interpretar_sorteo(leer("f1/sorteo-3426.html"))
    r = normalizar(pagina, F1, 3426, FECHA)
    cat = categoria(r, M.PREMIO_EXTRA, "GANADORA")
    assert cat.pozo_destinado is NO_DISPONIBLE
    assert cat.aciertos is NO_DISPONIBLE  # F1 publica "-": no lo publica por diseño
    assert not [o for o in r.observaciones if o.codigo == "obs.pozo_premio_extra_texto"]
    assert r.resultado is ResultadoIntento.OBTENIDO


def test_rn_17_texto_fijo_de_f2_se_ignora():
    cat = categoria(normalizar(pagina_f2(), F2, 3426), M.PREMIO_EXTRA, "GANADORA")
    assert cat.pozo_destinado is NO_DISPONIBLE  # "85 millones de pesos" no se toma


def test_rn_21_f1_con_fecha_distinta_de_la_direccion():
    pagina = f1.interpretar_sorteo(leer("f1/sorteo-3426.html"))
    r = normalizar(pagina, F1, 3426, date(2026, 11, 16))
    assert r.resultado is ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA
    assert r.datos is None
    assert textos(r) == [
        "El número o la fecha de la página no coinciden con los de la dirección consultada"
    ]


def test_rn_26_siempre_sale_invalida():
    filas = (FilaPremioCruda("5", "0", "1.000"),)
    r = normalizar(cambiar(pagina_f2(), "SIEMPRE SALE", filas_premios=filas), F2, 3426)
    obs = [o for o in r.observaciones if o.codigo == "obs.siempre_sale_invalida"]
    assert obs and obs[0].es_inconsistencia


def test_rn_26_premio_extra_invalida():
    filas = (FilaPremioCruda("3", "10", "1.000"),)
    r = normalizar(cambiar(pagina_f2(), "POZO EXTRA", filas_premios=filas), F2, 3426)
    assert any(o.codigo == "obs.premio_extra_invalida" for o in r.observaciones)


def test_rn_26_valor_negativo():
    filas = (FilaPremioCruda("5", "17", "-1.000"),)
    r = normalizar(cambiar(pagina_f2(), "SIEMPRE SALE", filas_premios=filas), F2, 3426)
    assert "La fuente publica un valor negativo: «-1.000». No se usa." in textos(r)
    assert categoria(r, M.SIEMPRE_SALE, "GANADORA").importe_individual is NO_DISPONIBLE


def test_rn_26_dos_extracciones_iguales_es_advertencia():
    pagina = pagina_f2()
    iguales = cambiar(pagina, "LA SEGUNDA", numeros_textos=pagina.bloques[0].numeros_textos)
    r = normalizar(iguales, F2, 3426)
    obs = [o for o in r.observaciones if o.codigo == "obs.extracciones_iguales"]
    assert obs[0].texto == ("Tradicional y La Segunda: la fuente publica los mismos seis números")
    assert not obs[0].es_inconsistencia


def test_sc_002_ningun_importe_calculado_ni_desconocido_como_cero():
    """Todo importe con valor es uno de los textos publicados; los desconocidos no son 0."""
    pagina = f1.interpretar_sorteo(leer("f1/sorteo-3427.html"))
    r = normalizar(pagina, F1, 3427, date(2026, 11, 18))
    publicados = {
        Decimal(t.replace("$", "").replace(".", "").replace(",", ".").strip())
        for b in pagina.bloques
        for fila in b.filas_premios or ()
        for t in [fila.importe_texto]
    } | {Decimal(55000000)}
    for md in r.datos.modalidades.values():
        for cat in md.categorias.values():
            for dato in (cat.pozo_destinado, cat.importe_individual):
                if isinstance(dato, Valor):
                    assert dato.v in publicados
                else:
                    assert dato in (NO_DISPONIBLE, NO_CORRESPONDE)


@pytest.mark.parametrize("texto, esperado", [
    ("15/11/2026", date(2026, 11, 15)),
    ("domingo 15-11-2026", date(2026, 11, 15)),
    ("1/2/2026", date(2026, 2, 1)),
    ("domingo 09 de agosto de 2026", date(2026, 8, 9)),
    ("miércoles 18 de noviembre del 2026", date(2026, 11, 18)),
    ("30/02/2026", None),
    ("", None),
])  # fmt: skip
def test_parsear_fecha_fuente(texto, esperado):
    assert parsear_fecha_fuente(texto) == esperado


def test_bloque_crudo_por_defecto():
    assert BloqueCrudo("X").numeros_textos is None
