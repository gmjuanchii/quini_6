"""NFR-004 y R-17: cantidad acotada de consultas, sin N+1, con 104 concursos y 50 jugadas."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from dominio.tipos import ORDEN_MODALIDADES, Modalidad
from jugadas.models import Jugada
from resultados.models import (
    Concurso,
    EstadoVersion,
    ModalidadConcurso,
    PremioCategoria,
    VersionNumeros,
    VersionPremios,
)
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

TOPE = 20


@pytest.fixture
def volumen(usuario_a):
    admin = crear_usuario("vol-admin@prueba.local", admin=True)
    inicio = date(2024, 7, 1)
    versiones_n, versiones_p = [], []
    concursos = Concurso.objects.bulk_create(
        [
            Concurso(numero=3000 + i, fecha_sorteo=inicio + timedelta(days=3 * i), creado_por=admin)
            for i in range(104)
        ]
    )
    mcs = ModalidadConcurso.objects.bulk_create(
        [
            ModalidadConcurso(concurso=c, modalidad=m.value)
            for c in concursos
            for m in ORDEN_MODALIDADES
        ]
    )
    for i, mc in enumerate(mcs):
        comunes = {
            "estado": EstadoVersion.PUBLICADA,
            "fuente_descripcion": "Extracto",
            "fuente_fecha_consulta": inicio,
            "creada_por": admin,
            "publicada_por": admin,
            "publicada_en": mc.concurso.creado_en,
        }
        if mc.modalidad != Modalidad.PREMIO_EXTRA.value:
            base = i % 40
            versiones_n.append(
                VersionNumeros(
                    modalidad_concurso=mc,
                    n1=base,
                    n2=base + 1,
                    n3=base + 2,
                    n4=base + 3,
                    n5=base + 4,
                    n6=base + 5,
                    **comunes,
                )
            )
        versiones_p.append(
            VersionPremios(
                modalidad_concurso=mc,
                aciertos_categoria_ganadora=(
                    5 if mc.modalidad in ("SIEMPRE_SALE", "PREMIO_EXTRA") else None
                ),
                **comunes,
            )
        )
    VersionNumeros.objects.bulk_create(versiones_n)
    versiones_p = VersionPremios.objects.bulk_create(versiones_p)
    PremioCategoria.objects.bulk_create(
        [
            PremioCategoria(
                version_premios=v, categoria=c, ganadores=1, importe_individual=Decimal("1000")
            )
            for v in versiones_p
            for c in Modalidad(v.modalidad_concurso.modalidad).categorias
        ]
    )
    jugadas = []
    for i in range(50):
        j = Jugada(usuario=usuario_a, concurso=concursos[i * 2], costo=Decimal("100"))
        j.asignar_numeros({0, 1, 2, 3, 4, 5})
        jugadas.append(j)
    Jugada.objects.bulk_create(jugadas)
    return Jugada.objects.filter(usuario=usuario_a).first()


@pytest.mark.parametrize(
    "url",
    [
        "/resultados/",
        "/resultados/3050/",
        "/mis-jugadas/",
        "/estadisticas/",
        "/estadisticas/?modalidad=SIEMPRE_SALE&numero=07",
    ],
)
def test_tope_de_consultas(cliente_a, volumen, django_assert_max_num_queries, url):
    with django_assert_max_num_queries(TOPE):
        r = cliente_a.get(url)
    assert r.status_code == 200


def test_detalle_de_jugada(cliente_a, volumen, django_assert_max_num_queries):
    with django_assert_max_num_queries(TOPE):
        r = cliente_a.get(f"/mis-jugadas/{volumen.id}/")
    assert r.status_code == 200
