"""[003] T188: Mis jugadas en la API v1 (contracts/api.md § "Pantalla 3 — Mis jugadas").

Las seis operaciones; jugada ajena o inexistente → el mismo 404 (Const. IV); 409 de duplicada con
``confirmar`` y de jugada fija; ``Idempotency-Key``; 401 con ``pendiente``; paridad con
tests/integration/test_us4_jugadas.py y test_us5_comparacion.py (NFR-009).
"""

import json
import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.test import Client

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Modalidad
from jugadas.models import Jugada
from quini6.formulario_pendiente import ruta_de
from tests.api.conftest import token_csrf
from tests.fabricas import (
    EJEMPLOS_REFERENCIA,
    cargar_numeros,
    crear_concurso,
    crear_concurso_ejemplo,
    crear_usuario,
)

pytestmark = pytest.mark.django_db

API = "/api/v1/jugadas/"
SEIS = ["03", "08", "14", "21", "32", "40"]


def _cliente(correo):
    cliente = Client(enforce_csrf_checks=True)
    usuario = crear_usuario(correo)
    cliente.force_login(usuario)
    cliente.usuario = usuario
    return cliente


@pytest.fixture
def ana(db):
    return _cliente("ana@jugadas.local")


@pytest.fixture
def beto(db):
    return _cliente("beto@jugadas.local")


@pytest.fixture
def sorteo(db):
    return crear_concurso(9001, date(2025, 3, 2))


def _enviar(cliente, metodo, ruta, datos=None, clave=None):
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)}
    if clave:
        extra["HTTP_IDEMPOTENCY_KEY"] = clave
    cuerpo = "" if datos is None else json.dumps(datos)
    return cliente.generic(metodo, ruta, data=cuerpo, content_type="application/json", **extra)


def _datos(**extra):
    return {"sorteo": "9001", "numeros": SEIS, "costo": "1500,50", **extra}


def _jugada(usuario, concurso, numeros=(3, 8, 14, 21, 32, 40)):
    j = Jugada(usuario=usuario, concurso=concurso, costo=Decimal("100"))
    j.asignar_numeros(numeros)
    j.save()
    return j


def test_registrar_201_con_aviso_e_idempotencia(ana, sorteo):
    clave = str(uuid.uuid4())
    respuesta = _enviar(ana, "POST", API, _datos(), clave)
    assert respuesta.status_code == 201
    jugada = respuesta.json()
    assert jugada["sorteo"] == {"numero": 9001, "fecha": "2025-03-02"}
    assert jugada["numeros"] == [3, 8, 14, 21, 32, 40]
    assert jugada["costo"] == "1500.50"
    assert jugada["modificable"] is True
    assert "Revancha" in jugada["modalidades"]
    otra = _enviar(ana, "POST", API, _datos(), clave)
    assert otra.status_code == 201 and otra.json()["id"] == jugada["id"]
    assert Jugada.objects.count() == 1
    assert ana.get("/api/v1/avisos/").json() == [
        {"tipo": "exito", "texto": MENSAJES["jugada.registrada"]}
    ]


@pytest.mark.parametrize(
    ("datos", "campo", "texto"),
    [
        ({"sorteo": ""}, "sorteo", MENSAJES["jugada.elegi_concurso"]),
        ({"numeros": SEIS[:4]}, "numeros", mensaje("jugada.faltan", n=2)),
        ({"numeros": [*SEIS[:5], "46"]}, "numeros", MENSAJES["jugada.fuera_de_rango"]),
        ({"costo": ""}, "costo", MENSAJES["jugada.costo_vacio"]),
    ],
)
def test_registrar_422_con_los_textos_del_formulario(ana, sorteo, datos, campo, texto):
    respuesta = _enviar(ana, "POST", API, _datos(**datos))
    assert respuesta.status_code == 422
    assert (campo, texto) in {(e["campo"], e["mensaje"]) for e in respuesta.json()["errores"]}
    assert not Jugada.objects.exists()


def test_duplicada_409_con_confirmar_y_luego_se_guarda(ana, sorteo):
    _jugada(ana.usuario, sorteo)
    respuesta = _enviar(ana, "POST", API, _datos())
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == MENSAJES["jugada.duplicada"]
    assert respuesta.json()["confirmar"] is True
    assert _enviar(ana, "POST", API, _datos(confirmar_duplicado=True)).status_code == 201
    assert Jugada.objects.count() == 2


def test_listado_solo_las_propias(ana, beto, sorteo):
    propia = _jugada(ana.usuario, sorteo)
    _jugada(beto.usuario, sorteo, (1, 2, 3, 4, 5, 6))
    datos = ana.get(API).json()
    assert [j["id"] for j in datos] == [propia.pk]
    assert datos[0]["estado"]["texto"] == "Resultado pendiente"
    assert ana.get(API)["Cache-Control"] == "no-store"


