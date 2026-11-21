"""[002] R-11: escenarios del servidor de fuentes de prueba (T086)."""

import threading
import urllib.error
import urllib.request

import pytest

from tests.fuentes_prueba.servidor import ESCENARIOS, cargar_escenario, crear_servidor

NOMBRES = ["normal", "fallas", "estructura", "discrepancias", "normalizacion"]


def test_estan_los_cinco_escenarios():
    assert sorted(p.name for p in ESCENARIOS.iterdir() if p.is_dir()) == sorted(NOMBRES)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_escenario_valido_y_paginas_existentes(nombre):
    carpeta, escenario = cargar_escenario(nombre)
    assert escenario["descripcion"]
    assert escenario["rutas"]
    for ruta, regla in escenario["rutas"].items():
        assert ruta.startswith(("/f1/", "/f2/", "/f3/")), ruta
        assert set(regla) <= {"pagina", "codigo", "demora"}, ruta
        assert 100 <= int(regla.get("codigo", 200)) <= 599
        if "pagina" in regla:
            assert (carpeta / regla["pagina"]).is_file(), regla["pagina"]


@pytest.fixture
def servidor():
    httpd = crear_servidor("fallas", puerto=0)
    hilo = threading.Thread(target=httpd.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def obtener(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as respuesta:
            return respuesta.status, respuesta.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8")


def test_el_servidor_responde_lo_declarado(servidor):
    carpeta, escenario = cargar_escenario("fallas")
    codigo, texto = obtener(f"{servidor}/f2/sorteos/3422")
    assert codigo == 200
    assert texto == (carpeta / escenario["rutas"]["/f2/sorteos/3422"]["pagina"]).read_text(
        encoding="utf-8"
    )
    assert obtener(f"{servidor}/f2/sorteos/3423")[0] == 500
    assert obtener(f"{servidor}/f3/sorteos/3423")[0] == 404
    assert obtener(f"{servidor}/f9/no-declarada")[0] == 404
