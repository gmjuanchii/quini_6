# Investigación y decisiones técnicas (Research): Modernización visual y de experiencia de uso

**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) | **Fecha**: 21/11/2026

Cada decisión sigue el formato **Decisión / Motivo / Alternativas descartadas**. Se citan como `[003] R-xx`. Las decisiones de [001] y [002] siguen vigentes salvo donde se indica que esta feature las reemplaza.

**Entrada del responsable**: la estrategia híbrida en tres etapas (Django mejorado → Next.js en paralelo → conmutación gradual) y el stack de la Etapa 2 forman parte del pedido de planificación del 21/11/2026. Este documento la convierte en decisiones concretas y registra dónde se aparta del pedido para respetar la spec aprobada (R-30).

---

## R-01 — Estrategia por etapas y alcance de cada una

**Decisión**: tres etapas precedidas de una Fase 0 de cimientos.

| Etapa | Qué entrega | Arquitectura al terminar |
|-------|-------------|--------------------------|
| **Fase 0** | Tokens, catálogo único de mensajes, API v1 documentada (lectura), entorno paritario (PostgreSQL 16 + proxy), línea base de rendimiento y accesibilidad | Django monolito, sin cambios visibles |
| **Etapa 1** | **La spec completa** (P1, P2 y, en lo posible, P3) sobre las plantillas de Django, con Tailwind 4, HTMX y Alpine.js | Django monolito con la nueva identidad |
| **Etapa 2** | Next.js con las mismas pantallas, una por una (R-27), cada una lista para conmutar | Proxy → Django (todo) + Next.js (preparado, sin tráfico público) |
| **Etapa 3** | Conmutación por ruta, estabilización y retiro de plantillas | Proxy → Next.js (interfaz) + Django (API, CSV, trabajador) |

La Etapa 1 cumple por sí sola todos los criterios de aceptación de la spec. Las Etapas 2 y 3 **no agregan comportamiento**: cambian la tecnología de la interfaz manteniendo exactamente los mismos criterios, textos, rutas y permisos. Por eso el criterio de terminado de una pantalla migrada es "pasa el mismo guion E2E que su versión de Django" (R-23).

**Motivo**: entrega valor visible en pocas semanas, adopta el stack moderno pedido sin reescritura de golpe y mantiene el backend (dominio, extracción, estadísticas) intacto, con sus pruebas como red de seguridad. Si el responsable decide detenerse tras la Etapa 1, la feature queda completa.

**Alternativas descartadas**: (a) reescritura total en Next.js de una vez: riesgo alto y meses sin entregas; (b) quedarse solo en Django: no cumple la decisión del responsable de adoptar el stack moderno; (c) migrar la Etapa 2 sin Etapa 1: dejaría semanas sin mejoras y sin línea base contra la cual medir la paridad.

**Regla anti-doble trabajo** (principio 6 del pedido): como todas las pantallas reciben en la Etapa 1 la implementación completa de la spec, lo que se evita duplicar es el **diseño**, no el código: tokens, variantes de componentes, iconos, textos y guiones E2E se definen una vez y se reutilizan en ambas etapas (R-02 a R-05, R-13, R-23). Lo que se descarta de la Etapa 1 son solo las piezas de interacción (HTMX, Alpine.js y Cally) y las plantillas. **Confirmado por el responsable el 21/11/2026 (CHK019)**: la spec completa se implementa en Django en todas las pantallas, también en Extracción histórica, aunque sea la primera en migrarse; el principio 6 del pedido se interpreta como "no duplicar el diseño".

---

## R-02 — Fuente única del diseño: tokens

**Decisión**: Figma es la fuente de diseño y `ui/tokens.css` su **transcripción exacta**, el único lugar del código donde existen colores, tipografía, espaciado, radios, sombras y duraciones. Se escribe con la sintaxis de Tailwind CSS 4 (`@theme` + variables CSS semánticas) y lo importan tanto el CSS de Django (Etapa 1) como el de Next.js (Etapa 2). Los valores y sus contrastes medidos están en [contracts/tokens.md](contracts/tokens.md).

- Los componentes usan **solo tokens semánticos** (`bg-surface`, `text-foreground`, `text-success-text`…), nunca colores directos. El tema oscuro redefine las variables y no requiere variantes `dark:` en las plantillas ni en los componentes.
- Tema: `:root[data-theme="oscuro"]` y `@media (prefers-color-scheme: dark) { :root:not([data-theme="claro"]) {…} }` (R-14).
- Una prueba de Vitest/Node lee `ui/tokens.css` y verifica los pares de contraste del contrato (SC-009, T004b del pedido).
- **Precedencia** (21/11/2026, CHK040): **Figma manda**. Un cambio de token se hace en Figma y, en el mismo cambio del repositorio, en `ui/tokens.css` y [contracts/tokens.md](contracts/tokens.md), con el contraste medido de nuevo. Quien diseña mantiene Figma; quien desarrolla, el código. Un valor de Figma que no cumple NFR-002 no se incorpora: se devuelve a diseño.

**Motivo**: un cambio de color se hace en un solo archivo y llega a las dos interfaces; la verificación de contraste es automática.

**Alternativas descartadas**: Style Dictionary o Tokens Studio con generación automática desde Figma (una herramienta y un paso más para unas 60 variables; puede adoptarse después sin cambiar los nombres); tokens duplicados por etapa (deriva segura).

---

## R-03 — Tailwind CSS 4 en Django (Etapa 1)

**Decisión**: `estilos/django.css` importa `ui/tokens.css` y `ui/base.css`, y declara `@source "../templates"` y `@source "../ui/variantes.json"`. Se compila con `@tailwindcss/cli` a `static/css/app.css`, que **deja de versionarse** (se agrega a `.gitignore`; el CSS propio actual se reemplaza). Comandos: `npm run css` (una vez) y `npm run css:watch` (desarrollo). El despliegue compila antes de `collectstatic`.

**Motivo**: las clases y tokens pasan sin cambios a Next.js (pedido §6). Las pruebas de Django no necesitan el CSS: `tests/conftest.py` ya usa el almacenamiento estático simple.

**Alternativas descartadas**: `django-tailwind` o `django-tailwind-cli` (dependencia de Python solo para invocar la CLI); binario autónomo de Tailwind (Node hace falta igual para la Etapa 2 y para Playwright); seguir con CSS propio (no reutiliza nada en la Etapa 2).

---

## R-04 — Variantes compartidas de componentes

**Decisión**: `ui/variantes.json` define, para los componentes con variantes (`Button`, `StatusBadge`, `Callout`, `Toast`, `EmptyState`), la lista de clases de Tailwind de su base, de cada variante y de cada tamaño. Lo leen:

- Django: un filtro `{% clases "boton" variante="destructivo" %}` en `quini6/templatetags/ui.py`, usado por los fragmentos `templates/ui/_*.html`.
- Next.js: `frontend/src/components/ui/variantes.ts` construye los `cva(...)` de shadcn/ui a partir del mismo JSON.

Los componentes, sus estados y su correspondencia Django ↔ React están en [contracts/componentes.md](contracts/componentes.md).

**Motivo**: "mismo aspecto, nombres, estados y clases" (pedido §10) garantizado por construcción, no por disciplina. Tailwind ve las clases porque escanea el JSON.

**Alternativas descartadas**: copiar las clases a mano en ambos lados (deriva); clases semánticas con `@apply` (Tailwind 4 lo desaconseja y oculta qué utilidades se usan).

---

## R-05 — Iconos (Lucide)

**Decisión**: lista cerrada de iconos en [contracts/componentes.md](contracts/componentes.md) § Iconos. Etapa 1: los SVG de `lucide-static` (licencia ISC) se copian una vez a `templates/ui/iconos/<nombre>.svg` y **se versionan** con su licencia; el filtro `{% icono "nombre" %}` los incluye con `aria-hidden="true"` y `focusable="false"`. Etapa 2: `lucide-react` con los mismos nombres.

**Motivo**: unos 25 archivos pequeños; versionarlos evita que las pruebas de Django dependan de `npm install`. Mismo trazo y tamaño en ambas etapas (AC-13.5).

**Alternativas descartadas**: sprite generado en cada build (las plantillas fallarían sin Node); fuente de iconos (problemas de accesibilidad y carga).

---

## R-06 — Interactividad de la Etapa 1: HTMX y Alpine.js

**Decisión**: HTMX 2 y Alpine.js 3 (con los complementos oficiales `anchor` y `focus`), servidos desde `static/vendor/` (copiados de `node_modules` por `npm run vendor`, no versionados), **sin CDN**. Uso acotado:

| Necesidad | Herramienta | Sin scripts (NFR-007) |
|-----------|-------------|------------------------|
| Avance de extracción y aviso final (HU-03) | HTMX: sondeo del fragmento (R-10) | Se recarga la página ([002] R-10) |
| Menú ⋮ anclado y con teclado (HU-02) | Alpine `x-anchor` + patrón de menú (flechas, Escape, clic afuera) sobre el `<details>` actual | `<details class="menu-acciones">` de [002] |
| Confirmación de eliminación (HU-02) | `<dialog>` nativo cargado con `hx-get` de la página de confirmación existente; foco inicial en "Cancelar" | Página de confirmación aparte de [002] |
| Menú móvil, menú de cuenta, mostrar/ocultar contraseña (HU-05, HU-06) | Alpine | Navegación visible como lista; contraseña oculta |
| Validación previa (FR-033) | Validador ligero propio con Alpine (R-13) | Validación del servidor |
| Avisos breves (RN-09) | Alpine: región de avisos con cierre automático | Mensajes de Django en la página |
| Estado de trabajo del botón (FR-034) | Alpine: al enviar, deshabilita y muestra "…ando…" | Indicador global "Cargando…" actual |

