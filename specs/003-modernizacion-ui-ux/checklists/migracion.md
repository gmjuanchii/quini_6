# Checklist de migración y convivencia: Modernización visual y de experiencia de uso

**Propósito**: evaluar la calidad (completitud, claridad, consistencia, medibilidad y cobertura) de los requisitos que rigen la estrategia por etapas: Django mejorado → Next.js en paralelo → conmutación gradual, la sesión compartida, la paridad entre interfaces, la reversa y el retiro. Puerta formal antes de `/speckit-tasks` y de implementar.
**Creado**: 21/11/2026
**Feature**: [spec.md](../spec.md) · [plan.md](../plan.md) · [research.md](../research.md) · [data-model.md](../data-model.md) · [contracts/](../contracts/)

**Nota**: checklist personalizado generado por `/speckit-checklist` a partir de la spec, el plan y los contratos de la feature.
**Responsable de la revisión**: es un artefacto de revisión de calidad de requisitos a cargo de quien revisa. Marcar un ítem `[x]` solo cuando quien revisa determina que el criterio de calidad del requisito se cumple.
**Significado de la marca**: `[x]` significa que el criterio se revisó y se cumple en cuanto a calidad de los requisitos. No significa que la implementación esté terminada.

Referencias: `Spec §` = spec.md · `Plan §` = plan.md · `R-xx` = research.md · `rutas.md`, `api.md`, `mensajes.md`, `componentes.md` = contracts/ · `Pedido §` = pedido de planificación del 21/11/2026 · `Const.` = Constitución.

## Completitud de los requisitos

- [ ] CHK001 - ¿Existen requisitos aprobados (FR/NFR/AC con ID) para el comportamiento observable de la convivencia (sesión compartida entre interfaces, cierre de sesión que alcanza a ambas, reversa), o solo figuran en el plan y en research como decisiones técnicas? [Traceability, Gap, Const. II, R-19]
  - Resolución propuesta (21/11/2026), decisión del responsable: se agregó a la spec HU-14 (AC-14.1 a AC-14.6), FR-039 a FR-044 y SC-012.
- [ ] CHK002 - ¿Está asignada en el contrato de rutas una aplicación dueña, por etapa, para **cada** ruta de [001] y [002], incluidas `/salir/`, `/preferencias/tema/`, las páginas de error y las rutas de administración de sorteos? [Completeness, rutas.md §3]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32; tabla de propiedad completa en rutas.md § 3.
- [ ] CHK003 - ¿Están especificados campo por campo los DTO de Resultados, Mis jugadas y Estadísticas antes de que el plan exija "contrato primero", o quedan diferidos a "antes de migrar cada pantalla"? [Gap, data-model §5, Pedido §3.3]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32; los DTO se fijan por pantalla como compuerta del criterio de terminado (R-27).
- [ ] CHK004 - ¿Están definidas las operaciones de API de Administración de sorteos (pantalla 6) o al menos el criterio para darlas por especificadas, dado que el estado final "Django solo API" depende de ellas? [Gap, api.md §2, R-27]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32; misma compuerta por pantalla. Estado final sin la pantalla 6 descrito en research (P-03).
- [ ] CHK005 - ¿Está definida la "versión básica sin scripts" de **cada** componente interactivo en la implementación de Next.js (menú ⋮, diálogo, calendario, avisos, tema, gráfico), y no solo en la de Django? [Completeness, Spec §NFR-007, R-18, componentes.md]
  - Resolución propuesta (21/11/2026), decisión técnica: componentes.md § 4.
- [ ] CHK006 - ¿Se definen requisitos de caché para la capa de Next.js (respuestas privadas, datos que el servidor de Next.js obtiene de la API, navegación del cliente) equivalentes al `no-store` de las páginas privadas de Django? [Completeness, Spec §NFR-008, R-19]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32.
- [ ] CHK007 - ¿Están especificadas las reglas de formato es-AR (fechas, horas, importes desde cadena decimal, porcentajes, dos dígitos, redondeo) como contrato único que ambas implementaciones deben respetar, en lugar de existir solo como filtros de Django? [Gap, Const. VII, R-16]
  - Resolución propuesta (21/11/2026), decisión técnica: nuevo contrato contracts/formatos.md con casos compartidos.
