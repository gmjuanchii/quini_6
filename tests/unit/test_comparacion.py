"""Comparación de jugadas (RN-28 a RN-33, RN-49 a RN-54; AC-5.1 a AC-5.33; SC-005).

Pruebas del dominio puro: no usan la base de datos.
"""

from datetime import date
from decimal import Decimal

import pytest

from dominio.comparacion import (
    AVISO_ACIERTOS_SUPERAN_CATEGORIA,
    AVISO_EN_REVISION,
    Elegibilidad,
    EstadoValidacion,
    ResultadoPremio,
    comparar_jugada,
)
from dominio.tipos import (
    ORDEN_MODALIDADES,
    BloqueNumerosVista,
    BloquePremiosVista,
    CategoriaPublicada,
    DatosConcurso,
    EstadoBloque,
)

PS, LS, RV, SS, PE = ORDEN_MODALIDADES
CON = ResultadoPremio.CON_PREMIO
SIN = ResultadoPremio.SIN_PREMIO
PEND = ResultadoPremio.PENDIENTE_DETERMINACION
FECHA = date(2025, 3, 2)

EJEMPLOS = {
    1: (
        {3, 8, 14, 21, 32, 40},
        {
            PS: {3, 8, 14, 21, 32, 40},
            LS: {3, 8, 14, 21, 32, 41},
            RV: {3, 8, 14, 21, 33, 41},
            SS: {3, 8, 14, 22, 33, 41},
        },
    ),
    2: (
        {1, 7, 12, 19, 28, 44},
        {
            PS: {1, 7, 12, 19, 30, 45},
            LS: {1, 7, 12, 20, 30, 45},
            RV: {1, 7, 12, 19, 28, 44},
            SS: {1, 7, 12, 19, 28, 40},
        },
    ),
    3: (
        {2, 9, 16, 23, 31, 42},
        {
            PS: {2, 9, 16, 25, 34, 45},
            LS: {2, 11, 16, 23, 35, 42},
            RV: {5, 9, 18, 23, 31, 42},
            SS: {2, 9, 16, 23, 31, 40},
        },
    ),
}


def _num(numeros, estado=EstadoBloque.PUBLICADO):
    publicado = estado.publicado
    return BloqueNumerosVista(estado, frozenset(numeros) if publicado else None)


def _premios(categorias=None, aciertos=None, sin_ganadores=False, estado=EstadoBloque.PUBLICADO):
    if not estado.publicado:
        return BloquePremiosVista(estado)
    return BloquePremiosVista(
        estado,
        tuple(CategoriaPublicada(codigo, **datos) for codigo, datos in (categorias or {}).items()),
        aciertos,
        sin_ganadores,
    )


def datos(numeros: dict, premios: dict | None = None, fecha=FECHA, modalidades=None):
    modalidades = frozenset(modalidades or ORDEN_MODALIDADES)
    return DatosConcurso(
        fecha_sorteo=fecha,
        modalidades=modalidades,
        numeros={
            m: (v if isinstance(v, BloqueNumerosVista) else _num(v)) for m, v in numeros.items()
        },
        premios=premios or {},
    )


def _por_modalidad(resultados):
    return {r.modalidad: r for r in resultados}


def comparar(jugada, numeros, premios=None, **kw):
    return _por_modalidad(comparar_jugada(frozenset(jugada), datos(numeros, premios, **kw)))


# --- Ejemplos de referencia (AC-5.33) ------------------------------------------------------


