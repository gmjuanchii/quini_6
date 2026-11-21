"""[002] Historia 6: matriz de acceso de las cinco rutas (T060; AC-6.1, AC-6.2, AC-6.6, SC-005,
NFR-004). Mismo estilo que ``tests/integration/test_matriz_acceso.py``."""

from datetime import date

import pytest
from django.test import Client
from django.utils import timezone

from dominio.extraccion.clasificacion import aplicar_clasificacion
from dominio.extraccion.consolidacion import modalidades_no_informadas
from dominio.extraccion.tipos import NO_DISPONIBLE_CONSOLIDADO, SorteoConsolidado
from extracciones.models import Extraccion, SorteoExtraido
from extracciones.serializacion import sorteo_a_json
from tests.fabricas import CLAVE, crear_usuario

pytestmark = pytest.mark.django_db

SIN_PERMISO = "No tenés permisos para acceder a esta sección"
A = "/administracion/extracciones"


@pytest.fixture
def extraccion(admin):
    e = Extraccion.objects.create(
        creada_por=admin,
        desde=date(2026, 11, 1),
        hasta=date(2026, 11, 15),
        estado="FINALIZADA",
        iniciada_en=timezone.now(),
        finalizada_en=timezone.now(),
        numero_desde=3422,
        numero_hasta=3422,
        resumen={"identificados": 1, "por_estado": {"RECUPERADO": 1}, "fuentes": []},
        archivo_csv="version_contrato\r\n1.0\r\n",
        nombre_archivo="quini6-extraccion-1-2026-11-01-a-2026-11-15.csv",
        version_contrato="1.0",
    )
    SorteoExtraido.objects.create(
        extraccion=e,
        numero=3422,
        estado="NO_RECUPERADO",
        consolidado=sorteo_a_json(
            aplicar_clasificacion(
                SorteoConsolidado(
                    numero=3422,
                    fecha=NO_DISPONIBLE_CONSOLIDADO,
                    modalidades=modalidades_no_informadas(),
                    error_inesperado=True,
                )
            )
        ),
        procesado_en=timezone.now(),
    )
    return e


def rutas(e):
    return [
        ("GET", f"{A}/"),
        ("POST", f"{A}/"),
        ("GET", f"{A}/{e.pk}/"),
        ("GET", f"{A}/{e.pk}/sorteos/3422/"),
        ("GET", f"{A}/{e.pk}/csv/"),
        ("GET", f"{A}/{e.pk}/eliminar/"),  # D-24
        ("POST", f"{A}/{e.pk}/eliminar/"),  # D-24: al final, porque elimina la extracción
    ]


DATOS = {"inicio": "01/11/2026", "fin": "15/11/2026"}


def pedir(cliente, metodo, ruta):
    return cliente.post(ruta, DATOS) if metodo == "POST" else cliente.get(ruta)


def test_visitante_es_llevado_a_ingresar(extraccion):
    visitante = Client()
    for metodo, ruta in rutas(extraccion):
        respuesta = pedir(visitante, metodo, ruta)
        assert respuesta.status_code == 302, ruta
        assert respuesta["Location"].startswith("/ingresar/?next=")
        assert respuesta["Cache-Control"] == "no-store"


def test_usuario_sin_permiso_403_sin_datos(extraccion, usuario_a):
    cliente = Client()
    cliente.force_login(usuario_a)
    total = Extraccion.objects.count()
    for metodo, ruta in rutas(extraccion):
        respuesta = pedir(cliente, metodo, ruta)
        assert respuesta.status_code == 403, ruta
        texto = respuesta.content.decode()
        assert SIN_PERMISO in texto
        assert "Extracciones anteriores" not in texto and "3422" not in texto
        assert "version_contrato" not in texto
        assert respuesta["Cache-Control"] == "no-store"
    assert Extraccion.objects.count() == total  # no se generó información


def test_ac_6_2_visitante_que_inicia_sesion_sin_permiso(extraccion, usuario_a):
    cliente = Client()
    destino = cliente.get(f"{A}/{extraccion.pk}/")["Location"]
    respuesta = cliente.post(
        destino, {"username": usuario_a.email, "email": usuario_a.email, "password": CLAVE},
        follow=True,
    )  # fmt: skip
    assert respuesta.status_code == 403
    assert SIN_PERMISO in respuesta.content.decode()


def test_administrador_accede_a_todo(extraccion, cliente_admin):
    esperados = {f"{A}/": 200, f"{A}/{extraccion.pk}/": 200, f"{A}/{extraccion.pk}/csv/": 200,
                 f"{A}/{extraccion.pk}/sorteos/3422/": 200,
                 f"{A}/{extraccion.pk}/eliminar/": 200}  # fmt: skip
    for metodo, ruta in rutas(extraccion):
        respuesta = pedir(cliente_admin, metodo, ruta)
        assert respuesta["Cache-Control"] == "no-store"
        if metodo == "POST":
            assert respuesta.status_code == 303
        else:
            assert respuesta.status_code == esperados[ruta], ruta


def test_post_sin_token_csrf_se_rechaza(admin):
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(admin)
    assert cliente.post(f"{A}/", DATOS).status_code == 403
    assert Extraccion.objects.count() == 0


def test_sc_005_ningun_acceso_no_autorizado_pasa(extraccion):
    usuarios = [None, crear_usuario("comun@prueba.local")]
    rechazados = 0
    intentos = 0
    for usuario in usuarios:
        cliente = Client()
        if usuario:
            cliente.force_login(usuario)
        for metodo, ruta in rutas(extraccion):
            intentos += 1
            rechazados += pedir(cliente, metodo, ruta).status_code in (302, 403)
    assert rechazados == intentos
