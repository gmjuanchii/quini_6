# Contrato del archivo CSV — versión 3.0

**Plan**: [../plan.md](../plan.md) | **Decisión**: [../research.md](../research.md) R-09 | **Reglas**: RN-34 a RN-39, RN-43, NFR-008 a NFR-010

Este documento fija los encabezados definitivos que RN-34 deja al plan. Es el **contrato de datos** de la futura ingesta (fuera del alcance de esta feature). Toda versión futura conserva el significado de las columnas existentes y solo agrega columnas al final (NFR-009).

**Versión 3.0 (20/11/2026, spec Clarifications 2026-11-20, ajustes de pantalla)**: cambio mayor aprobado por el responsable antes de que exista la ingesta. Se quitan las columnas `se_acumula_segun_fuente` e `importe_trasladado` (antes 21 y 22), que ninguna fuente publica (D-22); las columnas siguientes se corren dos lugares y conservan su significado. Los archivos de extracciones anteriores conservan su versión (RN-44).

**Versión 2.0 (20/11/2026, spec Clarifications 2026-11-20)**: cambio mayor aprobado por el responsable antes de que exista la ingesta. Cambian los valores de `modalidad` (D-15), `pozo_destinado` e `importe_individual` (D-16) y se agrega al final la columna 27 `numeros_pozo_extra` (D-19). Los archivos de extracciones anteriores conservan su versión 1.0 (RN-44).

## Formato

| Aspecto | Valor |
|---------|-------|
| Codificación | UTF-8, sin marca BOM |
| Separador de columnas | Coma (`,`) |
| Comillas | Dobles, solo cuando el valor contiene coma, comillas o salto de línea (las comillas internas se duplican) |
| Fin de línea | `\r\n` |
| Primera fila | Encabezados, exactamente los de la tabla de columnas y en ese orden |
| Fechas | `AAAA-MM-DD` |
| Fechas y horas de consulta | `AAAA-MM-DD HH:MM:SS` en `America/Argentina/Buenos_Aires` |
| Importes | Pesos con punto decimal, dos decimales y sin separador de miles: `1100000000.00` |
| Números del Quini 6 | Dos dígitos, de `00` a `45` |
| Sí o no | `Sí` / `No` |
| Estados de RN-20 | `No disponible`, `No corresponde`, `Sin determinar`, escritos así en la celda del dato |
| Celdas vacías | Solo en las columnas de listas de texto (`sorteo_motivos`, `datos_sin_corroborar`, `discrepancias`, `observaciones`) y significan "ninguno". **Nunca** en una columna de valor (RN-36) |
| Protección contra fórmulas | Una celda que empieza con `=`, `+`, `-`, `@`, tabulación o retorno de carro lleva un apóstrofo (`'`) adelante (NFR-010, AC-5.9) |
| Nombre del archivo | `quini6-extraccion-{id}-{AAAA-MM-DD}-a-{AAAA-MM-DD}.csv` con las fechas del período consultado |

## Filas

- **Una fila por sorteo, modalidad y categoría**, solo con los datos consolidados (RN-43). Ningún par repetido de (`sorteo_numero`, `modalidad`, `categoria`) (RN-37, AC-5.5). No hay filas por fuente.
- **Orden**: por `sorteo_numero` ascendente; dentro del sorteo, modalidades en el orden Tradicional, La Segunda, Revancha, Siempre Sale, Pozo Extra ([001] AC-5.31); dentro de la modalidad, Primer, Segundo y Tercer Premio, o la única categoría, y al final las "Categoría de N aciertos" por aciertos descendentes.
- **Sorteo recuperado, parcial o con inconsistencias**: una fila por cada categoría esperada de las cinco modalidades (nueve filas), más las "Categoría de N aciertos" que informen las fuentes antes del 18/06/2024. Datos faltantes como `No disponible` y datos en conflicto como `Sin determinar` (RN-39).
- **Modalidad no informada por ninguna fuente**: una sola fila de esa modalidad, con `categoria` = `No disponible`, todos los valores `No disponible` y la observación "No informada por las fuentes" (RN-39, AC-3.12).
- **Sorteo "No recuperado"**: una sola fila con su número, su fecha si se conoce (si no, `No disponible`), su estado y sus motivos. `modalidad` y `categoria` = `No disponible` y todas las demás columnas de valor `No disponible`: sin números ni importes (RN-39, AC-5.8).
- Los datos del sorteo (`sorteo_*`) se repiten en cada fila del sorteo. Los seis números se repiten en cada fila de su modalidad (RN-43).

