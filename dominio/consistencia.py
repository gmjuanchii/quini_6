"""Controles de consistencia antes de publicar (RN-22, AC-2.5, AC-2.9).

Devuelven ``(bloqueantes, advertencias)``: listas de ``Observacion`` con un código y un
texto en español que indica qué falta o qué es inconsistente.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date

from dominio.mensajes import MENSAJES, mensaje
from dominio.numeros import ErrorNumero, formatear, validar_extraccion
from dominio.tipos import CategoriaPublicada, Modalidad, Numeros, nombre_categoria

Fuente = tuple[str, date | None] | None


@dataclass(frozen=True)
class Observacion:
    codigo: str
    texto: str


def _revisar_fuente(fuente: Fuente) -> list[Observacion]:
    descripcion, fecha = fuente if fuente else ("", None)
    faltan = []
    if not (descripcion or "").strip():
        faltan.append("la descripción de la fuente")
    if fecha is None:
        faltan.append("la fecha de consulta de la fuente")
    if not faltan:
        return []
    return [Observacion("SIN_FUENTE", "Falta registrar " + " y ".join(faltan) + ".")]


def _texto_error_numero(error: ErrorNumero) -> Observacion:
    if error.codigo in ("FALTAN_N", "SOBRAN"):
        return Observacion("CANTIDAD", "Los números sorteados deben ser exactamente seis.")
    if error.codigo == "REPETIDO":
        return Observacion(
            "REPETIDO", mensaje("admin.numero_repetido", nn=formatear(error.numero or 0))
        )
    return Observacion("FUERA_DE_RANGO", MENSAJES["admin.numeros_rango"])


def revisar_numeros(
    numeros: Iterable[int | str],
    otras_modalidades_del_concurso: Mapping[Modalidad, Numeros],
    fecha_sorteo: date,
    hoy: date,
    fuente: Fuente,
) -> tuple[list[Observacion], list[Observacion]]:
    bloqueantes: list[Observacion] = []
    advertencias: list[Observacion] = []
    resultado = validar_extraccion(list(numeros))
    if isinstance(resultado, list):
        for error in resultado:
            observacion = _texto_error_numero(error)
            if observacion not in bloqueantes:
                bloqueantes.append(observacion)
    else:
        for modalidad, otros in otras_modalidades_del_concurso.items():
            if otros and frozenset(otros) == resultado:
                advertencias.append(
                    Observacion(
                        "NUMEROS_IGUALES",
                        f"Los seis números son iguales a los de {modalidad.nombre} en este sorteo.",
                    )
                )
    bloqueantes.extend(_revisar_fuente(fuente))
    if fecha_sorteo > hoy:
        advertencias.append(
            Observacion(
                "FECHA_FUTURA",
                MENSAJES["admin.fecha_futura"],
            )
        )
    return bloqueantes, advertencias


def revisar_premios(
    modalidad: Modalidad,
    categorias: Iterable[CategoriaPublicada],
    aciertos_categoria_ganadora: int | None,
    sin_ganadores: bool,
    fuente: Fuente,
) -> tuple[list[Observacion], list[Observacion]]:
    bloqueantes: list[Observacion] = []
    advertencias: list[Observacion] = []
    categorias = list(categorias)

    for cat in categorias:
        nombre = nombre_categoria(modalidad, cat.codigo, aciertos_categoria_ganadora)
        if cat.ganadores is not None and cat.ganadores < 0:
            bloqueantes.append(
                Observacion(
                    "GANADORES_NEGATIVO",
                    f"{nombre}: la cantidad de ganadores no puede ser negativa.",
                )
            )
        importes = (cat.importe_categoria, cat.importe_individual, cat.pozo_vacante_acumulado)
        if any(v is not None and v < 0 for v in importes):
            bloqueantes.append(
                Observacion("IMPORTE_NEGATIVO", f"{nombre}: los importes no pueden ser negativos.")
            )
        if cat.ganadores and cat.ganadores > 0 and cat.importe_individual is None:
            advertencias.append(
                Observacion(
                    "SIN_IMPORTE_INDIVIDUAL",
                    f"{nombre}: tiene ganadores pero no tiene importe individual.",
                )
            )

    if modalidad is Modalidad.SIEMPRE_SALE:
        if aciertos_categoria_ganadora is not None:
            if not 0 <= aciertos_categoria_ganadora <= 6:
                bloqueantes.append(
                    Observacion(
                        "CATEGORIA_GANADORA_INVALIDA",
                        "La categoría ganadora de Siempre Sale debe ser de 0 a 6 aciertos.",
                    )
                )
            ganadora = next((c for c in categorias if c.codigo == "GANADORA"), None)
            if ganadora is not None and ganadora.ganadores == 0:
                bloqueantes.append(
                    Observacion(
                        "CATEGORIA_SIN_GANADORES",
                        "La categoría ganadora de Siempre Sale no puede tener 0 ganadores.",
                    )
                )
    elif modalidad is Modalidad.PREMIO_EXTRA:
        if aciertos_categoria_ganadora is not None and aciertos_categoria_ganadora not in (6, 5, 4):
            bloqueantes.append(
                Observacion(
                    "CATEGORIA_GANADORA_INVALIDA",
                    "La categoría ganadora de Premio Extra debe ser 6, 5 o 4 aciertos, "
                    'o "sin ganadores".',
                )
            )
    elif aciertos_categoria_ganadora is not None:
        bloqueantes.append(
            Observacion(
                "CATEGORIA_GANADORA_INVALIDA",
                f"{modalidad.nombre} no tiene categoría ganadora variable.",
            )
        )

    if sin_ganadores:
        if modalidad is not Modalidad.PREMIO_EXTRA:
            bloqueantes.append(
                Observacion(
                    "SIN_GANADORES_NO_APLICA",
                    "Solo Premio Extra puede informar que no hubo ganadores.",
                )
            )
        elif aciertos_categoria_ganadora is not None:
            bloqueantes.append(
                Observacion(
                    "SIN_GANADORES_CON_CATEGORIA",
                    MENSAJES["admin.sin_ganadores_y_categoria"],
                )
            )

    bloqueantes.extend(_revisar_fuente(fuente))
    return bloqueantes, advertencias
