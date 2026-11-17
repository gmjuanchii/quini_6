# Especificación funcional (Feature Specification): QUINI_6 — MVP v0

**Feature Branch**: `001-quini6-mvp` (el proyecto no es un repositorio git; no se creó rama)

**Created**: 13/11/2026

**Status**: Aprobada por el responsable del proyecto (13/11/2026). Reglas de premios incorporadas y discrepancias con el reglamento resueltas. Quedan decisiones no bloqueantes en "Decisiones pendientes"

**Input**: Descripción del responsable del proyecto: "SpecKit Specify — Definición funcional del MVP de QUINI_6 (v0)": consulta pública de resultados, registro y autenticación, gestión de jugadas personales, seguimiento y comparación de jugadas, estadísticas históricas y administración de resultados.

**Marco normativo**: [Constitución del proyecto QUINI_6 v1.1.0](../../.specify/memory/constitution.md). Esta especificación no repite sus principios; los referencia por número (por ejemplo, "Const. VIII"). Ante un conflicto, prevalece la Constitución.

---

## Contexto y alcance

### Objetivo del MVP

Validar la propuesta de valor inicial de QUINI_6: que cualquier persona pueda consultar resultados y estadísticas del Quini 6 sin registrarse, y que un usuario registrado pueda llevar el seguimiento de las jugadas que hizo fuera de la aplicación y conocer sus aciertos y premios a partir de información oficial validada.

### Módulos incluidos

| Módulo | Actor principal | Historias |
|--------|-----------------|-----------|
| M1. Consulta pública de resultados | Visitante | US1 |
| M2. Administración de resultados (carga, validación, publicación) | Administrador | US2 |
| M3. Corrección de resultados publicados | Administrador | US7 |
| M4. Registro y autenticación | Visitante / Usuario registrado | US3 |
| M5. Gestión de jugadas personales | Usuario registrado | US4 |
| M6. Seguimiento y comparación de jugadas | Usuario registrado | US5 |
| M7. Estadísticas históricas | Visitante | US6 |

### Fuera del alcance de esta versión

Compra de cartones; realización de apuestas; pasarelas de pago; depósitos, retiros o saldos (Const. V). OCR de cartones o imágenes. Predicciones o recomendaciones de números, incluidas las basadas en inteligencia artificial. Notificaciones push, por correo electrónico o por mensajería. Comparaciones sociales entre usuarios. Aplicación móvil nativa. Integraciones automáticas con fuentes externas para obtener resultados. Cualquier automatización de carga no aprobada expresamente.

### Actores y permisos

| Capacidad | Visitante | Usuario registrado | Administrador |
|-----------|:---------:|:------------------:|:-------------:|
| Consultar resultados, premios, pozos y ganadores publicados | Sí | Sí | Sí |
| Consultar estadísticas históricas | Sí | Sí | Sí |
| Crear una cuenta, iniciar y cerrar sesión | Crear cuenta / iniciar sesión | Cerrar sesión | Iniciar y cerrar sesión |
| Registrar, consultar, editar y eliminar jugadas | No | Solo las propias | Solo las propias (una cuenta de administrador también es una cuenta de usuario) |
| Ver la comparación de jugadas con resultados | No | Solo las propias | Solo las propias |
| Ver jugadas de otros usuarios | No | No | No |
| Crear concursos, cargar resultados y premios | No | No | Sí |
| Validar y publicar información de concursos | No | No | Sí, incluida la que cargó él mismo (RN-17) |
| Corregir información publicada y ver su historial de cambios | No | No | Sí |

Nadie, ni siquiera un administrador, puede consultar las jugadas de otra cuenta en el MVP (Const. IV).

---

## Clarifications

### Session 2026-11-13

- Q: ¿Cómo se asocia una jugada registrada a las modalidades del Quini 6 y a Premio Extra? → A: Toda jugada participa en todas las modalidades aplicables a su concurso (RN-13), incluido Premio Extra cuando el concurso lo tiene; el usuario no elige modalidades.
- Q: ¿De dónde debe sacar la aplicación las reglas para decidir si una jugada tiene premio (categorías por modalidad y mecanismo de Premio Extra por período)? → A: Las categorías de cada modalidad se cargan desde el extracto oficial de cada concurso; el mecanismo de Premio Extra por período se toma de un anexo de reglamentación aportado y aprobado por el responsable del proyecto.
- Q: ¿Cómo se cargan en la aplicación los resultados de los concursos anteriores al lanzamiento? → A: Solo carga manual; el alcance del MVP incluye cargar y publicar, antes del lanzamiento, los concursos de los últimos 12 meses. No hay importación de archivos.
- Q: ¿Puede un usuario registrar una jugada para un concurso que un administrador todavía no creó en la aplicación? → A: No. Solo se registran jugadas en concursos ya creados; los administradores crean cada concurso próximo (número y fecha) antes del sorteo.
- Q: ¿Quién puede validar y publicar la información de un concurso: el mismo administrador que la cargó u otro distinto? → A: Un único rol de administrador; quien cargó la información puede validarla y publicarla, confirmando expresamente que la cotejó con el extracto oficial.
- Actualización del responsable del proyecto (13/11/2026, vía `/speckit-specify`): se aprueban las reglas de premios por modalidad (RN-49 a RN-54, RN-31 reescrita) y tres ejemplos de referencia. Cambios que esto obliga: RN-30 deja de cargar las categorías desde cada extracto; RN-29 separa estado de validación, aciertos, elegibilidad, resultado de premio e importe; y "Premio no determinable" pasa a llamarse "Premio pendiente de determinación".
- Q: ¿Premio Extra tiene solo la categoría de 6 aciertos o desciende a 5 y a 4 como indica el reglamento consultado? → A: Desciende como Siempre Sale (6; si no hay ganadores, 5; si no, 4), usando la categoría ganadora publicada en el extracto y manteniendo la exclusión de RN-53.
- Q: ¿Se mantiene que toda jugada registrada participa en todas las modalidades, aunque el reglamento consultado permite jugar solo Tradicional? → A: Sí, se mantiene RN-05.
- Q: ¿Puede un usuario registrar una jugada para un concurso que ya se sorteó, incluso si sus resultados ya están publicados? → A: No. Solo se admiten concursos que todavía no tienen números publicados en ninguna de sus extracciones.
- Q: Cuando ya se publicaron los resultados del concurso de una jugada, ¿puede el usuario editarla o eliminarla? → A: No. Desde que se publica la primera extracción del concurso, la jugada queda fija: no se puede editar ni eliminar.
- Q: ¿Puede un usuario registrar más de una jugada para el mismo concurso, incluso dos con los mismos seis números? → A: Sí. Se permiten varias jugadas por concurso. Si una repite exactamente los seis números de otra del mismo concurso, la aplicación advierte y pide confirmación antes de guardarla.
- Q: ¿Qué pasa si el usuario intenta registrar una jugada con un mismo número repetido? → A: Se rechaza. Los seis números deben ser distintos.
- Q: ¿La jugada debe registrar cuánto costó el cartón y, si es así, ese dato es obligatorio u opcional? → A: Es obligatorio: un único importe en pesos por jugada; no se puede guardar la jugada sin él.
- Q: ¿Qué texto se muestra cuando falta el importe de un premio, ya sea porque la información de premios todavía no se publicó o porque se publicó sin el importe individual de la categoría? → A: Un único texto en los dos casos y en todas las pantallas (consulta pública y comparación): "Información de premios pendiente de publicación". Se actualizan RN-27, AC-1.9 y AC-5.7.
- Q: En Estadísticas, si el visitante ingresa una fecha desde posterior a la fecha hasta, ¿qué debe ver? → A: El mensaje de error y, debajo, exactamente las mismas estadísticas que estaba viendo (misma modalidad, mismo período y mismo número consultado). Para lograrlo, cada consulta de estadísticas lleva también los datos de la consulta que se estaba mostrando. Se actualiza AC-6.8.
- Q: En la consulta pública, ¿qué se muestra en Premio Extra mientras Primer Sorteo, La Segunda o Revancha no están todas publicadas? → A: En lugar del conjunto de números se muestra el estado derivado de esas tres extracciones: "Resultado pendiente" si alguna está sin cargar y, si no, "Pendiente de validación" si alguna está en Borrador u Observado. Nunca se muestra un conjunto parcial. La información de premios de Premio Extra se muestra si está publicada, de forma independiente (RN-18). Se actualizan AC-1.14 y RN-20.
- Q: ¿Se aprueban los textos que propuso el plan (marcados con † en el catálogo de mensajes) y los valores de NFR-005 (5 intentos, 15 minutos de bloqueo, 30 minutos de inactividad y 8 caracteres)? → A: Sí. Se aprueban todos tal como están y dejan de ser propuestas o supuestos.
- Q: ¿Dónde se registran las decisiones sobre las interpretaciones P-01 a P-07 del plan? → A: En esta especificación: en Clarifications y en la regla o el criterio de aceptación que corresponda. research.md solo las referencia.
- Q: ¿Se confirma la interpretación de D-12 (el público ve el estado "Pendiente de validación", nunca los valores sin validar)? → A: Sí. D-12 queda resuelta tal como está escrita en RN-17 y RN-20.
- Q (P-01): ¿Cómo sale una modalidad del estado "En revisión"? → A: De dos formas: (a) al publicar una corrección, el bloque deja de estar en revisión; (b) el administrador puede quitar la marca indicando un motivo, sin modificar valores y sin que aparezca "Corregido el …". Las dos acciones quedan en el registro de cambios. Se actualizan RN-16 y AC-7.1.
- Q (P-02): Con 6 aciertos frente a una categoría ganadora publicada menor (o "sin ganadores" en Premio Extra), ¿qué prevalece? → A: El caso (a) de RN-52 y RN-31 se aplica mientras la categoría ganadora no esté publicada o sea 6. Si está publicada con un valor menor (o "sin ganadores" en Premio Extra), el resultado es "Premio pendiente de determinación" con el aviso de RN-52 e. Se actualizan RN-31, RN-52, AC-5.21 y AC-5.24.
- Q (P-03): ¿Cuándo se muestra "Actualizado por corrección del resultado oficial el dd/mm/aaaa"? → A: Solo en las modalidades de la jugada en las que alguna corrección publicada de los bloques que usa cambió alguno de los cinco datos de RN-29. La fecha es la de la corrección más reciente que produjo un cambio. Se actualizan RN-32 y AC-5.9.
- Q (P-04): ¿Qué estado resumido muestra el historial para cada jugada? → A: En este orden de precedencia: (1) alguna modalidad "Con premio" y todas esas con importe publicado → "Con premio"; (2) alguna "Con premio" sin importe publicado → "Con premio — información de premios pendiente de publicación"; (3) alguna "Premio pendiente de determinación" → "Premio pendiente de determinación"; (4) alguna modalidad sin publicar → "Resultado pendiente"; (5) en cualquier otro caso → "Sin premio". Se actualiza AC-5.13.
- Q (P-05): ¿Se puede modificar un concurso ya creado? → A: Sí. El administrador puede modificar la fecha del sorteo y las modalidades aplicables. Puede agregar modalidades siempre; solo puede quitar una modalidad sin información cargada; y solo puede cambiar la fecha mientras ninguna extracción esté publicada. Cada cambio queda en el registro de cambios. Se actualizan RN-05 y se agrega AC-2.14.
- Q (P-06): ¿Premio Extra exige sus tres extracciones? → A: Sí. Al crear o modificar un concurso, si se marca Premio Extra, también deben estar marcadas Primer Sorteo, La Segunda y Revancha; si no, se rechaza con "Premio Extra requiere Primer Sorteo, La Segunda y Revancha". Se actualizan RN-13 y AC-2.1.
- Q (P-07): ¿Qué se muestra cuando la búsqueda por fecha no encuentra concursos? → A: El mismo criterio que la búsqueda por número: "No hay información de concursos del dd/mm/aaaa", sin mostrar información de ningún otro concurso. Se actualiza AC-1.3.

---

## Escenarios de usuario y pruebas (User Scenarios & Testing) *(obligatorio)*

Cada criterio de aceptación tiene un identificador `AC-<historia>.<n>` y describe un resultado observable desde la aplicación (Const. VI). Las referencias `RN-xx` remiten a las reglas de negocio y `D-xx` a decisiones pendientes.

### Historia de usuario 1 — Consultar resultados del Quini 6 sin registrarse (Prioridad: P1)

Como visitante, quiero consultar los últimos resultados del Quini 6 y los de concursos anteriores, con sus números, premios, pozos y ganadores por modalidad, para conocer los números ganadores sin necesidad de registrarme.

**Por qué esta prioridad**: Es la propuesta de valor pública y el recorrido más frecuente. Sin esta historia no hay producto.

**Prueba independiente**: Con concursos ya publicados en distintos estados (completo, incompleto, pendiente, corregido), una persona sin cuenta recorre la sección de resultados y verifica cada estado sin que se le pida iniciar sesión.

