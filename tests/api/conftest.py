"""Clientes por perfil para las pruebas de la API v1 ([003] contracts/api.md § 4)."""

import pytest
from django.test import Client

from tests.fabricas import crear_usuario


def _cliente(usuario=None) -> Client:
    cliente = Client(enforce_csrf_checks=True)
    if usuario is not None:
        cliente.force_login(usuario)
    return cliente


@pytest.fixture
def visitante(db):
    return _cliente()


@pytest.fixture
def usuario(db):
    return _cliente(crear_usuario("usuaria@api.local"))


@pytest.fixture
def otro_usuario(db):
    return _cliente(crear_usuario("otra@api.local"))


@pytest.fixture
def administrador(db):
    return _cliente(crear_usuario("admin@api.local", admin=True))


def token_csrf(cliente: Client) -> str:
    """Obtiene la cookie ``csrftoken`` con ``GET /api/v1/sesion/`` (contracts/api.md § 1)."""
    cliente.get("/api/v1/sesion/")
    return cliente.cookies["csrftoken"].value
