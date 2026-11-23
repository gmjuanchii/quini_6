# Especificación funcional (Feature Specification): Modernización visual y de experiencia de uso

**Feature Branch**: `003-modernizacion-ui-ux`

**Created**: 21/11/2026

**Status**: Aprobada por el responsable del proyecto (21/11/2026), completa (HU-01 a HU-14), con las aclaraciones del responsable del proyecto del 21/11/2026 (tratamiento neutro, sin recuperación de contraseña, sin "Deshacer") y de `/speckit-clarify` del mismo día ("Con error", atajos de período, "sorteo" como término único, formulario pendiente al vencer la sesión y extracciones repetidas), y de la revisión del checklist de migración del mismo día (HU-14 y FR-039 a FR-044 de convivencia durante la renovación; alcance de "no se guarda en el servidor"). RN-02, RN-07, RN-08 y RN-09 se aprobaron el 21/11/2026 junto con el contrato de mensajes del plan; RN-08 con un isotipo tipográfico provisional (texto "QUINI_6" en el azul corporativo) reemplazable sin tocar código.

**Input**: Descripción del responsable del proyecto: "Especificación: Modernización visual y de experiencia de uso de QUINI_6". Revisión de las pantallas Resultados, Ingreso, Mis jugadas, Estadísticas y Extracción histórica para que cualquier persona entienda dónde está, qué ocurrió y qué puede hacer, desde un teléfono o una computadora, con una apariencia actual y coherente.

**Marco normativo**: [Constitución del proyecto QUINI_6 v1.1.0](../../.specify/memory/constitution.md), citada como "Const. N". Se apoya en las especificaciones aprobadas [001](../001-quini6-mvp/spec.md) y [002](../002-extraccion-historica-csv/spec.md).

**Convención de identificadores**: los IDs de este documento (HU-, AC-, FR-, NFR-, RN-, SC-, D-) son locales a la spec 003. Desde otra spec o desde el código se citan con el prefijo `[003]`, por ejemplo `[003] FR-010`. Las referencias a las specs anteriores llevan su prefijo, por ejemplo `[001] AC-3.5` o `[002] RN-44`. Los identificadores HU-01 a HU-13 y CE-1 a CE-10 del pedido original se conservan: cada historia de usuario lleva su HU y cada criterio de éxito indica el CE del que proviene.

---

## Contexto y alcance

### Objetivo

Que cualquier persona pueda **entender dónde está, qué ocurrió y qué puede hacer** en cada pantalla, sin instrucciones, desde un teléfono o una computadora, con una apariencia actual, profesional y coherente (Const. X).

### Situación actual

La revisión de las pantallas actuales muestra una base ordenada y coherente, pero con carencias de claridad, retroalimentación y presentación visual:

- En "Extracciones anteriores", cuatro de seis filas dicen en texto plano "Extracción finalizada con advertencias que requieren revisión"; todas se ven iguales y lo crítico pasa desapercibido.
- El menú de acciones (⋮) se despliega desplazado fuera de su fila.
- Los campos de fecha ocupan todo el ancho o muestran un calendario del navegador con apariencia ajena a la aplicación, que tapa contenido.
- Los enlaces del encabezado se ven todos iguales y subrayados, sin señal de la sección activa.
- El formulario de ingreso queda pegado a la izquierda, con un vacío grande a la derecha.
- En Estadísticas, la etiqueta "Consultar un número (00 a 45)" se parte en dos líneas y la modalidad "Tradicional – Primer Sorteo" aparece recortada.
- Los estados vacíos son cuadros punteados con una sola línea de texto.
- La advertencia "Estadística descriptiva de sorteos pasados. No predice resultados futuros." es una línea en cursiva que pasa inadvertida.
- Conviven textos con voseo ("Creá una", "elegís", "tenés") y formas neutras ("Registrar mi primera jugada").

### Incluido

Navegación, formularios, selección de fechas, tablas y listados, estados de procesos, mensajes y avisos, estados vacíos, accesibilidad, tema claro y oscuro, textos de interfaz e identidad visual (logotipo, isotipo, favicon, paleta, tipografía, componentes) de todas las pantallas existentes de [001] y [002].

### Fuera del alcance

- Cambios en las reglas de extracción, consolidación, validación o generación del CSV de [002], incluido su contrato (`contracts/csv.md`): el archivo y sus columnas no cambian.
- Cambios en el cálculo de estadísticas, aciertos o premios, o en la publicación y validación de resultados de [001].
- Cambios en el modelo de roles o en los permisos: cada pantalla mantiene exactamente los permisos actuales.
- Nuevas funcionalidades de negocio: no se agregan datos, cálculos, pantallas de negocio ni procesos nuevos, salvo los mecanismos de presentación y de protección contra errores que esta spec enumera (filtros, orden y paginación de listados; confirmaciones; avisos; preferencias de tema).
- Comprar cartones, realizar apuestas o incorporar pagos (Const. V).
- Cualquier ampliación no aprobada (Const. I). Las ideas detectadas figuran en "Propuestas futuras".

### Actores y permisos

| Perfil | Descripción | Cambio en esta spec |
|--------|-------------|---------------------|
| **Visitante** | No inició sesión. Consulta resultados y estadísticas. | Ninguno en permisos. |
| **Usuario registrado** | Además registra y consulta sus propias jugadas. | Ninguno en permisos. |
| **Administrador** | Además carga y publica concursos ([001]) y ejecuta y gestiona extracciones históricas ([002]). | Ninguno en permisos. |

Toda pantalla, componente o acceso nuevo respeta los permisos actuales: un acceso directo, un filtro o una acción que lleva a una función restringida solo se muestra a quien ya tiene permiso para ella, y el permiso se sigue verificando en el servidor (Const. IV).

---

## Clarifications

### Session 2026-11-21

- Q: ¿Qué tratamiento usa toda la interfaz? (D-01) → A: **Forma impersonal o neutra** ("Ingresar", "Falta la fecha de finalización", "El número debe estar entre 00 y 45"), sin voseo, tuteo ni usted. Los botones empiezan con un verbo en infinitivo. Los ejemplos con voseo del pedido se adaptan a la forma neutra, y los textos con voseo de [001] y [002] (por ejemplo, "No tenés permisos para acceder a esta sección" o "Podés volver a intentar a las {hora}") se reescriben con el mismo significado. Se actualizan AC-1.2, AC-2.3, AC-3.4, AC-6.4, AC-6.7, AC-7.6, AC-8.2, AC-11.1, FR-033, FR-035, RN-02 y los Casos límite.
- Q: ¿Qué hace el enlace de recuperación de contraseña de HU-06? (D-02) → A: **No se agrega el enlace en esta feature**: [001] D-15 sigue vigente y la recuperación de contraseña pasa a "Propuestas futuras". Ese criterio de HU-06 queda fuera del alcance. Se actualizan AC-6.3 y FR-021.
- Q: ¿Se ofrece "Deshacer" tras eliminar una extracción? (D-03) → A: **No**. La confirmación aclara "Esta acción no se puede deshacer." y "Cancelar" es la opción predeterminada; al confirmar, la extracción se borra como en [002] RN-44, sin cambios. Se actualizan AC-2.3, AC-2.5 y FR-009.

### Session 2026-11-21 (`/speckit-clarify`)

- Q: ¿Cuándo se muestra una extracción con la etiqueta "Con error"? → A: Cuando terminó con **al menos un** sorteo "No recuperado", sin importar el estado de los demás; "Con advertencias" queda para las que tienen sorteos "Recuperado parcialmente" o "Con inconsistencias" y ninguno "No recuperado". Es solo presentación: no cambia [002] RN-31 ni RN-33. Se actualizan RN-01, RN-02, los Casos límite y los Supuestos.
- Q: ¿Qué atajos de período ofrece cada formulario, si la extracción histórica no admite más de 12 meses? → A: "Último año" pasa a ser **"Año en curso"** (del 01/01 de este año hasta hoy). La extracción histórica ofrece "Año en curso" y "Año anterior"; Estadísticas ofrece además "Todo el historial". Se actualizan RN-04 y AC-4.4.
- Q: ¿Qué término nombra en la interfaz al evento numerado ("N.º 3250"): "concurso" o "sorteo"? (D-04) → A: **"Sorteo" en toda la interfaz**, también en Resultados y Mis jugadas ("Sorteo N.º 3250", "Cargar sorteo", "← Sorteos"). "Concurso" deja de usarse en los textos visibles de [001] y [002]. Solo cambian los textos: los nombres internos, las direcciones y el CSV no cambian. Se actualizan RN-05, RN-10, AC-5.6, AC-8.4, FR-026, D-04 y los Supuestos.
- Q: Si la sesión vence mientras se completa un formulario privado, ¿dónde se conserva lo escrito? (FR-032) → A: **Viaja con el pedido de ingreso**: al ingresar de nuevo, el formulario se muestra completo para revisarlo y enviarlo; nada queda guardado en el navegador ni se envía solo. Si la persona no ingresa, lo escrito se pierde. Se actualizan FR-032, NFR-008, las Entidades clave, los Casos límite y los Supuestos.
- Q: ¿Qué extracciones históricas cuentan como repetidas y no se pueden iniciar mientras otra está en curso o en espera? (RN-03) → A: Solo las de **período exactamente igual** (misma fecha de inicio y de finalización). Un período que se superpone en parte sí se puede iniciar. Se actualiza RN-03.

