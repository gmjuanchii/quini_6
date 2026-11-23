"""Constitución IV: CSRF, no-store, next validado, contraseñas hasheadas y errores sin detalles."""

from datetime import date

import pytest
from django.test import Client

from cuentas.models import Usuario
from dominio.mensajes import MENSAJES
from tests.fabricas import CLAVE, crear_concurso, crear_usuario

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "ruta",
    [
        "/ingresar/",
        "/registrarse/",
        "/salir/",
        "/mis-jugadas/nueva/",
        "/administracion/concursos/nuevo/",
    ],
)
def test_post_sin_csrf_rechazado(ruta):
    usuario = crear_usuario("admin@prueba.local", admin=True)
    crear_concurso(1, date(2025, 3, 2))
    cliente = Client(enforce_csrf_checks=True)
    if ruta not in ("/ingresar/", "/registrarse/"):
        cliente.force_login(usuario)
    r = cliente.post(
        ruta,
        {
            "email": "x@prueba.local",
            "password": "12345678",
            "numero": "2",
            "fecha_sorteo": "02/03/2025",
            "modalidades": ["PRIMER_SORTEO"],
        },
    )
    assert r.status_code == 403
    assert MENSAJES["gral.csrf_vencido"] in r.content.decode()
    assert Usuario.objects.count() == 1


def test_post_con_csrf_aceptado():
    crear_usuario("ana@prueba.local")
    cliente = Client(enforce_csrf_checks=True)
    cliente.get("/ingresar/")
    token = cliente.cookies["csrftoken"].value
    r = cliente.post(
        "/ingresar/", {"email": "ana@prueba.local", "password": CLAVE, "csrfmiddlewaretoken": token}
    )
    assert r.status_code == 302


@pytest.mark.parametrize(
    "ruta",
    [
        "/mis-jugadas/",
        "/mis-jugadas/nueva/",
        "/administracion/concursos/",
        "/administracion/concursos/1/",
        "/ingresar/",
        "/registrarse/",
    ],
)
def test_no_store(cliente_admin, ruta):
    crear_concurso(1, date(2025, 3, 2))
    r = cliente_admin.get(ruta)
    assert r["Cache-Control"] == "no-store"


def test_no_store_en_403(cliente_a):
    r = cliente_a.get("/administracion/concursos/")
    assert r.status_code == 403 and r["Cache-Control"] == "no-store"


@pytest.mark.parametrize("externo", ["https://otro.sitio/", "//otro.sitio/", "http://otro.sitio"])
def test_next_externo(client, externo):
    crear_usuario("ana@prueba.local")
    r = client.post("/ingresar/", {"email": "ana@prueba.local", "password": CLAVE, "next": externo})
    assert r["Location"] == "/mis-jugadas/"


def test_contrasenas_hasheadas(client):
    client.post("/registrarse/", {"email": "n@prueba.local", "password": "secreta-123"})
    usuario = Usuario.objects.get()
    assert usuario.password != "secreta-123"
    assert usuario.password.startswith(("pbkdf2_", "argon2", "bcrypt", "scrypt"))
    assert usuario.check_password("secreta-123")


def test_error_500_sin_detalles(client, settings, monkeypatch):
    settings.DEBUG = False

    def falla():
        raise RuntimeError("detalle-tecnico-secreto")

    monkeypatch.setattr("resultados.views_publicas.consultas.ultimos_resultados", falla)
    client.raise_request_exception = False
    r = client.get("/resultados/")
    assert r.status_code == 500
    contenido = r.content.decode()
    assert MENSAJES["gral.error"] in contenido
    assert "detalle-tecnico-secreto" not in contenido
    assert "Traceback" not in contenido


def test_404_generico(client, settings):
    settings.DEBUG = False
    r = client.get("/no-existe/")
    assert r.status_code == 404
    assert MENSAJES["gral.pagina_inexistente"] in r.content.decode()


def test_sin_admin_de_django(client):
    assert client.get("/admin/").status_code == 404
