"""Cuenta de usuario (data-model.md, FR-015, NFR-005, RN-37, RN-39)."""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    @staticmethod
    def normalizar(email: str) -> str:
        return (email or "").strip().lower()

    def create_user(self, email: str, password: str | None = None, **extra):
        email = self.normalizar(email)
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def get_by_natural_key(self, email: str):
        return self.get(email=self.normalizar(email))


class Usuario(AbstractBaseUser):
    email = models.EmailField("correo electrónico", unique=True)
    es_administrador = models.BooleanField(default=False)
    fecha_alta = models.DateTimeField(default=timezone.now)
    intentos_fallidos = models.SmallIntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self) -> str:
        return self.email
