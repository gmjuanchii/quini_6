"""US7 — Corregir información publicada con trazabilidad (AC-7.1 a AC-7.6, AC-5.9, SC-008)."""

from datetime import date
from decimal import Decimal

import pytest

from dominio.tipos import Modalidad
from jugadas.models import Jugada
from resultados import servicios
from resultados.models import (
    Accion,
    EstadoVersion,
    ModalidadConcurso,
    RegistroCambio,
    VersionNumeros,
)
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

PS, LS = Modalidad.PRIMER_SORTEO, Modalidad.LA_SEGUNDA
BASE = "/administracion/concursos/1/primer-sorteo/numeros"
ORIGINAL = frozenset({3, 8, 14, 21, 32, 40})
SIN_PERMISO = "No tenés permisos para acceder a esta sección"


@pytest.fixture
def concurso(db):
    c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS, LS])
    cargar_numeros(c, PS, ORIGINAL, publicada_en=date(2025, 3, 3))
    return c


def _mc(modalidad=PS):
    return ModalidadConcurso.objects.get(concurso__numero=1, modalidad=modalidad.value)


def _corregir(cliente, nuevos=("03", "08", "14", "21", "32", "41"), publicar=True):
    cliente.post(
        f"{BASE}/corregir/",
        {
            "motivo": "El extracto dice 41",
            "fuente_descripcion": "Extracto oficial corregido",
            "fuente_fecha_consulta": "05/03/2025",
        },
    )
    datos = {f"n{i}": v for i, v in enumerate(nuevos, start=1)}
    datos.update(
        {
            "fuente_descripcion": "Extracto oficial corregido",
            "fuente_fecha_consulta": "05/03/2025",
            "motivo_correccion": "El extracto dice 41",
        }
    )
    cliente.post(f"{BASE}/", datos)
    if publicar:
        cliente.post(f"{BASE}/publicar/", {"cotejo": "on"})


class TestRevision:
    def test_ac_7_1_marcar(self, cliente_admin, client, concurso):
        cliente_admin.post(f"{BASE}/revision/", {"motivo": ""})
        assert _mc().numeros_en_revision is False
        cliente_admin.post(f"{BASE}/revision/", {"motivo": "Posible error en el 40"})
        assert _mc().numeros_en_revision is True
        assert RegistroCambio.objects.filter(accion=Accion.MARCAR_REVISION).exists()
        publico = client.get("/resultados/1/").content.decode()
        assert "Información en revisión" in publico
        assert ">40<" in publico

    def test_solo_bloques_publicados(self, cliente_admin, admin, concurso):
        cargar_numeros(concurso, LS, frozenset({1, 2, 3, 4, 5, 6}), estado="BORRADOR")
        cliente_admin.post(
            "/administracion/concursos/1/la-segunda/numeros/revision/", {"motivo": "x"}
        )
        cliente_admin.post(
            "/administracion/concursos/1/la-segunda/premios/revision/", {"motivo": "x"}
        )
        assert _mc(LS).numeros_en_revision is False
        assert _mc(LS).premios_en_revision is False
        with pytest.raises(servicios.ErrorResultados):
            servicios.marcar_revision(admin, _mc(LS), "numeros", "x")
        with pytest.raises(servicios.ErrorResultados):
            servicios.marcar_revision(admin, _mc(PS), "premios", "x")
        assert not RegistroCambio.objects.filter(accion=Accion.MARCAR_REVISION).exists()

    def test_p01_quitar_revision(self, cliente_admin, client, concurso):
        cliente_admin.post(f"{BASE}/revision/", {"motivo": "Posible error"})
        cliente_admin.post(f"{BASE}/quitar-revision/", {"motivo": ""})
        assert _mc().numeros_en_revision is True
        cliente_admin.post(f"{BASE}/quitar-revision/", {"motivo": "Revisión cerrada sin cambios"})
        assert _mc().numeros_en_revision is False
        registro = RegistroCambio.objects.get(accion=Accion.QUITAR_REVISION)
        assert registro.motivo == "Revisión cerrada sin cambios"
        publico = client.get("/resultados/1/").content.decode()
        assert "Corregido el" not in publico
        assert "Información en revisión" not in publico