`static/js/selector-numeros.js` se conserva y solo cambia sus textos y estilos.

**Motivo**: es lo que pidió el responsable y alcanza para cada interacción de la spec con poco código; todo se apoya en el HTML que el servidor ya genera.

**Alternativas descartadas**: JS puro para todo (más código propio para menús con teclado y foco); React en islas (adelantaría la Etapa 2 dentro de Django); usar el `showPicker()` del navegador (descartado por [002] D-27).

---

## R-07 — Calendario y campos de fecha (HU-04)

**Decisión**:

- **Etapa 1**: componente `DateField`/`DateRangePicker` = campo de texto con máscara `dd/mm/aaaa` (barras automáticas, [002] D-27) + botón con icono que abre en un *popover* anclado la web component **Cally** (`calendar-date` / `calendar-range`), con `locale="es-AR"`, `first-day-of-week="1"`, `min`/`max` y estilos con tokens. El HTML que genera el servidor sigue siendo `<input type="date">` (sin scripts funciona como hoy); el script lo convierte en campo de texto con calendario y reenvía `AAAA-MM-DD` o `dd/mm/aaaa`, que el dominio ya acepta.
- **Etapa 2**: shadcn/ui `Calendar` (react-day-picker) con `date-fns` y `locale es`, `weekStartsOn: 1`, `mode="range"`, `disabled` para los días fuera de `min`/`max`, dentro de un `Popover`.
- **Atajos (RN-04)**: los calcula el servidor con la fecha de hoy en `America/Argentina/Buenos_Aires` y los entrega listos al formulario (Etapa 1) o en la API (`GET /api/v1/periodos/atajos?formulario=…`); el navegador nunca calcula "hoy" por su cuenta. "Todo el historial" usa la fecha del primer sorteo publicado.
- **Validación**: fechas imposibles y fin anterior al inicio se detectan al salir del campo con los mensajes del catálogo (R-13); el servidor repite la validación ([002] RN-01 a RN-04 y reglas de [001] sin cambios).
- El calendario se ancla debajo del campo (o encima si no hay lugar) y **nunca** lo tapa (AC-4.6); Escape lo cierra y devuelve el foco al campo.

**Motivo**: Cally es una web component pequeña, sin dependencias, accesible con teclado y con soporte de rangos y localización mediante `Intl`; evita escribir y mantener un calendario propio que se descartará en la Etapa 2.

**Alternativas descartadas**: calendario propio en Alpine (unas 300 líneas más pruebas, para una pieza temporal); flatpickr o Pikaday (más pesados, accesibilidad más débil); `<input type="date">` nativo (apariencia ajena y distinta en cada navegador, lo que motiva HU-04).

---

## R-08 — Etiqueta de estado de una extracción, filtro, orden y paginación (HU-01, HU-09)

**Decisión**:

- Función pura nueva `dominio/extraccion/etiqueta.py :: etiqueta_de(estado: EstadoExtraccion, tiene_no_recuperados: bool) -> EtiquetaEstado` con los cinco valores de RN-01 y la precedencia "Con error" sobre "Con advertencias". `EstadoExtraccion` de [002] **no cambia** y no se agrega ninguna columna (la etiqueta no se guarda; spec, Entidades clave).
- `extracciones/consultas.py :: listado_extracciones(filtro, orden, pagina)` anota cada fila con `Exists(SorteoExtraido con estado NO_RECUPERADO)` y, para ordenar por estado, con un `Case/When` que da el orden de RN-01. Son expresiones del ORM portables entre SQLite y PostgreSQL; no se consulta el contenido de ningún `JSONField` ([002] R-08).
- Filtro, orden y página viajan en la dirección (`?estado=con-advertencias&orden=-fecha&pagina=2`), así funcionan sin scripts, se pueden compartir y no se guarda nada en el navegador (NFR-008). Paginador de Django con 20 por página (RN-07); una página fuera de rango muestra la última con datos (Casos límite).
- Orden inicial: de la más reciente a la más antigua ([002] RN-44). Desempate estable por `id` descendente.

**Motivo**: el estado visible es presentación derivada; calcularlo en el dominio lo hace probable sin base de datos y reutilizable por la API.

**Alternativas descartadas**: agregar el estado `CON_ERROR` al modelo (cambia [002] RN-33, fuera del alcance); filtrar en Python después de traer todas las filas (no escala con [002] RN-44, que conserva las extracciones indefinidamente).

---

## R-09 — Extracciones idénticas (RN-03, AC-3.5)

**Decisión**: `servicios.iniciar_extraccion` verifica, dentro de la transacción, que no exista otra extracción `EN_CURSO` con el mismo `desde` y `hasta` (de cualquier administrador); si existe, devuelve el error `ext.periodo_en_curso` con la referencia a esa extracción (error como valor). Una **restricción única parcial** nueva (`desde`, `hasta`, condición `estado = EN_CURSO`) cubre la carrera entre dos administradores; la migración es `extracciones/0003_extraccion_periodo_unico_en_curso`. La restricción vigente de [002] (una en curso por administrador, AC-1.11) se mantiene: RN-03 se suma a ella, no la reemplaza.

**Motivo**: [002] solo impedía dos extracciones del mismo administrador; RN-03 agrega el caso entre administradores. Las restricciones únicas condicionales son portables (SQLite y PostgreSQL).

**Alternativas descartadas**: bloqueo por solapamiento parcial (la spec lo permite explícitamente); solo la verificación en el servicio (deja abierta la carrera).

---

## R-10 — Avance en vivo y aviso al terminar (HU-03)

**Decisión**:

- **Etapa 1**: el bloque `#avance-extraccion` y la fila "En curso" del listado llevan `hx-get` a su misma dirección con `hx-trigger="every 3s"` y `hx-select`/fragmento. Si la solicitud trae `HX-Request`, la vista responde **solo el fragmento** (sin rutas nuevas) con `Vary: HX-Request` y `no-store`. Cuando la extracción terminó, el fragmento final ya no trae el disparador (el sondeo se detiene solo) y la respuesta incluye `HX-Trigger: {"aviso": {...}}` con el texto de `ext.termino_*`, que la región de avisos muestra (AC-3.3). Reemplaza a `static/js/avance-extraccion.js`, que se elimina.
- **Etapa 2**: `useQuery(['extraccion', id, 'avance'], …, { refetchInterval: (q) => q.state.data?.en_curso ? 3000 : false })` contra `GET /api/v1/extracciones/{id}/avance`; al pasar a terminada, invalida el listado y muestra el aviso con Sonner.
- El marcador de posición (Skeleton) reserva el alto del bloque de avance para que la página no salte (AC-13.3, NFR-004). Con "reducir movimiento", la barra cambia de valor sin animación.

**Motivo**: 3 s da sensación de actividad sin carga apreciable (pocos administradores; la consulta es por clave primaria y un `count`). El ritmo de las fuentes (una consulta cada 2 s por sitio, [002]) no se ve afectado: el sondeo solo lee la base.

**Alternativas descartadas**: Server-Sent Events o WebSockets (requieren servidor asíncrono o Channels; desproporcionado para este volumen); seguir pidiendo la página completa cada 5 s (más pesado y no permite el aviso).

---

## R-11 — Reintentar sin duplicar el efecto (FR-031)

**Decisión**: todo formulario que crea o elimina algo lleva un campo oculto `clave_idempotencia` (UUID generado al mostrar el formulario). En la API, el mismo valor viaja en la cabecera `Idempotency-Key`. El servidor guarda en la **sesión** las últimas 50 claves usadas con el resultado obtenido (dirección de destino o identificador) durante la vida de la sesión; si llega una clave ya usada, devuelve el mismo resultado sin volver a ejecutar la acción. Aplica a: registrar jugada, eliminar jugada, iniciar extracción, eliminar extracción, crear sorteo ([001], administración) y crear cuenta.

Ante una falla de conexión, el aviso `gral.sin_conexion` ofrece "Reintentar", que reenvía el mismo pedido con la misma clave.

**Motivo**: la sesión ya está en la base ([001] R-04), así que no hace falta una tabla nueva; las claves vencen con la sesión, que es exactamente el horizonte de un reintento.

**Alternativas descartadas**: tabla `ClaveIdempotencia` (persistencia y limpieza para un dato efímero); confiar solo en el patrón POST → 303 (no cubre el doble envío por reintento tras un corte).

---

## R-12 — Formulario pendiente al vencer la sesión (FR-032)