### Session 2026-11-21 (planificación: migración y convivencia, `checklists/migracion.md`)

- Q: ¿La continuidad de la sesión, la paridad entre interfaces y la reversa durante la renovación tecnológica del plan se registran como requisitos? (CHK001) → A: **Sí**. Se agrega HU-14 con AC-14.1 a AC-14.6, FR-039 a FR-044 y SC-012.
- Q: ¿Qué significa "no se guarda en el servidor" para la preferencia de tema y el formulario pendiente? (CHK023, CHK024) → A: Que **ningún servidor lo registra ni lo conserva después de responder**. Leer la cookie de tema para mostrar la página con el tema elegido, o reenviar el formulario pendiente en tránsito entre partes de la aplicación, está permitido. Se actualizan NFR-008 y las Entidades clave.
- Q: Si la sesión vence en un formulario de una pantalla renovada mientras "Ingresar" sigue en la versión anterior, ¿cómo se vuelve al formulario? (CHK010) → A: Tras ingresar, una página breve ofrece **"Volver al formulario"**, que abre el formulario completo para revisarlo; nada se guarda ni se envía solo. Se actualiza FR-032 y se agrega AC-14.4.
- Q: ¿Qué pasa con los avisos cuando una acción termina en una pantalla servida por la otra versión? (CHK009) → A: **No se pierden**: se muestran en la pantalla de destino. Se agrega FR-043 y AC-14.3.
- Q: ¿Qué ve la persona si la versión nueva de una pantalla no responde? (CHK030) → A: Mientras exista la versión anterior, la pantalla se sigue mostrando con ella; después, una página que explica que el servicio no está disponible. Se agrega FR-044 y AC-14.6.

### Session 2026-11-21 (análisis previo a la implementación, `/speckit-analyze`)

- Q: ¿Se aprueba la spec 003 para implementar? (C1) → A: **Sí, completa** (HU-01 a HU-14, con todas las aclaraciones del 21/11/2026). Se aprueban también RN-02, RN-07, RN-08 y RN-09 con los textos de `contracts/mensajes.md`; RN-08 con el isotipo tipográfico provisional.
- Q: ¿FR-004 ("sin recargar la página") se mantiene en la versión actual de las pantallas? (I3) → A: **Sí**: con scripts, la persona se queda en el listado y la fila nueva aparece "En curso"; sin scripts, la versión básica abre el detalle de la extracción. FR-004 no cambia.

---

## Escenarios de usuario y pruebas (User Scenarios & Testing) *(obligatorio)*

Prioridad: **P1** imprescindible · **P2** importante · **P3** deseable. Cada historia se puede entregar y probar por separado.

### Historia de usuario 1 (HU-01) — Distinguir el estado de cada extracción (Prioridad: P1)

Como administrador, quiero ver de un vistazo cómo terminó cada extracción para saber cuáles requieren mi atención.

**Por qué esta prioridad**: hoy las extracciones con advertencias no se distinguen de las demás; es el problema que más riesgo operativo genera.

**Prueba independiente**: con extracciones en cada estado, un administrador abre "Extracción histórica" e identifica, sin ayuda, cuáles tienen advertencias o error; filtra la lista por estado.

**Escenarios de aceptación**:

1. **AC-1.1** — **Dado** el listado de extracciones, **cuando** el administrador lo mira, **entonces** cada fila muestra una etiqueta de estado con **texto corto, icono y color**: "En curso", "Finalizada", "Con advertencias", "Sin sorteos" o "Con error" (RN-01). Con la pantalla en escala de grises, cada estado sigue siendo distinguible por su texto y su icono.
2. **AC-1.2** — **Dado** una extracción con advertencias, **cuando** el administrador pasa el cursor sobre su etiqueta o la enfoca con el teclado, **entonces** lee "Hay sorteos del período que requieren revisión manual. El detalle los muestra." (RN-02). La misma explicación figura en el detalle de la extracción.
3. **AC-1.3** — **Dado** un listado con extracciones finalizadas sin novedades y otras con advertencias o con error, **cuando** el administrador lo mira, **entonces** las que requieren revisión se destacan del resto (por ejemplo, con el color ámbar o rojo de su etiqueta y una marca en la fila), y las finalizadas sin novedades no compiten visualmente con ellas.
4. **AC-1.4** — **Dado** el listado, **cuando** el administrador elige el filtro "Con advertencias", **entonces** ve solo las extracciones con ese estado y una indicación del filtro aplicado; **cuando** elige "Todos los estados", vuelve a ver todas.
5. **AC-1.5** — **Dado** una extracción, **cuando** el administrador abre su detalle, **entonces** ve la misma etiqueta de estado que en el listado y, debajo, el resultado completo de [002] RN-33 ("Extracción finalizada con advertencias que requieren revisión" o el que corresponda).

---

### Historia de usuario 2 (HU-02) — Eliminar con confirmación y posibilidad de arrepentirse (Prioridad: P1)

Como administrador, quiero que eliminar una extracción no pueda ocurrir por accidente.

**Por qué esta prioridad**: una eliminación accidental pierde el resultado y el archivo de una extracción que puede haber tardado horas.

**Prueba independiente**: un administrador abre el menú de acciones de una fila con el ratón y con el teclado, elige "Eliminar", cancela, vuelve a intentarlo y confirma.

**Escenarios de aceptación**:

1. **AC-2.1** — **Dado** el listado de extracciones, **cuando** el administrador pulsa el botón de acciones (⋮) de una fila, **entonces** el menú se despliega pegado a ese botón, dentro de los límites visibles de la pantalla, y sus opciones corresponden a esa fila. Con otro menú abierto, abrir uno nuevo cierra el anterior.
2. **AC-2.2** — **Dado** el foco en el botón de acciones, **cuando** el administrador pulsa Intro o Espacio, **entonces** el menú se abre y el foco pasa a la primera opción; con las flechas recorre las opciones; **cuando** pulsa Escape, el menú se cierra y el foco vuelve al botón. **Cuando** hace clic fuera del menú, el menú se cierra.
3. **AC-2.3** — **Dado** una extracción terminada, **cuando** el administrador elige "Eliminar", **entonces** ve la confirmación "¿Eliminar la extracción del 21/11/2026 12:15 (01/01/2024 al 31/12/2024)? Esta acción no se puede deshacer." con la aclaración de qué se pierde (resumen, detalle de sus sorteos y archivo CSV) y los botones "Cancelar" y "Eliminar". "Cancelar" tiene el foco inicial y es la acción predeterminada; "Eliminar" tiene estilo destructivo (rojo, con icono).
4. **AC-2.4** — **Dado** la confirmación abierta, **cuando** el administrador pulsa Escape, "Cancelar" o fuera de la confirmación, **entonces** la confirmación se cierra sin eliminar nada y el foco vuelve al botón de acciones de la fila.
5. **AC-2.5** — **Dado** la confirmación abierta, **cuando** el administrador pulsa "Eliminar", **entonces** la extracción desaparece del listado y aparece un aviso breve "Se eliminó la extracción del 21/11/2026 12:15", sin opción "Deshacer" (FR-009, D-03).
6. **AC-2.6** — **Dado** una extracción en curso, **cuando** el administrador abre su menú de acciones, **entonces** no ve "Eliminar" ([002] AC-1.19 sin cambios).

---

### Historia de usuario 3 (HU-03) — Ver el avance de una extracción en curso (Prioridad: P1)

Como administrador, quiero saber que mi extracción está funcionando y cuándo termina.

**Por qué esta prioridad**: sin respuesta visible, el administrador vuelve a pulsar, recarga o abandona la tarea.

**Prueba independiente**: un administrador inicia una extracción de un año y sigue su avance sin recargar la página hasta que termina.

**Escenarios de aceptación**:

1. **AC-3.1** — **Dado** un período válido, **cuando** el administrador pulsa "Iniciar extracción", **entonces** el botón pasa de inmediato a un estado de trabajo ("Iniciando…", con indicador de actividad) y no puede pulsarse de nuevo; la nueva extracción aparece en el listado con la etiqueta "En curso".
2. **AC-3.2** — **Dado** una extracción en curso, **cuando** el administrador mira la pantalla sin recargarla, **entonces** ve que hay actividad: mientras se identifican los sorteos, un indicador de actividad con "Identificando los sorteos del período…"; con el total conocido, la barra de progreso animada con "N de M sorteos procesados" ([002] FR-003, D-26). La fila del listado muestra el mismo avance.
3. **AC-3.3** — **Dado** una extracción en curso, **cuando** termina, **entonces** su etiqueta cambia sola al estado final y aparece un aviso con el resultado (por ejemplo, "La extracción terminó con advertencias: 3 sorteos requieren revisión", con acceso al detalle), sin que el administrador recargue la página.
4. **AC-3.4** — **Dado** que la extracción no pudo iniciarse o terminó con error, **cuando** el administrador mira la pantalla, **entonces** ve un mensaje que explica qué pasó y qué puede hacer (por ejemplo, "No se pudo consultar ninguna fuente. El detalle muestra qué respondió cada una; es posible volver a intentarlo más tarde.").
5. **AC-3.5** — **Dado** una extracción en curso o en espera para un período, **cuando** se intenta iniciar otra con el mismo período (misma fecha de inicio y de finalización), **entonces** no se crea una nueva y se ve "Ya hay una extracción en curso para el período del 01/01/2024 al 31/12/2024", con acceso a esa extracción (RN-03).
6. **AC-3.6** — **Dado** una extracción en curso, **cuando** el administrador cierra la pestaña y vuelve más tarde, **entonces** ve el estado real de la extracción (en curso con su avance actual, o el estado final) ([002] AC-1.11).