class TestCorreccion:
    def test_ac_7_2_exige_motivo_y_fuente(self, cliente_admin, concurso):
        cliente_admin.post(
            f"{BASE}/corregir/",
            {"motivo": "", "fuente_descripcion": "", "fuente_fecha_consulta": ""},
        )
        assert VersionNumeros.objects.count() == 1
        cliente_admin.post(
            f"{BASE}/corregir/",
            {"motivo": "x", "fuente_descripcion": "", "fuente_fecha_consulta": "05/03/2025"},
        )
        assert VersionNumeros.objects.count() == 1

    def test_ac_7_2_no_visible_hasta_publicar(
        self, cliente_admin, client, usuario_a, cliente_a, concurso
    ):
        jugada = Jugada(usuario=usuario_a, concurso=concurso, costo=Decimal("1"))
        jugada.asignar_numeros({3, 8, 14, 21, 32, 41})
        jugada.save(force_insert=True)
        _corregir(cliente_admin, publicar=False)
        trabajo = VersionNumeros.objects.get(estado=EstadoVersion.BORRADOR)
        assert trabajo.es_correccion and trabajo.numeros == frozenset({3, 8, 14, 21, 32, 41})
        publico = client.get("/resultados/1/").content.decode()
        assert ">40<" in publico and ">41<" not in publico
        detalle = cliente_a.get(f"/mis-jugadas/{jugada.id}/").content.decode()
        assert "Con premio — Segundo Premio" in detalle
        panel = cliente_admin.get("/administracion/concursos/1/").content.decode()
        assert "corrección en preparación" in panel

    def test_formulario_de_correccion_exige_motivo(self, cliente_admin, concurso):
        cliente_admin.post(
            f"{BASE}/corregir/",
            {"motivo": "m", "fuente_descripcion": "f", "fuente_fecha_consulta": "05/03/2025"},
        )
        r = cliente_admin.get(f"{BASE}/")
        assert "Motivo de la corrección" in r.content.decode()
        r = cliente_admin.post(
            f"{BASE}/",
            {
                "n1": "01",
                "n2": "02",
                "n3": "03",
                "n4": "04",
                "n5": "05",
                "n6": "06",
                "fuente_descripcion": "f",
                "fuente_fecha_consulta": "05/03/2025",
                "motivo_correccion": "",
            },
        )
        assert "Indicá el motivo de la corrección." in r.content.decode()

    def test_ac_7_4_publicada(self, cliente_admin, client, concurso):
        cliente_admin.post(f"{BASE}/revision/", {"motivo": "Posible error"})
        _corregir(cliente_admin)
        anterior = VersionNumeros.objects.get(estado=EstadoVersion.REEMPLAZADA)
        assert anterior.numeros == ORIGINAL and anterior.reemplazada_en is not None
        vigente = VersionNumeros.objects.get(estado=EstadoVersion.PUBLICADA)
        assert vigente.numeros == frozenset({3, 8, 14, 21, 32, 41})
        assert _mc().numeros_en_revision is False
        publico = client.get("/resultados/1/").content.decode()
        assert ">41<" in publico and ">40<" not in publico
        assert "Corregido el" in publico
        assert "Información en revisión" not in publico
        registro = RegistroCambio.objects.get(accion=Accion.PUBLICAR_CORRECCION)
        assert registro.valor_anterior == {"numeros": [3, 8, 14, 21, 32, 40]}
        assert registro.valor_nuevo == {"numeros": [3, 8, 14, 21, 32, 41]}
        assert registro.motivo == "El extracto dice 41"

    def test_ac_7_3_historial(self, cliente_admin, admin, concurso):
        _corregir(cliente_admin)
        contenido = cliente_admin.get("/administracion/concursos/1/historial/").content.decode()
        for texto in (
            "Publicar corrección",
            "03, 08, 14, 21, 32, 40",
            "03, 08, 14, 21, 32, 41",
            admin.email,
            "El extracto dice 41",
            "Extracto oficial corregido",
            "Iniciar corrección",
        ):
            assert texto in contenido

    def test_ac_7_5_y_5_9_comparacion_actualizada(
        self, cliente_admin, cliente_a, usuario_a, concurso
    ):
        afectada = Jugada(usuario=usuario_a, concurso=concurso, costo=Decimal("1"))
        afectada.asignar_numeros({3, 8, 14, 21, 32, 41})
        afectada.save()
        no_afectada = Jugada(usuario=usuario_a, concurso=concurso, costo=Decimal("1"))
        no_afectada.asignar_numeros({1, 2, 5, 6, 7, 9})
        no_afectada.save()
        _corregir(cliente_admin)
        detalle = cliente_a.get(f"/mis-jugadas/{afectada.id}/").content.decode()
        assert "Con premio — Primer Premio" in detalle
        assert "Actualizado por corrección del resultado oficial el" in detalle
        detalle = cliente_a.get(f"/mis-jugadas/{no_afectada.id}/").content.decode()
        assert "Actualizado por corrección del resultado oficial" not in detalle

    def test_premios_correccion(self, cliente_admin, admin, client, concurso):
        version = servicios.guardar_borrador_premios(
            admin,
            _mc(),
            {"PRIMER": {"ganadores": 1, "importe_individual": Decimal("100")}},
            fuente_descripcion="Extracto",
            fuente_fecha_consulta=date(2025, 3, 3),
        )
        servicios.publicar(admin, version, advertencias_confirmadas=True, cotejo_confirmado=True)
        url = "/administracion/concursos/1/primer-sorteo/premios"
        cliente_admin.post(
            f"{url}/corregir/",
            {
                "motivo": "Importe mal cargado",
                "fuente_descripcion": "Extracto",
                "fuente_fecha_consulta": "05/03/2025",
            },
        )
        cliente_admin.post(
            f"{url}/",
            {
                "PRIMER_ganadores": "1",
                "PRIMER_importe_individual": "250,00",
                "fuente_descripcion": "Extracto",
                "fuente_fecha_consulta": "05/03/2025",
                "motivo_correccion": "Importe mal cargado",
            },
        )
        cliente_admin.post(f"{url}/publicar/", {"cotejo": "on"})
        publico = client.get("/resultados/1/").content.decode()
        assert "$ 250,00" in publico and "$ 100,00" not in publico


class TestPermisos:
    @pytest.mark.parametrize("ruta", ["revision/", "quitar-revision/", "corregir/"])
    def test_ac_7_6_post_sin_permiso(self, cliente_a, concurso, ruta):
        r = cliente_a.post(
            f"{BASE}/{ruta}",
            {"motivo": "x", "fuente_descripcion": "x", "fuente_fecha_consulta": "05/03/2025"},
        )
        assert r.status_code == 403 and SIN_PERMISO in r.content.decode()
        assert VersionNumeros.objects.count() == 1
        assert _mc().numeros_en_revision is False
        assert not RegistroCambio.objects.exists()

    def test_ac_7_6_historial_sin_permiso(self, cliente_a, concurso):
        r = cliente_a.get("/administracion/concursos/1/historial/")
        assert r.status_code == 403 and SIN_PERMISO in r.content.decode()
