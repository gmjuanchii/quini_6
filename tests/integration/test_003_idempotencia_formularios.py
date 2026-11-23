"""[003] FR-031, R-11: un reintento con la misma clave no duplica el efecto (registrar y eliminar
jugada, crear cuenta, crear sorteo) y lleva al mismo destino."""

import re
from datetime import date
from decimal import Decimal

import pytest

from cuentas.models import Usuario
from jugadas.models import Jugada
from quini6.idempotencia import nueva_clave
from resultados.models import Concurso
from tests.fabricas import crear_concurso

pytestmark = pytest.mark.django_db


def _dos_veces(cliente, ruta, datos):
    datos = {**datos, "clave_idempotencia": nueva_clave()}
    primera = cliente.post(ruta, datos)
    segunda = cliente.post(ruta, datos)
    assert primera.status_code in (302, 303) and segunda.status_code == 303
    assert primera["Location"] == segunda["Location"]
    return primera, segunda


def test_registrar_jugada(cliente_a):
    crear_concurso(9001, date(2099, 3, 2))
    datos = {"concurso": "9001", "numeros": ["03", "08", "14", "21", "32", "40"], "costo": "100"}
    _dos_veces(cliente_a, "/mis-jugadas/nueva/", datos)
    assert Jugada.objects.count() == 1


def test_eliminar_jugada(cliente_a, usuario_a):
    concurso = crear_concurso(9001, date(2099, 3, 2))
    jugada = Jugada(usuario=usuario_a, concurso=concurso, costo=Decimal("100"))
    jugada.asignar_numeros((1, 2, 3, 4, 5, 6))
    jugada.save()
    _dos_veces(cliente_a, f"/mis-jugadas/{jugada.pk}/eliminar/", {})
    assert not Jugada.objects.exists()


def test_crear_cuenta(client):
    datos = {"email": "nueva@prueba.local", "password": "clave-segura-123"}
    _dos_veces(client, "/registrarse/", datos)
    assert Usuario.objects.filter(email="nueva@prueba.local").count() == 1


def test_crear_sorteo(cliente_admin):
    datos = {"numero": "3300", "fecha_sorteo": "2025-03-02", "modalidades": ["PRIMER_SORTEO"]}
    _dos_veces(cliente_admin, "/administracion/concursos/nuevo/", datos)
    assert Concurso.objects.filter(numero=3300).count() == 1


@pytest.mark.parametrize(
    ("ruta", "perfil"),
    [
        ("/mis-jugadas/nueva/", "cliente_a"),
        ("/registrarse/", "client"),
        ("/administracion/concursos/nuevo/", "cliente_admin"),
    ],
)
def test_los_formularios_traen_su_clave(request, ruta, perfil):
    contenido = request.getfixturevalue(perfil).get(ruta).content.decode()
    assert re.search(
        r'<input type="hidden" name="clave_idempotencia" value="[0-9a-f-]{36}">', contenido
    )
