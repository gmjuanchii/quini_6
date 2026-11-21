# Fichas de las fuentes (RN-06)

**Plan**: [../plan.md](../plan.md) | **Relevamiento**: [../analisis-fuentes.md](../analisis-fuentes.md) (18/11/2026) | **Decisión**: [../research.md](../research.md) R-05

Las fichas son configuración aprobada en el código (`extracciones/fuentes/fichas.py`). No se editan desde la interfaz. Cambiar una ficha, por ejemplo porque una fuente cambió su estructura, requiere una actualización aprobada de la spec (RN-10, D-07). Las direcciones base se pueden reemplazar solo para el servidor de fuentes de prueba ([002] R-11).

Marca **(relevar)**: dato que se confirma al implementar contra la página real y se completa en esta ficha. Si contradice [analisis-fuentes.md](../analisis-fuentes.md), se consulta al responsable antes de seguir.

**Relevamiento del 19/11/2026 (T006)**: se volvieron a leer las reglas para robots de los tres sitios (siguen con el mismo preámbulo de "señales de contenido", sin instrucciones ni restricciones nuevas) y se consultaron a mano, con una consulta cada 2 s por sitio como máximo, los listados, los sorteos 3426 y 3427, sorteos antiguos (2211, 2787, 3150, 3398) e inexistentes (9999). Todo coincide con [analisis-fuentes.md](../analisis-fuentes.md) salvo dos puntos, consultados al responsable el 19/11/2026: el bloque embebido de F3 (ver F3) y el enlace de F0 (ver F0). Las copias recortadas están en `tests/fixtures/fuentes/`.

## Prioridad (RN-07, RN-09; Clarifications 20/11/2026)

| Prioridad | Fuente | Uso |
|-----------|--------|-----|
| 1.ª | F2 — numerosganadores.com.ar | Se consulta siempre que cubre el sorteo. Ante una diferencia prevalece su valor, salvo en importes con una diferencia del 1 % o más (RN-30) |
| 2.ª | F3 — quiniya.com.ar | Se consulta siempre que cubre el sorteo |
| 3.ª | F1 — quini-6-resultados.com.ar | Respaldo y desempate: solo si, con F2 y F3, el sorteo queda "No recuperado", le falta un dato esperado, difieren en un dato o una publica un dato inválido (D-21). Si no, su intento es "No requerida". Si dos de tres fuentes coinciden, ese valor resuelve la diferencia. Su listado se sigue leyendo para identificar los sorteos |

Los identificadores F1, F2 y F3 se conservan del relevamiento y no indican la prioridad.

## Comunes a las tres fuentes

| Aspecto | Valor |
|---------|-------|
| Tipo | Secundaria |
| Verificación anti-robots | No se observó ninguna. Los tres sitios están detrás de Cloudflare: se reconocen como anti-robots las páginas 200 con los marcadores de su verificación (`<title>Just a moment...</title>`, `cf_chl_opt`, `cf-chl-`, `Attention Required! \| Cloudflare`). El texto `challenge-platform` **no** es marcador: aparece en las páginas normales de F1 |
| Ritmo | Como máximo una consulta cada 2 s por sitio (NFR-005) |
| Límite de espera | 10 s ([002] R-02) |
| Columna de importe | Una sola columna con dos significados (RN-17): **pozo destinado** si la categoría está vacante; **importe individual** si tiene ganadores |
| Pozo destinado de una categoría con ganadores | **No lo publica por diseño** (no es omisión, RN-28; no es dato esperado, RN-31) |
| Categoría "Estímulo" | No la publica |
| Cantidad de ganadores | "Vacante" / "Pozo vacante" = 0; vacío, "-" o ausente = `No disponible` (RN-15) |
| Importes | Formato argentino, con o sin "$", con o sin centavos (RN-16) |

## F1 — quini-6-resultados.com.ar