**Criterios de aceptación**:

1. **AC-1.1** — **Dado** que una persona ingresa a la aplicación sin estar autenticada, **cuando** accede a la sección de resultados, **entonces** ve el número de concurso, la fecha del sorteo y los números ganadores de cada modalidad publicada del concurso indicado por RN-25, sin que aparezca una solicitud de registro o inicio de sesión.
2. **AC-1.2** — **Dado** que el concurso más reciente registrado en la aplicación todavía no tiene ninguna modalidad publicada, **cuando** el visitante abre la sección de resultados, **entonces** ve ese concurso con su número, su fecha y la leyenda "Resultados pendientes", y los resultados del último concurso publicado se muestran aparte, rotulados con su propio número y fecha, sin presentarlos como los del concurso actual.
3. **AC-1.3** — **Dado** que existen concursos anteriores publicados, **cuando** el visitante busca un concurso por número o por fecha del sorteo, o lo elige del listado de concursos, **entonces** ve los resultados de ese concurso. **Dado** que el visitante busca una fecha sin concursos registrados, **cuando** confirma la búsqueda, **entonces** ve "No hay información de concursos del dd/mm/aaaa" y no se muestra información de ningún otro concurso (P-07, Clarifications 13/11/2026).
4. **AC-1.4** — **Dado** que el visitante busca un número de concurso que no está registrado en la aplicación, **cuando** confirma la búsqueda, **entonces** ve el mensaje "No hay información del concurso N.º X" y no se muestra información de ningún otro concurso.
5. **AC-1.5** — **Dado** un concurso con algunas modalidades publicadas y otras no, **cuando** el visitante lo consulta, **entonces** ve los números de las modalidades publicadas, cada modalidad no publicada aparece rotulada como "Resultado pendiente" o "Pendiente de validación" según RN-20, y el concurso se identifica como "Incompleto".
6. **AC-1.6** — **Dado** un concurso cuyas modalidades aplicables y su información de premios están todas publicadas, **cuando** el visitante lo consulta, **entonces** el concurso se identifica como "Completo".
7. **AC-1.7** — **Dado** una modalidad con información de premios publicada, **cuando** el visitante la consulta, **entonces** ve, para cada categoría de premio: la cantidad de aciertos o la condición que la define, la cantidad de ganadores, el importe destinado a la categoría, el importe individual por ganador cuando esté publicado y, si corresponde, el pozo vacante o acumulado; cada dato aparece con su propio rótulo, sin mezclar conceptos (RN-26).
8. **AC-1.8** — **Dado** una modalidad con números publicados pero sin información de premios publicada, **cuando** el visitante la consulta, **entonces** ve los números ganadores y la leyenda "Información de premios pendiente de publicación".
9. **AC-1.9** — **Dado** una categoría con ganadores, dentro de información de premios publicada, cuyo importe individual no fue informado, **cuando** el visitante la consulta, **entonces** ve en lugar de ese importe "Información de premios pendiente de publicación" y nunca un importe estimado o calculado por la aplicación (RN-27).
10. **AC-1.10** — **Dado** una categoría sin ganadores, **cuando** el visitante la consulta, **entonces** ve "0 ganadores" y la información de pozo vacante solo si fue publicada.
11. **AC-1.11** — **Dado** un resultado publicado que luego fue corregido, **cuando** el visitante consulta el concurso, **entonces** ve los valores vigentes junto a la indicación "Corregido el dd/mm/aaaa" (alcance del detalle visible: D-13).
12. **AC-1.12** — **Dado** un resultado publicado que un administrador marcó "En revisión", **cuando** el visitante lo consulta, **entonces** ve los valores publicados acompañados del aviso "Información en revisión" (RN-24).
13. **AC-1.13** — **Dado** que no existe ningún concurso con resultados publicados, **cuando** el visitante abre la sección de resultados, **entonces** ve el mensaje "Todavía no hay resultados publicados" y ningún número ni importe.
14. **AC-1.14** — **Dado** un concurso que incluye Premio Extra, **cuando** el visitante lo consulta, **entonces** el Premio Extra se presenta con su información de premios y su conjunto de números distintos, formado a partir del Primer Sorteo, La Segunda y Revancha (RN-31), y no como una extracción independiente de seis números (RN-15). **Dado** que alguna de esas tres extracciones no está publicada, **cuando** el visitante consulta el concurso, **entonces** en lugar del conjunto ve el estado de Premio Extra según RN-20 y ningún conjunto parcial; si la información de premios de Premio Extra está publicada, la ve igualmente (RN-18).
15. **AC-1.15** — **Dado** cualquier modalidad publicada, **cuando** el visitante la consulta, **entonces** ve la fuente de la información (RN-17).
16. **AC-1.16** — **Dado** un concurso en el que una modalidad no existía según la reglamentación de su período, **cuando** el visitante lo consulta, **entonces** esa modalidad no aparece como pendiente ni influye en que el concurso figure como incompleto (RN-13).

---

### Historia de usuario 2 — Incorporar, validar y publicar resultados (Prioridad: P1)

Como administrador, quiero cargar la información de cada concurso, cotejarla con la fuente oficial y publicarla solo cuando esté validada, para que el público y los usuarios consulten información exacta y trazable.

**Por qué esta prioridad**: Es la única vía de ingreso de datos al producto. Sin esta historia no hay resultados que consultar, comparar ni analizar.

**Prueba independiente**: Un administrador crea un concurso, carga parte de sus modalidades, intenta publicar sin validar, valida y publica una modalidad; luego una persona sin cuenta verifica qué ve en cada etapa.

**Criterios de aceptación**:

1. **AC-2.1** — **Dado** un administrador autenticado, **cuando** crea un concurso indicando número, fecha del sorteo y modalidades aplicables, **entonces** el concurso queda registrado y figura en el listado público con la leyenda "Resultados pendientes". Si marca Premio Extra sin marcar también Primer Sorteo, La Segunda y Revancha, la operación se rechaza con "Premio Extra requiere Primer Sorteo, La Segunda y Revancha" (P-06).
2. **AC-2.2** — **Dado** que ya existe el concurso N.º X, **cuando** un administrador intenta crear otro concurso con el mismo número, **entonces** la aplicación rechaza la operación con el mensaje "El concurso N.º X ya existe" y ofrece acceder al concurso existente (RN-11, RN-21).
3. **AC-2.3** — **Dado** un concurso creado, **cuando** el administrador carga los números de una modalidad con extracción propia, **entonces** la aplicación solo los acepta si son exactamente seis números distintos entre 00 y 45, y en caso contrario indica cuál es el error (RN-14, RN-22).
4. **AC-2.4** — **Dado** que el administrador cargó números o premios de una modalidad, **cuando** guarda sin validar, **entonces** la información queda en estado "Borrador", no es visible para el público y el público ve esa modalidad como "Pendiente de validación" (RN-16, RN-20).
5. **AC-2.5** — **Dado** información en estado "Borrador" sin fuente registrada o con errores de consistencia bloqueantes, **cuando** el administrador intenta validarla y publicarla, **entonces** la aplicación lo impide e informa qué falta o qué es inconsistente (RN-17, RN-22).
6. **AC-2.6** — **Dado** información en estado "Borrador" con fuente registrada y sin errores bloqueantes, **cuando** el administrador confirma que la cotejó con la fuente y la publica, **entonces** pasa a "Publicado" y queda visible para el público en la siguiente consulta.
7. **AC-2.7** — **Dado** un concurso en el que solo algunas modalidades están validadas, **cuando** el administrador publica esas modalidades, **entonces** el público las ve publicadas y el resto sigue rotulado como pendiente (RN-18).
8. **AC-2.8** — **Dado** que el administrador detecta que la información cargada no coincide con la fuente oficial, **cuando** la marca como "Observado" e indica el motivo, **entonces** la publicación queda bloqueada hasta que la inconsistencia se resuelva (RN-16).
9. **AC-2.9** — **Dado** que dos modalidades del mismo concurso tienen exactamente los mismos seis números, **cuando** el administrador intenta publicarlas, **entonces** la aplicación muestra una advertencia que debe confirmar expresamente antes de publicar (RN-22).
10. **AC-2.10** — **Dado** que la fuente oficial todavía no está disponible, **cuando** el administrador consulta el concurso, **entonces** puede dejarlo en "Borrador" o sin cargar, y el público sigue viendo "Resultado pendiente" o "Pendiente de validación", nunca datos no validados.
11. **AC-2.11** — **Dado** un usuario registrado sin permisos de administrador, **cuando** intenta acceder a una función administrativa desde la navegación o con una dirección directa, **entonces** ve el mensaje "No tenés permisos para acceder a esta sección" y no se muestra ni se modifica información (RN-37).
12. **AC-2.12** — **Dado** un visitante sin sesión, **cuando** intenta acceder a una función administrativa con una dirección directa, **entonces** se le pide iniciar sesión y, si inicia sesión con una cuenta sin permisos de administrador, ve el mensaje de AC-2.11.
13. **AC-2.13** — **Dado** un concurso en preparación, **cuando** el administrador carga la información de premios de una categoría, **entonces** puede registrar cantidad de ganadores, importe destinado a la categoría, importe individual y pozo vacante o acumulado por separado, y dejar como "no disponible" los datos que la fuente todavía no informó. Las categorías ya vienen predefinidas por modalidad y no pueden agregarse ni quitarse; en Siempre Sale y en Premio Extra, el administrador registra además la cantidad de aciertos de la categoría ganadora; en Premio Extra puede indicar que no hubo ganadores (RN-26, RN-31, RN-52).
14. **AC-2.14** — **Dado** un concurso creado, **cuando** el administrador modifica su fecha del sorteo o sus modalidades aplicables, **entonces** puede agregar modalidades siempre; solo puede quitar una modalidad que no tenga información cargada; solo puede cambiar la fecha mientras ninguna extracción del concurso esté publicada; se aplica la misma validación de Premio Extra de AC-2.1; y el cambio queda en el registro de cambios con el valor anterior y el nuevo (P-05, Clarifications 13/11/2026).

---

### Historia de usuario 3 — Crear una cuenta y acceder a las funciones personales (Prioridad: P2)

Como visitante, quiero crear una cuenta e iniciar sesión para poder registrar y seguir mis jugadas, con la seguridad de que nadie más puede verlas.

**Por qué esta prioridad**: Habilita todas las funciones personales (US4, US5). No aporta valor por sí sola, pero es condición necesaria del segundo bloque de valor.

**Prueba independiente**: Crear una cuenta, iniciar sesión, acceder al área personal, cerrar sesión y comprobar que las direcciones privadas dejan de ser accesibles.

**Criterios de aceptación**:

1. **AC-3.1** — **Dado** un visitante, **cuando** completa el formulario de registro con un correo electrónico válido y una contraseña que cumple los requisitos mínimos, **entonces** se crea la cuenta, queda con la sesión iniciada y ve su área personal.
2. **AC-3.2** — **Dado** un visitante, **cuando** intenta registrarse con un correo electrónico con formato inválido o con una contraseña que no cumple los requisitos, **entonces** ve qué dato debe corregir y no se crea la cuenta.
3. **AC-3.3** — **Dado** que ya existe una cuenta con un correo electrónico, **cuando** un visitante intenta registrarse con ese correo, **entonces** no se crea una segunda cuenta y ve un mensaje que lo invita a iniciar sesión.
4. **AC-3.4** — **Dado** un usuario registrado, **cuando** inicia sesión con credenciales correctas, **entonces** accede a sus funciones personales.
5. **AC-3.5** — **Dado** un intento de inicio de sesión con credenciales incorrectas, **cuando** se envía el formulario, **entonces** ve el mensaje "Correo electrónico o contraseña incorrectos", sin indicar cuál de los dos datos es el incorrecto.
6. **AC-3.6** — **Dado** varios intentos fallidos consecutivos de inicio de sesión para una misma cuenta (umbral en NFR-005), **cuando** se produce un nuevo intento, **entonces** la aplicación informa que el acceso está bloqueado temporalmente e indica cuándo puede volver a intentar.
7. **AC-3.7** — **Dado** un usuario con sesión iniciada, **cuando** cierra sesión, **entonces** vuelve a la vista pública y, si intenta abrir una página personal (incluso con el botón "Atrás" del navegador o una dirección guardada), se le pide iniciar sesión y no ve información personal.
8. **AC-3.8** — **Dado** un visitante sin sesión, **cuando** abre con una dirección directa una página personal, **entonces** se le pide iniciar sesión y, tras hacerlo, llega a la página que intentaba abrir.
9. **AC-3.9** — **Dado** un visitante que está consultando un concurso que todavía admite jugadas (RN-07), **cuando** elige "Registrar una jugada", **entonces** se le pide iniciar sesión o crear una cuenta y, al completar cualquiera de las dos acciones, se abre el formulario de registro de jugada con ese concurso ya seleccionado.
10. **AC-3.10** — **Dado** un usuario con sesión iniciada que no la usa durante el plazo de inactividad definido en NFR-005, **cuando** intenta realizar una operación personal, **entonces** se le pide volver a iniciar sesión.