---

### Historia de usuario 4 (HU-04) — Elegir fechas de forma simple y coherente (Prioridad: P1)

Como persona usuaria, quiero indicar un período sin cometer errores de formato.

**Por qué esta prioridad**: las fechas son el dato que más se ingresa (extracción, búsqueda de resultados, estadísticas) y hoy se presentan de dos formas distintas.

**Prueba independiente**: una persona completa un período escribiendo las fechas, luego eligiéndolas en el calendario y luego con un atajo, en un teléfono y en una computadora.

**Escenarios de aceptación**:

1. **AC-4.1** — **Dado** cualquier formulario con fechas, **cuando** la persona lo mira en escritorio, **entonces** cada campo de fecha tiene un ancho acorde a "dd/mm/aaaa" y no ocupa todo el ancho de la página; en un teléfono de 360 px se acomoda sin desbordar.
2. **AC-4.2** — **Dado** un campo de fecha, **cuando** la persona escribe 01012025, **entonces** el campo muestra 01/01/2025 (se conserva [002] D-27). **Cuando** pulsa el icono de calendario, **entonces** se abre un calendario con el estilo de la aplicación, con la semana empezando en lunes y los nombres de meses y días en español ("lunes", "enero").
3. **AC-4.3** — **Dado** un período con fecha de inicio y de finalización, **cuando** la persona abre el calendario de período, **entonces** puede elegir el inicio y el fin en el mismo calendario, con el rango resaltado; también puede escribir cada fecha por separado.
4. **AC-4.4** — **Dado** un formulario de período, **cuando** la persona elige uno de sus atajos ("Año en curso", "Año anterior" y, solo en Estadísticas, "Todo el historial"), **entonces** las dos fechas se completan según RN-04 y puede modificarlas antes de enviar. Por ejemplo, el 21/11/2026, "Año en curso" completa del 01/01/2026 al 21/11/2026 y "Año anterior", del 01/01/2025 al 31/12/2025. El formulario de extracción histórica no ofrece "Todo el historial".
5. **AC-4.5** — **Dado** una fecha imposible (31/02/2025, 29/02/2025) o un fin anterior al inicio, **cuando** la persona sale del campo o intenta enviar, **entonces** ve junto al campo un mensaje concreto, por ejemplo "La fecha de finalización no puede ser anterior al 01/01/2025", y el formulario no se envía. El 29/02/2024 se acepta.
6. **AC-4.6** — **Dado** el calendario abierto, **cuando** se despliega, **entonces** no tapa el campo que se está completando; **cuando** la persona pulsa Escape, se cierra y el foco vuelve al campo. Todo el calendario se puede usar con el teclado.
7. **AC-4.7** — **Dado** un campo con una fecha máxima (por ejemplo, no se aceptan fechas futuras donde [002] lo exige), **cuando** la persona abre el calendario, **entonces** los días no permitidos se ven deshabilitados y no se pueden elegir.

---

### Historia de usuario 5 (HU-05) — Saber dónde estoy y moverme con comodidad (Prioridad: P1)

Como persona usuaria, quiero que la navegación me indique la sección actual y funcione en el teléfono.

**Por qué esta prioridad**: la navegación aparece en todas las pantallas; sin indicación de la sección actual ni versión para teléfono, todo lo demás pierde valor.

**Prueba independiente**: una persona recorre todas las secciones con el ratón, con el teclado y en un teléfono, y en cada una indica dónde está y cómo volver.

**Escenarios de aceptación**:

1. **AC-5.1** — **Dado** cualquier pantalla, **cuando** la persona mira el encabezado, **entonces** la sección actual se distingue del resto por más de un rasgo (por ejemplo, color de fondo y marca inferior) y se anuncia a los lectores de pantalla como la página actual.
2. **AC-5.2** — **Dado** el encabezado, **cuando** la persona lo mira, **entonces** los enlaces de navegación no van subrayados, tienen un área de toque de al menos 44 × 44 px y responden visiblemente al cursor, al foco y al pulsarlos.
3. **AC-5.3** — **Dado** una persona con sesión iniciada, **cuando** mira el encabezado, **entonces** ve un menú de cuenta con su correo (abreviado si es muy largo, completo al enfocarlo) que contiene "Salir"; "Salir" no aparece como una sección más.
4. **AC-5.4** — **Dado** una pantalla de 360 px a 767 px de ancho, **cuando** la persona abre la página, **entonces** la navegación se condensa en un botón "Menú" que despliega las secciones; se abre y cierra con el teclado (incluida Escape) y el lector de pantalla anuncia si está abierto o cerrado.
5. **AC-5.5** — **Dado** cualquier pantalla, **cuando** la persona pulsa Tab por primera vez, **entonces** aparece "Saltar al contenido" y, al activarlo, el foco pasa al contenido principal.
6. **AC-5.6** — **Dado** una página interna (detalle de un sorteo, de una jugada, de una extracción histórica o de un sorteo extraído), **cuando** la persona la mira, **entonces** ve un camino de regreso con el nombre del destino (por ejemplo, "← Sorteos", "← Extracción histórica").
7. **AC-5.7** — **Dado** cualquier pantalla, **cuando** la persona la abre, **entonces** ve el logotipo de QUINI_6 en el encabezado (enlaza a la página de inicio) y la pestaña del navegador muestra el favicon propio (RN-08).

---

### Historia de usuario 6 (HU-06) — Ingresar sin fricción (Prioridad: P2)

Como persona usuaria, quiero iniciar sesión de forma rápida y segura.

**Por qué esta prioridad**: afecta a toda persona registrada en cada visita, pero la pantalla actual ya permite ingresar.

**Prueba independiente**: una persona ingresa con un gestor de contraseñas, muestra y oculta la contraseña, comete errores y crea una cuenta desde la misma pantalla.

**Escenarios de aceptación**:

1. **AC-6.1** — **Dado** la pantalla "Ingresar" o "Crear cuenta" en escritorio, **cuando** la persona la abre, **entonces** el formulario aparece centrado, en una tarjeta de ancho cómodo (no más de una columna de lectura); en un teléfono ocupa el ancho disponible con los márgenes de la aplicación.
2. **AC-6.2** — **Dado** el campo de contraseña, **cuando** la persona pulsa "Mostrar", **entonces** ve la contraseña y el botón pasa a "Ocultar"; el lector de pantalla anuncia el cambio.
3. **AC-6.3** — **Dado** la pantalla "Ingresar", **cuando** la persona la mira, **entonces** no ve un enlace de recuperación de contraseña: [001] D-15 sigue vigente y la recuperación queda en "Propuestas futuras" (D-02).
4. **AC-6.4** — **Dado** un correo con formato inválido, **cuando** la persona sale del campo, **entonces** ve junto al campo "El correo electrónico no tiene un formato válido", antes de enviar. **Dado** credenciales incorrectas, **cuando** envía, **entonces** ve "Correo electrónico o contraseña incorrectos" sin indicar cuál dato falla ni si el correo existe ([001] AC-3.5).
5. **AC-6.5** — **Dado** un navegador o gestor de contraseñas con datos guardados, **cuando** la persona abre "Ingresar", **entonces** puede autocompletar el correo y la contraseña; en "Crear cuenta", el gestor puede proponer una contraseña nueva.
6. **AC-6.6** — **Dado** el formulario completo, **cuando** la persona pulsa "Ingresar", **entonces** el botón muestra "Ingresando…" con indicador de actividad y no se puede pulsar de nuevo hasta recibir respuesta.
7. **AC-6.7** — **Dado** la pantalla "Ingresar", **cuando** la persona la mira, **entonces** "Crear cuenta" aparece como alternativa claramente separada de la acción principal (por ejemplo, "¿Todavía sin cuenta? Crear cuenta" debajo del formulario, con estilo secundario), y viceversa en "Crear cuenta".

---

### Historia de usuario 7 (HU-07) — Filtros de estadísticas claros (Prioridad: P2)

Como persona usuaria, quiero configurar la consulta sin que los campos se superpongan ni se corten.

**Por qué esta prioridad**: Estadísticas es una de las secciones públicas principales y hoy sus filtros se cortan.

**Prueba independiente**: una persona configura las estadísticas en escritorio y en un teléfono, consulta un número fuera de rango y ordena los resultados.

**Escenarios de aceptación**:

1. **AC-7.1** — **Dado** el selector de modalidad, **cuando** la persona lo abre o lo mira cerrado, **entonces** todas las opciones se leen completas, incluida "Tradicional – Primer Sorteo", sin recortes.
2. **AC-7.2** — **Dado** la barra de filtros en escritorio, **cuando** la persona la mira, **entonces** los campos y el botón "Consultar" comparten una misma línea base; **dado** un teléfono de 360 px, se reorganizan en filas sin superponerse.
3. **AC-7.3** — **Dado** los filtros, **cuando** la persona los mira, **entonces** las etiquetas son breves ("Número", "Modalidad", "Desde", "Hasta") y el formato o el rango se indican con un texto de ayuda asociado ("Entre 00 y 45").
4. **AC-7.4** — **Dado** la pantalla, **cuando** la persona la mira, **entonces** "Consultar un número" aparece como un bloque visualmente separado de los filtros del período.
5. **AC-7.5** — **Dado** una consulta con resultados, **cuando** la persona la mira, **entonces** ve un gráfico de frecuencia por número además de la tabla, con la misma información; **cuando** pulsa el encabezado de una columna de la tabla, la ordena por esa columna, ascendente o descendente, con indicación del orden actual.
6. **AC-7.6** — **Dado** el campo "Número", **cuando** la persona escribe 46 o -1 y sale del campo o intenta consultar, **entonces** ve de inmediato "El número debe estar entre 00 y 45" junto al campo y la consulta no se envía.