**Decisión**: si llega un POST a una vista privada sin sesión válida, en vez de redirigir y perder lo escrito, el servidor responde la pantalla "Ingresar" con el aviso `cuenta.sesion_vencida` y un campo oculto `pendiente` = token firmado con `django.core.signing` (sal `quini6.formulario_pendiente`, vigencia 60 min) que contiene la ruta destino y los campos enviados (sin `csrfmiddlewaretoken`, sin contraseñas). Al ingresar con éxito, la vista de ingreso **responde directamente** el formulario destino precargado (modo "reanudar", que cada vista privada con formulario declara en un registro `FORMULARIOS_REANUDABLES`), con `no-store`. La persona revisa y envía; nada se envía solo. Los permisos se verifican de nuevo con la persona que ingresó (por ejemplo, una persona no administradora recibe la página de "Sin permisos").

En la API (Etapa 2), una mutación sin sesión responde `401` con `pendiente` en el cuerpo; Next.js muestra "Ingresar" con ese token y, tras el ingreso, el formulario precargado.

**Entre aplicaciones** (21/11/2026, CHK010, AC-14.4): mientras "Ingresar" siga en Django y el formulario esté en Next.js, la Server Action que recibe el `401` lleva a la persona a la pantalla "Ingresar" de Django con el token `pendiente`. Tras ingresar, si la ruta del token pertenece a Next.js, Django responde una página breve con el aviso `cuenta.volver_formulario_texto` y un único botón **"Volver al formulario"**: un formulario POST (con el token en un campo oculto) hacia la ruta destino, que Next.js atiende mostrando el formulario precargado para revisarlo. Ese POST solo reabre el formulario; nunca registra nada. El token sigue sin guardarse en el navegador ni en ningún servidor (NFR-008, aclarado el 21/11/2026). Cuando se migra la pantalla 5, esta página deja de hacer falta.

**Motivo**: lo escrito viaja solo dentro del pedido de ingreso (spec, Clarifications): no se guarda en el navegador ni en el servidor, y la firma impide que un tercero arme un formulario precargado con datos propios.

**Alternativas descartadas**: `sessionStorage` o `localStorage` (prohibido por FR-032 y NFR-008); guardar lo escrito en la sesión del servidor (la spec lo excluye); redirigir con los datos en la dirección (quedan en el historial y en los registros del servidor).

---

## R-13 — Catálogo único de mensajes y validación previa (HU-11, FR-033)

**Decisión**:

- Módulo puro `dominio/mensajes.py` con un diccionario `clave → texto` que reúne **todos** los textos visibles de [001], [002] y [003] según [contracts/mensajes.md](contracts/mensajes.md). Formularios, servicios, dominio, plantillas (filtro `{% msg "clave" %}`) y API toman los textos de allí. Una prueba compara el módulo con las tablas del contrato (mismas claves, mismos textos).
- `manage.py exportar_contratos` escribe `contratos/mensajes.json` y `contratos/openapi.json` (R-16), versionados; la CI falla si difieren de lo generado.
- **Etapa 1**: los formularios llevan `novalidate` (los globos nativos del navegador pueden salir en inglés, Const. VII) y cada campo declara sus reglas en atributos `data-validar` con el texto del catálogo ya resuelto por el servidor. Un validador de unas 150 líneas (Alpine) comprueba al salir del campo y al enviar: obligatorio, formato y existencia de la fecha, fin ≥ inicio, máximo hoy, número 00–45, formato de correo. Muestra el mensaje con el mismo marcado que el error del servidor (`templates/_campo.html`), con `aria-describedby` y `aria-invalid`, y lleva el foco al primer campo con error.
- **Etapa 2**: esquemas Zod en `frontend/src/lib/esquemas/` que toman sus textos de `mensajes.json`; React Hook Form con `mode: "onBlur"`; los errores del servidor (`422`, R-16) se cargan con `setError` campo por campo.
- El servidor sigue siendo la fuente de verdad: ninguna regla existe solo en el navegador (pedido §3.2).

**Motivo**: hoy los textos están repartidos en plantillas, formularios, servicios, dominio y JS; la reescritura completa que exigen D-01 y D-04 es la oportunidad de centralizarlos una vez y de que ambas etapas muestren exactamente el mismo texto (SC-007).

**Alternativas descartadas**: textos literales en cada capa (imposible de auditar para SC-007); i18n con `.po` (CLAUDE.md lo excluye: no hay varios idiomas).

**Efecto en las pruebas**: las pruebas de reglas del dominio no cambian sus casos ni sus resultados esperados. Las afirmaciones sobre **textos literales** se actualizan a los del catálogo de [003] (cambio exigido por D-01 y D-04), y cada cambio queda trazado en [contracts/mensajes.md](contracts/mensajes.md) § Textos reescritos.

---

## R-14 — Tema claro, oscuro y según el dispositivo (HU-12)

**Decisión**: cookie `quini6_tema` con valor `claro` u `oscuro` (sin cookie = "Según el dispositivo"), `SameSite=Lax`, `Path=/`, 400 días, no `HttpOnly` (el script la cambia sin recargar), `Secure` en producción. El servidor la lee y escribe `data-theme` en `<html>` **antes** de enviar la página, así no hay destello de tema equivocado (NFR-004). El selector es un formulario `POST /preferencias/tema/` que funciona sin scripts (fija la cookie y vuelve a la página con 303); con scripts, Alpine (Etapa 1) o un componente cliente (Etapa 2) cambia `data-theme` al instante y fija la misma cookie (AC-12.2). La cookie solo guarda la preferencia; el servidor no la registra ni la asocia a la cuenta (NFR-008). El responsable confirmó el 21/11/2026 (CHK023) que leerla para mostrar la página con el tema elegido cumple "no se guarda en el servidor"; la spec lo aclara en NFR-008.

**Motivo**: es la única forma de pintar el tema correcto desde el primer byte con renderizado en el servidor; sirve igual para Django y para Next.js.

**Alternativas descartadas**: `localStorage` + script en `<head>` (destello en la primera pintura si el script tarda y no funciona sin scripts); Zustand con persistencia (el estado vive en el cliente; ver R-26).

---

## R-15 — Transiciones y movimiento (HU-13)

**Decisión**: duraciones en tokens (`--duracion-rapida: 150ms`, `--duracion-normal: 200ms`, máximo 250 ms, AC-13.1). Etapa 1: transiciones CSS para menús, diálogo y avisos, y **View Transitions entre documentos** (`@view-transition { navigation: auto; }`) para el cambio de pantalla donde el navegador la soporte (spec, Supuestos). Etapa 2: Motion para la entrada de contenido de cada pantalla (`template.tsx`) y los avisos, con `<MotionConfig reducedMotion="user">`; Dialog y DropdownMenu de shadcn/ui mantienen sus animaciones CSS. En ambas etapas, `@media (prefers-reduced-motion: reduce)` anula transiciones y desplazamientos; la barra de progreso y el indicador de actividad informan sin movimiento (AC-13.2).

**Alternativas descartadas**: animaciones con JS en la Etapa 1 (innecesarias); Motion también para Dialog y DropdownMenu (duplicaría las animaciones de shadcn/ui).

---

## R-16 — API v1 (Django Ninja)

**Decisión**: **Django Ninja** (con Pydantic v2) en `quini6/api.py`, montada en `/api/v1/`, con un router por app (`cuentas/api.py`, `resultados/api.py`, `jugadas/api.py`, `estadisticas/api.py`, `extracciones/api.py`). Reglas:

- **Las vistas de API son tan delgadas como las de HTML**: cargan con `consultas.py`, llaman al dominio y a `servicios.py`, y serializan. No hay lógica nueva en la API.
- Autenticación por **sesión de Django** (`django_auth`) con CSRF obligatorio en métodos que modifican; autorización con los mismos criterios que las vistas HTML (`administrador_requerido` y `usuario=request.user`, con `404` idéntico para jugadas ajenas o inexistentes).
- Errores en formato **Problem Details (RFC 9457)**, `application/problem+json`, con la extensión `errores: [{campo, codigo, mensaje}]`; los mensajes salen del catálogo (R-13).
- Fechas en ISO 8601 (`AAAA-MM-DD`; fecha y hora con desplazamiento `-03:00`); importes como **cadena decimal** (`"1234.56"`), nunca número de punto flotante; números de bolillas como enteros. El formato argentino lo aplica la interfaz.
- `Cache-Control: no-store` en toda respuesta privada; respuestas públicas sin caché compartida (los resultados pueden corregirse).
- El esquema OpenAPI 3.1 se exporta a `contratos/openapi.json` (versionado) con `manage.py exportar_contratos`; `tests/api/test_contrato_openapi.py` falla si el esquema generado difiere del versionado. La lista de operaciones está en [contracts/api.md](contracts/api.md).
- Se agrega **por pantalla**, antes de migrarla (pedido §3.3); la Fase 0 publica las de solo lectura y la de sesión.

**Motivo**: Ninja genera OpenAPI a partir de los tipos, sin un segundo paquete, y es más liviano que DRF para una API de este tamaño. El pedido deja abierta la elección "según lo que ya exista": no existe ninguna API.

**Alternativas descartadas**: Django REST Framework + drf-spectacular (dos dependencias y más ceremonia: serializadores, viewsets); vistas `JsonResponse` a mano (sin OpenAPI, contrario a "contrato primero"); GraphQL (sin necesidad).

