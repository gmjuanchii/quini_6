"""Conversión entre los tipos del dominio de la extracción y JSON ([002] R-08).

Cada ``Dato`` se guarda con su estado explícito. Los importes van como texto decimal con
``dominio.importes.a_texto_decimal``, nunca como ``float``; las fechas en ISO y los conjuntos de
números como listas ordenadas.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from dominio.extraccion.tipos import (
    CategoriaConsolidada,
    Dato,
    DatoConsolidado,
    DatosCategoriaFuente,
    DatosFuente,
    DatosModalidadFuente,
    Discrepancia,
    EstadoDato,
    EstadoPozo,
    EstadoSorteo,
    Fuente,
    Modalidad,
    ModalidadConsolidada,
    Observacion,
    ResultadoIntento,
    SorteoConsolidado,
    TipoDiscrepancia,
    Valor,
)
from dominio.importes import a_texto_decimal

# -- Dato ---------------------------------------------------------------------


def _valor_a_json(v) -> dict:
    if isinstance(v, bool):
        return {"tipo": "booleano", "valor": v}
    if isinstance(v, int):
        return {"tipo": "entero", "valor": v}
    if isinstance(v, Decimal):
        return {"tipo": "decimal", "valor": a_texto_decimal(v)}
    if isinstance(v, date):
        return {"tipo": "fecha", "valor": v.isoformat()}
    if isinstance(v, frozenset | set):
        return {"tipo": "numeros", "valor": sorted(v)}
    if isinstance(v, str):
        return {"tipo": "texto", "valor": v}
    raise TypeError(f"Tipo de valor no admitido: {type(v).__name__}")


def _valor_de_json(datos: dict):
    tipo, valor = datos["tipo"], datos["valor"]
    if tipo == "decimal":
        return Decimal(valor)
    if tipo == "fecha":
        return date.fromisoformat(valor)
    if tipo == "numeros":
        return frozenset(valor)
    return valor


def dato_a_json(dato: Dato) -> dict:
    if isinstance(dato, Valor):
        return {"estado": "valor", **_valor_a_json(dato.v)}
    return {"estado": dato.value}


def dato_de_json(datos: dict) -> Dato:
    if datos["estado"] == "valor":
        return Valor(_valor_de_json(datos))
    return EstadoDato(datos["estado"])


# -- Observaciones ------------------------------------------------------------


def observacion_a_json(o: Observacion) -> dict:
    return {
        "codigo": o.codigo,
        "texto": o.texto,
        "fuente": o.fuente.value if o.fuente else None,
        "es_inconsistencia": o.es_inconsistencia,
        "informativa": o.informativa,
        "modalidad": o.modalidad.value if o.modalidad else None,
    }


def observacion_de_json(d: dict) -> Observacion:
    return Observacion(
        codigo=d["codigo"],
        texto=d["texto"],
        fuente=Fuente(d["fuente"]) if d.get("fuente") else None,
        es_inconsistencia=d.get("es_inconsistencia", False),
        informativa=d.get("informativa", False),
        modalidad=Modalidad(d["modalidad"]) if d.get("modalidad") else None,
    )


def observaciones_a_json(observaciones) -> list[dict]:
    return [observacion_a_json(o) for o in observaciones]


def observaciones_de_json(lista) -> tuple[Observacion, ...]:
    return tuple(observacion_de_json(d) for d in lista or ())


# -- Datos de una fuente --------------------------------------------------------

_CAMPOS_CATEGORIA_FUENTE = (
    "aciertos",
    "ganadores",
    "pozo_destinado",
    "importe_individual",
)


def datos_fuente_a_json(d: DatosFuente) -> dict:
    return {
        "fuente": d.fuente.value,
        "numero": d.numero,
        "fecha": d.fecha.isoformat(),
        "modalidades": {
            m.value: {
                "numeros": sorted(md.numeros) if md.numeros is not None else None,
                "numeros_descartados": md.numeros_descartados,
                "categorias": {
                    codigo: {
                        **{c: dato_a_json(getattr(cat, c)) for c in _CAMPOS_CATEGORIA_FUENTE},
                        "texto_original": cat.texto_original,
                    }
                    for codigo, cat in md.categorias.items()
                },
            }
            for m, md in d.modalidades.items()
        },
        "observaciones": observaciones_a_json(d.observaciones),
    }


def datos_fuente_de_json(d: dict) -> DatosFuente:
    modalidades = {}
    for clave, md in d["modalidades"].items():
        categorias = {
            codigo: DatosCategoriaFuente(
                **{c: dato_de_json(cat[c]) for c in _CAMPOS_CATEGORIA_FUENTE},
                texto_original=cat.get("texto_original"),
            )
            for codigo, cat in md["categorias"].items()
        }
        numeros = frozenset(md["numeros"]) if md["numeros"] is not None else None
        modalidades[Modalidad(clave)] = DatosModalidadFuente(
            numeros=numeros,
            categorias=categorias,
            numeros_descartados=md.get("numeros_descartados", False),
        )
    return DatosFuente(
        fuente=Fuente(d["fuente"]),
        numero=d["numero"],
        fecha=date.fromisoformat(d["fecha"]),
        modalidades=modalidades,
        observaciones=observaciones_de_json(d.get("observaciones")),
    )


# -- Consolidado ------------------------------------------------------------------


def _discrepancia_a_json(d: Discrepancia | None) -> dict | None:
    if d is None:
        return None
    return {
        "tipo": d.tipo.value,
        "valores": [
            {"fuente": f.value, "valor": None if v is None else _valor_a_json(v)}
            for f, v in d.valores
        ],
    }


def _discrepancia_de_json(d: dict | None) -> Discrepancia | None:
    if not d:
        return None
    return Discrepancia(
        TipoDiscrepancia(d["tipo"]),
        tuple(
            (Fuente(v["fuente"]), None if v["valor"] is None else _valor_de_json(v["valor"]))
            for v in d["valores"]
        ),
    )


def dato_consolidado_a_json(d: DatoConsolidado) -> dict:
    return {
        "dato": dato_a_json(d.dato),
        "fuentes": [f.value for f in d.fuentes],
        "sin_corroborar": d.sin_corroborar,
        "discrepancia": _discrepancia_a_json(d.discrepancia),
        "diferencia_tolerada": _discrepancia_a_json(d.diferencia_tolerada),  # [002] RN-30
        "calculo": d.calculo,  # [002] RN-12, RN-18
    }


def dato_consolidado_de_json(d: dict) -> DatoConsolidado:
    """Las extracciones guardadas antes del 20/11/2026 no tienen ``diferencia_tolerada`` ni
    ``calculo``."""
    return DatoConsolidado(
        dato=dato_de_json(d["dato"]),
        fuentes=tuple(Fuente(f) for f in d["fuentes"]),
        sin_corroborar=d["sin_corroborar"],
        discrepancia=_discrepancia_de_json(d.get("discrepancia")),
        diferencia_tolerada=_discrepancia_de_json(d.get("diferencia_tolerada")),
        calculo=d.get("calculo"),
    )


#: [002] D-22: ``se_acumula`` e ``importe_trasladado`` de sorteos ya guardados se ignoran.
_CAMPOS_CATEGORIA = ("aciertos", "ganadores", "pozo_destinado", "importe_individual")


def _categoria_a_json(c: CategoriaConsolidada) -> dict:
    return {
        **{campo: dato_consolidado_a_json(getattr(c, campo)) for campo in _CAMPOS_CATEGORIA},
        "estado_pozo": c.estado_pozo.value,
    }


def _categoria_de_json(d: dict) -> CategoriaConsolidada:
    return CategoriaConsolidada(
        **{campo: dato_consolidado_de_json(d[campo]) for campo in _CAMPOS_CATEGORIA},
        estado_pozo=EstadoPozo(d["estado_pozo"]),
    )


def sorteo_a_json(s: SorteoConsolidado) -> dict:
    return {
        "numero": s.numero,
        "fecha": dato_consolidado_a_json(s.fecha),
        "modalidades": {
            m.value: {
                "informada": mc.informada,
                "numeros": dato_consolidado_a_json(mc.numeros),
                "categorias": {codigo: _categoria_a_json(c) for codigo, c in mc.categorias.items()},
            }
            for m, mc in s.modalidades.items()
        },
        "resultados": {f.value: r.value for f, r in s.resultados.items()},
        "estado": s.estado.value,
        "combina_fuentes": s.combina_fuentes,
        "sin_corroborar": s.sin_corroborar,
        "motivos": list(s.motivos),
        "observaciones": observaciones_a_json(s.observaciones),
        "reglas_no_verificadas": s.reglas_no_verificadas,
        "error_inesperado": s.error_inesperado,
    }


def sorteo_de_json(d: dict) -> SorteoConsolidado:
    return SorteoConsolidado(
        numero=d["numero"],
        fecha=dato_consolidado_de_json(d["fecha"]),
        modalidades={
            Modalidad(clave): ModalidadConsolidada(
                informada=mc["informada"],
                numeros=dato_consolidado_de_json(mc["numeros"]),
                categorias={
                    codigo: _categoria_de_json(c) for codigo, c in mc["categorias"].items()
                },
            )
            for clave, mc in d["modalidades"].items()
        },
        resultados={Fuente(f): ResultadoIntento(r) for f, r in d["resultados"].items()},
        estado=EstadoSorteo(d["estado"]),
        combina_fuentes=d["combina_fuentes"],
        sin_corroborar=d["sin_corroborar"],
        motivos=tuple(d["motivos"]),
        observaciones=observaciones_de_json(d["observaciones"]),
        reglas_no_verificadas=d["reglas_no_verificadas"],
        error_inesperado=d.get("error_inesperado", False),
    )
