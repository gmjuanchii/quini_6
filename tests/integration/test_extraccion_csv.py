"""[002] Historia 5: descarga del CSV unificado (T055)."""

import csv
import io
from datetime import date

import pytest
from django.test import Client

from dominio.extraccion.tipos import Fuente
from extracciones.models import Extraccion
from tests.extraccion_falsos import (
    HOY,
    cliente_con_sorteos,
    fichas_de,
    pagina,
    procesar_pendientes,
    url_sorteo,
)
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
F2, F3 = Fuente.F2, Fuente.F3
SORTEOS = {
    3421: date(2026, 10, 28),
    3422: date(2026, 11, 1),
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
}


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


@pytest.fixture
def terminada(cliente_admin):
    cliente = cliente_con_sorteos(SORTEOS, fuentes=(F2, F3))
    cliente.responder(url_sorteo(F2, 3423), 500, "Error.")
    cliente.responder(url_sorteo(F3, 3423), 404, "")
    # Un texto de la fuente que empieza con "=" (AC-5.9) en un rótulo desconocido.
    texto = pagina(F3, 3424, SORTEOS[3424]).replace(">Revancha</h2>", ">=HYPERLINK(1)</h2>")
    cliente.responder(url_sorteo(F3, 3424), 200, texto)
    cliente_admin.post(INICIO, {"inicio": "01/11/2026", "fin": "11/11/2026"})
    procesar_pendientes(cliente, fichas_de(F2, F3))
    return Extraccion.objects.get()


def descargar(cliente, extraccion):
    return cliente.get(f"{INICIO}{extraccion.pk}/csv/")


def test_ac_5_1_encabezados_de_la_descarga(cliente_admin, terminada):
    respuesta = descargar(cliente_admin, terminada)
    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "text/csv; charset=utf-8"
    assert respuesta["Content-Disposition"] == (
        f'attachment; filename="quini6-extraccion-{terminada.pk}-2026-11-01-a-2026-11-11.csv"'
    )
    assert respuesta["Cache-Control"] == "no-store"
    assert not respuesta.content.startswith(b"\xef\xbb\xbf")  # sin BOM


def test_ac_5_10_y_1_15_descargas_identicas(cliente_admin, terminada):
    otro = Client()
    otro.force_login(crear_usuario("admin2@prueba.local", admin=True))
    primera = descargar(cliente_admin, terminada).content
    assert descargar(cliente_admin, terminada).content == primera
    assert descargar(otro, terminada).content == primera
    assert primera.decode("utf-8") == terminada.archivo_csv


def test_ac_5_3_mismo_estado_que_en_la_pantalla(cliente_admin, terminada):
    filas = list(csv.DictReader(io.StringIO(descargar(cliente_admin, terminada).content.decode())))
    por_sorteo = {f["sorteo_numero"]: f["sorteo_estado"] for f in filas}
    pantalla = {str(s.numero): s.estado_enum.texto for s in terminada.sorteos.all()}
    assert por_sorteo == pantalla
    conteo = {}
    for estado in por_sorteo.values():
        conteo[estado] = conteo.get(estado, 0) + 1
    resumen = cliente_admin.get(f"{INICIO}{terminada.pk}/").content.decode()
    assert (
        f'<th scope="row">No recuperados</th><td>{conteo.get("No recuperado", 0)}</td>' in resumen
    )
    assert por_sorteo["3423"] == "No recuperado"


def test_ac_5_4_procedencia_de_cada_dato(cliente_admin, terminada):
    filas = list(csv.DictReader(io.StringIO(descargar(cliente_admin, terminada).content.decode())))
    fila = next(f for f in filas if f["sorteo_numero"] == "3422")
    assert (
        "ganadores: numerosganadores.com.ar https://numerosganadores.com.ar/sorteos/3422 "
        "2026-11-19 10:15:02; quiniya.com.ar https://quiniya.com.ar/sorteos/3422 "
        "2026-11-19 10:15:02"
    ) in fila["procedencia"]


def test_ac_5_9_texto_de_la_fuente_que_empieza_con_igual(cliente_admin, terminada):
    texto = descargar(cliente_admin, terminada).content.decode()
    assert "Rótulo no reconocido: «=HYPERLINK(1)»" in texto
    for fila in csv.reader(io.StringIO(texto)):
        assert not any(celda.startswith(("=", "+", "@")) for celda in fila)


def test_en_curso_o_sin_sorteos_responde_404_y_no_ofrece_el_boton(cliente_admin):
    cliente_admin.post(INICIO, {"inicio": "05/11/2026", "fin": "07/11/2026"})
    en_curso = Extraccion.objects.get()
    assert descargar(cliente_admin, en_curso).status_code == 404
    procesar_pendientes(cliente_con_sorteos(SORTEOS), fichas_de(F2))
    en_curso.refresh_from_db()
    assert en_curso.estado == "SIN_SORTEOS"
    assert descargar(cliente_admin, en_curso).status_code == 404
    assert "Descargar CSV" not in cliente_admin.get(f"{INICIO}{en_curso.pk}/").content.decode()
