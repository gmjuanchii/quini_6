"""Estados derivados de data-model.md (RN-07, RN-16, RN-19, RN-20, RN-25; SC-003)."""

from datetime import date

import pytest

from dominio.tipos import EstadoBloque, Modalidad
from resultados import consultas
from resultados.models import ModalidadConcurso
from tests.fabricas import (
    cargar_numeros,
    cargar_premios,
    crear_concurso,
    marcar_en_revision,
)

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)
N = frozenset({1, 2, 3, 4, 5, 6})
N2 = frozenset({10, 11, 12, 13, 14, 15})


def _mc(concurso, modalidad):
    return ModalidadConcurso.objects.get(concurso=concurso, modalidad=modalidad.value)


class TestEstadoBloque:
    def test_sin_versiones(self):
        c = crear_concurso(1, date(2025, 1, 1))
        assert consultas.estado_bloque(_mc(c, PS), "numeros") == EstadoBloque.SIN_CARGAR
        assert consultas.estado_bloque(_mc(c, PS), "premios") == EstadoBloque.SIN_CARGAR

    def test_borrador(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N, estado="BORRADOR")
        assert consultas.estado_bloque(_mc(c, PS), "numeros") == EstadoBloque.BORRADOR

    def test_observado(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_premios(c, PS, estado="OBSERVADO")
        assert consultas.estado_bloque(_mc(c, PS), "premios") == EstadoBloque.OBSERVADO

    def test_publicado(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        assert consultas.estado_bloque(_mc(c, PS), "numeros") == EstadoBloque.PUBLICADO

    def test_en_revision(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        marcar_en_revision(c, PS, "numeros", "Posible error")
        assert consultas.estado_bloque(_mc(c, PS), "numeros") == EstadoBloque.EN_REVISION

    def test_publicado_con_correccion_en_preparacion(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        cargar_numeros(c, PS, N2, estado="BORRADOR", es_correccion=True)
        mc = _mc(c, PS)
        assert consultas.estado_bloque(mc, "numeros") == EstadoBloque.PUBLICADO
        assert consultas.correccion_en_preparacion(mc, "numeros") is True
        assert consultas.version_vigente(mc, "numeros").numeros == N


class TestCompletitud:
    def test_sin_resultados(self):
        c = crear_concurso(1, date(2025, 1, 1), modalidades=[PS])
        assert consultas.completitud(c) == "SIN_RESULTADOS"

    def test_incompleto(self):
        c = crear_concurso(1, date(2025, 1, 1), modalidades=[PS, LS])
        cargar_numeros(c, PS, N)
        assert consultas.completitud(c) == "INCOMPLETO"

    def test_completo(self):
        c = crear_concurso(1, date(2025, 1, 1), modalidades=[PS])
        cargar_numeros(c, PS, N)
        cargar_premios(c, PS)
        assert consultas.completitud(c) == "COMPLETO"

    def test_modalidad_no_aplicable_no_cuenta(self):
        """AC-1.16: Revancha no aplica y no impide que el concurso esté completo."""
        c = crear_concurso(1, date(2025, 1, 1), modalidades=[PS, LS])
        for m in (PS, LS):
            cargar_numeros(c, m, N)
            cargar_premios(c, m)
        assert consultas.completitud(c) == "COMPLETO"

    def test_premio_extra_solo_aporta_premios(self):
        c = crear_concurso(1, date(2025, 1, 1))
        for m in (PS, LS, RV, SS):
            cargar_numeros(c, m, N)
            cargar_premios(c, m)
        assert consultas.completitud(c) == "INCOMPLETO"
        cargar_premios(c, PE, aciertos_categoria_ganadora=6)
        assert consultas.completitud(c) == "COMPLETO"


class TestAdmiteJugadas:
    def test_borrador_u_observado_no_cierran(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N, estado="BORRADOR")
        cargar_numeros(c, LS, N, estado="OBSERVADO")
        assert consultas.admite_jugadas(c) is True

    def test_publicada_cierra(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, SS, N)
        assert consultas.admite_jugadas(c) is False

    def test_reemplazada_cierra(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        cargar_numeros(c, PS, N2, es_correccion=True)
        assert consultas.admite_jugadas(c) is False

    def test_premios_publicados_no_cierran(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_premios(c, PS)
        assert consultas.admite_jugadas(c) is True


class TestUltimosResultados:
    def test_sin_concursos(self):
        assert consultas.ultimos_resultados() == (None, None)

    def test_ultimo_publicado_y_pendiente_aparte(self):
        viejo = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(viejo, PS, N)
        nuevo = crear_concurso(2, date(2025, 1, 4))
        ultimos, pendiente = consultas.ultimos_resultados()
        assert ultimos == viejo
        assert pendiente == nuevo

    def test_sin_pendiente_si_el_mas_reciente_tiene_publicaciones(self):
        crear_concurso(1, date(2025, 1, 1))
        nuevo = crear_concurso(2, date(2025, 1, 4))
        cargar_premios(nuevo, PS)
        assert consultas.ultimos_resultados() == (nuevo, None)

    def test_solo_pendiente(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N, estado="BORRADOR")
        assert consultas.ultimos_resultados() == (None, c)


class TestDatosConcurso:
    def test_nunca_expone_borrador_ni_observado(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N, estado="BORRADOR")
        cargar_numeros(c, LS, N2, estado="OBSERVADO")
        cargar_premios(c, PS, {"PRIMER": {"ganadores": 3}}, estado="BORRADOR")
        datos = consultas.datos_concurso(c)
        assert datos.numeros[PS].estado == EstadoBloque.BORRADOR
        assert datos.numeros[PS].numeros is None
        assert datos.numeros[LS].estado == EstadoBloque.OBSERVADO
        assert datos.numeros[LS].numeros is None
        assert datos.premios[PS].categorias is None

    def test_publicado_y_en_revision(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        cargar_numeros(c, LS, N2)
        marcar_en_revision(c, LS, "numeros", "Revisar")
        datos = consultas.datos_concurso(c)
        assert datos.numeros[PS].numeros == N
        assert datos.numeros[LS].estado == EstadoBloque.EN_REVISION
        assert datos.numeros[LS].numeros == N2
        assert PE not in datos.numeros
        assert datos.modalidades == frozenset({PS, LS, RV, SS, PE})

    def test_premios_publicados(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_premios(
            c,
            SS,
            {"GANADORA": {"ganadores": 2, "importe_individual": "1500.50"}},
            aciertos_categoria_ganadora=5,
        )
        bloque = consultas.datos_concurso(c).premios[SS]
        assert bloque.estado == EstadoBloque.PUBLICADO
        assert bloque.aciertos_categoria_ganadora == 5
        assert str(bloque.categoria("GANADORA").importe_individual) == "1500.50"


class TestVistaPublica:
    def test_premio_extra_sin_conjunto_parcial(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        cargar_numeros(c, RV, N2, estado="BORRADOR")
        vista = consultas.vista_publica_concurso(c)
        pe = vista.modalidad(PE)
        assert pe.estado_numeros == EstadoBloque.SIN_CARGAR  # La Segunda sin cargar
        assert pe.conjunto is None
        cargar_numeros(c, LS, N2)
        pe = consultas.vista_publica_concurso(c).modalidad(PE)
        assert pe.estado_numeros == EstadoBloque.BORRADOR
        assert pe.conjunto is None

    def test_premio_extra_conjunto_completo(self):
        c = crear_concurso(1, date(2025, 1, 1))
        cargar_numeros(c, PS, N)
        cargar_numeros(c, LS, N2)
        cargar_numeros(c, RV, frozenset({1, 2, 20, 21, 22, 23}))
        marcar_en_revision(c, RV, "numeros", "Revisar")
        pe = consultas.vista_publica_concurso(c).modalidad(PE)
        assert pe.estado_numeros == EstadoBloque.EN_REVISION
        assert pe.conjunto == sorted(N | N2 | {20, 21, 22, 23})

    def test_orden_y_no_aplicables(self):
        c = crear_concurso(1, date(2025, 1, 1), modalidades=[SS, PS])
        vista = consultas.vista_publica_concurso(c)
        assert [m.modalidad for m in vista.modalidades] == [PS, SS]


def test_fecha_ultima_correccion():
    c = crear_concurso(1, date(2025, 1, 1))
    cargar_numeros(c, PS, N, publicada_en=date(2025, 1, 2))
    mc = _mc(c, PS)
    assert consultas.fecha_ultima_correccion(mc, "numeros") is None
    cargar_numeros(c, PS, N2, es_correccion=True, publicada_en=date(2025, 1, 5))
    cargar_numeros(c, PS, N, es_correccion=True, publicada_en=date(2025, 1, 9))
    assert consultas.fecha_ultima_correccion(_mc(c, PS), "numeros") == date(2025, 1, 9)
    cargar_numeros(c, PS, N2, estado="BORRADOR", es_correccion=True)
    assert consultas.fecha_ultima_correccion(_mc(c, PS), "numeros") == date(2025, 1, 9)
