# Especificación funcional (Feature Specification): Extracción histórica de sorteos y exportación CSV

**Feature Branch**: `002-extraccion-historica-csv`

**Created**: 18/11/2026

**Status**: Aprobada por el responsable del proyecto (19/11/2026), con aclaraciones del 18/11/2026 y del 19/11/2026, incluidas las de la planificación y del análisis. No quedan decisiones funcionales pendientes ni propuestas sin aprobar. Plan y tareas generados; textos e interpretaciones del plan aprobados el 19/11/2026. **Corregida el 20/11/2026** por el responsable (Clarifications, sesión 2026-11-20): prioridad de fuentes, nombres de modalidades, pozo calculado, tolerancia del 1 %, corrección de importes mal cargados y números de Pozo Extra. **Ajustada el 20/11/2026** por el responsable (Clarifications, sesión 2026-11-20, ajustes de pantalla): sin acumulación ni importe trasladado, detalle sin fuentes por dato, eliminación de extracciones terminadas y calendario en las fechas (D-22 a D-25). **Ajustada el 21/11/2026** (Clarifications, sesión 2026-11-21): barra de progreso en el avance (D-26) y fechas escritas con el teclado (D-27). **Corregida el 23/11/2026** (Clarifications, sesión 2026-11-23): importes que difieren en menos de $ 1,00 (D-28), valores inválidos fuera de la consolidación (D-29), pozo de Pozo Extra calculado (D-30) y puntos de miles mal puestos (D-31); importes con coma en todos los separadores (D-32) y enlaces a las fuentes consultadas en lugar del extracto oficial (D-33).

**Input**: Descripción del responsable del proyecto: "Nueva Feature: Extracción histórica de sorteos y exportación CSV". Un administrador consulta fuentes públicas, extrae los resultados históricos del Quini 6 de un período, los normaliza y valida, y descarga un CSV unificado. Sin ingesta en la base de datos.

**Marco normativo**: [Constitución del proyecto QUINI_6 v1.1.0](../../.specify/memory/constitution.md), citada como "Const. N". Se apoya en la [especificación 001](../001-quini6-mvp/spec.md) aprobada.

**Convención de identificadores**: los IDs de este documento (FR-, NFR-, RN-, AC-, SC-, D-) son locales a la spec 002. Desde otra spec o desde el código se citan con el prefijo `[002]`, por ejemplo `[002] RN-17`. Las referencias a la spec 001 llevan el prefijo `[001]`, por ejemplo `[001] RN-27`.

**Documento de apoyo**: [analisis-fuentes.md](analisis-fuentes.md), con el relevamiento de las fuentes del 18/11/2026. Ahí se definen los identificadores F0 a F3.

---

## Contexto y alcance

### Objetivo

Que un administrador obtenga, para un período elegido, un archivo CSV con los resultados y premios históricos del Quini 6 recuperados de fuentes públicas. El archivo debe estar normalizado, validado y con la procedencia de cada dato, para que una futura funcionalidad de ingesta lo use como contrato de datos. Esta feature **no** incorpora nada a la base de datos de la aplicación.

### Incluido

- Pantalla de administración «Extracción histórica de sorteos».
- Consulta de fuentes externas configuradas, con respaldo ante fallas.
- Normalización de números, modalidades, categorías, ganadores e importes.
- Validación de integridad y consistencia, y detección de discrepancias entre fuentes.
- Resumen del resultado, detalle por sorteo y descarga del CSV.

### Fuera del alcance

- Insertar en la base de datos de la aplicación los datos extraídos, o modificar resultados ya existentes.
- Publicar resultados, o crear o modificar concursos, jugadas o el registro de cambios.
- Comprar cartones, realizar apuestas o incorporar pagos (Const. V).
- Extracciones periódicas o automáticas sin que un administrador las inicie.
- Agregar, quitar o reordenar fuentes desde la interfaz.
- Incluir el precio del cartón en el CSV.
- Cualquier ampliación no aprobada (Const. I). Las ideas detectadas figuran en "Propuestas futuras".

### Actores y permisos

| Capacidad | Visitante | Usuario registrado | Administrador |
|-----------|:---------:|:------------------:|:-------------:|
| Ver la pantalla «Extracción histórica de sorteos» | No | No | Sí |
| Iniciar una extracción | No | No | Sí |
| Ver el progreso, el resumen y el detalle | No | No | Sí |
| Descargar el CSV | No | No | Sí |
| Ver el listado de extracciones anteriores, propias o de otros administradores, y descargar sus archivos | No | No | Sí |

El permiso de administrador es el de [001] RN-37.

### Fuentes relevadas

El detalle está en [analisis-fuentes.md](analisis-fuentes.md). En síntesis:

- **F1, F2 y F3** son las fuentes secundarias del pedido. La página "último sorteo" del pedido pertenece al mismo sitio que F2, así que no es una fuente independiente.
- Las tres publican los datos en el HTML, sin requerir mecanismos adicionales.
- F2 y F3 permiten pedir un sorteo por su número. F1 exige además su fecha exacta.
- La profundidad histórica es muy distinta: F1 cubre unos 3 meses, F2 llega hasta 2014 y F3 hasta 2020.
- Ninguna secundaria publica el pozo destinado de una categoría con ganadores. Usan una sola columna "Premio" que significa pozo cuando la categoría está vacante e importe por ganador cuando hubo ganadores.
- Se detectaron diferencias reales entre fuentes: importes distintos, centavos omitidos, un importe con formato inválido y un pozo de Premio Extra que F2 muestra como texto fijo.
- **F0**, el extracto oficial de la Lotería de Santa Fe, **no se consulta automáticamente** (Clarifications 18/11/2026). Es la única que separa pozo, ganadores e importe individual, y queda como referencia de cotejo manual mediante un enlace en el detalle de cada sorteo.

---

## Clarifications

### Session 2026-11-18

- Q: Para cada sorteo, ¿la extracción debe consultar siempre todas las fuentes y comparar los datos, o detenerse en la primera fuente que trae todos los datos? (D-01) → A: Consultar siempre todas las fuentes que cubren el sorteo. Ninguna prevalece: toda diferencia es una discrepancia. Un dato que informa una sola fuente cuenta como recuperado, con la marca "Sin corroborar". Una fuente puede aportar los números y otra los premios, guardando el origen de cada dato. Se actualizan FR-005, RN-07, RN-08, RN-09, RN-29, RN-31, RN-32, RN-35 y AC-4.7, y se agrega AC-4.8.
- Q: ¿Se incorpora el extracto oficial de la Lotería de Santa Fe como una cuarta fuente que la extracción consulta automáticamente? (D-02) → A: No se consulta automáticamente. El detalle de cada sorteo muestra un enlace al extracto oficial para cotejarlo a mano. Consecuencias: las fuentes consultadas son F1, F2 y F3; el pozo destinado de toda categoría con ganadores queda "No disponible"; la categoría "Estímulo", que solo publica el extracto oficial, no aparece en ninguna fuente consultada (D-09 queda sin efecto). Se actualizan FR-007, RN-06, RN-07, RN-14, RN-17, RN-31, AC-3.6 y la correspondencia con el modelo, y se agrega AC-1.13.
- Q: ¿Cómo querés organizar las filas del CSV: una fila consolidada por sorteo, modalidad y categoría, o también filas con lo que informó cada fuente? (D-03) → A: Una fila por sorteo, modalidad y categoría, solo con los datos consolidados. Los números se repiten en cada fila de su modalidad. Las fuentes y las discrepancias van en columnas de texto. Derivado por el agente, a confirmar: un sorteo no recuperado figura en una sola fila con su número, su fecha si se conoce, su estado y sus motivos, con modalidad y categoría "No disponible". Se actualizan FR-014, RN-35, RN-37, RN-39, AC-4.1, AC-5.5 y AC-5.8, y se agrega RN-43.
- Q: Después de que termina una extracción, ¿cuánto tiempo y para quién debe quedar disponible su resultado (el resumen, el detalle y el CSV)? (D-12) → A: Se conservan todas las extracciones durante tiempo indefinido, visibles para todos los administradores, con quién y cuándo las ejecutó. Consecuencia: la pantalla incluye el listado de extracciones anteriores. Se actualizan FR-015, la tabla de actores, la entidad Extracción, los Supuestos y las Propuestas futuras, y se agregan RN-44, AC-1.14, AC-1.15 y AC-6.6.
- Q: En el CSV, ¿las fechas y los importes van en formato técnico (2026-11-15 y 1100000000.00, con columnas separadas por coma) o en formato argentino (15/11/2026 y 1.100.000.000,00, con columnas separadas por punto y coma)? (D-11) → A: Formato técnico: fechas AAAA-MM-DD, importes con punto decimal y sin separador de miles, columnas separadas por coma. Se confirma que el CSV no es contenido visible en el sentido de Const. VII; la pantalla mantiene el formato argentino. Se actualizan NFR-001, RN-34, RN-38 y AC-5.2.

### Session 2026-11-19

- Q: ¿Cuál es el período máximo que un administrador puede pedir en una sola extracción? (D-05) → A: 12 meses. Se actualizan RN-04, AC-1.6 y SC-007.
- Q: ¿Cómo debe identificar la extracción los sorteos de un período, si ninguna fuente permite buscar por fecha? (D-06) → A: Por numeración correlativa: se ubican el primer y el último sorteo del período verificando la fecha que informan las fuentes, y se procesan todos los números intermedios; los huecos se informan como advertencia. Se actualiza RN-05 y se agregan AC-1.16 y AC-1.17.
- Q: Un pozo puede estar acumulado y tener ganadores a la vez, y ninguna fuente informa el importe trasladado de sorteos anteriores. ¿Cómo se registra la acumulación? (D-08) → A: Como un dato aparte del estado del pozo: "Se acumula según la fuente" (sí, no o no disponible). El importe trasladado queda "No disponible" y nunca se reconstruye. Se actualizan RN-19 y RN-35 y se agrega AC-3.15.
- Q: Los tres sitios no prohíben ni autorizan el acceso automatizado y no publican condiciones de uso. ¿Autorizás consultarlos automáticamente y con qué ritmo máximo por sitio? (D-13) → A: Sí, con un máximo de una consulta cada 2 segundos por sitio. Se actualizan NFR-005 y SC-007 y se agrega AC-2.9.
- Q: ¿Aprobás las reglas marcadas "Propuesta" y los textos de pantalla marcados con †, incluida la fila única del sorteo no recuperado en el CSV? → A: Sí, se aprueban todas tal como están. Las reglas pasan a "Aprobada" y la marca † se conserva solo para la trazabilidad.
- Q: ¿Aprobás las recomendaciones de las decisiones no bloqueantes D-04 (modalidad ausente como "No informada", sin catálogo de vigencias), D-07 (aviso "requiere mantenimiento" en el resumen) y D-10 (diferencia de centavos como discrepancia, sin elegir valor)? → A: Sí, se aprueban las tres. Se actualizan RN-10, RN-30 y RN-33 y se agrega AC-2.10.

### Session 2026-11-19 (planificación)

Preguntas surgidas en `/speckit-plan` ([plan.md](plan.md), [research.md](research.md)):

- Q: F1 publica el pozo de Premio Extra como texto ("55 millones de pesos") y F2 muestra un texto fijo ("85 millones de pesos"). ¿Cómo se trata? → A: El texto de F1 con la forma "N millones de pesos" se registra como N × 1.000.000 exactos (por ejemplo, $ 55.000.000,00). El texto fijo de F2 no se toma: su ficha declara que F2 no publica ese dato. Se actualiza RN-17.
- Q: Antes del 18/06/2024, ¿una categoría fuera del catálogo vigente se registra (RN-25) o solo se observa (RN-14)? → A: Prevalece RN-25: se registra como una categoría propia rotulada "Categoría de N aciertos", con el aviso "Reglas del período no verificadas". Desde el 18/06/2024 se aplica RN-14. Se actualizan RN-14 y RN-25.
- Q: Mientras se ubican los sorteos del período y todavía no se conoce el total, ¿qué muestra la pantalla? → A: "Extracción en curso", el período y "Identificando los sorteos del período…" † en lugar del avance. Se actualizan FR-003 y AC-1.2.
- Q: ¿Cómo se actualiza el avance mientras la extracción está en curso? → A: Con JavaScript, el bloque de avance se actualiza solo cada 5 segundos y, al terminar, se muestra el resumen. Sin JavaScript, se actualiza al recargar la página. Se actualizan FR-003 y AC-1.2.

### Session 2026-11-19 (análisis)

Preguntas surgidas en `/speckit-analyze` sobre [plan.md](plan.md) y [tasks.md](tasks.md):

- Q: ¿Qué pasa ante un error inesperado mientras se procesa un sorteo? → A: Se aprueba [002] I-09 ([research.md](research.md)): si falla el intérprete de una fuente, ese intento queda "Estructura no reconocida"; si falla otra parte del tratamiento, el sorteo queda "No recuperado" con el motivo "Error inesperado al procesar el sorteo" y la extracción continúa (RN-10, RN-31, RN-33, NFR-006).
- Q: ¿Cuándo un número de sorteo es un hueco en la numeración (RN-05, AC-1.16)? → A: Se aprueba [002] I-10: solo cuando todas las fuentes que lo cubren respondieron "No encontrado" o "No disponible o no encontrado". Si alguna quedó "No disponible" o "Estructura no reconocida", el sorteo es "No recuperado" con el motivo de cada fuente y no se cuenta como hueco.
- Q: Con un único proceso que ejecuta las extracciones de a una, ¿cómo se mide SC-007 si otro administrador ya tiene una extracción en curso? → A: SC-007 se mide sin otras extracciones en curso. Si hay otras, la nueva espera su turno mostrando "Identificando los sorteos del período…", sin estados nuevos. Se actualiza SC-007.
- Q: ¿Aprobás los textos que el plan propuso con la marca ‡ ([contracts/mensajes.md](contracts/mensajes.md)), los rótulos del resumen y las interpretaciones I-01 a I-08 ([research.md](research.md))? → A: Sí, se aprueban todos tal como están. Los textos pasan a †.
- Q: ¿Confirmás que esta feature amplía el alcance de [001] para consultar fuentes externas (F1, F2 y F3), solo a pedido de un administrador y sin ingesta en la base? → A: Sí. Se actualiza el punto 1 de "Relación con la especificación 001 y posibles contradicciones".

### Session 2026-11-20 (correcciones del responsable)

El responsable pidió seis correcciones tras usar la extracción con las fuentes reales. Reemplazan lo aprobado antes en los puntos indicados (D-14 a D-19):

