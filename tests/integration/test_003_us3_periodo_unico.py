"""[003] RN-03, AC-3.5, R-09: no se inicia una extracción idéntica a otra en curso."""

from datetime import date

import pytest
from django.db import IntegrityError, connection
from django.db.migrations.executor import MigrationExecutor

from dominio.mensajes import mensaje
from extracciones import servicios
from extracciones.models import Extraccion
from tests.extraccion_estados import crear_extraccion
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
HOY = date(2026, 11, 19)


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


@pytest.fixture
def otra_admin(db):
    return crear_usuario("otra-admin@prueba.local", admin=True)


def test_mismo_periodo_en_curso_de_otra_cuenta_no_se_crea(cliente_admin, otra_admin):
    existente = crear_extraccion(
        otra_admin, "en-curso", desde=date(2026, 1, 1), hasta=date(2026, 6, 30)
    )
    respuesta = cliente_admin.post(INICIO, {"inicio": "01/01/2026", "fin": "30/06/2026"})
    html = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert mensaje("ext.periodo_en_curso", desde="01/01/2026", hasta="30/06/2026") in html
    assert f'href="{INICIO}{existente.pk}/"' in html
    assert mensaje("ext.ver_existente") in html
    assert Extraccion.objects.count() == 1


def test_periodo_que_se_superpone_en_parte_si_se_inicia(cliente_admin, otra_admin):
    crear_extraccion(otra_admin, "en-curso", desde=date(2026, 3, 1), hasta=date(2026, 9, 30))
    respuesta = cliente_admin.post(INICIO, {"inicio": "01/01/2026", "fin": "30/06/2026"})
    assert respuesta.status_code == 303
    assert Extraccion.objects.count() == 2


def test_mismo_periodo_terminado_si_se_inicia(cliente_admin, otra_admin):
    crear_extraccion(otra_admin, "finalizada", desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
    respuesta = cliente_admin.post(INICIO, {"inicio": "01/01/2026", "fin": "30/06/2026"})
    assert respuesta.status_code == 303


def test_la_misma_cuenta_sigue_viendo_la_suya(cliente_admin, admin):
    """[002] AC-1.11 sin cambios: con una en curso propia no se inicia otra."""
    propia = crear_extraccion(admin, "en-curso", desde=date(2026, 2, 1), hasta=date(2026, 2, 28))
    respuesta = cliente_admin.post(INICIO, {"inicio": "01/01/2026", "fin": "30/06/2026"})
    assert respuesta.status_code == 303
    assert respuesta["Location"] == f"{INICIO}{propia.pk}/"


def test_la_carrera_entre_dos_cuentas_se_informa_igual(admin, otra_admin, monkeypatch):
    from dominio.extraccion.periodo import Periodo

    crear_extraccion(otra_admin, "en-curso", desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
    # Simula que la verificación previa no vio la otra (carrera): decide la restricción.
    monkeypatch.setattr(servicios, "_extraccion_identica_en_curso", lambda periodo: None)
    resultado = servicios.iniciar_extraccion(admin, Periodo(date(2026, 1, 1), date(2026, 6, 30)))
    assert isinstance(resultado, servicios.ErrorInicio)
    assert resultado.clave == "ext.periodo_en_curso"
    assert resultado.existente is not None


def test_la_restriccion_existe_en_la_base(admin, otra_admin):
    crear_extraccion(otra_admin, "en-curso", desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
    with pytest.raises(IntegrityError):
        crear_extraccion(admin, "en-curso", desde=date(2026, 1, 1), hasta=date(2026, 6, 30))


@pytest.mark.django_db(transaction=True)
def test_la_migracion_0003_se_aplica_y_se_revierte():
    executor = MigrationExecutor(connection)
    executor.migrate([("extracciones", "0002_resultado_no_requerida")])
    executor.loader.build_graph()
    executor.migrate([("extracciones", "0003_extraccion_periodo_unico_en_curso")])