class TestEjemplosDeReferencia:
    def test_ejemplo_1(self):
        jugada, numeros = EJEMPLOS[1]
        r = comparar(jugada, numeros)
        assert (r[PS].aciertos, r[PS].resultado_premio, r[PS].categoria) == (
            6,
            CON,
            "Primer Premio",
        )
        assert (r[LS].aciertos, r[LS].resultado_premio, r[LS].categoria) == (
            5,
            CON,
            "Segundo Premio",
        )
        assert (r[RV].aciertos, r[RV].resultado_premio) == (4, SIN)
        assert r[SS].aciertos == 3
        assert r[PE].aciertos == 6
        assert r[PE].elegibilidad is Elegibilidad.EXCLUIDA
        assert r[PE].excluida_por is PS
        assert r[PE].resultado_premio is None
        assert r[PE].conjunto == frozenset({3, 8, 14, 21, 32, 33, 40, 41})

    def test_ejemplo_2(self):
        jugada, numeros = EJEMPLOS[2]
        r = comparar(jugada, numeros)
        assert (r[PS].aciertos, r[PS].resultado_premio, r[PS].categoria) == (
            4,
            CON,
            "Tercer Premio",
        )
        assert (r[LS].aciertos, r[LS].resultado_premio) == (3, SIN)
        assert (r[RV].aciertos, r[RV].resultado_premio, r[RV].categoria) == (
            6,
            CON,
            "Premio Revancha",
        )
        assert r[SS].aciertos == 5
        assert r[PE].elegibilidad is Elegibilidad.EXCLUIDA
        assert r[PE].excluida_por is RV
        assert len(r[PE].conjunto) == 9

    def test_ejemplo_3(self):
        jugada, numeros = EJEMPLOS[3]
        r = comparar(jugada, numeros)
        assert (r[PS].aciertos, r[PS].resultado_premio) == (3, SIN)
        assert (r[LS].aciertos, r[LS].resultado_premio, r[LS].categoria) == (
            4,
            CON,
            "Tercer Premio",
        )
        assert (r[RV].aciertos, r[RV].resultado_premio) == (4, SIN)
        assert r[SS].aciertos == 5
        assert r[PE].elegibilidad is Elegibilidad.PARTICIPA
        assert r[PE].aciertos == 6
        assert r[PE].resultado_premio is CON
        assert r[PE].categoria == "Premio Extra (6 aciertos)"
        assert len(r[PE].conjunto) == 13

    @pytest.mark.parametrize(
        ("ejemplo", "categoria", "esperado", "aviso"),
        [
            (1, 3, CON, False),
            (1, 4, SIN, False),
            (1, 5, SIN, False),
            (1, 6, SIN, False),
            (1, None, PEND, False),
            (1, 2, PEND, True),
            (1, 0, PEND, True),
            (2, 5, CON, False),
            (2, 6, SIN, False),
            (2, None, PEND, False),
            (2, 4, PEND, True),
            (3, 5, CON, False),
            (3, 6, SIN, False),
            (3, None, PEND, False),
            (3, 3, PEND, True),
        ],
    )
    def test_siempre_sale_variantes(self, ejemplo, categoria, esperado, aviso):
        jugada, numeros = EJEMPLOS[ejemplo]
        premios = {SS: _premios({"GANADORA": {"ganadores": 10}}, aciertos=categoria)}
        r = comparar(jugada, numeros, premios)[SS]
        assert r.resultado_premio is esperado
        assert (AVISO_ACIERTOS_SUPERAN_CATEGORIA in r.avisos) is aviso
        if esperado is CON:
            assert r.categoria == f"Siempre Sale ({r.aciertos} aciertos)"


# --- Primer Sorteo, La Segunda y Revancha ------------------------------------------------

BASE = {1, 2, 3, 4, 5, 6}


def _con_aciertos(n, desde=10):
    """Extracción con ``n`` números de BASE y el resto distintos."""
    return set(list(sorted(BASE))[:n]) | set(range(desde, desde + 6 - n))


class TestTradicionales:
    @pytest.mark.parametrize("modalidad", [PS, LS])
    @pytest.mark.parametrize(
        ("aciertos", "resultado", "categoria"),
        [
            (6, CON, "Primer Premio"),
            (5, CON, "Segundo Premio"),
            (4, CON, "Tercer Premio"),
            (3, SIN, None),
            (0, SIN, None),
        ],
    )
    def test_ac_5_14_a_5_17(self, modalidad, aciertos, resultado, categoria):
        r = comparar(BASE, {modalidad: _con_aciertos(aciertos)}, modalidades=[modalidad])
        assert r[modalidad].aciertos == aciertos
        assert r[modalidad].resultado_premio is resultado
        assert r[modalidad].categoria == categoria

    def test_ac_5_18_no_se_suman(self):
        r = comparar(
            BASE, {PS: {1, 2, 3, 10, 11, 12}, LS: {4, 5, 6, 20, 21, 22}}, modalidades=[PS, LS]
        )
        assert r[PS].aciertos == 3 and r[PS].resultado_premio is SIN
        assert r[LS].aciertos == 3 and r[LS].resultado_premio is SIN
        assert r[PS].numeros_acertados == frozenset({1, 2, 3})

    @pytest.mark.parametrize(("aciertos", "resultado"), [(6, CON), (5, SIN), (4, SIN)])
    def test_ac_5_19_y_5_20_revancha(self, aciertos, resultado):
        r = comparar(BASE, {RV: _con_aciertos(aciertos)}, modalidades=[RV])[RV]
        assert r.resultado_premio is resultado
        assert r.categoria == ("Premio Revancha" if resultado is CON else None)


# --- Siempre Sale -------------------------------------------------------------------------


