"""Reglas de registro y gestión de jugadas (RN-04 a RN-10). Las validaciones de números e
importes viven en ``dominio/``; aquí solo se aplican sobre la base de datos."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from dominio.numeros import misma_combinacion
from jugadas.models import Jugada
from resultados import consultas
from resultados.models import Concurso, EstadoVersion

NO_DISPONIBLE = "Este concurso todavía no está disponible para registrar jugadas"
CERRADO = (
    "Ya no se pueden registrar jugadas para este concurso porque sus resultados fueron publicados"
)
FIJA = (
    "Esta jugada no se puede modificar ni eliminar porque los resultados de su concurso ya fueron "
    "publicados"
)


@dataclass(frozen=True)
class ErrorJugada:
    codigo: str  # NO_DISPONIBLE, CERRADO, REQUIERE_CONFIRMACION, FIJA

    @property
    def mensaje(self) -> str:
        return {
            "NO_DISPONIBLE": NO_DISPONIBLE,
            "CERRADO": CERRADO,
            "FIJA": FIJA,
            "REQUIERE_CONFIRMACION": (
                "Ya registraste una jugada con estos números para este concurso. "
                "¿Querés guardarla igual?"
            ),
        }[self.codigo]


def concursos_disponibles():
    """Concursos que admiten jugadas (RN-07): ninguna extracción publicada."""
    cerrados = Concurso.objects.filter(
        modalidades__versiones_numeros__estado__in=[
            EstadoVersion.PUBLICADA,
            EstadoVersion.REEMPLAZADA,
        ]
    ).values("pk")
    return (
        Concurso.objects.exclude(pk__in=cerrados)
        .order_by("fecha_sorteo", "numero")
        .prefetch_related("modalidades")
    )


def resolver_concurso(numero) -> Concurso | ErrorJugada:
    try:
        numero = int(str(numero).strip())
    except (TypeError, ValueError):
        return ErrorJugada("NO_DISPONIBLE")
    concurso = consultas.cargar_concurso(numero)
    if concurso is None:
        return ErrorJugada("NO_DISPONIBLE")
    if not consultas.admite_jugadas(concurso):
        return ErrorJugada("CERRADO")
    return concurso


def hay_duplicado(usuario, concurso: Concurso, numeros, excluir_id=None) -> bool:
    """RN-06: otra jugada propia del mismo concurso con los mismos seis números."""
    otras = Jugada.objects.filter(usuario=usuario, concurso=concurso)
    if excluir_id is not None:
        otras = otras.exclude(pk=excluir_id)
    return any(misma_combinacion(j.numeros, numeros) for j in otras)


def es_modificable(jugada: Jugada) -> bool:
    """RN-08: el mismo corte que RN-07."""
    return consultas.admite_jugadas(jugada.concurso)


def _concurso_abierto(concurso: Concurso) -> Concurso | ErrorJugada:
    """Vuelve a verificar RN-07 con datos frescos y la fila del concurso bloqueada."""
    Concurso.objects.select_for_update().filter(pk=concurso.pk).exists()
    fresco = consultas.cargar_concurso(concurso.numero)
    if fresco is None:
        return ErrorJugada("NO_DISPONIBLE")
    if not consultas.admite_jugadas(fresco):
        return ErrorJugada("CERRADO")
    return fresco


def registrar_jugada(
    usuario, concurso: Concurso, numeros, costo: Decimal, confirmar_duplicado: bool
) -> Jugada | ErrorJugada:
    with transaction.atomic():
        abierto = _concurso_abierto(concurso)
        if isinstance(abierto, ErrorJugada):
            return abierto
        if not confirmar_duplicado and hay_duplicado(usuario, abierto, numeros):
            return ErrorJugada("REQUIERE_CONFIRMACION")
        jugada = Jugada(usuario=usuario, concurso=abierto, costo=costo)
        jugada.asignar_numeros(numeros)
        jugada.save()
    return jugada


def editar_jugada(
    jugada: Jugada, concurso: Concurso, numeros, costo: Decimal, confirmar_duplicado: bool
) -> Jugada | ErrorJugada:
    with transaction.atomic():
        jugada = Jugada.objects.select_for_update().select_related("concurso").get(pk=jugada.pk)
        if isinstance(_concurso_abierto(jugada.concurso), ErrorJugada):
            return ErrorJugada("FIJA")
        abierto = _concurso_abierto(concurso)
        if isinstance(abierto, ErrorJugada):
            return abierto
        if not confirmar_duplicado and hay_duplicado(
            jugada.usuario, abierto, numeros, excluir_id=jugada.pk
        ):
            return ErrorJugada("REQUIERE_CONFIRMACION")
        jugada.concurso = abierto
        jugada.asignar_numeros(numeros)
        jugada.costo = costo
        jugada.modificada_en = timezone.now()
        jugada.save()
    return jugada


def eliminar_jugada(jugada: Jugada) -> ErrorJugada | None:
    with transaction.atomic():
        jugada = Jugada.objects.select_for_update().select_related("concurso").get(pk=jugada.pk)
        if isinstance(_concurso_abierto(jugada.concurso), ErrorJugada):
            return ErrorJugada("FIJA")
        jugada.delete()
    return None