| Aspecto | Valor |
|---------|-------|
| Nombre en el archivo | `quini-6-resultados.com.ar` |
| Dirección base | `https://www.quini-6-resultados.com.ar` (sin `www.` el sitio redirige con 301 a otro nombre de sitio, que el cliente no sigue) |
| Listado | `/quini6/sorteos-anteriores.aspx`: últimos 3 meses, con número y fecha (relevado: 3405 del 02/09/2026 a 3427 del 18/11/2026) |
| Sorteo | `/quini6/sorteo-{N}-del-dia-{dd-mm-aaaa}.htm`: exige número y fecha exactos. La fecha se toma del propio listado de F1 o, si el sorteo no figura, de la que informan F2 y F3 (D-21) |
| Cobertura | Un sorteo está cubierto si figura en el listado o si F2 y F3 informan su fecha (I-08, D-21). Si no, "Fuera de cobertura". Verificado el 20/11/2026 con los sorteos 3235 (15-01-2025) y 3308 (28-09-2025) |
| Sorteo inexistente | 404 → "No encontrado". También responde 404 si la fecha de la dirección no coincide con el sorteo |
| Verificación (RN-21) | El número y la fecha de la página deben coincidir con los de la dirección; si no, "Estructura no reconocida" |
| Orden de los números | Ascendente |
| Columnas de premios | Aciertos · Ganadores · Premio |
| Premio Extra | Sin números propios. Aciertos "-": **no publica** los aciertos de la categoría ganadora. Pozo como texto "N millones de pesos" → N × 1.000.000,00 exactos (RN-17, Clarifications 19/11/2026, planificación); cualquier otro texto → RN-16 |
| Datos que publica | Número, fecha, seis números de Primer Sorteo, La Segunda, Revancha y Siempre Sale, ganadores e importe por categoría, aciertos de la categoría ganadora de Siempre Sale, pozo de Premio Extra |
| Codificación | `Content-Type: text/html` sin juego de caracteres; la página declara `charset=utf-8` en `<meta http-equiv>` |
| Selectores HTML (relevado) | **Listado**: cada `<a href=".../quini6/sorteo-{N}-del-dia-{dd-mm-aaaa}.htm">` con el texto "Sorteo {N} del {dd-mm-aaaa}". **Sorteo**: número y fecha en el `<h2>` "Sorteo Nro. {N} del dia {día} {dd-mm-aaaa}". Números: cada `<h3 class="verdeyblanco">` (rótulo) seguido de `<p class="numeros">` ("01 - 02 - 10 - 13 - 38 - 39"); el rótulo de Premio Extra trae el pozo entre paréntesis: "POZO EXTRA (55 millones de pesos)" y no tiene `<p class="numeros">`. Premios: una sola `<table class="table">` donde cada `<tr class="verde">` con `<span class="lblSorteo">` abre un bloque y las filas siguientes tienen tres `<td>` (aciertos, ganadores, premio "$ 1.100.000.000") |
| Sorteo inexistente (relevado) | 404 también con una fecha equivocada en la dirección (3426 con 16-11-2026) |

Rótulos de modalidad (equivalencia exacta, RN-11):

| Rótulo publicado | Modalidad |
|------------------|-----------|
| SORTEO TRADICIONAL | Tradicional – Primer Sorteo |
| LA SEGUNDA DEL QUINI · LA SEGUNDA DEL QUINI 6 | Tradicional – La Segunda |
| SORTEO REVANCHA · LA SEGUNDA DEL QUINI 6 REVANCHA | Revancha |
| QUINI QUE SIEMPRE SALE · EL QUINI QUE SIEMPRE SALE | Siempre Sale |
| POZO EXTRA · QUINI 6 POZO EXTRA | Premio Extra |

La comparación es exacta sobre el rótulo completo, sin distinguir mayúsculas y con espacios normalizados. "LA SEGUNDA DEL QUINI 6 REVANCHA" es Revancha y nunca La Segunda (AC-3.1).

## F2 — numerosganadores.com.ar

| Aspecto | Valor |
|---------|-------|
| Nombre en el archivo | `numerosganadores.com.ar` |
| Listado | `/sorteos`: últimos 20 sorteos, con número y fecha. `/ultimoSorteo` es una página del mismo sitio, no una fuente aparte |
| Sorteo | `/sorteos/{N}` |
| Cobertura | Desde el sorteo 2211 (17/12/2014). Antes: "Fuera de cobertura" |
| Sorteo inexistente | 500 → "No disponible o no encontrado" (no distingue ambos casos) |
| Orden de los números | Orden de extracción; en sorteos antiguos, ascendente. Se comparan como conjunto (RN-13) |
| Columnas de premios | Cantidad de aciertos · Cantidad de ganadores · Premio para cada uno |
| Premio Extra | Lista de números de las tres extracciones (a veces con repetidos), solo para el control de RN-12, como conjunto. Aciertos de la categoría ganadora: 6. Pozo: **no lo publica** (el texto "85 millones de pesos" es fijo y se ignora, Clarifications 19/11/2026, planificación) |
| Selectores HTML (relevado) | **Listado**: cada `<a href="/sorteos/{N}">` con el texto "Quini Sorteo {N} {dd/mm/aaaa}". **Sorteo**: número y fecha en `<p class="lead"><strong>Fecha del sorteo: {dd/mm/aaaa}; Número de sorteo: {N}</strong>`. Cada modalidad es un `<div class="card">` con el rótulo en `<h3 class="card-title">`, los números en `<p class="h2">` como `<span class="badge">` (Premio Extra agrega un `<span>` vacío, que se descarta) y una tabla cuyas filas tienen tres `<td>` (aciertos, ganadores "Vacante" o cantidad, premio sin "$") |
| Sorteo inexistente (relevado) | 500 con la página "Error. An error occurred while processing your request." (9999) |

