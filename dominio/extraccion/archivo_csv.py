"""Archivo CSV de una extracción, contrato versión 2.0 ([002] contracts/csv.md).

[002] RN-34 a RN-39, RN-43, NFR-008 a NFR-010. Función determinista: la misma entrada produce el
mismo texto. No importa Django.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable, Mapping
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from dominio.extraccion.clasificacion import NO_INFORMADA
from dominio.extraccion.tipos import (
    MODALIDADES_PROPIAS,
    NO_CORRESPONDE,
    NO_DISPONIBLE,
    CategoriaConsolidada,
    DatoConsolidado,
    Discrepancia,
    EstadoDato,
    EstadoSorteo,
    Fuente,
    Modalidad,
    Observacion,
    SorteoConsolidado,
    Valor,
    nombre_categoria,
    nombre_modalidad,
)
from dominio.numeros import formatear
from dominio.tipos import ORDEN_MODALIDADES

VERSION_CONTRATO = "3.0"  # [002] Clarifications 20/11/2026 (2.0: D-15, D-16, D-19; 3.0: D-22)
ZONA = ZoneInfo("America/Argentina/Buenos_Aires")
REGLAS_NO_VERIFICADAS = "Reglas del período no verificadas"

ENCABEZADOS = (
    "version_contrato",
    "sorteo_numero",
    "sorteo_fecha",
    "sorteo_estado",
    "sorteo_combina_fuentes",
    "sorteo_sin_corroborar",
    "sorteo_motivos",
    "modalidad",
    "numero_1",
    "numero_2",
    "numero_3",
    "numero_4",
    "numero_5",
    "numero_6",
    "categoria",
    "aciertos",
    "ganadores",
    "estado_pozo",
    "pozo_destinado",
    "importe_individual",
    "datos_sin_corroborar",
    "procedencia",
    "discrepancias",
    "observaciones",
    "numeros_pozo_extra",  # versión 2.0 (RN-12, AC-3.17)
)

#: Dato de la fila → atributo de ``CategoriaConsolidada`` ([002] contracts/csv.md, gramática).
_DATOS_CATEGORIA = (
    ("aciertos", "aciertos"),
    ("ganadores", "ganadores"),
    ("pozo_destinado", "pozo_destinado"),
    ("importe_individual", "importe_individual"),
)
_PELIGROSOS = ("=", "+", "-", "@", "\t", "\r")

#: Procedencia de cada fuente en un sorteo: (dirección consultada, fecha y hora de consulta).
Procedencia = Mapping[int, Mapping[Fuente, tuple[str, datetime | None]]]


def nombre_archivo(id_extraccion: int, desde: date, hasta: date) -> str:
    """``quini6-extraccion-{id}-{AAAA-MM-DD}-a-{AAAA-MM-DD}.csv`` ([002] R-09, AC-5.1)."""
    return f"quini6-extraccion-{id_extraccion}-{desde.isoformat()}-a-{hasta.isoformat()}.csv"


def proteger(celda: str) -> str:
    """NFR-010, AC-5.9: una celda que parece una fórmula lleva un apóstrofo adelante."""
    return "'" + celda if celda.startswith(_PELIGROSOS) else celda


def formato_tecnico(valor) -> str:
    """[002] RN-38: fechas ISO, importes con punto y dos decimales, Sí/No."""
    if isinstance(valor, EstadoDato):
        return valor.texto
    if isinstance(valor, Valor):
        valor = valor.v
    if isinstance(valor, bool):
        return "Sí" if valor else "No"
    if isinstance(valor, Decimal):
        return f"{valor:.2f}"
    if isinstance(valor, datetime):
        return valor.astimezone(ZONA).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, frozenset | set):
        return " ".join(formatear(n) for n in sorted(valor))
    return str(valor)


def _si_no(valor: bool) -> str:
    return "Sí" if valor else "No"


def _texto_observacion(observacion: Observacion) -> str:
    if observacion.fuente is not None:
        return f"{observacion.fuente.nombre}: {observacion.texto}"
    return observacion.texto


def _tramo_procedencia(nombre: str, dato: DatoConsolidado, procedencia) -> str | None:
    if isinstance(dato.dato, Valor) and dato.calculo:
        return f"{nombre}: Calculado: {dato.calculo}"  # [002] RN-12, RN-18, SC-002
    if not isinstance(dato.dato, Valor) or not dato.fuentes:
        return None
    partes = []
    for fuente in dato.fuentes:
        url, momento = procedencia.get(fuente, ("", None))
        consultado = formato_tecnico(momento) if momento else "No disponible"
        partes.append(f"{fuente.nombre} {url} {consultado}")
    return f"{nombre}: " + "; ".join(partes)


def _tramo_diferencia(nombre: str, diferencia: Discrepancia | None) -> str | None:
    """``<dato>: <tipo> — <valor> (<fuente>); …`` para discrepancias y diferencias toleradas."""
    if diferencia is None:
        return None
    valores = "; ".join(
        f"{'sin dato' if valor is None else formato_tecnico(valor)} ({fuente.nombre})"
        for fuente, valor in diferencia.valores
    )
    return f"{nombre}: {diferencia.tipo.texto} — {valores}"


class _Fila:
    def __init__(self, sorteo: SorteoConsolidado, procedencia):
        self.sorteo = sorteo
        self.procedencia = procedencia
        self.datos: list[tuple[str, DatoConsolidado]] = [("sorteo_fecha", sorteo.fecha)]

    def base(self) -> dict[str, str]:
        s = self.sorteo
        return {
            "version_contrato": VERSION_CONTRATO,
            "sorteo_numero": str(s.numero),
            "sorteo_fecha": formato_tecnico(s.fecha.dato),
            "sorteo_estado": s.estado.texto,
            "sorteo_combina_fuentes": _si_no(s.combina_fuentes),
            "sorteo_sin_corroborar": _si_no(s.sin_corroborar),
            "sorteo_motivos": " | ".join(s.motivos),
        }

    def columnas_texto(self, observaciones: list[str]) -> dict[str, str]:
        procedencia = [_tramo_procedencia(n, d, self.procedencia) for n, d in self.datos]
        discrepancias = [_tramo_diferencia(n, d.discrepancia) for n, d in self.datos]
        # RN-30: una diferencia menor al 1 % es una nota informativa, no una discrepancia.
        toleradas = [_tramo_diferencia(n, d.diferencia_tolerada) for n, d in self.datos]
        return {
            "datos_sin_corroborar": "; ".join(n for n, d in self.datos if d.sin_corroborar),
            "procedencia": " | ".join(t for t in procedencia if t),
            "discrepancias": " | ".join(t for t in discrepancias if t),
            "observaciones": " | ".join([*observaciones, *(t for t in toleradas if t)]),
        }


def _numeros(modalidad: Modalidad, dato: DatoConsolidado) -> list[str]:
    if modalidad not in MODALIDADES_PROPIAS:
        return [NO_CORRESPONDE.texto] * 6
    if isinstance(dato.dato, Valor):
        return [formatear(n) for n in sorted(dato.dato.v)]
    return [dato.dato.texto] * 6


def _observaciones_de(sorteo: SorteoConsolidado, modalidad: Modalidad | None) -> list[str]:
    textos = [
        _texto_observacion(o)
        for o in sorteo.observaciones
        if o.modalidad is None or o.modalidad is modalidad
    ]
    if sorteo.reglas_no_verificadas:
        textos.append(REGLAS_NO_VERIFICADAS)
    return textos


def _fila_vacia(sorteo, procedencia, modalidad_texto, observaciones) -> dict[str, str]:
    """Fila de un sorteo "No recuperado" o de una modalidad no informada ([002] RN-39)."""
    fila = _Fila(sorteo, procedencia)
    no_disp = NO_DISPONIBLE.texto
    valores = dict.fromkeys(ENCABEZADOS[8:22], no_disp)
    return {
        **fila.base(),
        "modalidad": modalidad_texto,
        **valores,
        **fila.columnas_texto(observaciones),
        "numeros_pozo_extra": no_disp,
    }


def _filas_sorteo(sorteo: SorteoConsolidado, procedencia) -> list[dict[str, str]]:
    if sorteo.estado is EstadoSorteo.NO_RECUPERADO:
        observaciones = _observaciones_de(sorteo, None)
        return [_fila_vacia(sorteo, procedencia, NO_DISPONIBLE.texto, observaciones)]
    filas = []
    for modalidad in ORDEN_MODALIDADES:
        mc = sorteo.modalidades[modalidad]
        observaciones = _observaciones_de(sorteo, modalidad)
        if not mc.informada:
            filas.append(
                _fila_vacia(
                    sorteo, procedencia, nombre_modalidad(modalidad), [NO_INFORMADA, *observaciones]
                )
            )
            continue
        numeros = _numeros(modalidad, mc.numeros)
        for codigo, categoria in mc.categorias.items():
            filas.append(
                _fila_categoria(
                    sorteo,
                    procedencia,
                    modalidad,
                    mc.numeros,
                    numeros,
                    codigo,
                    categoria,
                    observaciones,
                )
            )
    return filas


def _fila_categoria(
    sorteo, procedencia, modalidad, dato_numeros, numeros, codigo,
    categoria: CategoriaConsolidada, observaciones,
) -> dict[str, str]:  # fmt: skip
    fila = _Fila(sorteo, procedencia)
    if modalidad in MODALIDADES_PROPIAS:
        fila.datos.append(("numeros", dato_numeros))
        numeros_pozo_extra = NO_CORRESPONDE.texto
    else:
        fila.datos.append(("numeros_pozo_extra", dato_numeros))  # RN-12, AC-3.17
        numeros_pozo_extra = formato_tecnico(dato_numeros.dato)
    for nombre, atributo in _DATOS_CATEGORIA:
        fila.datos.append((nombre, getattr(categoria, atributo)))
    valores = {
        **{f"numero_{i + 1}": numeros[i] for i in range(6)},
        "categoria": nombre_categoria(codigo),
        "aciertos": formato_tecnico(categoria.aciertos.dato),
        "ganadores": formato_tecnico(categoria.ganadores.dato),
        "estado_pozo": categoria.estado_pozo.texto,
        "pozo_destinado": formato_tecnico(categoria.pozo_destinado.dato),
        "importe_individual": formato_tecnico(categoria.importe_individual.dato),
    }
    return {
        **fila.base(),
        "modalidad": nombre_modalidad(modalidad),
        **valores,
        **fila.columnas_texto(observaciones),
        "numeros_pozo_extra": numeros_pozo_extra,
    }


def generar_csv(sorteos: Iterable[SorteoConsolidado], procedencia: Procedencia) -> str:
    """Texto exacto del archivo: UTF-8 (sin BOM al codificar), coma, ``\\r\\n``, comillas solo
    cuando hacen falta. ``procedencia[numero][fuente] = (dirección, fecha y hora)``."""
    salida = io.StringIO()
    escritor = csv.writer(salida, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
    escritor.writerow(ENCABEZADOS)
    for sorteo in sorted(sorteos, key=lambda s: s.numero):
        for fila in _filas_sorteo(sorteo, procedencia.get(sorteo.numero, {})):
            escritor.writerow([proteger(fila[columna]) for columna in ENCABEZADOS])
    return salida.getvalue()
