"""Errores y métricas en Sentry ([003] R-25, P-01 aprobado el 21/11/2026).

Se activa **solo** si ``QUINI6_SENTRY_DSN`` tiene valor (producción); sin DSN no se importa nada ni
se envía nada. Configuración de R-25: sin datos personales (``send_default_pii=False``), 10 % de las
trazas y un filtro (``filtrar_evento``) que quita correos, cookies, cabeceras de autenticación y los
cuerpos de los formularios antes de enviar cada evento (NFR-008).
"""

from __future__ import annotations

import re
from typing import Any

CORREO = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
OCULTO = "[filtrado]"
_CABECERAS_SENSIBLES = {"cookie", "authorization", "x-csrftoken", "set-cookie", "idempotency-key"}


def _sin_correos(valor: Any) -> Any:
    if isinstance(valor, str):
        return CORREO.sub(OCULTO, valor)
    if isinstance(valor, dict):
        return {k: _sin_correos(v) for k, v in valor.items()}
    if isinstance(valor, list | tuple):
        return [_sin_correos(v) for v in valor]
    return valor


def filtrar_evento(evento: dict, _pista: dict | None = None) -> dict:
    """``before_send``: el evento sin datos personales ni contenidos de formularios."""
    pedido = evento.get("request")
    if isinstance(pedido, dict):
        pedido.pop("cookies", None)
        pedido.pop("data", None)  # cuerpos de formularios y de la API
        pedido.pop("query_string", None)
        cabeceras = pedido.get("headers")
        if isinstance(cabeceras, dict):
            pedido["headers"] = {
                k: v for k, v in cabeceras.items() if k.lower() not in _CABECERAS_SENSIBLES
            }
    evento.pop("user", None)
    return _sin_correos(evento)


def iniciar_sentry(dsn: str, entorno: str = "produccion") -> None:
    import sentry_sdk  # solo con DSN: dependencia opcional del extra "prod"

    sentry_sdk.init(
        dsn=dsn,
        environment=entorno,
        send_default_pii=False,
        traces_sample_rate=0.1,
        before_send=filtrar_evento,
    )