def _ss(aciertos, categoria=None, publicada=True, ganadores=5):
    premios = {}
    if publicada:
        premios[SS] = _premios({"GANADORA": {"ganadores": ganadores}}, aciertos=categoria)
    return comparar(BASE, {SS: _con_aciertos(aciertos)}, premios, modalidades=[SS])[SS]


class TestSiempreSale:
    def test_ac_5_21_seis_sin_categoria(self):
        r = _ss(6, publicada=False)
        assert r.resultado_premio is CON and r.categoria == "Siempre Sale (6 aciertos)"
        assert _ss(6, categoria=None).resultado_premio is CON
        assert _ss(6, categoria=6).resultado_premio is CON

    @pytest.mark.parametrize("categoria", [5, 4, 0])
    def test_p02_seis_frente_a_categoria_menor(self, categoria):
        r = _ss(6, categoria=categoria)
        assert r.resultado_premio is PEND
        assert AVISO_ACIERTOS_SUPERAN_CATEGORIA in r.avisos

    def test_ac_5_22(self):
        assert _ss(5, categoria=6).resultado_premio is SIN
        r = _ss(5, categoria=5)
        assert r.resultado_premio is CON and r.categoria == "Siempre Sale (5 aciertos)"

    def test_ac_5_23(self):
        r = _ss(4, categoria=4)
        assert r.resultado_premio is CON and r.categoria == "Siempre Sale (4 aciertos)"
        r = _ss(4, publicada=False)
        assert r.resultado_premio is PEND and not r.avisos
        assert _ss(4, categoria=None).resultado_premio is PEND

    def test_ac_5_30(self):
        r = _ss(5, categoria=4)
        assert r.resultado_premio is PEND
        assert AVISO_ACIERTOS_SUPERAN_CATEGORIA in r.avisos

    def test_ac_5_4_cero_aciertos_con_categoria_cero(self):
        r = _ss(0, categoria=0)
        assert r.resultado_premio is CON and r.categoria == "Siempre Sale (0 aciertos)"
        assert _ss(0, categoria=3).resultado_premio is SIN


# --- Premio Extra -------------------------------------------------------------------------

EJ3_JUGADA, EJ3_NUMEROS = EJEMPLOS[3]


def _pe(jugada, numeros, categoria=None, sin_ganadores=False, publicada=True):
    premios = {}
    if publicada:
        premios[PE] = _premios(
            {"GANADORA": {"ganadores": 2}}, aciertos=categoria, sin_ganadores=sin_ganadores
        )
    return comparar(jugada, numeros, premios)[PE]


