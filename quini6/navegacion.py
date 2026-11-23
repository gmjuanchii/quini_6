"""Sección activa del encabezado ([003] FR-014, AC-5.1): la decide el servidor por la dirección."""

#: Prefijo de la dirección → sección. Las rutas de administración (sorteos y extracción histórica)
#: pertenecen a "Administración"; la portada y la búsqueda, a "Resultados".
_SECCIONES = (
    ("/estadisticas/", "estadisticas"),
    ("/mis-jugadas/", "jugadas"),
    ("/administracion/", "administracion"),
    ("/resultados/", "resultados"),
)


def seccion_de(ruta: str) -> str | None:
    if ruta == "/":
        return "resultados"
    for prefijo, seccion in _SECCIONES:
        if ruta.startswith(prefijo):
            return seccion
    return None


def navegacion(request) -> dict:
    """Procesador de contexto: ``seccion_activa`` para marcar el enlace con ``aria-current``."""
    return {"seccion_activa": seccion_de(request.path)}