---

### Historia de usuario 8 (HU-08) — Estados vacíos que orientan (Prioridad: P2)

Como persona usuaria, quiero entender por qué no hay datos y qué hacer a continuación.

**Por qué esta prioridad**: es lo primero que ve una persona nueva o una instalación sin datos.

**Prueba independiente**: con la base vacía, una persona recorre cada sección como visitante, usuario y administrador; luego aplica filtros que no devuelven nada.

**Escenarios de aceptación**:

1. **AC-8.1** — **Dado** cualquier listado o consulta sin datos, **cuando** la persona lo mira, **entonces** ve un estado vacío con icono o ilustración, un título, una explicación breve y, cuando corresponde, una acción (RN-06).
2. **AC-8.2** — **Dado** un usuario sin jugadas, **cuando** abre "Mis jugadas", **entonces** ve un icono de boleta, "Todavía no hay jugadas registradas", "Cada jugada registrada muestra cuántos aciertos tuvo en cada sorteo" y el botón "Registrar mi primera jugada" (D-01).
3. **AC-8.3** — **Dado** un filtro sin resultados (por estado, período o búsqueda), **cuando** la persona lo aplica, **entonces** ve un estado vacío distinto del de "sin datos todavía", que nombra el filtro aplicado y ofrece "Limpiar filtros".
4. **AC-8.4** — **Dado** que no hay sorteos registrados, **cuando** un administrador abre Resultados, **entonces** además del estado vacío ve accesos directos a "Cargar sorteo" y a "Extracción histórica"; un visitante o un usuario registrado ve el mismo estado vacío sin esos accesos.

---

### Historia de usuario 9 (HU-09) — Tablas cómodas en cualquier pantalla (Prioridad: P2)

Como administrador, quiero manejar un historial largo de extracciones.

**Por qué esta prioridad**: el listado crece con cada extracción y [002] RN-44 las conserva por tiempo indefinido.

**Prueba independiente**: con 0, 1 y 300 extracciones, un administrador ordena, pagina y abre filas en escritorio y en un teléfono.

**Escenarios de aceptación**:

1. **AC-9.1** — **Dado** el listado de extracciones, **cuando** el administrador pulsa el encabezado "Fecha", "Período" o "Estado", **entonces** el listado se ordena por esa columna, ascendente o descendente, con indicación del orden actual. El orden inicial sigue siendo de la más reciente a la más antigua ([002] RN-44).
2. **AC-9.2** — **Dado** más de 20 extracciones, **cuando** el administrador abre el listado, **entonces** ve las primeras 20 y controles de paginación con la página actual y el total ("Página 1 de 15"); el filtro y el orden se mantienen al cambiar de página (RN-07).
3. **AC-9.3** — **Dado** un teléfono de 360 px, **cuando** el administrador abre el listado, **entonces** cada fila se muestra como una tarjeta con todas sus columnas rotuladas, y la página no se desplaza horizontalmente.
4. **AC-9.4** — **Dado** una fila del listado, **cuando** el administrador hace clic en cualquier parte de ella (salvo el menú de acciones), **entonces** abre el detalle de esa extracción; al pasar el cursor, la fila se resalta y el destino se indica (por ejemplo, "Ver detalle →").
5. **AC-9.5** — **Dado** cualquier pantalla de la aplicación, **cuando** se comparan los encabezados de columnas que muestran el mismo dato, **entonces** usan el mismo nombre (RN-05); y toda fecha se muestra como dd/mm/aaaa y toda fecha con hora como dd/mm/aaaa HH:MM.

---

### Historia de usuario 10 (HU-10) — Avisos importantes que se noten (Prioridad: P2)

Como persona usuaria, quiero ver las advertencias legales y de interpretación sin tener que buscarlas.

**Por qué esta prioridad**: las advertencias son exigidas por Const. V y VIII y hoy pasan inadvertidas.

**Prueba independiente**: una persona recorre Estadísticas y el pie de página en escritorio y en un teléfono, y provoca un mensaje de éxito, uno de advertencia y uno de error en distintas pantallas.

**Escenarios de aceptación**:

1. **AC-10.1** — **Dado** la pantalla de Estadísticas, **cuando** la persona la abre, **entonces** ve "Estadística descriptiva de sorteos pasados. No predice resultados futuros." en un aviso informativo con icono, antes de los resultados, y no como una línea en cursiva.
2. **AC-10.2** — **Dado** cualquier pantalla, **cuando** la persona mira el pie de página en un teléfono de 360 px, **entonces** lee "QUINI_6 no vende apuestas ni realiza pagos" con contraste de al menos 4,5:1 y un tamaño de letra no menor al del cuerpo de texto secundario.
3. **AC-10.3** — **Dado** mensajes de éxito, advertencia, error e información en distintas pantallas, **cuando** la persona los compara, **entonces** cada tipo tiene siempre el mismo icono, color, forma y ubicación, y el lector de pantalla los anuncia (RN-09).

---

### Historia de usuario 11 (HU-11) — Lenguaje de interfaz uniforme (Prioridad: P2)

Como persona usuaria, quiero que la aplicación me hable siempre de la misma manera.

**Por qué esta prioridad**: hoy conviven dos tratamientos; es un cambio de bajo riesgo con impacto en toda la aplicación.

**Prueba independiente**: una persona revisa todos los textos visibles de todas las pantallas y verifica tratamiento, verbos de botones y términos del glosario.

**Escenarios de aceptación**:

1. **AC-11.1** — **Dado** cualquier texto visible de la interfaz (botones, etiquetas, ayudas, mensajes, estados vacíos, avisos), **cuando** se lo revisa, **entonces** usa la forma impersonal o neutra ("Ingresar", "Falta la fecha de finalización"), sin voseo, tuteo ni usted; un texto como "No tenés permisos para acceder a esta sección" se reescribe, por ejemplo, como "Sin permisos para acceder a esta sección" (D-01).
2. **AC-11.2** — **Dado** cualquier botón de la interfaz, **cuando** se lo lee, **entonces** comienza con un verbo que nombra la acción ("Iniciar extracción", "Consultar", "Registrar jugada", "Eliminar"). No hay botones rotulados solo "Aceptar" u "OK".
3. **AC-11.3** — **Dado** el glosario de términos (RN-10), **cuando** se revisan todas las pantallas, **entonces** cada término se usa siempre con el mismo significado y ningún concepto aparece con dos nombres distintos.

---

### Historia de usuario 12 (HU-12) — Elegir tema claro u oscuro (Prioridad: P3)

Como persona usuaria, quiero una apariencia cómoda para mis ojos.

**Por qué esta prioridad**: mejora la comodidad, pero no bloquea ninguna tarea.

**Prueba independiente**: una persona abre la aplicación con el dispositivo en modo oscuro, cambia al tema claro, cierra el navegador y vuelve.

**Escenarios de aceptación**:

1. **AC-12.1** — **Dado** un dispositivo configurado en modo oscuro y sin elección previa, **cuando** la persona abre la aplicación, **entonces** la ve en tema oscuro; con el dispositivo en modo claro, en tema claro.
2. **AC-12.2** — **Dado** cualquier pantalla, **cuando** la persona usa el selector de tema ("Claro", "Oscuro", "Según el dispositivo"), **entonces** el tema cambia de inmediato sin perder lo que estaba haciendo.
3. **AC-12.3** — **Dado** que la persona eligió un tema, **cuando** vuelve otro día con el mismo navegador, **entonces** la aplicación usa el tema elegido, también como visitante.
4. **AC-12.4** — **Dado** el tema oscuro, **cuando** se revisan avisos, etiquetas de estado, tablas, calendario, gráficos, foco y pie de página, **entonces** todos mantienen los contrastes de NFR-002 y el mismo significado de color que en el tema claro.

---

### Historia de usuario 13 (HU-13) — Interfaz con sensación de calidad (Prioridad: P3)

Como persona usuaria, quiero que la aplicación se perciba fluida y cuidada.

**Por qué esta prioridad**: aporta a la percepción de calidad (CE-8), pero no a ninguna tarea concreta.

**Prueba independiente**: una persona recorre la aplicación con y sin la preferencia "reducir movimiento" activada en su dispositivo.

**Escenarios de aceptación**:

1. **AC-13.1** — **Dado** menús, confirmaciones, avisos y cambios de pantalla, **cuando** aparecen o desaparecen, **entonces** lo hacen con una transición breve (desvanecimiento de no más de 250 ms) que no demora la tarea.
2. **AC-13.2** — **Dado** un dispositivo con "reducir movimiento" activado, **cuando** la persona usa la aplicación, **entonces** no ve transiciones ni animaciones de desplazamiento; la barra de progreso y los indicadores de actividad siguen informando el avance sin animación de movimiento.
3. **AC-13.3** — **Dado** un contenido que se carga después de mostrar la página (por ejemplo, el avance de una extracción o un listado que se actualiza), **cuando** todavía no llegó, **entonces** se ve un marcador de posición con la forma del contenido, nunca un espacio en blanco, y la página no salta al aparecer el contenido.
4. **AC-13.4** — **Dado** botones, tarjetas, campos y menús de distintas pantallas, **cuando** se los compara, **entonces** comparten radios de esquina, sombras, espaciados, alturas y tamaños de letra de un único sistema (RN-11).
5. **AC-13.5** — **Dado** las acciones principales, **cuando** se las mira, **entonces** sus iconos son de un único estilo y siempre acompañan a una etiqueta de texto; ninguna acción principal es solo un icono. El botón de acciones (⋮) tiene un nombre accesible ("Acciones de la extracción del 21/11/2026 12:15").

