"""[002] R-02, R-03, RN-08, NFR-005, NFR-006: cliente HTTP y limitador (T017, T066).

Usa un ``http.server`` local en un hilo de la prueba: nunca consulta internet.
"""

import threading
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from dominio.extraccion.tipos import Fuente, ResultadoIntento
from extracciones import cliente_http
from extracciones.cliente_http import (
    ClienteHttp,
    LimitadorPorSitio,
    RespuestaHttp,
    resultado_por_respuesta,
)
from extracciones.fuentes.fichas import FICHAS
from tests.extraccion_falsos import LimitadorSinEspera

R = ResultadoIntento


class _Manejador(BaseHTTPRequestHandler):
    pedidos: list = []

    def log_message(self, *args):
        pass

    def do_GET(self):
        type(self).pedidos.append((self.path, self.headers.get("User-Agent")))
        if self.path == "/ok":
            cuerpo = "<p>Sorteo ñandú</p>".encode("latin-1")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=latin-1")
            self.end_headers()
            self.wfile.write(cuerpo)
        elif self.path == "/meta":
            cuerpo = '<meta charset="utf-8"><p>miércoles</p>'.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(cuerpo)
        elif self.path == "/grande":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"x" * (2 * 1024 * 1024 + 10))
        elif self.path == "/lento":
            threading.Event().wait(1.5)
            self.send_response(200)
            self.end_headers()
        elif self.path == "/afuera":
            self.send_response(302)
            self.send_header("Location", "http://otro.sitio.invalido/x")
            self.end_headers()
        elif self.path == "/adentro":
            self.send_response(302)
            self.send_header("Location", "/ok")
            self.end_headers()
        elif self.path == "/prohibido":
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
        else:
            self.send_response(404)
            self.end_headers()


@pytest.fixture
def servidor():
    _Manejador.pedidos = []
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Manejador)
    hilo = threading.Thread(target=httpd.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture
def cliente():
    return ClienteHttp(LimitadorSinEspera())


def test_codificacion_del_encabezado_y_user_agent(servidor, cliente):
    respuesta = cliente.obtener(Fuente.F2, f"{servidor}/ok")
    assert respuesta.codigo == 200 and "ñandú" in respuesta.texto
    assert _Manejador.pedidos[-1][1] == "QUINI6-extraccion-historica/1.0"


def test_codificacion_de_meta_charset(servidor, cliente):
    assert "miércoles" in cliente.obtener(Fuente.F1, f"{servidor}/meta").texto


def test_mas_de_2_mb_es_error(servidor, cliente):
    respuesta = cliente.obtener(Fuente.F2, f"{servidor}/grande")
    assert respuesta.error and respuesta.texto is None


def test_limite_de_espera_vencido_es_error(servidor, cliente, monkeypatch):
    monkeypatch.setattr(cliente_http, "LIMITE_ESPERA_SEGUNDOS", 0.3)
    respuesta = cliente.obtener(Fuente.F2, f"{servidor}/lento")
    assert respuesta.error is not None
    assert resultado_por_respuesta(respuesta, FICHAS[Fuente.F2]) is R.NO_DISPONIBLE


def test_redireccion_a_otro_sitio_rechazada_y_dentro_del_sitio_seguida(servidor, cliente):
    afuera = cliente.obtener(Fuente.F2, f"{servidor}/afuera")
    assert afuera.error and afuera.codigo is None
    assert cliente.obtener(Fuente.F2, f"{servidor}/adentro").codigo == 200


def test_un_403_se_consulta_una_sola_vez(servidor, cliente):
    respuesta = cliente.obtener(Fuente.F2, f"{servidor}/prohibido")
    assert respuesta.codigo == 403
    assert [p for p, _ in _Manejador.pedidos].count("/prohibido") == 1
    assert resultado_por_respuesta(respuesta, FICHAS[Fuente.F2]) is R.NO_DISPONIBLE


class _Reloj:
    def __init__(self):
        self.ahora = 100.0
        self.esperas = []

    def __call__(self):
        return self.ahora

    def dormir(self, segundos):
        self.esperas.append(segundos)
        self.ahora += segundos


def test_limitador_mismo_sitio_separado_por_2_segundos():
    reloj = _Reloj()
    limitador = LimitadorPorSitio(reloj=reloj, dormir=reloj.dormir)
    limitador.esperar_turno("numerosganadores.com.ar")
    reloj.ahora += 0.5
    limitador.esperar_turno("numerosganadores.com.ar")
    assert reloj.esperas == [pytest.approx(1.5)]


def test_limitador_sitios_distintos_sin_espera():
    reloj = _Reloj()
    limitador = LimitadorPorSitio(reloj=reloj, dormir=reloj.dormir)
    for sitio in ("a.com.ar", "b.com.ar", "c.com.ar"):
        limitador.esperar_turno(sitio)
    assert reloj.esperas == []


def test_intervalo_fijo_en_el_codigo():
    assert cliente_http.INTERVALO_SEGUNDOS == 2.0


# -- RN-08: resultado de cada respuesta (T066) -----------------------------------------


def respuesta(codigo=200, texto="<p>ok</p>", error=None):
    return RespuestaHttp(codigo, texto, error, datetime(2026, 11, 19, tzinfo=UTC))


@pytest.mark.parametrize("fuente, codigo, esperado", [
    (Fuente.F1, 404, R.NO_ENCONTRADO),
    (Fuente.F3, 404, R.NO_ENCONTRADO),
    (Fuente.F2, 500, R.NO_DISPONIBLE_O_NO_ENCONTRADO),
    (Fuente.F2, 404, R.NO_DISPONIBLE),
    (Fuente.F1, 500, R.NO_DISPONIBLE),
    (Fuente.F3, 503, R.NO_DISPONIBLE),
    (Fuente.F1, 403, R.NO_DISPONIBLE),
    (Fuente.F2, 429, R.NO_DISPONIBLE),
    (Fuente.F2, 200, None),
])  # fmt: skip
def test_rn_08_correspondencia_de_codigos(fuente, codigo, esperado):
    assert resultado_por_respuesta(respuesta(codigo), FICHAS[fuente]) is esperado


def test_error_de_conexion_tls_o_espera_es_no_disponible():
    r = respuesta(None, None, "URLError: certificate verify failed")
    assert resultado_por_respuesta(r, FICHAS[Fuente.F3]) is R.NO_DISPONIBLE


def test_ac_2_9_pagina_anti_robots_es_no_disponible():
    texto = "<html><head><title>Just a moment...</title></head></html>"
    assert resultado_por_respuesta(respuesta(200, texto), FICHAS[Fuente.F1]) is R.NO_DISPONIBLE


def test_pagina_normal_de_f1_con_challenge_platform_no_es_anti_robots():
    texto = "<script>var u='/cdn-cgi/challenge-platform/scripts/jsd/main.js'</script>"
    assert resultado_por_respuesta(respuesta(200, texto), FICHAS[Fuente.F1]) is None
