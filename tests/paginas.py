"""Ayudantes para comparar páginas en las pruebas de acceso ([003] R-14, FR-032)."""

import re

from django.urls import resolve

from dominio.mensajes import MENSAJES


def sin_variables(contenido: str) -> str:
    """La página sin lo que cambia en cada respuesta y no revela ningún dato: el token CSRF
    (enmascarado al azar) y la dirección pedida, que el selector de tema del pie usa para volver."""
    contenido = re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", contenido)
    return re.sub(r'name="next" value="[^"]+"', "", contenido)


def es_reanudable(ruta: str) -> bool:
    return bool(getattr(resolve(ruta).func, "reanudable", None))


def es_ingreso_con_pendiente(respuesta) -> bool:
    """ "Ingresar" con lo escrito firmado tras un POST sin sesión ([003] FR-032): no da acceso."""
    contenido = respuesta.content.decode()
    return (
        respuesta.status_code == 200
        and 'name="pendiente"' in contenido
        and MENSAJES["cuenta.sesion_vencida"] in contenido
    )