---

### Historia de usuario 14 (HU-14) — Usar la aplicación sin notar su renovación (Prioridad: P1 durante la renovación)

Como persona usuaria, quiero que la aplicación funcione igual mientras sus pantallas se renuevan una por una, sin volver a ingresar ni perder lo que hice.

**Por qué esta prioridad**: el plan renueva la tecnología de las pantallas de a una (Etapas 2 y 3); durante semanas conviven pantallas renovadas y sin renovar. Si la persona nota la diferencia o pierde su sesión, la renovación empeora la experiencia en lugar de mejorarla. Solo aplica mientras dure la renovación (Clarifications 21/11/2026, planificación).

**Prueba independiente**: con al menos una pantalla renovada, una persona ingresa, recorre pantallas renovadas y sin renovar, realiza una acción en cada una, sale y vuelve a entrar; luego el responsable vuelve una pantalla a su versión anterior y la persona repite el recorrido.

**Escenarios de aceptación**:

1. **AC-14.1** — **Dado** una persona con sesión iniciada, **cuando** pasa de una pantalla sin renovar a una renovada y viceversa, **entonces** sigue con la sesión iniciada, ve el mismo encabezado (sección activa, menú de cuenta, tema elegido) y no se le pide ingresar de nuevo.
2. **AC-14.2** — **Dado** una persona con sesión iniciada, **cuando** elige "Salir" en cualquier pantalla, **entonces** ninguna pantalla, renovada o no, muestra después sus datos privados; al abrir "Mis jugadas" se le pide ingresar.
3. **AC-14.3** — **Dado** una acción que termina en una pantalla servida por la otra versión (por ejemplo, ingresar y volver a "Mis jugadas"), **cuando** la pantalla de destino se muestra, **entonces** el aviso de la acción aparece en ella (RN-09).
4. **AC-14.4** — **Dado** que la sesión vence mientras se completa un formulario de una pantalla renovada y "Ingresar" todavía no está renovada, **cuando** la persona ingresa de nuevo, **entonces** ve "Volver al formulario" y, al elegirlo, el formulario aparece completo para revisarlo y enviarlo; nada se envía solo (FR-032).
5. **AC-14.5** — **Dado** una pantalla renovada y su versión anterior, **cuando** se comparan con los mismos datos y el mismo perfil, **entonces** muestran los mismos datos, textos, direcciones, permisos y mensajes, y cumplen los mismos criterios de aceptación de HU-01 a HU-13. Solo pueden diferir el tipo de transición y la interactividad adicional que no reemplaza ninguna información.
6. **AC-14.6** — **Dado** que la versión renovada de una pantalla no responde (situación que el responsable o la persona desarrolladora preparan para la prueba), **cuando** la persona la abre, **entonces**, mientras exista la versión anterior, la ve con ella; si ya no existe, ve una página que explica que el servicio no está disponible y que se puede volver a intentar en unos minutos, con el pie legal.

---

### Casos límite (Edge Cases)

| Situación | Comportamiento esperado | Criterio |
|-----------|-------------------------|----------|
| La extracción termina con error a mitad de camino | Los sorteos afectados quedan "No recuperado" ([002] I-09), la extracción se muestra "Con error" (RN-01) y el detalle explica qué falló en cada sorteo. | AC-3.4 |
| La persona cierra la pestaña con una extracción en curso | Al volver ve el estado real, sin iniciar otra. | AC-3.6 |
| Se pierde la conexión durante una acción | Se muestra "No se pudo conectar. Es necesario comprobar la conexión y volver a intentarlo." con "Reintentar"; reintentar no duplica el efecto (no crea dos jugadas ni dos extracciones, no elimina dos veces). | FR-031 |
| La sesión vence mientras se completa un formulario | Se invita a ingresar de nuevo; lo escrito viaja con el pedido de ingreso y, tras ingresar, el formulario se muestra completo para revisarlo y enviarlo (no se envía solo). Si la persona no ingresa o cierra la pestaña, lo escrito se pierde y no queda guardado en el navegador. | FR-032 |
| Listado de extracciones vacío, con un elemento o con cientos | Vacío: estado vacío orientador. Uno: sin paginación. Cientos: paginación de 20 y orden. | AC-8.1, AC-9.2 |
| Correos muy largos o textos extensos | Se abrevian con puntos suspensivos sin romper la fila ni la tarjeta; el texto completo se lee al enfocar o en el detalle. Nada desborda a 360 px. | FR-030 |
| Lector de pantalla, solo teclado, zoom al 200 % o movimiento reducido | Todas las tareas principales se completan. | NFR-001, NFR-003 |
| 29/02 en año bisiesto, inicio igual a fin, fechas futuras | 29/02/2024 válido, 29/02/2025 inválido; inicio igual a fin válido (un día); fechas futuras según la regla de cada formulario ([002] RN-01 a RN-04). | AC-4.5, AC-4.7 |
| Sin scripts en el navegador | Todas las funciones siguen disponibles con su versión básica (formularios, calendario del navegador, confirmación en página aparte, recarga para ver el avance). | NFR-007 |
| Dos administradores ven la misma extracción y uno la elimina | El otro, al intentar abrirla o eliminarla, ve "La extracción ya no existe" y vuelve al listado. | FR-006 |
| Filtro y paginación combinados que dejan una página vacía | Se muestra la última página con datos o el estado vacío de filtro con "Limpiar filtros". | AC-8.3 |

---

## Requisitos (Requirements) *(obligatorio)*

### Requisitos funcionales (Functional Requirements)

**Estado de las extracciones (HU-01, HU-03)**

- **FR-001**: Cada extracción DEBE mostrar, en el listado y en su detalle, una etiqueta de estado con texto corto, icono y color, según RN-01. *(HU-01)*
- **FR-002**: La etiqueta DEBE ofrecer su explicación completa (RN-02) al pasar el cursor y al enfocarla con el teclado, y la misma explicación DEBE figurar en el detalle. *(HU-01)*
- **FR-003**: El listado DEBE permitir filtrar por estado, con la opción "Todos los estados" y una indicación visible del filtro aplicado. *(HU-01)*
- **FR-004**: Al pulsar "Iniciar extracción", el botón DEBE pasar a un estado de trabajo no pulsable y la extracción DEBE aparecer en el listado como "En curso" sin recargar la página. *(HU-03)*
- **FR-005**: Mientras una extracción está en curso, la pantalla DEBE mostrar su actividad y su avance ([002] FR-003) y, al terminar, actualizar su estado y mostrar un aviso con el resultado, sin recargar. *(HU-03)*
- **FR-006**: El sistema NO DEBE crear una extracción con el mismo período que otra en curso o en espera; DEBE informar el motivo y dar acceso a la existente (RN-03). *(HU-03)*

**Acciones y eliminación (HU-02)**

- **FR-007**: El menú de acciones de cada fila DEBE desplegarse junto a su botón, dentro de la pantalla, operarse con teclado (Intro, Espacio, flechas, Escape) y cerrarse al hacer clic fuera. *(HU-02)*
- **FR-008**: Eliminar una extracción DEBE pedir una confirmación que nombre la extracción (fecha y hora de inicio y período), indique qué se pierde, tenga "Cancelar" como acción predeterminada con el foco inicial y "Eliminar" con estilo destructivo. *(HU-02)*
- **FR-009**: La confirmación DEBE advertir "Esta acción no se puede deshacer." y, tras eliminar, el sistema DEBE mostrar un aviso breve que confirme la acción, sin opción "Deshacer"; la eliminación sigue [002] RN-44 sin cambios (D-03). *(HU-02)*

**Fechas (HU-04)**

- **FR-010**: Todos los campos de fecha de la aplicación DEBEN presentarse igual: ancho acorde a dd/mm/aaaa, escritura con barras automáticas ([002] D-27) y un calendario propio con el estilo de la aplicación, semana desde el lunes y nombres en español. *(HU-04)*
- **FR-011**: Los formularios de período DEBEN permitir elegir inicio y fin en un único calendario, y ofrecer los atajos de RN-04. *(HU-04)*
- **FR-012**: El sistema DEBE rechazar fechas imposibles y fines anteriores al inicio con un mensaje concreto junto al campo, al salir del campo y al enviar; las reglas de fechas de [001] y [002] no cambian. *(HU-04)*
- **FR-013**: El calendario NO DEBE tapar el campo que se completa, DEBE cerrarse con Escape y DEBE poder usarse completo con el teclado. *(HU-04)*

**Navegación e identidad (HU-05)**

