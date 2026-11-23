"""Extracciones en cada etiqueta de [003] RN-01, escritas con el ORM (pruebas de presentación)."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from django.utils import timezone

from dominio.extraccion.tipos import EstadoExtraccion, EstadoSorteo
from extracciones.models import Extraccion, SorteoExtraido

#: etiqueta → (estado de [002], estados de sus sorteos)
CASOS = {
    "en-curso": (EstadoExtraccion.EN_CURSO, []),
    "finalizada": (EstadoExtraccion.FINALIZADA, [EstadoSorteo.RECUPERADO]),
    "con-advertencias": (
        EstadoExtraccion.CON_ADVERTENCIAS,
        [EstadoSorteo.RECUPERADO, EstadoSorteo.PARCIAL],
    ),
    "sin-sorteos": (EstadoExtraccion.SIN_SORTEOS, []),
    "con-error": (
        EstadoExtraccion.CON_ADVERTENCIAS,
        [EstadoSorteo.CON_INCONSISTENCIAS, EstadoSorteo.NO_RECUPERADO],
    ),
}


def crear_extraccion(
    usuario,
    etiqueta: str,
    iniciada_en: datetime | None = None,
    desde: date = date(2026, 11, 1),
    hasta: date = date(2026, 11, 15),
) -> Extraccion:
    estado, estados_sorteos = CASOS[etiqueta]
    momento = iniciada_en or timezone.make_aware(datetime(2026, 11, 21, 12, 15))
    terminada = estado is not EstadoExtraccion.EN_CURSO
    por_estado: dict[str, int] = {}
    for e in estados_sorteos:
        por_estado[e.value] = por_estado.get(e.value, 0) + 1
    extraccion = Extraccion.objects.create(
        creada_por=usuario,
        desde=desde,
        hasta=hasta,
        estado=estado.value,
        iniciada_en=momento,
        finalizada_en=momento + timedelta(minutes=3) if terminada else None,
        numero_desde=3422 if estados_sorteos else None,
        numero_hasta=3422 + len(estados_sorteos) - 1 if estados_sorteos else None,
        resumen={
            "identificados": len(estados_sorteos),
            "por_estado": por_estado,
            "fuentes": [],
            "huecos": [],
            "a_revisar": [],
        }
        if terminada
        else None,
    )
    for indice, e in enumerate(estados_sorteos):
        SorteoExtraido.objects.create(
            extraccion=extraccion,
            numero=3422 + indice,
            fecha=date(2026, 11, 1) + timedelta(days=indice * 3),
            estado=e.value,
            consolidado={},
            procesado_en=momento,
        )
    return extraccion
