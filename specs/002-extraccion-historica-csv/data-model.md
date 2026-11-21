# Modelo de datos (Fase 1): Extracción histórica de sorteos y exportación CSV

**Fecha**: 19/11/2026, actualizado el 21/11/2026 (D-14 a D-24) | **Plan**: [plan.md](plan.md) | **Decisiones**: [research.md](research.md) (R-07, R-08, R-16, R-17)

Convenciones heredadas de [001] [data-model.md](../001-quini6-mvp/data-model.md): importes en `Decimal` con dos decimales como máximo, fechas y horas guardadas en UTC y mostradas en `America/Argentina/Buenos_Aires`, números del Quini 6 como enteros de 0 a 45 en orden ascendente.

Diferencia importante con [001]: en la extracción, `null` **no alcanza** para representar la ausencia de un dato, porque RN-20 distingue cuatro situaciones. Por eso, los datos de la extracción usan el tipo `Dato` del dominio (ver más abajo), que se guarda en JSON con su estado explícito.

**Esta feature no crea ni modifica ninguna tabla de `resultados`, `jugadas` ni `cuentas`** (RN-41). Solo lee `cuentas.Usuario` para saber quién ejecutó cada extracción.

---

## Catálogos fijos (enumeraciones en código, no tablas)

### `EstadoExtraccion` (entidad Extracción de la spec)

| Código | Texto visible | Cuándo |
|--------|---------------|--------|
| `EN_CURSO` | Extracción en curso | Desde que se inicia hasta que el trabajador la termina. |
| `FINALIZADA` | Extracción finalizada | Todos los sorteos identificados quedaron "Recuperado" (RN-33). |
| `CON_ADVERTENCIAS` | Extracción finalizada con advertencias que requieren revisión | Al menos un sorteo quedó en otro estado (RN-33). |
| `SIN_SORTEOS` | No se identificaron sorteos en el período consultado | Ningún sorteo con fecha en el período (AC-1.10). |

Transiciones: `EN_CURSO` → `FINALIZADA` | `CON_ADVERTENCIAS` | `SIN_SORTEOS`. Los tres estados finales son definitivos (RN-44).

### `ResultadoIntento` (RN-08)

`OBTENIDO` "Obtenido" · `INCOMPLETO` "Incompleto" · `NO_ENCONTRADO` "No encontrado" · `NO_DISPONIBLE` "No disponible" · `NO_DISPONIBLE_O_NO_ENCONTRADO` "No disponible o no encontrado" · `ESTRUCTURA_NO_RECONOCIDA` "Estructura no reconocida" · `FUERA_DE_COBERTURA` "Fuera de cobertura" · `NO_REQUERIDA` "No requerida" (20/11/2026: F1 no hizo falta, RN-09, AC-2.11, D-14).

Son **intentos fallidos** (AC-2.1) todos menos `OBTENIDO`, `FUERA_DE_COBERTURA` y `NO_REQUERIDA`. Estos dos últimos tampoco cuentan para un hueco (I-10). `INCOMPLETO` se informa como un tipo de falla aparte, porque la fuente igual pudo aportar datos.

### `EstadoSorteo` (RN-31, en orden de precedencia)

`NO_RECUPERADO` "No recuperado" → `CON_INCONSISTENCIAS` "Con inconsistencias" → `PARCIAL` "Recuperado parcialmente" → `RECUPERADO` "Recuperado".

### `Fuente` (RN-06)

`F1`, `F2` y `F3`. No es un modelo: es una ficha inmutable en el código ([contracts/fuentes.md](contracts/fuentes.md), [002] R-05).

### Categorías por modalidad (RN-14, RN-25)

| Modalidad | Clave de categoría | Nombre en pantalla y en el archivo | Aciertos |
|-----------|--------------------|------------------------------------|----------|
| Tradicional – Primer Sorteo, Tradicional – La Segunda | `PRIMER`, `SEGUNDO`, `TERCER` | Primer Premio, Segundo Premio, Tercer Premio | 6, 5, 4 |
| Revancha | `UNICO` | Premio Revancha | 6 |
| Siempre Sale | `GANADORA` | Categoría ganadora | 0 a 6, según la fuente |
| Premio Extra | `GANADORA` | Categoría ganadora | 6, 5, 4 o "Sin ganadores" |
| Cualquiera, solo antes del 18/06/2024 | `ACIERTOS_N` | Categoría de N aciertos | N, según la fuente (Clarifications 19/11/2026, planificación) |