- [ ] CHK008 - ¿Se exige explícitamente que toda fecha y hora que muestre o calcule el servidor de Next.js use `America/Argentina/Buenos_Aires`, independientemente de la zona del servidor? [Completeness, Spec §RN-04, Const. VII]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32 y formatos.md.
- [ ] CHK009 - ¿Está definido qué ocurre con los avisos (mensajes de éxito o error) cuando una acción en una aplicación redirige a una pantalla servida por la otra (por ejemplo, ingreso en Django que vuelve a una pantalla de Next.js)? [Gap, Spec §RN-09]
  - Resolución propuesta (21/11/2026), decisión del responsable: avisos compartidos por la sesión de Django (R-31, FR-043, AC-14.3, api.md § Avisos).
- [ ] CHK010 - ¿Está definido el recorrido de FR-032 (formulario pendiente) cuando el formulario vive en Next.js pero "Ingresar" todavía vive en Django (pantallas 1 a 4 antes de migrar la 5)? [Gap, Spec §FR-032, R-12, R-27]
  - Resolución propuesta (21/11/2026), decisión del responsable: página "Volver al formulario" (R-12, FR-032, AC-14.4).
- [ ] CHK011 - ¿Se especifica quién genera y quién valida la clave de idempotencia en los formularios servidos por Next.js, y su relación con la sesión de Django? [Completeness, Spec §FR-031, R-11]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32.

## Claridad de los requisitos

- [ ] CHK012 - ¿Está cuantificada "la mayoría de las P2" en el criterio de terminado de la Etapa 1 (cuántas o cuáles historias)? [Ambiguity, Plan §Etapa 1, Pedido §6]
  - Resolución propuesta (21/11/2026), decisión del responsable: todas las P1 y P2 (HU-01 a HU-11); P3 sin bloquear (Plan § Etapa 1).
- [ ] CHK013 - ¿Está definido "comportamiento sin cambios" entre interfaces con una lista de qué debe ser idéntico (textos, direcciones, códigos de respuesta, orden de foco, mensajes por campo) y qué diferencias se admiten (tipo de transición, interactividad del gráfico)? [Clarity, R-01, R-23]
  - Resolución propuesta (21/11/2026), decisión técnica: AC-14.5, FR-041 y R-32.
- [ ] CHK014 - ¿Es medible "mismo aspecto" entre la versión de Django y la de Next.js, o la comparación visual solo se define contra referencias de cada implementación por separado? [Measurability, Pedido §10, R-23]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32 (igualdad por construcción + revisión lado a lado).
- [ ] CHK015 - ¿Está definida la línea base de "rendimiento igual o mejor": se mide sobre Django antes o después de la Etapa 1, con qué dispositivo, red simulada y volumen de datos? [Ambiguity, R-24, Pedido §7.3]
  - Resolución propuesta (21/11/2026), decisión técnica: R-24, línea base precisada.
- [ ] CHK016 - ¿Están definidos "horario de bajo uso" y "grupo pequeño" para la activación gradual (franja, criterio de selección, quién decide)? [Clarity, R-28, Pedido §8.2]
  - Resolución propuesta (21/11/2026), decisión del responsable: martes o jueves de 10 a 12, sin activación por grupo (R-28).
- [ ] CHK017 - ¿Está especificado el criterio de salida de la estabilización de dos semanas (umbral de errores, incidencias de accesibilidad o quejas que la reinician o la dan por cumplida)? [Gap, R-28]
  - Resolución propuesta (21/11/2026), decisión del responsable: umbrales concretos (R-28).
- [ ] CHK018 - ¿Están definidos los disparadores de una reversa (qué falla la justifica), quién la decide y en cuánto tiempo debe ejecutarse? [Gap, rutas.md §3, Pedido §3.5]
  - Resolución propuesta (21/11/2026), decisión del responsable: disparadores, quién decide y menos de 15 minutos (R-28).

## Consistencia de los requisitos

- [ ] CHK019 - ¿Es consistente el principio 6 del pedido ("una pantalla que se migra en las primeras semanas recibe solo correcciones críticas en la Etapa 1") con R-01 y el Plan §Etapa 1, que implementan la spec completa en Django en todas las pantallas, incluida Extracción histórica (pantalla 1)? [Conflict, Pedido §3.6, R-01]
  - Resolución propuesta (21/11/2026), decisión del responsable: spec completa en todas las pantallas (R-01, R-30).