---

## R-17 — Cliente tipado generado

**Decisión**: `openapi-typescript` genera `frontend/src/api/esquema.d.ts` desde `contratos/openapi.json` (`npm run api:tipos`); `openapi-fetch` es el cliente tipado. Hay dos instancias: `apiServidor` (en el servidor de Next.js, contra la dirección interna de Django y reenviando la cookie de la solicitud, R-19) y `apiNavegador` (en el navegador, contra `/api/v1/` del mismo origen, con `X-CSRFToken`). La CI regenera los tipos y falla si cambian sin haberse versionado.

**Alternativas descartadas**: Orval o Kubb (generan hooks y más código del necesario); tipos escritos a mano (pedido §3.3).

---

## R-18 — Next.js: renderizado, mutaciones y datos

**Decisión**:

- **Next.js 16 (App Router), React 19, TypeScript estricto**, salida `standalone`. Las páginas son **componentes de servidor** que leen con `apiServidor`: la primera pintura llega completa del servidor (rendimiento para visitantes, NFR-004).
- **Mismas direcciones que Django**, con `trailingSlash: true` (las de Django terminan en `/`). Así la conmutación por ruta no cambia ningún enlace ni marcador.
- **Mutaciones = Server Actions** usadas como `action` de `<form>`, con `useActionState`: funcionan **sin scripts** (mejora progresiva, NFR-007) y, con scripts, React Hook Form valida antes de llamarlas. La acción llama a Django con `apiServidor`, reenvía la cookie, el token CSRF y la `Idempotency-Key`, y vuelve con los errores por campo o redirige con un aviso.
- **TanStack Query** solo donde hay datos en vivo o recargas parciales: avance de extracciones (R-10) y refresco del listado tras eliminar. Mutaciones sin reintento automático salvo con `Idempotency-Key` (R-11).
- **Sin scripts** (NFR-007): el menú ⋮ (DropdownMenu de shadcn/ui) necesita scripts, por eso cada fila sigue siendo un enlace a su detalle, donde "Descargar CSV" y "Eliminar" son un enlace y un formulario comunes. "Eliminar" usa **rutas interceptadas** (`@modal/(.)eliminar`): con navegación del cliente se abre el `Dialog`; con carga completa o sin scripts, se ve la página de confirmación. El calendario se renderiza en el servidor como `<input type="date">` y se reemplaza por el `DateRangePicker` al hidratar, con el mismo ancho reservado.
- **Tablas**: TanStack Table en modo manual (orden y paginación en el servidor, estado en la dirección; encabezados y paginación son enlaces), y vista de tarjetas por fila debajo de 768 px (AC-9.3).
- **Gráfico** (decisión del 21/11/2026, CHK022): el gráfico de frecuencia es un **componente de servidor** que genera el SVG con los mismos cálculos de posición que hoy hace `estadisticas/views.py::_grafico` (portados a TypeScript y probados con Vitest contra los mismos casos). Funciona sin scripts (NFR-007) y no salta al cargar (NFR-004). La tabla con la misma información sigue presente (AC-7.5). **Recharts no se incorpora**: con scripts, la única interactividad adicional que se admite (por ejemplo, resaltar una barra al enfocarla) se agrega sobre el mismo SVG.
- **Avisos**: Sonner configurado según RN-09 (6 s; los de error permanecen; `role="status"`/`role="alert"`).

**Motivo**: SSR + Server Actions cumplen a la vez "moderno" y "funciona sin scripts" sin duplicar formularios; las mismas URLs hacen reversible cada conmutación (pedido §3.5).

**Alternativas descartadas**: SPA con todo en el cliente y mutaciones desde el navegador (rompe NFR-007 y empeora la primera pintura); Pages Router (en mantenimiento); Remix/React Router o Astro (no son el stack pedido).

---

## R-19 — Sesión compartida y seguridad en la convivencia

**Decisión**:

- **Mismo origen**: el proxy (R-20) sirve Django y Next.js bajo un único dominio; la cookie de sesión de Django (`HttpOnly`, `Secure`, `SameSite=Lax`, ya vigente) viaja a ambos. **No hay CORS** ni tokens en el navegador.
- Next.js no maneja la sesión: en el servidor lee la cookie entrante y la reenvía a Django; en el ingreso (pantalla 5, R-27) la Server Action reenvía al navegador las `Set-Cookie` que responde Django. El archivo de *middleware* de Next.js solo redirige a `/ingresar/?next=…` cuando falta la cookie (comodidad); la autorización real es siempre la respuesta de Django (`401`, `403`, `404`).
- CSRF: Django mantiene `CsrfViewMiddleware`; `CSRF_TRUSTED_ORIGINS` se toma de `QUINI6_ORIGEN_PUBLICO`; las Server Actions envían `X-CSRFToken` (de la cookie `csrftoken`) y el `Origin` original. Next.js además verifica el origen de cada Server Action.
- Django detrás del proxy: `USE_X_FORWARDED_HOST = True` y `SECURE_PROXY_SSL_HEADER` (ya vigente); `ALLOWED_HOSTS` incluye la dirección interna que usa Next.js.
- Next.js agrega `Cache-Control: no-store` en las rutas privadas (NFR-008) y las mismas cabeceras de seguridad que Django (`X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options: DENY`).
- **Prueba obligatoria al iniciar la Etapa 2 (T208 del pedido)**: guion Playwright `e2e/sesion-compartida.spec.ts` — ingresar en Django, abrir una pantalla de Next.js ya autenticado, volver a Django, salir y comprobar que Next.js ya no muestra datos privados; repetir con una persona sin permisos de administración (403 en ambos lados).

**Alternativas descartadas**: JWT en `localStorage` (prohibido por el pedido §5 y riesgo de XSS); subdominios separados con CORS y cookies de dominio (más configuración y superficie de ataque sin beneficio).

---

## R-20 — Enrutador: Caddy

**Decisión**: **Caddy 2** como proxy inverso en desarrollo y producción (`infra/Caddyfile`). Reglas, en este orden:

1. Siempre a Django: `/api/*`, `/static/*`, `/administracion/extracciones/*/csv/`, `/preferencias/*` (hasta su migración), `/salir/`.
2. Siempre a Next.js: `/_next/*`.
3. A Next.js: las rutas de la variable `QUINI6_RUTAS_NEXT` (lista de patrones separados por espacio; vacía en la Etapa 1).
4. Todo lo demás: Django.

**Reversa** (pedido §3.5): se quita el patrón de `QUINI6_RUTAS_NEXT` y se ejecuta `caddy reload`; no se toca código. La tabla de propiedad de cada ruta por etapa está en [contracts/rutas.md](contracts/rutas.md).

**Decisiones del 21/11/2026 (checklist de migración)**:

- **Sin activación parcial** (CHK020): no hay cookie de vista previa, porque NFR-008 solo permite recordar el tema en el navegador. Antes de conmutar, cada pantalla se prueba en el entorno de pruebas (Caddy local con su ruta en `QUINI6_RUTAS_NEXT`) y luego se conmuta para todo el público.
- **Vuelta automática** (CHK030, FR-044): en las rutas de `QUINI6_RUTAS_NEXT`, `reverse_proxy` declara Next.js y Django como destinos con `lb_policy first` y comprobación de salud activa del puerto interno de Next.js; si Next.js no responde, Caddy atiende con Django. Una pantalla cuyas plantillas ya se retiraron pasa a una regla sin respaldo, con `handle_errors` que sirve `infra/no-disponible.html` (página estática con el diseño, el texto `gral.no_disponible` y el pie legal).
- **Formularios abiertos durante un cambio** (CHK031; corregido el 21/11/2026 tras `/speckit-analyze`, I1 e I2): todo formulario POST de Django envía a su dirección con el parámetro `?_interfaz=django` (filtro `{% accion_formulario %}`), y Caddy dirige a Django todo POST que lo trae; cualquier otro POST de una ruta conmutada va a Next.js. Funciona con y sin scripts (sin scripts, una Server Action se envía como POST común **sin** la cabecera `Next-Action`, por eso esa cabecera no sirve como criterio) y también para los manejadores de ruta de Next.js (`/salir/`, `/preferencias/tema/`). Así, un formulario de Django abierto antes de la conmutación, o uno de Next.js abierto antes de una reversa, se envía igual. En una ruta ya retirada (`QUINI6_RUTAS_NEXT_SIN_RESPALDO`), un POST con la marca recibe de Next.js la página de formulario vencido (`gral.csrf_vencido`).

**Motivo**: configuración breve, HTTPS automático en producción y recarga sin cortar conexiones.

**Alternativas descartadas**: `rewrites` de Next.js como enrutador (si Next.js falla, cae todo el sitio, y la reversa exige redeploy); Nginx (más configuración, TLS manual); Traefik (orientado a contenedores dinámicos).

---

## R-21 — Paridad de entornos: PostgreSQL 16 en desarrollo

**Decisión**: `compose.yaml` con `db` (PostgreSQL 16) y `proxy` (Caddy 2); Django y Next.js corren en la máquina (recarga en caliente). `.env.example` trae `QUINI6_DB_*` completos para el contenedor. Se mantiene el respaldo a SQLite si `QUINI6_DB_NAME` está vacía (pruebas rápidas y arranque mínimo, decisión vigente de [001] R-03). La CI ejecuta `pytest` dos veces: SQLite y PostgreSQL 16. La regla "sin funciones exclusivas de un motor" sigue vigente.

