"""[002] Historia 4: discrepancias y procedencia en la pantalla y en el archivo (T077)."""

import csv
import io
from datetime import date

import pytest

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

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
F2, F3 = Fuente.F2, Fuente.F3
# Como en el listado real de F2, también figuran sorteos anteriores al período.
SORTEOS = {
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
    3426: date(2026, 11, 15),
    3427: date(2026, 11, 18),
}


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


@pytest.fixture
def extraccion(cliente_admin):
    cliente = cliente_con_sorteos(SORTEOS, fuentes=(F2, F3), base=3427)
    # 3427 real: F2 publica 5.015 para La Segunda, 4 aciertos; F3 5.547,85 (AC-4.1).
    f3 = pagina(F3, 3427, SORTEOS[3427], base=3427).replace("<td>5.015</td>", "<td>5.547,85</td>")
    # Tradicional 4 aciertos: 12.060 en F2 y 12.060,13 en F3 (AC-4.5).
    f3 = f3.replace("<td>12.060</td>", "<td>12.060,13</td>")
    # Tradicional 6 aciertos vacante en F2; F3 presenta la tabla sin esa fila (AC-4.2).
    fila = (
        '<th scope="row">6</th>\n                        <td>Pozo Vacante</td>\n'
        "                        <td>1.100.000.000</td>"
    )
    assert fila in f3
    f3 = f3.replace(fila, "", 1)
    cliente.responder(url_sorteo(F3, 3427), 200, f3)
    # 3426: fechas distintas entre fuentes (AC-4.4).
    cliente.responder(
        url_sorteo(F3, 3426),
        200,
        pagina(F3, 3426, date(2026, 11, 16), base=3427).replace("3427", "3426"),
    )
    cliente_admin.post(INICIO, {"inicio": "15/11/2026", "fin": "18/11/2026"})
    procesar_pendientes(cliente, fichas_de(F2, F3))
    return Extraccion.objects.get()


def test_detalle_con_inconsistencias(cliente_admin, extraccion):
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3427/").content.decode()
    assert "Con inconsistencias" in texto
    assert "Sin determinar" in texto
    assert "Valor distinto" in texto
    assert "$ 5.015,00 (numerosganadores.com.ar)" in texto
    assert "$ 5.547,85 (quiniya.com.ar)" in texto
    # RN-30: 12.060 y 12.060,13 redondeados coinciden: ni discrepancia ni nota.
    assert "Diferencia de centavos o redondeo" not in texto
    assert "Omisión" in texto


def test_ac_4_4_dos_fechas_con_su_fuente(cliente_admin, extraccion):
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3426/").content.decode()
    assert "Con inconsistencias" in texto
    assert "15/11/2026 (numerosganadores.com.ar)" in texto
    assert "16/11/2026 (quiniya.com.ar)" in texto


def test_csv_con_discrepancias_y_datos_sin_corroborar(cliente_admin, extraccion):
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/csv/").content.decode()
    filas = list(csv.DictReader(io.StringIO(texto)))
    tercer = next(
        f
        for f in filas
        if f["sorteo_numero"] == "3427"
        and f["modalidad"] == "La Segunda"
        and f["categoria"] == "Tercer Premio"
    )
    assert tercer["discrepancias"] == (
        "importe_individual: Valor distinto — 5015.00 (numerosganadores.com.ar); "
        "5547.85 (quiniya.com.ar)"
    )
    primer = next(
        f
        for f in filas
        if f["sorteo_numero"] == "3427"
        and f["modalidad"] == "Tradicional"
        and f["categoria"] == "Primer Premio"
    )
    assert (
        "ganadores: Omisión — 0 (numerosganadores.com.ar); sin dato (quiniya.com.ar)"
        in (primer["discrepancias"])
    )
    # RN-07 (D-14): ante la omisión valen los ganadores de F2 y la categoría queda vacante.
    assert primer["ganadores"] == "0" and primer["estado_pozo"] == "Vacante"
    assert primer["importe_individual"] == "0.00"
    assert primer["sorteo_estado"] == "Con inconsistencias"


def test_ac_4_7_combina_fuentes_en_pantalla(cliente_admin):
    """Números de F2 y premios de F3, sin diferencias: "Combina fuentes" y "Recuperado"."""
    cliente = cliente_con_sorteos(SORTEOS, fuentes=(F2, F3))
    solo_numeros = pagina(F2, 3426, SORTEOS[3426])
    while "<table" in solo_numeros:
        i = solo_numeros.index("<table")
        j = solo_numeros.index("</table>", i) + len("</table>")
        solo_numeros = solo_numeros[:i] + solo_numeros[j:]
    solo_premios = pagina(F3, 3426, SORTEOS[3426])
    solo_premios = solo_premios.replace('class="bolilla"', 'class="otra"')
    cliente.responder(url_sorteo(F2, 3426), 200, solo_numeros)
    cliente.responder(url_sorteo(F3, 3426), 200, solo_premios)
    cliente_admin.post(INICIO, {"inicio": "15/11/2026", "fin": "15/11/2026"})
    procesar_pendientes(cliente, fichas_de(F2, F3))
    extraccion = Extraccion.objects.get()
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3426/").content.decode()
    assert "Combina fuentes" in texto and "Sin corroborar" in texto
    sorteo = extraccion.sorteos.get(numero=3426)
    assert sorteo.combina_fuentes and sorteo.estado == "RECUPERADO"