---

### Historia de usuario 4 — Registrar y gestionar mis jugadas (Prioridad: P2)

Como usuario registrado, quiero registrar las jugadas que realicé fuera de la aplicación, consultarlas, corregirlas y eliminarlas, para tener mi historial personal ordenado y poder seguir sus resultados.

**Por qué esta prioridad**: Es el núcleo del valor personal del producto y la base de la comparación (US5).

**Prueba independiente**: Con una cuenta y concursos cargados, registrar jugadas válidas e inválidas, editarlas, eliminarlas y verificar el historial, incluido el historial vacío y el intento de acceso a jugadas ajenas.

**Criterios de aceptación**:

1. **AC-4.1** — **Dado** un usuario registrado, **cuando** selecciona seis números válidos y un concurso, ingresa el costo y confirma, **entonces** ve el mensaje "Jugada registrada" y la jugada aparece en su historial con el número de concurso, la fecha del sorteo, el costo, las modalidades aplicables a ese concurso (en las que participa automáticamente, RN-05) y los seis números con dos dígitos.
2. **AC-4.2** — **Dado** que el usuario seleccionó menos de seis números, **cuando** intenta registrar la jugada, **entonces** no puede confirmarla y ve cuántos números le faltan seleccionar.
3. **AC-4.3** — **Dado** que el usuario ya seleccionó seis números, **cuando** intenta seleccionar un séptimo, **entonces** la aplicación no lo permite e indica que la jugada admite exactamente seis números.
4. **AC-4.4** — **Dado** que el usuario ingresa un valor fuera del rango 00 a 45 o que no es un número, **cuando** intenta registrarlo, **entonces** la aplicación lo rechaza e indica el rango permitido.
5. **AC-4.5** — **Dado** que el usuario ingresa un número que ya forma parte de su jugada (por ejemplo, un segundo 07), **cuando** intenta agregarlo o guardar la jugada, **entonces** ve el mensaje "El 07 ya está en tu jugada", el número repetido no se agrega y la jugada no se puede guardar hasta tener seis números distintos (RN-03).
6. **AC-4.6** — **Dado** que el usuario no eligió un concurso, **cuando** intenta registrar la jugada, **entonces** no puede confirmarla y ve el mensaje "Elegí el concurso de tu jugada". El formulario no ofrece elegir modalidades: antes de confirmar, muestra las modalidades del concurso elegido en las que participará la jugada.
7. **AC-4.7** — **Dado** que el usuario quiere asociar la jugada a un concurso que no está registrado en la aplicación, **cuando** lo busca, **entonces** ve el mensaje "Este concurso todavía no está disponible para registrar jugadas" y no puede registrar la jugada (RN-07).
8. **AC-4.8** — **Dado** que el usuario elige un concurso con números publicados en al menos una extracción, **cuando** intenta registrar la jugada, **entonces** ve el mensaje "Ya no se pueden registrar jugadas para este concurso porque sus resultados fueron publicados" y la jugada no se guarda. **Dado** un concurso ya sorteado cuyas extracciones están todas sin publicar o en Borrador, **cuando** el usuario registra la jugada, **entonces** se guarda normalmente (RN-07).
9. **AC-4.9** — **Dado** que el usuario registra una jugada para un concurso sin resultados publicados, **cuando** la confirma, **entonces** la jugada se guarda y en su historial figura con el estado "Resultado pendiente".
10. **AC-4.10** — **Dado** una jugada propia, **cuando** el usuario modifica sus números y guarda, **entonces** ve el mensaje "Jugada actualizada", el historial muestra los nuevos números y su comparación se recalcula (RN-32). Esto solo es posible mientras el concurso no tenga números publicados (RN-08).
11. **AC-4.11** — **Dado** una jugada propia, **cuando** el usuario elige eliminarla, **entonces** la aplicación pide confirmación; si confirma, ve el mensaje "Jugada eliminada" y la jugada deja de aparecer en su historial; si cancela, la jugada permanece sin cambios. Esto solo es posible mientras el concurso no tenga números publicados (RN-08).12. **AC-4.12** — **Dado** dos usuarios registrados con jugadas, **cuando** el primero intenta ver, editar o eliminar una jugada del segundo (por ejemplo, con una dirección directa), **entonces** ve el mensaje "La jugada no existe o no está disponible", la jugada ajena no se modifica y no se revela ningún dato de ella ni si existe (RN-36).
13. **AC-4.13** — **Dado** un usuario sin jugadas registradas, **cuando** consulta su historial, **entonces** ve el mensaje "Todavía no registraste jugadas" y un acceso para registrar la primera.
14. **AC-4.14** — **Dado** que el usuario ya tiene una jugada para un concurso, **cuando** registra otra para el mismo concurso con números distintos, **entonces** se guarda sin advertencias y ambas aparecen en el historial. **Dado** que la nueva jugada tiene los mismos seis números que una existente del mismo concurso, **cuando** intenta registrarla, **entonces** ve la advertencia de RN-06: si confirma, se guarda y el historial muestra las dos jugadas por separado; si cancela, no se guarda (RN-06).
15. **AC-4.15** — **Dado** un usuario con jugadas en varios concursos, **cuando** consulta su historial, **entonces** ve sus jugadas ordenadas por fecha del sorteo, de la más reciente a la más antigua, y cada una identifica el concurso, las modalidades y su estado de comparación (RN-29).
16. **AC-4.16** — **Dado** que el usuario informa un costo válido (por ejemplo, 1500,50), **cuando** registra la jugada, **entonces** el historial y el detalle muestran "$ 1.500,50". **Dado** que deja el costo vacío, **cuando** intenta registrar la jugada, **entonces** ve "Ingresá el costo de tu jugada" y la jugada no se guarda. **Dado** un costo negativo, no numérico o con más de dos decimales, **cuando** intenta registrar la jugada, **entonces** ve qué debe corregir y la jugada no se guarda (RN-09).
17. **AC-4.17** — **Dado** una jugada propia cuyo concurso ya tiene al menos una extracción publicada, **cuando** el usuario la consulta, **entonces** no ve las opciones de editar ni de eliminar, sino el aviso "Esta jugada no se puede modificar ni eliminar porque los resultados de su concurso ya fueron publicados". Si intenta editarla o eliminarla por otra vía (por ejemplo, con una dirección directa), ve ese mismo mensaje y la jugada no cambia (RN-08).

---

### Historia de usuario 5 — Comparar mis jugadas con los resultados oficiales (Prioridad: P2)

Como usuario registrado, quiero comparar mis jugadas con los resultados oficiales para conocer mis aciertos en cada modalidad y saber si me corresponde un premio y de qué importe, cuando esa información sea oficial y esté validada.

**Por qué esta prioridad**: Completa el recorrido personal (registrar → seguir → conocer el resultado). Depende de US2, US3 y US4.

**Prueba independiente**: Con un conjunto de jugadas preparado para cubrir cada estado de comparación, verificar manualmente que la aplicación muestra para cada jugada y modalidad el estado, los aciertos y el premio esperados.

**Criterios de aceptación**:

1. **AC-5.1** — **Dado** una jugada cuyo concurso no tiene publicada la modalidad jugada, **cuando** el usuario consulta su seguimiento, **entonces** esa modalidad figura como "Resultado pendiente" y no se muestra ninguna cantidad de aciertos.
2. **AC-5.2** — **Dado** una jugada cuya modalidad tiene información cargada pero no validada, **cuando** el usuario consulta su seguimiento, **entonces** esa modalidad figura como "Pendiente de validación" y no se muestran números ni aciertos.
3. **AC-5.3** — **Dado** una modalidad con números publicados pero sin información de premios publicada, **cuando** el usuario consulta su jugada, **entonces** ve la cantidad de aciertos, los números acertados resaltados, el resultado de premio que surge de RN-49 a RN-53 y, en lugar del importe, la leyenda "Información de premios pendiente de publicación". En Siempre Sale, el resultado de premio se rige por RN-52.
4. **AC-5.4** — **Dado** una modalidad con números publicados y una jugada sin aciertos en esa extracción, **cuando** el usuario la consulta, **entonces** ve "0 aciertos — Sin premio", salvo en Siempre Sale si la categoría ganadora publicada fuera de 0 aciertos (RN-52).
5. **AC-5.5** — **Dado** una jugada cuyos aciertos no alcanzan ninguna categoría de la modalidad según RN-49 a RN-53, **cuando** el usuario la consulta, **entonces** ve "N aciertos — Sin premio".
6. **AC-5.6** — **Dado** una jugada cuyos aciertos alcanzan una categoría de la modalidad, **cuando** el usuario la consulta, **entonces** ve "Con premio", el nombre de la categoría y el importe individual oficial en pesos si fue publicado.
7. **AC-5.7** — **Dado** una jugada que alcanza una categoría premiada cuyo importe individual no fue publicado, **cuando** el usuario la consulta, **entonces** ve "Con premio", el nombre de la categoría y, en lugar del importe, "Información de premios pendiente de publicación" (el mismo texto que en AC-5.3), y ningún importe estimado (RN-27).
8. **AC-5.8** — **Dado** una jugada cuyo concurso tiene varias modalidades aplicables, **cuando** el usuario la consulta, **entonces** ve un resultado separado por cada modalidad aplicable, cada uno con su propio estado, aciertos y premio, aunque algunas modalidades estén publicadas y otras pendientes.
9. **AC-5.9** — **Dado** una jugada cuya comparación ya se había mostrado y un resultado oficial que luego se corrigió, **cuando** el usuario vuelve a consultarla, **entonces** ve la comparación recalculada con la información vigente y, en cada modalidad en la que la corrección cambió alguno de los cinco datos de RN-29, el aviso "Actualizado por corrección del resultado oficial el dd/mm/aaaa" con la fecha de la corrección más reciente que produjo un cambio (RN-32, P-03).
10. **AC-5.10** — **Dado** una jugada asociada a un concurso con Premio Extra, **cuando** el usuario consulta su seguimiento, **entonces** Premio Extra figura entre las modalidades de la jugada con su elegibilidad, sus aciertos en el conjunto de números del Premio Extra y su resultado de premio, según RN-31 y RN-53 (escenarios AC-5.24 a AC-5.29).
11. **AC-5.11** — **Dado** un concurso sorteado antes de la vigencia de las reglas de RN-33, **cuando** el usuario consulta una jugada asociada a él, **entonces** ve los aciertos, si los números están publicados, y el resultado "Premio pendiente de determinación".
12. **AC-5.12** — **Dado** una modalidad publicada que está "En revisión", **cuando** el usuario consulta su jugada, **entonces** ve la comparación con el aviso "Información en revisión: el resultado podría cambiar".
13. **AC-5.13** — **Dado** un usuario en su historial, **cuando** lo recorre, **entonces** cada jugada muestra un estado resumido que permite distinguir a simple vista las jugadas con premio, sin premio, con resultado pendiente, con premio pendiente de determinación y con información de premios pendiente de publicación. El estado resumido sigue esta precedencia (P-04): "Con premio" (alguna modalidad con premio y todas esas con importe publicado); "Con premio — información de premios pendiente de publicación"; "Premio pendiente de determinación"; "Resultado pendiente" (alguna modalidad sin publicar); y, en cualquier otro caso, "Sin premio".

*Reglas de premios por modalidad (RN-49 a RN-54). Los números son ilustrativos.*

