"""Cliente HTTP de las fuentes y limitador por sitio ([002] R-02, R-03, NFR-005, NFR-006).

Solo ``GET`` con ``urllib.request``, a direcciones armadas con las fichas (nunca tomadas del
contenido de una página). Límite de espera de 10 s, certificados verificados, redirecciones solo
dentro del mismo sitio, respuestas de hasta 2 MB y sin reintentos: ante un 403, un 429 o una
verificación anti-robots no se cambian encabezados ni se usan intermediarios.
"""

from __future__ import annotations

import re
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlsplit

from dominio.extraccion.tipos import Ficha, Fuente, ResultadoIntento

USER_AGENT = "QUINI6-extraccion-historica/1.0"
LIMITE_ESPERA_SEGUNDOS = 10
TAMANIO_MAXIMO = 2 * 1024 * 1024
#: NFR-005: al menos 2 s entre el inicio de dos consultas al mismo sitio. Fijo en el código:
#: no se configura por variable de entorno, para que no se pueda bajar por error.
INTERVALO_SEGUNDOS = 2.0

_META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?([A-Za-z0-9_\-]+)""", re.I)


@dataclass(frozen=True)
class RespuestaHttp:
    codigo: int | None
    texto: str | None
    error: str | None
    consultado_en: datetime


class LimitadorPorSitio:
    """Garantiza ``INTERVALO_SEGUNDOS`` entre el inicio de dos consultas al mismo sitio.

    Seguro entre hilos. El reloj y la espera se inyectan para las pruebas.
    """

    def __init__(
        self,
        intervalo: float = INTERVALO_SEGUNDOS,
        reloj: Callable[[], float] = time.monotonic,
        dormir: Callable[[float], None] = time.sleep,
    ):
        self.intervalo = intervalo
        self._reloj = reloj
        self._dormir = dormir
        self._candado = threading.Lock()
        self._por_sitio: dict[str, threading.Lock] = {}
        self._ultimo: dict[str, float] = {}

    def _candado_de(self, sitio: str) -> threading.Lock:
        with self._candado:
            return self._por_sitio.setdefault(sitio, threading.Lock())

    def esperar_turno(self, sitio: str) -> None:
        with self._candado_de(sitio):
            ultimo = self._ultimo.get(sitio)
            if ultimo is not None:
                espera = ultimo + self.intervalo - self._reloj()
                if espera > 0:
                    self._dormir(espera)
            self._ultimo[sitio] = self._reloj()


class _SoloMismoSitio(urllib.request.HTTPRedirectHandler):
    """Sigue redirecciones solo dentro del mismo sitio ([002] R-02)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).netloc.lower() != urlsplit(req.full_url).netloc.lower():
            raise urllib.error.HTTPError(
                req.full_url, code, "Redirección a otro sitio rechazada", headers, fp
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _ahora() -> datetime:
    return datetime.now(UTC)


def _codificacion(content_type: str | None, cuerpo: bytes) -> str:
    if content_type:
        coincidencia = re.search(r"charset\s*=\s*([A-Za-z0-9_\-]+)", content_type, re.I)
        if coincidencia:
            return coincidencia.group(1)
    coincidencia = _META_CHARSET.search(cuerpo[:4096])
    if coincidencia:
        return coincidencia.group(1).decode("ascii", "replace")
    return "utf-8"


def _decodificar(cuerpo: bytes, content_type: str | None) -> str:
    codificacion = _codificacion(content_type, cuerpo)
    try:
        return cuerpo.decode(codificacion, errors="replace")
    except LookupError:
        return cuerpo.decode("utf-8", errors="replace")


class ClienteHttp:
    """Cliente real. ``obtener`` respeta el limitador compartido del trabajador."""

    def __init__(self, limitador: LimitadorPorSitio | None = None):
        self.limitador = limitador or LimitadorPorSitio()
        self._abridor = urllib.request.build_opener(_SoloMismoSitio())

    def obtener(self, fuente: Fuente, url: str) -> RespuestaHttp:
        self.limitador.esperar_turno(urlsplit(url).netloc.lower() or fuente.value)
        consultado_en = _ahora()
        pedido = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
        try:
            with self._abridor.open(pedido, timeout=LIMITE_ESPERA_SEGUNDOS) as respuesta:
                cuerpo = respuesta.read(TAMANIO_MAXIMO + 1)
                if len(cuerpo) > TAMANIO_MAXIMO:
                    error = "Respuesta mayor a 2 MB"
                    return RespuestaHttp(respuesta.status, None, error, consultado_en)
                texto = _decodificar(cuerpo, respuesta.headers.get("Content-Type"))
                return RespuestaHttp(respuesta.status, texto, None, consultado_en)
        except urllib.error.HTTPError as error:
            try:
                cuerpo = error.read(TAMANIO_MAXIMO + 1) or b""
            except Exception:  # noqa: BLE001 - cuerpo ilegible: se registra solo el código
                cuerpo = b""
            texto = _decodificar(cuerpo[:TAMANIO_MAXIMO], error.headers.get("Content-Type"))
            if error.code in (301, 302, 303, 307, 308):
                return RespuestaHttp(None, None, "Redirección a otro sitio", consultado_en)
            return RespuestaHttp(error.code, texto, None, consultado_en)
        except Exception as error:  # noqa: BLE001 - conexión, TLS o límite de espera (NFR-006)
            return RespuestaHttp(None, None, f"{type(error).__name__}: {error}", consultado_en)


def es_pagina_antirobots(texto: str | None, ficha: Ficha) -> bool:
    return bool(texto) and any(m in texto for m in ficha.marcadores_antirobots)


def resultado_por_respuesta(respuesta: RespuestaHttp, ficha: Ficha) -> ResultadoIntento | None:
    """Tabla de [002] RN-08 / R-02. ``None`` significa "respuesta 200 para interpretar"."""
    if respuesta.error is not None or respuesta.codigo is None:
        return ResultadoIntento.NO_DISPONIBLE
    if respuesta.codigo in ficha.codigos_inexistente:
        return ficha.codigos_inexistente[respuesta.codigo]
    if respuesta.codigo != 200:
        return ResultadoIntento.NO_DISPONIBLE  # otro 5xx, 403, 429…
    if es_pagina_antirobots(respuesta.texto, ficha):
        return ResultadoIntento.NO_DISPONIBLE  # AC-2.9
    return None