Son **categorías esperadas** de un sorteo las de las cinco modalidades del catálogo vigente (D-04: sin catálogo de vigencias). `ACIERTOS_N` nunca es esperada: aparece solo si una fuente la informa.

---

## Tipos del dominio (valores, sin base de datos)

Los define `dominio/extraccion/tipos.py` ([contracts/dominio.md](contracts/dominio.md)). Se describen aquí porque son lo que se guarda en los campos JSON.

### `Dato` — las cuatro situaciones de RN-20

| Variante | Significado | Ejemplo en el archivo |
|----------|-------------|-----------------------|
| `Valor(v)` | Un valor, incluido el cero cuando la fuente lo informa. `v` es `int`, `Decimal`, `date`, `bool` o un conjunto de números. | `1100000000.00`, `0`, `Sí` |
| `NO_DISPONIBLE` | Ninguna fuente lo informa, o se descartó por inválido. | `No disponible` |
| `NO_CORRESPONDE` | El concepto no aplica (importe individual de una categoría vacante, números de Premio Extra). | `No corresponde` |
| `SIN_DETERMINAR` | Las fuentes difieren. | `Sin determinar` |

Regla de construcción: un `Dato` nunca se crea a partir de un valor ausente convertido en cero (RN-20, SC-002).

### `DatosFuente` — lo que informó una fuente para un sorteo, ya normalizado

| Campo | Tipo | Regla |
|-------|------|-------|
| `fuente` | `Fuente` | |
| `numero` | `int` | RN-21. |
| `fecha` | `date` | RN-22. |
| `modalidades` | `dict[Modalidad, DatosModalidadFuente]` | Solo las que la fuente presenta con un rótulo de su ficha (RN-11). |
| `observaciones` | `list[Observacion]` | Rótulos desconocidos, importes inválidos, números inválidos, etc. |

`DatosModalidadFuente`: `numeros: Numeros | None` (None si la fuente no los publica o se descartaron por RN-24) y `categorias: dict[ClaveCategoria, DatosCategoriaFuente]`.

`DatosCategoriaFuente`: `aciertos`, `ganadores`, `pozo_destinado` e `importe_individual` (desde D-22, sin `se_acumula`), cada uno como `Dato` según lo que la ficha dice que significa la columna (RN-15 a RN-19), más `texto_original` del importe cuando no se pudo interpretar (RN-16).

### `DatoConsolidado` — resultado de comparar las fuentes para un dato (RN-27)

| Campo | Tipo | Regla |
|-------|------|-------|
| `dato` | `Dato` | `SIN_DETERMINAR` si hay discrepancia. |
| `fuentes` | `tuple[Fuente, ...]` | Las que respaldan el valor (coincidentes). Vacía si `NO_DISPONIBLE`. |
| `sin_corroborar` | `bool` | `True` si el valor lo informa una sola fuente (RN-32). |
| `discrepancia` | `Discrepancia | None` | RN-27, RN-28, RN-30: la diferencia que deja el sorteo "Con inconsistencias". |
| `diferencia_tolerada` | `Discrepancia | None` | 20/11/2026: diferencia solo informativa, de tipo `CENTAVOS` si los importes difieren menos del 1 % (RN-30, D-17) o `MAYORIA` si 2 de 3 fuentes coinciden (RN-07, D-21). No cambia el estado. |
| `calculo` | `str | None` | 20/11/2026: texto del cálculo si el valor lo calculó el sistema (RN-12, RN-18, D-16, D-19); un dato calculado no tiene fuentes y nunca se presenta como publicado. |

`Discrepancia`: `tipo` (`VALOR_DISTINTO` "Valor distinto", `OMISION` "Omisión", `CENTAVOS` "Diferencia de centavos o redondeo (menor al 1 %)", que desde D-17 solo aparece como `diferencia_tolerada`, y `MAYORIA` "Resuelto por coincidencia de 2 de 3 fuentes", D-21) y `valores: tuple[(Fuente, texto del valor), ...]`.

### `Observacion`

