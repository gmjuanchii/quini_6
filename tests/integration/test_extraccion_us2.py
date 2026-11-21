"""[002] Historia 2: varias fuentes con respaldo (T068, T093; RN-07, RN-08, RN-09, RN-10, NFR-005,
NFR-006). Prioridad F2 → F3 → F1: F1 solo se consulta si falta algún dato (AC-2.11)."""

from datetime import date

import pytest

from dominio.extraccion.tipos import Fuente
from extracciones.models import Extraccion
from tests.extraccion_falsos import (
    HOY,
    cliente_con_sorteos,
    listado_f1,
    pagina,
    procesar_pendientes,
    url_listado,
    url_sorteo,
)

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
F1, F2, F3 = Fuente.F1, Fuente.F2, Fuente.F3
TODAS = (F1, F2, F3)
SORTEOS = {
    3421: date(2026, 10, 28),
    3422: date(2026, 11, 1),
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
    3426: date(2026, 11, 15),
    3427: date(2026, 11, 18),
}
ANTIROBOTS = "<html><head><title>Just a moment...</title></head><body>cf_chl_opt</body></html>"


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


def u(fuente, numero):
    return url_sorteo(fuente, numero, SORTEOS.get(numero) if fuente is F1 else None)


def extraer(cliente_admin, cliente, inicio="01/11/2026", fin="15/11/2026"):
    cliente_admin.post(INICIO, {"inicio": inicio, "fin": fin})
    procesar_pendientes(cliente)
    return Extraccion.objects.order_by("-id").first()


def detalle(cliente_admin, extraccion, numero):
    return cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/{numero}/").content.decode()


def resultado(extraccion, numero, fuente):
    return extraccion.sorteos.get(numero=numero).intentos.get(fuente=fuente.value).resultado


@pytest.fixture
def con_fallas(cliente_admin):
    cliente = cliente_con_sorteos(SORTEOS, fuentes=TODAS)
    cliente.responder(u(F3, 3422), 500, "")  # AC-2.2
    cliente.responder(u(F2, 3423), 500, "Error.")  # AC-2.3
    cliente.responder(u(F3, 3423), 404, "")
    cliente.responder(u(F3, 3424), 200, "<html><body><h1>Nuevo diseño</h1></body></html>")
    sin_revancha = pagina(F2, 3425, SORTEOS[3425]).replace(
        '<h3 class="card-title">REVANCHA</h3>', '<h3 class="card-title">OTRA COSA</h3>'
    )
    cliente.responder(u(F2, 3425), 200, sin_revancha)  # AC-2.5 (bloque no reconocido)
    cliente.demora(u(F1, 3426))  # AC-2.8
    cliente.responder(u(F2, 3426), 403, "Forbidden")  # AC-2.9
    cliente.responder(u(F3, 3426), 200, ANTIROBOTS)  # AC-2.9
    return cliente, extraer(cliente_admin, cliente)


def test_ac_2_2_fuente_que_no_responde(cliente_admin, con_fallas):
    _, extraccion = con_fallas
    assert resultado(extraccion, 3422, F3) == "NO_DISPONIBLE"
    assert resultado(extraccion, 3422, F1) == "NO_REQUERIDA"  # F2 aportó todo (AC-2.11)
    texto = detalle(cliente_admin, extraccion, 3422)
    assert "No disponible" in texto and "No requerida" in texto
    # D-23: la fuente que respondió figura en "Fuentes consultadas", no junto a cada dato.
    assert "numerosganadores.com.ar" in texto and "Obtenido" in texto
    assert "(numerosganadores.com.ar)" not in texto
    assert extraccion.sorteos.get(numero=3422).estado == "RECUPERADO"


def test_ac_2_3_no_encontrado_y_no_disponible_o_no_encontrado(cliente_admin, con_fallas):
    _, extraccion = con_fallas
    assert resultado(extraccion, 3423, F3) == "NO_ENCONTRADO"
    assert resultado(extraccion, 3423, F2) == "NO_DISPONIBLE_O_NO_ENCONTRADO"
    texto = detalle(cliente_admin, extraccion, 3423)
    assert "No encontrado" in texto and "No disponible o no encontrado" in texto
    assert "quini-6-resultados.com.ar" in texto  # los datos salen de F1


