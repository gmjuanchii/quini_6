import pytest

from tests.fabricas import crear_usuario


@pytest.fixture(autouse=True)
def _almacenamiento_estatico_simple(settings):
    """Evita exigir ``collectstatic`` en las pruebas."""
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


@pytest.fixture
def usuario_a(db):
    return crear_usuario("ana@prueba.local")


@pytest.fixture
def usuario_b(db):
    return crear_usuario("beto@prueba.local")


@pytest.fixture
def admin(db):
    return crear_usuario("admin@prueba.local", admin=True)


@pytest.fixture
def cliente_a(client, usuario_a):
    client.force_login(usuario_a)
    return client


@pytest.fixture
def cliente_b(db, usuario_b):
    from django.test import Client

    cliente = Client()
    cliente.force_login(usuario_b)
    return cliente


@pytest.fixture
def cliente_admin(db, admin):
    from django.test import Client

    cliente = Client()
    cliente.force_login(admin)
    return cliente
