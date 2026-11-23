"""Lecturas de la extracción histórica para las pantallas ([002] contracts/rutas.md).

Convierte lo guardado en estructuras simples para las plantillas. Cada dato lleva su tipo para
que la plantilla aplique el filtro de formato argentino que corresponde (Const. VII).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Case, Exists, F, IntegerField, OuterRef, Q, QuerySet, Value, When
from django.http import Http404
from django.shortcuts import get_object_or_404

from dominio.extraccion.clasificacion import NO_INFORMADA
from dominio.extraccion.etiqueta import EtiquetaEstado, etiqueta_de
from dominio.extraccion.tipos import (
    MODALIDADES_PROPIAS,
    ORDEN_FUENTES,
    DatoConsolidado,
    EstadoDato,
    EstadoExtraccion,
    EstadoSorteo,
    ResultadoIntento,
    Valor,
    nombre_categoria,
    nombre_modalidad,
)
from dominio.mensajes import mensaje
from dominio.tipos import ORDEN_MODALIDADES
from extracciones.models import Extraccion, SorteoExtraido
from extracciones.serializacion import observaciones_de_json, sorteo_de_json
from quini6.tablas import Pagina, paginar

_CLASE_ESTADO_SORTEO = {
    EstadoSorteo.RECUPERADO.value: "estado--con-premio",
    EstadoSorteo.PARCIAL.value: "estado--pendiente",
    EstadoSorteo.CON_INCONSISTENCIAS.value: "estado--revision",
    EstadoSorteo.NO_RECUPERADO.value: "estado--revision",
}
_CLASE_ESTADO_EXTRACCION = {
    EstadoExtraccion.EN_CURSO.value: "mensaje--info",
    EstadoExtraccion.FINALIZADA.value: "mensaje--exito",
    EstadoExtraccion.CON_ADVERTENCIAS.value: "mensaje--aviso",
    EstadoExtraccion.SIN_SORTEOS.value: "mensaje--info",
}
_CLASE_RESULTADO = {
    ResultadoIntento.OBTENIDO.value: "estado--con-premio",
    ResultadoIntento.FUERA_DE_COBERTURA.value: "estado--sin-premio",
    ResultadoIntento.NO_REQUERIDA.value: "estado--sin-premio",
    ResultadoIntento.INCOMPLETO.value: "estado--pendiente",
}
CAMPOS_PREMIO = (
    ("aciertos", "Aciertos"),
    ("ganadores", "Ganadores"),
    ("pozo_destinado", "Pozo destinado"),
    ("importe_individual", "Importe individual"),
)


# -- Valores --------------------------------------------------------------------


def valor_para_pantalla(v) -> dict:
    """``{"tipo": …, "valor": …}``: la plantilla elige el filtro según el tipo."""
    if isinstance(v, bool):
        return {"tipo": "texto", "valor": "Sí" if v else "No"}
    if isinstance(v, int):
        return {"tipo": "entero", "valor": v}
    if isinstance(v, Decimal):
        return {"tipo": "importe", "valor": v}
    if isinstance(v, date):
        return {"tipo": "fecha", "valor": v}
    if isinstance(v, frozenset | set):
        return {"tipo": "numeros", "valor": sorted(v)}
    return {"tipo": "texto", "valor": str(v)}


def dato_para_pantalla(dato) -> dict:
    if isinstance(dato, Valor):
        return valor_para_pantalla(dato.v)
    if isinstance(dato, EstadoDato):
        return {"tipo": "estado", "valor": dato.texto}
    return {"tipo": "estado", "valor": EstadoDato.NO_DISPONIBLE.texto}


def _diferencia_para_pantalla(diferencia) -> dict | None:
    if diferencia is None:
        return None
    return {
        "tipo": diferencia.tipo.texto,
        "valores": [
            {
                "fuente": fuente.nombre,
                "valor": (
                    {"tipo": "estado", "valor": EstadoDato.NO_DISPONIBLE.texto}
                    if v is None
                    else valor_para_pantalla(v)
                ),
            }
            for fuente, v in diferencia.valores
        ],
    }


def consolidado_para_pantalla(d: DatoConsolidado) -> dict:
    """``calculo``: texto del cálculo del sistema (RN-12, RN-18); ``diferencia_tolerada``: nota
    informativa de una diferencia de importes menor al 1 % (RN-30)."""
    return {
        **dato_para_pantalla(d.dato),
        "fuentes": [f.nombre for f in d.fuentes],
        "sin_corroborar": d.sin_corroborar,
        "discrepancia": _diferencia_para_pantalla(d.discrepancia),
        "diferencia_tolerada": _diferencia_para_pantalla(d.diferencia_tolerada),
        "calculo": d.calculo if isinstance(d.dato, Valor) else None,
    }


# -- Extracciones ---------------------------------------------------------------


_EN_CURSO = EstadoExtraccion.EN_CURSO.value
_FINALIZADA = EstadoExtraccion.FINALIZADA.value
_CON_ADVERTENCIAS = EstadoExtraccion.CON_ADVERTENCIAS.value
_SIN_SORTEOS = EstadoExtraccion.SIN_SORTEOS.value

#: [003] R-08: condición del ORM de cada etiqueta (sobre la anotación ``tiene_no_recuperados``).
_FILTRO_ETIQUETA = {
    EtiquetaEstado.EN_CURSO: Q(estado=_EN_CURSO),
    EtiquetaEstado.FINALIZADA: Q(estado=_FINALIZADA, tiene_no_recuperados=False),
    EtiquetaEstado.CON_ADVERTENCIAS: Q(estado=_CON_ADVERTENCIAS, tiene_no_recuperados=False),
    EtiquetaEstado.SIN_SORTEOS: Q(estado=_SIN_SORTEOS),
    EtiquetaEstado.CON_ERROR: Q(
        estado__in=[_FINALIZADA, _CON_ADVERTENCIAS], tiene_no_recuperados=True
    ),
}


def _con_no_recuperados(qs: QuerySet) -> QuerySet:
    """Anota si algún sorteo quedó "No recuperado" (subconsulta portable, sin leer JSON)."""
    return qs.annotate(
        tiene_no_recuperados=Exists(
            SorteoExtraido.objects.filter(
                extraccion=OuterRef("pk"), estado=EstadoSorteo.NO_RECUPERADO.value
            )
        )
    )


def etiqueta_de_extraccion(extraccion: Extraccion) -> EtiquetaEstado:
    tiene = getattr(extraccion, "tiene_no_recuperados", None)
    if tiene is None:
        tiene = extraccion.sorteos.filter(estado=EstadoSorteo.NO_RECUPERADO.value).exists()
    return etiqueta_de(extraccion.estado_enum, bool(tiene))


#: [003] AC-9.1, data-model § 2: columnas ordenables del listado y su orden predeterminado.
COLUMNAS_ORDEN = ("fecha", "periodo", "estado")
ORDEN_PREDETERMINADO = "-fecha"  # [002] RN-44: de la más reciente a la más antigua


def _orden_estado():
    """Rango de la etiqueta (EN_CURSO < CON_ERROR < CON_ADVERTENCIAS < SIN_SORTEOS < FINALIZADA)
    con expresiones del ORM, sin leer ningún JSONField ([002] R-08)."""
    return Case(
        *[When(_FILTRO_ETIQUETA[e], then=Value(e.orden)) for e in EtiquetaEstado],
        default=Value(len(EtiquetaEstado)),
        output_field=IntegerField(),
    )


def _campos_orden(orden: str) -> list:
    descendente = orden.startswith("-")
    columna = orden.lstrip("-")
    if columna == "estado":
        expresiones = [F("rango_estado")]
    elif columna == "periodo":
        expresiones = [F("desde"), F("hasta")]
    else:
        expresiones = [F("iniciada_en")]
    campos = [e.desc() if descendente else e.asc() for e in expresiones]
    return [*campos, F("id").desc()]  # data-model § 2: todos desempatan por -id


def listado_extracciones(
    filtro: EtiquetaEstado | None = None,
    orden: str = ORDEN_PREDETERMINADO,
    pagina: int | str | None = 1,
) -> Pagina:
    """AC-1.14: con quién la ejecutó; por defecto, de la más reciente a la más antigua.

    [003] AC-1.1, AC-1.4: cada fila con su ``etiqueta`` (RN-01) y, si se indica, solo las de una
    etiqueta. [003] AC-9.1, AC-9.2, RN-07: ordenado por ``fecha``, ``periodo`` o ``estado``
    (ascendente o con ``-``; inválido → ``-fecha``) y paginado de a 20 (fuera de rango → la última).
    """
    if orden.lstrip("-") not in COLUMNAS_ORDEN:
        orden = ORDEN_PREDETERMINADO
    qs = _con_no_recuperados(Extraccion.objects.select_related("creada_por"))
    if filtro is not None:
        qs = qs.filter(_FILTRO_ETIQUETA[filtro])
    qs = qs.annotate(rango_estado=_orden_estado()).order_by(*_campos_orden(orden))
    resultado = paginar(qs, pagina, orden=orden, filtro=filtro)
    for extraccion in resultado.elementos:
        extraccion.etiqueta = etiqueta_de_extraccion(extraccion)
    return resultado


def obtener_extraccion(id_extraccion: int) -> Extraccion:
    return get_object_or_404(Extraccion, pk=id_extraccion)


#: [003] AC-3.3: aviso al terminar según la etiqueta → (clave, tipo de aviso de RN-09).
_AVISO_FINAL = {
    EtiquetaEstado.FINALIZADA: ("ext.termino_finalizada", "success"),
    EtiquetaEstado.CON_ADVERTENCIAS: ("ext.termino_advertencias", "warning"),
    EtiquetaEstado.CON_ERROR: ("ext.termino_error", "error"),
    EtiquetaEstado.SIN_SORTEOS: ("ext.termino_sin_sorteos", "info"),
}


def _aviso_final(extraccion: Extraccion, etiqueta: EtiquetaEstado) -> dict | None:
    if etiqueta is EtiquetaEstado.EN_CURSO:
        return None
    clave, tipo = _AVISO_FINAL[etiqueta]
    por_estado = (extraccion.resumen or {}).get("por_estado", {})
    if etiqueta is EtiquetaEstado.CON_ERROR:
        texto = mensaje(clave, n=por_estado.get(EstadoSorteo.NO_RECUPERADO.value, 0))
    elif etiqueta is EtiquetaEstado.CON_ADVERTENCIAS:
        a_revisar = sum(n for e, n in por_estado.items() if e != EstadoSorteo.RECUPERADO.value)
        texto = mensaje(clave, n=a_revisar)
    else:
        texto = mensaje(clave)
    enlace = f"/administracion/extracciones/{extraccion.pk}/"
    return {"tipo": tipo, "texto": texto, "enlace": enlace}


def avance(extraccion: Extraccion) -> dict:
    etiqueta = etiqueta_de_extraccion(extraccion)
    return {
        "en_curso": extraccion.en_curso,
        "identificando": extraccion.identificando,
        "procesados": extraccion.procesados,
        "total": extraccion.total_identificados,
        "etiqueta": etiqueta,
        "aviso_final": _aviso_final(extraccion, etiqueta),
    }


def ninguna_fuente_respondio(extraccion: Extraccion) -> bool:
    """[003] AC-3.4: terminó y ninguna fuente aportó sorteos ([002] RN-33)."""
    fuentes = (extraccion.resumen or {}).get("fuentes") or []
    return bool(fuentes) and all(not f.get("aportados") for f in fuentes)


def _resumen_para_pantalla(resumen: dict) -> dict:
    fuentes = [
        {
            **f,
            "fallidos": [
                {"texto": ResultadoIntento(clave).texto, "cantidad": n}
                for clave, n in f.get("fallidos", {}).items()
            ],
        }
        for f in resumen.get("fuentes", [])
    ]
    a_revisar = [
        {
            **s,
            "fecha": date.fromisoformat(s["fecha"]) if s.get("fecha") else None,
            "estado_texto": EstadoSorteo(s["estado"]).texto,
            "clase": _CLASE_ESTADO_SORTEO[s["estado"]],
        }
        for s in resumen.get("a_revisar", [])
    ]
    por_estado = resumen.get("por_estado", {})
    return {
        "identificados": resumen.get("identificados", 0),
        "recuperados": por_estado.get(EstadoSorteo.RECUPERADO.value, 0),
        "parciales": por_estado.get(EstadoSorteo.PARCIAL.value, 0),
        "inconsistencias": por_estado.get(EstadoSorteo.CON_INCONSISTENCIAS.value, 0),
        "no_recuperados": por_estado.get(EstadoSorteo.NO_RECUPERADO.value, 0),
        "fuentes": fuentes,
        "huecos": resumen.get("huecos", []),
        "a_revisar": a_revisar,
    }


def datos_pagina(extraccion: Extraccion) -> dict:
    estado = extraccion.estado_enum
    datos = {
        "extraccion": extraccion,
        "estado_texto": estado.texto,
        "clase_estado": _CLASE_ESTADO_EXTRACCION[estado.value],
        "etiqueta": etiqueta_de_extraccion(extraccion),
        "ninguna_fuente": ninguna_fuente_respondio(extraccion),
        "avance": avance(extraccion),
        "terminada": not extraccion.en_curso,
        "sin_sorteos": estado is EstadoExtraccion.SIN_SORTEOS,
        "resumen": None,
        "sorteos": [],
        "puede_descargar": puede_descargar(extraccion),
    }
    # Los sorteos ya procesados se pueden abrir aunque la extracción siga en curso.
    datos["sorteos"] = [
        {
            "numero": s.numero,
            "fecha": s.fecha,
            "estado_texto": s.estado_enum.texto,
            "clase": _CLASE_ESTADO_SORTEO[s.estado],
        }
        for s in extraccion.sorteos.order_by("numero")
    ]
    terminada_con_sorteos = not extraccion.en_curso and estado is not EstadoExtraccion.SIN_SORTEOS
    if terminada_con_sorteos and extraccion.resumen:
        datos["resumen"] = _resumen_para_pantalla(extraccion.resumen)
    return datos


def puede_descargar(extraccion: Extraccion) -> bool:
    """AC-1.10, AC-5.1: terminada y con al menos un sorteo identificado."""
    return (
        not extraccion.en_curso
        and extraccion.estado != EstadoExtraccion.SIN_SORTEOS.value
        and bool(extraccion.archivo_csv)
    )


# -- Detalle de un sorteo ----------------------------------------------------------


def detalle_sorteo(extraccion: Extraccion, numero: int) -> dict:
    """Disponible desde que el sorteo se procesó, aunque la extracción siga en curso."""
    fila = (
        SorteoExtraido.objects.filter(extraccion=extraccion, numero=numero)
        .prefetch_related("intentos")
        .first()
    )
    if fila is None:
        raise Http404(mensaje("gral.pagina_inexistente"))
    sorteo = sorteo_de_json(fila.consolidado)
    intentos = {i.fuente: i for i in fila.intentos.all()}
    fuentes = []
    for fuente in ORDEN_FUENTES:
        intento = intentos.get(fuente.value)
        if intento is None:
            continue
        fuentes.append(
            {
                "nombre": fuente.nombre,
                "resultado": intento.resultado_enum.texto,
                "clase": _CLASE_RESULTADO.get(intento.resultado, "estado--revision"),
                "url": intento.url,
                "consultado_en": intento.consultado_en,
                "observaciones": [o.texto for o in observaciones_de_json(intento.observaciones)],
            }
        )
    modalidades = []
    for modalidad in ORDEN_MODALIDADES:
        mc = sorteo.modalidades.get(modalidad)
        if mc is None:
            continue
        categorias = []
        for codigo, cat in mc.categorias.items():
            categorias.append(
                {
                    "nombre": nombre_categoria(codigo),
                    "estado_pozo": cat.estado_pozo.texto,
                    "datos": [
                        {"rotulo": rotulo, **consolidado_para_pantalla(getattr(cat, campo))}
                        for campo, rotulo in CAMPOS_PREMIO
                    ],
                }
            )
        modalidades.append(
            {
                "nombre": nombre_modalidad(modalidad),  # [002] RN-11, D-15
                "informada": mc.informada,
                "propia": modalidad in MODALIDADES_PROPIAS,
                "numeros": consolidado_para_pantalla(mc.numeros),
                "categorias": categorias,
            }
        )
    return {
        "extraccion": extraccion,
        "numero": sorteo.numero,
        "fecha": consolidado_para_pantalla(sorteo.fecha),
        "estado_texto": sorteo.estado.texto,
        "clase_estado": _CLASE_ESTADO_SORTEO[sorteo.estado.value],
        "motivos": list(sorteo.motivos),
        "combina_fuentes": sorteo.combina_fuentes,
        "sin_corroborar": sorteo.sin_corroborar,
        "reglas_no_verificadas": sorteo.reglas_no_verificadas,
        "fuentes": fuentes,
        "modalidades": modalidades,
        "no_informada": NO_INFORMADA,
        "observaciones": [
            {"fuente": o.fuente.nombre if o.fuente else None, "texto": o.texto}
            for o in sorteo.observaciones
        ],
    }


def archivo(extraccion: Extraccion) -> tuple[str, str]:
    if not puede_descargar(extraccion):
        raise Http404(mensaje("gral.pagina_inexistente"))
    return extraccion.nombre_archivo, extraccion.archivo_csv
