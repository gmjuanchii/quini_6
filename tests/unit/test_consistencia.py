"""RN-22: controles de consistencia antes de publicar."""

from datetime import date
from decimal import Decimal

import pytest

from dominio.consistencia import revisar_numeros, revisar_premios
from dominio.tipos import CategoriaPublicada, Modalidad

FUENTE = ("Extracto oficial N.º 3215", date(2025, 3, 3))
HOY = date(2025, 3, 3)
FECHA = date(2025, 3, 2)
SEIS = ["01", "02", "03", "04", "05", "06"]


def _codigos(observaciones):
    return {o.codigo for o in observaciones}


class TestNumerosBloqueantes:
    @pytest.mark.parametrize(
        ("valores", "codigo"),
        [
            (SEIS[:5], "CANTIDAD"),
            ([*SEIS, "07"], "CANTIDAD"),
            (["01", "01", "03", "04", "05", "06"], "REPETIDO"),
            (["46", "02", "03", "04", "05", "06"], "FUERA_DE_RANGO"),
        ],
    )
    def test_numeros_invalidos(self, valores, codigo):
        bloqueantes, _ = revisar_numeros(valores, {}, FECHA, HOY, FUENTE)
        assert codigo in _codigos(bloqueantes)

    @pytest.mark.parametrize("fuente", [None, ("", FECHA), ("Extracto", None), ("  ", None)])
    def test_falta_fuente(self, fuente):
        bloqueantes, _ = revisar_numeros(SEIS, {}, FECHA, HOY, fuente)
        assert "SIN_FUENTE" in _codigos(bloqueantes)

    def test_mensaje_indica_que_falta(self):
        bloqueantes, _ = revisar_numeros(SEIS, {}, FECHA, HOY, ("", None))
        textos = " ".join(b.texto for b in bloqueantes)
        assert "descripción de la fuente" in textos
        assert "fecha de consulta" in textos


class TestNumerosAdvertencias:
    def test_mismos_numeros_en_otra_modalidad(self):
        otras = {Modalidad.LA_SEGUNDA: frozenset({1, 2, 3, 4, 5, 6})}
        bloqueantes, advertencias = revisar_numeros(SEIS, otras, FECHA, HOY, FUENTE)
        assert not bloqueantes
        assert "NUMEROS_IGUALES" in _codigos(advertencias)
        assert "Tradicional – La Segunda" in advertencias[0].texto

    def test_fecha_futura(self):
        _, advertencias = revisar_numeros(SEIS, {}, date(2025, 3, 10), HOY, FUENTE)
        assert "FECHA_FUTURA" in _codigos(advertencias)

    def test_sin_observaciones(self):
        otras = {Modalidad.LA_SEGUNDA: frozenset({1, 2, 3, 4, 5, 7})}
        assert revisar_numeros(SEIS, otras, FECHA, HOY, FUENTE) == ([], [])


def _cat(codigo, ganadores=1, individual=Decimal("100"), categoria=Decimal("100"), pozo=None):
    return CategoriaPublicada(codigo, ganadores, categoria, individual, pozo)


class TestPremios:
    def test_sin_observaciones(self):
        cats = [
            _cat("PRIMER", 0, None, Decimal("1000"), Decimal("1000")),
            _cat("SEGUNDO"),
            _cat("TERCER"),
        ]
        assert revisar_premios(Modalidad.PRIMER_SORTEO, cats, None, False, FUENTE) == ([], [])

    def test_no_disponible_no_es_error(self):
        cats = [CategoriaPublicada("UNICO")]
        assert revisar_premios(Modalidad.REVANCHA, cats, None, False, FUENTE) == ([], [])

    def test_ganadores_negativos(self):
        bloqueantes, _ = revisar_premios(
            Modalidad.REVANCHA, [_cat("UNICO", ganadores=-1)], None, False, FUENTE
        )
        assert "GANADORES_NEGATIVO" in _codigos(bloqueantes)

    @pytest.mark.parametrize(
        "campo", ["importe_categoria", "importe_individual", "pozo_vacante_acumulado"]
    )
    def test_importe_negativo(self, campo):
        datos = {
            "importe_categoria": None,
            "importe_individual": None,
            "pozo_vacante_acumulado": None,
            campo: Decimal("-1"),
        }
        cat = CategoriaPublicada("UNICO", 0, **datos)
        bloqueantes, _ = revisar_premios(Modalidad.REVANCHA, [cat], None, False, FUENTE)
        assert "IMPORTE_NEGATIVO" in _codigos(bloqueantes)

    @pytest.mark.parametrize("aciertos", [-1, 7])
    def test_siempre_sale_categoria_fuera_de_rango(self, aciertos):
        bloqueantes, _ = revisar_premios(
            Modalidad.SIEMPRE_SALE, [_cat("GANADORA")], aciertos, False, FUENTE
        )
        assert "CATEGORIA_GANADORA_INVALIDA" in _codigos(bloqueantes)

    @pytest.mark.parametrize("aciertos", [0, 3, 6])
    def test_siempre_sale_categoria_valida(self, aciertos):
        bloqueantes, _ = revisar_premios(
            Modalidad.SIEMPRE_SALE, [_cat("GANADORA")], aciertos, False, FUENTE
        )
        assert bloqueantes == []

    def test_siempre_sale_ganadora_sin_ganadores(self):
        bloqueantes, _ = revisar_premios(
            Modalidad.SIEMPRE_SALE, [_cat("GANADORA", ganadores=0)], 5, False, FUENTE
        )
        assert "CATEGORIA_SIN_GANADORES" in _codigos(bloqueantes)

    @pytest.mark.parametrize("aciertos", [3, 7, 0])
    def test_premio_extra_categoria_invalida(self, aciertos):
        bloqueantes, _ = revisar_premios(
            Modalidad.PREMIO_EXTRA, [_cat("GANADORA")], aciertos, False, FUENTE
        )
        assert "CATEGORIA_GANADORA_INVALIDA" in _codigos(bloqueantes)

    @pytest.mark.parametrize("aciertos", [6, 5, 4])
    def test_premio_extra_categoria_valida(self, aciertos):
        bloqueantes, _ = revisar_premios(
            Modalidad.PREMIO_EXTRA, [_cat("GANADORA")], aciertos, False, FUENTE
        )
        assert bloqueantes == []

    def test_premio_extra_sin_ganadores_valido(self):
        cat = CategoriaPublicada("GANADORA", 0, Decimal("5000"), None, Decimal("5000"))
        assert revisar_premios(Modalidad.PREMIO_EXTRA, [cat], None, True, FUENTE) == ([], [])

    def test_sin_ganadores_con_categoria(self):
        bloqueantes, _ = revisar_premios(
            Modalidad.PREMIO_EXTRA, [_cat("GANADORA")], 6, True, FUENTE
        )
        assert "SIN_GANADORES_CON_CATEGORIA" in _codigos(bloqueantes)

    def test_falta_fuente(self):
        bloqueantes, _ = revisar_premios(Modalidad.REVANCHA, [_cat("UNICO")], None, False, None)
        assert "SIN_FUENTE" in _codigos(bloqueantes)

    def test_advertencia_ganadores_sin_importe_individual(self):
        _, advertencias = revisar_premios(
            Modalidad.REVANCHA, [_cat("UNICO", ganadores=2, individual=None)], None, False, FUENTE
        )
        assert "SIN_IMPORTE_INDIVIDUAL" in _codigos(advertencias)
        assert "Premio Revancha" in advertencias[0].texto
