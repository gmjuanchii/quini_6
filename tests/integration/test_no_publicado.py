"""SC-003: la información en Borrador u Observado nunca llega al público, a una comparación ni
a una estadística."""

import re
from datetime import date
from decimal import Decimal

import pytest

from dominio.tipos import Modalidad
from jugadas.models import Jugada
from tests.fabricas import cargar_numeros, cargar_premios, crear_concurso

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)
OCULTOS_LS = frozenset({17, 29, 33, 36, 38, 43})  # Borrador
OCULTOS_RV = frozenset({16, 27, 34, 37, 39, 44})  # Observado
IMPORTES_OCULTOS = ("987.654,32", "876.543,21", "4321 ganadores", "1234 ganadores")


@pytest.fixture
def datos(usuario_a):
    c = crear_concurso(5000, date(2025, 3, 2))
    cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
    cargar_numeros(c, LS, OCULTOS_LS, estado="BORRADOR")
    cargar_numeros(c, RV, OCULTOS_RV, estado="OBSERVADO")
    cargar_premios(
        c, PS, {"PRIMER": {"ganadores": 4321, "importe_individual": "987654.32"}}, estado="BORRADOR"
    )
    cargar_premios(
        c,
        SS,
        {"GANADORA": {"ganadores": 1234, "importe_individual": "876543.21"}},
        aciertos_categoria_ganadora=5,
        estado="OBSERVADO",
    )
    jugada = Jugada(usuario=usuario_a, concurso=c, costo=Decimal("1"))
    jugada.asignar_numeros(OCULTOS_LS)
    jugada.save()
    return c, jugada


def _sin_ocultos(contenido, permitir_jugada=False):
    for texto in IMPORTES_OCULTOS:
        assert texto not in contenido
    if not permitir_jugada:
        for n in OCULTOS_LS | OCULTOS_RV:
            assert f">{n:02d}<" not in contenido


@pytest.mark.parametrize(
    "url", ["/resultados/", "/resultados/5000/", "/resultados/buscar/?fecha=02/03/2025"]
)
def test_paginas_publicas(client, datos, url):
    r = client.get(url)
    assert r.status_code == 200
    _sin_ocultos(r.content.decode())


def test_detalle_de_jugada(cliente_a, datos):
    _, jugada = datos
    contenido = cliente_a.get(f"/mis-jugadas/{jugada.id}/").content.decode()
    _sin_ocultos(contenido, permitir_jugada=True)
    for modalidad in (LS, RV):
        inicio = contenido.index(f'id="comparacion-{modalidad.slug}"')
        seccion = contenido[inicio : contenido.find('id="comparacion-', inicio + 5)]
        assert "Pendiente de validación" in seccion
        assert "bolilla--acertada" not in seccion
        assert "Números oficiales" not in seccion
    pe = contenido[contenido.index('id="comparacion-premio-extra"') :]
    assert "Conjunto de números" not in pe


def test_historial(cliente_a, datos):
    contenido = cliente_a.get("/mis-jugadas/").content.decode()
    _sin_ocultos(contenido, permitir_jugada=True)


@pytest.mark.parametrize("modalidad", ["LA_SEGUNDA", "REVANCHA"])
def test_estadisticas(client, datos, modalidad):
    contenido = client.get("/estadisticas/", {"modalidad": modalidad}).content.decode()
    assert "No hay sorteos publicados de" in contenido
    assert not re.search(r'id="frecuencia-', contenido)


def test_estadisticas_primer_sorteo(client, datos):
    contenido = client.get("/estadisticas/").content.decode()
    fila = re.search(r'<tr id="frecuencia-17">(.*?)</tr>', contenido, re.S).group(1)
    assert ">0<" in fila
