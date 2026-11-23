"""Normalización y validación de lo que informa una fuente ([002] RN-11 a RN-26, RN-10).

``normalizar`` recibe los textos sin interpretar de una página (``PaginaCruda``) y la ficha de la
fuente, y devuelve el resultado del intento ([002] RN-08), los datos normalizados y las
observaciones. Ningún importe se calcula (RN-18) y ningún dato desconocido se convierte en cero
ni en vacante (RN-20). No importa Django.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dominio.extraccion.tipos import (
    MODALIDADES_PROPIAS,
    NO_CORRESPONDE,
    NO_DISPONIBLE,
    SIN_GANADORES,
    BloqueCrudo,
    Dato,
    DatosCategoriaFuente,
    DatosFuente,
    DatosModalidadFuente,
    Ficha,
    FilaPremioCruda,
    Modalidad,
    Observacion,
    PaginaCruda,
    ResultadoIntento,
    Valor,
    categorias_esperadas,
    codigo_aciertos,
    nombre_categoria,
    nombre_modalidad,
    viola_rn_26,
)
from dominio.importes import ErrorImporte, formatear_pesos, parsear_pesos
from dominio.numeros import formatear
from dominio.tipos import FECHA_VIGENCIA_REGLAS, MODALIDADES_PREMIO_EXTRA, ORDEN_MODALIDADES

# Textos de contracts/mensajes.md, "Observaciones y motivos del detalle".
OBS_IMPORTE_INVALIDO = "Importe con formato no reconocido: «{texto}»"
OBS_PREMIO_EXTRA_NO_COINCIDE = (
    "Los números de Pozo Extra de la fuente no coinciden con sus extracciones"
)
OBS_NUMEROS_CANTIDAD = "{modalidad}: la fuente publica {n} números en lugar de seis. No se usan."
OBS_NUMEROS_REPETIDO = "{modalidad}: la fuente repite el número {nn}. No se usan."
OBS_NUMEROS_RANGO = "{modalidad}: la fuente publica «{texto}», fuera de 00 a 45. No se usan."
OBS_ROTULO_DESCONOCIDO = (
    "Rótulo no reconocido: «{texto}». Ese bloque no se asignó a ninguna modalidad."
)
OBS_CATEGORIA_FUERA_CATALOGO = "Categoría fuera del catálogo: «{texto}». No se asignó."
OBS_CONCEPTO_IMPORTE = "No se pudo determinar si el importe «{texto}» es pozo o premio individual."
OBS_FALTA = "Falta: {lista}"
OBS_SIEMPRE_SALE_INVALIDA = (
    "Siempre Sale: la categoría ganadora informada no es válida (debe tener entre 0 y 6 "
    "aciertos y al menos un ganador)"
)
OBS_PREMIO_EXTRA_INVALIDA = (
    'Pozo Extra: la categoría ganadora informada no es 6, 5, 4 ni "Sin ganadores"'
)
OBS_NEGATIVO = "La fuente publica un valor negativo: «{texto}». No se usa."
OBS_EXTRACCIONES_IGUALES = "{a} y {b}: la fuente publica los mismos seis números"
OBS_DIRECCION_NO_COINCIDE = (
    "El número o la fecha de la página no coinciden con los de la dirección consultada"
)
OBS_POZO_PREMIO_EXTRA_TEXTO = "Pozo Extra publicado como «{texto}»"
OBS_IMPORTE_CORREGIDO = "Importe corregido: «{texto}» → {importe}"

_MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10, "noviembre": 11,
    "diciembre": 12,
}  # fmt: skip
_FECHA_NUMERICA = re.compile(r"(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?!\d)")
_FECHA_TEXTO = re.compile(r"(?<!\d)(\d{1,2})\s+de\s+([a-záéíóú]+)\s+(?:de|del)\s+(\d{4})", re.I)
_ENTERO = re.compile(r"^\d+$")
_ENTERO_MILES = re.compile(r"^\d{1,3}(?:\.\d{3})+$")
_SEPARADORES_NUMEROS = re.compile(r"[\s,;\-–·|]+")
_MILLONES = re.compile(r"^(\d+(?:,\d+)?)\s+millones?\s+de\s+pesos$", re.I)
#: [002] RN-16, D-18: importe mal cargado con cuatro dígitos en el último grupo («410.1156,25»).
_MAL_CARGADO = re.compile(r"^(\d{1,3}(?:\.\d{3})*)\.(\d{4})(?:,(\d+))?$")
#: [002] RN-16, D-20: importe con tres o más decimales («1.278.143,114»).
_DEMASIADOS_DECIMALES = re.compile(r"^(\d+|\d{1,3}(?:\.\d{3})+),(\d{3,})$")
#: [002] RN-16, D-31: puntos de miles mal puestos en la parte entera, con el último grupo de tres
#: dígitos («1.0867.330», «2.57.2821.792», «2472.996,80»).
_MILES_MAL_PUESTOS = re.compile(r"^(\d+(?:\.\d+)*\.\d{3})(?:,(\d+))?$")
#: [002] RN-16, D-32: coma en lugar de todos los separadores, con dos o más comas y dos decimales
#: después de la última («494,443,71»).
_COMAS_EN_TODOS = re.compile(r"^(\d+(?:,\d+)+),(\d{2})$")
_CENTAVOS = Decimal("0.01")
_VACANTE = {"vacante", "pozo vacante"}
_SIN_DATO = {"", "-", "–", "—"}


# ---------------------------------------------------------------------------
# Textos simples
# ---------------------------------------------------------------------------


def _limpio(texto: str | None) -> str:
    return re.sub(r"\s+", " ", (texto or "").replace("\xa0", " ")).strip()


def parsear_numero_sorteo(texto: str | None) -> int | None:
    """[002] RN-21: entero positivo."""
    limpio = _limpio(texto).lstrip("#")
    if not _ENTERO.match(limpio):
        return None
    numero = int(limpio)
    return numero if numero > 0 else None


def parsear_fecha_fuente(texto: str | None) -> date | None:
    """Fecha publicada por una fuente: ``dd/mm/aaaa``, ``d-m-aaaa`` o ``dd de mes de aaaa``."""
    limpio = _limpio(texto)
    coincidencia = _FECHA_NUMERICA.search(limpio)
    if coincidencia:
        dia, mes, anio = (int(g) for g in coincidencia.groups())
    else:
        coincidencia = _FECHA_TEXTO.search(limpio)
        if not coincidencia:
            return None
        mes = _MESES.get(coincidencia.group(2).casefold())
        if mes is None:
            return None
        dia, anio = int(coincidencia.group(1)), int(coincidencia.group(3))
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None


@dataclass(frozen=True)
class ErrorImporteFuente:
    """Códigos: VACIO, NEGATIVO, NO_NUMERICO, DEMASIADOS_DECIMALES."""

    codigo: str
    texto: str


def parsear_importe_fuente(
    texto: str | None, permite_millones: bool = False
) -> Decimal | ErrorImporteFuente:
    """Importe de una fuente ([002] RN-16, RN-17). Quita "$" y espacios y delega en
    ``parsear_pesos``. Con ``permite_millones`` (solo el pozo de Premio Extra de F1) acepta
    "N millones de pesos" y devuelve N × 1.000.000 exactos. Nunca usa ``float``."""
    original = _limpio(texto)
    if permite_millones:
        coincidencia = _MILLONES.match(original)
        if coincidencia:
            return Decimal(coincidencia.group(1).replace(",", ".")) * 1_000_000
    sin_simbolo = original.replace("$", "").replace(" ", "")
    resultado = parsear_pesos(sin_simbolo)
    if isinstance(resultado, ErrorImporte):
        return ErrorImporteFuente(resultado.codigo, original)
    return resultado


def corregir_importe_mal_cargado(texto: str | None) -> Decimal | None:
    """[002] RN-16: corrección de importes mal cargados, siempre redondeada a centavos (mitad
    hacia arriba). Devuelve ``None`` si el texto no tiene una de estas formas:

    - D-18: el último grupo antes de la coma tiene cuatro dígitos; la coma decimal se corre un
      lugar a la izquierda: «410.1156,25» → 410115.63.
    - D-20: tres o más decimales: «1.278.143,114» → 1278143.11.
    - D-31: puntos de miles mal puestos en la parte entera y el último grupo de tres dígitos;
      los dígitos se reagrupan en tríos desde la derecha y los decimales se conservan:
      «1.0867.330» → 10867330, «2.57.2821.792» → 2572821792, «$ 1.0867.330,29» → 10867330.29.
      Se aplica después de D-18 y D-20, que tienen prioridad.
    - D-32: coma en lugar de todos los separadores (dos o más comas); de derecha a izquierda, los
      dos dígitos después de la última coma son los decimales y el resto, la parte entera:
      «494,443,71» → 494443.71. Si el último grupo no tiene dos dígitos («1,234,567») no se
      corrige.
    """
    limpio = _limpio(texto).replace("$", "").replace(" ", "")
    coincidencia = _MAL_CARGADO.match(limpio)
    if coincidencia:
        grupos, ultimo, decimales = coincidencia.groups()
        entero = grupos.replace(".", "") + ultimo[:3]
        valor = Decimal(f"{entero}.{ultimo[3]}{decimales or ''}")
        return valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
    coincidencia = _DEMASIADOS_DECIMALES.match(limpio)
    if coincidencia:
        entero, decimales = coincidencia.groups()
        valor = Decimal(f"{entero.replace('.', '')}.{decimales}")
        return valor.quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
    coincidencia = _MILES_MAL_PUESTOS.match(limpio)
    if coincidencia and not _ENTERO_MILES.match(coincidencia.group(1)):
        entero, decimales = coincidencia.groups()
        entero = entero.replace(".", "")
        if not decimales:
            return Decimal(entero)  # RN-16: sin centavos agregados
        return Decimal(f"{entero}.{decimales}").quantize(_CENTAVOS, rounding=ROUND_HALF_UP)
    coincidencia = _COMAS_EN_TODOS.match(limpio)
    if coincidencia:
        entero, decimales = coincidencia.groups()
        return Decimal(f"{entero.replace(',', '')}.{decimales}")
    return None


def tokens_numeros(textos) -> list[str]:
    """Separa los números publicados ("02 01 39", "01 - 02 - 10") en textos individuales."""
    tokens: list[str] = []
    for texto in textos or ():
        tokens.extend(t for t in _SEPARADORES_NUMEROS.split(_limpio(texto)) if t)
    return tokens


# ---------------------------------------------------------------------------
# normalizar
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultadoNormalizacion:
    resultado: ResultadoIntento
    datos: DatosFuente | None
    observaciones: tuple[Observacion, ...] = ()


class _Contexto:
    """Acumula observaciones y faltantes de un intento."""

    def __init__(self, ficha: Ficha):
        self.ficha = ficha
        self.observaciones: list[Observacion] = []
        self.faltantes: list[str] = []
        self.incompleto = False

    def observar(self, codigo, texto, modalidad=None, inconsistencia=False, informativa=False):
        self.observaciones.append(
            Observacion(
                codigo=codigo,
                texto=texto,
                fuente=self.ficha.fuente,
                es_inconsistencia=inconsistencia,
                informativa=informativa,
                modalidad=modalidad,
            )
        )

    def faltar(self, descripcion: str):
        if descripcion not in self.faltantes:
            self.faltantes.append(descripcion)


def normalizar(
    pagina: PaginaCruda, ficha: Ficha, numero_pedido: int, fecha_pedida: date | None = None
) -> ResultadoNormalizacion:
    """Pasos 1 a 7 de [002] contracts/dominio.md → ``normalizacion.py``."""
    ctx = _Contexto(ficha)
    numero = parsear_numero_sorteo(pagina.numero_texto)
    fecha = parsear_fecha_fuente(pagina.fecha_texto)
    # Paso 1 (RN-10, RN-21): número y fecha reconocibles y coincidentes con lo pedido.
    if numero is None or fecha is None:
        return ResultadoNormalizacion(ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA, None)
    no_coincide = numero != numero_pedido or (
        ficha.exige_fecha_en_direccion and fecha_pedida is not None and fecha != fecha_pedida
    )
    if no_coincide:
        ctx.observar("obs.direccion_no_coincide", OBS_DIRECCION_NO_COINCIDE)
        return ResultadoNormalizacion(
            ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA, None, tuple(ctx.observaciones)
        )

    # Paso 2 (RN-11): cada bloque, solo por la tabla exacta de rótulos de la ficha.
    bloques = _agrupar_bloques(pagina.bloques, ctx)
    modalidades: dict[Modalidad, DatosModalidadFuente] = {}
    for modalidad in ORDEN_MODALIDADES:
        if modalidad not in bloques:
            ctx.faltar(nombre_modalidad(modalidad))
            continue
        modalidades[modalidad] = _normalizar_modalidad(modalidad, bloques[modalidad], fecha, ctx)

    _controles_entre_modalidades(modalidades, bloques, ctx)  # RN-12, RN-26

    # Paso 7: faltan datos que la ficha declara → Incompleto, con qué falta (AC-2.5).
    if ctx.faltantes:
        ctx.observar("obs.falta", OBS_FALTA.format(lista="; ".join(ctx.faltantes)))
    datos = DatosFuente(
        fuente=ficha.fuente,
        numero=numero,
        fecha=fecha,
        modalidades=modalidades,
        observaciones=tuple(ctx.observaciones),
    )
    resultado = (
        ResultadoIntento.INCOMPLETO
        if ctx.faltantes or ctx.incompleto
        else ResultadoIntento.OBTENIDO
    )
    return ResultadoNormalizacion(resultado, datos, tuple(ctx.observaciones))


@dataclass
class _BloqueModalidad:
    numeros_textos: tuple[str, ...] | None = None
    filas: tuple[FilaPremioCruda, ...] | None = None
    pozo_texto: str | None = None


def normalizar_rotulo(texto: str | None) -> str:
    """Rótulo sin distinguir mayúsculas y con espacios normalizados ([002] RN-11)."""
    return _limpio(texto).casefold()


def _agrupar_bloques(
    bloques: tuple[BloqueCrudo, ...], ctx: _Contexto
) -> dict[Modalidad, _BloqueModalidad]:
    """Une los bloques de una misma modalidad (F1 publica números y premios por separado).

    Un rótulo que no figura en la ficha no se asigna por parecido: observación e "Incompleto"
    ([002] RN-10, RN-11, AC-3.1).
    """
    agrupados: dict[Modalidad, _BloqueModalidad] = {}
    for bloque in bloques:
        modalidad = ctx.ficha.rotulos.get(normalizar_rotulo(bloque.rotulo))
        if modalidad is None:
            texto = OBS_ROTULO_DESCONOCIDO.format(texto=_limpio(bloque.rotulo))
            ctx.observar("obs.rotulo_desconocido", texto)
            ctx.incompleto = True
            continue
        actual = agrupados.setdefault(modalidad, _BloqueModalidad())
        if actual.numeros_textos is None and bloque.numeros_textos is not None:
            actual.numeros_textos = bloque.numeros_textos
        if actual.filas is None and bloque.filas_premios is not None:
            actual.filas = bloque.filas_premios
        if actual.pozo_texto is None and bloque.pozo_texto:
            actual.pozo_texto = bloque.pozo_texto
    return agrupados


def _normalizar_modalidad(modalidad, bloque: _BloqueModalidad, fecha: date, ctx: _Contexto):
    numeros = None
    descartados = False
    if modalidad in MODALIDADES_PROPIAS:
        if not tokens_numeros(bloque.numeros_textos):
            # Sin números publicados: no es RN-24.
            ctx.faltar(f"{nombre_modalidad(modalidad)}: números")
        else:
            numeros = _validar_seis(modalidad, bloque.numeros_textos, ctx)
            if numeros is None:
                descartados = True
                ctx.incompleto = True
                ctx.faltar(f"{nombre_modalidad(modalidad)}: números")
    categorias = _normalizar_categorias(modalidad, bloque, fecha, ctx)
    return DatosModalidadFuente(
        numeros=numeros, categorias=categorias, numeros_descartados=descartados
    )


def _validar_seis(modalidad: Modalidad, textos, ctx: _Contexto) -> frozenset[int] | None:
    """[002] RN-13, RN-24: seis números distintos de 00 a 45; nunca se corrigen."""
    tokens = tokens_numeros(textos)
    valido = True
    valores: list[int] = []
    for token in tokens:
        if not _ENTERO.match(token) or int(token) > 45:
            ctx.observar(
                "obs.numeros_rango",
                OBS_NUMEROS_RANGO.format(modalidad=nombre_modalidad(modalidad), texto=token),
                modalidad=modalidad,
            )
            valido = False
        else:
            valores.append(int(token))
    repetidos = sorted({n for n in valores if valores.count(n) > 1})
    for n in repetidos:
        ctx.observar(
            "obs.numeros_repetido",
            OBS_NUMEROS_REPETIDO.format(modalidad=nombre_modalidad(modalidad), nn=formatear(n)),
            modalidad=modalidad,
        )
        valido = False
    if len(tokens) != 6:
        ctx.observar(
            "obs.numeros_cantidad",
            OBS_NUMEROS_CANTIDAD.format(modalidad=nombre_modalidad(modalidad), n=len(tokens)),
            modalidad=modalidad,
        )
        valido = False
    return frozenset(valores) if valido else None


# ---------------------------------------------------------------------------
# Categorías e importes (RN-14 a RN-20, RN-25, RN-26)
# ---------------------------------------------------------------------------

_POR_ACIERTOS = {
    Modalidad.PRIMER_SORTEO: {6: "PRIMER", 5: "SEGUNDO", 4: "TERCER"},
    Modalidad.LA_SEGUNDA: {6: "PRIMER", 5: "SEGUNDO", 4: "TERCER"},
    Modalidad.REVANCHA: {6: "UNICO"},
}


def _parsear_aciertos(texto: str | None) -> Dato:
    limpio = _limpio(texto)
    if limpio.casefold() == SIN_GANADORES.casefold():
        return Valor(SIN_GANADORES)
    if _ENTERO.match(limpio):
        return Valor(int(limpio))
    return NO_DISPONIBLE


def _parsear_ganadores(texto: str | None, modalidad: Modalidad, ctx: _Contexto) -> Dato:
    """[002] RN-15: "Vacante" y "Pozo vacante" = 0; vacío, "-" o ausente = No disponible."""
    limpio = _limpio(texto)
    if limpio.casefold() in _VACANTE:
        return Valor(0)
    if limpio in _SIN_DATO:
        return NO_DISPONIBLE
    if _ENTERO.match(limpio):
        return Valor(int(limpio))
    if _ENTERO_MILES.match(limpio):
        return Valor(int(limpio.replace(".", "")))
    if limpio.startswith("-") and _ENTERO.match(limpio[1:].strip()):
        ctx.observar("obs.negativo", OBS_NEGATIVO.format(texto=limpio), modalidad=modalidad)
    return NO_DISPONIBLE


def _importe(texto: str | None, modalidad: Modalidad, ctx: _Contexto, millones=False):
    """Devuelve (Dato, texto original si no se pudo interpretar)."""
    limpio = _limpio(texto)
    if limpio in _SIN_DATO:
        return NO_DISPONIBLE, None
    resultado = parsear_importe_fuente(limpio, permite_millones=millones)
    if isinstance(resultado, ErrorImporteFuente):
        corregido = corregir_importe_mal_cargado(limpio)
        if corregido is not None:  # RN-16, D-18, AC-3.16: nota informativa
            ctx.observar(
                "obs.importe_corregido",
                OBS_IMPORTE_CORREGIDO.format(texto=limpio, importe=formatear_pesos(corregido)),
                modalidad=modalidad,
                informativa=True,
            )
            return Valor(corregido), None
        if resultado.codigo == "NEGATIVO":
            ctx.observar("obs.negativo", OBS_NEGATIVO.format(texto=limpio), modalidad=modalidad)
        else:
            ctx.observar(
                "obs.importe_invalido",
                OBS_IMPORTE_INVALIDO.format(texto=limpio),
                modalidad=modalidad,
            )
        return NO_DISPONIBLE, limpio
    return Valor(resultado), None


def _categoria(fila: FilaPremioCruda, aciertos: Dato, modalidad: Modalidad, ctx: _Contexto):
    """[002] RN-17, RN-20: el concepto del importe depende de la cantidad de ganadores."""
    ganadores = _parsear_ganadores(fila.ganadores_texto, modalidad, ctx)
    importe, original = _importe(fila.importe_texto, modalidad, ctx)
    pozo: Dato = NO_DISPONIBLE
    individual: Dato = NO_DISPONIBLE
    if isinstance(ganadores, Valor) and ganadores.v == 0:
        individual = NO_CORRESPONDE  # AC-3.4, AC-3.14
        if isinstance(importe, Valor) and importe.v != 0:
            pozo = importe
        # "0,00" con 0 ganadores es el importe individual: No corresponde (RN-20).
    elif isinstance(ganadores, Valor):
        individual = importe  # AC-3.5: el pozo de una categoría con ganadores no se publica
    elif _limpio(fila.importe_texto) not in _SIN_DATO and original is None:
        ctx.observar(
            "obs.concepto_importe",
            OBS_CONCEPTO_IMPORTE.format(texto=_limpio(fila.importe_texto)),
            modalidad=modalidad,
        )
    return DatosCategoriaFuente(
        aciertos=aciertos,
        ganadores=ganadores,
        pozo_destinado=pozo,
        importe_individual=individual,
        texto_original=original,
    )


def _normalizar_categorias(modalidad, bloque: _BloqueModalidad, fecha: date, ctx: _Contexto):
    categorias: dict[str, DatosCategoriaFuente] = {}
    filas = bloque.filas
    if filas is None:
        for codigo in categorias_esperadas(modalidad):
            ctx.faltar(f"{nombre_modalidad(modalidad)}: {nombre_categoria(codigo)}")
        return categorias
    reglas_vigentes = fecha >= FECHA_VIGENCIA_REGLAS
    for fila in filas:
        aciertos = _parsear_aciertos(fila.aciertos_texto)
        codigo = _codigo_categoria(modalidad, aciertos, categorias)
        if codigo is None:
            n = aciertos.v if isinstance(aciertos, Valor) else None
            if not reglas_vigentes and isinstance(n, int):
                codigo = codigo_aciertos(n)  # RN-25: "Categoría de N aciertos"
            else:
                aciertos_texto = _limpio(fila.aciertos_texto) or "-"
                texto = f"{nombre_modalidad(modalidad)}, {aciertos_texto} aciertos"
                ctx.observar(
                    "obs.categoria_fuera_catalogo",
                    OBS_CATEGORIA_FUERA_CATALOGO.format(texto=texto),
                    modalidad=modalidad,
                )
                continue
        if codigo in categorias:
            continue
        categorias[codigo] = _categoria(fila, aciertos, modalidad, ctx)

    if modalidad is Modalidad.PREMIO_EXTRA and "GANADORA" in categorias:
        categorias["GANADORA"] = _pozo_premio_extra(categorias["GANADORA"], bloque, ctx)

    for codigo in categorias_esperadas(modalidad):
        _faltantes_categoria(modalidad, codigo, categorias.get(codigo), ctx)
    _validar_ganadora(modalidad, categorias.get("GANADORA"), ctx)
    return categorias


def _codigo_categoria(modalidad: Modalidad, aciertos: Dato, ya: dict) -> str | None:
    """[002] RN-14: categoría del catálogo por modalidad y aciertos."""
    if modalidad in _POR_ACIERTOS:
        if isinstance(aciertos, Valor) and isinstance(aciertos.v, int):
            return _POR_ACIERTOS[modalidad].get(aciertos.v)
        return None
    # Siempre Sale y Premio Extra: una sola categoría ganadora, con sus aciertos.
    return None if "GANADORA" in ya else "GANADORA"


def _pozo_premio_extra(categoria: DatosCategoriaFuente, bloque, ctx: _Contexto):
    """[002] RN-17: el pozo de Premio Extra solo se toma de F1 ("N millones de pesos")."""
    if not ctx.ficha.publica_pozo_premio_extra:
        return categoria  # F2 publica un texto fijo; F3 no lo publica
    texto = _limpio(bloque.pozo_texto)
    if not texto:
        ctx.faltar(f"{nombre_modalidad(Modalidad.PREMIO_EXTRA)}: pozo destinado")
        return categoria
    pozo, original = _importe(texto, Modalidad.PREMIO_EXTRA, ctx, millones=True)
    if isinstance(pozo, Valor):
        ctx.observar(
            "obs.pozo_premio_extra_texto",
            OBS_POZO_PREMIO_EXTRA_TEXTO.format(texto=texto),
            modalidad=Modalidad.PREMIO_EXTRA,
            informativa=True,
        )
    return DatosCategoriaFuente(
        aciertos=categoria.aciertos,
        ganadores=categoria.ganadores,
        pozo_destinado=pozo,
        importe_individual=categoria.importe_individual,
        texto_original=categoria.texto_original or original,
    )


def _faltantes_categoria(modalidad, codigo, categoria: DatosCategoriaFuente | None, ctx):
    nombre = f"{nombre_modalidad(modalidad)}: {nombre_categoria(codigo)}"
    if categoria is None:
        ctx.faltar(nombre)
        return
    if not isinstance(categoria.ganadores, Valor):
        ctx.faltar(f"{nombre}: ganadores")
        return
    es_premio_extra_f1 = modalidad is Modalidad.PREMIO_EXTRA and ctx.ficha.publica_pozo_premio_extra
    if (
        categoria.ganadores.v == 0
        and not es_premio_extra_f1
        and not isinstance(categoria.pozo_destinado, Valor)
    ):
        ctx.faltar(f"{nombre}: pozo destinado")
    if categoria.ganadores.v > 0 and not isinstance(categoria.importe_individual, Valor):
        ctx.faltar(f"{nombre}: importe individual")
    publica_aciertos = (
        modalidad is not Modalidad.PREMIO_EXTRA or ctx.ficha.publica_aciertos_premio_extra
    )
    if publica_aciertos and not isinstance(categoria.aciertos, Valor):
        ctx.faltar(f"{nombre}: aciertos")


def _validar_ganadora(modalidad: Modalidad, categoria: DatosCategoriaFuente | None, ctx):
    """[002] RN-26: categoría ganadora de Siempre Sale y de Premio Extra. El mismo control
    descarta el dato en la consolidación (D-29)."""
    if categoria is None or modalidad not in _OBS_GANADORA_INVALIDA:
        return
    if any(
        viola_rn_26(modalidad, "GANADORA", campo, getattr(categoria, campo))
        for campo in ("aciertos", "ganadores")
    ):
        codigo, texto = _OBS_GANADORA_INVALIDA[modalidad]
        ctx.observar(codigo, texto, modalidad=modalidad, inconsistencia=True)


_OBS_GANADORA_INVALIDA = {
    Modalidad.SIEMPRE_SALE: ("obs.siempre_sale_invalida", OBS_SIEMPRE_SALE_INVALIDA),
    Modalidad.PREMIO_EXTRA: ("obs.premio_extra_invalida", OBS_PREMIO_EXTRA_INVALIDA),
}


def _controles_entre_modalidades(modalidades, bloques, ctx: _Contexto):
    """[002] RN-12 (números de Premio Extra) y RN-26 (extracciones con los mismos números)."""
    bloque_extra = bloques.get(Modalidad.PREMIO_EXTRA)
    if ctx.ficha.publica_numeros_premio_extra and bloque_extra and bloque_extra.numeros_textos:
        publicados = tokens_numeros(bloque_extra.numeros_textos)
        propias = [modalidades.get(m) for m in MODALIDADES_PREMIO_EXTRA]
        if all(p is not None and p.numeros is not None for p in propias):
            union = frozenset().union(*(p.numeros for p in propias))
            conjunto = {int(t) for t in publicados if _ENTERO.match(t)}
            no_validos = any(not _ENTERO.match(t) for t in publicados)
            if no_validos or conjunto != union:
                ctx.observar(
                    "obs.premio_extra_no_coincide",
                    OBS_PREMIO_EXTRA_NO_COINCIDE,
                    modalidad=Modalidad.PREMIO_EXTRA,
                    inconsistencia=True,
                )
    propias_validas = [
        (m, modalidades[m].numeros)
        for m in MODALIDADES_PROPIAS
        if m in modalidades and modalidades[m].numeros is not None
    ]
    for i, (a, numeros_a) in enumerate(propias_validas):
        for b, numeros_b in propias_validas[i + 1 :]:
            if numeros_a == numeros_b:
                ctx.observar(
                    "obs.extracciones_iguales",
                    OBS_EXTRACCIONES_IGUALES.format(a=nombre_modalidad(a), b=nombre_modalidad(b)),
                    informativa=True,
                )
