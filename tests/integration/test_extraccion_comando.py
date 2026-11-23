"""[002] Comando ``procesar_extracciones`` (T027; R-01, I-07, I-09, NFR-006, RN-33)."""

from datetime import date, timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from dominio.extraccion.tipos import Fuente
from extracciones import servicios
from extracciones.fuentes import f2
from extracciones.management.commands.procesar_extracciones import Command
from extracciones.models import Extraccion
from tests.extraccion_falsos import MOMENTO, cliente_con_sorteos, fichas_de
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

F2, F3 = Fuente.F2, Fuente.F3
SORTEOS = {
    3421: date(2026, 10, 28),
    3422: date(2026, 11, 1),
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
}


@pytest.fixture
def inyectar(monkeypatch):
    def _inyectar(cliente, fichas):
        monkeypatch.setattr(Command, "crear_cliente_y_fichas", lambda self: (cliente, fichas))

    return _inyectar


def crear(usuario, desde=date(2026, 11, 1), hasta=date(2026, 11, 11), minutos=0, **campos):
    return Extraccion.objects.create(
        creada_por=usuario,
        desde=desde,
        hasta=hasta,
        iniciada_en=timezone.now() + timedelta(minutes=minutos),
        **campos,
    )


def ejecutar() -> str:
    salida = StringIO()
    call_command("procesar_extracciones", "--una-vez", stdout=salida)
    return salida.getvalue()


def test_procesa_por_orden_de_inicio_e_imprime_una_linea_por_extraccion(admin, inyectar):
    otro = crear_usuario("admin2@prueba.local", admin=True)
    # [003] RN-03: dos extracciones en curso no pueden tener el mismo período.
    segunda = crear(admin, desde=date(2026, 11, 2), minutos=5)
    primera = crear(otro, minutos=0)
    inyectar(cliente_con_sorteos(SORTEOS), fichas_de(F2))
    salida = ejecutar().splitlines()
    assert salida == [
        f"Extracción {primera.pk}: iniciada",
        f"Extracción {primera.pk}: Extracción finalizada",
        f"Extracción {segunda.pk}: iniciada",
        f"Extracción {segunda.pk}: Extracción finalizada",
    ]


def test_i_07_reanuda_sin_duplicar_y_repite_el_sorteo_a_medias(admin, inyectar):
    cliente = cliente_con_sorteos(SORTEOS)
    extraccion = crear(admin, numero_desde=3422, numero_hasta=3425)
    estado = servicios._Estado(cliente, fichas_de(F2), servicios.INTERPRETES)
    servicios._leer_listados(estado)
    servicios.procesar_sorteo(extraccion, estado, 3422)
    servicios.procesar_sorteo(extraccion, estado, 3423)
    antes = {s.numero: s.procesado_en for s in extraccion.sorteos.all()}
    cliente.pedidas.clear()
    inyectar(cliente, fichas_de(F2))
    ejecutar()
    extraccion.refresh_from_db()
    assert extraccion.estado == "FINALIZADA"
    assert sorted(extraccion.sorteos.values_list("numero", flat=True)) == [3422, 3423, 3424, 3425]
    assert {s.numero: s.procesado_en for s in extraccion.sorteos.filter(numero__lt=3424)} == antes
    detalles = [u for u in cliente.pedidas if "/sorteos/" in u]
    assert detalles == [
        "https://numerosganadores.com.ar/sorteos/3424",
        "https://numerosganadores.com.ar/sorteos/3425",
    ]
    intento = extraccion.sorteos.get(numero=3424).intentos.get()
    assert intento.consultado_en == MOMENTO


def test_i_09_a_interprete_que_falla_deja_estructura_no_reconocida(admin, inyectar, monkeypatch):
    original = f2.interpretar_sorteo

    def con_falla(html):
        if "Número de sorteo: 3423" in html:
            raise ValueError("estructura rarísima")
        return original(html)

    monkeypatch.setattr(f2, "interpretar_sorteo", con_falla)
    crear(admin)
    inyectar(cliente_con_sorteos(SORTEOS, fuentes=(F2, F3)), fichas_de(F2, F3))
    ejecutar()
    sorteo = Extraccion.objects.get().sorteos.get(numero=3423)
    intento = sorteo.intentos.get(fuente="F2")
    assert intento.resultado == "ESTRUCTURA_NO_RECONOCIDA" and intento.datos is None
    assert intento.observaciones[0]["texto"] == "La página de la fuente no se pudo interpretar"
    assert sorteo.estado == "RECUPERADO"  # los datos se tomaron de F3
    assert sorteo.consolidado["fecha"]["fuentes"] == ["F3"]


def test_i_09_b_error_inesperado_deja_no_recuperado_y_la_extraccion_sigue(
    admin, inyectar, monkeypatch
):
    original = servicios.consolidar

    def con_falla(numero, intentos, fichas):
        if numero == 3423:
            raise RuntimeError("falla inesperada")
        return original(numero, intentos, fichas)

    monkeypatch.setattr(servicios, "consolidar", con_falla)
    crear(admin)
    inyectar(cliente_con_sorteos(SORTEOS), fichas_de(F2))
    ejecutar()
    extraccion = Extraccion.objects.get()
    sorteo = extraccion.sorteos.get(numero=3423)
    assert sorteo.estado == "NO_RECUPERADO"
    assert sorteo.consolidado["motivos"] == ["Error inesperado al procesar el sorteo"]
    assert sorteo.intentos.count() == 0  # sin datos de ninguna fuente
    assert extraccion.sorteos.count() == extraccion.total_identificados == 4
    assert sum(extraccion.resumen["por_estado"].values()) == 4
    assert extraccion.estado == "CON_ADVERTENCIAS"
