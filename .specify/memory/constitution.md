<!--
Sync Impact Report
- Versión: 1.0.0 → 1.1.0
- Tipo de cambio: MENOR. Se agregan principios y secciones nuevas y se amplía
  materialmente la guía existente. No se elimina ni se invalida ningún principio
  previo: todas las reglas de la 1.0.0 siguen vigentes dentro de la nueva estructura.
- Principios modificados (título anterior → título nuevo):
  - I. Simplicidad ante todo → XI. Calidad, simplicidad y mantenibilidad (ampliado)
  - II. Idioma y mercado: Argentina → VII. Español de Argentina y localización (ampliado)
  - III. Cero alcance fantasma → I. Desarrollo guiado por especificaciones (NO NEGOCIABLE)
    (ampliado)
  - IV. Verificable por una persona no técnica → VI. Criterios de aceptación verificables
    por personas no técnicas (ampliado)
  - V. Datos del usuario con respeto → IV. Aislamiento, seguridad y privacidad de la
    información personal (ampliado)
- Principios agregados:
  - II. Trazabilidad de requisitos
  - III. Acceso público sin registro y funciones personales para usuarios registrados
  - V. Prohibición de apuestas, compras y pagos
  - VIII. Exactitud de las reglas y datos del Quini 6
  - IX. Integridad y trazabilidad de los datos
  - X. Experiencia visual y usabilidad
- Secciones modificadas:
  - "Alcance del producto" → ampliada con modalidades, finalidad y exclusiones.
  - "Flujo de trabajo" → "Flujo de trabajo y comportamiento del agente de IA" (ampliada).
  - "Governance" → "Gobernanza" (traducida y ampliada con procedimiento de enmienda,
    política de versionado y revisión de cumplimiento).
- Secciones eliminadas: ninguna.
- Encabezados: se tradujeron al español ("Core Principles" → "Principios fundamentales",
  "Governance" → "Gobernanza") por requisito explícito del responsable del proyecto de
  redactar el documento íntegramente en español. La jerarquía de niveles se mantiene.
- Plantillas dependientes: no se modifican (leen la constitución en tiempo de ejecución).
- TODOs pendientes: ninguno.
-->

# Constitución del proyecto QUINI_6

## Principios fundamentales

### I. Desarrollo guiado por especificaciones (NO NEGOCIABLE)

El proyecto se desarrolla con el enfoque Spec-Driven Development (SDD) usando GitHub Spec Kit.
La especificación aprobada es la única fuente de autorización para implementar cualquier
funcionalidad.

- NO se implementa ninguna funcionalidad o proceso que no esté contemplado explícitamente en una especificación aprobada.
- El agente de IA NO tiene autorización para inventar funcionalidades, agregar comportamientos
  ni ampliar el alcance por iniciativa propia. La ausencia de una restricción NO equivale a una
  autorización.
- Toda idea de mejora o funcionalidad adicional se presenta como propuesta, indicando utilidad,
  impacto y consecuencias, y espera la aprobación explícita del responsable del proyecto antes
  de incorporarse.
- Las ambigüedades, contradicciones o requisitos incompletos se identifican y se consultan
  antes de tomar decisiones que afecten el comportamiento de la aplicación.
- Las decisiones técnicas se resuelven en la etapa de planificación siempre que no modifiquen
  los requisitos funcionales ni incorporen comportamientos no aprobados. Si una decisión
  técnica agrega una funcionalidad o altera la experiencia esperada del usuario, requiere
  aprobación.

Principio rector: si una funcionalidad no está especificada y aprobada, no está autorizada.

### II. Trazabilidad de requisitos

Toda funcionalidad implementada DEBE poder vincularse con un requisito o una historia de usuario
aprobada.

- Las tareas técnicas se derivan de las especificaciones y NO pueden usarse como justificación
  para incorporar funcionalidades adicionales.
- Para cada funcionalidad, el agente DEBE poder explicar: qué requisito la justifica, qué
  historia de usuario resuelve, qué criterios de aceptación debe cumplir y cómo se comprueba su
  comportamiento desde la aplicación.
- Al finalizar una tarea, el agente indica qué requisitos implementó, cómo se verifican desde la
  interfaz y qué desviaciones, limitaciones o criterios de aceptación quedan pendientes.