**Alternativas descartadas**: PostgreSQL obligatorio también para las pruebas locales (más lento y exige Docker para correr una prueba); todo el entorno en contenedores (recarga más lenta en Windows).

---

## R-22 — Estructura del repositorio y herramientas de Node

**Decisión**: monorepo con **npm workspaces** y **Node 24 LTS** (`.nvmrc`, `engines`):

```text
package.json        # workspaces: ui, frontend, e2e · scripts css, vendor, api:tipos, e2e
ui/                 # @quini6/ui: tokens.css, base.css, variantes.json, marca/ (logotipo, isotipo, favicon)
estilos/django.css  # entrada de Tailwind para las plantillas de Django
frontend/           # Next.js (Etapa 2)
e2e/                # Playwright: guiones únicos para Django y Next.js (R-23)
infra/Caddyfile     # enrutador (R-20)
compose.yaml        # PostgreSQL 16 + Caddy (R-21)
contratos/          # openapi.json y mensajes.json exportados (R-13, R-16)
```

`ruff` y `pytest` siguen como hasta ahora para Python; en Node, ESLint (config de Next.js) y Prettier (con el complemento de orden de clases de Tailwind) en `frontend/`.

**Alternativas descartadas**: pnpm o Bun (otra herramienta que instalar en Windows sin beneficio relevante para tres paquetes); repositorios separados (el contrato de API y los tokens deben cambiar en el mismo commit que su uso).

---

**Ajustes de la implementación (21/11/2026)**:

- **Node 26 LTS** en lugar de 24: es la LTS vigente al instalar (`winget install OpenJS.NodeJS.LTS`); `.nvmrc` = `26` y `engines` acepta `>=24`.
- **Base E2E aparte**: `QUINI6_DB_SQLITE` (opcional) elige el archivo SQLite; los recorridos usan `e2e.sqlite3`, porque `preparar_e2e` vacía la base y no debe tocar `db.sqlite3`.
- **Puerto 8001** para el Django que levanta Playwright, así no choca con un `runserver` de desarrollo en el 8000.
- **Contrato de mensajes normalizado** a una clave por fila (§ "Formato verificable" de [contracts/mensajes.md](contracts/mensajes.md)) para que `tests/unit/test_mensajes_catalogo.py` lo compare con `dominio/mensajes.py`. No cambió ningún texto aprobado; se agregaron los textos de la API (§ "API v1") y `cantidad_ar` en `quini6/templatetags/formato_ar.py` por [contracts/formatos.md](contracts/formatos.md).
- **Icono `arrow-up-down`**: el nombre real en Lucide (el contrato decía `arrows-up-down`).
- **`preparar_e2e`** genera las extracciones con el proceso real de [002] sobre los escenarios de `tests/fuentes_prueba/escenarios/` (período del 01/11/2026 al 15/11/2026, el del quickstart de [002]), con un cliente local sin red.

---

## R-23 — Estrategia de pruebas

**Decisión**:

| Nivel | Herramienta | Etapa | Qué cubre |
|-------|-------------|-------|-----------|
| Dominio | pytest | Todas | Reglas de [001] y [002] **sin cambios de casos**; nuevas: `etiqueta_de`, atajos de período, catálogo de mensajes |
| Vistas y API | pytest + pytest-django | Todas | Vistas HTML (fragmentos HTMX, filtros, orden, paginación, idempotencia, formulario pendiente, tema) y cada operación de la API; **la matriz de acceso de [001] se extiende a todas las operaciones de `/api/v1/`** (visitante, usuario, otro usuario, administrador) |
| Contratos | pytest | Todas | `openapi.json` y `mensajes.json` versionados = generados; catálogo = [contracts/mensajes.md](contracts/mensajes.md); [002] CSV idéntico en estructura (SC-011) |
| Flujos completos | Playwright (`e2e/`) | 1 y 2 | Un guion por historia (HU-01 a HU-13) escrito con **roles y textos accesibles** (`getByRole`, textos del catálogo), nunca con clases CSS. El **mismo guion** corre contra Django y contra Next.js (pedido §11): demuestra que la migración no cambió el comportamiento |
| Accesibilidad | `@axe-core/playwright` en cada guion; addon a11y de Storybook | 1 y 2 | SC-004: 0 críticos y 0 graves, en ambos temas, a 360 px y 1280 px; foco visible y orden de tabulación con guiones de teclado |
| Sin scripts | Playwright con `javaScriptEnabled: false` | 1 y 2 | NFR-007: recorridos básicos de cada pantalla |
| Adaptabilidad | Playwright | 1 y 2 | SC-006: sin desplazamiento horizontal a 360 px y con zoom de texto al 200 % (`scrollWidth ≤ clientWidth`) |
| Unidad frontend | Vitest + Testing Library | 2 | Esquemas Zod, formateadores es-AR (fechas, importes como cadena, dos dígitos), componentes |
| Visual | Playwright `toHaveScreenshot` | 2 | Regresiones por componente (Storybook) y por pantalla, en ambos temas |
| Contraste | Vitest (lee `ui/tokens.css`) | 0 en adelante | SC-009 |

Datos de los guiones: comando `manage.py preparar_e2e` (solo con `QUINI6_DEBUG=1` y `QUINI6_E2E=1`; se niega en otro caso) que crea usuarios, sorteos y extracciones en cada uno de los cinco estados, con datos deterministas. Las pruebas nunca consultan internet ([002]).

---

## R-24 — Rendimiento y presupuesto

**Decisión**: en la Fase 0 se mide la línea base de Django con Lighthouse CI (móvil simulado) en Resultados, Estadísticas, Mis jugadas y Extracción histórica. Criterio "igual o mejor" (pedido §7.3) = para cada pantalla migrada: LCP ≤ línea base y ≤ 2,5 s; CLS ≤ 0,05 (NFR-004); INP ≤ 200 ms; JavaScript inicial ≤ 120 kB comprimido en pantallas públicas y ≤ 200 kB en privadas. Motion y TanStack Table se cargan solo en las pantallas que los usan (importación dinámica donde corresponda).

**Desviación aprobada por el responsable (22/11/2026)**: el JavaScript de base de Next.js 16 + React 19 (`react-dom`, el entorno de Next.js y su cargador) ocupa ≈ 130 kB comprimidos en una página vacía, así que "≤ 120 kB en pantallas públicas" no se alcanza con el stack elegido. Para las públicas el criterio pasa a ser **lo más bajo posible sobre ese piso**, sin bibliotecas que se descarguen sin usarse; las privadas mantienen ≤ 200 kB y el resto del criterio no cambia. Medición y optimizaciones en [linea-base.md](linea-base.md) § "Etapa 2" y en § "Ajustes al correr los guiones contra Next.js".

**Línea base precisada** (CHK015): se mide sobre Django **al cerrar la Etapa 1** (la versión que se reemplaza), con el perfil móvil por defecto de Lighthouse (4G lento simulado, CPU ×4), mediana de 5 corridas, con los datos de `preparar_e2e` y en el mismo equipo que las mediciones de Next.js. La medición de la Fase 0 queda como referencia histórica.

---

## R-25 — Monitoreo (Etapa 3)

**Decisión**: Sentry en Next.js (`@sentry/nextjs`) y en Django (`sentry-sdk`), activado solo si `QUINI6_SENTRY_DSN` tiene valor (vacía = apagado, como en desarrollo y pruebas). `sendDefaultPii: false`, sin reproducción de sesiones, y un filtro `beforeSend` que elimina correos, cookies, cabeceras de autenticación y cuerpos de formularios (Const. IV). Muestreo de rendimiento al 10 %. **Requiere confirmación (P-01)**: enviar errores a un servicio externo es una decisión que el responsable debe aprobar (cuenta, región de los datos y plan).

**Alternativas descartadas**: GlitchTip autoalojado (compatible con el SDK; queda como opción si no se aprueba un servicio externo); registros del servidor solamente (no cubren errores del navegador).

---

## R-26 — Dependencias nuevas

CLAUDE.md cierra la lista de dependencias "salvo justificación en el plan". Esta es esa justificación.

