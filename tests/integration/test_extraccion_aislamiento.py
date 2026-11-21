"""[002] Historia 6: nada extraído llega a los datos de la aplicación (T061; RN-41, AC-6.3 a
AC-6.5, SC-004)."""

import re
from datetime import date
from decimal import Decimal

import pytest
from django.apps import apps
from django.core import serializers

from dominio.extraccion.tipos import Fuente
from dominio.tipos import Modalidad
from jugadas.models import Jugada
from resultados.models import RegistroCambio
from tests.extraccion_falsos import HOY, cliente_con_sorteos, fichas_de, procesar_pendientes
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

SORTEOS = {
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
    3426: date(2026, 11, 15),
    3427: date(2026, 11, 18),
}


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


def pagina(cliente, ruta) -> str:
    """HTML de la página sin el token CSRF, que cambia en cada respuesta."""
    texto = cliente.get(ruta).content.decode()
    return re.sub(r'name="csrfmiddlewaretoken" value="[^"]+"', "", texto)


def foto_de_tablas() -> dict[str, str]:
    """Contenido completo de todas las tablas de resultados, jugadas y cuentas."""
    foto = {}
    for app in ("resultados", "jugadas", "cuentas"):
        for modelo in apps.get_app_config(app).get_models():
            filas = modelo.objects.order_by("pk")
            foto[modelo._meta.label] = serializers.serialize("json", filas)
    return foto


def test_sc_004_y_ac_6_3_a_6_5_la_extraccion_no_toca_la_aplicacion(cliente_admin, cliente_a):
    # 3425 publicado con números distintos de los que traen las fuentes (AC-6.4).
    concurso = crear_concurso(3425, date(2026, 11, 11))
    cargar_numeros(concurso, Modalidad.PRIMER_SORTEO, [3, 7, 11, 22, 33, 44])
    jugada = Jugada(usuario=cliente_a_usuario(cliente_a), concurso=concurso, costo=Decimal("100"))
    jugada.asignar_numeros([3, 7, 11, 22, 33, 44])
    jugada.save()

    publico_antes = pagina(cliente_a, "/resultados/3425/")
    jugada_antes = pagina(cliente_a, f"/mis-jugadas/{jugada.id}/")
    cambios_antes = RegistroCambio.objects.count()
    foto_antes = foto_de_tablas()

    cliente_admin.post(
        "/administracion/extracciones/", {"inicio": "08/11/2026", "fin": "18/11/2026"}
    )
    procesar_pendientes(
        cliente_con_sorteos(SORTEOS, fuentes=(Fuente.F2, Fuente.F3)),
        fichas_de(Fuente.F2, Fuente.F3),
    )

    # AC-6.3: el 3426 sigue sin existir en la aplicación.
    inexistente = cliente_a.get("/resultados/buscar/?numero=3426").content.decode()
    assert "No hay información del concurso N.º 3426" in inexistente
    assert "Concurso N.º 3426" not in pagina(cliente_admin, "/administracion/concursos/")
    # AC-6.4: el 3425 publicado se muestra igual, sin corrección ni revisión.
    publico_despues = pagina(cliente_a, "/resultados/3425/")
    assert publico_despues == publico_antes
    assert "Corregido el" not in publico_despues
    assert "Información en revisión" not in publico_despues
    assert RegistroCambio.objects.count() == cambios_antes
    # AC-6.5: la jugada y su comparación no cambian.
    assert pagina(cliente_a, f"/mis-jugadas/{jugada.id}/") == jugada_antes
    # SC-004: ninguna tabla de resultados, jugadas ni cuentas cambió.
    despues = foto_de_tablas()
    despues.pop("cuentas.Usuario")  # el inicio de sesión de las pruebas actualiza last_login
    antes = dict(foto_antes)
    antes.pop("cuentas.Usuario")
    assert despues == antes


def cliente_a_usuario(cliente):
    from django.contrib.auth import get_user

    return get_user(cliente)
