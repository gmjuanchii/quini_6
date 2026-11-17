"""Tipos compartidos del dominio (contracts/dominio.md, data-model.md "Catálogos fijos").

Este paquete no importa Django: recibe valores y devuelve valores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

Numeros = frozenset[int]

#: RN-33: las reglas de RN-31 y RN-49 a RN-54 rigen desde esta fecha del sorteo.
FECHA_VIGENCIA_REGLAS = date(2024, 6, 18)


class Modalidad(Enum):
    PRIMER_SORTEO = "PRIMER_SORTEO"
    LA_SEGUNDA = "LA_SEGUNDA"
    REVANCHA = "REVANCHA"
    SIEMPRE_SALE = "SIEMPRE_SALE"
    PREMIO_EXTRA = "PREMIO_EXTRA"

    @property
    def nombre(self) -> str:
        return _NOMBRES[self]

    @property
    def slug(self) -> str:
        return _SLUGS[self]

    @property
    def tiene_extraccion_propia(self) -> bool:
        """RN-15: Premio Extra no es una extracción independiente."""
        return self is not Modalidad.PREMIO_EXTRA

    @property
    def categorias(self) -> tuple[str, ...]:
        """Categorías predefinidas de premios (RN-26, RN-49 a RN-52, RN-31)."""
        return _CATEGORIAS[self]

    @classmethod
    def desde_slug(cls, slug: str) -> Modalidad:
        for modalidad, valor in _SLUGS.items():
            if valor == slug:
                return modalidad
        raise ValueError(f"Modalidad desconocida: {slug}")


_NOMBRES = {
    Modalidad.PRIMER_SORTEO: "Tradicional – Primer Sorteo",
    Modalidad.LA_SEGUNDA: "Tradicional – La Segunda",
    Modalidad.REVANCHA: "Revancha",
    Modalidad.SIEMPRE_SALE: "Siempre Sale",
    Modalidad.PREMIO_EXTRA: "Premio Extra",
}

_SLUGS = {
    Modalidad.PRIMER_SORTEO: "primer-sorteo",
    Modalidad.LA_SEGUNDA: "la-segunda",
    Modalidad.REVANCHA: "revancha",
    Modalidad.SIEMPRE_SALE: "siempre-sale",
    Modalidad.PREMIO_EXTRA: "premio-extra",
}

_CATEGORIAS = {
    Modalidad.PRIMER_SORTEO: ("PRIMER", "SEGUNDO", "TERCER"),
    Modalidad.LA_SEGUNDA: ("PRIMER", "SEGUNDO", "TERCER"),
    Modalidad.REVANCHA: ("UNICO",),
    Modalidad.SIEMPRE_SALE: ("GANADORA",),
    Modalidad.PREMIO_EXTRA: ("GANADORA",),
}

#: Orden de presentación de las modalidades (AC-5.31).
ORDEN_MODALIDADES: tuple[Modalidad, ...] = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)

#: Modalidades cuyas extracciones forman el conjunto de Premio Extra (RN-31).
MODALIDADES_PREMIO_EXTRA: tuple[Modalidad, ...] = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
)

#: Nombre visible de las categorías con aciertos fijos.
NOMBRE_CATEGORIA: dict[str, str] = {
    "PRIMER": "Primer Premio",
    "SEGUNDO": "Segundo Premio",
    "TERCER": "Tercer Premio",
    "UNICO": "Premio Revancha",
}

#: Aciertos que definen cada categoría fija.
ACIERTOS_CATEGORIA: dict[str, int] = {
    "PRIMER": 6,
    "SEGUNDO": 5,
    "TERCER": 4,
    "UNICO": 6,
}


def nombre_categoria(modalidad: Modalidad, codigo: str, aciertos: int | None = None) -> str:
    """Nombre visible de una categoría ("Siempre Sale (5 aciertos)" para la ganadora)."""
    if codigo == "GANADORA":
        if aciertos is None:
            return "Categoría ganadora"
        return f"{modalidad.nombre} ({aciertos} aciertos)"
    return NOMBRE_CATEGORIA[codigo]


class EstadoBloque(Enum):
    SIN_CARGAR = "SIN_CARGAR"
    BORRADOR = "BORRADOR"
    OBSERVADO = "OBSERVADO"
    PUBLICADO = "PUBLICADO"
    EN_REVISION = "EN_REVISION"

    @property
    def publicado(self) -> bool:
        return self in (EstadoBloque.PUBLICADO, EstadoBloque.EN_REVISION)


@dataclass(frozen=True)
class BloqueNumerosVista:
    estado: EstadoBloque
    numeros: Numeros | None = None  # solo si está PUBLICADO o EN_REVISION


@dataclass(frozen=True)
class CategoriaPublicada:
    codigo: str
    ganadores: int | None = None
    importe_categoria: Decimal | None = None
    importe_individual: Decimal | None = None
    pozo_vacante_acumulado: Decimal | None = None


@dataclass(frozen=True)
class BloquePremiosVista:
    estado: EstadoBloque
    categorias: tuple[CategoriaPublicada, ...] | None = None
    aciertos_categoria_ganadora: int | None = None
    sin_ganadores: bool = False

    def categoria(self, codigo: str) -> CategoriaPublicada | None:
        for cat in self.categorias or ():
            if cat.codigo == codigo:
                return cat
        return None


@dataclass(frozen=True)
class DatosConcurso:
    fecha_sorteo: date
    modalidades: frozenset[Modalidad]
    numeros: dict[Modalidad, BloqueNumerosVista] = field(default_factory=dict)
    premios: dict[Modalidad, BloquePremiosVista] = field(default_factory=dict)

    def bloque_numeros(self, modalidad: Modalidad) -> BloqueNumerosVista:
        return self.numeros.get(modalidad, BloqueNumerosVista(EstadoBloque.SIN_CARGAR))

    def bloque_premios(self, modalidad: Modalidad) -> BloquePremiosVista:
        return self.premios.get(modalidad, BloquePremiosVista(EstadoBloque.SIN_CARGAR))
