"""[003] RN-01, RN-02, data-model § 2: etiqueta de estado de una extracción."""

import pytest

from dominio.extraccion.etiqueta import EtiquetaEstado, desde_slug, etiqueta_de
from dominio.extraccion.tipos import EstadoExtraccion as E
from dominio.mensajes import MENSAJES


@pytest.mark.parametrize(
    ("estado", "no_recuperados", "esperada"),
    [
        (E.EN_CURSO, False, EtiquetaEstado.EN_CURSO),
        (E.FINALIZADA, False, EtiquetaEstado.FINALIZADA),
        (E.CON_ADVERTENCIAS, False, EtiquetaEstado.CON_ADVERTENCIAS),
        (E.SIN_SORTEOS, False, EtiquetaEstado.SIN_SORTEOS),
        (E.CON_ADVERTENCIAS, True, EtiquetaEstado.CON_ERROR),  # precedencia de "Con error"
        (E.FINALIZADA, True, EtiquetaEstado.CON_ERROR),  # no ocurre ([002] RN-33): nunca se oculta
    ],
)
def test_etiqueta_de(estado, no_recuperados, esperada):
    assert etiqueta_de(estado, no_recuperados) is esperada


def test_slugs_y_desde_slug():
    assert [e.slug for e in EtiquetaEstado] == [
        "en-curso",
        "finalizada",
        "con-advertencias",
        "sin-sorteos",
        "con-error",
    ]
    for etiqueta in EtiquetaEstado:
        assert desde_slug(etiqueta.slug) is etiqueta
    assert desde_slug("desconocido") is None
    assert desde_slug("") is None


def test_textos_y_explicaciones_del_catalogo():
    for etiqueta in EtiquetaEstado:
        assert etiqueta.clave_texto in MENSAJES
        assert etiqueta.clave_explicacion in MENSAJES
    assert MENSAJES[EtiquetaEstado.CON_ADVERTENCIAS.clave_explicacion] == (
        "Hay sorteos del período que requieren revisión manual. El detalle los muestra."
    )


def test_variante_e_icono():
    assert {e: (e.variante, e.icono) for e in EtiquetaEstado} == {
        EtiquetaEstado.EN_CURSO: ("info", "loader-circle"),
        EtiquetaEstado.FINALIZADA: ("success", "circle-check"),
        EtiquetaEstado.CON_ADVERTENCIAS: ("warning", "triangle-alert"),
        EtiquetaEstado.SIN_SORTEOS: ("neutral", "circle-dashed"),
        EtiquetaEstado.CON_ERROR: ("danger", "circle-x"),
    }


def test_orden_primero_lo_que_requiere_atencion():
    assert sorted(EtiquetaEstado, key=lambda e: e.orden) == [
        EtiquetaEstado.EN_CURSO,
        EtiquetaEstado.CON_ERROR,
        EtiquetaEstado.CON_ADVERTENCIAS,
        EtiquetaEstado.SIN_SORTEOS,
        EtiquetaEstado.FINALIZADA,
    ]


def test_requiere_revision():
    assert {e for e in EtiquetaEstado if e.requiere_revision} == {
        EtiquetaEstado.CON_ADVERTENCIAS,
        EtiquetaEstado.CON_ERROR,
    }