def test_ac_2_4_estructura_no_reconocida_sin_datos(con_fallas):
    _, extraccion = con_fallas
    intento = extraccion.sorteos.get(numero=3424).intentos.get(fuente="F3")
    assert intento.resultado == "ESTRUCTURA_NO_RECONOCIDA" and intento.datos is None


def test_ac_2_5_incompleto_indica_que_falta_y_se_completa(cliente_admin, con_fallas):
    _, extraccion = con_fallas
    assert resultado(extraccion, 3425, F2) == "INCOMPLETO"
    texto = detalle(cliente_admin, extraccion, 3425)
    assert "Incompleto" in texto and "Falta: Revancha" in texto
    revancha = extraccion.sorteos.get(numero=3425).consolidado["modalidades"]["REVANCHA"]
    assert revancha["informada"] and revancha["numeros"]["fuentes"] == ["F3"]
    assert resultado(extraccion, 3425, F1) == "NO_REQUERIDA"  # F3 completó lo que faltaba


def test_ac_2_8_y_2_9_demora_403_y_anti_robots(cliente_admin, con_fallas):
    cliente, extraccion = con_fallas
    for fuente in TODAS:
        assert resultado(extraccion, 3426, fuente) == "NO_DISPONIBLE"
    assert extraccion.sorteos.count() == 5  # el avance llegó al total
    for fuente in (F2, F3):
        assert cliente.pedidas.count(u(fuente, 3426)) == 1  # sin reintentos (NFR-005)
    texto = detalle(cliente_admin, extraccion, 3426)
    assert "No recuperado" in texto
    assert "quiniya.com.ar: No disponible" in texto  # AC-2.7: motivo de cada fuente
    sorteo = extraccion.sorteos.get(numero=3426).consolidado
    assert not any(m["informada"] for m in sorteo["modalidades"].values())  # sin números


def test_ac_2_1_resumen_por_fuente(cliente_admin, con_fallas):
    _, extraccion = con_fallas
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/").content.decode()
    assert "Sorteos aportados" in texto and "Intentos fallidos" in texto
    fuentes = {f["fuente"]: f for f in extraccion.resumen["fuentes"]}
    assert fuentes["F1"]["fallidos"] == {"NO_DISPONIBLE": 1}  # "No requerida" no es falla
    assert fuentes["F2"]["fallidos"] == {
        "INCOMPLETO": 1,
        "NO_DISPONIBLE": 1,
        "NO_DISPONIBLE_O_NO_ENCONTRADO": 1,
    }
    assert fuentes["F3"]["aportados"] == 1
    assert "No disponible o no encontrado: 1" in texto


def test_ac_4_8_y_2_11_f2_y_f3_siempre_y_f1_solo_si_hace_falta(cliente_admin):
    cliente = cliente_con_sorteos(SORTEOS, fuentes=TODAS)
    extraccion = extraer(cliente_admin, cliente, "01/11/2026", "01/11/2026")
    assert extraccion.sorteos.get(numero=3422).intentos.count() == 3
    for fuente in (F2, F3):
        assert u(fuente, 3422) in cliente.pedidas
    assert u(F1, 3422) not in cliente.pedidas
    assert resultado(extraccion, 3422, F1) == "NO_REQUERIDA"
    assert extraccion.resumen["fuentes"][2]["fuente"] == "F1"  # orden de prioridad (RN-07)


def test_ac_2_11_f1_completa_lo_que_falta_en_f2_y_f3(cliente_admin):
    cliente = cliente_con_sorteos(SORTEOS, fuentes=TODAS)
    sin_revancha = pagina(F2, 3422, SORTEOS[3422]).replace(
        '<h3 class="card-title">REVANCHA</h3>', '<h3 class="card-title">OTRA COSA</h3>'
    )
    cliente.responder(u(F2, 3422), 200, sin_revancha)
    cliente.responder(u(F3, 3422), 404, "")
    extraccion = extraer(cliente_admin, cliente, "01/11/2026", "01/11/2026")
    assert u(F1, 3422) in cliente.pedidas
    assert resultado(extraccion, 3422, F1) == "OBTENIDO"
    revancha = extraccion.sorteos.get(numero=3422).consolidado["modalidades"]["REVANCHA"]
    assert revancha["numeros"]["fuentes"] == ["F1"]


