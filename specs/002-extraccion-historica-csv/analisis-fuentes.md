# Relevamiento de fuentes: Extracción histórica de sorteos

**Feature**: [spec.md](spec.md) | **Fecha del relevamiento**: 18/11/2026

**Método**: consulta de las páginas públicas indicadas por el responsable del proyecto, lectura del HTML recibido sin ejecutar JavaScript y prueba de direcciones de sorteos existentes, antiguos e inexistentes. Los datos citados son los que cada sitio publicaba ese día. **No fueron validados** y se usan solo como evidencia del comportamiento de cada fuente. Las estructuras pueden cambiar sin aviso.

Identificadores usados en la especificación:

| Id | Fuente | Tipo | Relación con el pedido |
|----|--------|------|------------------------|
| **F1** | quini-6-resultados.com.ar | Secundaria | Fuente 1 del pedido |
| **F2** | numerosganadores.com.ar | Secundaria | Fuentes 2 y 4 del pedido. `/ultimoSorteo` es una página del mismo sitio: **no es una fuente independiente** |
| **F3** | quiniya.com.ar | Secundaria | Fuente 3 del pedido |
| **F0** | Lotería de Santa Fe, extractos oficiales | **Oficial** (organismo que realiza el sorteo) | **No se consulta automáticamente**: solo enlace de cotejo manual (D-02, resuelta el 18/11/2026) |

---

## 1. Comparación de las fuentes

| Aspecto | F1 | F2 | F3 | F0 (solo cotejo) |
|---------|----|----|----|----------------|
| Acceso a un sorteo | `/quini6/sorteo-{N}-del-dia-{dd-mm-aaaa}.htm`. Exige número **y** fecha exactos | `/sorteos/{N}` | `/sorteos/{N}` | Formulario con selectores de mes y de sorteo dentro de una aplicación embebida. No hay una dirección propia por sorteo: elegir otro sorteo requiere interactuar con el formulario |
| Listado de sorteos | `/quini6/sorteos-anteriores.aspx`: últimos 3 meses, agrupados por mes, con número y fecha | `/sorteos`: últimos 20 sorteos, con número y fecha | `/sorteos`: lista única agrupada por mes, con número, fecha y números | Selector con los últimos 3 meses (septiembre a noviembre de 2026) |
| Profundidad histórica comprobada | Unos 3 meses. El sitio advierte que los sorteos más viejos "pueden haber caducado" | Desde el sorteo 2211 (17/12/2014) | Desde el sorteo 2787 (09/09/2020) | Unos 3 meses |
| Sorteo inexistente | "No encontrada" (404). También responde así si la fecha de la dirección no coincide con el sorteo | **Error del servidor (500)**: no distingue "no existe" de "falla del sitio" | "No encontrada" (404) | No ofrece sorteos inexistentes |
| Último sorteo | No tiene una página propia | `/ultimoSorteo` | `/sorteos/ultimo` | Es el que muestra al abrir |
| Datos en el HTML | Sí | Sí | Sí, y además datos estructurados embebidos | El último sorteo viene en la primera carga. Los demás requieren el formulario |
| Orden de los números | Ascendente | Orden de extracción; en sorteos antiguos, ascendente | Orden de extracción | Ascendente |
| Columnas de premios | Aciertos · Ganadores · Premio | Cantidad de aciertos · Cantidad de ganadores · Premio para cada uno | Aciertos · Ganadores · Premio | Premio · POZO $ · Ganadores · Premios $ (y ACIERTOS en Siempre Sale) |
| Pozo destinado a la categoría | **No**. Solo aparece cuando la categoría está vacante, en la misma columna "Premio" | **No**. Ídem | **No**. Ídem | **Sí**, para todas las categorías |
| Categoría vacante | "Vacante" en la columna de ganadores | "Vacante" | "Pozo Vacante" o "Pozo vacante" | "VACANTE*" y la nota "El pozo se acumula para el primer premio del concurso siguiente según artículo 23° del reglamento" |
| Categoría "Estímulo" | No | No | No | **Sí**, en Tradicional, La Segunda, Revancha y Siempre Sale |
| Centavos | A veces los omite | A veces los omite | A veces los omite | Siempre con dos decimales |
| Símbolo de moneda | "$ " | Sin símbolo | Sin símbolo | "$" en el encabezado |
| Aviso de calidad | "En caso de discrepancia prevalece el extracto oficial" | "Los datos pueden contener errores" | Atribuye los datos a la Lotería de Santa Fe | Es la fuente oficial |

### Nombres de las modalidades en cada fuente

| Modalidad del catálogo vigente ([001] RN-13) | F1 | F2 | F3 | F0 |
|----------------------------------------------|----|----|----|----|
| Tradicional – Primer Sorteo | SORTEO TRADICIONAL | TRADICIONAL | Tradicional Primer Sorteo | Tradicional Primer Sorteo |
| Tradicional – La Segunda | LA SEGUNDA DEL QUINI / LA SEGUNDA DEL QUINI 6 | LA SEGUNDA | La Segunda del Quini | Tradicional La Segunda del Quini |
| Revancha | SORTEO REVANCHA / **LA SEGUNDA DEL QUINI 6 REVANCHA** (en la tabla de premios) | REVANCHA | Revancha | Revancha |
| Siempre Sale | QUINI QUE SIEMPRE SALE / EL QUINI QUE SIEMPRE SALE | SIEMPRE SALE | Siempre Sale | Siempre Sale |
| Premio Extra | POZO EXTRA / QUINI 6 POZO EXTRA | POZO EXTRA | Pozo Extra | Premio Extra |

