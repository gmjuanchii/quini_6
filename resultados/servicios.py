"""Operaciones administrativas sobre resultados (US2, US7).

Transiciones de data-model.md: borrador → observado → borrador → publicado → en revisión →
corrección. Cada operación corre en una transacción y deja su entrada en ``RegistroCambio``
(NFR-006). Las reglas de consistencia viven en ``dominio.consistencia``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date

from django.db import IntegrityError, transaction
from django.utils import timezone

from dominio.consistencia import Observacion, revisar_numeros, revisar_premios
from dominio.mensajes import MENSAJES, mensaje
from dominio.numeros import mensaje_error_extraccion, validar_extraccion
from dominio.tipos import MODALIDADES_PREMIO_EXTRA, ORDEN_MODALIDADES, CategoriaPublicada, Modalidad
from resultados import consultas
from resultados.models import (
    ESTADOS_EN_TRABAJO,
    Accion,
    Bloque,
    Concurso,
    EstadoVersion,
    ModalidadConcurso,
    PremioCategoria,
    RegistroCambio,
    VersionNumeros,
    VersionPremios,
)

NUMEROS = consultas.NUMEROS
PREMIOS = consultas.PREMIOS
CAMPOS_PREMIO = ("ganadores", "importe_categoria", "importe_individual", "pozo_vacante_acumulado")
PREMIO_EXTRA_REQUIERE = "Premio Extra requiere Primer Sorteo, La Segunda y Revancha"
COTEJO_FALTANTE = "Confirmá que cotejaste esta información con la fuente oficial."


class ErrorResultados(Exception):
    def __init__(self, mensajes: str | list[str]):
        self.mensajes = [mensajes] if isinstance(mensajes, str) else list(mensajes)
        super().__init__("; ".join(self.mensajes))


class ConcursoDuplicado(ErrorResultados):
    def __init__(self, numero: int):
        self.numero = numero
        super().__init__(mensaje("admin.concurso_duplicado", N=numero))


# --- Utilidades ------------------------------------------------------------------------


def _texto_fuente(descripcion: str, fecha: date | None) -> str:
    partes = [descripcion.strip()] if descripcion and descripcion.strip() else []
    if fecha:
        partes.append(f"consultada el {fecha.strftime('%d/%m/%Y')}")
    return ", ".join(partes)


def _registrar(
    autor,
    concurso: Concurso,
    accion: str,
    bloque: str,
    modalidad: Modalidad | None = None,
    valor_anterior=None,
    valor_nuevo=None,
    motivo: str = "",
    fuente: str = "",
) -> RegistroCambio:
    return RegistroCambio.objects.create(
        concurso=concurso,
        modalidad=modalidad.value if modalidad else None,
        bloque=bloque,
        accion=accion,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        autor=autor,
        motivo=motivo,
        fuente=fuente,
    )


def _bloque_registro(bloque: str) -> str:
    return Bloque.NUMEROS if bloque == NUMEROS else Bloque.PREMIOS


def _modelo(bloque: str):
    return VersionNumeros if bloque == NUMEROS else VersionPremios


def _bloque_de(version) -> str:
    return NUMEROS if isinstance(version, VersionNumeros) else PREMIOS


def _bloquear_mc(mc: ModalidadConcurso) -> ModalidadConcurso:
    return ModalidadConcurso.objects.select_for_update().select_related("concurso").get(pk=mc.pk)


def _validar_modalidades(modalidades: Iterable[Modalidad]) -> list[Modalidad]:
    elegidas = [m for m in ORDEN_MODALIDADES if m in set(modalidades)]
    if not elegidas:
        raise ErrorResultados(MENSAJES["admin.falta_modalidad"])
    if Modalidad.PREMIO_EXTRA in elegidas and not all(
        m in elegidas for m in MODALIDADES_PREMIO_EXTRA
    ):
        raise ErrorResultados(PREMIO_EXTRA_REQUIERE)
    return elegidas


def _valor_concurso(concurso: Concurso, modalidades: list[str]) -> dict:
    return {
        "numero": concurso.numero,
        "fecha_sorteo": concurso.fecha_sorteo.isoformat(),
        "modalidades": modalidades,
    }


def _modalidades_actuales(concurso: Concurso) -> list[str]:
    actuales = {mc.modalidad for mc in concurso.modalidades.all()}
    return [m.value for m in ORDEN_MODALIDADES if m.value in actuales]


# --- Concursos -------------------------------------------------------------------------


def crear_concurso(autor, numero: int, fecha_sorteo: date, modalidades) -> Concurso:
    elegidas = _validar_modalidades(modalidades)
    if Concurso.objects.filter(numero=numero).exists():
        raise ConcursoDuplicado(numero)
    try:
        with transaction.atomic():
            concurso = Concurso.objects.create(
                numero=numero, fecha_sorteo=fecha_sorteo, creado_por=autor
            )
            for modalidad in elegidas:
                ModalidadConcurso.objects.create(concurso=concurso, modalidad=modalidad.value)
            _registrar(
                autor,
                concurso,
                Accion.CREAR_CONCURSO,
                Bloque.CONCURSO,
                valor_nuevo=_valor_concurso(concurso, [m.value for m in elegidas]),
            )
    except IntegrityError as error:
        raise ConcursoDuplicado(numero) from error
    return concurso


def modificar_concurso(autor, concurso: Concurso, fecha_sorteo: date, modalidades) -> Concurso:
    """P-05 (AC-2.14): agregar modalidades siempre; quitar solo sin información cargada;
    cambiar la fecha solo mientras ninguna extracción esté publicada."""
    elegidas = _validar_modalidades(modalidades)
    with transaction.atomic():
        concurso = Concurso.objects.select_for_update().get(pk=concurso.pk)
        anteriores = _modalidades_actuales(concurso)
        valor_anterior = _valor_concurso(concurso, anteriores)
        nuevas = [m.value for m in elegidas]
        errores = []
        quitar = [mc for mc in concurso.modalidades.all() if mc.modalidad not in nuevas]
        for mc in quitar:
            if mc.versiones_numeros.exists() or mc.versiones_premios.exists():
                errores.append(
                    f"No se puede quitar {mc.modalidad_enum.nombre} porque tiene información "
                    "cargada."
                )
        if fecha_sorteo != concurso.fecha_sorteo and not consultas.admite_jugadas(concurso):
            errores.append(
                "No se puede cambiar la fecha del sorteo porque ya tiene números publicados."
            )
        if errores:
            raise ErrorResultados(errores)
        if fecha_sorteo == concurso.fecha_sorteo and nuevas == anteriores:
            return concurso
        for mc in quitar:
            mc.delete()
        for valor in nuevas:
            if valor not in anteriores:
                ModalidadConcurso.objects.create(concurso=concurso, modalidad=valor)
        concurso.fecha_sorteo = fecha_sorteo
        concurso.save(update_fields=["fecha_sorteo"])
        _registrar(
            autor,
            concurso,
            Accion.MODIFICAR_CONCURSO,
            Bloque.CONCURSO,
            valor_anterior=valor_anterior,
            valor_nuevo=_valor_concurso(concurso, nuevas),
        )
    return concurso


# --- Borradores ------------------------------------------------------------------------


def _version_para_editar(mc: ModalidadConcurso, bloque: str, autor):
    modelo = _modelo(bloque)
    trabajo = modelo.objects.filter(modalidad_concurso=mc, estado__in=ESTADOS_EN_TRABAJO).first()
    if trabajo is not None:
        return trabajo, False
    if modelo.objects.filter(modalidad_concurso=mc, estado=EstadoVersion.PUBLICADA).exists():
        raise ErrorResultados(MENSAJES["admin.bloque_publicado"])
    return modelo(modalidad_concurso=mc, estado=EstadoVersion.BORRADOR, creada_por=autor), True


def _validar_correccion(version, motivo_correccion: str, descripcion: str, fecha) -> None:
    if not version.es_correccion:
        return
    errores = []
    if not (motivo_correccion or "").strip():
        errores.append("Falta el motivo de la corrección.")
    if not (descripcion or "").strip() or fecha is None:
        errores.append("Falta la fuente de la corrección (descripción y fecha de consulta).")
    if errores:
        raise ErrorResultados(errores)


def guardar_borrador_numeros(
    autor,
    mc: ModalidadConcurso,
    numeros,
    fuente_descripcion: str = "",
    fuente_fecha_consulta: date | None = None,
    motivo_correccion: str = "",
) -> VersionNumeros:
    if not mc.modalidad_enum.tiene_extraccion_propia:
        raise ErrorResultados("Premio Extra no tiene números propios.")
    resultado = validar_extraccion(list(numeros))
    if isinstance(resultado, list):
        mensajes = []
        for error in resultado:
            texto = mensaje_error_extraccion(error)
            if texto not in mensajes:
                mensajes.append(texto)
        raise ErrorResultados(mensajes)
    with transaction.atomic():
        mc = _bloquear_mc(mc)
        version, _nueva = _version_para_editar(mc, NUMEROS, autor)
        _validar_correccion(version, motivo_correccion, fuente_descripcion, fuente_fecha_consulta)
        version.asignar_numeros(resultado)
        version.fuente_descripcion = (fuente_descripcion or "").strip()
        version.fuente_fecha_consulta = fuente_fecha_consulta
        if version.es_correccion:
            version.motivo_correccion = motivo_correccion.strip()
        version.actualizada_por = autor
        version.actualizada_en = timezone.now()
        version.save()
        _registrar(
            autor,
            mc.concurso,
            Accion.GUARDAR_BORRADOR,
            Bloque.NUMEROS,
            mc.modalidad_enum,
            valor_nuevo=version.valor_json(),
            motivo=version.motivo_correccion,
            fuente=_texto_fuente(version.fuente_descripcion, version.fuente_fecha_consulta),
        )
    return version


def _categorias_dominio(datos: Mapping[str, Mapping], modalidad: Modalidad):
    return [
        CategoriaPublicada(
            codigo=codigo,
            ganadores=(datos.get(codigo) or {}).get("ganadores"),
            importe_categoria=(datos.get(codigo) or {}).get("importe_categoria"),
            importe_individual=(datos.get(codigo) or {}).get("importe_individual"),
            pozo_vacante_acumulado=(datos.get(codigo) or {}).get("pozo_vacante_acumulado"),
        )
        for codigo in modalidad.categorias
    ]


#: Errores que no se pueden guardar ni siquiera como borrador (la base los rechaza).
_NO_GUARDABLES = {
    "GANADORES_NEGATIVO",
    "IMPORTE_NEGATIVO",
    "SIN_GANADORES_CON_CATEGORIA",
    "SIN_GANADORES_NO_APLICA",
}


def guardar_borrador_premios(
    autor,
    mc: ModalidadConcurso,
    datos_por_categoria: Mapping[str, Mapping],
    aciertos_categoria_ganadora: int | None = None,
    sin_ganadores: bool = False,
    fuente_descripcion: str = "",
    fuente_fecha_consulta: date | None = None,
    motivo_correccion: str = "",
) -> VersionPremios:
    """Una fila por categoría predefinida; ``None`` = "no disponible" (AC-2.13)."""
    modalidad = mc.modalidad_enum
    categorias = _categorias_dominio(datos_por_categoria, modalidad)
    bloqueantes, _ = revisar_premios(
        modalidad, categorias, aciertos_categoria_ganadora, sin_ganadores, None
    )
    no_guardables = [b.texto for b in bloqueantes if b.codigo in _NO_GUARDABLES]
    if no_guardables:
        raise ErrorResultados(no_guardables)
    with transaction.atomic():
        mc = _bloquear_mc(mc)
        version, _nueva = _version_para_editar(mc, PREMIOS, autor)
        _validar_correccion(version, motivo_correccion, fuente_descripcion, fuente_fecha_consulta)
        version.aciertos_categoria_ganadora = aciertos_categoria_ganadora
        version.sin_ganadores = bool(sin_ganadores)
        version.fuente_descripcion = (fuente_descripcion or "").strip()
        version.fuente_fecha_consulta = fuente_fecha_consulta
        if version.es_correccion:
            version.motivo_correccion = motivo_correccion.strip()
        version.actualizada_por = autor
        version.actualizada_en = timezone.now()
        version.save()
        for cat in categorias:
            PremioCategoria.objects.update_or_create(
                version_premios=version,
                categoria=cat.codigo,
                defaults={campo: getattr(cat, campo) for campo in CAMPOS_PREMIO},
            )
        _registrar(
            autor,
            mc.concurso,
            Accion.GUARDAR_BORRADOR,
            Bloque.PREMIOS,
            modalidad,
            valor_nuevo=version.valor_json(),
            motivo=version.motivo_correccion,
            fuente=_texto_fuente(version.fuente_descripcion, version.fuente_fecha_consulta),
        )
    return version


# --- Observación y publicación ---------------------------------------------------------


def _recargar(version):
    return type(version).objects.select_for_update().get(pk=version.pk)


def observar(autor, version, motivo: str):
    if not (motivo or "").strip():
        raise ErrorResultados("Falta el motivo de la observación.")
    with transaction.atomic():
        mc = _bloquear_mc(version.modalidad_concurso)
        version = _recargar(version)
        if version.estado != EstadoVersion.BORRADOR:
            raise ErrorResultados("Solo se puede observar información en Borrador.")
        version.estado = EstadoVersion.OBSERVADO
        version.motivo_observacion = motivo.strip()
        version.save(update_fields=["estado", "motivo_observacion"])
        _registrar(
            autor,
            mc.concurso,
            Accion.OBSERVAR,
            _bloque_registro(_bloque_de(version)),
            mc.modalidad_enum,
            motivo=version.motivo_observacion,
        )
    return version


def resolver_observacion(autor, version):
    with transaction.atomic():
        mc = _bloquear_mc(version.modalidad_concurso)
        version = _recargar(version)
        if version.estado != EstadoVersion.OBSERVADO:
            raise ErrorResultados("La información no está Observada.")
        version.estado = EstadoVersion.BORRADOR
        version.save(update_fields=["estado"])
        _registrar(
            autor,
            mc.concurso,
            Accion.RESOLVER_OBSERVACION,
            _bloque_registro(_bloque_de(version)),
            mc.modalidad_enum,
            motivo=version.motivo_observacion,
        )
    return version


def _numeros_actuales(mc: ModalidadConcurso):
    """Valores cargados de un bloque de números (en trabajo o publicado), para RN-22."""
    trabajo = mc.versiones_numeros.filter(estado__in=ESTADOS_EN_TRABAJO).first()
    if trabajo is not None:
        return trabajo.numeros
    vigente = mc.versiones_numeros.filter(estado=EstadoVersion.PUBLICADA).first()
    return vigente.numeros if vigente else None


def revisar_para_publicar(version, hoy: date | None = None) -> tuple[list, list]:
    """RN-17 (a) a (c) y RN-22: lo que impide publicar y lo que exige confirmación."""
    hoy = hoy or timezone.localdate()
    mc = version.modalidad_concurso
    fuente = (version.fuente_descripcion, version.fuente_fecha_consulta)
    if isinstance(version, VersionNumeros):
        otras = {}
        for otro in mc.concurso.modalidades.exclude(pk=mc.pk):
            if otro.modalidad_enum.tiene_extraccion_propia:
                numeros = _numeros_actuales(otro)
                if numeros:
                    otras[otro.modalidad_enum] = numeros
        bloqueantes, advertencias = revisar_numeros(
            sorted(version.numeros), otras, mc.concurso.fecha_sorteo, hoy, fuente
        )
    else:
        categorias = [
            CategoriaPublicada(
                codigo=c.categoria,
                ganadores=c.ganadores,
                importe_categoria=c.importe_categoria,
                importe_individual=c.importe_individual,
                pozo_vacante_acumulado=c.pozo_vacante_acumulado,
            )
            for c in version.categorias.all()
        ]
        bloqueantes, advertencias = revisar_premios(
            mc.modalidad_enum,
            categorias,
            version.aciertos_categoria_ganadora,
            version.sin_ganadores,
            fuente,
        )
    if version.estado == EstadoVersion.OBSERVADO:
        bloqueantes = [
            Observacion(
                "OBSERVADO",
                "La información está Observada: resolvé la observación antes de publicar.",
            ),
            *bloqueantes,
        ]
    elif version.estado != EstadoVersion.BORRADOR:
        bloqueantes = [
            Observacion("NO_BORRADOR", "Solo se puede publicar información en Borrador."),
            *bloqueantes,
        ]
    return bloqueantes, advertencias


def publicar(
    autor,
    version,
    advertencias_confirmadas: bool,
    cotejo_confirmado: bool,
    hoy: date | None = None,
):
    """RN-17 (a) a (e). Si es una corrección, la publicada anterior pasa a ``REEMPLAZADA``,
    la marca de revisión se quita y se registra ``PUBLICAR_CORRECCION`` (RN-23, P-01)."""
    bloque = _bloque_de(version)
    with transaction.atomic():
        mc = _bloquear_mc(version.modalidad_concurso)
        version = _recargar(version)
        bloqueantes, advertencias = revisar_para_publicar(version, hoy)
        if bloqueantes:
            raise ErrorResultados([b.texto for b in bloqueantes])
        if advertencias and not advertencias_confirmadas:
            raise ErrorResultados("Confirmá expresamente las advertencias antes de publicar.")
        if not cotejo_confirmado:
            raise ErrorResultados(COTEJO_FALTANTE)
        ahora = timezone.now()
        modelo = _modelo(bloque)
        anterior = modelo.objects.filter(
            modalidad_concurso=mc, estado=EstadoVersion.PUBLICADA
        ).first()
        valor_anterior = anterior.valor_json() if anterior else None
        if anterior is not None:
            if not version.es_correccion:
                raise ErrorResultados("El bloque ya tiene una versión publicada.")
            anterior.estado = EstadoVersion.REEMPLAZADA
            anterior.reemplazada_en = ahora
            anterior.save(update_fields=["estado", "reemplazada_en"])
        version.estado = EstadoVersion.PUBLICADA
        version.publicada_por = autor
        version.publicada_en = ahora
        version.save(update_fields=["estado", "publicada_por", "publicada_en"])
        if version.es_correccion:
            setattr(mc, f"{bloque}_en_revision", False)
            setattr(mc, f"{bloque}_motivo_revision", "")
            mc.save(update_fields=[f"{bloque}_en_revision", f"{bloque}_motivo_revision"])
        _registrar(
            autor,
            mc.concurso,
            Accion.PUBLICAR_CORRECCION if version.es_correccion else Accion.PUBLICAR,
            _bloque_registro(bloque),
            mc.modalidad_enum,
            valor_anterior=valor_anterior,
            valor_nuevo=version.valor_json(),
            motivo=version.motivo_correccion if version.es_correccion else "",
            fuente=_texto_fuente(version.fuente_descripcion, version.fuente_fecha_consulta),
        )
    return version


# --- Revisión y corrección (US7) -------------------------------------------------------


def marcar_revision(autor, mc: ModalidadConcurso, bloque: str, motivo: str) -> ModalidadConcurso:
    """RN-16 y AC-7.1: solo sobre un bloque con versión publicada, con motivo."""
    if not (motivo or "").strip():
        raise ErrorResultados("Falta el motivo de la revisión.")
    with transaction.atomic():
        mc = _bloquear_mc(mc)
        vigente = (
            _modelo(bloque)
            .objects.filter(modalidad_concurso=mc, estado=EstadoVersion.PUBLICADA)
            .first()
        )
        if vigente is None:
            raise ErrorResultados("Solo se puede marcar en revisión un bloque publicado.")
        if getattr(mc, f"{bloque}_en_revision"):
            raise ErrorResultados("El bloque ya está en revisión.")
        setattr(mc, f"{bloque}_en_revision", True)
        setattr(mc, f"{bloque}_motivo_revision", motivo.strip())
        mc.save(update_fields=[f"{bloque}_en_revision", f"{bloque}_motivo_revision"])
        _registrar(
            autor,
            mc.concurso,
            Accion.MARCAR_REVISION,
            _bloque_registro(bloque),
            mc.modalidad_enum,
            motivo=motivo.strip(),
            fuente=_texto_fuente(vigente.fuente_descripcion, vigente.fuente_fecha_consulta),
        )
    return mc


def quitar_revision(autor, mc: ModalidadConcurso, bloque: str, motivo: str) -> ModalidadConcurso:
    """P-01 (b): quita la marca con un motivo, sin cambiar valores."""
    if not (motivo or "").strip():
        raise ErrorResultados("Falta el motivo para quitar la revisión.")
    with transaction.atomic():
        mc = _bloquear_mc(mc)
        if not getattr(mc, f"{bloque}_en_revision"):
            raise ErrorResultados("El bloque no está en revisión.")
        setattr(mc, f"{bloque}_en_revision", False)
        setattr(mc, f"{bloque}_motivo_revision", "")
        mc.save(update_fields=[f"{bloque}_en_revision", f"{bloque}_motivo_revision"])
        _registrar(
            autor,
            mc.concurso,
            Accion.QUITAR_REVISION,
            _bloque_registro(bloque),
            mc.modalidad_enum,
            motivo=motivo.strip(),
        )
    return mc


def iniciar_correccion(
    autor,
    mc: ModalidadConcurso,
    bloque: str,
    motivo: str,
    fuente_descripcion: str,
    fuente_fecha_consulta: date | None,
):
    """RN-23 y AC-7.2: crea una versión en trabajo con los valores de la publicada."""
    errores = []
    if not (motivo or "").strip():
        errores.append("Falta el motivo de la corrección.")
    if not (fuente_descripcion or "").strip() or fuente_fecha_consulta is None:
        errores.append("Falta la fuente de la corrección (descripción y fecha de consulta).")
    if errores:
        raise ErrorResultados(errores)
    modelo = _modelo(bloque)
    with transaction.atomic():
        mc = _bloquear_mc(mc)
        vigente = modelo.objects.filter(
            modalidad_concurso=mc, estado=EstadoVersion.PUBLICADA
        ).first()
        if vigente is None:
            raise ErrorResultados("Solo se puede corregir un bloque publicado.")
        if modelo.objects.filter(modalidad_concurso=mc, estado__in=ESTADOS_EN_TRABAJO).exists():
            raise ErrorResultados("Ya hay una corrección en preparación para este bloque.")
        ahora = timezone.now()
        nueva = modelo(
            modalidad_concurso=mc,
            estado=EstadoVersion.BORRADOR,
            es_correccion=True,
            motivo_correccion=motivo.strip(),
            fuente_descripcion=fuente_descripcion.strip(),
            fuente_fecha_consulta=fuente_fecha_consulta,
            creada_por=autor,
            creada_en=ahora,
            actualizada_por=autor,
            actualizada_en=ahora,
        )
        if bloque == NUMEROS:
            nueva.asignar_numeros(vigente.numeros)
        else:
            nueva.aciertos_categoria_ganadora = vigente.aciertos_categoria_ganadora
            nueva.sin_ganadores = vigente.sin_ganadores
        nueva.save()
        if bloque == PREMIOS:
            for cat in vigente.categorias.all():
                PremioCategoria.objects.create(
                    version_premios=nueva,
                    categoria=cat.categoria,
                    **{campo: getattr(cat, campo) for campo in CAMPOS_PREMIO},
                )
        _registrar(
            autor,
            mc.concurso,
            Accion.INICIAR_CORRECCION,
            _bloque_registro(bloque),
            mc.modalidad_enum,
            valor_anterior=vigente.valor_json(),
            motivo=motivo.strip(),
            fuente=_texto_fuente(nueva.fuente_descripcion, nueva.fuente_fecha_consulta),
        )
    return nueva