def test_ac_2_6_fuera_de_cobertura_no_es_falla(cliente_admin):
    antiguos = {2700: date(2020, 3, 1), 2701: date(2020, 3, 4)}
    cliente = cliente_con_sorteos(SORTEOS, fuentes=TODAS)
    for numero, fecha in antiguos.items():
        cliente.responder(url_sorteo(F2, numero), 200, pagina(F2, numero, fecha))
    cliente.responder(url_sorteo(F2, 2699), 200, pagina(F2, 2699, date(2020, 2, 26)))
    cliente.responder(url_sorteo(F2, 2702), 200, pagina(F2, 2702, date(2020, 3, 8)))
    extraccion = extraer(cliente_admin, cliente, "01/03/2020", "04/03/2020")
    assert (extraccion.numero_desde, extraccion.numero_hasta) == (2700, 2701)
    intento = extraccion.sorteos.get(numero=2700).intentos.get(fuente="F3")
    assert intento.resultado == "FUERA_DE_COBERTURA" and intento.url == ""
    assert intento.consultado_en is None
    # I-08 (D-21): la fecha la informa F2, así que F1 lo cubre; no hizo falta consultarla.
    assert resultado(extraccion, 2700, F1) == "NO_REQUERIDA"
    assert url_sorteo(F3, 2700) not in cliente.pedidas
    assert "Fuera de cobertura" in detalle(cliente_admin, extraccion, 2700)
    fuentes = {f["fuente"]: f for f in extraccion.resumen["fuentes"]}
    assert fuentes["F3"]["fallidos"] == {}


def test_ac_2_10_requiere_mantenimiento(cliente_admin):
    cliente = cliente_con_sorteos(SORTEOS, fuentes=TODAS)
    for numero in (3422, 3423):
        cliente.responder(u(F3, numero), 200, "<html><body><p>Rediseño</p></body></html>")
    extraccion = extraer(cliente_admin, cliente, "01/11/2026", "04/11/2026")
    fuentes = {f["fuente"]: f for f in extraccion.resumen["fuentes"]}
    assert fuentes["F3"]["requiere_mantenimiento"]
    assert not fuentes["F2"]["requiere_mantenimiento"]
    texto = cliente_admin.get(f"{INICIO}{extraccion.pk}/").content.decode()
    assert "Requiere mantenimiento" in texto


def test_d_21_f1_desempata_aunque_el_sorteo_no_figure_en_su_listado(cliente_admin):
    """Como en el sorteo 3235: numerosganadores informa vacante el Segundo Premio de Tradicional
    y quiniya 18 ganadores. F1 no lo tiene en su listado, pero se le pide con la fecha de las
    otras dos y desempata: valen los 18 ganadores y el sorteo queda "Recuperado"."""
    cliente = cliente_con_sorteos(SORTEOS, fuentes=TODAS)
    cliente.responder(url_listado(F1), 200, listado_f1({3427: SORTEOS[3427]}))
    vacante = pagina(F2, 3422, SORTEOS[3422]).replace(
        "<tr><td>5</td><td> 18 </td><td>3.013.912</td></tr>",
        "<tr><td>5</td><td>  <span>Vacante</span>  </td><td>3.013.912</td></tr>",
    )
    cliente.responder(u(F2, 3422), 200, vacante)
    extraccion = extraer(cliente_admin, cliente, "01/11/2026", "01/11/2026")
    assert u(F1, 3422) in cliente.pedidas  # dirección con la fecha 01-11-2026
    assert resultado(extraccion, 3422, F1) == "OBTENIDO"
    fila = extraccion.sorteos.get(numero=3422)
    segundo = fila.consolidado["modalidades"]["PRIMER_SORTEO"]["categorias"]["SEGUNDO"]
    assert segundo["ganadores"]["dato"]["valor"] == 18
    assert segundo["ganadores"]["fuentes"] == ["F3", "F1"]
    assert fila.estado == "RECUPERADO"
    texto = detalle(cliente_admin, extraccion, 3422)
    assert "Resuelto por coincidencia de 2 de 3 fuentes" in texto
