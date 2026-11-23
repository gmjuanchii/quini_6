"""Estadísticas públicas de frecuencia (US6, FR-026 a FR-028). Sin sesión.

[003] HU-07: etiquetas breves, bloque "Consultar un número", validación previa del número y tabla
ordenable por enlaces (AC-7.1 a AC-7.6). El orden es solo presentación: los cálculos siguen en
``dominio/estadisticas.py`` sin cambios (NFR-009).
"""

import json
from urllib.parse import urlencode

from django.shortcuts import render

from dominio import periodos
from dominio.estadisticas import PERIODO_INVALIDO, Frecuencias, calcular_frecuencias
from estadisticas.forms import (
    COLUMNAS_ORDEN,
    MODALIDADES,
    ORDEN_PREDETERMINADO,
    Consulta,
    EstadisticasForm,
)
from quini6 import fechas, tablas
from resultados import consultas

#: RN-05: nombres únicos de columnas.
COLUMNAS = [
    ("numero", "Número"),
    ("frecuencia", "Frecuencia", "derecha"),
    ("porcentaje", "Porcentaje", "derecha"),  # mismo orden que Frecuencia: no se ofrece
]

ANCHO_BARRA = 10
ALTO_GRAFICO = 120
MARGEN_INFERIOR = 22


def _grafico(frecuencias: Frecuencias, consultado: int | None) -> dict:
    """Barras SVG calculadas en el servidor, con alto proporcional al máximo (R-11)."""
    maximo = frecuencias.frecuencia_maxima or 1
    barras = []
    for f in frecuencias.numeros:
        alto = round(ALTO_GRAFICO * f.frecuencia / maximo, 2)
        barras.append(
            {
                "numero": f.numero,
                "frecuencia": f.frecuencia,
                "x": f.numero * ANCHO_BARRA + 1,
                "x_texto": f.numero * ANCHO_BARRA + ANCHO_BARRA / 2,
                "y": round(ALTO_GRAFICO - alto, 2),
                "alto": alto,
                "ancho": ANCHO_BARRA - 2,
                "consultado": f.numero == consultado,
                "rotulo": f.numero % 5 == 0 or f.numero == consultado,
            }
        )
    return {
        "barras": barras,
        "ancho": len(barras) * ANCHO_BARRA,
        "alto": ALTO_GRAFICO + MARGEN_INFERIOR,
        "base": ALTO_GRAFICO,
        "y_texto": ALTO_GRAFICO + 14,
    }


def _con_atajo(datos, atajos: list[periodos.Atajo]):
    """[003] AC-4.4: ``?atajo=<clave>`` (sin scripts) precarga el período y lo consulta."""
    atajo = periodos.buscar(atajos, datos.get("atajo"))
    if atajo is None or datos.get("desde") or datos.get("hasta"):
        return datos
    datos = datos.copy()
    datos["desde"] = atajo.desde.strftime("%d/%m/%Y")
    datos["hasta"] = atajo.hasta.strftime("%d/%m/%Y")
    return datos


def _campos_periodo(valores: dict, errores: dict) -> dict:
    """DateRangePicker de Estadísticas ([003] FR-010, FR-011, FR-022): etiquetas breves."""
    desde = {"nombre": "desde", "id": "est-desde", "etiqueta": "Desde"}
    hasta = {"nombre": "hasta", "id": "est-hasta", "etiqueta": "Hasta"}
    reglas_hasta = [
        fechas.regla_fecha(),
        fechas.regla("fin_no_anterior_a", "fecha.fin_anterior", campo="est-desde"),
    ]
    return {
        "desde": {
            **desde,
            "valor": valores["desde"],
            "error": errores.get("desde", ""),
            "reglas": [fechas.regla_fecha()],
        },
        "hasta": {
            **hasta,
            "valor": valores["hasta"],
            "error": errores.get("hasta", ""),
            "reglas": reglas_hasta,
        },
    }


