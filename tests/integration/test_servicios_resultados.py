"""Servicios de resultados: concursos, borradores, observación, publicación y auditoría."""

from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from dominio.mensajes import mensaje
from dominio.tipos import ORDEN_MODALIDADES
from resultados import consultas, servicios
from resultados.models import (
    Accion,
    EstadoVersion,
    ModalidadConcurso,
    PremioCategoria,
    RegistroCambio,
    VersionNumeros,
)
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = ORDEN_MODALIDADES
SEIS = ["01", "02", "03", "04", "05", "06"]
HOY = date(2025, 3, 3)
FECHA = date(2025, 3, 2)


def _mc(concurso, modalidad):
    return ModalidadConcurso.objects.get(concurso=concurso, modalidad=modalidad.value)


def _borrador_numeros(admin, concurso, modalidad=PS, numeros=SEIS, fuente=True):
    return servicios.guardar_borrador_numeros(
        admin,
        _mc(concurso, modalidad),
        numeros,
        fuente_descripcion="Extracto oficial N.º 3215" if fuente else "",
        fuente_fecha_consulta=HOY if fuente else None,
    )


class TestConcurso:
    def test_crear_concurso(self, admin):
        c = servicios.crear_concurso(admin, 3215, FECHA, [PS, LS, RV])
        assert {mc.modalidad for mc in c.modalidades.all()} == {
            "PRIMER_SORTEO",
            "LA_SEGUNDA",
            "REVANCHA",
        }
        registro = RegistroCambio.objects.get(accion=Accion.CREAR_CONCURSO)
        assert registro.autor == admin
        assert registro.valor_nuevo["numero"] == 3215

    def test_duplicado(self, admin):
        servicios.crear_concurso(admin, 3215, FECHA, [PS])
        with pytest.raises(servicios.ConcursoDuplicado) as error:
            servicios.crear_concurso(admin, 3215, FECHA, [PS])
        assert error.value.mensajes == [mensaje("admin.concurso_duplicado", N=3215)]

    def test_sin_modalidades(self, admin):
        with pytest.raises(servicios.ErrorResultados):
            servicios.crear_concurso(admin, 1, FECHA, [])

    def test_p06_premio_extra_requiere_tres_extracciones(self, admin):
        with pytest.raises(servicios.ErrorResultados) as error:
            servicios.crear_concurso(admin, 1, FECHA, [PS, LS, PE])
        assert error.value.mensajes == [
            "Premio Extra requiere Primer Sorteo, La Segunda y Revancha"
        ]
        servicios.crear_concurso(admin, 1, FECHA, [PS, LS, RV, PE])

    def test_p05_modificar(self, admin):
        c = servicios.crear_concurso(admin, 1, FECHA, [PS, LS])
        servicios.modificar_concurso(admin, c, date(2025, 3, 5), [PS, LS, RV])
        c.refresh_from_db()
        assert c.fecha_sorteo == date(2025, 3, 5)
        registro = RegistroCambio.objects.get(accion=Accion.MODIFICAR_CONCURSO)
        assert registro.valor_anterior["fecha_sorteo"] == "2025-03-02"
        assert registro.valor_nuevo["modalidades"] == ["PRIMER_SORTEO", "LA_SEGUNDA", "REVANCHA"]

    def test_p05_no_quita_modalidad_con_informacion(self, admin):
        c = servicios.crear_concurso(admin, 1, FECHA, [PS, LS])
        _borrador_numeros(admin, c, LS)
        with pytest.raises(servicios.ErrorResultados):
            servicios.modificar_concurso(admin, c, FECHA, [PS])
        servicios.modificar_concurso(admin, c, FECHA, [LS])
        assert {mc.modalidad for mc in c.modalidades.all()} == {"LA_SEGUNDA"}

    def test_p05_no_cambia_fecha_con_numeros_publicados(self, admin):
        c = servicios.crear_concurso(admin, 1, FECHA, [PS, LS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        with pytest.raises(servicios.ErrorResultados):
            servicios.modificar_concurso(admin, c, date(2025, 4, 1), [PS, LS])
        servicios.modificar_concurso(admin, c, FECHA, [PS, LS, SS])

    def test_p06_al_modificar(self, admin):
        c = servicios.crear_concurso(admin, 1, FECHA, [PS, LS])
        with pytest.raises(servicios.ErrorResultados):
            servicios.modificar_concurso(admin, c, FECHA, [PS, LS, PE])


class TestBorradores:
    def test_crea_y_actualiza_la_unica_version_en_trabajo(self, admin):
        c = crear_concurso(1, FECHA)
        v1 = _borrador_numeros(admin, c, fuente=False)
        v2 = _borrador_numeros(admin, c, numeros=["07", "08", "09", "10", "11", "12"])
        assert v1.pk == v2.pk
        assert VersionNumeros.objects.count() == 1
        v2.refresh_from_db()
        assert v2.numeros == frozenset({7, 8, 9, 10, 11, 12})
        assert v2.estado == EstadoVersion.BORRADOR
        assert RegistroCambio.objects.filter(accion=Accion.GUARDAR_BORRADOR).count() == 2

    def test_numeros_invalidos(self, admin):
        c = crear_concurso(1, FECHA)
        with pytest.raises(servicios.ErrorResultados):
            _borrador_numeros(admin, c, numeros=["01", "01", "02", "03", "04", "05"])
        assert not VersionNumeros.objects.exists()

    def test_premio_extra_no_tiene_numeros(self, admin):
        c = crear_concurso(1, FECHA)
        with pytest.raises(servicios.ErrorResultados):
            _borrador_numeros(admin, c, PE)

    def test_premios_una_fila_por_categoria(self, admin):
        c = crear_concurso(1, FECHA)
        v = servicios.guardar_borrador_premios(
            admin, _mc(c, PS), {"PRIMER": {"ganadores": 1}, "OTRA": {"ganadores": 9}}
        )
        assert sorted(
            PremioCategoria.objects.filter(version_premios=v).values_list("categoria", flat=True)
        ) == ["PRIMER", "SEGUNDO", "TERCER"]
        servicios.guardar_borrador_premios(
            admin, _mc(c, PS), {"SEGUNDO": {"importe_individual": Decimal("10.50")}}
        )
        assert PremioCategoria.objects.filter(version_premios=v).count() == 3
        assert PremioCategoria.objects.get(categoria="SEGUNDO").importe_individual == Decimal(
            "10.50"
        )
        assert PremioCategoria.objects.get(categoria="PRIMER").ganadores is None


class TestObservacion:
    def test_observar_exige_motivo(self, admin):
        c = crear_concurso(1, FECHA)
        v = _borrador_numeros(admin, c)
        with pytest.raises(servicios.ErrorResultados):
            servicios.observar(admin, v, "  ")
        servicios.observar(admin, v, "No coincide con el extracto")
        v.refresh_from_db()
        assert v.estado == EstadoVersion.OBSERVADO
        assert RegistroCambio.objects.get(accion=Accion.OBSERVAR).motivo == (
            "No coincide con el extracto"
        )

    def test_resolver_vuelve_a_borrador(self, admin):
        c = crear_concurso(1, FECHA)
        v = _borrador_numeros(admin, c)
        servicios.observar(admin, v, "Motivo")
        servicios.resolver_observacion(admin, v)
        v.refresh_from_db()
        assert v.estado == EstadoVersion.BORRADOR
        assert RegistroCambio.objects.filter(accion=Accion.RESOLVER_OBSERVACION).exists()


class TestPublicar:
    def _publicar(self, admin, v, adv=True, cotejo=True):
        return servicios.publicar(
            admin, v, advertencias_confirmadas=adv, cotejo_confirmado=cotejo, hoy=HOY
        )

    def test_rechaza_sin_fuente(self, admin):
        c = crear_concurso(1, FECHA)
        v = _borrador_numeros(admin, c, fuente=False)
        with pytest.raises(servicios.ErrorResultados) as error:
            self._publicar(admin, v)
        assert any("fuente" in m for m in error.value.mensajes)

    def test_rechaza_observado(self, admin):
        c = crear_concurso(1, FECHA)
        v = _borrador_numeros(admin, c)
        servicios.observar(admin, v, "Motivo")
        with pytest.raises(servicios.ErrorResultados):
            self._publicar(admin, v)

    def test_rechaza_advertencias_sin_confirmar(self, admin):
        c = crear_concurso(1, FECHA)
        _borrador_numeros(admin, c, LS)
        v = _borrador_numeros(admin, c, PS)
        assert servicios.revisar_para_publicar(v, hoy=HOY)[1]
        with pytest.raises(servicios.ErrorResultados):
            self._publicar(admin, v, adv=False)
        self._publicar(admin, v, adv=True)

    def test_rechaza_bloqueantes_de_premios(self, admin):
        c = crear_concurso(1, FECHA)
        v = servicios.guardar_borrador_premios(
            admin,
            _mc(c, SS),
            {"GANADORA": {"ganadores": 0}},
            aciertos_categoria_ganadora=5,
            fuente_descripcion="Extracto",
            fuente_fecha_consulta=HOY,
        )
        with pytest.raises(servicios.ErrorResultados):
            self._publicar(admin, v)

    def test_rechaza_sin_cotejo(self, admin):
        c = crear_concurso(1, FECHA)
        v = _borrador_numeros(admin, c)
        with pytest.raises(servicios.ErrorResultados) as error:
            self._publicar(admin, v, cotejo=False)
        assert error.value.mensajes == [
            "Confirmá que cotejaste esta información con la fuente oficial."
        ]

    def test_publica_y_registra(self, admin):
        c = crear_concurso(1, FECHA)
        v = _borrador_numeros(admin, c)
        self._publicar(admin, v)
        v.refresh_from_db()
        assert v.estado == EstadoVersion.PUBLICADA
        assert v.publicada_por == admin and v.publicada_en is not None
        registro = RegistroCambio.objects.get(accion=Accion.PUBLICAR)
        assert registro.valor_nuevo == {"numeros": [1, 2, 3, 4, 5, 6]}
        assert "Extracto oficial N.º 3215" in registro.fuente
        assert registro.autor == admin and registro.fecha_hora is not None

    def test_rn18_numeros_no_publica_premios(self, admin):
        c = crear_concurso(1, FECHA)
        servicios.guardar_borrador_premios(admin, _mc(c, PS), {})
        self._publicar(admin, _borrador_numeros(admin, c))
        mc = _mc(c, PS)
        assert consultas.estado_bloque(mc, "numeros").name == "PUBLICADO"
        assert consultas.estado_bloque(mc, "premios").name == "BORRADOR"

    def test_premios_con_importes_en_registro_como_texto(self, admin):
        c = crear_concurso(1, FECHA)
        v = servicios.guardar_borrador_premios(
            admin,
            _mc(c, RV),
            {
                "UNICO": {
                    "ganadores": 1,
                    "importe_individual": Decimal("1500.50"),
                    "importe_categoria": Decimal("1500.50"),
                }
            },
            fuente_descripcion="Extracto",
            fuente_fecha_consulta=HOY,
        )
        self._publicar(admin, v)
        registro = RegistroCambio.objects.get(accion=Accion.PUBLICAR)
        assert registro.valor_nuevo["categorias"][0]["importe_individual"] == "1500.50"


class TestRestricciones:
    def test_un_solo_borrador_por_bloque(self, admin):
        c = crear_concurso(1, FECHA)
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}), estado="BORRADOR")
        with pytest.raises(IntegrityError), transaction.atomic():
            cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 7}), estado="BORRADOR")

    @pytest.mark.parametrize("bloque", ["numeros", "premios"])
    def test_revision_sin_motivo(self, bloque):
        c = crear_concurso(1, FECHA)
        mc = _mc(c, PS)
        setattr(mc, f"{bloque}_en_revision", True)
        with pytest.raises(IntegrityError), transaction.atomic():
            mc.save()

    def test_registro_de_cambios_solo_agregado(self, admin):
        c = servicios.crear_concurso(admin, 1, FECHA, [PS])
        registro = RegistroCambio.objects.get()
        with pytest.raises(PermissionError):
            registro.save()
        with pytest.raises(PermissionError):
            registro.delete()
        with pytest.raises(PermissionError):
            RegistroCambio.objects.filter(concurso=c).update(motivo="x")