- Q: ¿En qué orden se usan las fuentes y qué significa "fuente de la verdad"? (D-14) → A: **Prioridad con cotejo**. La 1.ª fuente es numerosganadores.com.ar (F2), la 2.ª quiniya.com.ar (F3) y la 3.ª quini-6-resultados.com.ar (F1). Siempre se consultan F2 y F3 y se comparan; si difieren, vale el valor de la fuente de mayor prioridad. F1 solo se consulta si, con F2 y F3, el sorteo queda sin recuperar o le falta algún dato esperado; si no hace falta, su intento figura "No requerida". Interpretación del agente, a confirmar: una diferencia que no es de importes (números, ganadores, fecha, aciertos) o una omisión muestra el valor de la fuente prioritaria, pero se sigue registrando como discrepancia y el sorteo queda "Con inconsistencias" (Const. IX: no se ocultan inconsistencias). Se actualizan RN-06, RN-07, RN-08, RN-09, RN-27, RN-28, FR-005, AC-4.1 y AC-4.8, y se agregan AC-2.11 y AC-4.9. D-01 queda reemplazada.
- Q: ¿Cómo se nombran las modalidades? (D-15) → A: En la pantalla de extracción y en el CSV: "Tradicional", "La Segunda", "Revancha", "Siempre Sale" y "Pozo Extra". El resto de la aplicación ([001]) no cambia. Se actualizan RN-11 y AC-3.1.
- Q: ¿Qué pozo destinado y qué importe individual se muestran? (D-16) → A: En una categoría con ganadores, el pozo destinado es **importe individual × ganadores**, marcado "Calculado: importe individual × ganadores" en la pantalla y en la procedencia del CSV, para que no se confunda con un pozo publicado. Si una fuente publica el pozo (F1, pozo de Pozo Extra), se usa el publicado. En una categoría vacante, el importe individual es 0,00. Es una excepción aprobada a RN-18, FR-011 y Const. VIII ("no se inventan pozos"): el valor no se presenta como oficial y su origen queda a la vista. Se actualizan RN-17, RN-18, RN-19, RN-20, RN-31, FR-011, AC-3.4, AC-3.5, AC-3.6, AC-3.14 y SC-002.
- Q: ¿Cómo se tratan las diferencias de importes entre fuentes? (D-17) → A: Si todos los importes difieren menos del 1 % del valor de la fuente de mayor prioridad, no hay inconsistencia: se usa el valor de esa fuente redondeado a pesos enteros (por ejemplo, $ 657.151.589,00) y el detalle muestra una nota informativa con los valores de cada fuente. Si la diferencia llega al 1 %, el sorteo queda "Con inconsistencias" y el importe "Sin determinar", como antes. Se actualizan RN-30, NFR-007 y AC-4.5. D-10 queda reemplazada. **Aclaración posterior del responsable (20/11/2026, sorteo 3233)**: primero se redondea cada importe y después se compara; si los importes redondeados coinciden (756.099.026 y 756.099.025,92), no hay diferencia ni nota.
- Q: ¿Qué se hace con un importe mal cargado como «410.1156,25»? (D-18) → A: Cuando el último grupo antes de la coma tiene cuatro dígitos, la coma decimal se corre un lugar a la izquierda y el resultado se redondea a centavos (mitad hacia arriba): «410.1156,25» → $ 410.115,63. El detalle muestra la nota informativa "Importe corregido: «410.1156,25» → $ 410.115,63". No cambia el estado del sorteo y el valor corregido se coteja con las demás fuentes según D-17. Los demás formatos inválidos siguen RN-16. Se actualizan RN-16 y AC-3.8 y se agrega AC-3.16.
- Q: ¿Qué se hace con un importe con tres o más decimales, como «1.278.143,114» (sorteo 3250, publicado igual por F2 y F3)? (D-20) → A: Se redondea a centavos (mitad hacia arriba): $ 1.278.143,11, con la misma nota informativa de D-18, "Importe corregido: «1.278.143,114» → $ 1.278.143,11". No cambia el estado del sorteo y el valor corregido se coteja con las demás fuentes según D-17. Si el importe tiene además cuatro dígitos en el último grupo, se aplican las dos correcciones. Se actualiza RN-16 y se agrega AC-3.18.
- Q: Cuando numerosganadores.com.ar y quiniya.com.ar difieren (sorteo 3235: vacante frente a 13 ganadores en el Segundo Premio de Tradicional; sorteo 3308: Siempre Sale inválido en numerosganadores frente a 21 ganadores con 5 aciertos en quiniya), ¿cómo se decide? (D-21) → A: **Se consulta quini-6-resultados.com.ar para desempatar**. F1 se consulta también cuando F2 y F3 difieren en algún dato o una de ellas publica un dato inválido, y se le pide cualquier sorteo con la fecha que informan las otras dos, aunque no figure en su listado. Si dos de las tres fuentes coinciden, ese valor resuelve la diferencia: no es inconsistencia y el detalle muestra la nota informativa "Resuelto por coincidencia de 2 de 3 fuentes" con lo que publicó cada una; los importes se comparan redondeados (RN-30). La observación de dato inválido de la fuente que quedó en minoría en esa modalidad pasa a ser informativa. Si F1 no tiene el sorteo, no responde o publica un tercer valor, rige lo anterior (D-14 y RN-30) y el sorteo queda "Con inconsistencias". Se actualizan RN-07, RN-09 y AC-4.9 y se agregan AC-4.10 y AC-4.11; la interpretación I-08 queda ampliada.
- Q: ¿Cómo se ven los números de Pozo Extra? (D-19) → A: Pozo Extra muestra como números la unión de los números consolidados de Tradicional, La Segunda y Revancha, marcada "Calculado: unión de Tradicional, La Segunda y Revancha"; si falta alguno de los tres, queda "No disponible". En el CSV no caben en `numero_1` a `numero_6`: van en la nueva columna `numeros_pozo_extra`, al final. El contrato pasa a la versión 2.0, porque cambian valores de columnas existentes (modalidad, pozo e importe individual). Se actualizan RN-12, RN-43 y AC-3.3 y se agrega AC-3.17.

### Session 2026-11-20 (ajustes de pantalla del responsable)

El responsable pidió, como administrador, cuatro ajustes de la pantalla de extracción (D-22 a D-25). Reemplazan lo aprobado antes en los puntos indicados:

- Q: ¿Se conservan "Se acumula según la fuente" y el importe trasladado? (D-22) → A: **No**. Ninguna fuente los publica y no aportan información: se quitan del detalle del sorteo, del CSV y del dominio. El CSV pasa a la **versión 3.0** porque se quitan las columnas `se_acumula_segun_fuente` e `importe_trasladado` (cambio mayor aprobado antes de que exista la ingesta; las demás columnas conservan su significado y su orden relativo). Los archivos ya guardados conservan su versión (RN-44). Se actualizan RN-19 y RN-35, se quita AC-3.15 y D-08 queda reemplazada.
- Q: ¿Qué fuentes se muestran en el detalle del sorteo? (D-23) → A: **Solo en la sección "Fuentes consultadas"**, con su columna "Fuente". Se quitan la columna "Fuentes" de las tablas de cada categoría y las fuentes que acompañaban a la fecha y a los números ("Números: 06, 10, 11, 22, 27, 28"). La marca "Calculado: …" del pozo destinado y del importe individual deja de verse en la pantalla y queda solo en la procedencia del CSV; el responsable lo decide sabiendo que, en pantalla, ese valor calculado se ve igual que uno publicado (enmienda de D-16 solo para la pantalla). Se conservan la marca "Sin corroborar", que pasa junto al valor, y la marca "Calculado: unión de Tradicional, La Segunda y Revancha" de los números de Pozo Extra (D-19). Se actualizan RN-18, AC-1.12, AC-2.2 y AC-3.5.
- Q: ¿Se pueden eliminar extracciones? (D-24) → A: **Sí, las terminadas**. Cada fila de "Extracciones anteriores" tiene un menú de acciones (⋮) con "Eliminar", que lleva a una confirmación; al confirmar se borran la extracción, su resumen, el detalle de sus sorteos y su archivo. Cualquier administrador puede eliminar cualquier extracción terminada; la que está en curso no ofrece la opción. Además, la columna "Inicio" del listado pasa a llamarse "Fecha". Se actualizan RN-44, FR-015, AC-1.14 y los Supuestos, se agregan AC-1.18 y AC-1.19, y D-12 queda ampliada.
- Q: ¿Cómo se ingresan las fechas del período? (D-25) → A: **Con un calendario**: al hacer clic en "Fecha de inicio" o "Fecha de finalización" se despliega un calendario para elegir el día, y al escribir la fecha las barras se agregan solas (01012025 → 01/01/2025). Se usa el selector de fecha del navegador, sin dependencias nuevas; las validaciones de RN-01 a RN-04 no cambian. Se agrega AC-1.20. *(Enmendada el 21/11/2026 por D-27: el calendario se abre con su ícono y no al hacer clic en el campo, para poder escribir la fecha con el teclado.)*

### Session 2026-11-21 (ajustes de pantalla del responsable)

- Q: ¿Cómo se ve que la extracción avanza? (D-26) → A: Además del texto "N de M sorteos procesados", el bloque de avance muestra una **barra de progreso** que crece a medida que se procesan los sorteos (procesados sobre identificados). Se actualiza junto con el texto: cada 5 segundos con JavaScript, al recargar sin él. Mientras se identifican los sorteos no se muestra, porque todavía no se conoce el total. Se usa el elemento de progreso del navegador, sin dependencias nuevas, con el texto del avance como nombre accesible. Se actualiza FR-003 y se agrega AC-1.21.
- Q: Al hacer clic en un campo de fecha se abre el calendario y no deja escribir la fecha con el teclado. ¿Cómo se corrige? (D-27) → A: Se **conserva el calendario**, pero **se abre con su ícono** (o con el teclado, según el navegador) y no al hacer clic en cualquier parte del campo: forzarlo así hacía que el calendario abierto tomara las teclas. Al hacer clic en el campo, el administrador escribe la fecha con el teclado, también con el teclado numérico, y las barras se agregan solas (01012025 → 01/01/2025). Se quita el script que abría el calendario. D-25 queda enmendada y se actualiza AC-1.20.

### Session 2026-11-23 (corrección del responsable)

- Q: En el sorteo 2918 (19/12/2021, Revancha), el pozo destinado quedó "Sin determinar" con $ 47.930.930,50 (numerosganadores.com.ar), $ 74.669.257,73 (quiniya.com.ar) y $ 47.930.930,00 (quini-6-resultados.com.ar): redondeado, 47.930.930,50 da 47.930.931 y no coincide con 47.930.930, así que no hay 2 de 3. ¿Cómo se comparan los importes? (D-28) → A: **Dos importes coinciden si difieren en menos de $ 1,00**, porque unas fuentes redondean los centavos y otras los quitan. El consolidado toma el importe de la fuente de mayor prioridad **sin centavos** (en el 2918, $ 47.930.930 por coincidencia de 2 de 3); si ese importe tenía centavos, el detalle muestra la nota informativa "Diferencia de centavos o redondeo (menor al 1 %)", porque el valor no es el publicado. Los sorteos 3232 y 3233 siguen sin nota (657.151.589 y 657.151.588,80 difieren en menos de $ 1,00 y el importe prioritario no tiene centavos). La tolerancia del 1 % se mide sobre los importes sin centavos. Reemplaza el "redondeo → comparación" de la aclaración del 20/11/2026 (D-17); se actualizan RN-30, AC-4.5 y NFR-007 y se agrega AC-4.12.
- Q: En el sorteo 3425 (11/11/2026), numerosganadores.com.ar y quiniya.com.ar publican Siempre Sale con 0 ganadores (dato inválido según RN-26) y quini-6-resultados.com.ar, 6 ganadores con $ 56.785.482 cada uno; la coincidencia de 2 de 3 dio por bueno el 0. ¿Cómo se decide? (D-29) → A: **Un valor que viola RN-26 no participa en la comparación ni en la coincidencia de 2 de 3**, aunque lo publiquen dos fuentes: se descarta, como un dato con formato inválido (no es una omisión). Los importes de esa categoría que publica la misma fuente tampoco se usan, porque su concepto depende de los ganadores (RN-17). Si otra fuente publica un valor válido, ese valor prevalece (con la marca "Sin corroborar" si es la única) y la observación de dato inválido de las fuentes descartadas pasa a ser informativa, como en D-21. Si ninguna publica un valor válido, el dato queda "No disponible" y la observación sigue siendo inconsistencia. Se actualizan RN-07 y RN-26 y se agrega AC-4.13.
- Q: En el sorteo 3425, el pozo de Pozo Extra figura $ 55.000.000,00 "Sin corroborar", aunque numerosganadores.com.ar y quiniya.com.ar coinciden en 772 ganadores y $ 259.067 cada uno (≈ $ 200.000.000). ¿Cómo se corrige? (D-30) → A: El texto "55 millones de pesos" de quini-6-resultados.com.ar es **fijo**: aparece igual en los 28 sorteos extraídos de 2024 a 2026, mientras que ganadores × importe individual da 65, 85, 105, 130 y 200 millones según la época. **Se trata como el texto fijo de F2: la ficha de F1 declara que no publica el pozo de Pozo Extra** y ninguna fuente consultada lo publica. El pozo de Pozo Extra se calcula como el de cualquier categoría con ganadores (RN-18, D-16): importe individual consolidado × ganadores, marcado "Calculado: importe individual × ganadores" y sin la marca "Sin corroborar", porque se calcula con datos corroborados. Reemplaza la aclaración del 19/11/2026 sobre el texto de F1; se actualizan RN-17 y se agrega AC-4.14.
- Q: En el sorteo 3383 (Tradicional, Segundo Premio) las tres fuentes publican «1.0867.330» y en el 3415 (Revancha, vacante) «2.57.2821.792», con los puntos de miles mal puestos, y el sorteo queda "Recuperado parcialmente". ¿Cómo se corrige? (D-31) → A: **Se reagrupan los dígitos de la parte entera en tríos desde la derecha**, con el punto de miles entre ellos: «1.0867.330» → $ 10.867.330 y «2.57.2821.792» → $ 2.572.821.792. Los decimales se conservan («$ 1.0867.330,29» de quini-6-resultados.com.ar → $ 10.867.330,29) y, si son tres o más, se redondean según D-20. Se aplica solo si el último grupo antes de la coma tiene tres dígitos y después de D-18, que conserva su prioridad («3.0000» → $ 3.000,00). El detalle muestra la nota informativa de D-18, "Importe corregido: «1.0867.330» → $ 10.867.330,00", y el valor corregido se coteja con las demás fuentes (D-17, D-21, D-28): si no coincide, rige la discrepancia como para cualquier importe. Se actualiza RN-16 y se agrega AC-3.19.
- Q: En el sorteo 3398 (09/08/2026, Tradicional, Segundo Premio) las tres fuentes publican el importe individual «494,443,71», con la coma en todos los separadores, y el sorteo queda "Recuperado parcialmente" con el motivo "Falta: Tradicional: Segundo Premio: importe individual". ¿Cómo se corrige? (D-32) → A: **Se leen los dígitos de derecha a izquierda: los dos que siguen a la última coma son los decimales y el resto, la parte entera**: «494,443,71» → $ 494.443,71. Se aplica solo si el importe tiene dos o más comas, ningún punto y dos dígitos después de la última coma; «1,234,567» no se corrige y sigue siendo un formato no reconocido. El detalle muestra la nota informativa de D-18, "Importe corregido: «494,443,71» → $ 494.443,71", y el valor corregido se coteja con las demás fuentes como cualquier importe. Reemplaza el ejemplo "494,443,71" de RN-16 y AC-3.8, que pasa a ser «1,234,567»; se agrega AC-3.20.
- Q: El detalle del sorteo muestra "Ver extracto oficial (Lotería de Santa Fe)", que lleva a https://numerosganadores.com.ar/sorteos/{N}, y en "Fuentes consultadas" las direcciones de las tres fuentes solo como texto. ¿Cómo se muestran? (D-33) → A: **Se quita el enlace "Ver extracto oficial (Lotería de Santa Fe)"** (llevaba a una de las fuentes consultadas y no al extracto oficial) y **cada "Dirección consultada" pasa a ser un enlace** a la página de esa fuente para ese sorteo, que se abre en una pestaña nueva; el texto del enlace es la dirección. El extracto oficial (F0) sigue sin consultarse (D-02). Se actualizan FR-007, AC-1.12 y AC-1.13; se quitan la clave `ext.enlace_oficial` y el campo `enlace_oficial` de la API.

