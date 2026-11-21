"""Tipos del dominio de la extracción histórica ([002] data-model.md, contracts/dominio.md).

No importa Django: son valores inmutables. Los errores se devuelven como valores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

from dominio.tipos import Modalidad, Numeros

# ---------------------------------------------------------------------------
# Dato: las cuatro situaciones de [002] RN-20
# ---------------------------------------------------------------------------

#: Texto de la categoría ganadora de Premio Extra sin ganadores ([002] RN-14, RN-26).
SIN_GANADORES = "Sin ganadores"


@dataclass(frozen=True)
class Valor:
    """Un valor informado, incluido el cero ([002] RN-20).

    ``v`` es ``int``, ``Decimal``, ``date``, ``bool``, un conjunto de números (``frozenset``)
    o el texto ``SIN_GANADORES``. Un ``Dato`` nunca se crea a partir de un valor ausente
    convertido en cero.
    """

    v: object

    def __post_init__(self):
        if self.v is None:
            raise ValueError("Un Valor no puede ser nulo: usar NO_DISPONIBLE ([002] RN-20).")
        if isinstance(self.v, float):
            raise TypeError("Los importes se manejan con Decimal, nunca con float.")


class EstadoDato(Enum):
    """Las tres situaciones sin valor de [002] RN-20."""

    NO_DISPONIBLE = "no_disponible"
    NO_CORRESPONDE = "no_corresponde"
    SIN_DETERMINAR = "sin_determinar"

    @property
    def texto(self) -> str:
        return _TEXTOS_ESTADO_DATO[self]


_TEXTOS_ESTADO_DATO = {
    EstadoDato.NO_DISPONIBLE: "No disponible",
    EstadoDato.NO_CORRESPONDE: "No corresponde",
    EstadoDato.SIN_DETERMINAR: "Sin determinar",
}

NO_DISPONIBLE = EstadoDato.NO_DISPONIBLE
NO_CORRESPONDE = EstadoDato.NO_CORRESPONDE
SIN_DETERMINAR = EstadoDato.SIN_DETERMINAR

Dato = Valor | EstadoDato


def es_valor(dato: Dato) -> bool:
    return isinstance(dato, Valor)


# ---------------------------------------------------------------------------
# Catálogos fijos
# ---------------------------------------------------------------------------


class Fuente(Enum):
    """Lista cerrada de fuentes ([002] RN-06). El nombre visible es el dominio del sitio."""

    F1 = "F1"
    F2 = "F2"
    F3 = "F3"

    @property
    def nombre(self) -> str:
        return _NOMBRES_FUENTE[self]


_NOMBRES_FUENTE = {
    Fuente.F1: "quini-6-resultados.com.ar",
    Fuente.F2: "numerosganadores.com.ar",
    Fuente.F3: "quiniya.com.ar",
}

#: Prioridad de las fuentes ([002] RN-07, D-14): 1.ª numerosganadores (F2), 2.ª quiniya (F3) y
#: 3.ª quini-6-resultados (F1). Ante una diferencia prevalece la de mayor prioridad (salvo
#: importes con diferencia del 1 % o más, RN-30). También es el orden de presentación.
ORDEN_FUENTES: tuple[Fuente, ...] = (Fuente.F2, Fuente.F3, Fuente.F1)

#: Fuentes de respaldo: solo se consultan si con las demás falta algún dato ([002] RN-09).
FUENTES_RESPALDO: tuple[Fuente, ...] = (Fuente.F1,)


def prioridad(fuente: Fuente) -> int:
    """Posición de la fuente en ``ORDEN_FUENTES`` (0 = mayor prioridad)."""
    return ORDEN_FUENTES.index(fuente)


class ResultadoIntento(Enum):
    """Resultado de cada intento por sorteo y fuente ([002] RN-08)."""

    OBTENIDO = "OBTENIDO"
    INCOMPLETO = "INCOMPLETO"
    NO_ENCONTRADO = "NO_ENCONTRADO"
    NO_DISPONIBLE = "NO_DISPONIBLE"
    NO_DISPONIBLE_O_NO_ENCONTRADO = "NO_DISPONIBLE_O_NO_ENCONTRADO"
    ESTRUCTURA_NO_RECONOCIDA = "ESTRUCTURA_NO_RECONOCIDA"
    FUERA_DE_COBERTURA = "FUERA_DE_COBERTURA"
    #: [002] RN-08, RN-09, AC-2.11: la fuente de respaldo no hizo falta.
    NO_REQUERIDA = "NO_REQUERIDA"

    @property
    def texto(self) -> str:
        return _TEXTOS_RESULTADO[self]

    @property
    def es_fallido(self) -> bool:
        """AC-2.1: todos menos "Obtenido", "Fuera de cobertura" y "No requerida"."""
        return self not in (
            ResultadoIntento.OBTENIDO,
            ResultadoIntento.FUERA_DE_COBERTURA,
            ResultadoIntento.NO_REQUERIDA,
        )

    @property
    def no_consultada(self) -> bool:
        """La fuente no se consultó para el sorteo (no cuenta para un hueco, I-10)."""
        return self in (ResultadoIntento.FUERA_DE_COBERTURA, ResultadoIntento.NO_REQUERIDA)

    @property
    def aporta_datos(self) -> bool:
        return self in (ResultadoIntento.OBTENIDO, ResultadoIntento.INCOMPLETO)


_TEXTOS_RESULTADO = {
    ResultadoIntento.OBTENIDO: "Obtenido",
    ResultadoIntento.INCOMPLETO: "Incompleto",
    ResultadoIntento.NO_ENCONTRADO: "No encontrado",
    ResultadoIntento.NO_DISPONIBLE: "No disponible",
    ResultadoIntento.NO_DISPONIBLE_O_NO_ENCONTRADO: "No disponible o no encontrado",
    ResultadoIntento.ESTRUCTURA_NO_RECONOCIDA: "Estructura no reconocida",
    ResultadoIntento.FUERA_DE_COBERTURA: "Fuera de cobertura",
    ResultadoIntento.NO_REQUERIDA: "No requerida",
}


#: Nombres de las modalidades en la pantalla de extracción y en el CSV ([002] RN-11, D-15).
#: El resto de la aplicación ([001]) sigue usando ``Modalidad.nombre``.
_NOMBRES_MODALIDAD = {
    Modalidad.PRIMER_SORTEO: "Tradicional",
    Modalidad.LA_SEGUNDA: "La Segunda",
    Modalidad.REVANCHA: "Revancha",
    Modalidad.SIEMPRE_SALE: "Siempre Sale",
    Modalidad.PREMIO_EXTRA: "Pozo Extra",
}


def nombre_modalidad(modalidad: Modalidad) -> str:
    return _NOMBRES_MODALIDAD[modalidad]


#: Textos de los datos calculados ([002] RN-12, RN-18, contracts/mensajes.md "calculo.*").
CALCULO_POZO = "importe individual × ganadores"
CALCULO_VACANTE = "sin ganadores"
CALCULO_POZO_EXTRA = "unión de Tradicional, La Segunda y Revancha"


class EstadoSorteo(Enum):
    """Estado de un sorteo, en orden de precedencia ([002] RN-31)."""

    NO_RECUPERADO = "NO_RECUPERADO"
    CON_INCONSISTENCIAS = "CON_INCONSISTENCIAS"
    PARCIAL = "PARCIAL"
    RECUPERADO = "RECUPERADO"

    @property
    def texto(self) -> str:
        return _TEXTOS_ESTADO_SORTEO[self]


_TEXTOS_ESTADO_SORTEO = {
    EstadoSorteo.NO_RECUPERADO: "No recuperado",
    EstadoSorteo.CON_INCONSISTENCIAS: "Con inconsistencias",
    EstadoSorteo.PARCIAL: "Recuperado parcialmente",
    EstadoSorteo.RECUPERADO: "Recuperado",
}


class EstadoExtraccion(Enum):
    """Estado de una extracción ([002] data-model.md, RN-33, AC-1.10)."""

    EN_CURSO = "EN_CURSO"
    FINALIZADA = "FINALIZADA"
    CON_ADVERTENCIAS = "CON_ADVERTENCIAS"
    SIN_SORTEOS = "SIN_SORTEOS"

    @property
    def texto(self) -> str:
        return _TEXTOS_ESTADO_EXTRACCION[self]


_TEXTOS_ESTADO_EXTRACCION = {
    EstadoExtraccion.EN_CURSO: "Extracción en curso",
    EstadoExtraccion.FINALIZADA: "Extracción finalizada",
    EstadoExtraccion.CON_ADVERTENCIAS: (
        "Extracción finalizada con advertencias que requieren revisión"
    ),
    EstadoExtraccion.SIN_SORTEOS: "No se identificaron sorteos en el período consultado",
}


class ClaveCategoria(Enum):
    """Categorías por modalidad ([002] RN-14, RN-25).

    En los diccionarios de categorías la clave es un código de texto: el valor del enum para
    las categorías del catálogo y ``ACIERTOS_{n}`` para "Categoría de N aciertos".
    """

    PRIMER = "PRIMER"
    SEGUNDO = "SEGUNDO"
    TERCER = "TERCER"
    UNICO = "UNICO"
    GANADORA = "GANADORA"
    ACIERTOS_N = "ACIERTOS_N"


_NOMBRES_CATEGORIA = {
    "PRIMER": "Primer Premio",
    "SEGUNDO": "Segundo Premio",
    "TERCER": "Tercer Premio",
    "UNICO": "Premio Revancha",
    "GANADORA": "Categoría ganadora",
}

#: Aciertos que definen las categorías fijas ([002] data-model.md, "Categorías por modalidad").
ACIERTOS_FIJOS = {"PRIMER": 6, "SEGUNDO": 5, "TERCER": 4, "UNICO": 6}

_ESPERADAS = {
    Modalidad.PRIMER_SORTEO: ("PRIMER", "SEGUNDO", "TERCER"),
    Modalidad.LA_SEGUNDA: ("PRIMER", "SEGUNDO", "TERCER"),
    Modalidad.REVANCHA: ("UNICO",),
    Modalidad.SIEMPRE_SALE: ("GANADORA",),
    Modalidad.PREMIO_EXTRA: ("GANADORA",),
}

#: Modalidades con extracción propia (seis números, [002] RN-24).
MODALIDADES_PROPIAS: tuple[Modalidad, ...] = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
)


def categorias_esperadas(modalidad: Modalidad) -> tuple[str, ...]:
    """Categorías esperadas de la modalidad. ``ACIERTOS_N`` nunca es esperada."""
    return _ESPERADAS[modalidad]


def codigo_aciertos(n: int) -> str:
    return f"ACIERTOS_{n}"


def clave_de(codigo: str) -> ClaveCategoria:
    if codigo.startswith("ACIERTOS_"):
        return ClaveCategoria.ACIERTOS_N
    return ClaveCategoria(codigo)


def aciertos_de_codigo(codigo: str) -> int | None:
    """Aciertos de una categoría ``ACIERTOS_N`` o de una fija; ``None`` para la ganadora."""
    if codigo.startswith("ACIERTOS_"):
        return int(codigo.removeprefix("ACIERTOS_"))
    return ACIERTOS_FIJOS.get(codigo)


def nombre_categoria(codigo: str) -> str:
    """Nombre en pantalla y en el archivo ("Categoría de N aciertos", [002] RN-25)."""
    if codigo.startswith("ACIERTOS_"):
        return f"Categoría de {aciertos_de_codigo(codigo)} aciertos"
    return _NOMBRES_CATEGORIA[codigo]


def orden_categorias(modalidad: Modalidad, codigos) -> list[str]:
    """Esperadas en su orden y al final las "Categoría de N aciertos" por aciertos descendentes."""
    esperadas = [c for c in categorias_esperadas(modalidad) if c in codigos]
    extra = sorted(
        (c for c in codigos if c not in categorias_esperadas(modalidad)),
        key=lambda c: -(aciertos_de_codigo(c) or 0),
    )
    return esperadas + extra


# ---------------------------------------------------------------------------
# Salida de los intérpretes (solo textos sin interpretar)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FilaPremioCruda:
    aciertos_texto: str | None
    ganadores_texto: str | None
    importe_texto: str | None


@dataclass(frozen=True)
class BloqueCrudo:
    """Un bloque de la página con su rótulo.

    ``numeros_textos`` es ``None`` si el bloque no tiene números; ``filas_premios`` es ``None``
    si no tiene tabla de premios. Una fuente puede presentar la misma modalidad en dos bloques
    (F1: números y premios por separado).
    """

    rotulo: str
    numeros_textos: tuple[str, ...] | None = None
    filas_premios: tuple[FilaPremioCruda, ...] | None = None
    pozo_texto: str | None = None


@dataclass(frozen=True)
class PaginaCruda:
    numero_texto: str | None
    fecha_texto: str | None
    bloques: tuple[BloqueCrudo, ...] = ()


@dataclass(frozen=True)
class NoReconocida:
    """La página no tiene la estructura conocida de la fuente ([002] RN-10)."""

    motivo: str = ""


@dataclass(frozen=True)
class ReferenciaListado:
    """Fila de un listado, sin interpretar."""

    numero_texto: str
    fecha_texto: str


# ---------------------------------------------------------------------------
# Observaciones, datos de una fuente y consolidado
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Observacion:
    """Observación del detalle ([002] contracts/mensajes.md, "Observaciones y motivos")."""

    codigo: str
    texto: str
    fuente: Fuente | None = None
    es_inconsistencia: bool = False
    informativa: bool = False
    modalidad: Modalidad | None = None


@dataclass(frozen=True)
class DatosCategoriaFuente:
    aciertos: Dato
    ganadores: Dato
    pozo_destinado: Dato
    importe_individual: Dato
    texto_original: str | None = None


@dataclass(frozen=True)
class DatosModalidadFuente:
    numeros: Numeros | None
    categorias: dict[str, DatosCategoriaFuente] = field(default_factory=dict)
    numeros_descartados: bool = False


@dataclass(frozen=True)
class DatosFuente:
    """Lo que informó una fuente para un sorteo, ya normalizado."""

    fuente: Fuente
    numero: int
    fecha: date
    modalidades: dict[Modalidad, DatosModalidadFuente] = field(default_factory=dict)
    observaciones: tuple[Observacion, ...] = ()


class TipoDiscrepancia(Enum):
    VALOR_DISTINTO = "VALOR_DISTINTO"
    OMISION = "OMISION"
    CENTAVOS = "CENTAVOS"
    #: [002] RN-07, D-21: dos de tres fuentes coinciden; es una nota informativa.
    MAYORIA = "MAYORIA"

    @property
    def texto(self) -> str:
        return _TEXTOS_DISCREPANCIA[self]


_TEXTOS_DISCREPANCIA = {
    TipoDiscrepancia.VALOR_DISTINTO: "Valor distinto",
    TipoDiscrepancia.OMISION: "Omisión",
    #: Desde el 20/11/2026 es una nota informativa, no una discrepancia ([002] RN-30, D-17).
    TipoDiscrepancia.CENTAVOS: "Diferencia de centavos o redondeo (menor al 1 %)",
    TipoDiscrepancia.MAYORIA: "Resuelto por coincidencia de 2 de 3 fuentes",
}


@dataclass(frozen=True)
class Discrepancia:
    """``valores``: (fuente, valor) por cada fuente; ``None`` es la omisión ("sin dato")."""

    tipo: TipoDiscrepancia
    valores: tuple[tuple[Fuente, object], ...]


@dataclass(frozen=True)
class DatoConsolidado:
    """``discrepancia``: diferencia que deja el sorteo "Con inconsistencias" (RN-27).
    ``diferencia_tolerada``: diferencia de importes menor al 1 %, solo informativa (RN-30).
    ``calculo``: texto del cálculo si el sistema calculó el valor (RN-12, RN-18); un dato
    calculado no tiene fuentes."""

    dato: Dato
    fuentes: tuple[Fuente, ...] = ()
    sin_corroborar: bool = False
    discrepancia: Discrepancia | None = None
    diferencia_tolerada: Discrepancia | None = None
    calculo: str | None = None


NO_DISPONIBLE_CONSOLIDADO = DatoConsolidado(NO_DISPONIBLE)


class EstadoPozo(Enum):
    CON_GANADORES = "CON_GANADORES"
    VACANTE = "VACANTE"
    PENDIENTE = "PENDIENTE"
    SIN_DETERMINAR = "SIN_DETERMINAR"

    @property
    def texto(self) -> str:
        return _TEXTOS_POZO[self]


_TEXTOS_POZO = {
    EstadoPozo.CON_GANADORES: "Con ganadores",
    EstadoPozo.VACANTE: "Vacante",
    EstadoPozo.PENDIENTE: "Pendiente",
    EstadoPozo.SIN_DETERMINAR: "Sin determinar",
}


@dataclass(frozen=True)
class CategoriaConsolidada:
    aciertos: DatoConsolidado
    ganadores: DatoConsolidado
    pozo_destinado: DatoConsolidado
    importe_individual: DatoConsolidado
    #: [002] RN-19. Sin acumulación ni importe trasladado desde D-22 (20/11/2026).
    estado_pozo: EstadoPozo


@dataclass(frozen=True)
class ModalidadConsolidada:
    informada: bool
    numeros: DatoConsolidado
    categorias: dict[str, CategoriaConsolidada] = field(default_factory=dict)


@dataclass(frozen=True)
class SorteoConsolidado:
    numero: int
    fecha: DatoConsolidado
    modalidades: dict[Modalidad, ModalidadConsolidada]
    resultados: dict[Fuente, ResultadoIntento] = field(default_factory=dict)
    estado: EstadoSorteo = EstadoSorteo.NO_RECUPERADO
    combina_fuentes: bool = False
    sin_corroborar: bool = False
    motivos: tuple[str, ...] = ()
    observaciones: tuple[Observacion, ...] = ()
    reglas_no_verificadas: bool = False
    error_inesperado: bool = False


# ---------------------------------------------------------------------------
# Ficha de una fuente (estructura, sin valores: los valores están en extracciones/fuentes)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Ficha:
    fuente: Fuente
    nombre: str
    url_base: str
    ruta_listado: str
    #: Plantilla con ``{numero}`` y, si la fuente lo exige, ``{fecha}`` (dd-mm-aaaa).
    ruta_sorteo: str
    exige_fecha_en_direccion: bool
    #: Primer número cubierto; ``None`` si la cobertura la da el listado (F1, I-08).
    cobertura_desde_numero: int | None
    #: Rótulo normalizado (minúsculas, espacios simples) → modalidad ([002] RN-11).
    rotulos: dict[str, Modalidad]
    #: Código HTTP de "sorteo inexistente" → resultado ([002] R-02).
    codigos_inexistente: dict[int, ResultadoIntento]
    marcadores_antirobots: tuple[str, ...]
    publica_numeros_premio_extra: bool
    publica_aciertos_premio_extra: bool
    publica_pozo_premio_extra: bool

    @property
    def cobertura_por_listado(self) -> bool:
        return self.cobertura_desde_numero is None

    def url_listado(self) -> str:
        return self.url_base.rstrip("/") + self.ruta_listado

    def url_sorteo(self, numero: int, fecha: date | None = None) -> str:
        texto_fecha = fecha.strftime("%d-%m-%Y") if fecha else ""
        return self.url_base.rstrip("/") + self.ruta_sorteo.format(numero=numero, fecha=texto_fecha)

    def publica(self, dato: str, modalidad: Modalidad, con_ganadores: bool | None) -> bool:
        """Si la fuente publica el dato por diseño ([002] RN-28, contracts/fuentes.md).

        ``dato`` ∈ ``aciertos``, ``ganadores``, ``pozo_destinado``, ``importe_individual``,
        ``numeros``, ``fecha``.
        """
        if modalidad is Modalidad.PREMIO_EXTRA:
            if dato == "numeros":
                return False
            if dato == "aciertos":
                return self.publica_aciertos_premio_extra
            if dato == "pozo_destinado" and self.publica_pozo_premio_extra:
                return True
        if dato == "pozo_destinado":
            return con_ganadores is False
        if dato == "importe_individual":
            return con_ganadores is True
        return True


#: Importes: el dominio nunca usa float ([002] NFR-007).
Importe = Decimal