- [ ] CHK020 - ¿La cookie `quini6_vista_previa` usada para la activación gradual es compatible con NFR-008 ("en el navegador solo se recuerda la preferencia de tema")? [Conflict, Spec §NFR-008, R-20, R-28]
  - Resolución propuesta (21/11/2026), decisión del responsable: sin vista previa ni cookie nueva (R-20, R-28, rutas.md § 3).
- [ ] CHK021 - ¿Es consistente el supuesto "las pantallas se generan completas en el servidor; los marcadores de posición solo aplican a contenidos que se actualizan" con un renderizado de Next.js que pueda mostrar esqueletos en la carga inicial? [Consistency, Spec §Supuestos, Spec §AC-13.3, R-18]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32 (sin esqueletos en la primera carga del contenido principal).
- [ ] CHK022 - ¿Es consistente NFR-007 ("toda función sigue disponible sin scripts") con un gráfico de Estadísticas que en Next.js solo existe con scripts, considerando que AC-7.5 exige gráfico además de tabla? [Conflict, Spec §NFR-007, Spec §AC-7.5, R-18]
  - Resolución propuesta (21/11/2026), decisión del responsable: SVG generado en el servidor también en Next.js; Recharts no se incorpora (R-18, R-26).
- [ ] CHK023 - ¿Es inequívoco si la cookie de tema, que el navegador envía al servidor, cumple "no se guarda en el servidor" (Entidades clave) y "solo se recuerda en el navegador"? [Ambiguity, Spec §FR-036, Spec §NFR-008, R-14]
  - Resolución propuesta (21/11/2026), decisión del responsable: aclarado en la spec, NFR-008 y Entidades clave.
- [ ] CHK024 - ¿Es consistente "lo escrito no se guarda ni en el navegador ni en el servidor" (FR-032) con un token que atraviesa el servidor de Next.js además del de Django? [Ambiguity, Spec §FR-032, R-12]
  - Resolución propuesta (21/11/2026), decisión del responsable: aclarado en la spec, NFR-008.
- [ ] CHK025 - ¿Se exige que el encabezado (sección activa, menú de cuenta, menú móvil, tema) sea idéntico mientras conviven dos implementaciones de la estructura común, y está definido qué pasa al pasar de una pantalla de Django a una de Next.js? [Consistency, Spec §FR-014 a FR-016, R-27]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32.
- [ ] CHK026 - ¿Son consistentes las reglas de sesión de [001] (30 min de inactividad, bloqueo tras 5 fallos, mensajes que no revelan si el correo existe) entre el ingreso por vistas HTML y por `POST /api/v1/sesion/`, y se define qué cuenta como "actividad" cuando la persona usa pantallas de Next.js? [Consistency, [001] NFR-005, Spec §FR-020, api.md §2]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32.

## Calidad de los criterios de aceptación