class TestPremioExtra:
    def test_ac_5_24_participa_con_seis_repartidos(self):
        r = _pe(EJ3_JUGADA, EJ3_NUMEROS, publicada=False)
        assert r.elegibilidad is Elegibilidad.PARTICIPA
        assert r.resultado_premio is CON
        assert r.numeros_acertados == frozenset(EJ3_JUGADA)
        assert _pe(EJ3_JUGADA, EJ3_NUMEROS, categoria=6).resultado_premio is CON

    @pytest.mark.parametrize(("categoria", "sin"), [(5, False), (4, False), (None, True)])
    def test_p02_seis_frente_a_categoria_menor_o_sin_ganadores(self, categoria, sin):
        r = _pe(EJ3_JUGADA, EJ3_NUMEROS, categoria=categoria, sin_ganadores=sin)
        assert r.resultado_premio is PEND
        assert AVISO_ACIERTOS_SUPERAN_CATEGORIA in r.avisos

    @pytest.mark.parametrize("excluyente", [PS, LS, RV])
    def test_ac_5_25_excluida(self, excluyente):
        numeros = {
            PS: {10, 11, 12, 13, 14, 15},
            LS: {20, 21, 22, 23, 24, 25},
            RV: {30, 31, 32, 33, 34, 35},
            SS: {1, 2, 3, 4, 5, 6},
        }
        numeros[excluyente] = set(BASE)
        r = comparar(BASE, numeros)
        assert r[PE].elegibilidad is Elegibilidad.EXCLUIDA
        assert r[PE].excluida_por is excluyente
        assert r[PE].resultado_premio is None
        assert r[excluyente].resultado_premio is CON

    def test_ac_5_25_primera_extraccion_en_orden(self):
        numeros = {PS: set(BASE), LS: set(BASE), RV: set(BASE), SS: {40, 41, 42, 43, 44, 45}}
        assert comparar(BASE, numeros)[PE].excluida_por is PS

    def test_siempre_sale_con_seis_no_excluye(self):
        numeros = {
            PS: {1, 2, 3, 10, 11, 12},
            LS: {4, 5, 6, 20, 21, 22},
            RV: {30, 31, 32, 33, 34, 35},
            SS: set(BASE),
        }
        r = comparar(BASE, numeros)
        assert r[PE].elegibilidad is Elegibilidad.PARTICIPA
        assert r[PE].resultado_premio is CON

    def test_ac_5_26_repetidos_cuentan_una_vez(self):
        numeros = {
            PS: {1, 2, 3, 10, 11, 12},
            LS: {1, 2, 3, 20, 21, 22},
            RV: {1, 2, 3, 30, 31, 32},
            SS: {40, 41, 42, 43, 44, 45},
        }
        r = comparar(BASE, numeros)[PE]
        assert r.aciertos == 3
        assert len(r.conjunto) == 12

    @pytest.mark.parametrize(
        ("aciertos", "categoria", "sin", "esperado"),
        [
            (5, 6, False, SIN),
            (5, 5, False, CON),
            (5, None, False, PEND),
            (5, 4, False, PEND),
            (4, 6, False, SIN),
            (4, 5, False, SIN),
            (4, 4, False, CON),
            (4, None, False, PEND),
            (3, None, False, SIN),
            (3, 4, False, SIN),
            (0, None, False, SIN),
            (5, None, True, SIN),
            (4, None, True, SIN),
        ],
    )
    def test_ac_5_27(self, aciertos, categoria, sin, esperado):
        base = sorted(BASE)
        numeros = {
            PS: set(base[:aciertos]) | set(range(10, 16 - aciertos)),
            LS: {20, 21, 22, 23, 24, 25},
            RV: {30, 31, 32, 33, 34, 35},
            SS: {40, 41, 42, 43, 44, 45},
        }
        r = _pe(BASE, numeros, categoria=categoria, sin_ganadores=sin)
        assert r.aciertos == aciertos
        assert r.resultado_premio is esperado
        if esperado is CON:
            assert r.categoria == f"Premio Extra ({aciertos} aciertos)"
        if (aciertos, categoria) == (5, 4):
            assert AVISO_ACIERTOS_SUPERAN_CATEGORIA in r.avisos

    def test_ac_5_28_siempre_sale_no_cuenta(self):
        numeros = {
            PS: {1, 2, 3, 10, 11, 12},
            LS: {20, 21, 22, 23, 24, 25},
            RV: {30, 31, 32, 33, 34, 35},
            SS: {4, 5, 6, 40, 41, 42},
        }
        r = comparar(BASE, numeros)[PE]
        assert r.aciertos == 3
        assert not ({4, 5, 6} & r.conjunto)
        assert r.resultado_premio is SIN

    @pytest.mark.parametrize(
        ("estado_ls", "esperado"),
        [
            (EstadoBloque.SIN_CARGAR, EstadoValidacion.RESULTADO_PENDIENTE),
            (EstadoBloque.BORRADOR, EstadoValidacion.PENDIENTE_VALIDACION),
            (EstadoBloque.OBSERVADO, EstadoValidacion.PENDIENTE_VALIDACION),
        ],
    )
    def test_ac_5_29_extraccion_sin_publicar(self, estado_ls, esperado):
        numeros = {PS: set(BASE), RV: {30, 31, 32, 33, 34, 35}}
        if estado_ls is not EstadoBloque.SIN_CARGAR:
            numeros[LS] = BloqueNumerosVista(estado_ls, None)
        r = comparar(BASE, numeros)[PE]
        assert r.estado_validacion is esperado
        assert r.aciertos is None and r.conjunto is None and r.elegibilidad is None

    def test_ac_5_29_sin_cargar_prevalece(self):
        numeros = {PS: BloqueNumerosVista(EstadoBloque.BORRADOR, None), RV: set(BASE)}
        r = comparar(BASE, numeros)[PE]
        assert r.estado_validacion is EstadoValidacion.RESULTADO_PENDIENTE


# --- Varias modalidades -------------------------------------------------------------------


class TestVariasModalidades:
    def test_ac_5_31_un_resultado_por_modalidad_en_orden(self):
        resultados = comparar_jugada(frozenset(BASE), datos({}, modalidades=[SS, PE, PS, LS, RV]))
        assert [r.modalidad for r in resultados] == [PS, LS, RV, SS, PE]

    def test_solo_modalidades_aplicables(self):
        resultados = comparar_jugada(frozenset(BASE), datos({}, modalidades=[PS, RV]))
        assert [r.modalidad for r in resultados] == [PS, RV]

    def test_ac_5_32_premios_simultaneos(self):
        r = comparar(BASE, {PS: set(BASE), LS: _con_aciertos(5)}, modalidades=[PS, LS])
        assert r[PS].categoria == "Primer Premio" and r[LS].categoria == "Segundo Premio"


