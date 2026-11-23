"""[003] T194: Resultados en la API v1 (contracts/api.md § "Pantalla 4 — Resultados").

Las cuatro operaciones con los casos de tests/integration/test_us1_consulta.py y
test_no_publicado.py: nada en borrador u observado se expone (Const. VIII), ``no-cache`` y los
mismos datos que la vista HTML (NFR-009).
"""

import json
from datetime import date

import pytest

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Modalidad
from tests.fabricas import cargar_numeros, cargar_premios, crear_concurso

pytestmark = pytest.mark.django_db

PS, LS, RV, SS = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
)
OCULTOS_LS = frozenset({17, 29, 33, 36, 38, 43})  # Borrador
OCULTOS_RV = frozenset({16, 27, 34, 37, 39, 44})  # Observado
API = "/api/v1/sorteos/"


@pytest.fixture
def sorteo(db):
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
    return c


def _sin_ocultos(respuesta):
    texto = json.dumps(respuesta.json())
    for oculto in ("987654.32", "876543.21", "4321", "1234", "BORRADOR", "OBSERVADO"):
        assert oculto not in texto


def test_detalle_solo_lo_publicado(visitante, sorteo):
    respuesta = visitante.get(f"{API}5000/")
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-cache"
    _sin_ocultos(respuesta)
    datos = respuesta.json()
    modalidades = {m["slug"]: m for m in datos["modalidades"]}
    assert modalidades["primer-sorteo"]["numeros"] == [1, 2, 3, 4, 5, 6]
    assert modalidades["primer-sorteo"]["estado_numeros"]["codigo"] == "PUBLICADO"
    assert modalidades["la-segunda"]["numeros"] is None
    assert modalidades["la-segunda"]["estado_numeros"] == {
        "codigo": "PENDIENTE_VALIDACION",
        "texto": "Pendiente de validación",
    }
    assert modalidades["revancha"]["numeros"] is None
    assert modalidades["primer-sorteo"]["categorias"] == []
    assert datos["completitud"]["texto"] in ("Incompleto", "Completo", "Resultados pendientes")


@pytest.mark.parametrize("ruta", [API, f"{API}ultimo/", f"{API}buscar/?fecha=02/03/2025"])
def test_ninguna_operacion_expone_lo_no_publicado(visitante, sorteo, ruta):
    respuesta = visitante.get(ruta)
    assert respuesta.status_code == 200
    _sin_ocultos(respuesta)


def test_ultimo_y_pendiente(visitante, sorteo):
    crear_concurso(5001, date(2025, 3, 5))
    datos = visitante.get(f"{API}ultimo/").json()
    assert datos["ultimo"]["numero"] == 5000
    assert datos["pendiente"]["numero"] == 5001


def test_ultimo_sin_publicados(visitante, db):
    assert visitante.get(f"{API}ultimo/").json() == {"ultimo": None, "pendiente": None}


def test_listado_en_una_sola_pagina(visitante, sorteo):
    crear_concurso(5001, date(2025, 3, 5))
    datos = visitante.get(API).json()
    assert [s["numero"] for s in datos["elementos"]] == [5001, 5000]
    assert (datos["pagina"], datos["paginas"], datos["total"]) == (1, 1, 2)
    assert datos["elementos"][0]["fecha"] == "2025-03-05"


def test_buscar_por_numero_y_fecha(visitante, sorteo):
    assert visitante.get(f"{API}buscar/?numero=5000").json()["redirigir"] == "/resultados/5000/"
    inexistente = visitante.get(f"{API}buscar/?numero=7").json()
    assert inexistente["mensaje"] == mensaje("resultados.concurso_inexistente", N=7)
    por_fecha = visitante.get(f"{API}buscar/?fecha=2025-03-02").json()
    assert [s["numero"] for s in por_fecha["elementos"]] == [5000]
    sin = visitante.get(f"{API}buscar/?fecha=01/01/2020").json()
    assert sin["mensaje"] == mensaje("resultados.fecha_sin_concursos", fecha="01/01/2020")


def test_buscar_422_por_campo(visitante, db):
    numero = visitante.get(f"{API}buscar/?numero=abc")
    assert numero.status_code == 422
    assert numero.json()["errores"][0]["mensaje"] == MENSAJES["admin.numero_sorteo_invalido"]
    fecha = visitante.get(f"{API}buscar/?fecha=31/02/2025")
    assert fecha.status_code == 422
    assert fecha.json()["errores"][0]["mensaje"] == mensaje("fecha.inexistente", fecha="31/02/2025")


def test_detalle_inexistente_404(visitante, db):
    assert visitante.get(f"{API}999/").status_code == 404


def test_paridad_con_la_vista_html(visitante, client, sorteo):
    """NFR-009: los mismos estados y textos que muestra la página HTML."""
    datos = visitante.get(f"{API}5000/").json()
    html = client.get("/resultados/5000/").content.decode()
    assert datos["completitud"]["texto"] in html
    for m in datos["modalidades"]:
        assert m["nombre"] in html
        if m["numeros"] is None:  # lo publicado se ve como bolillas; lo demás, por su estado
            assert m["estado_numeros"]["texto"] in html
