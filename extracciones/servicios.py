"""Servicios de la extracción histórica ([002] R-01, R-03, R-06, R-08, I-07, I-09).

``iniciar_extraccion`` lo usa la vista; ``procesar_extraccion`` lo ejecuta el trabajador
(``manage.py procesar_extracciones``). Toda regla de negocio vive en ``dominio/extraccion``: este
módulo solo orquesta consultas, lecturas y escrituras. Solo escribe en las tablas de
``extracciones`` ([002] RN-41).
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from dominio.extraccion.archivo_csv import VERSION_CONTRATO, generar_csv, nombre_archivo
from dominio.extraccion.clasificacion import aplicar_clasificacion, requiere_respaldo
from dominio.extraccion.consolidacion import (
    consolidar,
    modalidades_no_informadas,
    revisar_correlatividad,
)
from dominio.extraccion.identificacion import (
    Identificacion,
    Referencia,
    SinSorteos,
    identificar_sorteos,
)
from dominio.extraccion.normalizacion import (
    normalizar,
    parsear_fecha_fuente,
    parsear_numero_sorteo,
)
from dominio.extraccion.periodo import Periodo
from dominio.extraccion.resumen import resumir
from dominio.extraccion.tipos import (
    FUENTES_RESPALDO,
    NO_DISPONIBLE_CONSOLIDADO,
    ORDEN_FUENTES,
    DatosFuente,
    EstadoExtraccion,
    Ficha,
    Fuente,
    NoReconocida,
    Observacion,
    ResultadoIntento,
    SorteoConsolidado,
    Valor,
)
from dominio.mensajes import MENSAJES
from extracciones.cliente_http import (
    ClienteHttp,
    LimitadorPorSitio,
    RespuestaHttp,
    resultado_por_respuesta,
)
from extracciones.fuentes import f1, f2, f3
from extracciones.fuentes.fichas import PRIMER_CUBIERTO, obtener_fichas
from extracciones.models import Extraccion, IntentoConsulta, SorteoExtraido
from extracciones.serializacion import (
    datos_fuente_a_json,
    observaciones_a_json,
    sorteo_a_json,
    sorteo_de_json,
)

logger = logging.getLogger("extracciones")

OBS_ERROR_INTERPRETE = "La página de la fuente no se pudo interpretar"  # I-09 (a)

#: Fuentes con intérprete ([002] RN-06). Cada intérprete solo extrae textos (R-04).
INTERPRETES = {Fuente.F1: f1, Fuente.F2: f2, Fuente.F3: f3}


def crear_cliente_y_fichas(limitador: LimitadorPorSitio | None = None):
    """Cliente real con el limitador compartido y las fichas (con las direcciones de prueba)."""
    return ClienteHttp(limitador), obtener_fichas(settings.QUINI6_FUENTES_URL_BASE)


# ---------------------------------------------------------------------------
# Inicio (vista)
# ---------------------------------------------------------------------------


def extraccion_en_curso(usuario) -> Extraccion | None:
    return Extraccion.objects.filter(
        creada_por=usuario, estado=EstadoExtraccion.EN_CURSO.value
    ).first()


@dataclass(frozen=True)
class ErrorInicio:
    """[003] RN-03: no se inició porque hay otra idéntica en curso (error como valor)."""

    clave: str
    existente: Extraccion | None


def _extraccion_identica_en_curso(periodo: Periodo) -> Extraccion | None:
    return Extraccion.objects.filter(
        estado=EstadoExtraccion.EN_CURSO.value, desde=periodo.desde, hasta=periodo.hasta
    ).first()


def iniciar_extraccion(usuario, periodo: Periodo) -> Extraccion | ErrorInicio:
    """Crea una extracción en curso, o devuelve la que el administrador ya tiene (AC-1.11).

    [003] RN-03: si otro administrador tiene en curso una con el mismo período, no se crea y se
    devuelve ``ErrorInicio`` con la existente. Un período que se superpone en parte sí se inicia.
    """
    existente = extraccion_en_curso(usuario)
    if existente is not None:
        return existente
    identica = _extraccion_identica_en_curso(periodo)
    if identica is not None:
        return ErrorInicio("ext.periodo_en_curso", identica)
    try:
        with transaction.atomic():
            return Extraccion.objects.create(
                creada_por=usuario,
                desde=periodo.desde,
                hasta=periodo.hasta,
                estado=EstadoExtraccion.EN_CURSO.value,
                iniciada_en=timezone.now(),
            )
    except IntegrityError:
        propia = extraccion_en_curso(usuario)
        if propia is not None:
            return propia
        return ErrorInicio(
            "ext.periodo_en_curso",
            Extraccion.objects.filter(
                estado=EstadoExtraccion.EN_CURSO.value, desde=periodo.desde, hasta=periodo.hasta
            ).first(),
        )


NO_ELIMINABLE_EN_CURSO = MENSAJES["ext.eliminar_en_curso"]


def eliminar_extraccion(extraccion: Extraccion) -> str | None:
    """[002] RN-44, AC-1.18, AC-1.19 (D-24): elimina una extracción terminada.

    Borra la extracción con sus sorteos e intentos (en cascada) y su archivo, que vive en la
    misma fila. Devuelve el motivo si no se puede eliminar (errores como valores). El estado se
    vuelve a leer bloqueado para no borrar una extracción que el trabajador sigue procesando.
    """
    with transaction.atomic():
        actual = Extraccion.objects.select_for_update().filter(pk=extraccion.pk).first()
        if actual is None:
            return None
        if actual.en_curso:
            return NO_ELIMINABLE_EN_CURSO
        actual.delete()
    return None


# ---------------------------------------------------------------------------
# Procesamiento (trabajador)
# ---------------------------------------------------------------------------


@dataclass
class IntentoProcesado:
    fuente: Fuente
    resultado: ResultadoIntento
    url: str = ""
    consultado_en: object = None
    datos: DatosFuente | None = None
    observaciones: tuple[Observacion, ...] = ()


@dataclass
class _Estado:
    """Estado en memoria de una ejecución del trabajador sobre una extracción."""

    cliente: object
    fichas: dict[Fuente, Ficha]
    interpretes: dict
    listado_f1: dict[int, date] = field(default_factory=dict)
    #: Páginas de detalle ya obtenidas durante la identificación (R-06): se reutilizan.
    paginas: dict[tuple[Fuente, int], tuple[str, RespuestaHttp]] = field(default_factory=dict)


def _leer_listados(estado: _Estado) -> list[Referencia]:
    referencias: list[Referencia] = []
    for fuente, ficha in estado.fichas.items():
        respuesta = estado.cliente.obtener(fuente, ficha.url_listado())
        if resultado_por_respuesta(respuesta, ficha) is not None:
            continue
        try:
            filas = estado.interpretes[fuente].interpretar_listado(respuesta.texto)
        except Exception:  # noqa: BLE001 - I-09: un intérprete que falla no detiene nada
            logger.exception("Falló el intérprete del listado de %s", fuente.value)
            continue
        for fila in filas:
            numero = parsear_numero_sorteo(fila.numero_texto)
            fecha = parsear_fecha_fuente(fila.fecha_texto)
            if numero is None or fecha is None:
                continue
            referencias.append(Referencia(numero, fecha, fuente))
            if ficha.cobertura_por_listado:
                estado.listado_f1[numero] = fecha
    return referencias


def _cubre(ficha: Ficha, numero: int, estado: _Estado, fecha_informada: date | None = None) -> bool:
    """I-08 (actualizada el 20/11/2026, D-21): F1 cubre los sorteos de su listado y cualquier
    otro cuya fecha informen las demás fuentes, porque su dirección exige la fecha."""
    if ficha.cobertura_por_listado:
        return numero in estado.listado_f1 or fecha_informada is not None
    return numero >= ficha.cobertura_desde_numero


def _fecha_para(ficha: Ficha, numero: int, estado: _Estado, fecha_informada: date | None):
    """Fecha de la dirección de F1: la de su listado o, si no figura, la que informan F2 y F3."""
    if not ficha.exige_fecha_en_direccion:
        return None
    return estado.listado_f1.get(numero, fecha_informada)


def _fecha_de(estado: _Estado):
    """Fechas que informan F2 o F3 para un número, pidiendo su página de detalle (R-06)."""

    def fecha_de(numero: int) -> list[date]:
        for fuente in ORDEN_FUENTES:
            ficha = estado.fichas.get(fuente)
            if ficha is None or ficha.cobertura_por_listado or not _cubre(ficha, numero, estado):
                continue
            url = ficha.url_sorteo(numero)
            respuesta = estado.cliente.obtener(fuente, url)
            estado.paginas[(fuente, numero)] = (url, respuesta)
            if resultado_por_respuesta(respuesta, ficha) is not None:
                continue
            try:
                pagina = estado.interpretes[fuente].interpretar_sorteo(respuesta.texto)
            except Exception:  # noqa: BLE001
                logger.exception("Falló el intérprete de %s con el sorteo %s", fuente.value, numero)
                continue
            if isinstance(pagina, NoReconocida):
                continue
            fecha = parsear_fecha_fuente(pagina.fecha_texto)
            if fecha and parsear_numero_sorteo(pagina.numero_texto) == numero:
                return [fecha]
        return []

    return fecha_de


def _interpretar(estado: _Estado, fuente: Fuente, numero, url, fecha_pedida, respuesta):
    ficha = estado.fichas[fuente]
    intento = IntentoProcesado(fuente, ResultadoIntento.NO_DISPONIBLE, url, respuesta.consultado_en)
    resultado = resultado_por_respuesta(respuesta, ficha)
    if resultado is not None:
        intento.resultado = resultado
        return intento
    try:
        pagina = estado.interpretes[fuente].interpretar_sorteo(respuesta.texto)
    except Exception:  # noqa: BLE001 - I-09 (a)
        logger.exception("Falló el intérprete de %s con el sorteo %s", fuente.value, numero)
        intento.resultado = ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA
        intento.observaciones = (
            Observacion("obs.error_interprete", OBS_ERROR_INTERPRETE, fuente=fuente),
        )
        return intento
    if isinstance(pagina, NoReconocida):
        intento.resultado = ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA
        return intento
    normalizado = normalizar(pagina, ficha, numero, fecha_pedida)
    intento.resultado = normalizado.resultado
    intento.datos = normalizado.datos
    intento.observaciones = normalizado.observaciones
    return intento


def consultar_sorteo(estado: _Estado, numero: int) -> list[IntentoProcesado]:
    """[002] RN-09, AC-2.11, D-21: consulta siempre las fuentes prioritarias que cubren el
    sorteo y las de respaldo solo si hacen falta (``requiere_respaldo``): para completar datos o
    para desempatar. Si no hacen falta, su intento es "No requerida". Devuelve los intentos en
    el orden de prioridad (RN-07)."""
    principales = [f for f in ORDEN_FUENTES if f not in FUENTES_RESPALDO]
    intentos = _consultar_fuentes(estado, numero, principales)
    respaldo = [f for f in FUENTES_RESPALDO if f in estado.fichas]
    if respaldo:
        parcial = consolidar(
            numero, [(i.fuente, i.resultado, i.datos) for i in intentos.values()], estado.fichas
        )
        fecha = parcial.fecha.dato.v if isinstance(parcial.fecha.dato, Valor) else None
        if requiere_respaldo(parcial):
            intentos.update(_consultar_fuentes(estado, numero, respaldo, fecha))
        else:
            for fuente in respaldo:
                cubre = _cubre(estado.fichas[fuente], numero, estado, fecha)
                resultado = (
                    ResultadoIntento.NO_REQUERIDA if cubre else ResultadoIntento.FUERA_DE_COBERTURA
                )
                intentos[fuente] = IntentoProcesado(fuente, resultado)
    return [intentos[f] for f in ORDEN_FUENTES if f in intentos]


def _consultar_fuentes(
    estado: _Estado, numero: int, fuentes: list[Fuente], fecha_informada: date | None = None
) -> dict[Fuente, IntentoProcesado]:
    """Consulta las fuentes indicadas que cubren el sorteo, en paralelo y una por sitio (R-03).

    ``fecha_informada``: la fecha consolidada de las fuentes prioritarias, para pedir a F1 un
    sorteo que no figura en su listado (D-21). Los hilos solo hacen HTTP; el resto ocurre en el
    hilo principal.
    """
    pedidos: dict[Fuente, tuple[str, date | None]] = {}
    intentos: dict[Fuente, IntentoProcesado] = {}
    for fuente in fuentes:
        ficha = estado.fichas.get(fuente)
        if ficha is None:
            continue
        if not _cubre(ficha, numero, estado, fecha_informada):
            intentos[fuente] = IntentoProcesado(fuente, ResultadoIntento.FUERA_DE_COBERTURA)
            continue
        fecha = _fecha_para(ficha, numero, estado, fecha_informada)
        pedidos[fuente] = (ficha.url_sorteo(numero, fecha), fecha)

    respuestas: dict[Fuente, RespuestaHttp] = {}
    pendientes = {}
    for fuente, (url, _) in pedidos.items():
        guardada = estado.paginas.pop((fuente, numero), None)
        if guardada is not None and guardada[0] == url:
            respuestas[fuente] = guardada[1]
        else:
            pendientes[fuente] = url
    if pendientes:
        with ThreadPoolExecutor(max_workers=3) as ejecutor:
            futuros = {
                fuente: ejecutor.submit(estado.cliente.obtener, fuente, url)
                for fuente, url in pendientes.items()
            }
            for fuente, futuro in futuros.items():
                respuestas[fuente] = futuro.result()

    for fuente, (url, fecha) in pedidos.items():
        intentos[fuente] = _interpretar(estado, fuente, numero, url, fecha, respuestas[fuente])
    return intentos


def _guardar_sorteo(extraccion, sorteo: SorteoConsolidado, intentos: list[IntentoProcesado]):
    fecha = sorteo.fecha.dato.v if isinstance(sorteo.fecha.dato, Valor) else None
    with transaction.atomic():
        SorteoExtraido.objects.filter(extraccion=extraccion, numero=sorteo.numero).delete()
        fila = SorteoExtraido.objects.create(
            extraccion=extraccion,
            numero=sorteo.numero,
            fecha=fecha,
            estado=sorteo.estado.value,
            combina_fuentes=sorteo.combina_fuentes,
            sin_corroborar=sorteo.sin_corroborar,
            consolidado=sorteo_a_json(sorteo),
            procesado_en=timezone.now(),
        )
        IntentoConsulta.objects.bulk_create(
            IntentoConsulta(
                sorteo=fila,
                fuente=i.fuente.value,
                resultado=i.resultado.value,
                url=i.url,
                consultado_en=i.consultado_en,
                datos=datos_fuente_a_json(i.datos) if i.datos else None,
                observaciones=observaciones_a_json(i.observaciones),
            )
            for i in intentos
        )
    return fila


def procesar_sorteo(extraccion, estado: _Estado, numero: int) -> None:
    intentos = consultar_sorteo(estado, numero)
    sorteo = consolidar(numero, [(i.fuente, i.resultado, i.datos) for i in intentos], estado.fichas)
    _guardar_sorteo(extraccion, aplicar_clasificacion(sorteo), intentos)


def _guardar_error_inesperado(extraccion, numero: int) -> None:
    """I-09 (b): el sorteo queda "No recuperado", sin datos de ninguna fuente."""
    sorteo = SorteoConsolidado(
        numero=numero,
        fecha=NO_DISPONIBLE_CONSOLIDADO,
        modalidades=modalidades_no_informadas(),
        error_inesperado=True,
    )
    _guardar_sorteo(extraccion, aplicar_clasificacion(sorteo), [])


def _terminar_sin_sorteos(extraccion: Extraccion, cobertura: date | None) -> None:
    extraccion.estado = EstadoExtraccion.SIN_SORTEOS.value
    extraccion.cobertura_desde = cobertura
    extraccion.resumen = {
        "identificados": 0,
        "cobertura_desde": cobertura.isoformat() if cobertura else None,
        "resultado": EstadoExtraccion.SIN_SORTEOS.value,
    }
    extraccion.archivo_csv = ""
    extraccion.finalizada_en = timezone.now()
    extraccion.save()


def _finalizar(extraccion: Extraccion, fichas: dict[Fuente, Ficha]) -> None:
    filas = list(extraccion.sorteos.prefetch_related("intentos").order_by("numero"))
    originales = [sorteo_de_json(f.consolidado) for f in filas]
    revisados = revisar_correlatividad(originales)  # RN-23, antes de clasificar
    sorteos = []
    cambios = []
    for fila, original, revisado in zip(filas, originales, revisados, strict=True):
        if revisado is not original:
            revisado = aplicar_clasificacion(revisado)
            fila.estado = revisado.estado.value
            fila.consolidado = sorteo_a_json(revisado)
            cambios.append(fila)
        sorteos.append(revisado)
    identificacion = Identificacion(
        extraccion.numero_desde, extraccion.numero_hasta, extraccion.cobertura_desde
    )
    resumen = resumir(identificacion, sorteos, [f for f in ORDEN_FUENTES if f in fichas])
    procedencia = {
        fila.numero: {Fuente(i.fuente): (i.url, i.consultado_en) for i in fila.intentos.all()}
        for fila in filas
    }
    with transaction.atomic():
        for fila in cambios:
            fila.save(update_fields=["estado", "consolidado"])
        extraccion.resumen = resumen
        extraccion.estado = resumen["resultado"]
        extraccion.archivo_csv = generar_csv(sorteos, procedencia)  # una sola vez (RN-44)
        extraccion.nombre_archivo = nombre_archivo(
            extraccion.pk, extraccion.desde, extraccion.hasta
        )
        extraccion.version_contrato = VERSION_CONTRATO
        extraccion.finalizada_en = timezone.now()
        extraccion.save()


def procesar_extraccion(
    extraccion: Extraccion, cliente, fichas: dict[Fuente, Ficha], interpretes=None
) -> Extraccion:
    """Identifica, consulta, normaliza, consolida, clasifica, resume y genera el CSV.

    Reanuda una extracción interrumpida (I-07): conserva los sorteos ya guardados y repite las
    consultas del que quedó a medias. Una falla inesperada en un sorteo no detiene la extracción
    (I-09, NFR-006).
    """
    interpretes = interpretes or INTERPRETES
    fichas = {f: ficha for f, ficha in fichas.items() if f in interpretes}
    estado = _Estado(cliente=cliente, fichas=fichas, interpretes=interpretes)
    referencias = _leer_listados(estado)

    if extraccion.numero_desde is None:
        identificacion = identificar_sorteos(
            Periodo(extraccion.desde, extraccion.hasta),
            referencias,
            _fecha_de(estado),
            PRIMER_CUBIERTO,
        )
        if isinstance(identificacion, SinSorteos):
            _terminar_sin_sorteos(extraccion, identificacion.cobertura_desde)
            return extraccion
        extraccion.numero_desde = identificacion.numero_desde
        extraccion.numero_hasta = identificacion.numero_hasta
        extraccion.cobertura_desde = identificacion.cobertura_desde
        extraccion.save(update_fields=["numero_desde", "numero_hasta", "cobertura_desde"])

    procesados = set(extraccion.sorteos.values_list("numero", flat=True))
    for numero in range(extraccion.numero_desde, extraccion.numero_hasta + 1):
        if numero in procesados:
            continue
        try:
            procesar_sorteo(extraccion, estado, numero)
        except Exception:  # noqa: BLE001 - I-09 (b)
            logger.exception("Error inesperado al procesar el sorteo %s", numero)
            _guardar_error_inesperado(extraccion, numero)
    _finalizar(extraccion, fichas)
    return extraccion
