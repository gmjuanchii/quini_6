"""Etiqueta de estado visible de una extracción ([003] RN-01, RN-02, data-model § 2).

Es presentación derivada del estado de [002] y de si algún sorteo quedó "No recuperado": no se
guarda ni cambia [002] RN-33. Sin dependencias de Django.
"""

from __future__ import annotations

from enum import Enum

from dominio.extraccion.tipos import EstadoExtraccion


class EtiquetaEstado(Enum):
    """Las cinco etiquetas de RN-01, en el orden en que se presentan los filtros."""

    EN_CURSO = "en_curso"
    FINALIZADA = "finalizada"
    CON_ADVERTENCIAS = "con_advertencias"
    SIN_SORTEOS = "sin_sorteos"
    CON_ERROR = "con_error"

    @property
    def slug(self) -> str:
        """Valor en la dirección (``?estado=con-advertencias``)."""
        return self.value.replace("_", "-")

    @property
    def clave_texto(self) -> str:
        return f"etiqueta.{self.value}"

    @property
    def clave_explicacion(self) -> str:
        return f"etiqueta.{self.value}.explicacion"

    @property
    def variante(self) -> str:
        return _VARIANTES[self]

    @property
    def icono(self) -> str:
        return _ICONOS[self]

    @property
    def orden(self) -> int:
        """Orden ascendente de la columna "Estado": primero lo que requiere atención (AC-9.1)."""
        return _ORDEN[self]

    @property
    def requiere_revision(self) -> bool:
        """Se destaca en el listado (AC-1.3)."""
        return self in (EtiquetaEstado.CON_ADVERTENCIAS, EtiquetaEstado.CON_ERROR)


_VARIANTES = {
    EtiquetaEstado.EN_CURSO: "info",
    EtiquetaEstado.FINALIZADA: "success",
    EtiquetaEstado.CON_ADVERTENCIAS: "warning",
    EtiquetaEstado.SIN_SORTEOS: "neutral",
    EtiquetaEstado.CON_ERROR: "danger",
}
_ICONOS = {
    EtiquetaEstado.EN_CURSO: "loader-circle",
    EtiquetaEstado.FINALIZADA: "circle-check",
    EtiquetaEstado.CON_ADVERTENCIAS: "triangle-alert",
    EtiquetaEstado.SIN_SORTEOS: "circle-dashed",
    EtiquetaEstado.CON_ERROR: "circle-x",
}
_ORDEN = {
    EtiquetaEstado.EN_CURSO: 0,
    EtiquetaEstado.CON_ERROR: 1,
    EtiquetaEstado.CON_ADVERTENCIAS: 2,
    EtiquetaEstado.SIN_SORTEOS: 3,
    EtiquetaEstado.FINALIZADA: 4,
}


def etiqueta_de(estado: EstadoExtraccion, tiene_no_recuperados: bool) -> EtiquetaEstado:
    """RN-01: "Con error" tiene precedencia sobre "Con advertencias".

    ``(FINALIZADA, True)`` no puede ocurrir por [002] RN-33; si ocurriera, se informa "Con error"
    para no ocultar nunca un sorteo no recuperado (Const. IX).
    """
    if estado is EstadoExtraccion.EN_CURSO:
        return EtiquetaEstado.EN_CURSO
    if estado is EstadoExtraccion.SIN_SORTEOS:
        return EtiquetaEstado.SIN_SORTEOS
    if tiene_no_recuperados:
        return EtiquetaEstado.CON_ERROR
    if estado is EstadoExtraccion.CON_ADVERTENCIAS:
        return EtiquetaEstado.CON_ADVERTENCIAS
    return EtiquetaEstado.FINALIZADA


def desde_slug(slug: str | None) -> EtiquetaEstado | None:
    """Etiqueta del parámetro ``estado`` de la dirección; desconocida o vacía → ``None``."""
    for etiqueta in EtiquetaEstado:
        if etiqueta.slug == (slug or "").strip():
            return etiqueta
    return None