- **FR-014**: El encabezado DEBE indicar la sección actual con más de un rasgo visual y anunciarla como página actual a los lectores de pantalla. *(HU-05)*
- **FR-015**: Los elementos de navegación DEBEN tener un área de toque de al menos 44 × 44 px y no ir subrayados; "Salir" DEBE estar dentro de un menú de cuenta que muestre el correo de la persona conectada. *(HU-05)*
- **FR-016**: Entre 360 px y 767 px de ancho, la navegación DEBE condensarse en un menú desplegable operable con teclado y lector de pantalla. *(HU-05)*
- **FR-017**: Toda pantalla DEBE ofrecer "Saltar al contenido" como primer elemento enfocable, y toda página interna un camino de regreso con el nombre del destino. *(HU-05)*
- **FR-018**: La aplicación DEBE tener logotipo, isotipo y favicon propios (RN-08). *(HU-05)*

**Ingreso y cuentas (HU-06)**

- **FR-019**: Las pantallas "Ingresar" y "Crear cuenta" DEBEN presentar el formulario centrado en una tarjeta, con mostrar/ocultar contraseña, autocompletado compatible con navegadores y gestores de contraseñas, errores de formato junto a cada campo antes de enviar, y botón en estado de trabajo mientras se verifica. *(HU-06)*
- **FR-020**: Los mensajes de ingreso NO DEBEN revelar si un correo está registrado ([001] AC-3.5 sin cambios). *(HU-06)*
- **FR-021**: Esta feature NO DEBE agregar recuperación de contraseña ni un enlace hacia ella; [001] D-15 sigue vigente (D-02). *(HU-06)*

**Estadísticas (HU-07)**

- **FR-022**: Los filtros de Estadísticas DEBEN mostrar todas las opciones completas, compartir línea base en escritorio y reorganizarse en filas en pantallas chicas; las etiquetas DEBEN ser breves, con formato y rango en una ayuda asociada. *(HU-07)*
- **FR-023**: "Consultar un número" DEBE presentarse como un bloque separado de los filtros del período, y un número fuera de 00–45 DEBE rechazarse con un mensaje inmediato junto al campo. *(HU-07)*
- **FR-024**: Los resultados de Estadísticas DEBEN mostrarse con un gráfico de frecuencia por número y una tabla ordenable por cada columna; los cálculos de [001] no cambian. *(HU-07)*

**Estados vacíos, tablas y avisos (HU-08, HU-09, HU-10)**

- **FR-025**: Cada estado vacío DEBE cumplir RN-06 y distinguir "sin datos todavía" de "el filtro no devolvió nada" (este último con "Limpiar filtros"). *(HU-08)*
- **FR-026**: El estado vacío de Resultados sin sorteos DEBE ofrecer al administrador, y solo a él, accesos a "Cargar sorteo" y a "Extracción histórica". *(HU-08)*
- **FR-027**: El listado de extracciones DEBE poder ordenarse por fecha, período y estado, paginarse según RN-07, transformarse en tarjetas en pantallas chicas y abrir el detalle al hacer clic en cualquier parte de la fila. *(HU-09)*
- **FR-028**: Los nombres de columnas y el formato de fechas DEBEN ser uniformes en toda la aplicación (RN-05, Const. VII). *(HU-09)*
- **FR-029**: Las advertencias de interpretación y el pie legal DEBEN presentarse según AC-10.1 y AC-10.2, y todos los mensajes según RN-09. *(HU-10)*

**Robustez de la interacción (casos límite, 6.3 del pedido)**

- **FR-030**: Ningún texto extenso (correos, períodos, motivos) DEBE romper filas, tarjetas o encabezados; se abrevia con el texto completo accesible. *(Casos límite)*
- **FR-031**: Ante una falla de conexión, la aplicación DEBE informarla y permitir reintentar sin duplicar el efecto de la acción. *(Casos límite)*
- **FR-032**: Si la sesión vence mientras se completa un formulario, el sistema DEBE invitar a ingresar de nuevo, llevar lo escrito junto con el pedido de ingreso y, tras ingresar, mostrar el formulario completo para que la persona lo revise y lo envíe. Si el formulario y "Ingresar" pertenecen a versiones distintas durante la renovación, tras ingresar DEBE ofrecerse "Volver al formulario", que lo abre completo (AC-14.4). Lo escrito NO DEBE guardarse en el navegador ni enviarse automáticamente; si la persona no ingresa, se pierde. Tras el ingreso, se verifican de nuevo los permisos (por ejemplo, la jugada se registra para la persona que ingresó). *(Casos límite; Clarifications 21/11/2026)*
- **FR-033**: Ningún formulario DEBE enviarse con datos obligatorios vacíos o inválidos: el sistema DEBE señalar cada campo con su mensaje junto a él, mover el foco al primero y, si la persona pulsa el botón, explicar por qué no avanza (por ejemplo, "Falta la fecha de finalización"). La validación se repite en el servidor. *(6.3 del pedido, CE-10)*
- **FR-034**: Toda acción que tarde más de 1 segundo DEBE mostrar una respuesta visible (estado de trabajo del botón, indicador de actividad o marcador de posición). *(7 del pedido, HU-13)*

**Lenguaje, tema y acabado (HU-11, HU-12, HU-13)**

- **FR-035**: Todos los textos visibles DEBEN usar la forma impersonal o neutra (D-01), botones con verbo inicial y los términos del glosario (RN-10). *(HU-11)*
- **FR-036**: La aplicación DEBE respetar el tema del dispositivo y permitir elegir "Claro", "Oscuro" o "Según el dispositivo"; la elección DEBE recordarse en ese navegador entre visitas. *(HU-12)*
- **FR-037**: Menús, confirmaciones, avisos y cambios de pantalla DEBEN usar transiciones breves que se desactivan con "reducir movimiento"; los contenidos que cargan después DEBEN mostrar marcadores de posición con su forma. *(HU-13)*
- **FR-038**: Todos los componentes DEBEN seguir un único sistema visual (RN-11) y la paleta de RN-12. *(HU-13, 6 del pedido)*

**Convivencia durante la renovación (HU-14)** — aplican mientras convivan pantallas renovadas y sin renovar (Clarifications 21/11/2026, planificación)

- **FR-039**: La sesión iniciada DEBE mantenerse al pasar entre pantallas renovadas y sin renovar, con las mismas reglas de vencimiento y bloqueo de [001], sin pedir ingresar de nuevo. *(HU-14, AC-14.1)*
- **FR-040**: "Salir" DEBE cerrar la sesión para todas las pantallas a la vez. *(HU-14, AC-14.2)*
- **FR-041**: Una pantalla renovada DEBE mostrar los mismos datos, textos, direcciones, permisos y mensajes que su versión anterior y cumplir los mismos criterios de aceptación; solo pueden diferir el tipo de transición y la interactividad adicional que no reemplaza información. *(HU-14, AC-14.5)*
- **FR-042**: Cada pantalla renovada DEBE poder volver a su versión anterior sin cambiar sus direcciones ni perder datos, mientras esa versión exista. *(HU-14)*
- **FR-043**: Los avisos de una acción DEBEN mostrarse en la pantalla de destino aunque pertenezca a la otra versión. *(HU-14, AC-14.3)*
- **FR-044**: Si la versión renovada de una pantalla no responde, la pantalla DEBE mostrarse con su versión anterior mientras exista; si ya no existe, DEBE mostrarse una página de servicio no disponible con el pie legal. *(HU-14, AC-14.6)*

### Requisitos de calidad (no funcionales)

- **NFR-001 (Accesibilidad)**: Todas las pantallas cumplen WCAG 2.2 nivel AA (reemplaza la referencia a WCAG 2.1 AA de [002] NFR-003): foco de teclado siempre visible y no tapado por otros elementos; orden lógico de tabulación; todas las acciones disponibles con teclado; cada campo con etiqueta asociada; errores y avisos anunciados a lectores de pantalla; la información nunca se transmite solo por color; objetivos táctiles de al menos 44 × 44 px en móvil.
- **NFR-002 (Contraste)**: Texto, incluidos marcadores de posición, ayudas y pie de página, con contraste de al menos 4,5:1 sobre su fondo en ambos temas; iconos informativos, bordes de campos y foco con al menos 3:1.
- **NFR-003 (Adaptabilidad)**: Uso completo desde 360 px de ancho hasta pantallas grandes; sin desplazamiento horizontal de la página en ningún tamaño (las tablas anchas se transforman en tarjetas); el texto puede ampliarse al 200 % sin perder contenido ni funciones.
- **NFR-004 (Estabilidad visual)**: Ninguna pantalla salta al cargar: fuentes, imágenes, logotipo, gráficos y marcadores de posición reservan su espacio.
- **NFR-005 (Respuesta)**: Toda acción muestra una respuesta visible en menos de 100 ms (cambio de estado del botón, apertura del menú) aunque el resultado tarde más.
- **NFR-006 (Localización)**: Se mantiene Const. VII: español de Argentina, fechas dd/mm/aaaa, horas HH:MM, importes $ 1.234,56 y números con dos dígitos; el calendario, en español y con la semana desde el lunes.
- **NFR-007 (Mejora progresiva)**: Toda función sigue disponible si el navegador no ejecuta scripts, en su versión básica (ver Casos límite). Las mejoras de interacción no reemplazan las verificaciones del servidor.
- **NFR-008 (Seguridad y privacidad sin cambios)**: Las pantallas y componentes nuevos respetan los permisos actuales por perfil, verificados en el servidor; el correo de quien ejecutó una extracción solo lo ven los administradores ([002]); las páginas privadas siguen sin guardarse en caché; en el navegador solo se recuerda la preferencia de tema (FR-036); lo escrito en formularios no se guarda allí (FR-032). "No se guarda en el servidor" significa que ningún servidor lo registra ni lo conserva después de responder: leer la preferencia de tema para mostrar la página, o reenviar en tránsito el formulario pendiente entre partes de la aplicación, está permitido (Clarifications 21/11/2026, planificación).
- **NFR-009 (Sin cambios de negocio)**: Los resultados, premios, estadísticas, jugadas, extracciones y el CSV muestran exactamente los mismos datos que antes de esta feature; solo cambia su presentación.