def _ordenar(frecuencias: Frecuencias, orden: str) -> list:
    """Filas de la tabla en el orden pedido; los empates, por número ascendente (AC-7.5)."""
    filas = list(frecuencias.numeros)
    if orden.lstrip("-") == "frecuencia":
        filas.sort(key=lambda f: f.numero)
        filas.sort(key=lambda f: f.frecuencia, reverse=orden.startswith("-"))
    else:
        filas.sort(key=lambda f: f.numero, reverse=orden.startswith("-"))
    return filas


def _parametros(consulta: Consulta) -> dict[str, str]:
    """La consulta mostrada (válida) para los enlaces de orden: nunca la entrada con errores."""
    return tablas.parametros_de(
        {
            "modalidad": consulta.modalidad.value,
            "desde": consulta.desde.strftime("%d/%m/%Y") if consulta.desde else "",
            "hasta": consulta.hasta.strftime("%d/%m/%Y") if consulta.hasta else "",
            "numero": f"{consulta.numero:02d}" if consulta.numero is not None else "",
        }
    )


def _campo_numero(valor: str, error: str) -> dict:
    """ "Número" con su ayuda y la regla previa del rango (AC-7.3, AC-7.6, FR-033)."""
    reglas = [fechas.regla("rango_00_45", "jugada.fuera_de_rango")]
    return {
        "valor": valor,
        "error": error,
        "reglas": json.dumps(reglas, ensure_ascii=False),
    }


def index(request):
    atajos = periodos.atajos(
        fechas.hoy_buenos_aires(), "estadisticas", consultas.fecha_primer_sorteo_publicado()
    )
    form = EstadisticasForm(_con_atajo(request.GET, atajos))
    consulta, errores = form.consulta_actual()
    mensajes_error = []
    if errores:
        mensajes_error = [PERIODO_INVALIDO if e == "PERIODO_INVALIDO" else e for e in errores]
        consulta = form.consulta_anterior()  # AC-6.8: se repite la consulta anterior

    resultado = calcular_frecuencias(
        consultas.sorteos_publicados(consulta.modalidad, consulta.desde, consulta.hasta),
        consultas.concursos_sin_informacion(consulta.modalidad, consulta.desde, consulta.hasta),
        consulta.desde,
        consulta.hasta,
    )
    frecuencias = resultado if isinstance(resultado, Frecuencias) else None
    contexto = {
        "consulta": consulta,
        "modalidades": MODALIDADES,
        "errores": mensajes_error,
        "avisos": form.avisos,
        "ocultos": consulta.valores_ocultos,
        "frecuencias": frecuencias,
        "sin_informacion": resultado.concursos_sin_informacion
        if hasattr(resultado, "concursos_sin_informacion")
        else 0,
        "valores": {
            "desde": consulta.desde.strftime("%d/%m/%Y") if consulta.desde else "",
            "hasta": consulta.hasta.strftime("%d/%m/%Y") if consulta.hasta else "",
            "numero": f"{consulta.numero:02d}" if consulta.numero is not None else "",
        },
    }
    contexto["periodo"] = _campos_periodo(contexto["valores"], form.errores_campo)
    numero_escrito = (request.GET.get("numero") or "").strip()
    error_numero = form.errores_campo.get("numero", "")
    contexto["numero"] = _campo_numero(
        numero_escrito if error_numero else contexto["valores"]["numero"], error_numero
    )
    contexto["atajos"] = atajos
    contexto["parametros_atajo"] = "&" + urlencode({"modalidad": consulta.modalidad.value})
    orden = tablas.orden_valido(request.GET.get("orden"), COLUMNAS_ORDEN, ORDEN_PREDETERMINADO)
    contexto["orden"] = orden
    contexto["ocultos"] = {**consulta.valores_ocultos, "orden": orden}
    if frecuencias is not None:
        contexto["filas"] = _ordenar(frecuencias, orden)
        contexto["encabezados"] = tablas.encabezados(
            _parametros(consulta), COLUMNAS, orden, ordenables=COLUMNAS_ORDEN
        )
        contexto["grafico"] = _grafico(frecuencias, consulta.numero)
        if consulta.numero is not None:
            contexto["numero_consultado"] = frecuencias.numero(consulta.numero)
    return render(request, "estadisticas/index.html", contexto)
