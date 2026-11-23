"""[003] HU-04: campos de fecha iguales en toda la aplicación, atajos y mensajes junto al campo.

AC-4.4, AC-4.5, AC-4.7, FR-010 a FR-012, RN-04. Las reglas de fechas de [001] y [002] no cambian:
solo cambian la presentación y el lugar del mensaje.
"""

import html
import json
import re
from datetime import date

import pytest

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Modalidad
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

HOY = date(2026, 11, 21)
EXTRACCION = "/administracion/extracciones/"
ESTADISTICAS = "/estadisticas/"


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)
    monkeypatch.setattr("quini6.fechas.hoy_buenos_aires", lambda: HOY)


def _entrada(contenido: str, nombre: str) -> dict[str, str]:
    """Atributos del ``<input>`` con ese ``name`` (valores sin escapar)."""
    m = re.search(rf'<input\b[^>]*\bname="{nombre}"[^>]*>', contenido)
    assert m, f"no está el campo {nombre}"
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', m.group(0))}


def _error_junto_al_campo(contenido: str, id_campo: str) -> str:
    m = re.search(rf'<p\b[^>]*id="{id_campo}_error"[^>]*>(.*?)</p>', contenido, re.S)
    assert m, f"no está el lugar del error de {id_campo}"
    assert " hidden" not in m.group(0).split(">")[0], "el error está oculto"
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()


def _reglas(entrada: dict[str, str]) -> list[dict]:
    return json.loads(entrada["data-validar"])


# --- FR-010: el mismo campo de fecha en los cuatro formularios ------------------------------


def test_extraccion_usa_el_campo_de_fecha_con_maximo_hoy(cliente_admin):
    contenido = cliente_admin.get(EXTRACCION).content.decode()
    for nombre in ("inicio", "fin"):
        entrada = _entrada(contenido, nombre)
        assert entrada["type"] == "date"
        assert entrada["max"] == "2026-11-21"  # AC-4.7: el calendario no ofrece días futuros
        assert "data-validar" in entrada
    assert 'data-campo-fecha="inicio"' in contenido
    assert "data-validar-formulario" in contenido and "novalidate" in contenido


def test_extraccion_declara_las_reglas_previas_con_los_textos_del_catalogo(cliente_admin):
    contenido = cliente_admin.get(EXTRACCION).content.decode()
    inicio = {r["regla"]: r for r in _reglas(_entrada(contenido, "inicio"))}
    fin = {r["regla"]: r for r in _reglas(_entrada(contenido, "fin"))}
    assert inicio["requerido"]["texto"] == MENSAJES["fecha.falta_inicio"]
    assert inicio["fecha"]["texto"] == MENSAJES["gral.fecha_invalida"]
    assert inicio["fecha"]["texto_inexistente"] == MENSAJES["fecha.inexistente"]
    assert fin["requerido"]["texto"] == MENSAJES["fecha.falta_fin"]
    assert fin["max"] == {
        "regla": "max",
        "valor": "2026-11-21",
        "texto": MENSAJES["ext.fin_futura"],
    }
    assert fin["fin_no_anterior_a"]["campo"] == "id_inicio"
    assert fin["fin_no_anterior_a"]["texto"] == MENSAJES["fecha.fin_anterior"]


def test_estadisticas_usa_el_campo_de_fecha_con_etiquetas_breves(client):
    contenido = client.get(ESTADISTICAS).content.decode()
    for nombre in ("desde", "hasta"):
        entrada = _entrada(contenido, nombre)
        assert entrada["type"] == "date"
        assert "data-validar" in entrada
    assert re.search(r'<label for="est-desde"[^>]*>\s*Desde\s*</label>', contenido)
    assert re.search(r'<label for="est-hasta"[^>]*>\s*Hasta\s*</label>', contenido)
    assert "data-validar-formulario" in contenido


def test_busqueda_por_fecha_usa_el_campo_de_fecha(client):
    crear_concurso(3420, date(2026, 11, 1), modalidades=[Modalidad.PRIMER_SORTEO])
    contenido = client.get("/resultados/").content.decode()
    entrada = _entrada(contenido, "fecha")
    assert entrada["type"] == "date"
    assert 'data-campo-fecha="fecha"' in contenido


def test_carga_de_sorteo_usa_el_campo_de_fecha(cliente_admin):
    contenido = cliente_admin.get("/administracion/concursos/nuevo/").content.decode()
    entrada = _entrada(contenido, "fecha_sorteo")
    assert entrada["type"] == "date"
    assert 'data-campo-fecha="fecha_sorteo"' in contenido


# --- AC-4.4, RN-04: atajos ---------------------------------------------------------------------


def test_extraccion_ofrece_solo_dos_atajos_como_enlaces(cliente_admin):
    contenido = cliente_admin.get(EXTRACCION).content.decode()
    assert 'href="?atajo=anio_en_curso"' in contenido
    assert 'href="?atajo=anio_anterior"' in contenido
    assert "atajo=todo_el_historial" not in contenido
    assert MENSAJES["ext.atajo_anio_en_curso"] in contenido


def test_atajo_anio_anterior_precarga_la_extraccion(cliente_admin):
    contenido = cliente_admin.get(EXTRACCION, {"atajo": "anio_anterior"}).content.decode()
    assert _entrada(contenido, "inicio")["value"] == "2025-01-01"
    assert _entrada(contenido, "fin")["value"] == "2025-12-31"


def test_atajo_desconocido_no_precarga_nada(cliente_admin):
    contenido = cliente_admin.get(EXTRACCION, {"atajo": "manana"}).content.decode()
    assert _entrada(contenido, "inicio").get("value", "") == ""


