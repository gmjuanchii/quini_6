"""Atajos de período ([003] RN-04, data-model § 2). Sin dependencias de Django.

"Hoy" lo calcula siempre el servidor en America/Argentina/Buenos_Aires y se recibe como parámetro.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Literal

from dominio.extraccion.periodo import parsear_fecha

Formulario = Literal["extraccion", "estadisticas"]

_CLAVES_TEXTO = {
    "anio_en_curso": "ext.atajo_anio_en_curso",
    "anio_anterior": "ext.atajo_anio_anterior",
    "todo_el_historial": "est.atajo_todo",
}


@dataclass(frozen=True)
class Atajo:
    clave: str
    desde: date
    hasta: date

    @property
    def clave_texto(self) -> str:
        return _CLAVES_TEXTO[self.clave]


def atajos(hoy: date, formulario: Formulario, primer_sorteo: date | None) -> list[Atajo]:
    """Atajos de cada formulario: la extracción histórica ofrece "Año en curso" y "Año anterior"
    (ambos dentro de los 12 meses de [002] RN-04); Estadísticas, además, "Todo el historial"
    desde el primer sorteo publicado (se omite si no hay ninguno)."""
    lista = [
        Atajo("anio_en_curso", date(hoy.year, 1, 1), hoy),
        Atajo("anio_anterior", date(hoy.year - 1, 1, 1), date(hoy.year - 1, 12, 31)),
    ]
    if formulario == "estadisticas" and primer_sorteo is not None:
        lista.append(Atajo("todo_el_historial", primer_sorteo, hoy))
    return lista


def buscar(lista: list[Atajo], clave: str | None) -> Atajo | None:
    """Atajo de la dirección (``?atajo=anio_anterior``); desconocido → ``None``."""
    return next((a for a in lista if a.clave == clave), None)


_CON_FORMA_DE_FECHA = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$|^(\d{4})-(\d{2})-(\d{2})$")


def error_de_fecha(texto: str | None, clave_falta: str | None = None) -> tuple[str, dict] | None:
    """Clave del catálogo (y sus valores) para una fecha mal escrita ([003] AC-4.5, FR-012).

    Vacía → ``clave_falta`` (si el campo es obligatorio); con forma de fecha pero imposible
    (31/02/2025, 29/02/2025) → ``fecha.inexistente`` con la fecha escrita en ``dd/mm/aaaa``;
    otro texto → ``gral.fecha_invalida``; válida → ``None``. Acepta ``dd/mm/aaaa`` y
    ``AAAA-MM-DD`` como ``parsear_fecha`` ([002] RN-02): las reglas no cambian.
    """
    texto = (texto or "").strip()
    if not texto:
        return (clave_falta, {}) if clave_falta else None
    if parsear_fecha(texto) is not None:
        return None
    forma = _CON_FORMA_DE_FECHA.match(texto)
    if forma is None:
        return ("gral.fecha_invalida", {})
    if forma.group(1):
        dia, mes, anio = forma.group(1), forma.group(2), forma.group(3)
    else:
        anio, mes, dia = forma.group(4), forma.group(5), forma.group(6)
    return ("fecha.inexistente", {"fecha": f"{int(dia):02d}/{int(mes):02d}/{anio}"})
