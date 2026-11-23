"""[003] T182: Estadísticas en la API v1 (contracts/api.md § "Pantalla 2 — Frecuencias").

Los mismos casos que tests/integration/test_us6_estadisticas.py con la misma lectura de la consulta
y los mismos cálculos (NFR-009): porcentajes como cadena decimal, sorteos sin información y la
consulta anterior ante un error ([001] AC-6.8).
"""

from datetime import date

import pytest

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Modalidad
from quini6.fechas import hoy_buenos_aires
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

PS, LS = Modalidad.PRIMER_SORTEO, Modalidad.LA_SEGUNDA
API = "/api/v1/estadisticas/"


@pytest.fixture
def sorteos(db):
    """Ocho sorteos de enero de 2025 (los de test_us6_estadisticas.py)."""
    for i in range(8):
        c = crear_concurso(100 + i, date(2025, 1, 1 + i * 3), modalidades=[PS, LS])
        ps = {14, 1, 2, 3, 4, 5} if i == 0 else {20 + i, 1, 2, 3, 4, 5}
        cargar_numeros(c, PS, frozenset(ps))
        cargar_numeros(c, LS, frozenset({40, 41, 42, 43, 44, 14}))


def _numero(datos, n):
    return next(f for f in datos["numeros"] if f["numero"] == n)


def test_ac_6_1_predeterminado(visitante, sorteos):
    respuesta = visitante.get(API)
    assert respuesta.status_code == 200
    assert respuesta["Cache-Control"] == "no-cache"
    datos = respuesta.json()
    assert datos["consulta"]["modalidad"] == "PRIMER_SORTEO"
    assert datos["consulta"]["modalidad_nombre"] == "Tradicional – Primer Sorteo"
    assert datos["cantidad_sorteos"] == 8
    assert (datos["primera_fecha"], datos["ultima_fecha"]) == ("2025-01-01", "2025-01-22")
    assert len(datos["numeros"]) == 46
    assert _numero(datos, 1) == {"numero": 1, "frecuencia": 8, "porcentaje": "100.00"}
    assert _numero(datos, 45) == {"numero": 45, "frecuencia": 0, "porcentaje": "0.00"}
    assert [m["valor"] for m in datos["modalidades"]] == [
        "PRIMER_SORTEO",
        "LA_SEGUNDA",
        "REVANCHA",
        "SIEMPRE_SALE",
    ]


def test_ac_6_2_y_6_3_modalidad_y_periodo(visitante, sorteos):
    datos = visitante.get(API, {"modalidad": "LA_SEGUNDA"}).json()
    assert _numero(datos, 14)["frecuencia"] == 8
    periodo = visitante.get(API, {"desde": "04/01/2025", "hasta": "2025-01-10"}).json()
    assert periodo["cantidad_sorteos"] == 3
    assert _numero(periodo, 14) == {"numero": 14, "frecuencia": 0, "porcentaje": "0.00"}


def test_ac_6_6_numero_consultado(visitante, sorteos):
    datos = visitante.get(API, {"numero": "14"}).json()
    assert datos["numero_consultado"] == {"numero": 14, "frecuencia": 1, "porcentaje": "12.50"}


def test_ac_6_4_sin_sorteos(visitante, sorteos):
    datos = visitante.get(API, {"desde": "01/06/2025"}).json()
    assert datos["cantidad_sorteos"] == 0 and datos["numeros"] == []
    assert datos["primera_fecha"] is None and datos["numero_consultado"] is None


def test_rn_46_premio_extra_no_se_ofrece(visitante, sorteos):
    datos = visitante.get(API, {"modalidad": "PREMIO_EXTRA"}).json()
    assert datos["consulta"]["modalidad"] == "PRIMER_SORTEO"
    assert len(datos["avisos"]) == 1 and "Premio Extra" in datos["avisos"][0]


def test_ac_6_8_periodo_invalido_422_con_la_consulta_anterior(visitante, sorteos):
    respuesta = visitante.get(
        API,
        {
            "desde": "10/01/2025",
            "hasta": "01/01/2025",
            "anterior_modalidad": "LA_SEGUNDA",
            "anterior_desde": "04/01/2025",
            "anterior_hasta": "10/01/2025",
            "anterior_numero": "14",
        },
    )
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["detail"] == MENSAJES["est.periodo_invalido"]
    assert {(e["campo"], e["mensaje"]) for e in cuerpo["errores"]} == {
        ("hasta", mensaje("fecha.fin_anterior", fecha="10/01/2025"))
    }
    anterior = cuerpo["resultado"]
    assert anterior["consulta"]["modalidad"] == "LA_SEGUNDA"
    assert anterior["cantidad_sorteos"] == 3
    assert _numero(anterior, 14) == {"numero": 14, "frecuencia": 3, "porcentaje": "100.00"}


def test_ac_7_6_numero_fuera_de_rango(visitante, sorteos):
    respuesta = visitante.get(API, {"numero": "46"})
    assert respuesta.status_code == 422
    cuerpo = respuesta.json()
    assert cuerpo["errores"] == [
        {
            "campo": "numero",
            "codigo": "jugada.fuera_de_rango",
            "mensaje": MENSAJES["jugada.fuera_de_rango"],
        }
    ]
    assert cuerpo["resultado"]["cantidad_sorteos"] == 8  # predeterminada


def test_fecha_inexistente_junto_al_campo(visitante, sorteos):
    cuerpo = visitante.get(API, {"desde": "31/02/2025"}).json()
    assert {"campo": "desde", "codigo": "fecha.inexistente"}.items() <= cuerpo["errores"][0].items()


def test_paridad_con_la_vista_html(visitante, client, sorteos):
    """NFR-009: la página HTML muestra los mismos valores que devuelve la API."""
    datos = visitante.get(API, {"modalidad": "LA_SEGUNDA", "numero": "40"}).json()
    contenido = client.get("/estadisticas/", {"modalidad": "LA_SEGUNDA", "numero": "40"})
    html = contenido.content.decode()
    assert f"{datos['cantidad_sorteos']} sorteos considerados" in html
    assert "100,00 %" in html and datos["numero_consultado"]["porcentaje"] == "100.00"


def test_atajos_de_estadisticas_publicos_con_todo_el_historial(visitante, sorteos):
    atajos = visitante.get("/api/v1/periodos/atajos/", {"formulario": "estadisticas"}).json()
    assert [a["clave"] for a in atajos] == ["anio_en_curso", "anio_anterior", "todo_el_historial"]
    todo = atajos[2]
    assert todo["texto"] == MENSAJES["est.atajo_todo"]
    assert (todo["desde"], todo["hasta"]) == ("2025-01-01", hoy_buenos_aires().isoformat())


def test_atajos_sin_sorteos_omiten_todo_el_historial(visitante, db):
    atajos = visitante.get("/api/v1/periodos/atajos/", {"formulario": "estadisticas"}).json()
    assert [a["clave"] for a in atajos] == ["anio_en_curso", "anio_anterior"]
