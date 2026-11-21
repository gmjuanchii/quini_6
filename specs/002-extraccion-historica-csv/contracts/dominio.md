# Contrato del dominio de la extracción (reglas puras)

**Plan**: [../plan.md](../plan.md) | **Decisión**: [../research.md](../research.md) R-07 | **Tipos**: [../data-model.md](../data-model.md) → "Tipos del dominio"

El subpaquete `dominio/extraccion/` sigue las reglas de [001] [contracts/dominio.md](../../001-quini6-mvp/contracts/dominio.md): no importa Django, no accede a la base ni a la red, recibe valores y devuelve valores, y los errores son valores. Es la **única** implementación de RN-01 a RN-39 y RN-43: el servicio y las vistas lo invocan y no repiten la lógica. Las firmas son orientativas.

Reutiliza de `dominio/`: `Modalidad`, `ORDEN_MODALIDADES`, `FECHA_VIGENCIA_REGLAS` (`tipos.py`), `formatear` (`numeros.py`), y `parsear_pesos` y `a_texto_decimal` (`importes.py`).

## `tipos.py`

`Dato` (`Valor`, `NO_DISPONIBLE`, `NO_CORRESPONDE`, `SIN_DETERMINAR`), `Fuente`, `ResultadoIntento`, `EstadoSorteo`, `ClaveCategoria`, `PaginaCruda`, `DatosFuente`, `DatoConsolidado`, `Discrepancia`, `Observacion`, `SorteoConsolidado`, `Ficha` (la estructura de las fichas, sin sus valores). Detalle en [data-model.md](../data-model.md).

`PaginaCruda` es la salida de los intérpretes de `extracciones/fuentes/`: `numero_texto`, `fecha_texto` y una lista de bloques con `rotulo`, `numeros_textos`, `filas_premios` (`aciertos_texto`, `ganadores_texto`, `importe_texto`) y `pozo_texto`. Todo texto sin interpretar.

## `periodo.py` — RN-01 a RN-04

| Función | Entrada | Salida |
|---------|---------|--------|
| `validar_periodo(inicio_texto, fin_texto, hoy)` | dos textos `dd/mm/aaaa` y la fecha local de hoy | `Periodo(desde, hasta)` o lista de `ErrorPeriodo` (`FECHA_INVALIDA` por campo, `INICIO_POSTERIOR`, `FIN_FUTURA`, `PERIODO_LARGO`) |
| `mismo_dia_anio_siguiente(fecha)` | `date` | `date` (del 29/02 da el 01/03, I-01) |

Casos obligatorios: AC-1.3 a AC-1.6, incluidos 01/01/2026–31/12/2026 válido y 01/01/2026–01/01/2027 inválido, y el 29/02.

## `identificacion.py` — RN-05

### `identificar_sorteos(periodo, referencias, fecha_de, primer_cubierto) -> Identificacion | SinSorteos`

- `referencias`: lista de `(numero, fecha, fuente)` de los listados.
- `fecha_de(numero) -> list[date]`: fechas que informan las fuentes para ese número (vacía si ninguna). La inyecta el servicio, que consulta y guarda en memoria las páginas ([002] R-06).
- `primer_cubierto`: `(numero, fecha)` del sorteo más antiguo que cubre alguna ficha (2211, 17/12/2014).
- Devuelve `Identificacion(numero_desde, numero_hasta, cobertura_desde | None)`. Un número entra si alguna de sus fechas cae en el período (I-02). Nunca deduce una fecha del calendario.

Casos obligatorios: AC-1.7 (incluye el primer y el último día), AC-1.10, AC-1.16 (hueco), AC-1.17 (cobertura), un sorteo especial fuera de los días habituales y un número cuya fecha queda fuera del período.

## `normalizacion.py` — RN-11 a RN-20, RN-24, RN-26

### `normalizar(pagina: PaginaCruda, ficha: Ficha, numero_pedido, fecha_pedida) -> (ResultadoIntento, DatosFuente | None)`

1. Número y fecha irreconocibles, o distintos de los pedidos cuando la ficha lo exige (F1, RN-21) → `ESTRUCTURA_NO_RECONOCIDA` sin datos (RN-10).
2. Cada bloque se asigna a una modalidad **solo** por la tabla exacta de la ficha. Un rótulo desconocido → observación y `INCOMPLETO` (RN-10, RN-11, AC-3.1).
3. Números: se parsean, se validan seis distintos de 00 a 45 y se guardan como conjunto. Si no cumplen, se descartan con su observación y el intento es `INCOMPLETO` (RN-13, RN-24, AC-3.2, AC-3.9). Los de Premio Extra solo se comparan con la unión de las tres extracciones de la misma fuente y nunca se guardan como números de Premio Extra (RN-12, AC-3.13).
4. Categorías: por modalidad y aciertos con RN-14. Antes del 18/06/2024, una categoría fuera del catálogo se guarda como `ACIERTOS_N`; desde esa fecha, se observa y no se asigna (RN-25).
5. Ganadores: RN-15. Importe: `parsear_importe_fuente` y concepto según la ficha (RN-17). Con 0 ganadores, el importe es `pozo_destinado` y el importe individual es `NO_CORRESPONDE`, aunque la fuente publique "0,00" (RN-20, AC-3.4, AC-3.14). Con 1 o más, el importe es `importe_individual` y el pozo es `NO_DISPONIBLE` (AC-3.5). Sin ganadores disponibles, ambos son `NO_DISPONIBLE` (AC-3.7).
6. Controles de RN-26 como observaciones.
7. Faltan datos que la ficha declara → `INCOMPLETO`, con la observación de qué falta (AC-2.5). Si no → `OBTENIDO`.

