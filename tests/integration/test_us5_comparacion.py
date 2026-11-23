"""US5 — Comparar mis jugadas con los resultados oficiales (pantallas; AC-5.33, SC-003)."""

from datetime import date
from decimal import Decimal

import pytest

from dominio.mensajes import MENSAJES
from dominio.tipos import Modalidad
from jugadas.models import Jugada
from tests.fabricas import (
    EJEMPLOS_REFERENCIA,
    cargar_numeros,
    cargar_premios,
    crear_concurso,
    crear_concurso_ejemplo,
    marcar_en_revision,
)

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)
PENDIENTE_IMPORTE = "Información de premios pendiente de publicación"


def _jugada(usuario, concurso, numeros, costo="100"):
    j = Jugada(usuario=usuario, concurso=concurso, costo=Decimal(costo))
    j.asignar_numeros(numeros)
    j.save()
    return j


def _detalle(cliente, jugada):
    r = cliente.get(f"/mis-jugadas/{jugada.id}/")
    assert r.status_code == 200
    return r.content.decode()


def _seccion(contenido, modalidad):
    inicio = contenido.index(f'id="comparacion-{modalidad.slug}"')
    fin = contenido.find('id="comparacion-', inicio + 10)
    return contenido[inicio : fin if fin != -1 else None]


@pytest.fixture
def ejemplo(usuario_a):
    def crear(n, numero=None):
        concurso = crear_concurso_ejemplo(n, numero or 9000 + n)
        return _jugada(usuario_a, concurso, EJEMPLOS_REFERENCIA[n]["jugada"])

    return crear


class TestEjemplosDeReferencia:
    def test_ejemplo_1(self, cliente_a, ejemplo):
        contenido = _detalle(cliente_a, ejemplo(1))
        assert "Con premio — Primer Premio" in _seccion(contenido, PS)
        assert "Con premio — Segundo Premio" in _seccion(contenido, LS)
        assert "4 aciertos — Sin premio" in _seccion(contenido, RV)
        assert "Premio pendiente de determinación" in _seccion(contenido, SS)
        pe = _seccion(contenido, PE)
        assert "Excluida del Premio Extra: obtuvo 6 aciertos en Tradicional – Primer Sorteo" in pe
        assert "Con premio" not in pe
        assert PENDIENTE_IMPORTE in _seccion(contenido, PS)  # AC-5.7 / AC-5.3

    def test_ejemplo_2(self, cliente_a, ejemplo):
        contenido = _detalle(cliente_a, ejemplo(2))
        assert "Con premio — Tercer Premio" in _seccion(contenido, PS)
        assert "3 aciertos — Sin premio" in _seccion(contenido, LS)
        assert "Con premio — Premio Revancha" in _seccion(contenido, RV)
        assert "Excluida del Premio Extra: obtuvo 6 aciertos en Revancha" in _seccion(contenido, PE)

    def test_ejemplo_3(self, cliente_a, ejemplo):
        contenido = _detalle(cliente_a, ejemplo(3))
        assert "3 aciertos — Sin premio" in _seccion(contenido, PS)
        assert "Con premio — Tercer Premio" in _seccion(contenido, LS)
        assert "4 aciertos — Sin premio" in _seccion(contenido, RV)
        pe = _seccion(contenido, PE)
        assert "Participa" in pe
        assert "Con premio — Premio Extra (6 aciertos)" in pe
        assert "13 números distintos" in pe

    def test_siempre_sale_con_categoria_menor_muestra_aviso(self, cliente_a, ejemplo):
        jugada = ejemplo(2)
        cargar_premios(
            jugada.concurso, SS, {"GANADORA": {"ganadores": 3}}, aciertos_categoria_ganadora=4
        )
        ss = _seccion(_detalle(cliente_a, jugada), SS)
        assert "Premio pendiente de determinación" in ss
        assert MENSAJES["comp.aciertos_superan"] in ss


class TestDetalle:
    def test_numeros_acertados_resaltados(self, cliente_a, ejemplo):
        contenido = _detalle(cliente_a, ejemplo(2))
        ls = _seccion(contenido, LS)
        assert ls.count("bolilla--acertada") == 3
        assert ls.count("(acertado)") == 3

    def test_importe_oficial(self, cliente_a, ejemplo):
        jugada = ejemplo(1)
        cargar_premios(
            jugada.concurso, PS, {"PRIMER": {"ganadores": 1, "importe_individual": "1234567.89"}}
        )
        ps = _seccion(_detalle(cliente_a, jugada), PS)
        assert "$ 1.234.567,89" in ps
        assert PENDIENTE_IMPORTE not in ps

    def test_en_revision(self, cliente_a, ejemplo):
        jugada = ejemplo(1)
        marcar_en_revision(jugada.concurso, LS, "numeros", "Revisar")
        assert "Información en revisión: el resultado podría cambiar" in _seccion(
            _detalle(cliente_a, jugada), LS
        )

    def test_borrador_nunca_aporta_aciertos(self, cliente_a, usuario_a):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS, LS])
        cargar_numeros(c, PS, frozenset({3, 8, 14, 21, 32, 40}), estado="BORRADOR")
        cargar_numeros(c, LS, frozenset({3, 8, 14, 21, 32, 41}), estado="OBSERVADO")
        jugada = _jugada(usuario_a, c, {3, 8, 14, 21, 32, 40})
        contenido = _detalle(cliente_a, jugada)
        for modalidad in (PS, LS):
            seccion = _seccion(contenido, modalidad)
            assert "Pendiente de validación" in seccion
            assert "aciertos" not in seccion
            assert "bolilla--acertada" not in seccion

    def test_sin_cargar(self, cliente_a, usuario_a):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        contenido = _detalle(cliente_a, _jugada(usuario_a, c, {1, 2, 3, 4, 5, 6}))
        assert "Resultado pendiente" in _seccion(contenido, PS)


class TestHistorial:
    def test_estado_resumido(self, cliente_a, usuario_a, ejemplo):
        ejemplo(3, numero=9003)
        pendiente = crear_concurso(9100, date(2025, 4, 1))
        _jugada(usuario_a, pendiente, {1, 2, 3, 4, 5, 6})
        sin_premio = crear_concurso(9101, date(2025, 2, 1), modalidades=[PS])
        cargar_numeros(sin_premio, PS, frozenset({40, 41, 42, 43, 44, 45}))
        _jugada(usuario_a, sin_premio, {1, 2, 3, 4, 5, 6})
        contenido = cliente_a.get("/mis-jugadas/").content.decode()
        assert "Con premio — información de premios pendiente de publicación" in contenido
        assert "Resultado pendiente" in contenido
        assert "Sin premio" in contenido

    def test_con_premio(self, cliente_a, usuario_a):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[RV])
        cargar_numeros(c, RV, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_premios(c, RV, {"UNICO": {"ganadores": 1, "importe_individual": "1000"}})
        _jugada(usuario_a, c, {1, 2, 3, 4, 5, 6})
        contenido = cliente_a.get("/mis-jugadas/").content.decode()
        assert ">Con premio<" in contenido
