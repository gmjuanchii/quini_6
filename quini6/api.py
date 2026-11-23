"""API v1 de QUINI_6 montada en /api/v1/ ([003] R-16, contracts/api.md).

Cada pantalla agrega su router cuando se migra (contrato primero, R-32) y sus filas a
tests/api/test_matriz_acceso_api.py.
"""

from cuentas.api import router as router_cuentas
from estadisticas.api import router as router_estadisticas
from extracciones.api import router as router_extracciones
from jugadas.api import router as router_jugadas
from quini6.api_avisos import router as router_avisos
from quini6.api_base import ProblemaAPI, crear_api, error_de_campo, nivel, problema
from quini6.api_pendiente import router as router_pendiente
from quini6.api_periodos import router as router_periodos
from resultados.api import router as router_resultados
from resultados.api_admin import router as router_admin_sorteos

__all__ = ["api", "crear_api", "nivel", "problema", "ProblemaAPI", "error_de_campo"]

api = crear_api()
api.add_router("", router_cuentas)
api.add_router("", router_avisos)  # [003] R-31
api.add_router("", router_periodos)  # [003] pantallas 1 y 2
api.add_router("", router_extracciones)  # [003] pantalla 1 (T174)
api.add_router("", router_estadisticas)  # [003] pantalla 2 (T183)
api.add_router("", router_jugadas)  # [003] pantalla 3 (T189)
api.add_router("", router_pendiente)  # [003] R-12, AC-14.4
api.add_router("", router_resultados)  # [003] pantalla 4 (T195)
api.add_router("", router_admin_sorteos)  # [003] pantalla 6 (T207)