| Dependencia | Etapa | Para qué (requisito) | Se retira |
|-------------|-------|----------------------|-----------|
| `django-ninja` (+ `pydantic`) | 0 | API v1 y OpenAPI (R-16) | No |
| `tailwindcss`, `@tailwindcss/cli` | 0–1 | Estilos con tokens (R-03) | La CLI, en la Etapa 3 |
| `htmx.org`, `alpinejs`, `@alpinejs/anchor`, `@alpinejs/focus` | 1 | Interacciones de R-06 | Etapa 3 |
| `cally` | 1 | Calendario (R-07) | Etapa 3 |
| `lucide-static` | 1 | Iconos (R-05) | Etapa 3 |
| `@playwright/test`, `@axe-core/playwright`, `@lhci/cli` | 0–1 | R-23, R-24 | No |
| `next`, `react`, `react-dom`, `typescript` | 2 | Interfaz (R-18) | No |
| shadcn/ui (código copiado) + Radix UI, `class-variance-authority`, `tailwind-merge`, `tw-animate-css` | 2 | Componentes (R-04) | No |
| `lucide-react`, `motion`, `sonner`, `date-fns`, `react-day-picker` | 2 | R-05, R-15, R-18, R-07 | No |
| `@tanstack/react-query`, `@tanstack/react-table` | 2 | R-10, R-18 | No |
| `react-hook-form`, `zod`, `@hookform/resolvers` | 2 | R-13 | No |
| `openapi-typescript`, `openapi-fetch` | 2 | R-17 | No |
| `vitest`, `@testing-library/react`, `jsdom` | 2 | R-23 | No |
| `storybook` (`@storybook/nextjs-vite`, addon a11y) | 2 (pantalla 1) | Catálogo de componentes (pedido §7.3) | No |
| `@sentry/nextjs`, `sentry-sdk` | 3 | R-25 (si se aprueba P-01) | No |

**No se incorporan**:

- **Zustand**: el único estado de interfaz que la spec permite recordar es el tema, que vive en una cookie (R-14). "Filtros recordados" está prohibido por NFR-008 ("en el navegador solo se recuerda la preferencia de tema"). Aplica la regla de disciplina del pedido (§7.1): ninguna pantalla lo necesita.
- **django-cors-headers**: con un único origen no hay solicitudes entre orígenes (R-19).
- **DRF**: reemplazado por Django Ninja (R-16).
- **Recharts** (21/11/2026, CHK022): solo funciona con scripts, lo que incumple NFR-007 para un gráfico que AC-7.5 exige; el SVG del servidor cumple ambos (R-18).

---

## R-27 — Orden de migración de pantallas (Etapa 2)

**Decisión**: el orden del pedido, con dos agregados necesarios para llegar a "Django solo API":

| Orden | Pantalla (rutas en [contracts/rutas.md](contracts/rutas.md)) | Nota |
|-------|---------------------------------------------------------------|------|
| 0 | Estructura común: `layout` (encabezado, menú de cuenta, menú móvil, saltar al contenido, pie, tema), páginas 403/404/500 | Requisito de cualquier pantalla; se conmuta con la 1 |
| 1 | Extracción histórica (inicio, detalle, sorteo extraído, eliminar) | Valida casi todo el sistema de diseño |
| 2 | Estadísticas | Gráfico y filtros complejos |
| 3 | Mis jugadas | Estados vacíos y formularios |
| 4 | Resultados y búsqueda (incluye inicio `/`) | Rendimiento para visitantes |
| 5 | Ingresar y Crear cuenta | Toca la autenticación; la sesión compartida ya está probada |
| 6 | **Administración de sorteos** ([001]: listado, carga, números, premios, publicación, correcciones, historial) | **Agregada (P-03)**: no figuraba en el pedido y sin ella Django no puede quedar como API pura |

Criterio de terminado de cada pantalla: el del pedido §7.3, verificado con el guion E2E único, axe, prueba a 360 px, historia en Storybook, presupuesto de R-24 y reversa probada (quitar la ruta de `QUINI6_RUTAS_NEXT` y comprobar que Django responde).

---

## R-28 — Conmutación, estabilización y retiro (Etapa 3)

**Decisión** (precisada el 21/11/2026, CHK016 a CHK018 y CHK033): por pantalla:

1. **Prueba previa** en el entorno de pruebas: guion E2E de sus historias y de HU-14, axe, 360 px y presupuesto de R-24.
2. **Conmutación** para todo el público, agregando sus patrones a `QUINI6_RUTAS_NEXT`, un **martes o jueves entre las 10 y las 12** (lejos de los sorteos de los miércoles y domingos a la noche, cuando más se consulta) y con la persona desarrolladora disponible para revertir.
3. **Estabilización de 14 días** con la reversa disponible, observando errores (Sentry si se aprueba P-01; registros del servidor y de Caddy si no).
   - **Reversa inmediata** (ejecutada en menos de 15 minutos) ante cualquiera de estos casos: una tarea principal de SC-005 que no se puede completar; un dato, texto o permiso distinto del de Django (FR-041); una incidencia crítica de accesibilidad. La decide el responsable (o la persona desarrolladora si el responsable no está disponible, con aviso inmediato). Tras una reversa, los 14 días vuelven a empezar con la siguiente conmutación.
   - **Estabilización cumplida**: 14 días seguidos sin ninguno de esos casos y con una tasa de respuestas de error 5xx de la pantalla no mayor que la de su versión de Django en las dos semanas previas a la conmutación.
4. **Punto sin retorno**: el retiro de sus plantillas, fragmentos, vistas y rutas HTML de Django requiere la **aprobación explícita del responsable**, registrada en `plan.md` (§ Registro de conmutaciones) con la fecha. Las vistas de API, el CSV, el trabajador y los comandos se quedan.
5. Al retirar la última, eliminar HTMX, Alpine.js, Cally, `lucide-static`, la compilación de `estilos/django.css` y `static/vendor/`. Auditoría final con lector de pantalla y medición de SC-001 a SC-012.

---

## R-29 — Sistema visual y responsivo (RN-11)

**Decisión**: escala de espaciado en múltiplos de 4 px; radios 8 px (controles) y 12 px (tarjetas); dos sombras sutiles; alturas de control de 44 px (táctil, NFR-001); tipografía `sans` del sistema (sin descargas: sin saltos al cargar, NFR-004) con escala 12/14/16/18/24/32 px; ancho de lectura máximo de 72 rem en escritorio; un solo botón principal por pantalla; puntos de quiebre de Tailwind (`md` = 768 px, que coincide con el límite de AC-5.4). Tablas: a partir de 768 px, tabla; debajo, tarjetas con cada columna rotulada (`<dl>`), sin desplazamiento horizontal (NFR-003). Textos largos: `truncate` con el texto completo en `title` y en un elemento enfocable o en el detalle (FR-030).

---

## R-30 — Desviaciones respecto del pedido de planificación

La spec aprobada prevalece sobre el pedido cuando se contradicen (Const. I). Ninguna desviación cambia la estrategia.

| Pedido | Spec aprobada | Decisión del plan |
|--------|---------------|-------------------|
| "Eliminación con posibilidad de deshacer (si se aprueba)" y Sonner con "Deshacer" | D-03: **sin "Deshacer"** (FR-009, AC-2.5) | Sin "Deshacer". Sonner solo para avisos. Ningún cambio de backend en la eliminación |
| Zustand para "filtros recordados" | NFR-008: en el navegador **solo** se recuerda el tema | No se recuerdan filtros; Zustand no se incorpora (R-26) |
| "Estados de extracción normalizados" como cambio de backend | RN-01 y Supuestos: **solo presentación**, no se agrega un estado ni se cambia [002] RN-33 | Función pura derivada (R-08); el modelo no cambia |
| "Ejecutar extracciones en segundo plano con estado y progreso consultables" (T007) | Ya existe: trabajador de [002] R-01 y avance de [002] FR-003 | Sin trabajo nuevo; solo se expone el avance en la API |
| "Advertencia: ámbar, si se aprueba la decisión 0" | RN-01 ya fija ámbar para "Con advertencias" | Ámbar como token propio, distinto del naranja de acento ([contracts/tokens.md](contracts/tokens.md)) |
| "CORS/CSRF para convivencia" | — | CSRF sí; CORS no hace falta con un único origen (R-19) |
| Orden de migración de 5 pantallas | — | Se agregan la estructura común (0) y Administración de sorteos (6), P-03 (R-27) |
| "Calendario: campo de fecha con control propio ligero" | FR-010 | Cally como control ligero con estilo propio (R-07) |
| Principio 6: "una pantalla que se migra pronto recibe solo correcciones críticas" | HU-01 a HU-03 (P1) viven en Extracción histórica | Spec completa en todas las pantallas; el principio se aplica al diseño (R-01, confirmado el 21/11/2026) |
| Recharts para el gráfico de Estadísticas | NFR-007 y AC-7.5: el gráfico debe existir sin scripts | SVG generado en el servidor también en Next.js; Recharts no se incorpora (R-18, confirmado el 21/11/2026) |
| "Activar la pantalla para un grupo pequeño" | NFR-008: solo el tema se recuerda en el navegador | Sin activación parcial; prueba en el entorno de pruebas y conmutación para todo el público en una franja fija (R-20, R-28, confirmado el 21/11/2026) |

---

## R-31 — Avisos compartidos entre aplicaciones (FR-043, AC-14.3)

**Decisión** (21/11/2026, CHK009): los avisos de una acción se siguen guardando con el sistema de mensajes de Django (almacenamiento en la sesión, del lado del servidor). Django los muestra en sus plantillas como hoy. Next.js los obtiene en el servidor al mostrar cada página con `GET /api/v1/avisos/`, que **los entrega y los marca como leídos** (igual que hace una plantilla de Django al mostrarlos), y los pinta con el componente `Toast`/`Callout` según RN-09. Las Server Actions de Next.js que terminan en una redirección agregan su aviso con `POST /api/v1/avisos/` antes de redirigir, así el aviso aparece sea cual sea la aplicación de destino. Nada se guarda en el navegador.