`codigo`, `texto` (de [contracts/mensajes.md](contracts/mensajes.md)), `fuente` (o `None` si es del consolidado), `es_inconsistencia: bool` (RN-23 y las que RN-31 cuenta como inconsistencia) e `informativa: bool` (no afecta el estado, como el aviso "Reglas del período no verificadas").

### `SorteoConsolidado` — un sorteo procesado (RN-29, RN-31, RN-32)

| Campo | Tipo |
|-------|------|
| `numero` | `int` |
| `fecha` | `DatoConsolidado` |
| `modalidades` | `dict[Modalidad, ModalidadConsolidada]`, con las cinco del catálogo |
| `estado` | `EstadoSorteo` |
| `combina_fuentes` | `bool` (I-03) |
| `sin_corroborar` | `bool` (algún dato con `sin_corroborar`) |
| `motivos` | `list[str]`: por qué no está "Recuperado" (datos faltantes, discrepancias, motivo de cada fuente si no se recuperó) |
| `observaciones` | `list[Observacion]` |
| `reglas_no_verificadas` | `bool`: fecha anterior al 18/06/2024 (RN-25, AC-3.11) |

`ModalidadConsolidada`: `informada: bool` (False → "No informada por las fuentes", AC-3.12), `numeros: DatoConsolidado` (`NO_CORRESPONDE` en Premio Extra) y `categorias: dict[ClaveCategoria, CategoriaConsolidada]`.

`CategoriaConsolidada`: `aciertos`, `ganadores`, `pozo_destinado`, `importe_individual` (cada uno `DatoConsolidado`) y `estado_pozo` (derivado: "Con ganadores", "Vacante", "Pendiente" o "Sin determinar", RN-19 e I-06). Desde D-22 (20/11/2026) no tiene `se_acumula` ni `importe_trasladado`; al leer sorteos guardados antes, esas claves del JSON se ignoran.

---

## Entidades persistidas (aplicación `extracciones`)

### `extracciones.Extraccion` — entidad Extracción

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | Aparece en la dirección y en el nombre del archivo. |
| `creada_por` | FK → `cuentas.Usuario` (PROTECT) | Administrador que la inició (RN-44). |
| `desde`, `hasta` | `DateField` | Período inclusivo, validado con RN-01 a RN-04 antes de crear. |
| `estado` | `EstadoExtraccion`, indexado | |
| `iniciada_en` | `DateTimeField`, indexado | Orden del listado, de la más reciente a la más antigua (AC-1.14). |
| `finalizada_en` | `DateTimeField`, `null` | Obligatorio si el estado es final. |
| `numero_desde`, `numero_hasta` | `PositiveIntegerField`, `null` | Resultado de la identificación (RN-05). `null` mientras se identifica: la pantalla muestra "Identificando los sorteos del período…". |
| `cobertura_desde` | `DateField`, `null` | Fecha del aviso "Las fuentes no cubren el período anterior al dd/mm/aaaa" (AC-1.17). |
| `resumen` | `JSONField`, `null` | Resumen de RN-33, calculado al terminar ([contracts/dominio.md](contracts/dominio.md) → `resumir`). |
| `archivo_csv` | `TextField`, vacío | Contenido exacto del archivo, generado una sola vez al terminar (RN-44, AC-5.10). Vacío si el estado es `SIN_SORTEOS`. |
| `nombre_archivo` | `CharField` | `quini6-extraccion-{id}-{desde}-a-{hasta}.csv` ([002] R-09). |
| `version_contrato` | `CharField` | `1.0` ([contracts/csv.md](contracts/csv.md)). |

Derivados (no se guardan): `total_identificados = numero_hasta − numero_desde + 1`; `procesados = cantidad de SorteoExtraido`; `identificando = numero_desde is None`.

Restricciones:

- `UniqueConstraint(creada_por, condition=estado = EN_CURSO)`: un administrador tiene como máximo una extracción en curso (Supuestos, AC-1.11).
- `CheckConstraint(desde <= hasta)`.
- `CheckConstraint`: `finalizada_en` es nulo si y solo si `estado = EN_CURSO`.
- `CheckConstraint`: `numero_desde <= numero_hasta` cuando ambos existen.

Las restricciones únicas parciales y los `CheckConstraint` funcionan en SQLite y en PostgreSQL ([001] R-03).