14. **AC-5.14** — **Dado** una jugada con 6 aciertos en el Primer Sorteo publicado, **cuando** el usuario la consulta, **entonces** ve "Primer Sorteo: 6 aciertos — Con premio — Primer Premio" (RN-49).
15. **AC-5.15** — **Dado** una jugada con 5 aciertos en el Primer Sorteo, **cuando** el usuario la consulta, **entonces** ve "Primer Sorteo: 5 aciertos — Con premio — Segundo Premio".
16. **AC-5.16** — **Dado** una jugada con 4 aciertos en el Primer Sorteo, **cuando** el usuario la consulta, **entonces** ve "Primer Sorteo: 4 aciertos — Con premio — Tercer Premio"; con 3 o menos aciertos ve "Sin premio".
17. **AC-5.17** — **Dado** una jugada con 6, 5 o 4 aciertos en La Segunda, **cuando** el usuario la consulta, **entonces** ve en La Segunda el Primer, el Segundo o el Tercer Premio respectivamente, determinado solo con los números de La Segunda (RN-50).
18. **AC-5.18** — **Dado** una jugada con 3 aciertos en el Primer Sorteo y otros 3 en La Segunda, **cuando** el usuario la consulta, **entonces** ve "Sin premio" en ambos sorteos: los aciertos no se suman entre extracciones (RN-28, RN-50).
19. **AC-5.19** — **Dado** una jugada con 6 aciertos en Revancha, **cuando** el usuario la consulta, **entonces** ve "Revancha: 6 aciertos — Con premio — Premio Revancha" (RN-51).
20. **AC-5.20** — **Dado** una jugada con 5 o 4 aciertos en Revancha, **cuando** el usuario la consulta, **entonces** ve "Revancha: N aciertos — Sin premio", sin ninguna categoría de 5 ni de 4 aciertos (RN-51).
21. **AC-5.21** — **Dado** una jugada con 6 aciertos en Siempre Sale, **cuando** el usuario la consulta, **entonces** ve "Con premio — Siempre Sale (6 aciertos)", aunque la categoría ganadora todavía no esté publicada (RN-52 a). **Dado** que la categoría ganadora publicada es menor que 6, ve "Premio pendiente de determinación" con el aviso de RN-52 e (P-02).
22. **AC-5.22** — **Dado** una jugada con 5 aciertos en Siempre Sale y una categoría ganadora publicada de 6 aciertos, **cuando** el usuario la consulta, **entonces** ve "Siempre Sale: 5 aciertos — Sin premio"; **y dado** que la categoría ganadora publicada es de 5 aciertos (no hubo apuestas con 6), ve "Con premio — Siempre Sale (5 aciertos)" (RN-52 b y c).
23. **AC-5.23** — **Dado** una jugada con 4 aciertos en Siempre Sale y una categoría ganadora publicada de 4 aciertos (no hubo apuestas con 5 ni con 6), **cuando** el usuario la consulta, **entonces** ve "Con premio — Siempre Sale (4 aciertos)"; **y dado** que la categoría ganadora todavía no está publicada, ve "Siempre Sale: 4 aciertos — Premio pendiente de determinación", nunca "Con premio" (RN-52 d).
24. **AC-5.24** — **Dado** una jugada cuyos seis números están en el conjunto de números del Premio Extra, repartidos entre distintas extracciones, y que no tiene 6 aciertos en Primer Sorteo, La Segunda ni Revancha, **cuando** el usuario la consulta, **entonces** ve "Premio Extra: participa — 6 aciertos — Con premio" y los números de la jugada resaltados dentro del conjunto (RN-31), salvo que la categoría ganadora publicada sea 5 o 4 o el extracto informe "sin ganadores": en ese caso ve "Premio pendiente de determinación" con el aviso de RN-52 e (P-02).
25. **AC-5.25** — **Dado** una jugada con 6 aciertos en el Primer Sorteo, en La Segunda o en Revancha, **cuando** el usuario consulta su resultado en Premio Extra, **entonces** ve "Excluida del Premio Extra: obtuvo 6 aciertos en <sorteo>", aunque sus seis números estén en el conjunto, y sus otros premios no cambian (RN-53).
26. **AC-5.26** — **Dado** un concurso en el que un número aparece en más de una de las tres extracciones del Premio Extra, **cuando** el usuario consulta el conjunto de números del Premio Extra, **entonces** ese número figura una sola vez, la cantidad de números distintos del conjunto es la real (entre 6 y 18) y un número de la jugada repetido entre extracciones cuenta como un único acierto (RN-31).
27. **AC-5.27** — **Dado** una jugada no excluida con 5 aciertos en el conjunto de Premio Extra, **cuando** el usuario la consulta, **entonces** ve: con una categoría ganadora publicada de 6, "Sin premio"; con una categoría ganadora publicada de 5 (no hubo ganadores con 6), "Con premio — Premio Extra (5 aciertos)"; y sin categoría ganadora publicada, "Premio pendiente de determinación". Con 4 aciertos se aplica lo mismo respecto de una categoría ganadora de 4. Con 3 aciertos o menos ve "Sin premio" (RN-31).
28. **AC-5.28** — **Dado** una jugada cuyos seis números solo estarían completos sumando los números de Siempre Sale, **cuando** el usuario consulta Premio Extra, **entonces** los números de Siempre Sale no cuentan y el resultado se calcula solo con el conjunto de RN-31.
29. **AC-5.29** — **Dado** un concurso con alguna de las tres extracciones del Premio Extra sin publicar, **cuando** el usuario consulta Premio Extra, **entonces** ve "Resultado pendiente" o "Pendiente de validación" según RN-29 y ningún acierto en el conjunto.
30. **AC-5.30** — **Dado** una jugada con aciertos en Siempre Sale mayores que la categoría ganadora publicada (por ejemplo, 5 aciertos con una categoría ganadora de 4), **cuando** el usuario la consulta, **entonces** ve "Premio pendiente de determinación" y el aviso de RN-52 e.
31. **AC-5.31** — **Dado** cualquier jugada con resultados publicados, **cuando** el usuario la consulta, **entonces** ve un bloque separado por cada modalidad (Primer Sorteo, La Segunda, Revancha, Siempre Sale y Premio Extra), cada uno con su estado de validación, sus aciertos, su elegibilidad si es Premio Extra, su resultado de premio y su importe (RN-29, RN-54).
32. **AC-5.32** — **Dado** una jugada que cumple las condiciones de premio en más de una modalidad, **cuando** el usuario la consulta, **entonces** ve todos sus premios a la vez, uno por modalidad (por ejemplo, Primer Premio del Primer Sorteo y Segundo Premio de La Segunda) (RN-54).
33. **AC-5.33** — **Dado** cada uno de los tres ejemplos de referencia (sección "Ejemplos de referencia para la comparación de jugadas"), cargados como concursos de prueba, **cuando** el usuario consulta la jugada del ejemplo, **entonces** ve exactamente los aciertos, la elegibilidad y el resultado de premio que indica el ejemplo para cada modalidad.

---

### Historia de usuario 6 — Consultar estadísticas históricas de frecuencia (Prioridad: P3)

Como visitante, quiero consultar cuántas veces salió cada número en cada modalidad y en el período que elija, para conocer el comportamiento histórico de los sorteos.

**Por qué esta prioridad**: Aporta valor público diferencial, pero depende de que exista un historial de resultados publicado (US2 y el historial inicial de 12 meses de FR-010).

**Prueba independiente**: Con un conjunto conocido de sorteos publicados, consultar frecuencias por modalidad y período y compararlas con un conteo manual.

**Criterios de aceptación**:

1. **AC-6.1** — **Dado** un visitante sin sesión, **cuando** abre la sección de estadísticas, **entonces** ve la frecuencia de aparición de los 46 números (00 a 45) para la modalidad y el período predeterminados (RN-42), junto con la cantidad de sorteos considerados y las fechas del primero y del último.
2. **AC-6.2** — **Dado** la sección de estadísticas, **cuando** el visitante cambia la modalidad, **entonces** las frecuencias, la cantidad de sorteos y el rango de fechas se actualizan para esa modalidad.
3. **AC-6.3** — **Dado** la sección de estadísticas, **cuando** el visitante define un período (fecha desde y fecha hasta), **entonces** las frecuencias se recalculan considerando solo los sorteos de ese período y se informa la cantidad de sorteos considerados.
4. **AC-6.4** — **Dado** un período sin sorteos publicados para la modalidad elegida, **cuando** el visitante consulta, **entonces** ve el mensaje "No hay sorteos publicados de [modalidad] en el período seleccionado" y no se muestra una tabla ni un gráfico con ceros.
5. **AC-6.5** — **Dado** un número que no salió en el período consultado, **cuando** el visitante consulta, **entonces** ese número figura con 0 apariciones y no se omite.
6. **AC-6.6** — **Dado** la sección de estadísticas, **cuando** el visitante consulta un número determinado, **entonces** ve la cantidad de sorteos en que salió y el porcentaje sobre los sorteos considerados (RN-40, RN-43).
7. **AC-6.7** — **Dado** que el período consultado incluye concursos sin información publicada para la modalidad, **cuando** el visitante consulta, **entonces** ve el aviso "El período incluye N concursos sin información disponible para esta modalidad" (RN-45).
8. **AC-6.8** — **Dado** una fecha desde posterior a la fecha hasta, **cuando** el visitante intenta consultar, **entonces** ve un mensaje que le pide corregir el período y, debajo, exactamente las mismas estadísticas que estaba viendo antes de la consulta (misma modalidad, mismo período, mismo número consultado, misma cantidad de sorteos y mismas frecuencias); el período inválido no se aplica.
9. **AC-6.9** — **Dado** cualquier consulta de estadísticas, **cuando** se muestran resultados, **entonces** se acompaña de la leyenda "Estadística descriptiva de sorteos pasados. No predice resultados futuros." y no aparece ninguna recomendación de números (RN-47).
10. **AC-6.10** — **Dado** dos períodos de interés, **cuando** el visitante quiere comparar sus frecuencias, **entonces** la aplicación se comporta según RN-48 (pendiente D-14).
11. **AC-6.11** — **Dado** un resultado corregido, **cuando** el visitante consulta estadísticas que incluyen ese sorteo, **entonces** las frecuencias reflejan los valores vigentes.

---

### Historia de usuario 7 — Corregir información publicada con trazabilidad (Prioridad: P2)

Como administrador, quiero corregir información ya publicada dejando registro del cambio, para que el público y los usuarios vean la información vigente sin perder la trazabilidad de lo que se modificó.

**Por qué esta prioridad**: Protege la exactitud y la integridad de los datos (Const. VIII y IX). Los errores de carga son esperables desde el primer concurso publicado.

**Prueba independiente**: Publicar un resultado, corregirlo y verificar lo que ven el administrador, el público, un usuario con una jugada sobre ese concurso y la sección de estadísticas.

**Criterios de aceptación**:

1. **AC-7.1** — **Dado** una modalidad publicada, **cuando** el administrador detecta un posible error y la marca "En revisión" indicando el motivo, **entonces** el público sigue viendo los valores publicados con el aviso "Información en revisión". La marca se quita al publicar una corrección o cuando el administrador la quita indicando un motivo, sin cambiar valores; en este último caso no aparece "Corregido el …" (P-01). Solo se puede marcar en revisión un bloque publicado.
2. **AC-7.2** — **Dado** una modalidad publicada o en revisión, **cuando** el administrador modifica sus valores, **entonces** debe indicar el motivo y la fuente de la corrección; los nuevos valores no son visibles para el público hasta que se validan y publican (RN-23).
3. **AC-7.3** — **Dado** una corrección publicada, **cuando** el administrador consulta el historial del concurso, **entonces** ve, para cada cambio, el valor anterior, el valor nuevo, la fecha, la persona que lo hizo, el motivo y la fuente.
4. **AC-7.4** — **Dado** una corrección publicada, **cuando** el público consulta el concurso, **entonces** ve los valores vigentes con la indicación "Corregido el dd/mm/aaaa" (detalle visible: D-13).
5. **AC-7.5** — **Dado** una corrección publicada, **cuando** un usuario con una jugada sobre ese concurso consulta su seguimiento, **entonces** se cumple AC-5.9.
6. **AC-7.6** — **Dado** un usuario sin permisos de administrador, **cuando** intenta corregir información de resultados por cualquier vía, **entonces** se cumple AC-2.11 y la información no cambia.

---

### Casos límite (Edge Cases)

Cada caso límite solicitado está cubierto por un criterio de aceptación, una regla o una decisión pendiente:

