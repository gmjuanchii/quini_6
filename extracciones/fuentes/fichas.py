"""Fichas de las fuentes F1, F2 y F3 ([002] RN-06, R-05, contracts/fuentes.md).

Configuración aprobada en el código: no se edita desde la interfaz. Cambiar una ficha requiere
una actualización aprobada de la spec ([002] RN-10, D-07). Este módulo no importa Django: las
direcciones de reemplazo del servidor de fuentes de prueba llegan como parámetro.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from dominio.extraccion.normalizacion import normalizar_rotulo
from dominio.extraccion.tipos import Ficha, Fuente, Modalidad, ResultadoIntento

#: Sorteo más antiguo que cubre alguna ficha (F2, [002] RN-05, AC-1.17).
PRIMER_CUBIERTO = (2211, date(2014, 12, 17))

#: Enlace "Ver extracto oficial (Lotería de Santa Fe)" ([002] FR-007, AC-1.13). Dirección por
#: sorteo elegida por el responsable el 19/11/2026 (contracts/fuentes.md, F0).
ENLACE_EXTRACTO_OFICIAL = "https://numerosganadores.com.ar/sorteos/{numero}"

#: Marcadores de las verificaciones anti-robots de Cloudflare, que usan los tres sitios
#: (relevamiento del 19/11/2026). "challenge-platform" NO es marcador: aparece en F1 normal.
MARCADORES_CLOUDFLARE = (
    "<title>Just a moment...</title>",
    "cf_chl_opt",
    "cf-chl-",
    "Attention Required! | Cloudflare",
)


def _rotulos(tabla: dict[str, Modalidad]) -> dict[str, Modalidad]:
    return {normalizar_rotulo(rotulo): modalidad for rotulo, modalidad in tabla.items()}


M = Modalidad

F1 = Ficha(
    fuente=Fuente.F1,
    nombre=Fuente.F1.nombre,
    url_base="https://www.quini-6-resultados.com.ar",
    ruta_listado="/quini6/sorteos-anteriores.aspx",
    ruta_sorteo="/quini6/sorteo-{numero}-del-dia-{fecha}.htm",
    exige_fecha_en_direccion=True,
    cobertura_desde_numero=None,  # I-08: cubre los sorteos de su listado
    rotulos=_rotulos(
        {
            "SORTEO TRADICIONAL": M.PRIMER_SORTEO,
            "LA SEGUNDA DEL QUINI": M.LA_SEGUNDA,
            "LA SEGUNDA DEL QUINI 6": M.LA_SEGUNDA,
            "SORTEO REVANCHA": M.REVANCHA,
            "LA SEGUNDA DEL QUINI 6 REVANCHA": M.REVANCHA,
            "QUINI QUE SIEMPRE SALE": M.SIEMPRE_SALE,
            "EL QUINI QUE SIEMPRE SALE": M.SIEMPRE_SALE,
            "POZO EXTRA": M.PREMIO_EXTRA,
            "QUINI 6 POZO EXTRA": M.PREMIO_EXTRA,
        }
    ),
    codigos_inexistente={404: ResultadoIntento.NO_ENCONTRADO},
    marcadores_antirobots=MARCADORES_CLOUDFLARE,
    publica_numeros_premio_extra=False,
    publica_aciertos_premio_extra=False,  # aciertos "-"
    publica_pozo_premio_extra=True,  # "N millones de pesos" (RN-17)
)

F2 = Ficha(
    fuente=Fuente.F2,
    nombre=Fuente.F2.nombre,
    url_base="https://numerosganadores.com.ar",
    ruta_listado="/sorteos",
    ruta_sorteo="/sorteos/{numero}",
    exige_fecha_en_direccion=False,
    cobertura_desde_numero=2211,  # 17/12/2014
    rotulos=_rotulos(
        {
            "TRADICIONAL": M.PRIMER_SORTEO,
            "LA SEGUNDA": M.LA_SEGUNDA,
            "REVANCHA": M.REVANCHA,
            "SIEMPRE SALE": M.SIEMPRE_SALE,
            "POZO EXTRA": M.PREMIO_EXTRA,
        }
    ),
    codigos_inexistente={500: ResultadoIntento.NO_DISPONIBLE_O_NO_ENCONTRADO},
    marcadores_antirobots=MARCADORES_CLOUDFLARE,
    publica_numeros_premio_extra=True,
    publica_aciertos_premio_extra=True,
    publica_pozo_premio_extra=False,  # "85 millones de pesos" es un texto fijo y se ignora
)

F3 = Ficha(
    fuente=Fuente.F3,
    nombre=Fuente.F3.nombre,
    url_base="https://quiniya.com.ar",
    ruta_listado="/sorteos",
    ruta_sorteo="/sorteos/{numero}",
    exige_fecha_en_direccion=False,
    cobertura_desde_numero=2787,  # 09/09/2020
    rotulos=_rotulos(
        {
            "Tradicional Primer Sorteo": M.PRIMER_SORTEO,
            "La Segunda del Quini": M.LA_SEGUNDA,
            "Revancha": M.REVANCHA,
            "Siempre Sale": M.SIEMPRE_SALE,
            "Pozo Extra": M.PREMIO_EXTRA,
        }
    ),
    codigos_inexistente={404: ResultadoIntento.NO_ENCONTRADO},
    marcadores_antirobots=MARCADORES_CLOUDFLARE,
    publica_numeros_premio_extra=True,
    publica_aciertos_premio_extra=True,
    publica_pozo_premio_extra=False,
)

FICHAS: dict[Fuente, Ficha] = {Fuente.F1: F1, Fuente.F2: F2, Fuente.F3: F3}


def obtener_fichas(urls_base: dict[str, str | None] | None = None) -> dict[Fuente, Ficha]:
    """Fichas con las direcciones base de reemplazo (solo fuentes de prueba, [002] R-11)."""
    urls_base = urls_base or {}
    fichas = {}
    for fuente, ficha in FICHAS.items():
        reemplazo = urls_base.get(fuente.value)
        fichas[fuente] = replace(ficha, url_base=reemplazo) if reemplazo else ficha
    return fichas


def enlace_extracto_oficial(numero: int) -> str:
    return ENLACE_EXTRACTO_OFICIAL.format(numero=numero)