### `extracciones.SorteoExtraido` — un sorteo identificado y su resultado

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `extraccion` | FK → `Extraccion` (CASCADE) | Desde D-24 (20/11/2026), eliminar una extracción terminada borra sus sorteos e intentos en cascada. |
| `numero` | `PositiveIntegerField` | Único junto con `extraccion` (RN-37). |
| `fecha` | `DateField`, `null` | Fecha consolidada si está determinada; `null` si no se conoce o está en conflicto (el detalle lo muestra desde `consolidado`). |
| `estado` | `EstadoSorteo`, indexado | RN-31. |
| `combina_fuentes` | `bool` | RN-29, I-03. |
| `sin_corroborar` | `bool` | RN-32. |
| `consolidado` | `JSONField` | `SorteoConsolidado` serializado: modalidades, categorías, `DatoConsolidado` con fuentes, discrepancias, observaciones y motivos. |
| `procesado_en` | `DateTimeField` | |

Se crea con todos sus `IntentoConsulta` en **una sola transacción**, después de consultar las fuentes que correspondan (F1 solo si hace falta, D-14). Así, el avance cuenta solo sorteos completos y un reinicio a medio sorteo no deja datos parciales (I-07).

### `extracciones.IntentoConsulta` — entidad Intento de consulta

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `sorteo` | FK → `SorteoExtraido` (CASCADE) | |
| `fuente` | `Fuente` | Único junto con `sorteo`. Existe uno por cada fuente configurada, también si quedó "Fuera de cobertura" (AC-4.8). |
| `resultado` | `ResultadoIntento` | RN-08. |
| `url` | `CharField(500)`, vacío | Dirección consultada (FR-006). Vacía si es "Fuera de cobertura". |
| `consultado_en` | `DateTimeField`, `null` | Fecha y hora de la consulta (FR-006). `null` si no se consultó. |
| `datos` | `JSONField`, `null` | `DatosFuente` serializado. `null` si la fuente no aportó datos. |
| `observaciones` | `JSONField` | Lista de `Observacion` de la fuente, incluido qué falta si es "Incompleto" (AC-2.5). |

No se guarda el HTML recibido: el detalle conserva los valores normalizados y, cuando un texto no se pudo interpretar, su texto original en la observación (RN-16).

---

## Resumen guardado (`Extraccion.resumen`, RN-33)

| Clave | Contenido |
|-------|-----------|
| `identificados` | Cantidad de números identificados. |
| `por_estado` | Cantidad de sorteos en cada `EstadoSorteo`. Los cuatro suman `identificados`. |
| `fuentes` | Por cada fuente configurada: sorteos que aportó (I-05), intentos por resultado y la marca `requiere_mantenimiento` (RN-10: cubre al menos un sorteo y quedó "Estructura no reconocida" en todos los que cubre). |
| `huecos` | Números que ninguna fuente informa (AC-1.16). |
| `cobertura_desde` | Fecha del aviso de AC-1.17, si corresponde. |
| `a_revisar` | Lista de sorteos que no quedaron "Recuperado", con número, fecha si se conoce, estado y motivos (AC-1.9). |

---

## Correspondencia con el modelo de [001]

La tabla "Correspondencia con el modelo vigente" de la spec sigue vigente. Este modelo **no** la resuelve: las brechas (estado del pozo, "No corresponde" frente a "No disponible", acumulación, procedencia por dato) quedan expresadas en el contrato del CSV para que la futura ingesta las trate (RN-40).

---

## Flujo de estados de una extracción

```text
[Formulario válido] ──crear──▶ EN_CURSO (identificando: numero_desde = null)
                                   │ trabajador: listados + identificación (RN-05)
                                   ├── ningún sorteo en el período ──▶ SIN_SORTEOS
                                   ▼
                              EN_CURSO (procesando: N de M)
                                   │ por cada número: F1 ∥ F2 ∥ F3 → normalizar → validar
                                   │ → consolidar → clasificar → guardar sorteo + intentos
                                   ▼
                              resumen + CSV generados una vez
                                   ├── todos "Recuperado" ──▶ FINALIZADA
                                   └── alguno en otro estado ──▶ CON_ADVERTENCIAS
```