def test_ajena_o_inexistente_404_identico(ana, beto, sorteo):
    ajena = _jugada(beto.usuario, sorteo)
    a = ana.get(f"{API}{ajena.pk}/")
    b = ana.get(f"{API}999999/")
    assert a.status_code == b.status_code == 404
    assert a.json() == b.json()
    assert a.json()["detail"] == MENSAJES["jugada.no_existe"]
    assert _enviar(ana, "DELETE", f"{API}{ajena.pk}/").status_code == 404
    assert _enviar(ana, "PUT", f"{API}{ajena.pk}/", _datos()).status_code == 404
    assert Jugada.objects.filter(pk=ajena.pk).exists()


def test_modificar_y_eliminar(ana, sorteo):
    jugada = _jugada(ana.usuario, sorteo)
    respuesta = _enviar(
        ana, "PUT", f"{API}{jugada.pk}/", _datos(numeros=["01", "02", "03", "04", "05", "06"])
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["numeros"] == [1, 2, 3, 4, 5, 6]
    clave = str(uuid.uuid4())
    assert _enviar(ana, "DELETE", f"{API}{jugada.pk}/", clave=clave).status_code == 204
    assert _enviar(ana, "DELETE", f"{API}{jugada.pk}/", clave=clave).status_code == 204
    assert not Jugada.objects.exists()


def test_jugada_fija_409(ana):
    concurso = crear_concurso(9100, date(2025, 3, 2))
    cargar_numeros(concurso, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
    jugada = _jugada(ana.usuario, concurso)
    assert ana.get(f"{API}{jugada.pk}/").json()["modificable"] is False
    for metodo, datos in (("PUT", _datos(sorteo="9100")), ("DELETE", None)):
        respuesta = _enviar(ana, metodo, f"{API}{jugada.pk}/", datos)
        assert respuesta.status_code == 409
        assert respuesta.json()["detail"] == MENSAJES["jugada.fija"]


def test_sorteos_disponibles(ana, sorteo):
    cerrado = crear_concurso(9100, date(2025, 3, 5))
    cargar_numeros(cerrado, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
    disponibles = ana.get(f"{API}sorteos-disponibles/").json()
    assert [s["numero"] for s in disponibles] == [9001]
    assert disponibles[0]["modalidades"][0]["nombre"] == "Tradicional – Primer Sorteo"


def test_401_con_pendiente_al_registrar_y_modificar(visitante):
    respuesta = _enviar(visitante, "POST", API, _datos())
    assert respuesta.status_code == 401
    assert ruta_de(respuesta.json()["pendiente"]) == "/mis-jugadas/nueva/"
    respuesta = _enviar(visitante, "PUT", f"{API}7/", _datos())
    assert ruta_de(respuesta.json()["pendiente"]) == "/mis-jugadas/7/editar/"


def test_sin_csrf_403(ana, sorteo):
    respuesta = ana.post(API, data=_datos(), content_type="application/json")
    assert respuesta.status_code == 403


def test_comparacion_del_ejemplo_1_igual_que_la_vista(ana):
    """NFR-009: los mismos resultados que tests/integration/test_us5_comparacion.py."""
    concurso = crear_concurso_ejemplo(1, 9001)
    jugada = _jugada(ana.usuario, concurso, EJEMPLOS_REFERENCIA[1]["jugada"])
    datos = ana.get(f"{API}{jugada.pk}/").json()
    por_modalidad = {c["modalidad"]["slug"]: c for c in datos["comparacion"]}
    assert (
        por_modalidad["primer-sorteo"]["resultado_premio"]["texto"] == "Con premio — Primer Premio"
    )
    assert por_modalidad["la-segunda"]["resultado_premio"]["texto"] == "Con premio — Segundo Premio"
    assert por_modalidad["revancha"]["resultado_premio"]["texto"] == "4 aciertos — Sin premio"
    assert por_modalidad["siempre-sale"]["resultado_premio"]["texto"] == (
        "Premio pendiente de determinación"
    )
    extra = por_modalidad["premio-extra"]
    assert extra["elegibilidad"] == "excluida"
    assert extra["excluida_por"] == "Tradicional – Primer Sorteo"
    assert por_modalidad["primer-sorteo"]["importe_pendiente"] is True
    vista = Client()
    vista.force_login(ana.usuario)
    html = vista.get(f"/mis-jugadas/{jugada.pk}/").content.decode()
    assert datos["resumen"]["texto"] in html
