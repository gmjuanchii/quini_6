# Contrato del dominio (reglas puras)

**Plan**: [../plan.md](../plan.md) | **Decisión**: [../research.md](../research.md) R-07

El paquete `dominio/` no importa Django ni accede a la base de datos. Recibe valores y devuelve valores. Es la **única** implementación de las reglas de negocio de jugadas, comparación y estadísticas: las vistas y los servicios lo invocan, no repiten la lógica. Las firmas son orientativas (Python con tipos). El cuerpo de cada función se define en la implementación.

## Tipos compartidos (`dominio/tipos.py`)

```text
Modalidad            = Enum(PRIMER_SORTEO, LA_SEGUNDA, REVANCHA, SIEMPRE_SALE, PREMIO_EXTRA)
Numeros              = frozenset[int]          # 6 enteros distintos de 0 a 45
EstadoBloque         = Enum(SIN_CARGAR, BORRADOR, OBSERVADO, PUBLICADO, EN_REVISION)

BloqueNumerosVista   = (estado: EstadoBloque, numeros: Numeros | None)      # numeros solo si está PUBLICADO o EN_REVISION
CategoriaPublicada   = (codigo: str, ganadores: int | None, importe_individual: Decimal | None, ...)
BloquePremiosVista   = (estado: EstadoBloque,
                        categorias: list[CategoriaPublicada] | None,
                        aciertos_categoria_ganadora: int | None,
                        sin_ganadores: bool)

DatosConcurso        = (fecha_sorteo: date,
                        modalidades: set[Modalidad],
                        numeros: dict[Modalidad, BloqueNumerosVista],
                        premios: dict[Modalidad, BloquePremiosVista])
```

## `dominio/numeros.py` — RN-01 a RN-03

| Función | Entrada | Salida | Reglas |
|---------|---------|--------|--------|
| `parsear_numero(texto)` | `str` | `int` o `ErrorNumero(FUERA_DE_RANGO / NO_NUMERICO)` | AC-4.4 |
| `validar_jugada(valores)` | lista de `str` o `int` | `Numeros` o lista de errores (`FALTAN_N`, `SOBRAN`, `REPETIDO(n)`, `FUERA_DE_RANGO`, `NO_NUMERICO`) | RN-01 a RN-03; AC-4.2 a AC-4.5 |
| `validar_extraccion(valores)` | igual | `Numeros` o errores bloqueantes | RN-14; AC-2.3 |
| `formatear(n)` | `int` | `"07"` | RN-01 |
| `misma_combinacion(a, b)` | `Numeros`, `Numeros` | `bool` (sin importar el orden) | RN-06 |

## `dominio/importes.py` — RN-09, NFR-007

| Función | Entrada | Salida |
|---------|---------|--------|
| `parsear_pesos(texto)` | `"1500,50"`, `"1.500,50"`, `"1500"` | `Decimal` o error (`VACIO`, `NEGATIVO`, `NO_NUMERICO`, `DEMASIADOS_DECIMALES`) |
| `formatear_pesos(valor)` | `Decimal` | `"$ 1.500,50"` |
| `formatear_porcentaje(valor)` | `Decimal` | `"12,50 %"` (RN-43) |

## `dominio/consistencia.py` — RN-22

| Función | Salida |
|---------|--------|
| `revisar_numeros(numeros, otras_modalidades_del_concurso, fecha_sorteo, hoy, fuente)` | `(bloqueantes: list, advertencias: list)` |
| `revisar_premios(modalidad, categorias, aciertos_categoria_ganadora, sin_ganadores, fuente)` | `(bloqueantes: list, advertencias: list)` |

Bloqueantes (impiden publicar): cantidad distinta de 6, número repetido, número fuera de rango, cantidad o importe negativo, categoría ganadora de Siempre Sale fuera de 0 a 6, categoría ganadora de Siempre Sale con 0 ganadores, categoría ganadora de Premio Extra que no sea 6, 5, 4 ni "sin ganadores", y falta de fuente.

Advertencias (exigen confirmación expresa): números iguales a los de otra modalidad del concurso, categoría con ganadores sin importe individual, y fecha del sorteo posterior a hoy al publicar números.

## `dominio/comparacion.py` — RN-28 a RN-33, RN-49 a RN-54

### `comparar_jugada(jugada: Numeros, concurso: DatosConcurso) -> list[ResultadoModalidad]`

Devuelve un `ResultadoModalidad` por cada modalidad aplicable del concurso, en este orden: Primer Sorteo, La Segunda, Revancha, Siempre Sale, Premio Extra (AC-5.31).