| Área | Caso límite | Cobertura |
|------|-------------|-----------|
| Resultados | No existen resultados publicados | AC-1.13 |
| Resultados | Resultados parciales | AC-1.5, AC-2.7, RN-18, RN-19 |
| Resultados | Concurso duplicado | AC-2.2, RN-21 |
| Resultados | Modificación de un resultado publicado | US7, RN-23, RN-24 |
| Resultados | Inconsistencias entre modalidades | AC-2.9, RN-22 |
| Resultados | Fuente de información no disponible | AC-2.10, RN-17 |
| Resultados | Información de premios pendiente | AC-1.8, AC-5.3 |
| Resultados | El concurso más reciente aún no tiene resultados | AC-1.2, RN-25 |
| Resultados | Modalidad inexistente en el período del concurso | AC-1.16, RN-13 |
| Resultados | Premio Extra con alguna de sus tres extracciones sin publicar | AC-1.14, RN-20 |
| Jugadas | Selección incompleta de números | AC-4.2 |
| Jugadas | Más de seis números | AC-4.3 |
| Jugadas | Números fuera de rango | AC-4.4, RN-01 |
| Jugadas | Números repetidos | AC-4.5, RN-03 |
| Jugadas | Costo faltante, negativo o con formato inválido | AC-4.16, RN-09 |
| Jugadas | Duplicación de registros | AC-4.14, RN-06 |
| Jugadas | Concurso inexistente o todavía no creado | AC-4.7, RN-07 |
| Jugadas | Concurso anterior a la fecha de registro | AC-4.8, RN-07 |
| Jugadas | Concurso con solo una extracción publicada | AC-4.8, RN-07 |
| Jugadas | Jugada asociada a múltiples modalidades | AC-5.8, RN-05 |
| Jugadas | Concurso sin alguna modalidad en su período | AC-4.1, RN-05, RN-13 |
| Jugadas | Modificación o eliminación posterior al resultado | AC-4.17, RN-08 |
| Jugadas | Historial vacío | AC-4.13 |
| Jugadas | Acceso a registros de otro usuario | AC-4.12, RN-36 |
| Comparaciones | Resultado pendiente | AC-5.1 |
| Comparaciones | Resultado pendiente de validación | AC-5.2 |
| Comparaciones | Resultado incompleto (algunas modalidades) | AC-5.8 combinado con AC-5.1 |
| Comparaciones | Premio todavía no informado | AC-5.3, AC-5.7 |
| Comparaciones | Información histórica insuficiente para determinar premio | AC-5.11, RN-33 |
| Comparaciones | Corrección de resultados | AC-5.9, RN-32 |
| Comparaciones | Reglas actuales distintas de las históricas | AC-5.11, RN-33 |
| Comparaciones | Aciertos de Primer Sorteo y La Segunda sumados por error | AC-5.18, RN-28, RN-50 |
| Comparaciones | 4 o 5 aciertos en Revancha | AC-5.20, RN-51 |
| Comparaciones | Siempre Sale sin categoría ganadora publicada | AC-5.23, RN-52 d |
| Comparaciones | Siempre Sale: jugada con más aciertos que la categoría ganadora publicada | AC-5.30, RN-52 e |
| Comparaciones | Premio Extra con 6 en el conjunto, pero con 6 aciertos en una extracción | AC-5.25, RN-53 |
| Comparaciones | Números repetidos entre las extracciones del Premio Extra | AC-5.26, RN-31 |
| Comparaciones | Premio Extra completado con números de Siempre Sale | AC-5.28, RN-31 |
| Comparaciones | Premio Extra con 4 o 5 aciertos sin categoría ganadora publicada | AC-5.27, RN-31 d |
| Comparaciones | Premio Extra con alguna extracción sin publicar | AC-5.29, RN-29 |
| Comparaciones | Premios en varias modalidades a la vez | AC-5.32, RN-54 |
| Estadísticas | Período sin sorteos | AC-6.4 |
| Estadísticas | Modalidad sin información suficiente | AC-6.4, RN-44 |
| Estadísticas | Número sin apariciones | AC-6.5 |
| Estadísticas | Cambio del período seleccionado | AC-6.3 |
| Estadísticas | Información histórica incompleta (huecos) | AC-6.7, RN-45 |
| Estadísticas | Período inválido | AC-6.8 |
| Usuarios y permisos | Acceso a funciones privadas sin autenticación | AC-3.8, AC-2.12 |
| Usuarios y permisos | Sesión cerrada o vencida | AC-3.7, AC-3.10 |
| Usuarios y permisos | Acceso a información de otros usuarios | AC-4.12 |
| Usuarios y permisos | Operaciones administrativas sin permisos | AC-2.11, AC-7.6 |
| Usuarios y permisos | Intentos repetidos de inicio de sesión fallidos | AC-3.6 |

---

## Requisitos (Requirements) *(obligatorio)*

### Requisitos funcionales (Functional Requirements)

**M1 — Consulta pública de resultados**

- **FR-001**: Las funciones de consulta de resultados y de estadísticas DEBEN estar disponibles sin cuenta y sin sesión. *(US1, US6; RN-34)*
- **FR-002**: El sistema DEBE mostrar los "últimos resultados" según RN-25. *(US1; RN-25)*
- **FR-003**: El visitante DEBE poder acceder a cualquier concurso registrado mediante un listado ordenado por fecha del sorteo descendente, la búsqueda por número de concurso y la búsqueda por fecha del sorteo. *(US1)*
- **FR-004**: Para cada concurso, el sistema DEBE mostrar número, fecha del sorteo, estado de completitud (RN-19) y, por cada modalidad aplicable, su estado público (RN-20), sus números si está publicada, la información de premios publicada (RN-26) y la fuente. *(US1)*
- **FR-005**: El sistema DEBE mostrar las indicaciones de corrección y de revisión definidas en RN-24. *(US1, US7)*

**M2 — Administración de resultados**

- **FR-006**: Un administrador DEBE poder crear un concurso con número, fecha del sorteo y modalidades aplicables, incluso antes de que se realice el sorteo, para que los usuarios puedan registrar jugadas en él (RN-07). *(US2, US4; RN-07, RN-11, RN-12, RN-13, RN-21)*
- **FR-007**: Un administrador DEBE poder cargar, por modalidad, los números ganadores y la información de premios por categoría, y la fuente de la información. *(US2; RN-14, RN-26)*
- **FR-008**: El sistema DEBE aplicar los controles de consistencia de RN-22 antes de permitir la publicación. *(US2)*
- **FR-009**: El sistema DEBE gestionar los estados de la información según RN-16 y publicar únicamente según RN-17, con publicación independiente por modalidad y por bloque de premios (RN-18). *(US2)*
- **FR-010**: El único mecanismo de incorporación de información DEBE ser la carga manual por un administrador, concurso por concurso, a través de la aplicación; no hay importación de archivos ni carga automática. Antes del lanzamiento, los administradores DEBEN cargar, validar y publicar con ese mismo flujo todos los concursos sorteados en los 12 meses anteriores a la fecha de lanzamiento (historial inicial). *(US2, US6)*
- **FR-011**: Toda operación administrativa DEBE requerir una cuenta con permiso de administrador, verificado en cada operación. *(US2, US7; RN-37)*

**M3 — Corrección de información publicada**

- **FR-012**: Un administrador DEBE poder marcar una modalidad publicada como "En revisión" y corregir información publicada según RN-23. *(US7)*
- **FR-013**: El sistema DEBE conservar el historial completo de cambios de la información de resultados y premios, consultable por administradores. *(US7; RN-23)*
- **FR-014**: Las correcciones publicadas DEBEN reflejarse en la consulta pública, en la comparación de jugadas y en las estadísticas en la siguiente consulta posterior a la publicación. *(US1, US5, US6, US7; RN-32)*

**M4 — Registro y autenticación**

- **FR-015**: Un visitante DEBE poder crear una cuenta con correo electrónico y contraseña; el correo electrónico identifica la cuenta y no puede repetirse. *(US3)*
- **FR-016**: Un usuario registrado DEBE poder iniciar sesión y cerrar sesión. *(US3)*
- **FR-017**: Al requerir autenticación para una función personal, el sistema DEBE llevar al usuario, después de autenticarse, a la función que intentaba usar, conservando el concurso seleccionado cuando la acción partió desde un concurso. *(US3; AC-3.8, AC-3.9)*
- **FR-018**: El sistema DEBE aplicar las protecciones de acceso de NFR-005. *(US3)*

**M5 — Gestión de jugadas personales**

- **FR-019**: Un usuario registrado DEBE poder registrar una jugada con seis números, un concurso y su costo, según RN-01 a RN-10; la jugada participa automáticamente en todas las modalidades aplicables al concurso (RN-05). *(US4)*
- **FR-020**: Un usuario registrado DEBE poder consultar su historial de jugadas según AC-4.15, y el detalle de cada jugada. *(US4)*
- **FR-021**: Un usuario registrado DEBE poder editar y eliminar sus jugadas, con confirmación previa para eliminar, según RN-08. *(US4)*
- **FR-022**: El sistema DEBE impedir que un usuario consulte, edite o elimine jugadas de otra cuenta, por cualquier vía. *(US4; RN-36)*

**M6 — Seguimiento y comparación**

- **FR-023**: El sistema DEBE calcular y mostrar, por cada jugada y cada modalidad asociada, los cinco datos de RN-29 (estado de validación, aciertos con los números acertados resaltados, elegibilidad, resultado de premio e importe), aplicando las reglas propias de cada modalidad (RN-28, RN-30, RN-31, RN-49 a RN-54). *(US5)*
- **FR-024**: El sistema DEBE mostrar el importe individual del premio únicamente cuando esté publicado oficialmente (RN-27). *(US5)*
- **FR-025**: El sistema DEBE recalcular las comparaciones ante cambios de la jugada o del resultado oficial y señalar las actualizadas por corrección (RN-32). *(US5, US7)*

**M7 — Estadísticas**

- **FR-026**: El sistema DEBE mostrar la frecuencia de aparición de cada número de 00 a 45, por modalidad, para el período elegido, según RN-40 a RN-47. *(US6)*
- **FR-027**: El visitante DEBE poder elegir la modalidad y un período (fecha desde y hasta), y consultar un número determinado. *(US6)*
- **FR-028**: Las estadísticas DEBEN presentarse en una tabla y en un gráfico que muestren los 46 números con su cantidad de apariciones. *(US6; NFR-008)*

### Reglas de negocio

Estado: **Aprobada** = derivada directamente de la solicitud del responsable o de la Constitución. **Pendiente** = no se completa por suposición; requiere la decisión indicada.

**Números y jugadas**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-01 | Cada número de una jugada es un entero entre 00 y 45 inclusive y se muestra siempre con dos dígitos. | Aprobada | US4, US5 |
| RN-02 | Una jugada tiene exactamente seis números. | Aprobada | US4 |
| RN-03 | Los seis números de una jugada son distintos entre sí. No se puede guardar, ni al registrar ni al editar, una jugada con un número repetido. | Aprobada (Clarifications 13/11/2026) | US4, US5 |
| RN-04 | Cada jugada está asociada a exactamente un concurso registrado y pertenece a exactamente una cuenta. | Aprobada | US4, US5 |
| RN-05 | Toda jugada participa en todas las modalidades aplicables a su concurso (RN-13), incluido Premio Extra cuando el concurso lo tiene. El usuario no elige modalidades ni puede excluir ninguna. Si un administrador cambia las modalidades aplicables de un concurso (según AC-2.14, P-05), las de sus jugadas cambian en consecuencia. Se mantiene aunque el reglamento consultado permite jugar solo Tradicional (ver Supuestos). | Aprobada (Clarifications 13/11/2026; ratificada el 13/11/2026) | US4, US5 |
| RN-06 | Un usuario puede registrar varias jugadas para el mismo concurso, sin límite. Si una nueva jugada, o una editada, tiene los mismos seis números que otra jugada propia del mismo concurso (sin importar el orden), la aplicación muestra "Ya registraste una jugada con estos números para este concurso. ¿Querés guardarla igual?" y solo la guarda si el usuario confirma. Las jugadas idénticas se comparan y se muestran por separado, cada una con sus propios resultados. | Aprobada (Clarifications 13/11/2026) | US4, US5 |
| RN-07 | Una jugada solo puede asociarse a un concurso ya creado por un administrador; no se aceptan concursos ingresados por el usuario. Además, el concurso no puede tener números publicados en ninguna de sus extracciones (Primer Sorteo, La Segunda, Revancha o Siempre Sale). Desde que se publica la primera extracción, el concurso no admite nuevas jugadas, aunque las demás sigan pendientes. Los números en Borrador u Observado no lo cierran. La regla se aplica al registrar una jugada y al cambiar el concurso de una existente. | Aprobada (Clarifications 13/11/2026) | US2, US4 |
| RN-08 | Mientras el concurso de una jugada no tenga números publicados en ninguna extracción (el mismo momento de corte que RN-07), el usuario puede editar sus números y su concurso, y eliminarla. Desde que se publica la primera extracción, la jugada queda fija: no se puede editar ni eliminar, ni siquiera su costo, y permanece en el historial. Los números en Borrador u Observado no la fijan. | Aprobada (Clarifications 13/11/2026) | US4, US5 |
| RN-09 | Toda jugada tiene un costo obligatorio: un único importe en pesos para toda la jugada, sin desglose por modalidad (RN-05). Debe ser mayor o igual a cero, con hasta dos decimales (centavos), y se muestra con formato argentino ($ 1.234,56). Es un dato declarado por el usuario sobre un cartón que compró fuera de la aplicación y no habilita ninguna operación de pago (Const. V). | Aprobada (Clarifications 13/11/2026) | US4 |
| RN-10 | La fecha del sorteo de una jugada es la del concurso asociado; el usuario no la ingresa por separado, para evitar fechas inconsistentes con el concurso. Las modalidades tampoco se ingresan: se derivan del concurso (RN-05). Son obligatorios los seis números, el concurso y el costo (RN-09). | Aprobada (13/11/2026; ver D-07) | US4 |