def test_estadisticas_ofrece_los_tres_atajos(client):
    concurso = crear_concurso(3300, date(2025, 3, 2), modalidades=[Modalidad.PRIMER_SORTEO])
    cargar_numeros(concurso, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
    contenido = client.get(ESTADISTICAS).content.decode()
    for clave in ("anio_en_curso", "anio_anterior", "todo_el_historial"):
        assert f"atajo={clave}" in contenido
    assert MENSAJES["est.atajo_todo"] in contenido
    assert 'data-hasta="2026-11-21"' in contenido and 'data-desde="2025-03-02"' in contenido


def test_estadisticas_sin_sorteos_publicados_no_ofrece_todo_el_historial(client):
    contenido = client.get(ESTADISTICAS).content.decode()
    assert "atajo=todo_el_historial" not in contenido


def test_atajo_anio_anterior_precarga_estadisticas(client):
    contenido = client.get(ESTADISTICAS, {"atajo": "anio_anterior"}).content.decode()
    assert _entrada(contenido, "desde")["value"] == "2025-01-01"
    assert _entrada(contenido, "hasta")["value"] == "2025-12-31"


# --- AC-4.5, FR-012: mensajes junto al campo (el servidor repite la validación previa) --------


@pytest.mark.parametrize("escrita", ["31/02/2025", "29/02/2025"])
def test_fecha_inexistente_junto_al_campo(cliente_admin, escrita):
    respuesta = cliente_admin.post(EXTRACCION, {"inicio": escrita, "fin": "01/03/2025"})
    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert _error_junto_al_campo(contenido, "id_inicio") == mensaje(
        "fecha.inexistente", fecha=escrita
    )


def test_29_02_2024_se_acepta(cliente_admin):
    respuesta = cliente_admin.post(EXTRACCION, {"inicio": "29/02/2024", "fin": "01/03/2024"})
    assert respuesta.status_code == 303


def test_formato_invalido_junto_al_campo(cliente_admin):
    contenido = cliente_admin.post(EXTRACCION, {"inicio": "ayer", "fin": "01/03/2025"})
    texto = _error_junto_al_campo(contenido.content.decode(), "id_inicio")
    assert texto == MENSAJES["gral.fecha_invalida"]


def test_fin_anterior_al_inicio_junto_al_campo_y_resumen_general(cliente_admin):
    contenido = cliente_admin.post(
        EXTRACCION, {"inicio": "01/01/2025", "fin": "01/12/2024"}
    ).content.decode()
    assert _error_junto_al_campo(contenido, "id_fin") == mensaje(
        "fecha.fin_anterior", fecha="01/01/2025"
    )
    # El mensaje general de [002] RN-03 se mantiene en el resumen del formulario.
    assert "La fecha de inicio no puede ser posterior a la fecha de finalización" in contenido


def test_fechas_vacias_obligatorias(cliente_admin):
    contenido = cliente_admin.post(EXTRACCION, {"inicio": "", "fin": ""}).content.decode()
    assert _error_junto_al_campo(contenido, "id_inicio") == MENSAJES["fecha.falta_inicio"]
    assert _error_junto_al_campo(contenido, "id_fin") == MENSAJES["fecha.falta_fin"]


def test_el_campo_conserva_la_fecha_valida_en_formato_del_calendario(cliente_admin):
    contenido = cliente_admin.post(
        EXTRACCION, {"inicio": "01/01/2025", "fin": "01/12/2024"}
    ).content.decode()
    assert _entrada(contenido, "inicio")["value"] == "2025-01-01"


def test_estadisticas_fecha_inexistente_junto_al_campo(client):
    contenido = client.get(ESTADISTICAS, {"desde": "31/02/2025"}).content.decode()
    assert _error_junto_al_campo(contenido, "est-desde") == mensaje(
        "fecha.inexistente", fecha="31/02/2025"
    )


def test_estadisticas_fin_anterior_junto_al_campo(client):
    contenido = client.get(
        ESTADISTICAS, {"desde": "01/06/2025", "hasta": "01/01/2025"}
    ).content.decode()
    assert _error_junto_al_campo(contenido, "est-hasta") == mensaje(
        "fecha.fin_anterior", fecha="01/06/2025"
    )


def test_estadisticas_acepta_la_fecha_del_calendario(client):
    """Sin scripts el navegador envía AAAA-MM-DD ([003] R-07): se acepta igual que dd/mm/aaaa."""
    contenido = client.get(ESTADISTICAS, {"desde": "2025-01-01"}).content.decode()
    assert 'role="alert"' not in contenido.split("<main", 1)[1].split("</form>", 1)[0]
    assert _entrada(contenido, "desde")["value"] == "2025-01-01"


def test_busqueda_fecha_inexistente_junto_al_campo(client):
    contenido = client.get("/resultados/buscar/", {"fecha": "29/02/2025"}).content.decode()
    assert _error_junto_al_campo(contenido, "buscar-fecha") == mensaje(
        "fecha.inexistente", fecha="29/02/2025"
    )


def test_busqueda_acepta_la_fecha_del_calendario(client):
    crear_concurso(3420, date(2026, 11, 1), modalidades=[Modalidad.PRIMER_SORTEO])
    respuesta = client.get("/resultados/buscar/", {"fecha": "2026-11-01"})
    assert respuesta.status_code == 200
    assert "3420" in respuesta.content.decode()


def test_carga_de_sorteo_fecha_inexistente_junto_al_campo(cliente_admin):
    contenido = cliente_admin.post(
        "/administracion/concursos/nuevo/",
        {"numero": "3500", "fecha_sorteo": "31/02/2025", "modalidades": ["PRIMER_SORTEO"]},
    ).content.decode()
    assert _error_junto_al_campo(contenido, "id_fecha_sorteo") == mensaje(
        "fecha.inexistente", fecha="31/02/2025"
    )
