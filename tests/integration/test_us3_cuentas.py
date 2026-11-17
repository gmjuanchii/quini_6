"""US3 — Crear una cuenta y acceder a las funciones personales (AC-3.1 a AC-3.10)."""

from datetime import timedelta

import pytest
from django.contrib.sessions.models import Session
from django.utils import timezone

from cuentas.models import Usuario
from tests.fabricas import CLAVE, crear_usuario

pytestmark = pytest.mark.django_db

CORREO_EXISTENTE = "Ya existe una cuenta con este correo electrónico. Iniciá sesión."
CREDENCIALES = "Correo electrónico o contraseña incorrectos"


def _ingresar(client, email, password=CLAVE, next_=None):
    url = "/ingresar/" + (f"?next={next_}" if next_ else "")
    datos = {"email": email, "password": password}
    if next_:
        datos["next"] = next_
    return client.post(url, datos)


class TestRegistro:
    def test_ac_3_1_registro_valido(self, client):
        r = client.post("/registrarse/", {"email": "  Nueva@Prueba.Local ", "password": "12345678"})
        assert r.status_code == 302
        assert r["Location"] == "/mis-jugadas/"
        usuario = Usuario.objects.get()
        assert usuario.email == "nueva@prueba.local"
        assert usuario.es_administrador is False
        r = client.get("/mis-jugadas/")
        assert r.status_code == 200

    def test_ac_3_2_correo_invalido(self, client):
        r = client.post("/registrarse/", {"email": "no-es-correo", "password": "12345678"})
        assert r.status_code == 200
        assert "Ingresá un correo electrónico válido." in r.content.decode()
        assert not Usuario.objects.exists()

    def test_ac_3_2_contrasena_corta(self, client):
        r = client.post("/registrarse/", {"email": "a@prueba.local", "password": "1234567"})
        assert "La contraseña debe tener al menos 8 caracteres." in r.content.decode()
        assert not Usuario.objects.exists()

    def test_ac_3_3_correo_existente(self, client):
        crear_usuario("beto@prueba.local")
        r = client.post("/registrarse/", {"email": "BETO@prueba.local", "password": "12345678"})
        contenido = r.content.decode()
        assert CORREO_EXISTENTE in contenido
        assert 'href="/ingresar/' in contenido
        assert Usuario.objects.count() == 1


class TestIngreso:
    def test_ac_3_4_ingreso_correcto(self, client):
        crear_usuario("ana@prueba.local")
        r = _ingresar(client, "Ana@Prueba.local")
        assert r.status_code == 302
        assert r["Location"] == "/mis-jugadas/"
        assert client.get("/mis-jugadas/").status_code == 200

    @pytest.mark.parametrize(
        ("email", "password"),
        [("nadie@prueba.local", CLAVE), ("ana@prueba.local", "incorrecta")],
    )
    def test_ac_3_5_mismo_mensaje(self, client, email, password):
        crear_usuario("ana@prueba.local")
        r = _ingresar(client, email, password)
        assert r.status_code == 200
        assert CREDENCIALES in r.content.decode()

    def test_ac_3_6_bloqueo(self, client):
        usuario = crear_usuario("ana@prueba.local")
        for _ in range(5):
            r = _ingresar(client, "ana@prueba.local", "incorrecta")
            assert CREDENCIALES in r.content.decode()
        r = _ingresar(client, "ana@prueba.local")
        contenido = r.content.decode()
        usuario.refresh_from_db()
        hora = timezone.localtime(usuario.bloqueado_hasta).strftime("%H:%M")
        assert (
            "Por seguridad, bloqueamos el acceso por 15 minutos. "
            f"Podés volver a intentar a las {hora}."
        ) in contenido
        assert client.get("/mis-jugadas/").status_code == 302

        usuario.bloqueado_hasta = timezone.now() - timedelta(seconds=1)
        usuario.save()
        r = _ingresar(client, "ana@prueba.local")
        assert r.status_code == 302
        usuario.refresh_from_db()
        assert usuario.intentos_fallidos == 0
        assert usuario.bloqueado_hasta is None

    def test_ac_3_7_salir(self, cliente_a):
        r = cliente_a.get("/mis-jugadas/")
        assert r["Cache-Control"] == "no-store"
        r = cliente_a.post("/salir/")
        assert r.status_code == 302
        assert r["Location"] == "/resultados/"
        r = cliente_a.get("/mis-jugadas/")
        assert r.status_code == 302
        assert r["Location"] == "/ingresar/?next=/mis-jugadas/"

    def test_get_salir_no_cierra_sesion(self, cliente_a):
        r = cliente_a.get("/salir/")
        assert r.status_code == 405
        assert cliente_a.get("/mis-jugadas/").status_code == 200

    def test_ac_3_8_vuelve_a_la_ruta_pedida(self, client):
        crear_usuario("ana@prueba.local")
        r = _ingresar(client, "ana@prueba.local", next_="/mis-jugadas/nueva/")
        assert r["Location"] == "/mis-jugadas/nueva/"

    @pytest.mark.parametrize("externo", ["https://otro.sitio/", "//otro.sitio/"])
    def test_ac_3_8_next_externo_se_ignora(self, client, externo):
        crear_usuario("ana@prueba.local")
        r = _ingresar(client, "ana@prueba.local", next_=externo)
        assert r["Location"] == "/mis-jugadas/"

    def test_ac_3_9_next_se_conserva_entre_ingresar_y_registrarse(self, client):
        destino = "/mis-jugadas/nueva/?concurso=9001"
        r = client.get("/ingresar/", {"next": destino})
        contenido = r.content.decode()
        assert 'href="/registrarse/?next=/mis-jugadas/nueva/%3Fconcurso%3D9001"' in contenido
        assert 'value="/mis-jugadas/nueva/?concurso=9001"' in contenido
        r = client.get("/registrarse/", {"next": destino})
        assert 'href="/ingresar/?next=/mis-jugadas/nueva/%3Fconcurso%3D9001"' in r.content.decode()
        r = client.post(
            "/registrarse/", {"email": "n@prueba.local", "password": "12345678", "next": destino}
        )
        assert r["Location"] == destino

    def test_ac_3_10_sesion_vencida(self, client):
        crear_usuario("ana@prueba.local")
        _ingresar(client, "ana@prueba.local")
        assert client.get("/mis-jugadas/").status_code == 200
        Session.objects.update(expire_date=timezone.now() - timedelta(minutes=1))
        r = client.get("/mis-jugadas/")
        assert r.status_code == 302
        assert r["Location"].startswith("/ingresar/")


def test_sesion_vence_a_los_30_minutos(settings):
    assert settings.SESSION_COOKIE_AGE == 1800
    assert settings.SESSION_SAVE_EVERY_REQUEST is True
