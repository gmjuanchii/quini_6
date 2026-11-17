"""Registro e ingreso con bloqueo por intentos fallidos (R-04, NFR-005)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.contrib.auth import login
from django.db import IntegrityError, transaction
from django.utils import timezone

from cuentas.models import Usuario, UsuarioManager

MAX_INTENTOS = 5
DURACION_BLOQUEO = timedelta(minutes=15)


@dataclass(frozen=True)
class ErrorRegistro:
    codigo: str  # CORREO_EXISTENTE


@dataclass(frozen=True)
class Ingreso:
    resultado: str  # OK, CREDENCIALES_INCORRECTAS o BLOQUEADO
    hasta: datetime | None = None

    @property
    def ok(self) -> bool:
        return self.resultado == "OK"


def registrar(email: str, password: str) -> Usuario | ErrorRegistro:
    email = UsuarioManager.normalizar(email)
    if Usuario.objects.filter(email=email).exists():
        return ErrorRegistro("CORREO_EXISTENTE")
    try:
        with transaction.atomic():
            return Usuario.objects.create_user(email=email, password=password)
    except IntegrityError:
        return ErrorRegistro("CORREO_EXISTENTE")


def ingresar(request, email: str, password: str) -> Ingreso:
    email = UsuarioManager.normalizar(email)
    ahora = timezone.now()
    with transaction.atomic():
        usuario = Usuario.objects.select_for_update().filter(email=email).first()
        if usuario is None:
            # Se calcula un hash igual para no revelar por el tiempo si la cuenta existe.
            Usuario().set_password(password)
            return Ingreso("CREDENCIALES_INCORRECTAS")
        if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
            return Ingreso("BLOQUEADO", usuario.bloqueado_hasta)
        if not usuario.check_password(password) or not usuario.is_active:
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= MAX_INTENTOS:
                usuario.bloqueado_hasta = ahora + DURACION_BLOQUEO
                usuario.intentos_fallidos = 0
            usuario.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
            return Ingreso("CREDENCIALES_INCORRECTAS")
        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario.save(update_fields=["intentos_fallidos", "bloqueado_hasta"])
    login(request, usuario, backend="django.contrib.auth.backends.ModelBackend")
    return Ingreso("OK")