### Reglas de presentación

Estado: **Aprobada** = surge directamente del pedido, de la Constitución o de una spec aprobada. **Propuesta** = derivada por el agente, a confirmar en `/speckit-clarify`.

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-01 | **Etiquetas de estado de una extracción**, derivadas de los estados de [002] sin cambiar sus reglas: **En curso** (azul, indicador de actividad) — en curso o en espera de turno; **Finalizada** (verde, ✓) — "Extracción finalizada" de [002] RN-33; **Con advertencias** (ámbar, ⚠) — "Extracción finalizada con advertencias que requieren revisión" sin ningún sorteo "No recuperado" (hay sorteos "Recuperado parcialmente" o "Con inconsistencias"); **Sin sorteos** (gris, ○) — "No se identificaron sorteos en el período consultado" ([002] AC-1.10); **Con error** (rojo, ✕) — finalizada con **al menos un** sorteo "No recuperado" ([002] RN-31), sin importar el estado de los demás. "Con error" tiene precedencia sobre "Con advertencias". | Aprobada (Clarifications 21/11/2026, `/speckit-clarify`) | HU-01 |
| RN-02 | **Explicaciones de cada estado**: En curso — "La extracción se está procesando. El avance se actualiza en esta pantalla."; Finalizada — "Todos los sorteos del período se recuperaron sin novedades."; Con advertencias — "Hay sorteos del período que requieren revisión manual. El detalle los muestra."; Sin sorteos — "Las fuentes no informaron sorteos en el período consultado."; Con error — "Hay sorteos del período que no se pudieron recuperar. El detalle muestra cuáles y qué respondió cada fuente." Forma neutra (D-01). | Aprobada (Con advertencias, del pedido; las demás, 21/11/2026 con el contrato de mensajes) | HU-01 |
| RN-03 | **Extracciones idénticas**: dos extracciones son idénticas si tienen la misma fecha de inicio y de finalización. No puede iniciarse una idéntica a otra en curso o en espera; sí a una terminada, y sí una con un período que solo se superpone en parte (por ejemplo, 01/01/2024–30/06/2024 mientras está en curso 01/03/2024–31/12/2024). | Aprobada (Clarifications 21/11/2026, `/speckit-clarify`) | HU-03 |
| RN-04 | **Atajos de período** (calculados a la fecha de hoy en America/Argentina/Buenos_Aires): **Año en curso** — del 01/01 del año actual hasta hoy (el 01/01, inicio igual a fin); **Año anterior** — del 01/01 al 31/12 del año calendario anterior; **Todo el historial** — desde la fecha del primer sorteo publicado hasta hoy. Atajos por formulario: **Extracción histórica** — "Año en curso" y "Año anterior" (ambos dentro del máximo de 12 meses de [002] RN-04); **Estadísticas** — "Año en curso", "Año anterior" y "Todo el historial". | Aprobada (Clarifications 21/11/2026, `/speckit-clarify`) | HU-04 |
| RN-05 | **Nombres de columnas**: un mismo dato lleva el mismo nombre en todas las pantallas; la fecha y hora de inicio de una extracción se llama "Fecha" ([002] D-24) y la fecha de un sorteo, "Fecha del sorteo". La lista definitiva de nombres se fija con el glosario (RN-10). | Aprobada | HU-09 |
| RN-06 | **Estado vacío**: icono o ilustración, título, explicación breve y, si existe una acción permitida para el perfil, un botón con esa acción. "Sin datos todavía" y "Sin resultados para el filtro" son variantes distintas; la segunda nombra el filtro y ofrece "Limpiar filtros". | Aprobada | HU-08 |
| RN-07 | **Paginación**: 20 elementos por página en el listado de extracciones; se muestra la página actual, el total de páginas y los accesos "Anterior" y "Siguiente"; el filtro y el orden se conservan al cambiar de página. | Aprobada (21/11/2026, con el contrato de mensajes del plan) | HU-09 |
| RN-08 | **Identidad**: logotipo, isotipo y favicon originales de QUINI_6, sobrios y acordes al tono de 6.2 del pedido; NO reproducen ni imitan el logotipo, los colores institucionales ni la marca oficial del Quini 6 ni de la Lotería de Santa Fe, ni sugieren que QUINI_6 sea un sitio oficial (Const. V, VIII). | Aprobada (21/11/2026, con el contrato de mensajes del plan) | HU-05 |
| RN-09 | **Mensajes**: cuatro tipos (éxito, información, advertencia, error) con icono, color de fondo tenue, borde del color pleno y texto oscuro (RN-12); se anuncian a los lectores de pantalla; los avisos breves (toasts) se cierran solos a los 6 s salvo los de error, que permanecen hasta cerrarlos, y todos pueden cerrarse con el teclado. | Aprobada (21/11/2026, con el contrato de mensajes del plan) | HU-10 |
| RN-10 | **Glosario único** de la interfaz (el contrato de mensajes del plan lo aplica y lo completa sin contradecirlo): **Sorteo** — el evento con número y fecha ("Sorteo N.º 3250", "Fecha del sorteo"); reemplaza a "concurso" en todos los textos visibles; **Modalidad** — cada juego de un sorteo (Tradicional – Primer Sorteo, La Segunda, Revancha, Siempre Sale, Premio Extra); **Números sorteados** — los seis números de una modalidad (no se llaman "extracción" en la interfaz); **Jugada** — la boleta que una persona registra; **Extracción histórica** — el proceso de administración de [002], siempre con ese nombre completo. Términos que no se usan en la interfaz: "concurso" y "extracción" sola para referirse a números. El cambio es solo de textos visibles: los nombres internos, las direcciones y el CSV de [002] no cambian. | Aprobada (Clarifications 21/11/2026, `/speckit-clarify`, D-04) | HU-11 |
| RN-11 | **Sistema visual**: una única escala de espaciados, radios de esquina, sombras, alturas de controles y tamaños de letra; tarjetas con fondo blanco (o su equivalente oscuro), esquinas redondeadas y sombra sutil; botones grandes con estados de cursor, foco y pulsación; un único botón principal por pantalla; tipografía sans-serif sobria sin fuentes decorativas; en escritorio, contenido centrado con ancho de lectura limitado; en móvil, una columna con botones principales a todo el ancho y al alcance del pulgar. | Aprobada (6.2 y 6.3 del pedido) | HU-13 |
| RN-12 | **Paleta**: azul corporativo `#1E40AF` (encabezado, botones principales, enlaces, sección activa); naranja de acento `#F97316` (cifras clave y resaltados no críticos, nunca en el mismo botón que el azul); fondo claro `#F3F4F6`; texto `#1F2937`; verde positivo `#10B981`; rojo negativo `#EF4444`. Verde y rojo siempre con icono y texto. El naranja, el verde y el rojo plenos se usan para iconos, bordes y rellenos sin texto pequeño; cuando acompañan texto se usan variantes más oscuras del mismo tono para el texto, o texto oscuro sobre un fondo tenue de ese tono, hasta cumplir NFR-002. Cada color tiene su equivalente en tema oscuro con el mismo significado. | Aprobada (6.1 del pedido) | HU-12, HU-13 |

### Entidades clave (Key Entities)

Esta feature no agrega datos de negocio. Solo involucra:

- **Preferencia de tema**: elección "Claro", "Oscuro" o "Según el dispositivo" de una persona, recordada en su navegador; no se asocia a la cuenta ni se guarda en el servidor (el servidor puede leerla para mostrar la página con ese tema, sin registrarla; NFR-008).
- **Etiqueta de estado de extracción**: presentación derivada del estado y del resumen de cada extracción de [002] (RN-01); no se guarda.
- **Formulario pendiente**: lo escrito en un formulario al vencer la sesión (FR-032); viaja una sola vez con el pedido de ingreso y no se guarda ni en el navegador ni en el servidor.

### Dependencias

- Estados, resumen, avance y eliminación de extracciones de [002] (RN-31, RN-33, RN-44, FR-003, D-24, D-26, D-27).
- Mensajes, reglas de fechas y comportamiento de cuentas de [001] (AC-3.5, NFR-005) y sus catálogos de mensajes (`contracts/mensajes.md` de [001] y [002]), que esta feature actualiza en su tratamiento y glosario.
- Cálculos de estadísticas de [001], sin cambios.

---

## Criterios de éxito (Success Criteria) *(obligatorio)*

### Resultados medibles (Measurable Outcomes)

Las pruebas con usuarios se hacen con al menos 5 participantes por perfil involucrado, que no hayan usado la versión nueva, sin ayuda ni instrucciones.