El rótulo de Revancha en la tabla de premios de F1 contiene "LA SEGUNDA". Una equivalencia de rótulos por coincidencia parcial asignaría mal esa tabla.

### Premio Extra en cada fuente

| Aspecto | F1 | F2 | F3 | F0 |
|---------|----|----|----|----|
| Números | No muestra números propios | Lista los números de las tres extracciones. A veces incluye los 18 con repetidos y a veces sin repetidos | Conjunto sin repetidos, ordenado | Los 18 números ordenados, con repetidos |
| Aciertos de la categoría | "-" | 6 | 6 | Sin columna de aciertos |
| Pozo | Texto: "55 millones de pesos" (sorteo 3426) | Texto **fijo** "85 millones de pesos": aparece igual en el sorteo 2211 de 2014 y en el 3426 de 2026 | No informa | POZO $ 200.000.000,00 (sorteo 3427) |

Conclusión: el pozo de Premio Extra que publica F2 no es un dato confiable, porque es un texto fijo de la página.

---

## 2. Evidencias de diferencias entre fuentes

### Sorteo 3427 (18/11/2026): F2 frente a F0

| Dato | F2 | F0 | Tipo de diferencia |
|------|----|----|--------------------|
| La Segunda, 4 aciertos, importe por ganador | 5.015 | 5.547,85 | Valor distinto |
| Premio Extra, pozo | "85 millones de pesos" | 200.000.000,00 | Valor distinto |
| Tradicional – Primer Sorteo, 4 aciertos, importe por ganador | 12.060 | 12.060,13 | Centavos omitidos |
| La Segunda, 6 aciertos, importe por ganador | 3.294.600.472 | 3.294.600.472,80 | Centavos omitidos |
| La Segunda, 5 aciertos, importe por ganador | 1.370.834 | 1.370.834,40 | Centavos omitidos |
| Revancha, pozo vacante | 3.113.164.973 | 3.113.164.972,80 | Redondeo |
| Categoría Estímulo | No la informa | Primer Sorteo $ 11.000.000,00 vacante; La Segunda $ 36.286.810,56 con 1 ganador; Revancha $ 34.043.107,68 vacante; Siempre Sale $ 3.689.352,36 con 0 ganadores y $ 0,00 | Categoría omitida |

### Sorteo 3426 (15/11/2026): F1, F2 y F3

- Los números coinciden como conjunto, aunque F1 los muestra ordenados y F2 y F3 en orden de extracción. Por ejemplo, F1 publica "01 - 02 - 10 - 13 - 38 - 39" y F2 publica "02 01 39 13 10 38".
- Las cantidades de ganadores y los importes coinciden en las tres.
- El pozo de Premio Extra difiere: F1 informa 55 millones y F2 informa 85 millones.

### Sorteo 3398 (09/08/2026)

- F3 publica el importe "494,443,71", con un formato inválido. F2 publica 494.443,71 para el mismo dato.
- El código de F0 trata al 3398 como sorteo "especial" y no muestra el detalle de sus modalidades. F2 y F3 lo presentan como un sorteo habitual.

---

## 3. Significado de la columna "Premio" en las fuentes secundarias

Las tres fuentes secundarias usan una sola columna de importe con dos significados distintos:

- **Categoría vacante**: el importe es el **pozo destinado** a la categoría. Ejemplo: en el sorteo 3427, F2 publica Tradicional 6 aciertos "Vacante · 1.100.000.000", y F0 publica para esa categoría "POZO $ 1.100.000.000,00 · VACANTE".
- **Categoría con ganadores**: el importe es el **importe individual por ganador**. Ejemplo: en el sorteo 3427, F2 publica La Segunda 6 aciertos "1 · 3.294.600.472", y F0 publica "Ganadores 1 · Premios $ 3.294.600.472,80".

Por eso, en las fuentes secundarias **el pozo destinado a una categoría con ganadores nunca está disponible**. Calcularlo multiplicando el importe individual por los ganadores está prohibido ([001] RN-27 y RN-18 de esta spec).

---

## 4. Consecuencias para la especificación

1. Solo F0 permite distinguir pozo destinado e importe individual en todas las categorías. Como F0 no se consulta (D-02), el pozo destinado de toda categoría con ganadores queda "No disponible".
2. F0 y F1 cubren unos 3 meses. Para períodos más antiguos solo quedan F2 (desde 2014) y F3 (desde 2020), así que a menudo habrá una sola fuente o ninguna (D-01, D-05).
3. F2 responde con un error del servidor ante un sorteo inexistente. La aplicación no puede distinguir en F2 entre "no encontrado" y "no disponible" (RN-08).
4. F1 exige conocer la fecha para construir la dirección. La fecha debe obtenerse de otra fuente o del listado de F1 (D-06).
5. Las secundarias omiten centavos o redondean. Compararlas con F0 producirá diferencias de centavos frecuentes (D-10).
6. F0 publica una categoría "Estímulo" que no existe en el catálogo vigente de la aplicación. No afecta a la extracción porque F0 no se consulta (D-09).
7. Existen sorteos "especiales" que la fuente oficial presenta sin detalle (D-06).
8. Reglas de acceso (verificado el 19/11/2026): el archivo de reglas para robots de F1, F2 y F3 contiene solo un preámbulo comentado sobre "señales de contenido", sin ninguna instrucción de acceso ni señal declarada. Ese preámbulo indica que, sin señal, el sitio "ni otorga ni restringe" permiso. Ninguno de los tres publica condiciones de uso. quiniya publica un aviso legal que no garantiza la exactitud de los datos y pide cotejarlos con las fuentes oficiales. El responsable autorizó la consulta automatizada con un máximo de una consulta cada 2 segundos por sitio (D-13).