### III. Acceso público sin registro y funciones personales para usuarios registrados

La aplicación distingue dos tipos de usuarios: visitantes no registrados y usuarios registrados.
Esta distinción es un principio fundamental del diseño funcional y de seguridad.

Visitantes (no registrados):

- DEBEN poder usar todas las funcionalidades públicas de consulta sin crear una cuenta ni
  iniciar sesión. Esto incluye, cuando la especificación lo contemple: últimos resultados
  publicados, resultados de sorteos anteriores, números de cada modalidad, información de
  premios, pozos y ganadores, históricos de sorteos, estadísticas históricas, frecuencias de
  aparición de números y otras consultas o análisis definidos como públicos.
- NO se exige registro para acceder a información pública ni a las funcionalidades de análisis
  estadístico definidas como públicas.
- NO pueden acceder a funcionalidades personales, como registrar jugadas o consultar un
  historial privado.

Usuarios registrados:

- Acceden a todas las funcionalidades públicas y, adicionalmente, a las de gestión y
  seguimiento personal: registrar jugadas que ya realizaron fuera de la aplicación, editarlas,
  eliminarlas, consultar su historial personal, compararlas con los resultados oficiales,
  consultar sus aciertos y consultar los premios que correspondan a sus jugadas cuando exista
  información oficial y validada para determinarlos.
- El registro de una jugada en la aplicación es exclusivamente un mecanismo de seguimiento
  personal de una jugada realizada previamente fuera de la aplicación. Registrar una jugada NO
  significa comprar un cartón, realizar una apuesta ni participar en un sorteo.

### IV. Aislamiento, seguridad y privacidad de la información personal

La información personal de cada usuario está aislada y protegida.

- Cada usuario registrado únicamente puede consultar y gestionar sus propias jugadas y su
  propia información personal.
- Toda operación privada requiere autorización. La autorización se verifica en el servidor y
  NO depende exclusivamente de restricciones visuales en la interfaz.
- Los visitantes NO pueden acceder a información privada mediante rutas, solicitudes o
  mecanismos alternativos.
- Las contraseñas NO se almacenan en texto plano. Los mecanismos de autenticación y
  autorización se implementan de forma segura.
- Los secretos, credenciales y configuraciones sensibles NO se almacenan en el repositorio.
- Los datos públicos se distinguen claramente de los datos privados.
- Se solicita al usuario únicamente la información imprescindible para cada función.
- La experiencia de usuario NO compromete la seguridad de la información.

### V. Prohibición de apuestas, compras y pagos

QUINI_6 es una aplicación informativa, estadística y de seguimiento personal. NO es una
plataforma de apuestas ni un sistema de comercialización de juegos de azar.

Queda expresamente prohibido implementar funcionalidades para:

- Comprar cartones o apuestas.
- Realizar jugadas desde la aplicación para participar en sorteos.
- Pagar apuestas o integrar pasarelas de pago para comprar jugadas.
- Administrar saldos de apuestas, depósitos o retiros de dinero.
- Procesar transacciones económicas relacionadas con la participación en el Quini 6.

La carga de una jugada por parte de un usuario registrado representa exclusivamente una jugada
que ya realizó por fuera de la aplicación. Los importes que se muestren corresponden a
información de costos históricos o premios, cuando estén contemplados en las especificaciones;
mostrarlos NO habilita operaciones de pago ni transacciones.

### VI. Criterios de aceptación verificables por personas no técnicas

Todo criterio de aceptación DEBE poder comprobarse por una persona sin conocimientos técnicos
utilizando la aplicación, sin leer código fuente.

- Cada criterio describe un resultado observable desde la interfaz de la aplicación.
- NO se usan como único criterio afirmaciones técnicas (por ejemplo, que una función, API,
  consulta SQL o proceso interno se ejecutó correctamente). Esas afirmaciones pueden integrar
  pruebas técnicas, pero no constituyen por sí solas un criterio de aceptación funcional.
- Los criterios describen comportamientos concretos y contemplan los escenarios exitosos, los
  errores y las situaciones excepcionales relevantes.
- Se evitan expresiones ambiguas como "funciona correctamente", "es intuitivo" o "tiene buen
  rendimiento" sin una condición objetiva que permita verificarlas.
- Las pruebas automatizadas son complementarias y NO sustituyen la verificación funcional desde
  la aplicación.