- **SC-001** (CE-1): En un listado con extracciones en los cinco estados, al menos el 90 % de los administradores identifica, sin ayuda, todas las que tienen advertencias o error.
- **SC-002** (CE-2): 0 eliminaciones accidentales en las pruebas de usabilidad (una eliminación es accidental si la persona no tenía la consigna de eliminar esa extracción).
- **SC-003** (CE-3): Un administrador nuevo lanza la extracción de un año en menos de 30 s, medidos desde que abre la pantalla hasta que ve la extracción "En curso".
- **SC-004** (CE-4): Una auditoría de accesibilidad automática de todas las pantallas, en ambos temas y en 360 px y escritorio, informa 0 incumplimientos críticos y 0 graves.
- **SC-005** (CE-5): En una revisión manual solo con teclado y con un lector de pantalla, se completan todas las tareas principales: consultar resultados, consultar estadísticas, ingresar, crear cuenta, registrar, ver y eliminar una jugada, iniciar, seguir, abrir, descargar y eliminar una extracción.
- **SC-006** (CE-6): Todas las pantallas, a 360 px de ancho y con el texto al 200 %, sin desplazamiento horizontal de la página y sin contenido ni funciones perdidas.
- **SC-007** (CE-7): Una revisión de todos los textos visibles encuentra 0 textos con tratamiento distinto al elegido y 0 nombres de columna contradictorios entre pantallas.
- **SC-008** (CE-8): En una encuesta breve tras la prueba, la percepción de modernidad y profesionalismo promedia al menos 4 sobre 5.
- **SC-009** (CE-9): El 100 % de las combinaciones de color usadas para texto alcanzan 4,5:1 y el 100 % de las usadas para iconos informativos, bordes y foco alcanzan 3:1, en ambos temas.
- **SC-010** (CE-10): El 100 % de los formularios impiden enviar o avanzar con datos obligatorios vacíos o inválidos, señalan cada campo con su mensaje y llevan el foco al primero.
- **SC-011**: Ninguna pantalla muestra datos de negocio distintos de los que mostraba antes de la feature, y el CSV de [002] generado para un mismo período es idéntico en estructura (NFR-009).
- **SC-012** (HU-14): En cada pantalla renovada, el recorrido de AC-14.1 a AC-14.5 se completa sin volver a ingresar, sin avisos perdidos y sin diferencias de datos, textos ni permisos respecto de su versión anterior; y al volverla a su versión anterior, el mismo recorrido se completa igual.

---

## Supuestos (Assumptions)

- **Tratamiento**: los textos de esta spec ya usan la forma neutra (D-01). Los textos exactos de cada pantalla se fijan en el contrato de mensajes del plan.
- **"Con error"**: [002] no tiene un estado de error para una extracción completa; los errores de una fuente o de un sorteo dejan ese sorteo "No recuperado" y la extracción continúa. "Con error" es solo una etiqueta de presentación (RN-01, Clarifications 21/11/2026): no se agrega un estado nuevo a la extracción ni se cambia [002] RN-33.
- **Calendario**: el calendario propio reemplaza, como mejora, el selector de fecha del navegador de [002] D-25; se conserva [002] D-27 (escribir la fecha con el teclado y barras automáticas, sin que el calendario tome las teclas). Sin scripts, se usa el campo de fecha del navegador.
- **Confirmación de eliminación**: con scripts, la confirmación aparece en un cuadro sobre la página; sin ellos, se conserva la página de confirmación aparte de [002].
- **Tema**: se recuerda solo en el navegador de la persona; cambiar de dispositivo no lo traslada.
- **Marcadores de posición**: las pantallas se generan completas en el servidor, así que solo se aplican a los contenidos que se actualizan o cargan después de mostrar la página (avance de extracción, listados que se refrescan).
- **Transición entre pantallas**: se aplica donde el navegador la soporte; en los demás, el cambio es inmediato, sin pérdida de funciones.
- **Gráfico de estadísticas**: ya existe un gráfico de frecuencia; se mejora su presentación y se agrega el orden de la tabla, sin cambiar los cálculos.
- **Acceso a "Extracción histórica" desde Resultados vacío** (AC-8.4): es solo un acceso directo; la extracción sigue sin cargar sorteos en la aplicación ([002] RN-41), y el estado vacío lo aclara ("La extracción histórica genera un archivo CSV; no carga sorteos en la aplicación").
- **Pruebas con usuarios** (SC-001 a SC-003, SC-008): las organiza el responsable del proyecto con al menos 5 participantes por perfil; las auditorías y revisiones (SC-004 a SC-007, SC-009 a SC-011) se pueden hacer sin participantes.

---

## Decisiones pendientes

### D-01 — Tratamiento de la interfaz — **Resuelta (21/11/2026)**

Forma impersonal o neutra en toda la interfaz (Clarifications 21/11/2026). Ver AC-11.1 y FR-035.

### D-02 — Recuperación de contraseña — **Resuelta (21/11/2026)**

Sin enlace ni recuperación en esta feature; [001] D-15 sigue vigente y la recuperación pasa a "Propuestas futuras" (Clarifications 21/11/2026). Ver AC-6.3 y FR-021.

### D-03 — "Deshacer" tras eliminar una extracción — **Resuelta (21/11/2026)**

Sin "Deshacer": la confirmación advierte que la acción no se puede deshacer (Clarifications 21/11/2026). Ver AC-2.3, AC-2.5 y FR-009.

### D-04 — Glosario y uso de "sorteo" frente a "concurso" — **Resuelta (21/11/2026)**

[001] llamaba "concurso" al evento numerado y "extracción" a los números de cada modalidad; [002] llama "sorteo" al mismo evento y "extracción" al proceso de administración. Se unifica en "sorteo" para el evento, "números sorteados" para los de cada modalidad y "extracción histórica" para el proceso (RN-10). Afecta textos visibles de [001] y [002], no el CSV ni los nombres internos.

---

## Relación con las especificaciones 001 y 002

| Punto | Antes | Con esta spec |
|-------|-------|---------------|
| [002] D-25 / D-27 — calendario | Selector de fecha del navegador, abierto con su icono | Calendario propio con el estilo de la aplicación; se conserva la escritura con barras automáticas; sin scripts, el del navegador. |
| [002] D-24 / AC-1.18 — eliminación | Menú ⋮ y página de confirmación aparte | Menú junto a su botón, con teclado y Escape; confirmación que nombra la extracción, con "Cancelar" predeterminado. Sin scripts, la página aparte sigue igual. |
| [002] AC-1.9 / RN-33 — resultado global | Texto completo en el listado | Etiqueta corta con icono y color (RN-01); el texto completo sigue en el detalle. |
| [002] NFR-003 | WCAG 2.1 AA | WCAG 2.2 AA en todas las pantallas (NFR-001). |
| [002] RN-44 — listado | Orden de más reciente a más antigua | Mismo orden inicial, más orden por columna, filtro por estado y paginación. |
| [001] D-15 — recuperación de contraseña | Fuera del MVP | Sin cambios: sigue fuera del alcance (D-02). |
| Catálogos de mensajes de [001] y [002] | Tratamiento mixto, mayormente voseo; "concurso" en [001] y "sorteo" en [002] | Forma neutra (D-01) y "sorteo" en toda la interfaz (D-04, RN-10); los textos que cambian se registran en el contrato de mensajes de esta feature, con su texto anterior. |

---

## Propuestas futuras (fuera del alcance de esta especificación)

- Recuperación de contraseña (HU-06, D-02): requiere aprobar el envío de correos excluido por [001] D-15.
- Guardar la preferencia de tema en la cuenta para que siga a la persona entre dispositivos.
- Avisos fuera de la pantalla (por ejemplo, notificación del navegador) cuando termina una extracción.
- Filtros y orden en otros listados (Mis jugadas, Resultados) con los mismos componentes.

---

## Trazabilidad

| Historia (pedido) | Criterios | Requisitos | Reglas | Éxito |
|-------------------|-----------|------------|--------|-------|
| HU-01 | AC-1.1 a AC-1.5 | FR-001 a FR-003 | RN-01, RN-02 | SC-001 |
| HU-02 | AC-2.1 a AC-2.6 | FR-007 a FR-009 | — | SC-002 |
| HU-03 | AC-3.1 a AC-3.6 | FR-004 a FR-006 | RN-03 | SC-003 |
| HU-04 | AC-4.1 a AC-4.7 | FR-010 a FR-013 | RN-04 | SC-010 |
| HU-05 | AC-5.1 a AC-5.7 | FR-014 a FR-018 | RN-08 | SC-005, SC-006 |
| HU-06 | AC-6.1 a AC-6.7 | FR-019 a FR-021 | — | SC-005, SC-010 |
| HU-07 | AC-7.1 a AC-7.6 | FR-022 a FR-024 | — | SC-006, SC-010 |
| HU-08 | AC-8.1 a AC-8.4 | FR-025, FR-026 | RN-06 | — |
| HU-09 | AC-9.1 a AC-9.5 | FR-027, FR-028 | RN-05, RN-07 | SC-006, SC-007 |
| HU-10 | AC-10.1 a AC-10.3 | FR-029 | RN-09 | SC-009 |
| HU-11 | AC-11.1 a AC-11.3 | FR-035 | RN-10 | SC-007 |
| HU-12 | AC-12.1 a AC-12.4 | FR-036 | RN-12 | SC-009 |
| HU-13 | AC-13.1 a AC-13.5 | FR-034, FR-037, FR-038 | RN-11, RN-12 | SC-008 |
| HU-14 (planificación) | AC-14.1 a AC-14.6 | FR-039 a FR-044 | — | SC-012 |
| Transversales (7 del pedido) | Casos límite | FR-030 a FR-034 | — | SC-004 a SC-006, SC-009 a SC-011 |