### `parsear_importe_fuente(texto, permite_millones=False) -> Decimal | ErrorImporteFuente`

Quita "$" y espacios, y delega en `parsear_pesos`. Con `permite_millones` (solo el pozo de Premio Extra de F1), acepta "N millones de pesos" con N entero o con coma decimal y devuelve N × 1.000.000 exactos. Cualquier otro texto → error con el texto original (RN-16, AC-3.8). Nunca usa `float`.

## `consolidacion.py` — RN-07, RN-09, RN-22, RN-23, RN-27 a RN-30, RN-32

### `consolidar(numero, intentos: list[(Fuente, ResultadoIntento, DatosFuente | None)], fichas) -> SorteoConsolidado`

- Cada dato se compara entre las fuentes que lo informan, como conjunto en el caso de los números. Iguales → `Valor` con la lista de fuentes; una sola → `sin_corroborar` (AC-4.6, AC-4.8). Distintos → `SIN_DETERMINAR` con `Discrepancia` (`VALOR_DISTINTO` o `CENTAVOS` según I-04) y todos los valores (AC-4.1, AC-4.5). Ninguna fuente prevalece.
- Omisión: una fuente que por su ficha publica el dato, con intento obtenido o incompleto, no lo presenta y otra sí → `Discrepancia(OMISION)` (AC-4.2). Un dato que la ficha declara como no publicado no se compara (AC-4.3).
- Fechas distintas para el número → discrepancia en `fecha` (AC-4.4).
- `combina_fuentes` según I-03 (AC-4.7).

### `revisar_correlatividad(sorteos: list[SorteoConsolidado]) -> list[SorteoConsolidado]`

RN-23: si un número mayor tiene una fecha anterior a la de uno menor, agrega a ambos una observación de inconsistencia. Se aplica al terminar, sobre todos los sorteos de la extracción, antes de clasificar.

## `clasificacion.py` — RN-31

### `clasificar(sorteo: SorteoConsolidado) -> (EstadoSorteo, motivos)`

Precedencia: `NO_RECUPERADO` (ninguna fuente aportó datos válidos) → `CON_INCONSISTENCIAS` (alguna discrepancia u observación de inconsistencia) → `PARCIAL` (falta algún dato esperado) → `RECUPERADO`. Datos esperados: número, fecha, seis números de cada extracción propia y, por categoría esperada, ganadores y el importe que corresponde a su estado. El pozo de una categoría con ganadores no es esperado (AC-3.6). Un importe inválido deja el dato `NO_DISPONIBLE` y el sorteo no queda `RECUPERADO` (AC-3.8). Una modalidad no informada deja el sorteo no `RECUPERADO` (AC-3.12). "Combina fuentes" y "Sin corroborar" no cambian el estado.

## `resumen.py` — RN-10, RN-33

### `resumir(identificacion, sorteos, intentos_por_fuente) -> Resumen`

Cantidades por estado (suman los identificados), fuentes con sorteos aportados (I-05) e intentos por resultado, marca "Requiere mantenimiento" (RN-10, AC-2.10), huecos, aviso de cobertura, lista a revisar y resultado global (`FINALIZADA` o `CON_ADVERTENCIAS`). Forma en [data-model.md](../data-model.md) → "Resumen guardado".

## `archivo_csv.py` — RN-34 a RN-39, RN-43, NFR-009, NFR-010

### `generar_csv(sorteos: list[SorteoConsolidado], intentos, fichas) -> str`

Produce el texto exacto de [csv.md](csv.md): encabezados, orden de filas, formatos técnicos, estados explícitos, procedencia, discrepancias, observaciones y protección contra fórmulas. Es determinista: la misma entrada produce el mismo texto.

## Casos de prueba obligatorios

- Uno o más casos por criterio de las historias 2, 3, 4 y 5 (SC-001), con los valores de los ejemplos de la spec: 1.100.000.000 vacante, 18 ganadores con 3.013.912, "494,443,71", 5.015 frente a 5.547,85, 12.060 frente a 12.060,13, los números "02 01 39 13 10 38" frente a "01 - 02 - 10 - 13 - 38 - 39", Siempre Sale con 5 aciertos y 17 ganadores, y "55 millones de pesos".
- SC-002: ningún importe del archivo es un producto o un cociente, y ningún dato desconocido figura como `0` o `Vacante`.
- Sorteos del 17/06/2024 y del 18/06/2024 (RN-25).