**Alternativas descartadas**: aviso en la dirección (`?aviso=…`; queda en el historial y se puede falsificar); cookie de aviso de Next.js (Django no la leería y suma una cookie, NFR-008).

---

## R-32 — Decisiones técnicas de la revisión del checklist de migración

Resuelven ítems de [checklists/migracion.md](checklists/migracion.md) que no requieren decisión del responsable.

| Ítem | Decisión |
|------|----------|
| CHK002 | [contracts/rutas.md](contracts/rutas.md) § 3 asigna dueño a toda ruta de [001] y [002]; `/salir/` y `/preferencias/*` se mueven con la pantalla 5; las páginas de error las genera la aplicación dueña de la ruta, y las rutas inexistentes, Django (regla 5) |
| CHK003, CHK004 | "Contrato primero" se aplica **por pantalla**: sus DTO y operaciones se escriben en [contracts/api.md](contracts/api.md) y se aprueban antes de empezar su migración; es una compuerta del criterio de terminado (R-27), no un trabajo de la Fase 0 |
| CHK005 | [contracts/componentes.md](contracts/componentes.md) § 4 fija la versión sin scripts de cada componente interactivo también en Next.js |
| CHK006 | En Next.js, toda lectura privada usa `fetch` con `cache: "no-store"` y renderizado dinámico; la caché del enrutador del cliente no se usa para páginas privadas (`staleTimes.dynamic = 0`); `proxy.ts` agrega `Cache-Control: no-store` a las rutas privadas |
| CHK007 | Nuevo contrato [contracts/formatos.md](contracts/formatos.md): reglas únicas de fechas, horas, importes, porcentajes y números, con casos de ejemplo que prueban **las dos** implementaciones (filtros de Django y `frontend/src/lib/formato.ts`) |
| CHK008 | El proceso de Next.js corre con `TZ=America/Argentina/Buenos_Aires` y, además, todo formateo pasa `timeZone: "America/Argentina/Buenos_Aires"` explícito; "hoy" lo calcula siempre Django (atajos, máximos de fecha) |
| CHK011 | El servidor de Next.js genera la `clave_idempotencia` (UUID v4) al mostrar el formulario y la Server Action la envía como `Idempotency-Key`; Django la registra en la sesión igual que en sus formularios (R-11) |
| CHK013, CHK014 | Lo que debe ser idéntico y lo que puede diferir queda en AC-14.5 y FR-041. La igualdad visual se garantiza por construcción (mismos tokens, variantes e iconos) y se revisa a mano por pantalla comparando ambas versiones lado a lado con los datos de `preparar_e2e`; las capturas automáticas se comparan contra la referencia aprobada de cada implementación, no entre ellas |
| CHK021 | Las páginas de Next.js se generan completas en el servidor: el contenido principal no usa `loading.tsx` ni `Suspense` con esqueleto en la primera carga; los marcadores de posición quedan para lo que se actualiza después (avance, listado tras eliminar), como dice la spec |
| CHK025 | Ambas implementaciones de NavBar, AccountMenu, menú móvil y ThemeSelect siguen el mismo contrato y pasan el mismo guion de HU-05; pasar de una aplicación a la otra es una carga completa de página (con View Transitions donde el navegador la soporte) |
| CHK026 | Cada página de Next.js consulta la API con la cookie de la persona, lo que renueva la sesión igual que una página de Django (`SESSION_SAVE_EVERY_REQUEST`, [001] NFR-005). El ingreso por API usa el mismo servicio `cuentas.servicios` (bloqueo tras 5 fallos y mensajes que no revelan si el correo existe) |
| CHK027, CHK028 | Los criterios de terminado se verifican con escenarios observables (HU-14, [quickstart.md](quickstart.md)); la cabecera `X-Interfaz` y Lighthouse son apoyo técnico, no criterio de aceptación |
| CHK029 | Umbrales fijos de R-24 con la línea base precisada |
| CHK032 | Orden de despliegue: primero Django (API con cambios solo compatibles hacia atrás), después Next.js. Un campo u operación se quita de la API solo cuando ninguna versión desplegada de Next.js lo usa |
| CHK034 | La migración 0003 es reversible (`RemoveConstraint` automático de Django); si se detiene por datos existentes, no deja cambios a medias (una sola operación dentro de una transacción) |
| CHK035 | La auditoría de accesibilidad y la revisión con teclado y lector de pantalla son parte del criterio de terminado de **cada** pantalla migrada, en ambos temas y anchos (R-27) |
| CHK036 | Los datos que el monitoreo puede recolectar son los de R-25; cualquier campo adicional exige actualizar R-25 y P-01 |
| CHK031 | Ver R-20: marca `?_interfaz=django` en los formularios de Django (no la cabecera `Next-Action`), decidida el 21/11/2026 |
| CHK037 | Next.js envía las mismas cabeceras de seguridad que Django (R-19); HSTS y HTTPS los aplica Caddy para ambas; `serverActions.allowedOrigins` = `QUINI6_ORIGEN_PUBLICO` |

---

## Ajustes de la implementación de la Fase 18 (22/11/2026)

Decisiones técnicas tomadas al construir la convivencia (T149 a T171), sin cambiar ningún requisito:

- **Vuelta automática con comprobación pasiva** (R-20, T153): `health_uri /` exigiría que Next.js responda 2xx en `/`, ruta que recién existe con la pantalla 4, y el contrato no admite rutas de salud (rutas.md § 4). Caddy usa `lb_policy first` + `lb_try_duration 3s` + `fail_duration 10s` + `unhealthy_status 502 503 504`: si Next.js rechaza la conexión, el mismo pedido lo atiende Django. Verificado con Next.js detenido (`X-Interfaz: django`).
- **`X-Interfaz` en las rutas conmutadas** la envía Next.js (`next.config.ts`); Caddy pone `django` solo si falta (`header ?X-Interfaz django`), así la cabecera dice quién respondió de verdad.
- **Avisos en la sesión** (R-31): `MESSAGE_STORAGE = SessionStorage`. Con el almacenamiento por cookie de Django, un componente de servidor de Next.js no podría borrar la cookie al marcar los avisos como leídos y se repetirían.
- **Acceso por ruta en `proxy.ts`** (AC-14.1, NFR-007): en Next.js 16, `forbidden()`/`notFound()` lanzados en una página responden un armazón que solo se completa con scripts (comprobado también en una aplicación mínima). El proxy presenta la respuesta de Django de `GET /api/v1/sesion/` antes de responder: sin sesión → "Ingresar"; `/administracion/*` sin permisos → `rewrite` a la página "Sin permisos" con **403** y completa en el HTML. Django sigue autorizando cada operación de la API; las pantallas que reciban `404` de una operación propia (jugada ajena o inexistente, sorteo inexistente) muestran la página de error en la misma página.
- **Renovación de la sesión y `csrftoken`** (CHK026, R-19): el proxy consulta `GET /api/v1/sesion/` con la cookie de la persona y devuelve al navegador las `Set-Cookie` de Django; los formularios POST que atiende Django desde Next.js (`/salir/`, `/preferencias/tema/`) llevan `csrfmiddlewaretoken` con el valor de esa cookie.
- **AccountMenu como panel desplegable**, no como `DropdownMenu` de Radix: igual que Django (botón con `aria-expanded` que muestra "Salir"); un `role="menu"` cambiaría el rol de "Salir" y el guion de HU-05 dejaría de servir para ambas interfaces.
- **Entrada de pantalla con CSS** (`template.tsx`, `tw-animate-css`) en lugar de Motion: la opacidad inicial de Motion en el HTML del servidor dejaría el contenido invisible sin scripts.
- **Textos de la estructura común al catálogo** (contracts/mensajes.md § 4, "Estructura común"): los rótulos que `templates/base.html` y las páginas de error escribían sin clave pasan al catálogo con la misma redacción; `aviso.region` ("Avisos", ‡) es el nombre accesible que Sonner exige para su región.
- **`ui/dominio.css`**: la base y los componentes propios del dominio salieron de `estilos/django.css` a `ui/`, importados por ambas interfaces (mismo aspecto por construcción, CHK013).
- **Esqueleto de `/administracion/extracciones/` en Next.js**: solo la estructura común y el acceso, para la prueba de sesión compartida (T169); la pantalla completa es T178. No se conmuta en producción antes de T180.
- **Telemetría desactivada**: `NEXT_TELEMETRY_DISABLED=1` y Storybook con `disableTelemetry` (CI y scripts); `agentRules: false` evita que `next dev` genere `AGENTS.md`.

## Ajustes de la implementación de las Fases 19 a 24 (22/11/2026)

Decisiones técnicas tomadas al migrar las seis pantallas a Next.js, sin cambiar ningún requisito:

- **ActionMenu ⋮ con `<details>`** (como el AccountMenu de la Fase 18): el mismo marcado que `templates/ui/_menu_acciones.html` con el teclado, el anclaje y "abrir otro cierra el anterior" programados en React. Con el DropdownMenu de Radix los guiones E2E dejaban de servir para ambas interfaces y, sin scripts, no habría menú; con `<details>` sí lo hay (mejor que el mínimo de componentes.md § 4).
- **Cuerpo completo hacia Django**: `apiServidor()` envía el cuerpo con `Content-Length`; el `fetch` de Next.js lo mandaba por partes (`Transfer-Encoding: chunked`) y Django (WSGI) lo recibía vacío (los POST de las Server Actions fallaban con 422).
- **Redirecciones relativas** (`lib/redireccion.ts`): detrás de Caddy, un manejador de ruta ve la URL interna (`http://localhost:3000`); `NextResponse.redirect(new URL(...))` sacaba al navegador del sitio. Toda `Location` es una ruta del sitio.
- **Avisos al redirigir desde una página** (`…/avisar/route.ts`): una página no puede agregar un aviso y redirigir, porque la estructura común lee los avisos al mismo tiempo y los consumiría en la respuesta que se descarta. La página redirige a un manejador de ruta que agrega el aviso (solo claves de una lista cerrada) y redirige con 303. Además, `AvisosAlNavegar` pide los avisos al montar y al cambiar de dirección (navegación del cliente), y un mismo aviso no se duplica (id del Toast = tipo + texto).
- **Avisos sin scripts fuera del documento al hidratar** (`SoloSinScripts`): como Django, que pasa los avisos de la página a Toast; ocultos con CSS seguían contando para los lectores y los guiones.
- **Server Actions sin sesión**: `proxy.ts` no redirige un pedido con `Next-Action`; la operación de Django responde 401 con el `pendiente` y el formulario ofrece "Ingresar". "Volver al formulario" envía el token por POST a la página de Next.js; `proxy.ts` lo verifica con `POST /api/v1/formularios/pendiente/` (operación agregada al contrato y aprobada) y la página recibe lo escrito en una cabecera interna, sin enviar nada.
- **Rótulos de las plantillas al catálogo** (`rot.*`, criterio aprobado): los textos que las plantillas de Django tenían escritos se catalogaron con la misma redacción para que Next.js no escriba textos fuera del catálogo.
- **Administración de sorteos con formularios descritos por Django** (`FormularioDTO`): la API describe cada formulario de `resultados/forms.py` campo por campo (nombre, etiqueta, tipo, valor, opciones, errores) y recibe `{campos}` con los mismos nombres; la pantalla de Next.js los dibuja (`FormularioDjango`) con los mismos rótulos y la validación es siempre la de Django.
- **Guiones E2E según las rutas conmutadas** (`E2E_RUTAS_NEXT`): las expectativas de "quién atiende" cada ruta salen de las reglas de contracts/rutas.md § 3, así el mismo guion sirve en cada etapa de la conmutación. Los guiones de calendario preguntan lo mismo a Cally (Django) y a react-day-picker (Next.js) (`e2e/apoyo/calendario.ts`), y los avisos se buscan por su texto (Next.js agrega su anunciador de rutas con `role="alert"`).
- **Transiciones entre documentos**: el `@view-transition` de `ui/base.css` deja la página sin recibir clics unos instantes al pasar de Django a Next.js; los guiones que hacen un clic "crudo" esperan antes a que el enlace sea pulsable.
- **Sentry** (P-01): Django y Next.js lo inician solo si hay DSN (`QUINI6_SENTRY_DSN`, `NEXT_PUBLIC_QUINI6_SENTRY_DSN`), con el mismo filtro de eventos (`quini6/observabilidad.py`, `lib/observabilidad.ts`).

### Ajustes al correr los guiones contra Next.js (T180 a T209, 22/11/2026)

- **Sesión sin cambios = solo renovar el vencimiento** (`SESSION_ENGINE = "quini6.sesiones"`): con `SESSION_SAVE_EVERY_REQUEST`, el almacén de Django reescribía la sesión completa al final de cada solicitud con los datos leídos al empezar. Next.js hace varias solicitudes simultáneas (sesión, avisos, lecturas de la página) y una que terminaba después borraba el aviso que `…/avisar/` acababa de agregar (Toast de error ausente en 5 de 18 repeticiones). Ahora una sesión que la solicitud no modificó solo actualiza `expire_date` y no revive una sesión cerrada; una modificada se guarda igual que antes (`tests/integration/test_003_sesion_concurrente.py`).
- **SQLite con `transaction_mode: IMMEDIATE` y `timeout: 20`** (solo pruebas y E2E): con las solicitudes simultáneas de Next.js, una transacción que primero leía y después escribía ("Quitar revisión") fallaba con `database is locked` (500). Así toma el bloqueo de escritura al empezar y espera su turno. PostgreSQL no cambia.
- **Sesión vencida sin scripts en un formulario de Next.js**: sin scripts, Next.js vuelve a dibujar la página después de ejecutar la Server Action; la lectura de la página recibía 401 y `redirect()` respondía 307, que repetía el POST en `/ingresar/` (409) y perdía lo escrito. `proxy.ts` marca esas solicitudes con la cabecera interna `x-quini6-accion` (nunca la del navegador) y las lecturas que lo piden (`verificarRespuesta(…, { continuarEnAccion: true })`, hoy las de los formularios de Mis jugadas) siguen sin datos, para que el formulario muestre "La sesión venció…" con su `pendiente` (FR-032). No otorga nada: sin sesión, Django no entrega datos. **Pendiente**: las páginas de Administración (Extracción histórica, sorteos) no lo aplican todavía; sin scripts y con la sesión vencida, su formulario no conserva lo escrito.
- **Guiones sin scripts y transición entre documentos**: `ingresarComo` espera a que termine el `@view-transition` (sondeo con `evaluate`, porque `waitForFunction` no avanza sin scripts); mientras dura, el clic forzado en una casilla de 1 px caía en la capa de la transición y no la marcaba.
- **JavaScript inicial (R-24)**: medido detrás del enrutador, Next.js descargaba 238–303 kB por pantalla. Se bajó a ≈ 165–190 kB sin cambiar comportamiento ni marcado visible:
  - el calendario (Popover de Radix, react-day-picker y date-fns `es`) se descarga al abrirlo o al acercar el puntero o el foco a "Abrir calendario" (`calendario-diferido.tsx`, `panel-calendario.tsx`, anclado con `virtualRef`), como Cally en Django;
  - `useHidratado` pasó a `lib/hidratado.ts`: al importarlo desde `date-field.tsx`, `SoloSinScripts` (estructura común) arrastraba el calendario a todas las pantallas;
  - TanStack Query se provee solo en el segmento de Extracción histórica; `MotionConfig` y `TooltipProvider` no tenían ningún uso y se quitaron con **Motion**;
  - `DataTable` es un componente de servidor sin **TanStack Table** (en modo manual no hacía nada en el navegador; mismo marcado);
  - el período se valida con `validarPeriodo` (función propia con los mismos textos) en lugar de **Zod**, **React Hook Form** y `@hookform/resolvers`; el formulario de inicio sigue el patrón del de Estadísticas (al salir de cada campo y al enviar, foco en el primer error);
  - Sonner se descarga con el primer aviso (`toaster-sonner.tsx`; los avisos esperan en una cola);
  - `Icono` dibuja en línea los mismos SVG que Django (`iconos-svg.ts`, generado por `node scripts/iconos.mjs --next`) en lugar de Lucide React. Al retirar Django (T230), `iconos-svg.ts` queda versionado como fuente.
- **`npm run lhci` detrás del enrutador**: `--ingreso <Django directo>` obtiene la sesión en Django, porque `/ingresar/` ya lo atiende Next.js; la cookie es la misma sesión de Django y sirve en el enrutador.

## Puntos que requieren confirmación del responsable

No bloquean el inicio de la Fase 0 ni de la Etapa 1.

| ID | Punto | Recomendación | Bloquea | Si no se aprueba (CHK038) |
|----|-------|---------------|---------|---------------------------|
| P-01 | Enviar errores y métricas a **Sentry** (servicio externo) | **Aprobado el 21/11/2026**: Sentry con `sendDefaultPii: false`, sin reproducción de sesiones y con el filtro de R-25; se activa solo con `QUINI6_SENTRY_DSN` | — | — |
| P-02 | **Archivo de Figma** y diseño del **logotipo, isotipo y favicon** (RN-08) | **Aprobado el 21/11/2026**: isotipo y logotipo tipográficos provisionales ("QUINI_6" en `primary`, sin imitar marcas oficiales), reemplazables sin tocar código; RN-08 aprobada con ese criterio. Figma se incorpora cuando exista y desde entonces manda (R-02) | — | — |
| P-03 | Agregar **Administración de sorteos** como pantalla 6 de la migración | **Aprobado el 21/11/2026** | — | — |
| P-04 | Textos marcados ‡ en [contracts/mensajes.md](contracts/mensajes.md) (incluye RN-02, RN-07, RN-09) | **Aprobados el 21/11/2026** tal como estaban (pasaron a †). `form.trabajando_*` (agregados después, FR-034) **aprobados también el 21/11/2026** tal cual (pasaron a †) | — | — |

**Supuesto registrado (CHK039)**: la Etapa 1 deja la feature completa (HU-01 a HU-13) aunque las Etapas 2 y 3 no se ejecuten. Ejecutarlas o no es decisión del responsable al cerrar la Etapa 1; HU-14 solo aplica si se ejecutan.
