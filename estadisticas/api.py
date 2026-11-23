"""Estadísticas en la API v1 ([003] contracts/api.md § Estadísticas, pantalla 2, T183).

Delgada sobre ``dominio/estadisticas.py``: la misma lectura de la consulta que la vista HTML
(``EstadisticasForm``), los mismos cálculos y los mismos mensajes (NFR-009). Con errores responde
``422`` con los errores por campo y, en ``resultado``, la consulta anterior ([001] AC-6.8).
"""

from __future__ import annotations

from datetime import date

from django.http import QueryDict
from ninja import Router, Schema

from dominio.estadisticas import PERIODO_INVALIDO, Frecuencias, calcular_frecuencias
from dominio.mensajes import MENSAJES
from estadisticas.forms import MODALIDADES, Consulta, EstadisticasForm
from quini6.api_base import ProblemaAPI, nivel
from resultados import consultas

router = Router(tags=["Estadísticas"])

_CLAVE_DE_TEXTO = {texto: clave for clave, texto in MENSAJES.items()}


class ConsultaEstadistica(Schema):
    modalidad: str
    modalidad_nombre: str
    desde: date | None
    hasta: date | None
    numero: int | None


class ModalidadEstadistica(Schema):
    valor: str
    nombre: str


class FrecuenciaNumero(Schema):
    numero: int
    frecuencia: int
    porcentaje: str


class FrecuenciasDTO(Schema):
    consulta: ConsultaEstadistica
    modalidades: list[ModalidadEstadistica]
    cantidad_sorteos: int
    primera_fecha: date | None
    ultima_fecha: date | None
    sorteos_sin_informacion: int
    numeros: list[FrecuenciaNumero]
    numero_consultado: FrecuenciaNumero | None
    avisos: list[str]


def _numero(f) -> dict:
    return {"numero": f.numero, "frecuencia": f.frecuencia, "porcentaje": f"{f.porcentaje:.2f}"}


def frecuencias_de(consulta: Consulta, avisos: list[str]) -> dict:
    """``Frecuencias`` de una consulta válida (contracts/api.md § "Pantalla 2")."""
    resultado = calcular_frecuencias(
        consultas.sorteos_publicados(consulta.modalidad, consulta.desde, consulta.hasta),
        consultas.concursos_sin_informacion(consulta.modalidad, consulta.desde, consulta.hasta),
        consulta.desde,
        consulta.hasta,
    )
    frecuencias = resultado if isinstance(resultado, Frecuencias) else None
    numero = None
    if frecuencias is not None and consulta.numero is not None:
        numero = _numero(frecuencias.numero(consulta.numero))
    return {
        "consulta": {
            "modalidad": consulta.modalidad.value,
            "modalidad_nombre": consulta.modalidad.nombre,
            "desde": consulta.desde,
            "hasta": consulta.hasta,
            "numero": consulta.numero,
        },
        "modalidades": [{"valor": m.value, "nombre": m.nombre} for m in MODALIDADES],
        "cantidad_sorteos": frecuencias.cantidad_sorteos if frecuencias else 0,
        "primera_fecha": frecuencias.primera_fecha if frecuencias else None,
        "ultima_fecha": frecuencias.ultima_fecha if frecuencias else None,
        "sorteos_sin_informacion": getattr(resultado, "concursos_sin_informacion", 0),
        "numeros": [_numero(f) for f in frecuencias.numeros] if frecuencias else [],
        "numero_consultado": numero,
        "avisos": list(avisos),
    }


@router.get("/estadisticas/", response=FrecuenciasDTO)
@nivel("P")
def frecuencias(
    request,
    modalidad: str = "",
    desde: str = "",
    hasta: str = "",
    numero: str = "",
    anterior_modalidad: str = "",
    anterior_desde: str = "",
    anterior_hasta: str = "",
    anterior_numero: str = "",
):
    """[001] AC-6.1 a AC-6.11, RN-41, RN-46, RN-47; [003] AC-7.6."""
    datos = QueryDict(mutable=True)
    for nombre, valor in {
        "modalidad": modalidad,
        "desde": desde,
        "hasta": hasta,
        "numero": numero,
        "anterior_modalidad": anterior_modalidad,
        "anterior_desde": anterior_desde,
        "anterior_hasta": anterior_hasta,
        "anterior_numero": anterior_numero,
    }.items():
        datos[nombre] = valor
    form = EstadisticasForm(datos)
    consulta, errores = form.consulta_actual()
    if not errores:
        return frecuencias_de(consulta, form.avisos)
    generales = [PERIODO_INVALIDO if e == "PERIODO_INVALIDO" else e for e in errores]
    anterior = FrecuenciasDTO(**frecuencias_de(form.consulta_anterior(), form.avisos))
    raise ProblemaAPI(
        422,
        _CLAVE_DE_TEXTO.get(generales[0], "api.detalle_validacion"),  # [001] AC-6.8
        tipo="validacion",
        errores=[
            {"campo": c, "codigo": form.claves_campo.get(c, "api.dato_invalido"), "mensaje": t}
            for c, t in form.errores_campo.items()
        ],
        resultado=anterior.model_dump(mode="json"),
    )