**Concursos, resultados y publicación**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-11 | El número de concurso identifica de forma única a un concurso. | Aprobada | US1, US2 |
| RN-12 | Cada concurso tiene una única fecha del sorteo, expresada en la zona horaria de referencia (Const. VII). | Aprobada | US1, US2 |
| RN-13 | Cada concurso declara qué modalidades le son aplicables según la reglamentación de su período (Tradicional – Primer Sorteo, Tradicional – La Segunda, Revancha, Siempre Sale, Premio Extra). Una modalidad no aplicable no se muestra como pendiente ni cuenta para la completitud ni para las estadísticas. Premio Extra solo puede ser aplicable si también lo son Primer Sorteo, La Segunda y Revancha (P-06). | Aprobada (P-06: Clarifications 13/11/2026) | US1, US2, US6 |
| RN-14 | En Tradicional – Primer Sorteo, Tradicional – La Segunda, Revancha y Siempre Sale, el resultado de la modalidad son seis números distintos entre 00 y 45, extraídos de forma independiente en cada una. | Aprobada | US2, US5, US6 |
| RN-15 | El Premio Extra no es una extracción independiente: se presenta y se trata conforme a su mecanismo reglamentario (Const. VIII). El administrador no carga números propios para Premio Extra: su conjunto de números se deriva de otras extracciones (RN-31), y solo se cargan sus datos de premios (RN-26). | Aprobada | US1, US2, US5, US6 |
| RN-16 | Estados de la información de cada modalidad (números) y de cada bloque de premios: **Sin cargar** → **Borrador** (cargada, sin validar) → **Publicado** (validada contra la fuente y visible). Desde "Borrador" puede pasar a **Observado** (inconsistencia detectada, con motivo; bloquea la publicación) y volver a "Borrador" al resolverse. Desde "Publicado" puede pasar a **En revisión** (publicado con posible error señalado; sigue visible con aviso). Desde "En revisión" vuelve a "Publicado" al publicar una corrección o cuando un administrador quita la marca indicando un motivo, sin cambiar valores (P-01). | Aprobada (P-01: Clarifications 13/11/2026) | US2, US7 |
| RN-17 | Condiciones para publicar: (a) estado "Borrador"; (b) fuente registrada; (c) sin errores bloqueantes de RN-22; (d) advertencias de RN-22 confirmadas expresamente; (e) confirmación expresa del administrador de que cotejó la información con la fuente. Cualquier administrador puede publicar, incluido el que cargó o corrigió la información. La información no publicada nunca es visible para visitantes ni usuarios. | Aprobada (Clarifications 13/11/2026) | US2, US7 |
| RN-18 | La publicación es independiente por modalidad y, dentro de cada modalidad, los números se publican independientemente de la información de premios. | Aprobada | US1, US2 |
| RN-19 | Completitud de un concurso: **Sin resultados** (ninguna modalidad aplicable publicada); **Incompleto** (al menos un elemento publicado y al menos uno de sus números o bloques de premios aplicables sin publicar); **Completo** (todos los números y bloques de premios de sus modalidades aplicables publicados). | Aprobada | US1 |
| RN-20 | Estado visible para el público de cada modalidad: "Resultado pendiente" (Sin cargar), "Pendiente de validación" (Borrador u Observado), valores publicados (Publicado), valores publicados con aviso (En revisión). Para premios: "Información de premios pendiente de publicación" mientras no estén publicados. **Premio Extra** no tiene números propios: el estado de su conjunto se deriva de Primer Sorteo, La Segunda y Revancha. Es "Resultado pendiente" si alguna está sin cargar; si no, "Pendiente de validación" si alguna está en Borrador u Observado; y el conjunto solo se muestra cuando las tres están publicadas (con el aviso "Información en revisión" si alguna lo está). Nunca se muestra un conjunto parcial. Su información de premios sigue la regla general de premios. | Aprobada (Premio Extra: Clarifications 13/11/2026) | US1, US5 |
| RN-21 | No puede crearse un concurso con un número ya registrado. | Aprobada | US2 |
| RN-22 | Controles de consistencia. **Bloqueantes**: cantidad de números distinta de seis, números repetidos o fuera de rango en una modalidad con extracción propia; cantidades de ganadores o importes negativos; cantidad de aciertos de la categoría ganadora de Siempre Sale que no es un entero entre 0 y 6; categoría ganadora de Siempre Sale sin ganadores; categoría ganadora de Premio Extra distinta de 6, 5, 4 o "sin ganadores"; falta de fuente. **Advertencias que requieren confirmación**: dos modalidades del mismo concurso con los mismos seis números; categoría con ganadores sin importe individual; fecha del sorteo posterior a la fecha actual al publicar números. | Aprobada | US2, US7 |
| RN-23 | Una corrección no borra la información anterior: registra valor anterior, valor nuevo, fecha, autor, motivo y fuente. Los valores corregidos pasan por las mismas condiciones de RN-17 antes de ser visibles; hasta entonces el público ve los valores publicados previos. | Aprobada | US7 |
| RN-24 | Toda modalidad con una corrección publicada muestra al público "Corregido el dd/mm/aaaa"; toda modalidad "En revisión" muestra "Información en revisión". El detalle de la corrección visible al público se define en D-13. | Aprobada (detalle pendiente — D-13) | US1, US5, US7 |
| RN-25 | "Últimos resultados" es el concurso con la fecha del sorteo más reciente que tenga al menos un elemento publicado. Si existe un concurso registrado más reciente sin elementos publicados, se informa por separado con su número, su fecha y "Resultados pendientes" (AC-1.2). | Aprobada | US1 |

**Premios y comparación**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-26 | La información de premios de cada modalidad se registra por categoría. Las categorías de cada modalidad son las que fijan RN-49 a RN-52 y RN-31; el administrador no las crea ni las modifica. Para cada categoría se cargan desde el extracto oficial del concurso, por separado: cantidad de ganadores, importe destinado a la categoría, importe individual por ganador y pozo vacante o acumulado. En Siempre Sale y en Premio Extra se carga además la **cantidad de aciertos de la categoría ganadora** publicada (RN-52, RN-31). En Premio Extra, ese dato puede indicar que no hubo ganadores. Cada dato puede figurar como "no disponible". | Aprobada (actualizada 13/11/2026) | US1, US2, US5 |
| RN-27 | La aplicación no calcula ni estima importes individuales (por ejemplo, dividiendo un pozo por la cantidad de ganadores): muestra solo el importe individual publicado oficialmente y validado. Si no está disponible, ya sea porque la información de premios todavía no se publicó o porque se publicó sin el importe individual de la categoría, muestra "Información de premios pendiente de publicación", tanto en la consulta pública como en la comparación de jugadas. | Aprobada (texto unificado, Clarifications 13/11/2026) | US1, US5 |
| RN-28 | En Tradicional – Primer Sorteo, Tradicional – La Segunda, Revancha y Siempre Sale, los aciertos de una jugada son la cantidad de sus números que figuran entre los seis números publicados de **esa** extracción en el concurso asociado, sin importar el orden de aparición. Los aciertos se cuentan por extracción y nunca se suman entre extracciones. La única excepción es Premio Extra, que usa su propio conjunto de números (RN-31). | Aprobada (actualizada 13/11/2026) | US5 |
| RN-29 | El resultado de cada jugada en cada modalidad informa por separado cinco datos. **(1) Estado de validación del resultado**: "Resultado pendiente" si falta cargar algún número que la modalidad necesita; "Pendiente de validación" si alguno está en Borrador u Observado; publicado; o publicado con el aviso "Información en revisión". Mientras no esté publicado, no se muestran los datos 2 a 5. **(2) Aciertos.** **(3) Elegibilidad**: solo en Premio Extra, "Participa" o "Excluida" (RN-53). **(4) Resultado de premio**: "Con premio — <categoría>", "Sin premio" o "Premio pendiente de determinación", según RN-49 a RN-53. **(5) Importe**: el importe individual oficial de la categoría alcanzada o "Información de premios pendiente de publicación" (RN-27). | Aprobada (actualizada 13/11/2026) | US4, US5 |
| RN-30 | La categoría alcanzada se determina con las reglas por modalidad de RN-49 a RN-53, aprobadas por el responsable del proyecto. Del extracto oficial se toman solo los datos que dependen del conjunto de apuestas: ganadores, importes y, en Siempre Sale y Premio Extra, la cantidad de aciertos de la categoría ganadora (RN-26). En Primer Sorteo, La Segunda y Revancha, la categoría se determina en cuanto se publican los números, aunque los premios todavía no estén publicados. En Siempre Sale y Premio Extra, eso solo ocurre en los casos que RN-52 y RN-31 resuelven sin la categoría ganadora. | Aprobada (actualizada 13/11/2026; reemplaza la versión anterior, que cargaba las categorías desde cada extracto) | US2, US5 |
| RN-31 | **Premio Extra.** Toda jugada de un concurso con Premio Extra participa en él (RN-05), sujeta a la exclusión de RN-53. **Conjunto de números del Premio Extra**: los números distintos que resultan de reunir las 18 extracciones de Tradicional – Primer Sorteo, Tradicional – La Segunda y Revancha; un número que se repite entre extracciones cuenta una sola vez, así que el conjunto tiene entre 6 y 18 números. No se usan los números de Siempre Sale. **Aciertos en Premio Extra**: cantidad de números de la jugada que pertenecen al conjunto, sin que haga falta que aparezcan en una misma extracción. **Categorías**: ganan las jugadas no excluidas con 6 aciertos en el conjunto; si no hay ganadores con 6, las de 5; y si tampoco hay con 5, las de 4. La aplicación usa la categoría ganadora de Premio Extra publicada en el extracto (RN-26). Determinación para una jugada no excluida: **(a)** 6 aciertos → "Con premio — Premio Extra (6 aciertos)", porque es el máximo posible, mientras la categoría ganadora no esté publicada o sea 6; si está publicada con 5 o 4, o el extracto informa "sin ganadores", prevalece (e) (P-02); **(b)** aciertos iguales a la categoría ganadora publicada → "Con premio — Premio Extra (N aciertos)"; **(c)** 3 aciertos o menos, aciertos menores que la categoría ganadora publicada, o extracto que informa que no hubo ganadores → "Sin premio"; **(d)** 4 o 5 aciertos con la categoría ganadora sin publicar → "Premio pendiente de determinación"; **(e)** aciertos mayores que la categoría ganadora publicada → "Premio pendiente de determinación", con el mismo aviso de RN-52 e. Requiere que las tres extracciones estén publicadas; si alguna no lo está, se aplica el estado de validación de RN-29. | Aprobada (13/11/2026) | US1, US2, US5 |
| RN-32 | Las comparaciones reflejan siempre la información publicada vigente y la versión vigente de la jugada. Si cambian por una corrección publicada, se muestra "Actualizado por corrección del resultado oficial el dd/mm/aaaa". El aviso aparece solo en las modalidades en las que la corrección cambió alguno de los cinco datos de RN-29, con la fecha de la corrección más reciente que produjo un cambio (P-03). | Aprobada (P-03: Clarifications 13/11/2026) | US5, US7 |
| RN-33 | No se aplican reglas actuales a concursos de períodos con reglas distintas. Las reglas RN-31 y RN-49 a RN-54 rigen para los concursos con fecha del sorteo igual o posterior al 18/06/2024, fecha de aprobación de la versión del reglamento consultada. Para concursos anteriores, el resultado de premio es "Premio pendiente de determinación" y se informa explícitamente. | Aprobada (actualizada 13/11/2026) | US5 |

**Reglas de premios por modalidad** (aprobadas por el responsable del proyecto el 13/11/2026)

Nombres de las modalidades: **Tradicional – Primer Sorteo** (abreviado "Primer Sorteo"), **Tradicional – La Segunda** ("La Segunda"), **Revancha**, **Siempre Sale** y **Premio Extra**. Las cuatro primeras son extracciones independientes de seis números; Premio Extra no lo es (RN-15).