## Columnas

| # | Encabezado | Valores posibles | Regla |
|---|------------|------------------|-------|
| 1 | `version_contrato` | `3.0` | NFR-009 |
| 2 | `sorteo_numero` | Entero positivo | RN-21 |
| 3 | `sorteo_fecha` | `AAAA-MM-DD` · `No disponible` · `Sin determinar` | RN-22, RN-38 |
| 4 | `sorteo_estado` | `Recuperado` · `Recuperado parcialmente` · `Con inconsistencias` · `No recuperado` | RN-31, AC-5.3 |
| 5 | `sorteo_combina_fuentes` | `Sí` · `No` | RN-29 |
| 6 | `sorteo_sin_corroborar` | `Sí` · `No` | RN-32 |
| 7 | `sorteo_motivos` | Lista de texto separada por ` \| ` | RN-31, RN-39 |
| 8 | `modalidad` | `Tradicional` · `La Segunda` · `Revancha` · `Siempre Sale` · `Pozo Extra` · `No disponible` | RN-11, D-15 |
| 9–14 | `numero_1` … `numero_6` | `00`–`45` en orden ascendente · `No corresponde` (Pozo Extra) · `No disponible` · `Sin determinar` | RN-12, RN-13, RN-24 |
| 15 | `categoria` | `Primer Premio` · `Segundo Premio` · `Tercer Premio` · `Premio Revancha` · `Categoría ganadora` · `Categoría de N aciertos` · `No disponible` | RN-14, RN-25 |
| 16 | `aciertos` | `0`–`6` · `Sin ganadores` (solo Premio Extra) · `No disponible` · `Sin determinar` | RN-14, RN-26 |
| 17 | `ganadores` | Entero ≥ 0 · `No disponible` · `Sin determinar` | RN-15 |
| 18 | `estado_pozo` | `Con ganadores` · `Vacante` · `Pendiente` · `Sin determinar` | RN-19, I-06 |
| 19 | `pozo_destinado` | Importe · `No disponible` · `Sin determinar` | RN-17, RN-18. Con ganadores y sin pozo publicado: importe individual × ganadores, con el tramo `pozo_destinado: Calculado: importe individual × ganadores` en `procedencia` (AC-3.6, D-16) |
| 20 | `importe_individual` | Importe (`0.00` si la categoría está vacante) · `No disponible` · `Sin determinar` | RN-17, RN-18, RN-20, D-16 |
| 21 | `datos_sin_corroborar` | Lista de nombres de columna separada por `; ` | RN-32, RN-35 |
| 22 | `procedencia` | Texto con la gramática de abajo | RN-35, NFR-008, AC-5.4 |
| 23 | `discrepancias` | Texto con la gramática de abajo | RN-27, RN-43, AC-4.1 |
| 24 | `observaciones` | Lista de texto separada por ` \| ` | FR-009 |
| 25 | `numeros_pozo_extra` | Filas de Pozo Extra: números `00`–`45` en orden ascendente, separados por un espacio (unión de Tradicional, La Segunda y Revancha) · `No disponible`. Demás filas: `No corresponde` | RN-12, D-19, AC-3.17 |

No hay columna de precio del cartón (RN-35, AC-5.6).

## Gramática de las columnas de texto

Nombres de dato válidos (`<dato>`): `sorteo_fecha`, `numeros`, `aciertos`, `ganadores`, `pozo_destinado`, `importe_individual`. Nombre de fuente (`<fuente>`): el dominio del sitio, por ejemplo `numerosganadores.com.ar`.