---

## Escenarios de usuario y pruebas (User Scenarios & Testing) *(obligatorio)*

Cada criterio de aceptación describe un resultado observable desde la pantalla o en el archivo descargado, abierto con una planilla de cálculo (Const. VI). Los criterios que requieren provocar fallas de una fuente se verifican en un entorno de prueba con fuentes de prueba configurables (ver Supuestos). Los textos marcados con † los propuso el agente y el responsable los aprobó el 19/11/2026; la marca se conserva solo para la trazabilidad.

### Historia de usuario 1 — Ejecutar una extracción y ver su resumen (Prioridad: P1)

Como administrador, quiero elegir un período, iniciar la extracción y ver su progreso y su resumen, para saber qué sorteos se recuperaron y cuáles requieren revisión.

**Por qué esta prioridad**: Es el recorrido principal. Sin él no hay extracción ni archivo.

**Prueba independiente**: Con una sola fuente configurada, un administrador extrae un período de dos semanas y verifica el progreso, el resumen y el detalle por sorteo.

**Criterios de aceptación**:

1. **AC-1.1** — **Dado** un administrador con sesión iniciada, **cuando** abre la sección de administración, **entonces** ve el acceso «Extracción histórica de sorteos». Al ingresar ve los campos "Fecha de inicio" y "Fecha de finalización" y el botón "Iniciar extracción" †.
2. **AC-1.2** — **Dado** que el administrador ingresa un período válido, **cuando** pulsa "Iniciar extracción", **entonces** ve "Extracción en curso" †, el período consultado y el avance "N de M sorteos procesados" † (FR-003). Mientras se identifican los sorteos del período, en lugar del avance ve "Identificando los sorteos del período…" †. Con JavaScript habilitado, el avance se actualiza sin recargar la página y, al terminar, se muestra el resumen (Clarifications 19/11/2026, planificación).
3. **AC-1.3** — **Dado** que la fecha de inicio es posterior a la de finalización, **cuando** pulsa "Iniciar extracción", **entonces** ve "La fecha de inicio no puede ser posterior a la fecha de finalización" †, la extracción no comienza y las fechas ingresadas se conservan (RN-02).
4. **AC-1.4** — **Dado** que una de las fechas está vacía o no es una fecha válida, **cuando** pulsa "Iniciar extracción", **entonces** ve "Ingresá una fecha válida (dd/mm/aaaa)" † junto al campo y la extracción no comienza.
5. **AC-1.5** — **Dado** que la fecha de finalización es posterior a la fecha actual, **cuando** pulsa "Iniciar extracción", **entonces** ve "La fecha de finalización no puede ser posterior a hoy" † y la extracción no comienza (RN-03).
6. **AC-1.6** — **Dado** el período del 01/01/2026 al 01/01/2027, **cuando** el administrador pulsa "Iniciar extracción", **entonces** ve "El período no puede superar los 12 meses" † y la extracción no comienza. **Dado** el período del 01/01/2026 al 31/12/2026, **cuando** pulsa "Iniciar extracción", **entonces** la extracción comienza (RN-04).
7. **AC-1.7** — **Dado** que las fuentes informan los sorteos 3422 (01/11/2026), 3423, 3424, 3425 y 3426 (15/11/2026), **cuando** el administrador extrae del 01/11/2026 al 15/11/2026, **entonces** el resumen informa 5 sorteos identificados, incluidos el del primer y el del último día (RN-01).
8. **AC-1.8** — **Dado** que la extracción terminó, **cuando** el administrador mira el resumen, **entonces** ve el período consultado, los sorteos identificados, recuperados, recuperados parcialmente, con inconsistencias y no recuperados, y las fuentes utilizadas. Los cuatro estados suman la cantidad de sorteos identificados (RN-33).
9. **AC-1.9** — **Dado** que todos los sorteos quedaron "Recuperado", **cuando** termina la extracción, **entonces** ve "Extracción finalizada" †. **Dado** que al menos uno quedó en otro estado, **cuando** termina, **entonces** ve "Extracción finalizada con advertencias que requieren revisión" † y la lista de esos sorteos, cada uno con su número, su fecha si se conoce, su estado y el motivo (RN-31, RN-33).
10. **AC-1.10** — **Dado** un período sin sorteos según las fuentes, **cuando** termina la extracción, **entonces** ve "No se identificaron sorteos en el período consultado" † y no se ofrece descargar un archivo.
11. **AC-1.11** — **Dado** una extracción en curso, **cuando** el administrador recarga la pantalla, **entonces** sigue viendo el avance de esa extracción y no se inicia otra (FR-003).
12. **AC-1.12** — **Dado** cualquier sorteo de la extracción, **cuando** el administrador abre su detalle, **entonces** ve, en "Fuentes consultadas", el resultado del intento de cada fuente (RN-08) con su dirección consultada como enlace (D-33) y, por cada dato, su valor normalizado o su estado. Las fuentes que respaldan cada dato no se repiten junto al dato: figuran en la procedencia del archivo (FR-012, D-23).
13. **AC-1.13** — **Dado** el detalle de cualquier sorteo, **cuando** el administrador pulsa la dirección consultada de una fuente en "Fuentes consultadas", **entonces** se abre en una pestaña nueva la página de esa fuente para ese sorteo (p. ej. https://quiniya.com.ar/sorteos/3398); el detalle no muestra el enlace "Ver extracto oficial (Lotería de Santa Fe)" (FR-007; actualizado el 23/11/2026, D-33).
16. **AC-1.16** — **Dado** que las fuentes informan los sorteos 3422 y 3424 dentro del período y ninguna informa el 3423, **cuando** termina la extracción, **entonces** el 3423 figura entre los identificados como "No recuperado", con el motivo "Ninguna fuente informa este número de sorteo" †, y el resumen advierte el hueco en la numeración (RN-05).
17. **AC-1.17** — **Dado** el período del 01/06/2014 al 31/12/2014, anterior en parte a la cobertura de todas las fuentes, **cuando** termina la extracción, **entonces** el resumen muestra "Las fuentes no cubren el período anterior al dd/mm/aaaa" †, con la fecha del sorteo más antiguo disponible, y solo se identifican los sorteos cubiertos (RN-05).
14. **AC-1.14** — **Dado** que existen extracciones anteriores, **cuando** un administrador abre la pantalla, **entonces** ve el listado "Extracciones anteriores" †, de la más reciente a la más antigua. Cada una muestra, en la columna "Fecha", la fecha y hora de inicio, y además quién la ejecutó, el período consultado y su estado (RN-44, D-24).
15. **AC-1.15** — **Dado** una extracción terminada que ejecutó otro administrador, **cuando** un administrador la abre desde el listado, **entonces** ve su resumen y su detalle por sorteo y puede descargar su archivo. El archivo tiene el mismo contenido que el que se pudo descargar al terminar la extracción (RN-44).
18. **AC-1.18** — **Dado** una extracción terminada en "Extracciones anteriores", propia o de otro administrador, **cuando** el administrador abre su menú de acciones (⋮), elige "Eliminar" y confirma en "Eliminar extracción", **entonces** vuelve a la pantalla con el mensaje "Extracción eliminada", la extracción ya no figura en el listado y su página, el detalle de sus sorteos y su archivo responden "La página que buscás no existe". Si cancela, nada cambia (RN-44, D-24).
19. **AC-1.19** — **Dado** una extracción en curso, **cuando** el administrador mira "Extracciones anteriores", **entonces** esa fila no ofrece "Eliminar"; si se pide eliminarla igualmente, ve "No se puede eliminar una extracción en curso" y la extracción sigue (RN-44, D-24).
20. **AC-1.20** — **Dado** el formulario del período, **cuando** el administrador pulsa el ícono de calendario de "Fecha de inicio" o de "Fecha de finalización", **entonces** se despliega un calendario para elegir la fecha; **cuando** hace clic en el campo y escribe 01012025 con el teclado (también el numérico), **entonces** el campo muestra 01/01/2025. El campo se valida igual con o sin JavaScript (RN-01 a RN-04, D-25, D-27).
21. **AC-1.21** — **Dado** una extracción en curso con el total de sorteos identificado, **cuando** el administrador mira la pantalla, **entonces** ve, junto a "N de M sorteos procesados", una barra de progreso llena en la proporción N/M, que avanza a medida que se procesan los sorteos; mientras se identifican los sorteos no ve la barra (FR-003, D-26).

---

### Historia de usuario 2 — Recuperar desde varias fuentes con respaldo (Prioridad: P2)

Como administrador, quiero que la extracción consulte todas las fuentes y use las demás cuando una falla, no tiene el sorteo o lo tiene incompleto, para recuperar la mayor cantidad posible de información verificable.

**Por qué esta prioridad**: Aumenta la cobertura y permite detectar errores de las fuentes. La historia 1 ya entrega valor con una sola fuente.

**Prueba independiente**: En el entorno de prueba, con una fuente forzada a fallar, se extrae un período y se verifica que los sorteos se recuperan de las demás fuentes.

**Criterios de aceptación**:

1. **AC-2.1** — **Dado** que terminó una extracción, **cuando** el administrador mira las fuentes utilizadas, **entonces** ve cada fuente configurada con la cantidad de sorteos que aportó y la cantidad de intentos fallidos por tipo (RN-08, RN-33).
2. **AC-2.2** — **Dado** que una fuente no responde, **cuando** se extrae un sorteo, **entonces** el detalle muestra esa fuente como "No disponible" † en "Fuentes consultadas" y los datos del sorteo se toman de las fuentes que sí respondieron, como lo indica la procedencia del archivo (RN-09, D-23).
3. **AC-2.3** — **Dado** que una fuente informa que el sorteo no existe, **cuando** se extrae, **entonces** el detalle muestra "No encontrado" † para esa fuente y los datos se toman de las demás. En F2, que responde igual ante un sorteo inexistente y ante una falla, se muestra "No disponible o no encontrado" † (RN-08).
4. **AC-2.4** — **Dado** que una fuente cambió su estructura y la aplicación no reconoce los datos del sorteo, **cuando** se extrae, **entonces** el detalle muestra "Estructura no reconocida" † para esa fuente, no se toma ningún dato de esa página y los datos se toman de las demás fuentes (RN-10).
5. **AC-2.5** — **Dado** que una fuente presenta el sorteo con datos faltantes, **cuando** se extrae, **entonces** el detalle muestra "Incompleto" † para esa fuente, indica qué falta y lo que falta se completa con lo que aportan las demás fuentes, si lo informan (RN-09).
6. **AC-2.6** — **Dado** un sorteo anterior a la cobertura histórica de una fuente, **cuando** se extrae, **entonces** esa fuente figura como "Fuera de cobertura" † y no se cuenta como intento fallido (RN-08).
7. **AC-2.7** — **Dado** que ninguna fuente permite recuperar un sorteo, **cuando** termina la extracción, **entonces** el sorteo figura como "No recuperado" †, con el motivo de cada fuente, y no se muestra ningún número ni importe para él (RN-31).
8. **AC-2.8** — **Dado** que una fuente tarda en responder más que el límite de espera, **cuando** se extrae, **entonces** la extracción no queda detenida: esa fuente figura como "No disponible" para ese sorteo y el avance continúa (NFR-006).
9. **AC-2.9** — **Dado** que un sitio rechaza las consultas, por ejemplo con una verificación anti-robots, **cuando** se extrae, **entonces** sus intentos figuran como "No disponible", los datos se toman de las demás fuentes y la aplicación no intenta eludir el rechazo (NFR-005).
10. **AC-2.10** — **Dado** que una fuente cambió su estructura y queda "Estructura no reconocida" en todos los sorteos que cubre, **cuando** termina la extracción, **entonces** el resumen muestra esa fuente con la marca "Requiere mantenimiento" † (RN-10).
11. **AC-2.11** — **Dado** que numerosganadores.com.ar y quiniya.com.ar informan todos los datos esperados de un sorteo, **cuando** se extrae, **entonces** quini-6-resultados.com.ar no se consulta para ese sorteo y el detalle la muestra como "No requerida". **Dado** que a ambas les falta un dato esperado o no tienen el sorteo, **cuando** se extrae, **entonces** se consulta quini-6-resultados.com.ar, si cubre el sorteo, y lo que aporte completa los datos (RN-09, D-14). **Dado** que difieren en un dato, **cuando** se extrae, **entonces** también se consulta quini-6-resultados.com.ar, con la fecha que informan las otras dos si el sorteo no figura en su listado (D-21).

---

### Historia de usuario 3 — Normalizar y validar números y premios (Prioridad: P1)

Como administrador, quiero que los datos de todas las fuentes queden en una estructura común y validada, para que el archivo no confunda pozo con premio individual, ni dato desconocido con cero.

**Por qué esta prioridad**: Es la exactitud que exige Const. VIII. Un archivo que mezcle conceptos económicos es inutilizable para una ingesta.

**Prueba independiente**: En el entorno de prueba, se extraen sorteos con vacantes, ganadores, datos faltantes e importes inválidos, y se comparan la pantalla y el archivo con los valores esperados.

**Criterios de aceptación**:

1. **AC-3.1** — **Dado** que las fuentes nombran la misma modalidad como "SORTEO TRADICIONAL", "TRADICIONAL" o "Tradicional Primer Sorteo", **cuando** se extrae, **entonces** el detalle y el archivo la muestran como "Tradicional". La tabla que F1 rotula "LA SEGUNDA DEL QUINI 6 REVANCHA" figura como "Revancha", y "POZO EXTRA" figura como "Pozo Extra" (RN-11, D-15).
2. **AC-3.2** — **Dado** que una fuente publica "02 01 39 13 10 38" y otra "01 - 02 - 10 - 13 - 38 - 39", **cuando** se extrae, **entonces** la modalidad muestra 01, 02, 10, 13, 38, 39, con dos dígitos y en orden ascendente, y no se registra una discrepancia (RN-13, RN-27).
3. **AC-3.3** — **Dado** un sorteo con Premio Extra, **cuando** el administrador abre el archivo, **entonces** Pozo Extra figura con sus datos de premios y con las columnas `numero_1` a `numero_6` como "No corresponde"; sus números van en la columna `numeros_pozo_extra` (RN-12, AC-3.17).
4. **AC-3.4** — **Dado** que una fuente informa una categoría como "Vacante" con el importe 1.100.000.000, **cuando** se extrae, **entonces** la categoría figura con 0 ganadores, pozo destinado $ 1.100.000.000,00, importe individual $ 0,00 y estado "Vacante" (RN-15, RN-17, RN-19, D-16).
5. **AC-3.5** — **Dado** que una fuente secundaria informa 18 ganadores y "Premio para cada uno 3.013.912", **cuando** se extrae, **entonces** la categoría figura con 18 ganadores, importe individual $ 3.013.912,00, pozo destinado $ 54.250.416,00 y estado "Con ganadores"; en el archivo, la procedencia del pozo dice "Calculado: importe individual × ganadores" (RN-17, RN-18, D-16, D-23).
6. **AC-3.6** — **Dado** cualquier categoría con ganadores, **cuando** se abre el archivo, **entonces** su pozo destinado figura calculado (o publicado, si una fuente lo publica) y su importe individual figura en un lugar distinto y rotulado, sin mezclarse; la procedencia del pozo calculado dice "Calculado: importe individual × ganadores". Si falta el importe individual, el pozo queda "No disponible" y el sorteo no queda "Recuperado parcialmente" solo por ese pozo (RN-17, RN-31, D-16).
7. **AC-3.7** — **Dado** que ninguna fuente informa la cantidad de ganadores de una categoría, **cuando** se extrae, **entonces** la categoría figura con ganadores "No disponible", importe individual "No disponible" y estado "Pendiente" †. Nunca figura como 0 ganadores ni como "Vacante" (RN-19, RN-20).
8. **AC-3.8** — **Dado** que una fuente publica un importe con formato inválido, como «1,234,567», **cuando** se extrae, **entonces** ese importe figura como "No disponible", el detalle muestra la observación "Importe con formato no reconocido: «1,234,567»" † y el sorteo no figura como "Recuperado" (RN-16). Un importe con cuatro dígitos en su último grupo se corrige según AC-3.16, uno con tres o más decimales según AC-3.18, uno con puntos de miles mal puestos según AC-3.19 y uno con coma en todos los separadores según AC-3.20 (ejemplo cambiado el 23/11/2026, D-32).
9. **AC-3.9** — **Dado** que una fuente publica una extracción con un número repetido, con un número fuera de 00 a 45 o con una cantidad de números distinta de seis, **cuando** se extrae, **entonces** esos números no se usan, el detalle muestra la observación con el motivo y la aplicación no los corrige (RN-24).
10. **AC-3.10** — **Dado** que una fuente informa Siempre Sale con 5 aciertos y 17 ganadores, **cuando** se extrae, **entonces** la categoría ganadora de Siempre Sale figura con 5 aciertos y 17 ganadores (RN-14, RN-26).
11. **AC-3.11** — **Dado** un sorteo con fecha anterior al 18/06/2024, **cuando** se extrae, **entonces** su detalle muestra el aviso "Reglas del período no verificadas" † y sus categorías se registran tal como las informan las fuentes (RN-25).
12. **AC-3.12** — **Dado** que ninguna fuente informa una modalidad de un sorteo, **cuando** se extrae, **entonces** esa modalidad figura como "No informada por las fuentes" †, nunca como inexistente, y el sorteo no figura como "Recuperado" (RN-25, D-04).
13. **AC-3.13** — **Dado** que una fuente publica una lista de números de Premio Extra distinta de la unión de sus propias tres extracciones, **cuando** se extrae, **entonces** el detalle muestra la observación "Los números de Premio Extra de la fuente no coinciden con sus extracciones" † (RN-12).
14. **AC-3.14** — **Dado** una categoría con 0 ganadores y un importe individual publicado como "0,00", **cuando** se extrae, **entonces** el importe individual figura como $ 0,00 (RN-20, D-16).
15. **AC-3.15** — *Quitado el 20/11/2026 (D-22)*: la acumulación y el importe trasladado ya no se registran.
16. **AC-3.16** — **Dado** que una fuente publica el importe individual «410.1156,25», **cuando** se extrae, **entonces** el importe figura como $ 410.115,63, el detalle muestra la nota informativa "Importe corregido: «410.1156,25» → $ 410.115,63" y esa nota sola no cambia el estado del sorteo (RN-16, D-18).
17. **AC-3.17** — **Dado** un sorteo con los números de Tradicional, La Segunda y Revancha recuperados, **cuando** el administrador abre el detalle, **entonces** Pozo Extra muestra como números la unión de esos tres conjuntos, sin repetidos y en orden ascendente, con la marca "Calculado: unión de Tradicional, La Segunda y Revancha"; en el archivo esos números figuran en la columna `numeros_pozo_extra` de las filas de Pozo Extra. Si falta alguno de los tres conjuntos, figuran "No disponible" (RN-12, D-19).
18. **AC-3.18** — **Dado** que las fuentes publican el importe individual «1.278.143,114» (sorteo 3250), **cuando** se extrae, **entonces** el importe figura como $ 1.278.143,11, el detalle muestra la nota informativa "Importe corregido: «1.278.143,114» → $ 1.278.143,11" y no la observación "Importe con formato no reconocido", y esa nota sola no cambia el estado del sorteo (RN-16, D-20).
19. **AC-3.19** — **Dado** que las fuentes publican el importe individual «1.0867.330» (sorteo 3383, Tradicional, Segundo Premio) o el pozo de una vacante «2.57.2821.792» (sorteo 3415, Revancha), **cuando** se extrae, **entonces** el importe figura como $ 10.867.330,00 o $ 2.572.821.792,00, el detalle muestra la nota informativa "Importe corregido: «1.0867.330» → $ 10.867.330,00" y no la observación "Importe con formato no reconocido", el sorteo no queda "Recuperado parcialmente" por ese importe y esa nota sola no cambia su estado (RN-16, D-31).
20. **AC-3.20** — **Dado** que las tres fuentes publican el importe individual «494,443,71» (sorteo 3398, 09/08/2026, Tradicional, Segundo Premio), **cuando** se extrae, **entonces** el importe figura como $ 494.443,71, el detalle muestra la nota informativa "Importe corregido: «494,443,71» → $ 494.443,71" y no la observación "Importe con formato no reconocido" ni el motivo "Falta: Tradicional: Segundo Premio: importe individual", y esa nota sola no cambia el estado del sorteo (RN-16, D-32).

---

### Historia de usuario 4 — Detectar discrepancias y conservar la procedencia (Prioridad: P2)

Como administrador, quiero ver qué fuentes coinciden y en qué datos difieren, sin que la aplicación elija un valor por su cuenta, para revisar los casos dudosos con la fuente oficial.

**Por qué esta prioridad**: Protege la trazabilidad de Const. IX. Requiere más de una fuente (historia 2).

**Prueba independiente**: En el entorno de prueba, dos fuentes publican valores distintos para un mismo dato y se verifican la pantalla y el archivo.

**Criterios de aceptación**:

1. **AC-4.1** — **Dado** que una fuente publica 5.015 y otra 5.547,85 como importe individual de la misma categoría (una diferencia de al menos el 1 %), **cuando** se extrae, **entonces** el sorteo figura "Con inconsistencias" †. El detalle muestra los dos valores con su fuente, el valor consolidado figura como "Sin determinar" † y la columna de discrepancias del archivo cita los dos valores con su fuente (RN-27, RN-30, RN-43).
2. **AC-4.2** — **Dado** que una fuente informa que una categoría quedó vacante y otra, que normalmente informa esa categoría, no la presenta, **cuando** se extrae, **entonces** el detalle muestra una discrepancia de tipo "Omisión" † con la procedencia de cada dato (RN-28).
3. **AC-4.3** — **Dado** que una fuente no publica un dato por diseño, como el pozo destinado de una categoría con ganadores en las secundarias, **cuando** se extrae, **entonces** esa ausencia no genera una discrepancia (RN-28).
4. **AC-4.4** — **Dado** que dos fuentes informan fechas distintas para el mismo número de sorteo, **cuando** se extrae, **entonces** el sorteo figura "Con inconsistencias" y el detalle muestra las dos fechas con su fuente (RN-22).
5. **AC-4.5** — **Dado** que numerosganadores.com.ar publica 756.099.026 y quiniya.com.ar 756.099.025,92 para el mismo importe (sorteo 3233), **cuando** se extrae, **entonces** el importe figura como $ 756.099.026,00 respaldado por las dos fuentes, sin discrepancia ni nota, porque difieren en menos de $ 1,00 (D-28). **Dado** que, sin centavos, difieren menos del 1 %, **cuando** se extrae, **entonces** el importe figura con el valor sin centavos de numerosganadores.com.ar, el detalle muestra la nota informativa "Diferencia de centavos o redondeo (menor al 1 %)" con los dos valores y su fuente, y esa nota no deja el sorteo "Con inconsistencias" (RN-30, D-17).
6. **AC-4.6** — **Dado** que dos o más fuentes coinciden en un dato, **cuando** el administrador abre el detalle del sorteo, **entonces** ve ese dato con la lista de fuentes que coinciden (RN-27).
7. **AC-4.7** — **Dado** que una fuente aporta los números y otra los premios de un sorteo, sin diferencias entre ellas, **cuando** se extrae, **entonces** cada dato muestra la fuente de la que proviene, el sorteo se identifica como "Combina fuentes" † y puede figurar "Recuperado" (RN-29).
8. **AC-4.8** — **Dado** que numerosganadores.com.ar aporta todos los datos de un sorteo, **cuando** se extrae, **entonces** el detalle muestra que también se consultó quiniya.com.ar, si cubre ese sorteo. Los datos que solo informó una fuente figuran con la marca "Sin corroborar" †, en la pantalla y en el archivo (RN-09, RN-32).
9. **AC-4.9** — **Dado** que numerosganadores.com.ar informa 14 ganadores y quiniya.com.ar 15 para la misma categoría, y quini-6-resultados.com.ar no permite desempatar (no tiene el sorteo o informa un tercer valor), **cuando** se extrae, **entonces** la categoría figura con 14 ganadores, el detalle muestra la discrepancia "Valor distinto" con los dos valores y su fuente, y el sorteo figura "Con inconsistencias". Los importes de la categoría solo se comparan entre las fuentes que coinciden en los ganadores (RN-07, RN-27, D-14).
10. **AC-4.10** — **Dado** el sorteo 3235, en el que numerosganadores.com.ar informa vacante el Segundo Premio de Tradicional y quiniya.com.ar y quini-6-resultados.com.ar informan 13 ganadores y $ 1.230.980,68, **cuando** se extrae, **entonces** la categoría figura con 13 ganadores, importe individual $ 1.230.980,68 y pozo calculado, el detalle muestra la nota informativa "Resuelto por coincidencia de 2 de 3 fuentes" con lo que publicó cada fuente, y esa diferencia no deja el sorteo "Con inconsistencias" (RN-07, D-21).
11. **AC-4.11** — **Dado** el sorteo 3308, en el que numerosganadores.com.ar publica Siempre Sale sin ganadores (dato inválido) y quiniya.com.ar y quini-6-resultados.com.ar informan 21 ganadores con 5 aciertos y $ 14.777.032,50 cada uno, **cuando** se extrae, **entonces** Siempre Sale figura con esos valores, la observación "Siempre Sale: la categoría ganadora informada no es válida…" de numerosganadores.com.ar queda como informativa y no deja el sorteo "Con inconsistencias" (RN-07, RN-26, D-21).
12. **AC-4.12** — **Dado** el sorteo 2918, en el que el pozo destinado de Revancha es $ 47.930.930,50 en numerosganadores.com.ar, $ 74.669.257,73 en quiniya.com.ar y $ 47.930.930,00 en quini-6-resultados.com.ar, **cuando** se extrae, **entonces** el pozo figura como $ 47.930.930,00, respaldado por numerosganadores.com.ar y quini-6-resultados.com.ar, con la nota informativa "Resuelto por coincidencia de 2 de 3 fuentes" y lo que publicó cada una, y esa diferencia no deja el sorteo "Con inconsistencias" (RN-30, D-21, D-28).
13. **AC-4.13** — **Dado** el sorteo 3425, en el que numerosganadores.com.ar y quiniya.com.ar publican Siempre Sale con 5 aciertos y 0 ganadores (dato inválido) y quini-6-resultados.com.ar informa 6 ganadores y $ 56.785.482 cada uno, **cuando** se extrae, **entonces** Siempre Sale figura con 6 ganadores y ese importe individual, marcados "Sin corroborar", el pozo figura calculado, las observaciones "Siempre Sale: la categoría ganadora informada no es válida…" de las dos primeras quedan como informativas y no dejan el sorteo "Con inconsistencias" (RN-07, RN-26, D-29).
14. **AC-4.14** — **Dado** el sorteo 3425, en el que numerosganadores.com.ar y quiniya.com.ar informan 772 ganadores de Pozo Extra y $ 259.067 cada uno y quini-6-resultados.com.ar, además, el texto "55 millones de pesos", **cuando** se extrae, **entonces** el pozo de Pozo Extra figura como $ 199.999.724,00 (importe individual × ganadores), con la procedencia "Calculado: importe individual × ganadores" y sin la marca "Sin corroborar" (RN-17, RN-18, D-30).

---

### Historia de usuario 5 — Descargar el CSV unificado (Prioridad: P1)

Como administrador, quiero descargar un único archivo CSV con los datos normalizados, sus estados y su procedencia, para usarlo en una futura ingesta y para revisarlo con una planilla de cálculo.

**Por qué esta prioridad**: Es el producto final de la feature.

**Prueba independiente**: Se descarga el archivo de una extracción terminada, se abre con una planilla de cálculo y se compara con el resumen y el detalle de la pantalla.

**Criterios de aceptación**:

1. **AC-5.1** — **Dado** una extracción terminada con al menos un sorteo identificado, **cuando** el administrador pulsa "Descargar CSV" †, **entonces** obtiene un archivo cuyo nombre incluye el período consultado (FR-014).
2. **AC-5.2** — **Dado** el archivo descargado, **cuando** se importa en una planilla de cálculo indicando codificación UTF-8 y separador coma, **entonces** los acentos y símbolos se ven correctamente, como en "Tradicional – Primer Sorteo", la primera fila tiene los encabezados del contrato, las fechas figuran como 2026-11-15 y los importes como 1100000000.00 (RN-34, RN-38).
3. **AC-5.3** — **Dado** el archivo y el resumen de la misma extracción, **cuando** se comparan, **entonces** cada sorteo identificado figura en el archivo con el mismo estado que en la pantalla, y las cantidades por estado coinciden (RN-35, RN-39).
4. **AC-5.4** — **Dado** cualquier dato del archivo, **cuando** se lo revisa, **entonces** se puede identificar de qué fuente proviene, la dirección consultada y la fecha y hora de la consulta (RN-35).
5. **AC-5.5** — **Dado** el archivo, **cuando** se lo revisa, **entonces** no hay dos filas con el mismo sorteo, la misma modalidad y la misma categoría (RN-37).
6. **AC-5.6** — **Dado** el archivo, **cuando** se revisan sus encabezados, **entonces** no hay ninguna columna de precio del cartón (RN-35).
7. **AC-5.7** — **Dado** una categoría vacante, una con ganadores sin importe individual informado y una sin información, **cuando** se revisa el archivo, **entonces** se distinguen sin ambigüedad "No corresponde", "No disponible" y "Sin determinar", y ninguna celda vacía representa un cero (RN-36).
8. **AC-5.8** — **Dado** un sorteo "No recuperado", **cuando** se revisa el archivo, **entonces** figura en una sola fila con su número, su estado y sus motivos, sin números ni importes. **Dado** un sorteo "Recuperado parcialmente", **cuando** se revisa el archivo, **entonces** figuran sus filas con los datos faltantes como "No disponible", sin valores inventados (RN-39).
9. **AC-5.9** — **Dado** que una fuente publicó un texto que empieza con "=", "+", "-" o "@", **cuando** se abre el archivo con una planilla de cálculo, **entonces** ese texto se ve como texto y no se ejecuta como fórmula (NFR-010).
10. **AC-5.10** — **Dado** una extracción terminada, **cuando** el administrador descarga el archivo dos veces, **entonces** ambos archivos tienen el mismo contenido (FR-014).

---

### Historia de usuario 6 — Acceso restringido y sin ingesta (Prioridad: P1)

Como responsable del proyecto, quiero que solo los administradores usen la extracción y que nada extraído llegue a los datos de la aplicación, para proteger la exactitud de la información publicada.

**Por qué esta prioridad**: Es una condición de seguridad (Const. IV) y de exactitud (Const. VIII y IX).

**Prueba independiente**: Con una matriz de accesos y una extracción que incluye un concurso ya publicado y uno inexistente en la aplicación, se verifica que nada cambia.

**Criterios de aceptación**:

1. **AC-6.1** — **Dado** un usuario registrado sin permiso de administrador, **cuando** intenta abrir la pantalla, iniciar una extracción o descargar un archivo, desde la navegación o con una dirección directa, **entonces** ve "No tenés permisos para acceder a esta sección" y no se muestra ni se genera información (RN-42; mismo mensaje que [001] AC-2.11).
2. **AC-6.2** — **Dado** un visitante sin sesión, **cuando** intenta acceder con una dirección directa, **entonces** se le pide iniciar sesión. Si inicia sesión con una cuenta sin permiso de administrador, ve el mensaje de AC-6.1 (RN-42).
3. **AC-6.3** — **Dado** que el concurso 3426 no está registrado en la aplicación, **cuando** un administrador extrae un período que lo incluye, **entonces** la consulta pública sigue mostrando "No hay información del concurso N.º 3426" y el listado de concursos de administración no lo incluye (RN-41).
4. **AC-6.4** — **Dado** un concurso publicado en la aplicación cuyos valores difieren de los extraídos, **cuando** termina la extracción, **entonces** la consulta pública muestra los mismos valores que antes, sin "Corregido el …" ni "Información en revisión", y su historial de cambios no tiene entradas nuevas (RN-41).
5. **AC-6.5** — **Dado** un usuario con jugadas en concursos del período extraído, **cuando** termina la extracción, **entonces** sus jugadas y sus comparaciones se muestran igual que antes (RN-41).
6. **AC-6.6** — **Dado** un usuario registrado sin permiso de administrador, **cuando** intenta abrir el listado de extracciones anteriores, una extracción conservada o su archivo con una dirección directa, **entonces** ve el mensaje de AC-6.1 y no se muestra información de ninguna extracción (RN-42, RN-44).

---

### Casos límite (Edge Cases)

| Área | Caso límite | Cobertura |
|------|-------------|-----------|
| Período | Fecha de inicio posterior a la de finalización | AC-1.3, RN-02 |
| Período | Fecha vacía o inválida | AC-1.4 |
| Período | Fecha de finalización futura | AC-1.5, RN-03 |
| Período | Período más largo que el máximo | AC-1.6, RN-04 |
| Período | Sorteos en el primer y el último día | AC-1.7, RN-01 |
| Período | Período sin sorteos | AC-1.10 |
| Período | Sorteos "especiales" o fuera de los días habituales | RN-05 |
| Período | Número intermedio que ninguna fuente informa | AC-1.16, RN-05 |
| Período | Período anterior a la cobertura de todas las fuentes | AC-1.17, RN-05 |
| Fuentes | Fuente que no responde o tarda demasiado | AC-2.2, AC-2.8, NFR-006 |
| Fuentes | Sitio que rechaza las consultas automatizadas | AC-2.9, NFR-005 |
| Fuentes | Sorteo inexistente en una fuente | AC-2.3 |
| Fuentes | Fuente que no distingue "no existe" de "falla" | AC-2.3, RN-08 |
| Fuentes | Cambio de estructura de una fuente | AC-2.4, AC-2.10, RN-10 |
| Fuentes | Sorteo fuera de la cobertura histórica de una fuente | AC-2.6 |
| Fuentes | Ninguna fuente recupera el sorteo | AC-2.7, RN-31 |
| Fuentes | Números en una fuente y premios en otra | AC-4.7, RN-29 |
| Normalización | Rótulos distintos para la misma modalidad | AC-3.1, RN-11 |
| Normalización | Rótulo de Revancha que contiene "La Segunda" | AC-3.1, RN-11 |
| Normalización | Números en distinto orden | AC-3.2, RN-13 |
| Normalización | Premio Extra presentado con números propios | AC-3.3, AC-3.13, RN-12 |
| Normalización | Columna "Premio" con dos significados | AC-3.4, AC-3.5, RN-17 |
| Normalización | Importe con formato inválido | AC-3.8, RN-16 |
| Normalización | Importe sin centavos | AC-4.5, RN-16, D-10 |
| Normalización | Categoría fuera del catálogo vigente | RN-14 |
| Cotejo | Revisión manual con el extracto oficial | AC-1.13, FR-007 |
| Normalización | Importe "0,00" con 0 ganadores | AC-3.14, RN-20 |
| Validación | Números repetidos, fuera de rango o en cantidad distinta de seis | AC-3.9, RN-24 |
| Validación | Fechas distintas entre fuentes | AC-4.4, RN-22 |
| Validación | Número y fecha no correlativos | RN-23 |
| Validación | Modalidad ausente en todas las fuentes | AC-3.12, RN-25, D-04 |
| Validación | Sorteo anterior al 18/06/2024 | AC-3.11, RN-25 |
| Validación | Siempre Sale o Premio Extra con categoría ganadora inválida | RN-26 |
| Discrepancias | Valores distintos entre fuentes | AC-4.1, RN-27 |
| Discrepancias | Dato informado por una sola fuente | AC-4.8, RN-32 |
| Discrepancias | Dato presente en una fuente y omitido en otra | AC-4.2, RN-28 |
| Discrepancias | Dato que una fuente no publica por diseño | AC-4.3, RN-28 |
| Discrepancias | Diferencias de centavos | AC-4.5, RN-30, D-10 |
| Pozos | Desconocido frente a cero frente a vacante | AC-3.7, AC-5.7, RN-19, RN-20 |
| Pozos | Pozo acumulado sin evolución histórica: no se registra (D-22) | RN-19 |
| Archivo | Sorteos parciales o no recuperados | AC-5.8, RN-39 |
| Archivo | Valores en conflicto entre fuentes | AC-4.1, RN-43 |
| Archivo | Texto de una fuente que parece una fórmula | AC-5.9, NFR-010 |
| Archivo | Duplicados | AC-5.5, RN-37 |
| Acceso | Usuario sin permiso o visitante | AC-6.1, AC-6.2 |
| Aislamiento | Concurso inexistente o ya publicado en la aplicación | AC-6.3, AC-6.4 |
| Uso | Dos extracciones a la vez del mismo administrador | AC-1.11, Supuestos |
| Uso | Descarga posterior de una extracción de otro administrador | AC-1.15, RN-44 |
| Acceso | Listado o archivo de extracciones sin permiso | AC-6.6 |

---

## Requisitos (Requirements) *(obligatorio)*

### Requisitos funcionales (Functional Requirements)

**Pantalla y período**

- **FR-001**: El sistema DEBE ofrecer la pantalla «Extracción histórica de sorteos», accesible desde la sección de administración y solo para administradores. *(US1, US6; RN-42)*
- **FR-002**: El administrador DEBE poder ingresar una fecha de inicio y una de finalización, inclusivas, que el sistema valida según RN-01 a RN-04. *(US1)*
- **FR-003**: Al iniciar una extracción, el sistema DEBE mostrar su estado y su avance (sorteos procesados sobre sorteos identificados) hasta que termine, también si el administrador recarga la pantalla. Mientras se identifican los sorteos, muestra "Identificando los sorteos del período…" en lugar del avance. Con JavaScript, el avance se actualiza solo cada 5 segundos; sin JavaScript, al recargar. Con el total conocido, el avance incluye una barra de progreso con la misma proporción. *(US1; Clarifications 19/11/2026, planificación; 21/11/2026, D-26)*
- **FR-004**: El sistema DEBE identificar los sorteos del período según RN-05. *(US1; D-06)*

**Consulta de fuentes**

- **FR-005**: El sistema DEBE consultar, para cada sorteo, las fuentes en el orden de prioridad de RN-07: siempre numerosganadores.com.ar y quiniya.com.ar, y quini-6-resultados.com.ar solo cuando hace falta (RN-09). Compara los datos de las fuentes consultadas; una falla, una ausencia o un dato incompleto en una fuente se cubre con lo que aportan las demás. *(US2, US4; Clarifications 18/11/2026 y 20/11/2026)*
- **FR-006**: El sistema DEBE registrar, por cada sorteo y cada fuente, el resultado del intento según RN-08, con la dirección consultada y la fecha y hora de la consulta. *(US2)*
- **FR-007**: El sistema NO DEBE consultar automáticamente el extracto oficial de la Lotería de Santa Fe (F0). Para el cotejo manual, el detalle de cada sorteo DEBE ofrecer, en "Fuentes consultadas", la dirección consultada de cada fuente como enlace a su página, que se abre en una pestaña nueva; no muestra un enlace al extracto oficial. *(US1, US2; Clarifications 18/11/2026; actualizado 23/11/2026, D-33)*

**Normalización, validación y discrepancias**

- **FR-008**: El sistema DEBE normalizar los datos de cada fuente a la estructura común de RN-11 a RN-20. *(US3)*
- **FR-009**: El sistema DEBE validar los datos según RN-21 a RN-26 y registrar cada observación con su motivo. *(US3)*
- **FR-010**: El sistema DEBE comparar los datos entre fuentes y registrar las coincidencias y discrepancias según RN-27 a RN-30, sin elegir un valor cuando difieren. *(US4)*
- **FR-011**: El sistema NO DEBE completar, estimar ni calcular datos faltantes, salvo los cálculos aprobados el 20/11/2026, que siempre se marcan como calculados: el pozo destinado de una categoría con ganadores, el importe individual 0,00 de una categoría vacante y los números de Pozo Extra (RN-12, RN-18). *(US3; RN-18; Clarifications 20/11/2026)*

**Resumen y detalle**

- **FR-012**: Al terminar, el sistema DEBE mostrar el resumen de RN-33 y la lista de sorteos que requieren revisión. Para cada sorteo, el administrador DEBE poder ver su detalle: resultado por fuente, valores normalizados, estados, coincidencias, discrepancias y observaciones. *(US1, US2, US4)*
- **FR-013**: El sistema DEBE clasificar cada sorteo según RN-31. *(US1, US2)*

**Archivo CSV**

- **FR-014**: El administrador DEBE poder descargar, tras una extracción terminada con al menos un sorteo identificado, un archivo CSV que respete RN-34 a RN-39. Descargas sucesivas de la misma extracción DEBEN tener el mismo contenido. El archivo tiene una fila por sorteo, modalidad y categoría, con los datos consolidados (RN-43). *(US5; Clarifications 18/11/2026)*
- **FR-015**: El sistema DEBE conservar todas las extracciones por tiempo indefinido, según RN-44, y ofrecer a cualquier administrador el listado de extracciones anteriores, con acceso a su resumen, su detalle y su archivo, y la opción de eliminar las terminadas con confirmación previa. *(US1, US5; Clarifications 18/11/2026 y 20/11/2026, D-24)*

**Aislamiento**

- **FR-016**: La extracción NO DEBE crear ni modificar concursos, modalidades, números, premios, estados de validación, jugadas ni registros de cambio de la aplicación (RN-41). *(US6)*

### Requisitos de calidad (no funcionales)

- **NFR-001 (Localización)**: La pantalla cumple Const. VII: textos en español de Argentina, fechas dd/mm/aaaa, importes $ 1.234,56 y números con dos dígitos. El CSV es un contrato de datos y no es contenido visible en el sentido de Const. VII: usa el formato técnico de RN-38 (Clarifications 18/11/2026). Sus textos, como los nombres de modalidades y los estados, siguen en español.
- **NFR-002 (Adaptabilidad)**: La pantalla se usa sin desplazamiento horizontal desde 360 px de ancho, como [001] NFR-002.
- **NFR-003 (Accesibilidad)**: La pantalla cumple WCAG 2.1 AA. Los estados (recuperado, parcial, inconsistente, no recuperado) se comunican con texto y no solo con color.
- **NFR-004 (Acceso)**: El permiso se verifica en el servidor en cada solicitud, incluida la descarga. Las páginas y el archivo no quedan guardados en la memoria del navegador, como [001] para las páginas privadas.
- **NFR-005 (Respeto por las fuentes)**: El responsable del proyecto autorizó el 19/11/2026 la consulta automatizada de F1, F2 y F3, cuyas reglas para robots no tienen instrucciones de acceso y que no publican condiciones de uso. El sistema hace como máximo una consulta cada 2 segundos a cada sitio; puede consultar sitios distintos al mismo tiempo. No elude mecanismos de protección, como verificaciones anti-robots o bloqueos: si un sitio rechaza las consultas, ese intento queda "No disponible" y no se insiste por otra vía. Si un sitio publica restricciones en el futuro, el uso se revisa con una nueva aprobación.
- **NFR-006 (Tolerancia a fallas)**: Una fuente que falla o tarda no detiene la extracción. Cada consulta tiene un límite de espera, y la falla de un sorteo o de una fuente no interrumpe el resto.
- **NFR-007 (Precisión monetaria)**: Los importes se conservan con precisión de centavos, sin redondeos ni conversiones que alteren el valor publicado (Const. IX). Excepciones aprobadas el 20/11/2026, siempre con una nota visible: quitar los centavos de un importe ante una diferencia menor al 1 % entre fuentes (RN-30, D-28) y el redondeo a centavos de un importe corregido (RN-16).
- **NFR-008 (Trazabilidad)**: Todo dato del archivo se puede vincular a la fuente, la dirección y la fecha y hora de consulta de las que proviene (Const. IX).
- **NFR-009 (Contrato extensible)**: El archivo declara la versión de su contrato. Agregar un dato en una versión futura no cambia el significado de los datos existentes.
- **NFR-010 (Contenido no confiable)**: El texto de las fuentes se trata como dato no confiable. Se muestra en pantalla sin interpretarse y el archivo no contiene celdas que una planilla de cálculo ejecute como fórmula.
- **NFR-011 (Estados visuales)**: La pantalla muestra estados diferenciados de carga o en curso, éxito, advertencia, error y ausencia de información (Const. X).

### Reglas de negocio

Estado: **Aprobada** = surge directamente del pedido, de la Constitución o de la spec 001, o la propuso el agente y el responsable la aprobó en Clarifications. Al 19/11/2026 no quedan reglas propuestas ni pendientes.

**Período e identificación de sorteos**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-01 | Las fechas de inicio y de finalización son inclusivas. Un sorteo pertenece al período si su fecha está entre ambas, incluidas. Las fechas se interpretan en la zona horaria `America/Argentina/Buenos_Aires`. | Aprobada | US1 |
| RN-02 | La fecha de inicio no puede ser posterior a la de finalización. Ambas son obligatorias y se ingresan como dd/mm/aaaa. | Aprobada | US1 |
| RN-03 | La fecha de finalización no puede ser posterior a la fecha actual. | Aprobada (Clarifications 19/11/2026) | US1 |
| RN-04 | El período no puede superar los 12 meses: la fecha de finalización debe ser anterior a la misma fecha del año siguiente a la de inicio. Por ejemplo, del 01/01/2026 al 31/12/2026 es válido y del 01/01/2026 al 01/01/2027 no lo es. | Aprobada (Clarifications 19/11/2026) | US1 |
| RN-05 | **Identificación por numeración correlativa**: el sistema ubica el primer y el último número de sorteo cuya fecha, informada por las fuentes, cae dentro del período, y considera identificados todos los números entre ambos. Las fechas nunca se deducen por calendario ni por los días habituales de sorteo. Un número intermedio que ninguna fuente informa queda "No recuperado" con el motivo "Ninguna fuente informa este número de sorteo" †, y el resumen lo destaca como hueco en la numeración. Un número cuya fecha informada queda fuera del período no se incluye. F1 se consulta con la fecha que informan las otras fuentes o su propio listado. Si una parte del período es anterior a la cobertura de todas las fuentes, el resumen lo advierte con "Las fuentes no cubren el período anterior al dd/mm/aaaa" †. | Aprobada (Clarifications 19/11/2026) | US1 |

**Fuentes y consulta**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-06 | Las fuentes configuradas forman una lista cerrada y aprobada: F1, F2 y F3, usadas en el orden de prioridad de RN-07. El extracto oficial (F0) no es una fuente consultada: solo se ofrece como enlace de cotejo (FR-007). Cada fuente tiene una ficha con su cobertura histórica, la forma de pedir un sorteo y el significado de cada dato que publica ([analisis-fuentes.md](analisis-fuentes.md)). La página "último sorteo" de F2 no es una fuente independiente. Las fuentes no se configuran desde la interfaz. | Aprobada (Clarifications 18/11/2026 y 19/11/2026) | US2 |
| RN-07 | **Prioridad de fuentes**: 1.ª numerosganadores.com.ar (F2), 2.ª quiniya.com.ar (F3) y 3.ª quini-6-resultados.com.ar (F1). Cuando las fuentes difieren en un dato, se desempata con la tercera fuente: si dos de tres coinciden, ese valor resuelve la diferencia, sin discrepancia y con la nota informativa "Resuelto por coincidencia de 2 de 3 fuentes" (D-21). Sin esa coincidencia, el consolidado toma el valor de la fuente de mayor prioridad que lo informa y la diferencia se registra como discrepancia (RN-27), salvo los importes, que siguen RN-30. Un valor que viola RN-26 no se compara ni cuenta para la coincidencia de 2 de 3 (D-29). El detalle, el resumen y la procedencia listan las fuentes en este orden. | Aprobada (Clarifications 20/11/2026; reemplaza la del 18/11/2026) | US2, US4 |
| RN-08 | Resultado de cada intento por sorteo y fuente: **Obtenido**; **Incompleto** (faltan datos esperados según la ficha); **No encontrado** (la fuente informa que el sorteo no existe); **No disponible** (sin respuesta, error o límite de espera vencido); **No disponible o no encontrado** (la fuente no distingue ambos casos, como F2); **Estructura no reconocida** (RN-10); **Fuera de cobertura** (sorteo anterior a la cobertura de la ficha, no se consulta); **No requerida** (la fuente de respaldo no se consultó porque las fuentes prioritarias aportaron todos los datos esperados, RN-09; no es un intento fallido). | Aprobada (Clarifications 19/11/2026) | US2 |
| RN-09 | Para cada sorteo se consultan siempre numerosganadores.com.ar y quiniya.com.ar, si lo cubren, aunque la primera haya aportado todos los datos. quini-6-resultados.com.ar es la fuente de respaldo: se consulta solo si, con las dos primeras, el sorteo queda "No recuperado", le falta algún dato esperado (RN-31), difieren en algún dato o una publica un dato inválido (D-21); si no, su intento es "No requerida". Como su dirección exige la fecha, se le pide con la fecha de su listado o, si el sorteo no figura en él, con la que informan las otras dos (Clarifications 20/11/2026). El resultado de cada intento se registra según RN-08. Un intento No encontrado, No disponible, Incompleto o Estructura no reconocida no detiene la extracción: los datos se toman de las demás fuentes. | Aprobada (Clarifications 18/11/2026) | US2 |
| RN-10 | Si una página no presenta el número y la fecha del sorteo de forma reconocible, el intento es "Estructura no reconocida" y no se toma ningún dato de ella. Si el sorteo se reconoce pero un bloque tiene un rótulo desconocido, ese bloque no se asigna a ninguna modalidad ni categoría, el intento es "Incompleto" y la observación indica el rótulo. Si una fuente queda "Estructura no reconocida" en todos los sorteos que cubre dentro de la extracción, el resumen la marca "Requiere mantenimiento" †. Adaptar la aplicación a una estructura nueva requiere actualizar la ficha de la fuente con aprobación (D-07). | Aprobada (Clarifications 19/11/2026) | US2 |

**Normalización**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-11 | Las modalidades se normalizan a las cinco del catálogo vigente ([001] RN-13) y en la pantalla de extracción y en el archivo se nombran "Tradicional", "La Segunda", "Revancha", "Siempre Sale" y "Pozo Extra" (Clarifications 20/11/2026). "Pozo Extra" es la modalidad que [001] llama Premio Extra. La equivalencia de rótulos de cada fuente es exacta y está en su ficha. Un rótulo que no figura en la ficha no se asigna por parecido. | Aprobada (Clarifications 19/11/2026) | US3 |
| RN-12 | Pozo Extra no tiene una extracción propia ([001] RN-15, Const. VIII): sus números son la unión de los números consolidados de Tradicional, La Segunda y Revancha, calculada por el sistema y marcada "Calculado: unión de Tradicional, La Segunda y Revancha"; si falta alguno de los tres, quedan "No disponible". Los números que una fuente publique para Pozo Extra solo se usan para verificar que coinciden con la unión de las tres extracciones de esa misma fuente; si no coinciden, se registra una observación. | Aprobada (Clarifications 20/11/2026) | US3 |
| RN-13 | Los números de cada extracción son enteros de 00 a 45. Se registran en orden ascendente y con dos dígitos, y se comparan como conjunto, sin importar el orden de publicación. | Aprobada (Clarifications 19/11/2026) | US3 |
| RN-14 | Las categorías se identifican por modalidad y aciertos con el catálogo de [001] RN-49 a RN-52 y RN-31: Primer Sorteo y La Segunda tienen Primer Premio (6), Segundo Premio (5) y Tercer Premio (4); Revancha tiene una única categoría de 6 aciertos; Siempre Sale y Premio Extra tienen la categoría ganadora con su cantidad de aciertos. Premio Extra puede figurar "Sin ganadores". En sorteos desde el 18/06/2024, una categoría que una fuente publique y no figure en este catálogo no se asigna a ninguna categoría y se registra como observación. Para sorteos anteriores rige RN-25. | Aprobada (Clarifications 19/11/2026, planificación) | US3 |
| RN-15 | La cantidad de ganadores es un entero mayor o igual a cero. "Vacante" y "Pozo vacante" significan 0 ganadores. Un valor vacío, "-" o ausente significa "No disponible". | Aprobada | US3 |
| RN-16 | Los importes publicados en formato argentino (punto de miles, coma decimal, con o sin "$") se convierten a pesos exactos con centavos. Un importe sin decimales se registra con el valor publicado, sin agregarle centavos estimados. Un importe con formato no reconocido, como «1,234,567», se registra como "No disponible" con una observación que cita el texto original. **Corrección de carga**: si el último grupo antes de la coma tiene cuatro dígitos, como «410.1156,25», la coma decimal se corre un lugar a la izquierda y el resultado se redondea a centavos, mitad hacia arriba ($ 410.115,63), con la nota informativa "Importe corregido: «410.1156,25» → $ 410.115,63". Un importe con **tres o más decimales**, como «1.278.143,114», se redondea a centavos, mitad hacia arriba ($ 1.278.143,11), con la misma nota (D-20). Un importe con los **puntos de miles mal puestos** y el último grupo de tres dígitos, como «1.0867.330», reagrupa su parte entera en tríos desde la derecha y conserva los decimales ($ 10.867.330), con la misma nota; D-18 tiene prioridad (D-31). Un importe con la **coma en todos los separadores** (dos o más comas, ningún punto y dos dígitos después de la última), como «494,443,71», toma esos dos dígitos como decimales y el resto como parte entera ($ 494.443,71), con la misma nota (D-32). | Aprobada (Clarifications 19/11/2026 y 20/11/2026; actualizada 23/11/2026, D-31 y D-32) | US3 |
| RN-17 | Cada importe se asigna al concepto que indica la ficha de su fuente. En F1, F2 y F3, el importe de una categoría vacante es su **pozo destinado**, y el de una categoría con ganadores es su **importe individual**; ninguna fuente consultada publica el pozo de una categoría con ganadores, que se calcula según RN-18. Si el concepto de un importe no puede determinarse con la ficha, se registra como "No disponible" con observación. **Pozo de Premio Extra**: ninguna fuente consultada lo publica; se calcula según RN-18. Los textos fijos "55 millones de pesos" de F1 y "85 millones de pesos" de F2 no se toman, porque sus fichas declaran que no publican ese dato; F3 no lo publica (D-30). | Aprobada (Clarifications 19/11/2026 y 19/11/2026, planificación; actualizada 23/11/2026, D-30) | US3 |
| RN-18 | El sistema nunca calcula el importe individual a partir del pozo y los ganadores. **Pozo calculado**: en una categoría con ganadores cuyo pozo no publica ninguna fuente, el pozo destinado es el importe individual consolidado × la cantidad de ganadores, marcado "Calculado: importe individual × ganadores" en la procedencia del archivo (desde D-23, la pantalla no muestra la marca). Si el importe individual o los ganadores no tienen valor, el pozo queda "No disponible", o "Sin determinar" si el importe individual quedó "Sin determinar". En una categoría vacante, el importe individual es 0,00. Excepción aprobada a [001] RN-27 solo para esta feature. | Aprobada (Clarifications 20/11/2026) | US3 |
| RN-19 | **Estado del pozo** de una categoría: "Con ganadores" si hay 1 o más ganadores; "Vacante" si una fuente informa 0 ganadores; "Pendiente" si la cantidad de ganadores no está disponible. El **importe individual** es un valor (0,00 si la categoría está vacante, RN-18) o "No disponible". La acumulación del pozo y el importe trasladado desde sorteos anteriores no se registran (D-22): ninguna fuente los publica y nunca se deducen de que la categoría esté vacante. | Aprobada (Clarifications 19/11/2026; actualizada 20/11/2026, D-22) | US3 |
| RN-20 | Se distinguen cuatro situaciones que nunca se confunden: un **valor**, incluido el cero cuando la fuente lo informa expresamente; **No disponible**, cuando ninguna fuente lo informa; **No corresponde**, cuando el concepto no aplica, como las columnas `numero_1` a `numero_6` de Pozo Extra; y **Sin determinar**, cuando las fuentes difieren. Un dato desconocido nunca se convierte en cero ni en vacante. | Aprobada | US3, US5 |

**Validación**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-21 | El número de sorteo es un entero positivo. En F1, el número y la fecha de la dirección deben coincidir con los de la página. Si no coinciden, el intento es "Estructura no reconocida". | Aprobada (Clarifications 19/11/2026) | US3 |
| RN-22 | La fecha del sorteo es una fecha válida. Si las fuentes informan fechas distintas para un mismo número, se registra una discrepancia. | Aprobada | US3, US4 |
| RN-23 | Correspondencia entre número y fecha: dentro de una extracción, un sorteo de número mayor no puede tener una fecha anterior a la de uno de número menor. Si ocurre, ambos sorteos quedan con una observación de inconsistencia. | Aprobada (Clarifications 19/11/2026) | US3 |
| RN-24 | Cada extracción propia (Primer Sorteo, La Segunda, Revancha y Siempre Sale) tiene exactamente seis números distintos de 00 a 45 ([001] RN-14). Si una fuente no cumple, sus números de esa modalidad no se usan, se registra la observación y el intento es "Incompleto". Los números nunca se corrigen. | Aprobada | US3 |
| RN-25 | Para sorteos desde el 18/06/2024, las categorías informadas se verifican contra RN-14. Para sorteos anteriores, se registran tal como las informan las fuentes, con el aviso "Reglas del período no verificadas" ([001] RN-33). Una categoría que no figura en RN-14 se registra como una categoría propia rotulada "Categoría de N aciertos" (Clarifications 19/11/2026, planificación). Una modalidad ausente en todas las fuentes figura como "No informada por las fuentes" y nunca se interpreta como inexistente en su período (Const. VIII, D-04). | Aprobada | US3 |
| RN-26 | Controles adicionales, tomados de [001] RN-22: la categoría ganadora de Siempre Sale tiene entre 0 y 6 aciertos y al menos un ganador; la de Premio Extra es 6, 5, 4 o "Sin ganadores"; las cantidades y los importes no son negativos; dos extracciones del mismo sorteo con los mismos seis números generan una observación de advertencia. Un aciertos o una cantidad de ganadores de la categoría ganadora que viola este control no participa en la consolidación (RN-07), y tampoco los importes de esa categoría en la misma fuente (D-29). | Aprobada (actualizada 23/11/2026, D-29) | US3 |

**Discrepancias y procedencia**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-27 | Cada dato se compara entre las fuentes que lo informan. Si coinciden, el dato queda con la lista de fuentes coincidentes. Si difieren, se registra una discrepancia, el valor consolidado queda "Sin determinar" y se conservan todos los valores con su fuente. | Aprobada | US4 |
| RN-28 | Hay discrepancia de tipo "Omisión" cuando una fuente que, según su ficha, informa un dato no lo presenta para ese sorteo, mientras otra sí. La ausencia de un dato que una fuente no publica por diseño no es una discrepancia. | Aprobada (Clarifications 19/11/2026) | US4 |
| RN-29 | Si distintas fuentes aportan datos complementarios, como los números de una y los premios de otra, el consolidado conserva la fuente de cada dato y el sorteo queda marcado "Combina fuentes". La combinación cuenta como recuperación: un sorteo puede quedar "Recuperado" con datos de varias fuentes. | Aprobada (Clarifications 18/11/2026) | US4 |
| RN-30 | **Tolerancia de importes**: cuando las fuentes publican importes distintos para un mismo dato, dos importes **coinciden si difieren en menos de $ 1,00** (unas fuentes redondean los centavos y otras los quitan); también al buscar la coincidencia de 2 de 3 fuentes (RN-07, D-21). Si todos coinciden con el de la fuente de mayor prioridad, no hay diferencia: el consolidado toma ese importe **sin centavos**, respaldado por todas las fuentes, sin nota si el importe prioritario no tenía centavos y con la nota informativa "Diferencia de centavos o redondeo (menor al 1 %)" si los tenía. Si no coinciden, se quitan los centavos de cada importe y, si todos difieren menos del 1 % del de la fuente de mayor prioridad, no hay discrepancia: el consolidado toma ese importe sin centavos y el detalle y el archivo muestran la misma nota informativa con el valor publicado por cada fuente. Si la diferencia es del 1 % o mayor, es una discrepancia de tipo "Valor distinto" y el importe queda "Sin determinar" (D-17, D-28). | Aprobada (Clarifications 20/11/2026; comparación con diferencia menor a $ 1,00 según D-28, 23/11/2026, que reemplaza el orden redondeo → comparación) | US4 |

**Clasificación y resumen**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-31 | Cada sorteo queda en un solo estado, con esta precedencia: **No recuperado** (ninguna fuente aportó datos válidos del sorteo); **Con inconsistencias** (al menos una discrepancia u observación de inconsistencia); **Recuperado parcialmente** (falta algún dato esperado, sin inconsistencias); **Recuperado** (todos los datos esperados, sin discrepancias). Son datos esperados: número, fecha, los seis números de cada extracción propia del catálogo vigente (Primer Sorteo, La Segunda, Revancha y Siempre Sale; D-04) y, por cada categoría esperada, la cantidad de ganadores y el importe que corresponde a su estado (pozo destinado si está vacante, importe individual si tiene ganadores). El pozo destinado de una categoría con ganadores no es un dato esperado, porque ninguna fuente consultada lo publica. Un dato informado por una sola fuente cuenta como presente (RN-32). Las indicaciones "Combina fuentes" y "Sin corroborar" se muestran aparte y no cambian el estado. | Aprobada (Clarifications 18/11/2026 y 19/11/2026) | US1, US2 |
| RN-32 | Un dato informado por una sola fuente cuenta como recuperado y lleva la marca "Sin corroborar" † en el detalle y en el archivo. Un dato en el que coinciden dos o más fuentes queda corroborado. Un sorteo con al menos un dato sin corroborar muestra la marca "Sin corroborar" en el detalle. | Aprobada (Clarifications 18/11/2026) | US4 |
| RN-33 | El resumen muestra: período consultado; sorteos identificados; recuperados; recuperados parcialmente; con inconsistencias; no recuperados (los cuatro suman los identificados); y fuentes utilizadas, cada una con los sorteos que aportó y sus intentos fallidos por tipo. Las fuentes marcadas "Requiere mantenimiento" (RN-10) se destacan en el resumen. El resultado global es "Extracción finalizada" si todos los sorteos están "Recuperado", y "Extracción finalizada con advertencias que requieren revisión" en cualquier otro caso. | Aprobada (Clarifications 19/11/2026) | US1, US2 |

**Archivo CSV**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-34 | El archivo es un único CSV en UTF-8, con encabezados estandarizados en la primera fila, fechas e importes en formato uniforme y la versión del contrato. Los encabezados definitivos se fijan en el plan, a partir de RN-43 y del análisis "Correspondencia con el modelo vigente". | Aprobada | US5 |
| RN-35 | El archivo permite identificar, como mínimo: número y fecha del sorteo; modalidad; números de cada extracción propia; categoría y aciertos requeridos; cantidad de ganadores; pozo destinado; importe individual; estado del pozo (RN-19); estado del sorteo y sus indicaciones "Combina fuentes" y "Sin corroborar"; la marca "Sin corroborar" de cada dato informado por una sola fuente; discrepancias y observaciones; y, por cada dato, su fuente, la dirección consultada y la fecha y hora de consulta, en columnas de texto (RN-43). No incluye el precio del cartón. | Aprobada | US5 |
| RN-36 | Los estados de RN-20 se representan de forma explícita y distinguible. Una celda vacía nunca representa un cero. | Aprobada | US5 |
| RN-37 | El archivo no tiene filas duplicadas. Cada fila se identifica por número de sorteo, modalidad y categoría. | Aprobada (Clarifications 18/11/2026) | US5 |
| RN-38 | **Formato técnico del archivo**: fechas AAAA-MM-DD; fechas y horas de consulta AAAA-MM-DD HH:MM:SS en `America/Argentina/Buenos_Aires`; importes en pesos con punto decimal, dos decimales y sin separador de miles, por ejemplo 1100000000.00; números extraídos del Quini 6 con dos dígitos, de 00 a 45; columnas separadas por coma. | Aprobada (Clarifications 18/11/2026) | US5 |
| RN-39 | Todo sorteo identificado figura en el archivo, en cualquier estado. Un sorteo **No recuperado** figura en una sola fila con su número, su fecha si se conoce, su estado y sus motivos, con modalidad y categoría "No disponible". Un sorteo **Recuperado parcialmente** o **Con inconsistencias** figura con todas sus filas, con los datos faltantes como "No disponible" y los datos en conflicto como "Sin determinar". Una modalidad que ninguna fuente informa figura en una fila con categoría "No disponible" y la observación "No informada por las fuentes". En ningún caso se inventan valores. | Aprobada (Clarifications 19/11/2026) | US5 |
| RN-43 | **Estructura del archivo**: una fila por sorteo, modalidad y categoría, solo con los datos consolidados. Las filas de una modalidad con extracción propia repiten sus seis números; las de Pozo Extra los tienen como "No corresponde" y sus números van en la columna `numeros_pozo_extra` (RN-12, Clarifications 20/11/2026). Los datos del sorteo (número, fecha, estado, "Combina fuentes" y "Sin corroborar") se repiten en cada fila. La procedencia de cada dato, la marca "Sin corroborar" de cada dato y las discrepancias, con cada valor en conflicto y su fuente, van en columnas de texto. El archivo no contiene filas por fuente. | Aprobada (Clarifications 18/11/2026) | US5 |

**Aislamiento y acceso**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-40 | Los datos extraídos no tienen ninguno de los estados de validación de [001] RN-16. Una futura ingesta deberá cargarlos como Borrador y someterlos a [001] RN-17 antes de publicarlos. | Aprobada | US6 |
| RN-41 | La extracción no crea ni modifica concursos, modalidades, números, premios, estados de validación, jugadas ni registros de cambio de la aplicación. | Aprobada | US6 |
| RN-42 | Solo una cuenta con permiso de administrador ([001] RN-37) usa esta funcionalidad. Las respuestas ante un acceso no permitido son las de [001] AC-2.11 y AC-2.12. | Aprobada | US6 |
| RN-44 | **Conservación de extracciones**: toda extracción se conserva por tiempo indefinido, hasta que un administrador la elimina (D-24), con el administrador que la ejecutó, la fecha y hora de inicio y de fin, el período, el estado, el resumen, el detalle por sorteo y el archivo. Todos los administradores ven el listado de extracciones, ordenado de la más reciente a la más antigua, y pueden abrir cualquiera y descargar su archivo. El archivo de una extracción terminada queda fijo: descargarlo después devuelve siempre el mismo contenido, aunque las fuentes hayan cambiado. Cualquier administrador puede eliminar una extracción terminada, previa confirmación: se borran la extracción, su resumen, el detalle de sus sorteos y su archivo, sin afectar a ninguna otra extracción ni a los datos de la aplicación. Una extracción en curso no se puede eliminar. Una extracción conservada no es una ingesta (RN-41). | Aprobada (Clarifications 18/11/2026; actualizada 20/11/2026, D-24) | US1, US5, US6 |

### Correspondencia con el modelo vigente

El pedido exige analizar cómo se relacionan los datos extraídos con las entidades existentes antes de fijar encabezados. Esta tabla usa las entidades de [001] "Entidades clave" y su modelo de datos.

| Dato extraído | Entidad y atributo vigente | Situación |
|---------------|----------------------------|-----------|
| Número de sorteo | Concurso: número | Equivalente |
| Fecha del sorteo | Concurso: fecha del sorteo | Equivalente |
| Modalidad | Modalidades aplicables del concurso | Equivalente, con la tabla de rótulos de RN-11 |
| Números de una extracción propia | Resultado de modalidad: seis números, en orden ascendente | Equivalente |
| Números de Premio Extra | Conjunto de Premio Extra, derivado y no cargado | No se exporta (RN-12) |
| Categoría | Categoría de premio predefinida por modalidad | Equivalente. La categoría **Estímulo** solo figura en el extracto oficial, que no se consulta |
| Aciertos de la categoría ganadora | Siempre Sale y Premio Extra: cantidad de aciertos de la categoría ganadora; Premio Extra: indicación "sin ganadores" | Equivalente |
| Cantidad de ganadores | Categoría de premio: cantidad de ganadores, que admite "no disponible" | Equivalente |
| Pozo destinado | Categoría de premio: importe destinado | Equivalente |
| Importe individual | Categoría de premio: importe individual, nunca calculado | Equivalente |
| Estado del pozo | No existe como atributo; se deriva de la cantidad de ganadores | Derivable |
| "No corresponde" frente a "No disponible" | El modelo solo tiene "no disponible" | **Brecha**: se deriva de ganadores = 0; la futura ingesta debe tenerlo en cuenta |
| Pozo acumulado | Un único atributo "pozo vacante o acumulado" | **Brecha**: mezcla dos conceptos que el pedido distingue (D-08) |
| Procedencia | Una fuente y una fecha de consulta por bloque de números o de premios | **Brecha**: la extracción conserva la procedencia por dato |
| Discrepancias y observaciones | No existen | Nuevo, propio del archivo |
| Estado de recuperación del sorteo | No existe | Nuevo, propio del archivo |

### Entidades clave (Key Entities)

- **Extracción**: pedido de un administrador para un período, conservado por tiempo indefinido (RN-44). Atributos: período, administrador que la ejecutó, fecha y hora de inicio y de fin, estado (en curso, finalizada, finalizada con advertencias, sin sorteos), avance, resumen, detalle por sorteo y archivo generado.
- **Fuente**: origen configurado (F1 a F3). Atributos: nombre, tipo (secundaria), cobertura histórica y ficha con la forma de pedir un sorteo, la equivalencia de rótulos y el significado de cada dato.
- **Intento de consulta**: consulta de un sorteo a una fuente. Atributos: dirección, fecha y hora, resultado según RN-08 y observaciones.
- **Dato informado por una fuente**: valor normalizado de un dato, como un número, una cantidad de ganadores o un importe, tal como lo informó una fuente, con el texto original cuando no pudo interpretarse.
- **Dato consolidado**: valor resultante de comparar las fuentes para un sorteo, una modalidad, una categoría y un concepto. Atributos: valor o estado de RN-20 y fuentes que lo respaldan.
- **Discrepancia**: diferencia entre fuentes para un dato. Atributos: tipo (valor distinto, omisión, centavos o redondeo) y valores con su fuente.
- **Resultado del sorteo**: estado de RN-31, indicación "Combina fuentes" y motivos.
- **Archivo CSV**: representación versionada de la extracción según RN-34 a RN-39.

### Dependencias

| Funcionalidad | Depende de | Motivo |
|---------------|------------|--------|
| Toda la feature | [001] cuentas y permiso de administrador | Acceso (RN-42) |
| Normalización | [001] catálogo de modalidades y categorías | RN-11 y RN-14 |
| Validación de categorías | [001] RN-33 y RN-49 a RN-54 | Reglas vigentes desde el 18/06/2024 |
| Futura ingesta | Esta spec (contrato del CSV) | El archivo es su entrada. No forma parte de esta feature |

---

## Criterios de éxito (Success Criteria) *(obligatorio)*

### Resultados medibles (Measurable Outcomes)

- **SC-001**: En un conjunto de casos de prueba que cubre los criterios de las historias 2, 3 y 4, el 100 % de los sorteos queda en el estado esperado y el 100 % de los datos queda con el valor o el estado esperado.
- **SC-002**: En el archivo de esos casos, el 100 % de los pozos calculados por la aplicación lleva la marca "Calculado" en su procedencia, ningún importe individual se calcula a partir de un pozo y el 0 % de los datos desconocidos figura como cero o como vacante.
- **SC-003**: En una muestra de al menos 10 sorteos extraídos de las fuentes reales, el 100 % de los valores del archivo coincide con lo que muestra la fuente citada como su origen.
- **SC-004**: Tras extraer un período que incluye concursos publicados y concursos inexistentes en la aplicación, el 0 % de la información pública, administrativa y de jugadas cambia.
- **SC-005**: En una matriz de accesos con visitante, usuario registrado y administrador sobre la pantalla, el inicio y la descarga, el 100 % de los accesos no autorizados es rechazado.
- **SC-006**: En una prueba con al menos 3 administradores, el 100 % identifica en menos de 1 minuto, sin ayuda, si la extracción terminó con advertencias y qué sorteos requieren revisión.
- **SC-007**: Con todas las fuentes disponibles y el ritmo de NFR-005, una extracción de un mes termina y su archivo se puede descargar en menos de 2 minutos, y una de 12 meses en menos de 10 minutos. Se mide sin otras extracciones en curso: si las hay, la nueva espera su turno (Clarifications 19/11/2026, análisis).
- **SC-008**: El 100 % de los archivos de prueba se importa en una planilla de cálculo de uso común, indicando UTF-8 y separador coma, mostrando bien los acentos y sin ejecutar ninguna fórmula.

---

## Supuestos (Assumptions)

Valores adoptados porque no cambian el alcance pedido. Se pueden revisar en `/speckit-clarify`:

- Se usa el rol único de administrador de [001] RN-37, sin permisos nuevos.
- Las fuentes y sus fichas forman parte de la configuración aprobada de la aplicación. Cambiarlas requiere una especificación aprobada, no una acción en la pantalla.
- Las pruebas de aceptación que requieren fallas, demoras, cambios de estructura o discrepancias se hacen en un entorno de prueba con fuentes de prueba que la persona que verifica puede configurar. La verificación se hace igualmente desde la pantalla y con el archivo descargado.
- Los números se registran en orden ascendente, como en el modelo vigente. No se conserva el orden de extracción, porque ninguna entidad actual lo usa.
- No se valida el día de la semana del sorteo, porque existen sorteos especiales.
- Un administrador tiene como máximo una extracción en curso. Mientras dura, la pantalla no permite iniciar otra.
- No hay opción para cancelar una extracción en curso, porque el pedido no la incluye.
- Desde el 20/11/2026 (D-24) se pueden eliminar extracciones terminadas. La eliminación es definitiva: no hay papelera ni registro de lo eliminado.
- El volumen conservado crece con cada extracción y no tiene un límite. Si eso fuera un problema de capacidad, se plantearía como propuesta.
- Las fechas y horas se muestran en `America/Argentina/Buenos_Aires`.
- El relevamiento de fuentes es del 18/11/2026 y las estructuras pueden cambiar antes de la implementación.

---

## Decisiones pendientes

Ninguna se resolvió por suposición. Todas quedaron resueltas por el responsable del proyecto entre el 18/11/2026 y el 19/11/2026. Las preguntas 1 a 11 del pedido están cubiertas así: 1, 2 y 3 en D-01; 4 en D-04; 5, 9 y 10 en D-03; 6 en D-05; 7 en D-06; 8 en D-07; 11 en D-08. Al 19/11/2026 no quedan decisiones bloqueantes.

### D-01 — Política de consolidación entre fuentes — **Reemplazada por D-14 (20/11/2026)**

Se consultan siempre todas las fuentes que cubren el sorteo y ninguna prevalece. Un dato de una sola fuente cuenta como recuperado, con la marca "Sin corroborar", y se permite combinar fuentes con procedencia por dato. Ver Clarifications, RN-07, RN-09, RN-29 y RN-32.

### D-02 — Incorporación del extracto oficial (F0) — **Resuelta (18/11/2026)**

No se consulta automáticamente. El detalle de cada sorteo ofrece un enlace a la página oficial de extractos para el cotejo manual. Ver Clarifications, FR-007, RN-06 y AC-1.13.

### D-03 — Granularidad y estructura del CSV — **Resuelta (18/11/2026)**

Una fila por sorteo, modalidad y categoría, solo con datos consolidados, y procedencia y discrepancias en columnas de texto. Consecuencia aceptada: los valores en conflicto quedan en el archivo solo como texto. La fila única del sorteo no recuperado, derivada por el agente, se aprobó el 19/11/2026. Ver Clarifications, RN-37, RN-39 y RN-43.

### D-04 — Modalidades que no existían en algunos períodos — **Resuelta (19/11/2026)**

No se aprueba un catálogo de vigencias en esta feature: una modalidad ausente en todas las fuentes figura "No informada por las fuentes" (RN-25).

### D-05 — Período máximo de una extracción — **Resuelta (19/11/2026)**

12 meses. Ver Clarifications y RN-04.

### D-06 — Identificación de los sorteos del período — **Resuelta (19/11/2026)**

Por numeración correlativa, verificando la fecha informada y procesando todos los números intermedios. Ver Clarifications y RN-05.

### D-07 — Cambio de estructura de una fuente — **Resuelta (19/11/2026)**

Se aplica RN-10 y el resumen marca "Requiere mantenimiento" la fuente que falla en todos los sorteos que cubre (AC-2.10).

### D-08 — Pozos acumulados y estado del pozo — **Reemplazada por D-22 (20/11/2026)**

La acumulación es un dato aparte del estado del pozo ("Se acumula según la fuente") y el importe trasladado nunca se reconstruye. Ver Clarifications y RN-19. **Reemplazada el 20/11/2026 (D-22)**: ni la acumulación ni el importe trasladado se registran.

### D-09 — Categoría "Estímulo" — **Sin efecto (18/11/2026)**

Solo la publica el extracto oficial, que no se consulta (D-02). Si alguna vez una fuente consultada publica una categoría fuera del catálogo, se aplica RN-14. Incorporar la categoría a la aplicación queda para una futura spec.

### D-10 — Diferencias de centavos o de redondeo — **Reemplazada por D-17 (20/11/2026)**

Toda diferencia de centavos o de redondeo es una discrepancia y no se elige ningún valor (RN-30, AC-4.5).

### D-11 — Formato técnico del CSV frente a Const. VII — **Resuelta (18/11/2026)**

Formato técnico en el archivo y formato argentino en la pantalla. El responsable confirma que el CSV no es contenido visible en el sentido de Const. VII. Ver Clarifications, NFR-001 y RN-38.

### D-12 — Conservación del resultado de una extracción — **Resuelta (18/11/2026)**

Se conservan todas las extracciones por tiempo indefinido, visibles para todos los administradores, con quién y cuándo las ejecutó. Ver Clarifications, FR-015 y RN-44. **Ampliada el 20/11/2026 (D-24)**: un administrador puede eliminar una extracción terminada.

### D-14 a D-21 — Correcciones del responsable — **Resueltas (20/11/2026)**

Prioridad de fuentes (D-14) y desempate con la tercera fuente (D-21), nombres de modalidades (D-15), pozo calculado e importe individual 0,00 en vacantes (D-16), tolerancia del 1 % (D-17), corrección de importes mal cargados (D-18 y D-20) y números de Pozo Extra (D-19). Ver Clarifications, sesión 2026-11-20. D-16, D-18 y D-20 son excepciones aprobadas a Const. VIII y IX ("no se inventan pozos", "no se completan datos mediante suposiciones"). Se admiten porque cada valor calculado o corregido queda marcado como tal en la pantalla y en el archivo, de modo que nunca se presenta como un dato publicado.

### D-13 — Condiciones de uso de las fuentes y ritmo de consulta — **Resuelta (19/11/2026)**

El responsable autoriza la consulta automatizada de F1, F2 y F3, con un máximo de una consulta cada 2 segundos por sitio. Las reglas para robots de los tres sitios no tienen instrucciones de acceso y ninguno publica condiciones de uso; quiniya publica solo un aviso legal que pide cotejar con las fuentes oficiales. Ver Clarifications y NFR-005.

---

## Relación con la especificación 001 y posibles contradicciones

1. **Integraciones con fuentes externas.** [001] excluye del MVP las "integraciones automáticas con fuentes externas para obtener resultados". Esta feature consulta fuentes externas, aunque a pedido de un administrador y sin ingesta. Es una ampliación de alcance, confirmada explícitamente por el responsable el 19/11/2026 (Clarifications, análisis).
2. **Carga solo manual.** [001] FR-010 fija la carga manual como único mecanismo de incorporación. No se contradice, porque esta feature no incorpora datos. La futura ingesta sí deberá revisar FR-010.
3. **Estado del pozo y acumulación.** El modelo vigente tiene un único atributo "pozo vacante o acumulado" y no distingue "No corresponde" de "No disponible" (ver la tabla de correspondencia y D-08).
4. **Categoría Estímulo.** El extracto oficial publica una categoría que el catálogo cerrado de [001] no tiene. No afecta a esta feature, porque el extracto no se consulta (D-09), pero sí afectaría a una futura ingesta desde el extracto oficial.
5. **Formatos.** Const. VII y [001] NFR-001 exigen formatos argentinos en todo lo visible. Resuelto el 18/11/2026: el CSV no es contenido visible y usa formato técnico (D-11).
6. **Lista de estados del pozo del pedido.** "Acumulado" no es excluyente con "Con ganadores" ni con "Vacante". Resuelto el 19/11/2026: la acumulación es un dato aparte (D-08).
7. **Respaldo frente a detección.** El respaldo secuencial del pedido impedía detectar discrepancias si se detenía en la primera fuente que responde. Resuelto el 18/11/2026: se consultan siempre todas las fuentes (D-01).
8. **Reglas por período.** Las reglas de categorías aprobadas rigen desde el 18/06/2024 ([001] RN-33). Los sorteos anteriores no se pueden validar contra ellas (RN-25).
9. **Documentación del proyecto.** `CLAUDE.md` indica que el estado del producto está en `specs/README.md`, pero ese archivo no existe.
10. **Restricciones técnicas para el plan.** El contrato de rutas de [001] no admite rutas nuevas sin especificarlas, y `CLAUDE.md` cierra la lista de dependencias. El plan deberá agregar las rutas de esta feature y justificar cualquier dependencia nueva para consultar e interpretar páginas externas.

---

## Propuestas futuras (fuera del alcance de esta especificación)

Se presentan para evaluación del responsable y no están autorizadas:

- Ingesta del CSV a la aplicación, con el flujo Borrador, validación y publicación de [001].
- Verificación de coherencia entre pozo, ganadores e importe individual cuando una fuente publica los tres, sin completar datos.
- Cancelación de una extracción en curso.
- Comparación entre dos extracciones conservadas. El listado de extracciones anteriores ya forma parte de esta feature (RN-44).
- Exportación del detalle de discrepancias como un informe aparte.

---

## Trazabilidad

| Historia | Requisitos funcionales | Reglas de negocio | Criterios de aceptación | Decisiones |
|----------|------------------------|-------------------|-------------------------|------------|
| US1 | FR-001 a FR-004, FR-007, FR-012, FR-013, FR-015 | RN-01 a RN-05, RN-31, RN-33, RN-44 | AC-1.1 a AC-1.17 | D-02, D-05, D-06 y D-12 (resueltas) |
| US2 | FR-005, FR-006, FR-012, FR-013 | RN-06 a RN-10, RN-31, RN-33 | AC-2.1 a AC-2.10 | D-01, D-02, D-07 y D-13 (resueltas) |
| US3 | FR-008, FR-009, FR-011 | RN-11 a RN-26 | AC-3.1 a AC-3.18 (AC-3.15 quitado) | D-04 (resuelta), D-08 (reemplazada por D-22), D-09 (sin efecto) |
| US4 | FR-005, FR-010, FR-012 | RN-07, RN-09, RN-27 a RN-30, RN-32 | AC-4.1 a AC-4.8 | D-01 y D-10 (resueltas) |
| US5 | FR-014, FR-015 | RN-34 a RN-39, RN-43, RN-44 | AC-5.1 a AC-5.10 | D-03, D-11 y D-12 (resueltas) |
| US6 | FR-001, FR-015, FR-016 | RN-40 a RN-42, RN-44 | AC-6.1 a AC-6.6 | D-12 (resuelta) |

| Requisito de calidad | Criterios relacionados |
|----------------------|------------------------|
| NFR-001 | AC-1.1 a AC-1.17, AC-5.2, RN-38 |
| NFR-002, NFR-003, NFR-011 | AC-1.2, AC-1.9, SC-006 |
| NFR-004 | AC-6.1, AC-6.2, SC-005 |
| NFR-005 | AC-2.9, SC-007 |
| NFR-006 | AC-2.8 |
| NFR-007 | AC-3.4, AC-3.5, AC-4.5 |
| NFR-008 | AC-5.4, SC-003 |
| NFR-009 | RN-34 |
| NFR-010 | AC-5.9, SC-008 |