```text
ResultadoModalidad = (
  modalidad:          Modalidad,
  estado_validacion:  RESULTADO_PENDIENTE | PENDIENTE_VALIDACION | PUBLICADO | EN_REVISION,   # dato 1
  aciertos:           int | None,             # dato 2 (None si no está publicado)
  numeros_acertados:  Numeros | None,         # para resaltarlos
  elegibilidad:       PARTICIPA | EXCLUIDA | None,   # dato 3, solo Premio Extra
  excluida_por:       Modalidad | None,       # RN-53: la extracción con 6 aciertos
  resultado_premio:   CON_PREMIO | SIN_PREMIO | PENDIENTE_DETERMINACION | None,   # dato 4
  categoria:          str | None,             # "Primer Premio", "Siempre Sale (5 aciertos)", ...
  importe:            Decimal | None,         # dato 5: solo el importe individual publicado
  importe_pendiente:  bool,                   # True → "Información de premios pendiente de publicación"
  avisos:             set[AVISO_EN_REVISION | AVISO_ACIERTOS_SUPERAN_CATEGORIA]
)
```

Reglas que debe cumplir:

1. **Estado de validación (RN-29.1)**. Para las modalidades con extracción propia se usa su bloque de números. Para Premio Extra se usan los bloques de Primer Sorteo, La Segunda y Revancha: si alguno está sin cargar, el resultado es `RESULTADO_PENDIENTE`; si no, y alguno está en borrador u observado, es `PENDIENTE_VALIDACION`. Si el estado no es publicado, los datos 2 a 5 son `None` (AC-5.1, AC-5.2, AC-5.29).
2. **Aciertos (RN-28)**: `len(jugada ∩ números de la extracción)`. Nunca se suman entre extracciones (AC-5.18).
3. **Primer Sorteo y La Segunda (RN-49, RN-50)**: 6 → Primer Premio; 5 → Segundo Premio; 4 → Tercer Premio; 3 o menos → sin premio.
4. **Revancha (RN-51)**: 6 → Premio Revancha; cualquier otro valor → sin premio.
5. **Siempre Sale (RN-52)**: los casos (a) a (e), con la precedencia de **P-02, a confirmar**.
6. **Premio Extra (RN-31, RN-53)**: el conjunto es la unión de Primer Sorteo, La Segunda y Revancha (nunca Siempre Sale, AC-5.28). La jugada queda excluida si tiene 6 aciertos en alguna de esas tres extracciones; en ese caso no hay resultado de premio. Si no está excluida, se aplican los casos (a) a (e) con **P-02**.
7. **RN-33**: si `fecha_sorteo < 18/06/2024`, el resultado de premio es `PENDIENTE_DETERMINACION` en todas las modalidades. Los aciertos se informan igual.
8. **Importe (RN-27)**: si el resultado es `CON_PREMIO` y el bloque de premios está publicado con un `importe_individual` no nulo para la categoría alcanzada, se devuelve ese importe. Si no, `importe = None` e `importe_pendiente = True`. Esto cubre los dos casos, bloque de premios sin publicar e importe individual no informado, que se muestran con el mismo texto (RN-27, Clarifications 13/11/2026), así que no hace falta distinguirlos. **Nunca** se divide un pozo ni se estima un valor.
9. **Avisos**: `AVISO_EN_REVISION` si algún bloque usado está en revisión (AC-5.12). `AVISO_ACIERTOS_SUPERAN_CATEGORIA` en el caso (e) de RN-52 y RN-31.

### `resumir_jugada(resultados: list[ResultadoModalidad]) -> EstadoResumido`

Devuelve el estado resumido para el historial (AC-5.13), según la precedencia de **P-04, a confirmar**.

### `cambio_por_correccion(jugada, historial_de_versiones) -> dict[Modalidad, date | None]`

Para cada modalidad, devuelve la fecha de la última corrección publicada que cambió alguno de los datos de RN-29, o `None` si ninguna lo cambió (AC-5.9). Sigue la interpretación de **P-03, a confirmar**.

### Casos de prueba obligatorios

- Los tres **ejemplos de referencia** de la spec, con cada variante de categoría ganadora de Siempre Sale indicada en ellos (AC-5.33).
- AC-5.14 a AC-5.32, uno o más casos por criterio (SC-005).
- Estados de validación: cada combinación de bloque sin cargar, en borrador, observado, publicado y en revisión, incluido el caso de Premio Extra con una sola extracción sin publicar.
- RN-33: un concurso del 17/06/2024 y otro del 18/06/2024.

## `dominio/estadisticas.py` — RN-40 a RN-47

### `calcular_frecuencias(sorteos, concursos_sin_informacion, desde, hasta) -> Frecuencias | SinSorteos`

- `sorteos`: lista de `(fecha_sorteo, Numeros)` publicados de **una** modalidad aplicable dentro del período (RN-41).
- Devuelve: `cantidad_sorteos`, `primera_fecha`, `ultima_fecha`, `concursos_sin_informacion` (RN-45) y, para **cada** número de 0 a 45 (incluidos los que tienen 0 apariciones, AC-6.5), su `frecuencia` y su `porcentaje` (`Decimal` redondeado a dos decimales, RN-43).
- Si `cantidad_sorteos == 0`, devuelve `SinSorteos` (AC-6.4).
- Rechaza `desde > hasta` con un error de período (AC-6.8).
- No produce ninguna clasificación, predicción ni recomendación (RN-47).