Ejemplo adecuado: "Al ingresar como visitante a la página de resultados, la aplicación muestra
los últimos resultados publicados sin solicitar iniciar sesión."

Ejemplo inadecuado: "El endpoint de resultados responde correctamente y devuelve un HTTP 200."

Principio rector: si una persona no técnica no puede comprobar un criterio usando la
aplicación, ese criterio DEBE reformularse.

### VII. Español de Argentina y localización

La aplicación está dirigida principalmente a personas de Argentina.

- Todo el contenido visible (mensajes, botones, formularios, validaciones, notificaciones y
  textos) está en español de Argentina (es-AR), claro y natural. NO se introducen textos en
  inglés en la interfaz, salvo nombres propios, marcas o términos técnicos cuya traducción no
  resulte apropiada.
- La moneda es el peso argentino (ARS) y los importes usan el formato numérico argentino
  (por ejemplo: $ 1.234,56).
- Las fechas y horas usan formatos habituales en Argentina (por ejemplo: 06/11/2026) y la zona
  horaria de referencia es `America/Argentina/Buenos_Aires`.
- Los números del Quini 6 se representan con dos dígitos cuando corresponda (por ejemplo:
  `03`, `08`, `17`, `25`, `34`, `42`).
- La documentación del proyecto, las especificaciones y las comunicaciones del agente también
  se redactan en español.

### VIII. Exactitud de las reglas y datos del Quini 6

La exactitud de la información del Quini 6 tiene prioridad sobre la presentación visual y sobre
la disponibilidad aparente de información.

- Las reglas de cada modalidad (Tradicional o Primer Sorteo, La Segunda, Revancha, Siempre Sale
  y Premio Extra) corresponden a la reglamentación oficial aplicable a cada concurso y período
  histórico. Se contemplan las modificaciones históricas de las reglas y NO se aplican
  automáticamente las reglas actuales a sorteos históricos cuando no correspondan.
- NO se inventan reglas, resultados, importes, pozos ni datos históricos.
- Los resultados proceden de fuentes identificables y confiables.
- Los premios se calculan únicamente cuando existen datos suficientes y reglas verificadas.
  NO se presentan importes estimados como premios oficiales.
- Se diferencia entre pozo acumulado, importe destinado a una categoría, cantidad de ganadores
  e importe individual.
- La ausencia de información se muestra explícitamente y NUNCA se reemplaza por valores
  inventados. La información incompleta, dudosa o pendiente de validación se comunica con
  claridad.
- Los cálculos de aciertos respetan las reglas específicas de cada modalidad. El Premio Extra
  se trata conforme a su mecanismo reglamentario y NO como una extracción independiente.

### IX. Integridad y trazabilidad de los datos

Los datos de resultados y premios tienen trazabilidad.

- Siempre que corresponda, se identifica: la fuente de información, el concurso, la fecha del
  sorteo, la modalidad, el estado de validación y si los datos están completos, incompletos o
  pendientes de revisión.
- Las correcciones preservan la integridad de los datos y permiten identificar los cambios
  relevantes.
- NO se ocultan inconsistencias ni se completan datos faltantes mediante suposiciones.
- Los cálculos monetarios usan una precisión adecuada para evitar errores de redondeo.

### X. Experiencia visual y usabilidad

La aplicación tiene una identidad visual moderna, profesional y atractiva, y resulta sencilla
para personas con distintos niveles de conocimientos tecnológicos.

- Diseño moderno y consistente, con buena jerarquía visual, uso coherente de colores y
  tipografías, y espaciado equilibrado.
- Botones claros y reconocibles, formularios fáciles de comprender, gráficos legibles, tablas
  organizadas y tarjetas de información cuando aporten valor.
- Pestañas, filtros y carruseles solo cuando estén justificados por los requisitos aprobados.
- Estados visuales claros para operaciones exitosas, errores, cargas y ausencia de información.
- Diseño adaptable a distintos tamaños de pantalla, accesible y de navegación fácil.
- Se prioriza la claridad de la información y se evitan interfaces sobrecargadas.
- El agente puede proponer alternativas visuales, pero NO introduce pantallas, componentes,
  accesos ni interacciones funcionales que no estén especificados y aprobados. La dirección
  visual definitiva respeta las decisiones del responsable del proyecto.