- [ ] CHK027 - ¿Los criterios de terminado de una pantalla migrada (Pedido §7.3, R-27) pueden comprobarse por una persona no técnica, o dependen de señales técnicas como la cabecera `X-Interfaz` o informes de Lighthouse? [Measurability, Const. VI, quickstart §5]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32; criterios observables de HU-14 y quickstart.
- [ ] CHK028 - ¿Tiene la prueba de sesión compartida (T208) criterios de aceptación escritos como resultados observables (qué ve la persona en cada paso, incluido el caso sin permisos y el cierre de sesión)? [Acceptance Criteria, R-19, quickstart §5 #22]
  - Resolución propuesta (21/11/2026), decisión técnica: AC-14.1 y AC-14.2; quickstart #22.
- [ ] CHK029 - ¿Están fijados los umbrales de rendimiento por pantalla (LCP, CLS, INP, JavaScript inicial) de modo que una pantalla migrada pueda aprobarse o rechazarse sin interpretación? [Measurability, R-24]
  - Resolución propuesta (21/11/2026), decisión técnica: R-24.

## Cobertura de escenarios

- [ ] CHK030 - ¿Se definen requisitos para el escenario de excepción en que Next.js no está disponible (caída o despliegue): qué ve la persona en las rutas ya conmutadas y si existe retorno automático a Django? [Gap, Exception Flow, R-20]
  - Resolución propuesta (21/11/2026), decisión del responsable: vuelta automática a Django y luego página estática (FR-044, R-20, rutas.md § 3).
- [ ] CHK031 - ¿Se definen requisitos para quien está a mitad de una tarea (formulario completo, confirmación abierta, extracción en seguimiento) en el momento en que su ruta se conmuta o se revierte? [Gap, Recovery, R-28]
  - Resolución propuesta (21/11/2026), decisión técnica: reparto de POST con la marca ?_interfaz=django de los formularios de Django (R-20, rutas.md § 3, quickstart #28; corregido el 21/11/2026 en /speckit-analyze, porque sin scripts las Server Actions no envían la cabecera Next-Action).
- [ ] CHK032 - ¿Se define el orden de despliegue y la compatibilidad entre versiones de la API y de Next.js para que un despliegue parcial no deje a la interfaz con un contrato desactualizado? [Gap, api.md §1 Versionado, R-17]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32 (primero Django, cambios compatibles).
- [ ] CHK033 - ¿Está definido el "punto sin retorno" de cada pantalla (retiro de sus plantillas), con su aprobación explícita, dado que después la reversa ya no es posible? [Gap, R-28, Pedido §3.5]
  - Resolución propuesta (21/11/2026), decisión del responsable: aprobación explícita registrada en el plan (§ Registro de conmutaciones).
- [ ] CHK034 - ¿Se definen requisitos de reversión para la migración `0003_extraccion_periodo_unico_en_curso` (incluido el caso de datos existentes que la impiden)? [Gap, Recovery, data-model §1]
  - Resolución propuesta (21/11/2026), decisión técnica: R-32.

## Requisitos no funcionales

- [ ] CHK035 - ¿Se exige que la auditoría de accesibilidad (SC-004) y la revisión con teclado y lector de pantalla (SC-005) se repitan para cada pantalla migrada en ambos temas y ambos anchos, y no solo al cierre de la Etapa 1? [Coverage, Spec §SC-004, Spec §SC-005, R-23]
  - Resolución propuesta (21/11/2026), decisión técnica: R-27 y R-32.
- [ ] CHK036 - ¿Están especificados los datos que el monitoreo (Sentry o su alternativa) puede y no puede recolectar, con la misma precisión que exige Const. IV para el resto de los datos personales? [Clarity, Const. IV, R-25]
  - Resolución propuesta (21/11/2026), decisión técnica: R-25 y R-32; sujeto a P-01.
- [ ] CHK037 - ¿Se definen requisitos de seguridad equivalentes para las cabeceras de Next.js (marcos, tipo de contenido, referente, HTTPS) y para la verificación de origen de las mutaciones que pasan por Next.js? [Completeness, Spec §NFR-008, R-19]
  - Resolución propuesta (21/11/2026), decisión técnica: R-19 y R-32.

## Dependencias y supuestos

- [ ] CHK038 - ¿Está documentado qué partes del plan quedan bloqueadas si no se aprueban P-01 (Sentry), P-02 (Figma y marca), P-03 (pantalla 6) o P-04 (textos ‡), y cuál es el estado final aceptable en cada caso (por ejemplo, Django sin poder quedar como API pura)? [Dependency, research.md §Puntos a confirmar]
  - Resolución propuesta (21/11/2026), decisión técnica: columna "Si no se aprueba" en research § Puntos a confirmar.
- [ ] CHK039 - ¿Está validado el supuesto de que la Etapa 1 deja la feature completa aunque las Etapas 2 y 3 no se ejecuten, y está registrado que esa posibilidad queda en manos del responsable? [Assumption, R-01, Plan §Riesgos]
  - Resolución propuesta (21/11/2026), decisión técnica: supuesto registrado en research § Puntos a confirmar.
- [ ] CHK040 - ¿Es explícito que la fuente de diseño en Figma (P-02) prevalece sobre `ui/tokens.css` ante una discrepancia, y quién mantiene sincronizados ambos? [Ambiguity, R-02, tokens.md]
  - Resolución propuesta (21/11/2026), decisión del responsable: Figma manda (R-02).

## Notas

- Marcar un ítem `[x]` solo cuando la revisión confirma que se cumple el criterio de calidad del requisito.
- Dejar sin marcar los ítems que todavía necesitan aclaración, corrección o evaluación de quien revisa.
- `/speckit-implement` lee el estado de las marcas como compuerta y no debe modificarlas.
- `checklists/requirements.md` tiene su propio ciclo de vida, que mantienen `/speckit-specify` y `/speckit-clarify`.
- Los ítems marcados `[Conflict]` (CHK019, CHK020, CHK022) conviene resolverlos antes de `/speckit-tasks`, porque cambian el alcance de la Etapa 1 o de la Etapa 3.
- Agregar comentarios o hallazgos debajo de cada ítem.
