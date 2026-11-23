"""Operaciones de sesión y cuentas de la API v1 ([003] contracts/api.md § 2)."""

from datetime import datetime

from django.contrib.auth import login, logout
from django.http import HttpResponse, QueryDict
from django.middleware.csrf import get_token
from django.utils import timezone
from ninja import Router, Schema, Status

from cuentas import servicios
from cuentas.forms import IngresoForm, RegistroForm
from dominio.mensajes import MENSAJES
from quini6 import formulario_pendiente, idempotencia
from quini6.api_base import ProblemaAPI, error_de_campo, nivel

router = Router(tags=["Sesión y cuentas"])


class Sesion(Schema):
    """DTO ``Sesion`` ([003] data-model § 5)."""

    correo: str | None
    es_administrador: bool
    vence_en: datetime | None


@router.get("/sesion/", response=Sesion)
@nivel("P", sin_cache=True)
def consultar_sesion(request):
    """Sesión actual; fija la cookie ``csrftoken`` para las mutaciones siguientes."""
    get_token(request)
    usuario = request.user
    if not usuario.is_authenticated:
        return {"correo": None, "es_administrador": False, "vence_en": None}
    return {
        "correo": usuario.email,
        "es_administrador": bool(getattr(usuario, "es_administrador", False)),
        "vence_en": request.session.get_expiry_date(),
    }


# -- Ingresar, salir y crear cuenta (pantalla 5, T199) ------------------------------------------

_CLAVE_DE_TEXTO = {texto: clave for clave, texto in MENSAJES.items()}
#: Campo de la API ← campo de los formularios de Django.
_CAMPOS = {"email": "correo", "password": "contrasena", "__all__": ""}


class Reanudar(Schema):
    ruta: str
    campos: dict[str, list[str]]


class SesionIniciada(Sesion):
    reanudar: Reanudar | None = None


class Ingreso(Schema):
    correo: str = ""
    contrasena: str = ""
    pendiente: str | None = None


class NuevaCuenta(Schema):
    correo: str = ""
    contrasena: str = ""
    contrasena_repetida: str | None = None  # el formulario de [001] no la pide: se ignora


def _datos_sesion(request) -> dict:
    get_token(request)  # login() rota el token CSRF: el nuevo vuelve en Set-Cookie
    usuario = request.user
    return {
        "correo": usuario.email,
        "es_administrador": bool(getattr(usuario, "es_administrador", False)),
        "vence_en": request.session.get_expiry_date(),
    }


def _invalido(form) -> ProblemaAPI:
    errores = [
        {
            "campo": _CAMPOS.get(campo, campo),
            "codigo": _CLAVE_DE_TEXTO.get(str(texto), "api.dato_invalido"),
            "mensaje": str(texto),
        }
        for campo, lista in form.errors.items()
        for texto in lista
    ]
    return ProblemaAPI(422, "api.detalle_validacion", tipo="validacion", errores=errores)


def _formulario(form_clase, correo: str, contrasena: str):
    datos = QueryDict(mutable=True)
    datos["email"] = correo
    datos["password"] = contrasena
    return form_clase(datos)


@router.post("/sesion/", response=SesionIniciada)
@nivel("P", sin_cache=True)
def ingresar(request, datos: Ingreso):
    """[001] AC-3.4 a AC-3.7, R-04 (bloqueo); [003] FR-020, R-12. Los mismos servicios y mensajes
    que la vista HTML: credenciales incorrectas sin revelar si el correo existe; con un
    ``pendiente`` válido, devuelve lo escrito para reabrir ese formulario (sin enviarlo)."""
    form = _formulario(IngresoForm, datos.correo, datos.contrasena)
    if not form.is_valid():
        raise _invalido(form)
    ingreso = servicios.ingresar(request, form.cleaned_data["email"], form.cleaned_data["password"])
    if ingreso.resultado == "BLOQUEADO":
        hora = timezone.localtime(ingreso.hasta).strftime("%H:%M")
        raise ProblemaAPI(422, "cuenta.bloqueada", tipo="validacion", valores={"hora": hora})
    if not ingreso.ok:
        raise ProblemaAPI(422, "cuenta.credenciales_incorrectas", tipo="validacion")
    contenido = formulario_pendiente.contenido(datos.pendiente)
    reanudar = {"ruta": contenido[0], "campos": contenido[1]} if contenido else None
    return {**_datos_sesion(request), "reanudar": reanudar}


@router.delete("/sesion/")
@nivel("U")
def salir(request):
    """[001] AC-3.8: cierra la sesión (Django borra la cookie)."""
    logout(request)
    return HttpResponse(status=204)


@router.post("/cuentas/", response={201: Sesion})
@nivel("P", sin_cache=True)
def crear_cuenta(request, datos: NuevaCuenta):
    """[001] AC-3.1 a AC-3.3. ⟳ ``Idempotency-Key``. Crea la cuenta e ingresa (como la vista
    HTML)."""
    clave, anterior = idempotencia.anterior_api(request, "cuenta.crear")
    if anterior is not None and request.user.is_authenticated:
        return Status(201, _datos_sesion(request))
    form = _formulario(RegistroForm, datos.correo, datos.contrasena)
    if not form.is_valid():
        raise _invalido(form)
    resultado = servicios.registrar(form.cleaned_data["email"], form.cleaned_data["password"])
    if isinstance(resultado, servicios.ErrorRegistro):
        raise ProblemaAPI(
            422,
            "cuenta.correo_existente",
            tipo="validacion",
            errores=[error_de_campo("correo", "cuenta.correo_existente")],
        )
    login(request, resultado, backend="django.contrib.auth.backends.ModelBackend")
    if clave is not None:
        idempotencia.registrar(request, clave, "cuenta.crear", str(resultado.pk))
    return Status(201, _datos_sesion(request))