| Rótulo publicado | Modalidad |
|------------------|-----------|
| TRADICIONAL | Tradicional – Primer Sorteo |
| LA SEGUNDA | Tradicional – La Segunda |
| REVANCHA | Revancha |
| SIEMPRE SALE | Siempre Sale |
| POZO EXTRA | Premio Extra |

## F3 — quiniya.com.ar

| Aspecto | Valor |
|---------|-------|
| Nombre en el archivo | `quiniya.com.ar` |
| Listado | `/sorteos`: lista agrupada por mes, con número, fecha y números. Profundidad (relevada): unos 12 meses, del 3324 (23/11/2025) al 3427 (18/11/2026) |
| Sorteo | `/sorteos/{N}` |
| Cobertura | Desde el sorteo 2787 (09/09/2020). Antes: "Fuera de cobertura" |
| Sorteo inexistente | 404 → "No encontrado" |
| Orden de los números | Orden de extracción. Se comparan como conjunto (RN-13) |
| Columnas de premios | Aciertos · Ganadores · Premio |
| Datos estructurados (relevado) | Un bloque `<script type="application/ld+json">` con un `BreadcrumbList` de schema.org cuyo último elemento es "Sorteo {N}". **No trae números ni premios**, a diferencia de lo que suponía R-04. Decisión del responsable (19/11/2026): se lee con `json` y solo se coteja el número; si difiere del HTML, el intento es "Estructura no reconocida". Si el bloque falta o no se puede leer, no es un error. Todos los datos salen del HTML |
| Premio Extra | Conjunto de números sin repetidos, ordenado, solo para el control de RN-12. Aciertos: 6. Pozo: no lo publica |
| Selectores HTML (relevado) | **Listado**: los últimos 4 sorteos en tarjetas con `<h3>` "{dd/mm/aaaa} #{N}" y el histórico en una tabla cuyas filas tienen `<th scope="row">` con la fecha "{d/m/aaaa}" (sin ceros a la izquierda) y un `<a href="/sorteos/{N}">`. **Sorteo**: número en el `<h1>` "Resultados del Sorteo {N} de Quini 6"; fecha en el `<p>` "Sorteado el {día} {dd} de {mes} de {aaaa}". Cada modalidad es un `<div class="shadow">` con el rótulo en `<h2>`, los números como `<span class="bolilla">` dentro de `<div class="draw-numbers">` y una tabla cuyas filas tienen `<th>` (aciertos) y dos `<td>` (ganadores "Pozo Vacante" o cantidad, premio sin "$"). La sección "Estadísticas y comparación" repite rótulos sin `draw-numbers` y se ignora |
| Sorteo inexistente (relevado) | 404 sin contenido (9999) |

| Rótulo publicado | Modalidad |
|------------------|-----------|
| Tradicional Primer Sorteo | Tradicional – Primer Sorteo |
| La Segunda del Quini | Tradicional – La Segunda |
| Revancha | Revancha |
| Siempre Sale | Siempre Sale |
| Pozo Extra | Premio Extra |

## F0 — Extracto oficial de la Lotería de Santa Fe (solo enlace)

No se consulta automáticamente (FR-007, D-02). El detalle de cada sorteo muestra el enlace "Ver extracto oficial (Lotería de Santa Fe)", que abre la página general de extractos en una pestaña nueva, porque el sitio oficial no tiene una dirección por sorteo (AC-1.13).

| Aspecto | Valor |
|---------|-------|
| Dirección del enlace | **Decisión del responsable (19/11/2026)**: `https://numerosganadores.com.ar/sorteos/{N}`, con el número del sorteo. En el relevamiento se propuso la página general de la Lotería de Santa Fe (`https://www.loteriasantafe.gov.ar/quini-6-2/`, canónica y con el visor de extractos), y el responsable eligió la dirección por sorteo de F2. Queda pendiente confirmar si el texto "Ver extracto oficial (Lotería de Santa Fe)" se mantiene con este destino |
