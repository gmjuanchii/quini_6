"""Qué aplicación atiende cada ruta mientras conviven Django y Next.js ([003] R-20).

Ver contracts/rutas.md § 3.

Los patrones son los mismos que lee el enrutador (``QUINI6_RUTAS_NEXT`` y
``QUINI6_RUTAS_NEXT_SIN_RESPALDO``, separados por espacio): una ruta exacta (``/estadisticas/``) o
con ``*`` al final (``/mis-jugadas/*``), como el comparador ``path`` de Caddy.
"""

from __future__ import annotations

from fnmatch import fnmatchcase

from django.conf import settings

#: Marca que agregan los formularios de Django para que el enrutador los entregue a Django (R-20).
MARCA_DJANGO = "_interfaz"
VALOR_MARCA_DJANGO = "django"


def es_de_next(ruta: str) -> bool:
    """``True`` si el enrutador entrega ``ruta`` a Next.js (con o sin respaldo de Django)."""
    patrones = [*settings.QUINI6_RUTAS_NEXT, *settings.QUINI6_RUTAS_NEXT_SIN_RESPALDO]
    return any(fnmatchcase(ruta, patron) for patron in patrones)
