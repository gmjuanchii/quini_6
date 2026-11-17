"""Estadísticas públicas de frecuencia (US6, FR-026 a FR-028). Sin sesión."""

from django.shortcuts import render

from dominio.estadisticas import PERIODO_INVALIDO, Frecuencias, calcular_frecuencias
from estadisticas.forms import MODALIDADES, EstadisticasForm
from resultados import consultas

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


def index(request):
    form = EstadisticasForm(request.GET)
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
    if frecuencias is not None:
        contexto["grafico"] = _grafico(frecuencias, consulta.numero)
        if consulta.numero is not None:
            contexto["numero_consultado"] = frecuencias.numero(consulta.numero)
    return render(request, "estadisticas/index.html", contexto)
