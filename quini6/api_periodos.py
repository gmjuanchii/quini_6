"""Atajos de período en la API v1 ([003] contracts/api.md, data-model § 2, RN-04).

``GET /periodos/atajos/?formulario=estadisticas|extraccion``. El nivel depende del formulario: los
de Estadísticas son públicos (P) y los de la extracción histórica, solo para administración (A),
igual que las pantallas que los muestran. La operación se declara P y exige A para ``extraccion``.
"""

from datetime import date
from typing import Literal

from ninja import Router, Schema

from dominio import periodos
from dominio.mensajes import mensaje
from quini6.api_base import nivel, rechazo_de_acceso
from quini6.fechas import hoy_buenos_aires

router = Router(tags=["Períodos"])


class Atajo(Schema):
    clave: str
    texto: str
    desde: date
    hasta: date


def atajos_dto(lista: list[periodos.Atajo]) -> list[dict]:
    return [
        {"clave": a.clave, "texto": mensaje(a.clave_texto), "desde": a.desde, "hasta": a.hasta}
        for a in lista
    ]


@router.get("/periodos/atajos/", response=list[Atajo])
@nivel("P", sin_cache=True)
def atajos(request, formulario: Literal["estadisticas", "extraccion"]):
    if formulario == "extraccion":
        rechazo = rechazo_de_acceso(request, "A")
        if rechazo is not None:
            return rechazo
        return atajos_dto(periodos.atajos(hoy_buenos_aires(), "extraccion", None))
    from resultados.consultas import fecha_primer_sorteo_publicado

    primer = fecha_primer_sorteo_publicado()
    return atajos_dto(periodos.atajos(hoy_buenos_aires(), "estadisticas", primer))