| Modalidad | Números con los que se compara | Categorías premiadas | Cómo se determina si la jugada gana |
|-----------|-------------------------------|----------------------|--------------------------------------|
| Primer Sorteo | Los 6 del Primer Sorteo | 6, 5 y 4 aciertos (Primer, Segundo y Tercer Premio) | Solo por los aciertos de la jugada |
| La Segunda | Solo los 6 de La Segunda | 6, 5 y 4 aciertos (Primer, Segundo y Tercer Premio) | Solo por los aciertos de la jugada |
| Revancha | Los 6 de Revancha | Solo 6 aciertos | Solo por los aciertos de la jugada |
| Siempre Sale | Los 6 de Siempre Sale | La mayor cantidad de aciertos obtenida por el conjunto de apuestas | Por los aciertos de la jugada y la categoría ganadora publicada |
| Premio Extra | El conjunto de números distintos de Primer Sorteo, La Segunda y Revancha | 6 aciertos en el conjunto; si no hay ganadores con 6, 5; si tampoco hay con 5, 4 | Por los aciertos en el conjunto, la exclusión de RN-53 y la categoría ganadora publicada |

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-49 | **Tradicional – Primer Sorteo**: 6 aciertos → Primer Premio; 5 aciertos → Segundo Premio; 4 aciertos → Tercer Premio; 3 o menos → Sin premio. | Aprobada | US5 |
| RN-50 | **Tradicional – La Segunda**: tiene las mismas categorías que RN-49, evaluadas solo contra los seis números de La Segunda. Sus aciertos no se suman a los del Primer Sorteo. Una jugada puede obtener premio en ambos sorteos a la vez, cada uno en su propia categoría. | Aprobada | US5 |
| RN-51 | **Revancha**: 6 aciertos → Premio Revancha; 5 o menos → Sin premio. No existen categorías de 4 ni de 5 aciertos. | Aprobada | US5 |
| RN-52 | **Siempre Sale**: ganan las apuestas con la mayor cantidad de aciertos obtenida por el conjunto de apuestas participantes. Si hay apuestas con 6, ganan esas; si no, las de 5; si no, las de 4; y así se desciende hasta encontrar ganadores. Como la aplicación no conoce las demás apuestas, usa la cantidad de aciertos de la categoría ganadora publicada en el extracto oficial (RN-26). Determinación: **(a)** 6 aciertos → "Con premio — Siempre Sale (6 aciertos)", porque es el máximo posible, mientras la categoría ganadora no esté publicada o sea 6; si está publicada con un valor menor, prevalece (e) (P-02); **(b)** aciertos iguales a la categoría ganadora publicada → "Con premio — Siempre Sale (N aciertos)"; **(c)** aciertos menores que la categoría ganadora publicada → "Sin premio"; **(d)** categoría ganadora no publicada y menos de 6 aciertos → "Premio pendiente de determinación"; **(e)** aciertos mayores que la categoría ganadora publicada → "Premio pendiente de determinación", con el aviso "Los aciertos de tu jugada superan la categoría ganadora publicada. Verificá los números y el concurso de tu jugada." Nunca se considera ganadora una jugada solo por tener 4, 5 o menos aciertos. | Aprobada | US2, US5 |
| RN-53 | **Exclusión del Premio Extra**: queda excluida del Premio Extra toda jugada con 6 aciertos en Tradicional – Primer Sorteo, Tradicional – La Segunda o Revancha, aunque tenga 6 aciertos en el conjunto de RN-31. La comparación muestra "Excluida del Premio Extra: obtuvo 6 aciertos en <sorteo>". La exclusión no afecta los premios obtenidos en las demás modalidades. Los 6 aciertos en Siempre Sale no excluyen. | Aprobada | US5 |
| RN-54 | Cada modalidad se evalúa y se muestra por separado. Una misma jugada puede obtener premio en varias modalidades del mismo concurso. La única dependencia entre modalidades es la exclusión de RN-53. | Aprobada | US5 |

**Acceso e información personal**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-34 | Resultados, premios, pozos, ganadores y estadísticas publicados son públicos (Const. III). | Aprobada | US1, US6 |
| RN-35 | Registrar, consultar, editar, eliminar y comparar jugadas requiere sesión iniciada, verificada en cada operación (Const. IV). | Aprobada | US3, US4, US5 |
| RN-36 | Cada cuenta accede solo a sus jugadas. Ante un intento sobre una jugada ajena, la respuesta es la misma que para una jugada inexistente. | Aprobada | US4, US5 |
| RN-37 | Las funciones administrativas requieren una cuenta con permiso de administrador. Hay un único rol de administrador, sin roles diferenciados de carga y validación. El permiso no puede obtenerse mediante el registro público: lo otorga directamente el responsable del proyecto, y el MVP no incluye una pantalla de gestión de permisos. | Aprobada (Clarifications 13/11/2026) | US2, US7 |
| RN-38 | Al cerrar sesión o vencer la sesión, se pierde el acceso a toda función personal hasta volver a iniciar sesión. | Aprobada | US3 |
| RN-39 | Para crear una cuenta solo se piden correo electrónico y contraseña (Const. IV, información imprescindible). | Aprobada | US3 |

**Estadísticas**

| ID | Regla | Estado | Historias |
|----|-------|--------|-----------|
| RN-40 | La frecuencia de un número en una modalidad y un período es la cantidad de sorteos de ese período en los que el número figura entre los números publicados de esa modalidad. | Aprobada | US6 |
| RN-41 | Las estadísticas se calculan solo con números publicados (incluidos los que están "En revisión", con sus valores publicados vigentes) de concursos en los que la modalidad es aplicable. Nunca incluyen información en Borrador u Observado. | Aprobada | US6 |
| RN-42 | Si el visitante no elige un período, se consideran todos los sorteos publicados de la modalidad. La modalidad predeterminada es Tradicional – Primer Sorteo. | Aprobada (sujeta a D-14) | US6 |
| RN-43 | El porcentaje de un número es su frecuencia dividida por la cantidad de sorteos considerados, multiplicada por 100, con dos decimales en formato argentino. | Aprobada | US6 |
| RN-44 | No se fija un umbral mínimo de sorteos: siempre se informa la cantidad de sorteos considerados; con cero sorteos se muestra el mensaje de ausencia de información (AC-6.4). | Aprobada (sujeta a D-14) | US6 |
| RN-45 | Si el período incluye concursos registrados sin la modalidad publicada, se informa su cantidad. | Aprobada | US6 |
| RN-46 | Premio Extra no se ofrece como modalidad en las estadísticas de frecuencia, porque no es una extracción independiente (RN-15). | Aprobada | US6 |
| RN-47 | Las estadísticas son descriptivas. No se muestran predicciones, recomendaciones ni calificaciones de números (por ejemplo, "números calientes" o "fríos"). | Aprobada | US6 |
| RN-48 | Forma de comparar frecuencias entre dos períodos. | Pendiente — D-14 | US6 |

### Ejemplos de referencia para la comparación de jugadas

Estos ejemplos son escenarios de prueba de RN-28 a RN-31 y RN-49 a RN-54 (AC-5.33). **Los números son ilustrativos y no corresponden a concursos reales.** No incluyen importes: en todos los casos, el importe es el oficial publicado o "Información de premios pendiente de publicación" (RN-27). En Siempre Sale, el resultado depende de la categoría ganadora publicada (RN-52), por eso se indica para cada caso posible.

**Ejemplo 1 — Ganador del Primer Sorteo y de La Segunda.** Jugada: 03, 08, 14, 21, 32, 40.

| Modalidad | Números extraídos | Aciertos | Resultado esperado |
|-----------|-------------------|---------:|--------------------|
| Primer Sorteo | 03, 08, 14, 21, 32, 40 | 6 | Con premio — Primer Premio |
| La Segunda | 03, 08, 14, 21, 32, 41 | 5 | Con premio — Segundo Premio |
| Revancha | 03, 08, 14, 21, 33, 41 | 4 | Sin premio (Revancha solo premia 6) |
| Siempre Sale | 03, 08, 14, 22, 33, 41 | 3 | Con categoría ganadora de 3: Con premio. De 4, 5 o 6: Sin premio. No publicada: Premio pendiente de determinación. De 2 o menos: Premio pendiente de determinación con aviso (RN-52 e) |
| Premio Extra | Conjunto de 8 números distintos: 03, 08, 14, 21, 32, 33, 40, 41 | 6 en el conjunto | Excluida del Premio Extra: obtuvo 6 aciertos en el Primer Sorteo (RN-53) |

**Ejemplo 2 — Ganador de Revancha.** Jugada: 01, 07, 12, 19, 28, 44.

| Modalidad | Números extraídos | Aciertos | Resultado esperado |
|-----------|-------------------|---------:|--------------------|
| Primer Sorteo | 01, 07, 12, 19, 30, 45 | 4 | Con premio — Tercer Premio |
| La Segunda | 01, 07, 12, 20, 30, 45 | 3 | Sin premio |
| Revancha | 01, 07, 12, 19, 28, 44 | 6 | Con premio — Premio Revancha |
| Siempre Sale | 01, 07, 12, 19, 28, 40 | 5 | Con categoría ganadora de 5: Con premio. De 6: Sin premio. No publicada: Premio pendiente de determinación. De 4 o menos: Premio pendiente de determinación con aviso (RN-52 e) |
| Premio Extra | Conjunto de 9 números distintos: 01, 07, 12, 19, 20, 28, 30, 44, 45 | 6 en el conjunto | Excluida del Premio Extra: obtuvo 6 aciertos en Revancha (RN-53) |

**Ejemplo 3 — Ganador del Premio Extra.** Jugada: 02, 09, 16, 23, 31, 42.

| Modalidad | Números extraídos | Aciertos | Resultado esperado |
|-----------|-------------------|---------:|--------------------|
| Primer Sorteo | 02, 09, 16, 25, 34, 45 | 3 | Sin premio |
| La Segunda | 02, 11, 16, 23, 35, 42 | 4 | Con premio — Tercer Premio |
| Revancha | 05, 09, 18, 23, 31, 42 | 4 | Sin premio |
| Siempre Sale | 02, 09, 16, 23, 31, 40 | 5 | Con categoría ganadora de 5: Con premio. De 6: Sin premio. No publicada: Premio pendiente de determinación. De 4 o menos: Premio pendiente de determinación con aviso (RN-52 e) |
| Premio Extra | Conjunto de 13 números distintos: 02, 05, 09, 11, 16, 18, 23, 25, 31, 34, 35, 42, 45 (02, 09, 16, 23 y 42 se repiten entre extracciones y cuentan una vez) | 6 en el conjunto | Participa — Con premio — Premio Extra (6 aciertos), sin necesidad de que la categoría ganadora esté publicada (RN-31 a). Ninguna extracción individual tiene 6 aciertos: 02, 09 y 16 salen del Primer Sorteo, 23 y 42 de La Segunda y 31 solo de Revancha |

El ejemplo 3 verifica que los 6 aciertos del Premio Extra no se confundan con 6 aciertos en una extracción individual (AC-5.24). Los ejemplos 1 y 2 verifican que la exclusión se aplique aunque los seis números estén en el conjunto (AC-5.25).

### Requisitos de calidad

- **NFR-001 (Localización)**: Todos los textos, formatos de fecha, importes y números siguen Const. VII. Verificación: revisión de cada pantalla del MVP sin textos en inglés y con fechas `dd/mm/aaaa`, importes `$ 1.234,56` y números de dos dígitos.
- **NFR-002 (Adaptabilidad)**: Todas las pantallas del MVP se pueden usar sin desplazamiento horizontal en pantallas de 360 px de ancho en adelante.
- **NFR-003 (Accesibilidad)**: Las pantallas cumplen el nivel AA de las pautas WCAG 2.1; en particular, los estados (con premio, sin premio, pendiente, etc.) no se comunican solo por color, sino también con texto.
- **NFR-004 (Tiempo de respuesta percibido)**: En una conexión móvil 4G típica, la sección de resultados, el historial personal y las estadísticas muestran su contenido en menos de 3 segundos en el 95 % de las consultas; mientras se carga, se muestra un indicador de carga.
- **NFR-005 (Protección de acceso)**: Tras 5 intentos fallidos consecutivos de inicio de sesión en una cuenta, se bloquean los intentos para esa cuenta durante 15 minutos. La sesión vence tras 30 minutos sin actividad. La contraseña tiene al menos 8 caracteres. *(Valores aprobados por el responsable del proyecto el 13/11/2026.)*
- **NFR-006 (Auditoría administrativa)**: Toda creación, publicación, marca de revisión y corrección de información de resultados queda registrada con fecha, hora y autor, consultable por administradores (RN-23).
- **NFR-007 (Precisión monetaria)**: Los importes se registran y muestran con precisión de centavos, sin errores de redondeo respecto de la fuente (Const. IX).
- **NFR-008 (Estados visuales)**: Toda pantalla del MVP presenta estados visibles y diferenciados para carga, éxito, error y ausencia de información (Const. X).

### Entidades clave (Key Entities)

- **Cuenta de usuario**: Persona registrada. Atributos: correo electrónico (único), credencial protegida, permiso de administrador (sí/no, otorgado por el responsable del proyecto; RN-37), fecha de alta.
- **Concurso**: Sorteo identificado por su número único. Atributos: número, fecha del sorteo, modalidades aplicables, estado de completitud (derivado, RN-19).
- **Resultado de modalidad**: Números ganadores de una modalidad en un concurso (no aplica a Premio Extra como extracción propia). Atributos: modalidad, seis números, fuente, estado (RN-16), fecha de publicación, indicador de corrección.
- **Categoría de premio**: Información de premios de una categoría dentro de una modalidad y un concurso. Las categorías están predefinidas por modalidad (RN-49 a RN-52, RN-31). Atributos cargados desde el extracto: cantidad de ganadores, importe destinado, importe individual y pozo vacante o acumulado (cada uno puede estar "no disponible"); en Siempre Sale y en Premio Extra, además, la cantidad de aciertos de la categoría ganadora. También tiene fuente y estado (RN-16).
- **Conjunto de números del Premio Extra** (derivado, no se carga): números distintos de Primer Sorteo, La Segunda y Revancha de un concurso, entre 6 y 18 (RN-31).
- **Fuente de información**: Origen identificable de los datos cargados (por ejemplo, el extracto oficial del concurso), con su descripción y fecha de consulta.
- **Registro de cambio**: Traza de una creación, publicación, marca de revisión o corrección. Atributos: elemento afectado, valor anterior, valor nuevo, fecha y hora, autor, motivo, fuente.
- **Jugada**: Registro personal de una jugada hecha fuera de la aplicación. Atributos: cuenta propietaria, seis números, concurso, costo (obligatorio, en pesos; RN-09), fechas de alta y última modificación. Sus modalidades no se registran: son las aplicables a su concurso (RN-05).
- **Comparación de jugada** (derivada, no se carga): Resultado por jugada y modalidad: estado de validación, aciertos, números acertados, elegibilidad (Premio Extra), resultado de premio y categoría alcanzada, importe individual (RN-29), e indicadores de revisión y corrección.
- **Estadística de frecuencia** (derivada, no se carga): Para una modalidad y un período: sorteos considerados, rango de fechas, concursos sin información, y por cada número de 00 a 45 su frecuencia y porcentaje.

