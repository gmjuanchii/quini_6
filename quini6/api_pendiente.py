"""Formulario pendiente en la API v1 ([003] contracts/api.md § "Formulario pendiente", R-12,
AC-14.4).

Cuando "Volver al formulario" de Django envía el token a una ruta de Next.js, Next.js lo pasa aquí:
Django verifica la firma, la vigencia (60 min) y que la ruta sea la pedida, y devuelve lo escrito
para que la página muestre su formulario precargado **sin enviarlo**. No registra nada ni guarda el
token (NFR-008).
"""

from ninja import Router, Schema

from quini6 import formulario_pendiente
from quini6.api_base import ProblemaAPI, error_de_campo, nivel

router = Router(tags=["Formulario pendiente"])


class PedidoPendiente(Schema):
    pendiente: str
    ruta: str


class FormularioPendiente(Schema):
    ruta: str
    campos: dict[str, list[str]]


@router.post("/formularios/pendiente/", response=FormularioPendiente)
@nivel("U")
def leer_pendiente(request, datos: PedidoPendiente):
    contenido = formulario_pendiente.contenido(datos.pendiente)
    if contenido is None or contenido[0] != datos.ruta:
        raise ProblemaAPI(
            422,
            "api.detalle_validacion",
            tipo="validacion",
            errores=[error_de_campo("pendiente", "api.dato_invalido")],
        )
    ruta, campos = contenido
    return {"ruta": ruta, "campos": campos}