### XI. Calidad, simplicidad y mantenibilidad

El proyecto se construye con criterios de calidad y mantenibilidad, eligiendo siempre la
solución más simple que cumpla la especificación.

- Ante dos soluciones válidas, se elige la más simple. NO se agrega complejidad "por si acaso"
  (capas, configuraciones, dependencias o abstracciones que hoy no se necesitan). Toda
  complejidad adicional DEBE justificarse por escrito en el plan.
- Se promueve la separación de responsabilidades y la separación entre lógica de negocio,
  presentación e infraestructura, con código modular y reutilizable.
- Validaciones consistentes y manejo adecuado de errores.
- Pruebas automatizadas para las reglas de negocio y pruebas de los recorridos funcionales
  principales.
- Documentación actualizada y facilidad para incorporar cambios futuros mediante
  especificaciones aprobadas.
- Las decisiones de arquitectura y tecnología se definen en la etapa de planificación y NO se
  usan para modificar unilateralmente el alcance funcional.

## Alcance del producto

QUINI_6 es una aplicación web destinada a usuarios de Argentina que desean consultar
información pública del Quini 6, analizar resultados históricos, consultar estadísticas y
llevar un registro personal de las jugadas que realizaron fuera de la aplicación.

- Finalidad: informativa, estadística y de seguimiento personal.
- Modalidades contempladas: Tradicional (Primer Sorteo), La Segunda, Revancha, Siempre Sale y
  Premio Extra, respetando la reglamentación oficial de cada concurso y período histórico.
- Cualquier persona puede consultar la información pública; los usuarios registrados pueden,
  adicionalmente, gestionar sus propias jugadas y seguir sus resultados.
- Fuera de alcance de forma permanente: apuestas, compra de cartones, pagos y cualquier
  transacción económica vinculada a la participación en el Quini 6 (ver Principio V).
- Lo que la aplicación hace en concreto lo define cada especificación aprobada.

## Flujo de trabajo y comportamiento del agente de IA

El agente de IA actúa como asistente de desarrollo bajo la supervisión del responsable del
proyecto.

- Orden de trabajo: constitución → especificación → plan → tareas → implementación. Antes de
  implementar, el plan DEBE confirmar que cumple todos los principios de esta constitución.
- El responsable del proyecto tiene la decisión final sobre el alcance y el comportamiento de
  la aplicación. El agente propone y NO decide unilateralmente nuevas funcionalidades.
- Las especificaciones aprobadas son la única autorización para implementar. Las tareas se
  derivan de requisitos aprobados. Las modificaciones de alcance requieren aprobación explícita.
- Ante una contradicción, ambigüedad o falta de información relevante, el agente se detiene y
  consulta. NO resuelve contradicciones mediante suposiciones.
- Una funcionalidad NO se considera terminada únicamente porque compila o porque pasan las
  pruebas automatizadas: debe cumplir sus criterios de aceptación verificables desde la
  interfaz.
- El agente mantiene una separación clara y explícita entre: requisitos aprobados, decisiones
  técnicas, propuestas de mejora y supuestos pendientes de confirmación. Ninguna propuesta ni
  supuesto se convierte automáticamente en una funcionalidad.

Principio rector del proyecto: el agente propone, el responsable decide, la especificación
autoriza y la implementación cumple.

## Gobernanza

- Esta constitución está por encima de cualquier otra práctica, convención o documento del
  proyecto. Ante un conflicto, prevalece la constitución.
- Enmiendas: todo cambio se propone por escrito, indicando el motivo y el impacto; requiere la
  aprobación explícita del responsable del proyecto; se registra en el Sync Impact Report del
  documento y actualiza la versión y la fecha de última enmienda. NO se eliminan principios
  vigentes sin explicar la necesidad del cambio.
- Versionado semántico: MAYOR si se quita o redefine un principio de forma incompatible; MENOR
  si se agrega un principio o sección, o se amplía materialmente la guía; PARCHE para
  aclaraciones, redacción o correcciones no semánticas.
- Revisión de cumplimiento: cada especificación, plan, lista de tareas e implementación se
  verifica contra estos principios antes de aprobarse. Toda desviación se documenta y se somete
  a la decisión del responsable del proyecto.

**Version**: 1.1.0 | **Ratified**: 2026-11-06 | **Last Amended**: 2026-11-13
