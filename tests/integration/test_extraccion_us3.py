"""[002] Historia 3: normalizar y validar números y premios, verificado en la pantalla (T049).

Usa la variante editada ``tests/fixtures/fuentes/f2/variantes/sorteo-3426-normalizacion.html``:
importe "494,443,71" en La Segunda, ganadores sin informar en el Tercer Premio de Tradicional y
sin la tarjeta de Revancha.
"""

from datetime import date

import pytest

from dominio.extraccion.tipos import Fuente
from extracciones.models import Extraccion
from tests.extraccion_falsos import (
    HOY,
    cliente_con_sorteos,
    fichas_de,
    leer,
    pagina,
    procesar_pendientes,
    url_sorteo,
)

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
F2 = Fuente.F2
SORTEOS = {3424: date(2026, 11, 8), 3425: date(2026, 11, 11), 3426: date(2026, 11, 15)}


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


def extraer(cliente_admin, cliente, inicio="11/11/2026", fin="15/11/2026"):
    cliente_admin.post(INICIO, {"inicio": inicio, "fin": fin})
    procesar_pendientes(cliente, fichas_de(F2))
    return Extraccion.objects.get()


def test_detalle_normalizado_con_vacante_ganadores_e_importes(cliente_admin):
    extraccion = extraer(cliente_admin, cliente_con_sorteos(SORTEOS))
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3426/").content.decode()
    for esperado in (
        "<h2>Tradicional</h2>",  # AC-3.1 (D-15)
        "<h2>Pozo Extra</h2>",
        "01, 02, 10, 13, 38, 39",  # AC-3.2
        "$ 1.100.000.000,00",  # AC-3.4
        "$ 0,00",  # AC-3.4: importe individual de la vacante (D-16)
        "Vacante",
        "$ 3.013.912,00",  # AC-3.5
        "$ 54.250.416,00",  # AC-3.5: 18 × 3.013.912 (D-16)
        "Con ganadores",
        # AC-3.17: unión de Tradicional, La Segunda y Revancha (D-19)
        "Calculado: unión de Tradicional, La Segunda y Revancha",
    ):
        assert esperado in texto, esperado
    # D-23: la marca "Calculado" de pozo e importe individual ya no se ve en la pantalla (queda en
    # la procedencia del CSV); D-22: sin acumulación ni importe trasladado.
    for ausente in (
        "Calculado: sin ganadores",
        "Calculado: importe individual × ganadores",
        "Se acumula según la fuente",
        "Importe trasladado",
    ):
        assert ausente not in texto, ausente
    assert "Tradicional – Primer Sorteo" not in texto


def test_variante_con_importe_invalido_ganadores_ausentes_y_modalidad_no_informada(
    cliente_admin,
):
    cliente = cliente_con_sorteos(SORTEOS)
    cliente.responder(
        url_sorteo(F2, 3426), 200, leer("f2/variantes/sorteo-3426-normalizacion.html")
    )
    extraccion = extraer(cliente_admin, cliente)
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3426/").content.decode()
    assert "Importe con formato no reconocido: «494,443,71»" in texto  # AC-3.8
    assert "Pendiente" in texto  # AC-3.7
    assert "No informada por las fuentes" in texto  # AC-3.12
    assert "Incompleto" in texto
    fila = extraccion.sorteos.get(numero=3426)
    assert fila.estado != "RECUPERADO"
    resumen = cliente_admin.get(f"{INICIO}{extraccion.pk}/").content.decode()
    assert "Recuperado parcialmente" in resumen


def test_ac_3_11_reglas_del_periodo_no_verificadas(cliente_admin):
    sorteos = {2300: date(2015, 10, 25), 2301: date(2015, 10, 28)}
    cliente = cliente_con_sorteos({})
    for numero, fecha in sorteos.items():
        cliente.responder(url_sorteo(F2, numero), 200, pagina(F2, numero, fecha, base=2211))
    cliente.responder(url_sorteo(F2, 2302), 200, pagina(F2, 2302, date(2015, 11, 1), base=2211))
    cliente.responder(url_sorteo(F2, 2299), 200, pagina(F2, 2299, date(2015, 10, 21), base=2211))
    extraccion = extraer(cliente_admin, cliente, "25/10/2015", "28/10/2015")
    assert (extraccion.numero_desde, extraccion.numero_hasta) == (2300, 2301)
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/2300/").content.decode()
    assert "Reglas del período no verificadas" in texto


def test_ac_3_10_siempre_sale_y_premio_extra(cliente_admin):
    extraccion = extraer(cliente_admin, cliente_con_sorteos(SORTEOS, base=3427))
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3426/").content.decode()
    assert "Siempre Sale" in texto and "Categoría ganadora" in texto
    assert ">5<" in texto.replace(" ", "").replace("\n", "")  # 5 aciertos
    assert "17" in texto