### Dependencias entre funcionalidades

| Funcionalidad | Depende de | Motivo |
|---------------|------------|--------|
| US1 Consulta pública | US2 | Solo se muestra información publicada por un administrador. |
| US7 Corrección | US2 | Solo se corrige información ya publicada. |
| US4 Jugadas | US3, US2 | Requiere sesión y que los administradores hayan creado el concurso, incluido el próximo antes de su sorteo (RN-07). |
| US5 Comparación | US4, US2 | Requiere jugadas y resultados y premios publicados desde el extracto oficial (RN-30). |
| US6 Estadísticas | US2, historial inicial (FR-010) | Al lanzamiento, las estadísticas cubren los 12 meses previos cargados manualmente. |
| Siempre Sale (US5) | US2 (categoría ganadora publicada) | Salvo con 6 aciertos, el resultado de premio depende de que el administrador publique la cantidad de aciertos de la categoría ganadora (RN-52). |
| Premio Extra (US5) | Publicación de Primer Sorteo, La Segunda y Revancha, y de su categoría ganadora (US2) | Su conjunto de números y la exclusión dependen de esas tres extracciones. Con 4 o 5 aciertos, el resultado depende además de la categoría ganadora publicada (RN-31, RN-53). |

---

## Criterios de éxito (Success Criteria) *(obligatorio)*

### Resultados medibles (Measurable Outcomes)

- **SC-001**: En una prueba con al menos 5 personas sin conocimientos técnicos, el 100 % llega a los números ganadores del último concurso publicado en menos de 15 segundos desde que ingresa, sin que se le pida iniciar sesión.
- **SC-002**: En la misma prueba, al menos el 90 % registra una jugada válida en el primer intento y en menos de 2 minutos, partiendo de una cuenta con sesión iniciada.
- **SC-003**: Ante un conjunto de casos de prueba con información en Borrador, Observado y Publicado, el 0 % de la información no publicada aparece en la consulta pública, en las comparaciones o en las estadísticas.
- **SC-004**: En una matriz de pruebas de acceso (visitante, usuario A, usuario B, administrador) sobre cada función privada y administrativa, el 100 % de los intentos no autorizados son rechazados sin revelar información ajena.
- **SC-005**: En un conjunto de jugadas de prueba que incluye los tres ejemplos de referencia y los escenarios AC-5.14 a AC-5.32, que cubren las cinco modalidades, el 100 % de los aciertos, elegibilidades y resultados de premio mostrados coincide con el resultado esperado calculado a mano con RN-49 a RN-54.
- **SC-006**: Para al menos tres combinaciones de modalidad y período, las frecuencias mostradas coinciden en el 100 % con un conteo manual sobre los mismos sorteos publicados.
- **SC-007**: El 100 % de los concursos publicados muestra su fuente y su estado de completitud.
- **SC-008**: Tras publicar una corrección, la consulta pública, las comparaciones afectadas y las estadísticas muestran el valor corregido en la siguiente consulta (verificado en el 100 % de los casos de prueba).
- **SC-009**: En la prueba con usuarios, al menos el 90 % identifica correctamente, sin ayuda, si una jugada está pendiente, sin premio, con premio o con información de premios pendiente.
- **SC-010**: Al momento del lanzamiento, el 100 % de los concursos sorteados en los 12 meses anteriores figura publicado con su fuente, y la cantidad de sorteos considerados que muestran las estadísticas con el período predeterminado coincide con esa cantidad de concursos.

---

## Supuestos (Assumptions)

Valores predeterminados adoptados por no afectar el alcance ni contradecir la solicitud. Pueden revisarse en `/speckit-clarify`:

- La autenticación es por correo electrónico y contraseña; no se usan cuentas de terceros.
- Los valores de NFR-005 (5 intentos, 15 minutos de bloqueo, 30 minutos de inactividad, 8 caracteres) son estándares habituales. El responsable los aprobó el 13/11/2026 (ver Clarifications).
- Como el MVP excluye el envío de correos electrónicos, no hay verificación del correo ni recuperación de contraseña por correo (ver D-15).
- Los números ganadores se muestran en orden ascendente.
- La aplicación se usa desde navegadores web actuales en computadoras y teléfonos; no hay aplicación nativa.
- Las cuentas de administrador son pocas y las designa el responsable del proyecto.
- Las reglas de premios fueron contrastadas con la ficha oficial del Quini 6 "DOC - H8 - GCO - BYP - 013 V02" (IAFAS, aprobada el 18/06/2024). Coinciden en Primer Sorteo, La Segunda, Revancha y Siempre Sale. La ficha no menciona la exclusión del Premio Extra (RN-53), que se adopta tal como la aprobó el responsable del proyecto. La ficha solo describe Siempre Sale hasta 4 aciertos; el descenso por debajo de 4 (RN-52) se adopta como lo aprobó el responsable y se resuelve con la categoría ganadora publicada. Las categorías de 5 y de 4 aciertos de Premio Extra se tomaron de la ficha (RN-31).
- Según la ficha consultada, Revancha y Siempre Sale son opcionales. El responsable decidió mantener que toda jugada participa en todas las modalidades (RN-05). Consecuencia aceptada: a quien haya jugado solo Tradicional, la aplicación le muestra resultados de Revancha, Siempre Sale y Premio Extra que podrían no corresponder a su cartón.
- La fuente de referencia de los resultados es el extracto oficial publicado por el organismo que realiza el sorteo; su identificación concreta se registra en cada carga.

---

## Decisiones pendientes

Ninguna de estas cuestiones se resolvió por suposición. Las marcadas **Bloqueante** impiden pasar a `/speckit-plan`. La "Recomendación" es una propuesta del agente, no una decisión aprobada.

### D-01 — Estructura de la jugada y relación con las modalidades — **Resuelta (13/11/2026)**

Toda jugada participa en todas las modalidades aplicables a su concurso, incluido Premio Extra. Ver Clarifications y RN-05.

### D-02 — Varias jugadas para el mismo concurso y duplicados — **Resuelta (13/11/2026)**

Se permiten varias jugadas por concurso; las idénticas se guardan solo si el usuario confirma una advertencia. Ver Clarifications y RN-06.

### D-03 — Jugadas de concursos pasados — **Resuelta (13/11/2026)**

Solo se admiten concursos sin números publicados en ninguna extracción. Ver Clarifications y RN-07. Consecuencia: los usuarios no pueden reconstruir jugadas anteriores a su alta.

### D-04 — Edición y eliminación después del resultado — **Resuelta (13/11/2026)**

Desde que se publica la primera extracción del concurso, la jugada no se puede editar ni eliminar. Ver Clarifications, RN-08 y AC-4.17.

### D-05 — Costo de la jugada — **Resuelta (13/11/2026)**

El costo es obligatorio: un único importe en pesos por jugada. Ver Clarifications, RN-09 y AC-4.16.

### D-06 — Números repetidos en una jugada — **Resuelta (13/11/2026)**

Se rechazan: los seis números deben ser distintos. Ver Clarifications, RN-03 y AC-4.5.

### D-07 — Datos obligatorios y opcionales de la jugada — **Resuelta (13/11/2026), como consecuencia de D-01, D-05 y D-08**

Son obligatorios los seis números, el concurso y el costo, y no hay campos opcionales. La fecha y las modalidades se toman del concurso (RN-10).

### D-08 — Catálogo de concursos para registrar jugadas — **Resuelta (13/11/2026)**

Solo se registran jugadas en concursos creados por administradores, que crean cada concurso próximo antes del sorteo. Ver Clarifications y RN-07.

### D-09 — Reglas oficiales de premios y de Premio Extra por período — **Resuelta (13/11/2026)**

El 13/11/2026, el responsable del proyecto aprobó las reglas de premios por modalidad (RN-31, RN-49 a RN-54). Esas reglas reemplazan la decisión inicial de cargar las categorías desde cada extracto (RN-30), y el extracto queda como fuente de ganadores, importes y categorías ganadoras de Siempre Sale y Premio Extra.

### D-10 — Mecanismo de incorporación del historial — **Resuelta (13/11/2026)**

Solo carga manual, con un historial inicial de los concursos de los 12 meses previos al lanzamiento. Ver Clarifications y FR-010.

### D-11 — Roles y validación administrativa — **Resuelta (13/11/2026)**

Hay un único rol de administrador, y quien carga puede validar y publicar con confirmación expresa. El permiso lo otorga el responsable del proyecto. Ver Clarifications, RN-17 y RN-37.

### D-12 — Visibilidad de "Pendiente de validación" — **Resuelta (13/11/2026)**

La solicitud pide que el público identifique los resultados "pendientes de validación" y, a la vez, que no se publique información sin validar. La especificación resuelve ambas cosas así: el público ve el **estado** "Pendiente de validación", nunca los **valores** sin validar (RN-17, RN-20). El responsable del proyecto confirmó esta interpretación (ver Clarifications).

### D-13 — Detalle público de las correcciones

- **A.** El público ve solo "Corregido el dd/mm/aaaa". *Consecuencia*: simple y suficiente para saber que hubo un cambio.
- **B.** El público ve también qué dato cambió y su valor anterior. *Consecuencia*: máxima transparencia; más información en pantalla.

Recomendación: B para números ganadores y A para el resto.

### D-14 — Alcance exacto de las estadísticas

- Comparación de períodos: **A.** El visitante cambia el período y compara secuencialmente; **B.** Vista lado a lado de dos períodos.
- Período: ¿por fechas (propuesto), por rango de números de concurso o ambos?
- Umbral de "información insuficiente": se propone no fijarlo y mostrar siempre la cantidad de sorteos (RN-44).
- Modalidad predeterminada: se propone Tradicional – Primer Sorteo (RN-42).

Recomendación: A, por fechas, sin umbral.

### D-15 — Recuperación de contraseña y verificación del correo

Como el MVP excluye el envío de correos, un usuario que olvide su contraseña no podría recuperar el acceso.

- **A.** Sin recuperación en el MVP. *Consecuencia*: el usuario que olvida la contraseña pierde su historial.
- **B.** Aprobar como excepción el envío de un correo de recuperación (transaccional, no notificación). *Consecuencia*: mejor experiencia; amplía el alcance excluido.

Recomendación: B, sujeta a aprobación expresa.

---

## Propuestas futuras (fuera del alcance de esta especificación)

Se presentan para evaluación del responsable; no están autorizadas:

- Eliminación de la cuenta y de sus datos personales por el propio usuario (refuerza Const. IV).
- Importación de resultados históricos desde un archivo, con el mismo flujo de validación y publicación, para extender las estadísticas más allá de los 12 meses iniciales.
- Exportación del historial personal de jugadas.
- Filtros del historial personal (por estado, modalidad o período).
- Resumen personal de gasto declarado frente a premios obtenidos (posible porque el costo es obligatorio, RN-09).

---

## Trazabilidad

| Historia | Requisitos funcionales | Reglas de negocio | Criterios de aceptación | Decisiones |
|----------|------------------------|-------------------|-------------------------|------------|
| US1 | FR-001 a FR-005, FR-014 | RN-11 a RN-15, RN-18 a RN-20, RN-24 a RN-27, RN-34 | AC-1.1 a AC-1.16 | D-12, D-13 |
| US2 | FR-006 a FR-011 | RN-11 a RN-14, RN-16 a RN-18, RN-21, RN-22, RN-26, RN-37 | AC-2.1 a AC-2.13 | D-12 |
| US3 | FR-015 a FR-018 | RN-35, RN-38, RN-39 | AC-3.1 a AC-3.10 | D-15 |
| US4 | FR-019 a FR-022 | RN-01 a RN-10, RN-29, RN-35, RN-36 | AC-4.1 a AC-4.17 | — |
| US5 | FR-023 a FR-025, FR-014 | RN-01, RN-04, RN-05, RN-08, RN-15, RN-20, RN-26 a RN-33, RN-35, RN-36, RN-49 a RN-54 | AC-5.1 a AC-5.33; ejemplos de referencia 1 a 3 | — |
| US6 | FR-001, FR-010, FR-014, FR-026 a FR-028 | RN-13, RN-14, RN-15, RN-34, RN-40 a RN-48 | AC-6.1 a AC-6.11 | D-14 |
| US7 | FR-005, FR-011 a FR-014 | RN-16, RN-17, RN-22 a RN-24, RN-32, RN-37 | AC-7.1 a AC-7.6 | D-13 |