**`procedencia`**: un tramo por cada dato de la fila que tiene valor, separados por ` | `. Cada tramo indica las fuentes que lo respaldan, separadas por `; `:

```text
<dato>: <fuente> <dirección> <AAAA-MM-DD HH:MM:SS>; <fuente> <dirección> <AAAA-MM-DD HH:MM:SS>
```

Ejemplo: `ganadores: numerosganadores.com.ar https://numerosganadores.com.ar/sorteos/3426 2026-11-19 10:15:02; quiniya.com.ar https://quiniya.com.ar/sorteos/3426 2026-11-19 10:15:02 | importe_individual: …`

Un dato calculado por el sistema (desde la versión 2.0) lleva el tramo `<dato>: Calculado: <cálculo>` en lugar de fuentes: `pozo_destinado: Calculado: importe individual × ganadores`, `importe_individual: Calculado: sin ganadores` y `numeros_pozo_extra: Calculado: unión de Tradicional, La Segunda y Revancha`. Las fuentes se listan en el orden de prioridad de RN-07.

**`discrepancias`**: un tramo por cada dato en conflicto, separados por ` | `:

```text
<dato>: <tipo> — <valor> (<fuente>); <valor> (<fuente>)
```

`<tipo>` ∈ {`Valor distinto`, `Omisión`}. Los valores van en el formato técnico de este contrato; una omisión se escribe `sin dato`. Ejemplo (AC-4.1): `importe_individual: Valor distinto — 5015.00 (numerosganadores.com.ar); 5547.85 (quiniya.com.ar)`. Desde la versión 2.0, un dato con discrepancia que no es un importe muestra en su columna el valor de la fuente de mayor prioridad (RN-07); un importe con discrepancia queda `Sin determinar` (RN-30).

**`observaciones`** y **`sorteo_motivos`**: los textos de [mensajes.md](mensajes.md), precedidos por la fuente cuando corresponde (`<fuente>: <texto>`), separados por ` | `. Una diferencia de importes menor al 1 % (RN-30) se escribe en `observaciones` con la gramática de `discrepancias`: `<dato>: Diferencia de centavos o redondeo (menor al 1 %) — 657151589.00 (numerosganadores.com.ar); 657151588.80 (quiniya.com.ar)`.

## Ejemplo (encabezados y dos filas, recortado)

```text
version_contrato,sorteo_numero,sorteo_fecha,sorteo_estado,sorteo_combina_fuentes,sorteo_sin_corroborar,sorteo_motivos,modalidad,numero_1,numero_2,numero_3,numero_4,numero_5,numero_6,categoria,aciertos,ganadores,estado_pozo,pozo_destinado,importe_individual,datos_sin_corroborar,procedencia,discrepancias,observaciones,numeros_pozo_extra
3.0,3427,2026-11-18,Recuperado,No,No,,Tradicional,…,Primer Premio,6,0,Vacante,1100000000.00,0.00,,…,,,No corresponde
3.0,3423,No disponible,No recuperado,No,No,Ninguna fuente informa este número de sorteo,No disponible,No disponible,…,No disponible,No disponible,No disponible,…,,,,,No disponible
```

## Garantías para la futura ingesta

- Los datos no tienen ningún estado de validación de [001] RN-16: una ingesta debe cargarlos como Borrador (RN-40).
- Los únicos valores calculados por la aplicación son el pozo destinado de una categoría con ganadores, el importe individual `0.00` de una vacante y `numeros_pozo_extra`; todos llevan el tramo `Calculado` en `procedencia` (RN-12, RN-18, SC-002).
- Un valor desconocido nunca figura como `0` ni como `Vacante` (RN-20).
- Brechas con el modelo vigente, a resolver en la futura ingesta: "No corresponde" frente a "No disponible", estado del pozo y procedencia por dato (spec, "Correspondencia con el modelo vigente").