# --- Estados de validación ----------------------------------------------------------------


class TestEstadosDeValidacion:
    @pytest.mark.parametrize(
        ("estado", "esperado"),
        [
            (EstadoBloque.BORRADOR, EstadoValidacion.PENDIENTE_VALIDACION),
            (EstadoBloque.OBSERVADO, EstadoValidacion.PENDIENTE_VALIDACION),
            (EstadoBloque.PUBLICADO, EstadoValidacion.PUBLICADO),
            (EstadoBloque.EN_REVISION, EstadoValidacion.EN_REVISION),
        ],
    )
    def test_estados(self, estado, esperado):
        bloque = BloqueNumerosVista(estado, frozenset(BASE) if estado.publicado else None)
        r = comparar(BASE, {PS: bloque}, modalidades=[PS])[PS]
        assert r.estado_validacion is esperado
        if not estado.publicado:
            assert (r.aciertos, r.numeros_acertados, r.resultado_premio, r.importe) == (
                None,
                None,
                None,
                None,
            )
            assert r.importe_pendiente is False

    def test_ac_5_1_sin_cargar(self):
        r = comparar(BASE, {}, modalidades=[PS])[PS]
        assert r.estado_validacion is EstadoValidacion.RESULTADO_PENDIENTE
        assert r.aciertos is None

    def test_ac_5_12_en_revision(self):
        bloque = BloqueNumerosVista(EstadoBloque.EN_REVISION, frozenset(BASE))
        r = comparar(BASE, {PS: bloque}, modalidades=[PS])[PS]
        assert AVISO_EN_REVISION in r.avisos
        assert r.resultado_premio is CON

    def test_en_revision_en_premio_extra(self):
        numeros = {
            PS: BloqueNumerosVista(EstadoBloque.EN_REVISION, frozenset({1, 2, 3, 10, 11, 12})),
            LS: {20, 21, 22, 23, 24, 25},
            RV: {30, 31, 32, 33, 34, 35},
        }
        r = comparar(BASE, numeros)[PE]
        assert r.estado_validacion is EstadoValidacion.EN_REVISION
        assert AVISO_EN_REVISION in r.avisos


# --- Importe ------------------------------------------------------------------------------


class TestImporte:
    def test_ac_5_3_premios_sin_publicar(self):
        r = comparar(BASE, {PS: set(BASE)}, modalidades=[PS])[PS]
        assert r.resultado_premio is CON
        assert r.importe is None and r.importe_pendiente is True

    def test_ac_5_6_importe_publicado(self):
        premios = {
            PS: _premios({"PRIMER": {"ganadores": 1, "importe_individual": Decimal("1500000.50")}})
        }
        r = comparar(BASE, {PS: set(BASE)}, premios, modalidades=[PS])[PS]
        assert r.importe == Decimal("1500000.50") and r.importe_pendiente is False

    def test_ac_5_7_sin_importe_individual_nunca_calcula(self):
        premios = {
            PS: _premios(
                {
                    "PRIMER": {
                        "ganadores": 2,
                        "importe_categoria": Decimal("1000"),
                        "importe_individual": None,
                    }
                }
            )
        }
        r = comparar(BASE, {PS: set(BASE)}, premios, modalidades=[PS])[PS]
        assert r.importe is None and r.importe_pendiente is True

    def test_premios_en_borrador_no_aportan_importe(self):
        premios = {PS: _premios(estado=EstadoBloque.BORRADOR)}
        r = comparar(BASE, {PS: set(BASE)}, premios, modalidades=[PS])[PS]
        assert r.importe_pendiente is True

    def test_sin_premio_sin_importe(self):
        r = comparar(BASE, {PS: _con_aciertos(2)}, modalidades=[PS])[PS]
        assert r.importe is None and r.importe_pendiente is False


# --- RN-33 --------------------------------------------------------------------------------


class TestReglasPorPeriodo:
    def test_ac_5_11_anterior_a_la_vigencia(self):
        jugada, numeros = EJEMPLOS[1]
        r = comparar(jugada, numeros, fecha=date(2024, 6, 17))
        for modalidad in (PS, LS, RV, SS, PE):
            assert r[modalidad].resultado_premio is PEND
            assert r[modalidad].aciertos is not None
        assert r[PS].aciertos == 6

    def test_desde_la_vigencia_aplica_reglas(self):
        jugada, numeros = EJEMPLOS[1]
        r = comparar(jugada, numeros, fecha=date(2024, 6, 18))
        assert r[PS].resultado_premio is CON
