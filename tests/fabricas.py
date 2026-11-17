"""Fábricas de datos de prueba. Escriben directamente con el ORM, sin pasar por los
servicios de US2, para que cada historia se pruebe sola. Nunca se cargan en producción
(contracts/comandos.md)."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from django.utils import timezone

from cuentas.models import Usuario
from dominio.tipos import ORDEN_MODALIDADES, Modalidad
from resultados.models import (
    Concurso,
    EstadoVersion,
    ModalidadConcurso,
    PremioCategoria,
    VersionNumeros,
    VersionPremios,
)

TODAS = ORDEN_MODALIDADES
CLAVE = "clave-segura-123"
FUENTE = ("Extracto oficial de prueba", date(2025, 1, 10))


def crear_usuario(email: str, admin: bool = False, password: str = CLAVE) -> Usuario:
    return Usuario.objects.create_user(email=email, password=password, es_administrador=admin)


def _autor() -> Usuario:
    usuario = Usuario.objects.filter(es_administrador=True).order_by("id").first()
    return usuario or crear_usuario("fabrica-admin@prueba.local", admin=True)


def crear_concurso(numero: int, fecha: date, modalidades=TODAS) -> Concurso:
    concurso = Concurso.objects.create(numero=numero, fecha_sorteo=fecha, creado_por=_autor())
    for modalidad in modalidades:
        ModalidadConcurso.objects.create(concurso=concurso, modalidad=modalidad.value)
    return concurso


def _mc(concurso: Concurso, modalidad: Modalidad) -> ModalidadConcurso:
    return ModalidadConcurso.objects.get(concurso=concurso, modalidad=modalidad.value)


def _a_datetime(valor: date | datetime | None) -> datetime:
    if valor is None:
        return timezone.now()
    if isinstance(valor, datetime):
        return valor if timezone.is_aware(valor) else timezone.make_aware(valor)
    return timezone.make_aware(datetime(valor.year, valor.month, valor.day, 12, 0))


def _reemplazar_publicada(modelo, mc, momento):
    modelo.objects.filter(modalidad_concurso=mc, estado=EstadoVersion.PUBLICADA).update(
        estado=EstadoVersion.REEMPLAZADA, reemplazada_en=momento
    )


def cargar_numeros(
    concurso: Concurso,
    modalidad: Modalidad,
    numeros,
    estado: str = "PUBLICADA",
    fuente=FUENTE,
    es_correccion: bool = False,
    publicada_en=None,
    motivo_correccion: str = "Corrección de prueba",
) -> VersionNumeros:
    mc = _mc(concurso, modalidad)
    autor = _autor()
    momento = _a_datetime(publicada_en)
    if estado == EstadoVersion.PUBLICADA:
        _reemplazar_publicada(VersionNumeros, mc, momento)
    version = VersionNumeros(
        modalidad_concurso=mc,
        estado=estado,
        fuente_descripcion=fuente[0] if fuente else "",
        fuente_fecha_consulta=fuente[1] if fuente else None,
        es_correccion=es_correccion,
        motivo_correccion=motivo_correccion if es_correccion else "",
        motivo_observacion="Observación de prueba" if estado == EstadoVersion.OBSERVADO else "",
        creada_por=autor,
        actualizada_por=autor,
    )
    version.asignar_numeros(numeros)
    if estado == EstadoVersion.PUBLICADA:
        version.publicada_por = autor
        version.publicada_en = momento
    version.save()
    return version


def cargar_premios(
    concurso: Concurso,
    modalidad: Modalidad,
    categorias: dict | None = None,
    aciertos_categoria_ganadora: int | None = None,
    sin_ganadores: bool = False,
    estado: str = "PUBLICADA",
    fuente=FUENTE,
    es_correccion: bool = False,
    publicada_en=None,
    motivo_correccion: str = "Corrección de prueba",
) -> VersionPremios:
    """``categorias``: ``{"PRIMER": {"ganadores": 1, "importe_individual": "1000.00"}, ...}``.
    Las categorías no indicadas se crean con todos sus datos "no disponibles"."""
    mc = _mc(concurso, modalidad)
    autor = _autor()
    momento = _a_datetime(publicada_en)
    if estado == EstadoVersion.PUBLICADA:
        _reemplazar_publicada(VersionPremios, mc, momento)
    version = VersionPremios.objects.create(
        modalidad_concurso=mc,
        estado=estado,
        aciertos_categoria_ganadora=aciertos_categoria_ganadora,
        sin_ganadores=sin_ganadores,
        fuente_descripcion=fuente[0] if fuente else "",
        fuente_fecha_consulta=fuente[1] if fuente else None,
        es_correccion=es_correccion,
        motivo_correccion=motivo_correccion if es_correccion else "",
        motivo_observacion="Observación de prueba" if estado == EstadoVersion.OBSERVADO else "",
        creada_por=autor,
        actualizada_por=autor,
        publicada_por=autor if estado == EstadoVersion.PUBLICADA else None,
        publicada_en=momento if estado == EstadoVersion.PUBLICADA else None,
    )
    categorias = categorias or {}
    for codigo in modalidad.categorias:
        datos = categorias.get(codigo, {})
        PremioCategoria.objects.create(
            version_premios=version,
            categoria=codigo,
            ganadores=datos.get("ganadores"),
            importe_categoria=_dec(datos.get("importe_categoria")),
            importe_individual=_dec(datos.get("importe_individual")),
            pozo_vacante_acumulado=_dec(datos.get("pozo_vacante_acumulado")),
        )
    return version


def _dec(valor):
    if valor is None:
        return None
    return Decimal(str(valor))


def marcar_en_revision(concurso: Concurso, modalidad: Modalidad, bloque: str, motivo: str):
    mc = _mc(concurso, modalidad)
    setattr(mc, f"{bloque}_en_revision", True)
    setattr(mc, f"{bloque}_motivo_revision", motivo)
    mc.save()
    return mc


PS, LS, RV, SS, PE = ORDEN_MODALIDADES

#: Los tres ejemplos de referencia de la spec (AC-5.33).
EJEMPLOS_REFERENCIA = {
    1: {
        "jugada": frozenset({3, 8, 14, 21, 32, 40}),
        "numeros": {
            PS: frozenset({3, 8, 14, 21, 32, 40}),
            LS: frozenset({3, 8, 14, 21, 32, 41}),
            RV: frozenset({3, 8, 14, 21, 33, 41}),
            SS: frozenset({3, 8, 14, 22, 33, 41}),
        },
    },
    2: {
        "jugada": frozenset({1, 7, 12, 19, 28, 44}),
        "numeros": {
            PS: frozenset({1, 7, 12, 19, 30, 45}),
            LS: frozenset({1, 7, 12, 20, 30, 45}),
            RV: frozenset({1, 7, 12, 19, 28, 44}),
            SS: frozenset({1, 7, 12, 19, 28, 40}),
        },
    },
    3: {
        "jugada": frozenset({2, 9, 16, 23, 31, 42}),
        "numeros": {
            PS: frozenset({2, 9, 16, 25, 34, 45}),
            LS: frozenset({2, 11, 16, 23, 35, 42}),
            RV: frozenset({5, 9, 18, 23, 31, 42}),
            SS: frozenset({2, 9, 16, 23, 31, 40}),
        },
    },
}


def crear_concurso_ejemplo(n: int, numero: int, fecha: date = date(2025, 3, 2)) -> Concurso:
    """Crea el concurso del ejemplo ``n`` con las cinco modalidades y publica sus números."""
    concurso = crear_concurso(numero, fecha)
    for modalidad, numeros in EJEMPLOS_REFERENCIA[n]["numeros"].items():
        cargar_numeros(concurso, modalidad, numeros)
    return concurso
