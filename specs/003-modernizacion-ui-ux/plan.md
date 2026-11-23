# Plan de implementación (Implementation Plan): Modernización visual y de experiencia de uso

**Rama**: `003-modernizacion-ui-ux` | **Fecha**: 21/11/2026 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación funcional de `specs/003-modernizacion-ui-ux/spec.md` (con las aclaraciones del 21/11/2026) y el pedido de planificación del responsable del 21/11/2026: estrategia híbrida en tres etapas (Django mejorado → Next.js en paralelo → conmutación gradual) y el stack de la Etapa 2.

**Marco normativo**: [Constitución QUINI_6 v1.1.0](../../.specify/memory/constitution.md). Se apoya en los planes de [001](../001-quini6-mvp/plan.md) y [002](../002-extraccion-historica-csv/plan.md), cuyas decisiones siguen vigentes salvo donde [research.md](research.md) indica que esta feature las reemplaza.

## Resumen (Summary)

La feature rediseña **todas** las pantallas de [001] y [002] para que cualquier persona entienda dónde está, qué ocurrió y qué puede hacer: etiquetas de estado con texto, icono y color; menú de acciones anclado y confirmación de eliminación; avance en vivo de las extracciones; un único calendario en español; navegación con sección activa y menú móvil; ingreso centrado; estados vacíos que orientan; tablas ordenables, paginadas y apiladas en móvil; avisos visibles; lenguaje neutro con "sorteo" como término único; tema claro y oscuro; y un sistema visual único con la paleta de RN-12. **No cambia ningún dato, cálculo, permiso ni el CSV** (NFR-009).

**Enfoque técnico** (detalle en [research.md](research.md)):

1. **Fase 0 — cimientos**: tokens de diseño en un solo archivo (`ui/tokens.css`, transcripción de Figma) con contraste verificado; catálogo único de mensajes (`dominio/mensajes.py`); API v1 con **Django Ninja** y OpenAPI exportado; PostgreSQL 16 en desarrollo y **Caddy** como enrutador; línea base de rendimiento y accesibilidad.
2. **Etapa 1 — Django mejorado**: la spec completa sobre las plantillas actuales, con **Tailwind CSS 4**, **HTMX** (avance en vivo), **Alpine.js** (menús, diálogos, validación previa, avisos) y **Cally** (calendario), siempre como mejora progresiva: sin scripts, todo sigue funcionando.
3. **Etapa 2 — Next.js en paralelo**: **Next.js 16 (App Router) + TypeScript estricto** con shadcn/ui, Tailwind 4 (los mismos tokens y variantes), TanStack Query y Table, React Hook Form + Zod (mensajes del mismo catálogo), Sonner y Motion; el gráfico de Estadísticas se genera como SVG en el servidor, igual que hoy (R-18). Renderizado en el servidor y **Server Actions** para que los formularios funcionen sin scripts. Las pantallas se construyen en el orden de R-27, consumen solo la API y pasan **el mismo guion E2E** que su versión de Django.
4. **Etapa 3 — conmutación**: Caddy dirige cada ruta migrada a Next.js con un cambio de configuración reversible y vuelve sola a Django si Next.js no responde; tras 14 días estables y con la aprobación del responsable se retiran sus plantillas. Django queda como API, CSV y trabajador. La convivencia cumple HU-14 (FR-039 a FR-044), agregada a la spec el 21/11/2026 tras el checklist de migración.

La Etapa 1 cumple por sí sola todos los criterios de aceptación; las Etapas 2 y 3 cambian la tecnología de la interfaz sin cambiar el comportamiento (R-01).

## Contexto técnico (Technical Context)

| Aspecto | Decisión | Ref. |
|---------|----------|------|
| **Lenguajes y versiones** | Python 3.12 + Django 5.2 LTS (sin cambios). Node 24 LTS. TypeScript 5 estricto (Etapa 2) | [001] R-01, R-22 |
| **Dependencias principales** | Python: `django-ninja` (única nueva). Etapa 1: Tailwind CSS 4 (CLI), HTMX 2, Alpine.js 3 (+ `anchor`, `focus`), Cally, `lucide-static`. Etapa 2: Next.js 16, React 19, shadcn/ui (Radix), Lucide React, Motion, TanStack Query 5 y Table 8, React Hook Form 7, Zod 4, Sonner, date-fns 4 (`es`), `openapi-typescript` + `openapi-fetch`. Etapa 3: Sentry (sujeto a P-01). Versiones exactas fijadas en `package-lock.json` y `pyproject.toml` al iniciar cada etapa. **Ajuste del 22/11/2026 (presupuesto de R-24)**: se quitaron Motion, TanStack Table, React Hook Form, Zod y `@hookform/resolvers`, que no aportaban comportamiento propio (research.md § "Ajustes al correr los guiones contra Next.js") | R-26 |
| **Almacenamiento** | PostgreSQL 16 en producción **y en desarrollo** (compose); SQLite sigue disponible si `QUINI6_DB_NAME` está vacía y para `pytest` local. Sin tablas nuevas; una restricción única parcial (RN-03). Preferencia de tema en cookie; idempotencia en la sesión; formulario pendiente en token firmado | R-09, R-11, R-12, R-14, R-21, [data-model.md](data-model.md) |
| **Pruebas** | `pytest` (dominio sin cambios de casos; vistas, API con matriz de acceso, contratos OpenAPI y de mensajes), Playwright + axe con **un guion por historia que corre contra Django y contra Next.js**, Vitest + Testing Library, Storybook (addon a11y), capturas comparadas, Lighthouse CI | R-23, R-24 |
| **Plataforma objetivo** | Servidor Linux con HTTPS: Caddy → gunicorn (Django) y `next start` (salida `standalone`), más el trabajador de [002] como servicio | [001] R-16, R-20 |
| **Tipo de proyecto** | Etapa 1: monolito web renderizado en el servidor. Etapas 2–3: interfaz Next.js (SSR) + backend Django (API, CSV, trabajador) bajo un mismo origen | R-01, R-18, R-19 |
| **Objetivos de rendimiento** | Respuesta visible < 100 ms (NFR-005); LCP ≤ 2,5 s y ≤ línea base de Django; CLS ≤ 0,05; INP ≤ 200 ms; JS inicial ≤ 120 kB comprimido (públicas) / ≤ 200 kB (privadas); sondeo del avance cada 3 s. **Desviación aprobada el 22/11/2026**: en las públicas, el piso es el de Next.js 16 + React 19 (≈ 130 kB en una página vacía); se mide "lo más bajo posible" sobre ese piso ([linea-base.md](linea-base.md) § Etapa 2) | R-10, R-24 |
| **Restricciones** | WCAG 2.2 AA y contraste de NFR-002 en ambos temas; desde 360 px sin desplazamiento horizontal y con texto al 200 %; mejora progresiva (NFR-007); solo el tema se recuerda en el navegador (NFR-008); español de Argentina y formatos de Const. VII; importes nunca como `float` (también en la API y en TypeScript); sin cambios de negocio ni del CSV (NFR-009); permisos verificados en el servidor | R-13, R-16, R-18, R-19 |
| **Escala y alcance** | 6 grupos de pantallas (unas 30 plantillas), 21 componentes de interfaz, unas 38 operaciones de API, 1 ruta HTML nueva (`/preferencias/tema/`), 1 migración, ~110 textos reescritos o nuevos. Pocos administradores; tráfico público moderado | [contracts/](contracts/) |
| **Cronograma orientativo** (una persona) | Fase 0: 1 semana · Etapa 1: 2–3 semanas · Etapa 2: 5–7 semanas (incluye la pantalla 6, P-03) · Etapa 3: 2–3 semanas. Se recalcula al cerrar la Fase 0 **Recalculado al cerrar la Fase 0 (21/11/2026, T036)**: 44 plantillas (30 iconos aparte), 262 textos en el catálogo único, unas 38 operaciones de API; la Fase 0 llevó lo previsto y se mantiene la estimación (Etapa 1: 2–3 semanas; Etapa 2: 5–7 semanas; Etapa 3: 2–3 semanas). | Pedido §12, [linea-base.md](linea-base.md) |

No quedan marcas `NEEDS CLARIFICATION`. Los cuatro puntos que requieren confirmación (P-01 a P-04, [research.md](research.md) al final) no bloquean el inicio de la Fase 0 ni de la Etapa 1.

## Verificación contra la Constitución (Constitution Check)

*Compuerta: se evaluó antes de la Fase 0 y se reevaluó después del diseño de la Fase 1.*

| Principio | Cómo lo cumple el plan | Antes | Después del diseño |
|-----------|------------------------|:-----:|:------------------:|
| **I. SDD (no negociable)** | Cada componente, ruta, operación de API y texto se vincula a un FR, AC o RN de la spec. Donde el pedido de planificación contradice la spec aprobada, **prevalece la spec** y la desviación queda registrada (R-30: sin "Deshacer", sin filtros recordados, etiqueta "Con error" solo de presentación). Los textos nuevos que propone el plan (‡) y los cuatro puntos P-01 a P-04 se elevan para aprobación. La migración a Next.js es una **decisión técnica** del responsable: no agrega funcionalidades ni cambia la experiencia especificada (mismo guion E2E en ambas versiones), y su comportamiento visible durante la convivencia está trazado a HU-14 (FR-039 a FR-044), aprobada el 21/11/2026 | ✅ | ✅ |
| **II. Trazabilidad** | Los contratos citan el requisito de cada elemento ([componentes.md](contracts/componentes.md), [rutas.md](contracts/rutas.md), [api.md](contracts/api.md), [mensajes.md](contracts/mensajes.md), [tokens.md](contracts/tokens.md)); [quickstart.md](quickstart.md) vincula cada escenario con sus AC; los guiones E2E se nombran por historia | ✅ | ✅ |
| **III. Acceso público / funciones personales** | Ninguna ruta cambia de nivel. Los accesos directos nuevos (estado vacío de Resultados) solo se muestran a quien ya tiene el permiso (FR-026). La API repite exactamente los niveles de las vistas HTML | ✅ | ✅ |
| **IV. Aislamiento y seguridad** | Autorización en Django en cada GET, POST y operación de API (matriz de acceso extendida a `/api/v1/`); jugadas filtradas por `usuario=request.user` con 404 idéntico; sesión de Django con cookie `HttpOnly` + `Secure` + `SameSite`, **sin tokens en el navegador** y **sin CORS** (mismo origen); CSRF en todas las mutaciones, también desde Next.js; `no-store` en páginas y respuestas privadas; formulario pendiente firmado y sin contraseñas; Sentry sin datos personales y sujeto a aprobación (P-01). Next.js nunca decide permisos | ✅ | ✅ |
| **V. Sin apuestas ni pagos** | Sin cambios de funcionalidad. El aviso legal del pie gana visibilidad (AC-10.2) | ✅ | ✅ |
| **VI. Criterios verificables por personas no técnicas** | [quickstart.md](quickstart.md) describe 30 escenarios observables desde la aplicación; las pruebas automáticas los complementan, no los reemplazan | ✅ | ✅ |
| **VII. Español de Argentina** | Catálogo único de mensajes con forma neutra (D-01) y glosario (RN-10); formularios con `novalidate` para que el navegador no muestre globos en otro idioma; calendario con `es-AR` y semana desde el lunes; formatos `dd/mm/aaaa`, `HH:MM`, `$ 1.234,56` y dos dígitos aplicados por la interfaz a partir de datos ISO y decimales en cadena | ✅ | ✅ |
| **VIII. Exactitud de reglas y datos** | Ningún cálculo cambia; las reglas de fechas de [001] y [002] se siguen validando en el servidor; "Con error" nunca oculta un sorteo no recuperado (precedencia sobre "Con advertencias"); el `Dato` de [002] conserva su estado explícito en la API | ✅ | ✅ |
| **IX. Integridad y trazabilidad** | Sin escrituras nuevas sobre datos de negocio; idempotencia para que un reintento no duplique jugadas ni extracciones (FR-031); importes como `Decimal` en Python y como cadena decimal en la API y en TypeScript | ✅ | ✅ |
| **X. Experiencia visual** | Es el objeto de la feature: sistema visual único (RN-11, [tokens.md](contracts/tokens.md)), contraste medido en ambos temas, 360 px, estados claros de éxito, error, carga y vacío. Solo se agregan los componentes que la spec enumera | ✅ | ✅ |
| **XI. Simplicidad** | ⚠️ La convivencia de dos interfaces y el stack de la Etapa 2 **agregan complejidad** que la spec no exige por sí sola. Se justifica en "Seguimiento de complejidad" y se contiene: dependencias solo cuando una pantalla las usa, Zustand/CORS/DRF descartados, un solo origen, un solo archivo de tokens, un solo catálogo de textos y un solo guion E2E. Las piezas de la Etapa 1 que se descartan (HTMX, Alpine.js, Cally) son las más livianas posibles | ⚠️ justificada | ⚠️ justificada |

**Resultado de la compuerta: APROBADA con complejidad justificada** (Principio XI, ver abajo). No hay violaciones sin justificar.

## Estructura del proyecto (Project Structure)

### Documentación (esta feature)

```text
specs/003-modernizacion-ui-ux/
├── spec.md
├── plan.md              # este archivo
├── research.md          # decisiones R-01 a R-32 y puntos P-01 a P-04
├── data-model.md        # restricción RN-03, valores derivados, estados efímeros, DTO
├── quickstart.md        # 30 escenarios de validación
├── contracts/
│   ├── tokens.md        # colores (con contraste medido), tipografía, espaciado, movimiento
│   ├── componentes.md   # 21 componentes Django ↔ React, estados, teclado, iconos
│   ├── rutas.md         # cambios en rutas de Django y propiedad de cada ruta en Caddy
│   ├── api.md           # API v1: reglas comunes y operaciones por pantalla
│   ├── mensajes.md      # textos reescritos (antes → ahora) y textos nuevos
│   └── formatos.md      # reglas es-AR únicas para ambas interfaces, con casos compartidos
├── checklists/requirements.md
└── tasks.md             # lo genera /speckit-tasks
```

### Código fuente (raíz del repositorio)

```text
# Backend Django (existente; se indica solo lo que se agrega o cambia)
dominio/
├── mensajes.py                 # NUEVO: catálogo único de textos (R-13)
├── periodos.py                 # NUEVO: atajos de período (RN-04)
└── extraccion/etiqueta.py      # NUEVO: EtiquetaEstado y etiqueta_de (RN-01)
quini6/
├── api.py                      # NUEVO: NinjaAPI /api/v1/ (R-16)
├── formulario_pendiente.py     # NUEVO: token firmado y registro de vistas reanudables (R-12)
├── idempotencia.py             # NUEVO: claves en la sesión (R-11)
├── tema.py                     # NUEVO: vista /preferencias/tema/ y procesador de contexto (R-14)
├── templatetags/ui.py          # NUEVO: {% clases %}, {% icono %}, {% msg %}
└── management/commands/
    ├── exportar_contratos.py   # NUEVO: contratos/openapi.json y mensajes.json
    └── preparar_e2e.py         # NUEVO: datos deterministas para Playwright (solo desarrollo)
cuentas/ resultados/ jugadas/ estadisticas/ extracciones/
└── api.py                      # NUEVO en cada app: router de Ninja (delgado: consultas → dominio → servicios)
extracciones/migrations/0003_extraccion_periodo_unico_en_curso.py   # NUEVO (RN-03)
templates/
├── base.html                   # rediseñado: NavBar, AccountMenu, SkipLink, ThemeSelect, avisos, pie
├── ui/                         # NUEVO: fragmentos de componentes (contracts/componentes.md)
│   └── iconos/*.svg            # NUEVO: Lucide versionado con su licencia (R-05)
└── …                           # todas las plantillas existentes, rediseñadas
static/
├── css/app.css                 # GENERADO por Tailwind (deja de versionarse)
├── js/selector-numeros.js      # se conserva (textos y estilos nuevos)
├── js/ui.js                    # NUEVO: componentes Alpine (menú, diálogo, fechas, validación, avisos, tema)
└── vendor/                     # GENERADO: htmx, alpine, cally (no se versiona)
estilos/django.css              # NUEVO: entrada de Tailwind para las plantillas

# Diseño compartido
ui/                             # NUEVO: paquete @quini6/ui
├── tokens.css                  # fuente única de tokens (R-02)
├── base.css                    # capa base común (foco, movimiento reducido, View Transitions)
├── variantes.json              # clases de variantes compartidas (R-04)
├── tokens.test.ts              # contraste (SC-009)
└── marca/                      # logotipo, isotipo, favicon (P-02)

# Interfaz Next.js (Etapa 2)
frontend/                       # NUEVO
├── src/app/                    # mismas rutas que Django, trailingSlash
│   ├── layout.tsx, template.tsx, not-found.tsx, error.tsx
│   ├── administracion/extracciones/(…)/ y @modal/(.)[id]/eliminar/
│   ├── estadisticas/  mis-jugadas/  resultados/  ingresar/  registrarse/
│   └── administracion/concursos/   # pantalla 6 (P-03)
├── src/components/             # contracts/componentes.md (ui/ = shadcn)
├── src/api/                    # esquema.d.ts generado, apiServidor, apiNavegador (R-17)
├── src/lib/                    # esquemas Zod, formato es-AR, sesión
├── src/proxy.ts                # middleware: redirección sin cookie, no-store, cabeceras
└── .storybook/

# Calidad e infraestructura
e2e/                            # NUEVO: Playwright + axe, un guion por historia (R-23)
contratos/                      # NUEVO: openapi.json y mensajes.json exportados y versionados
infra/Caddyfile                 # NUEVO: enrutador (R-20)
compose.yaml                    # NUEVO: PostgreSQL 16 + Caddy (R-21)
package.json, package-lock.json, .nvmrc   # NUEVO: workspaces ui, frontend, e2e
tests/
├── unit/                       # + etiqueta, periodos, mensajes, textos prohibidos
├── integration/                # + fragmentos HTMX, filtro/orden/paginación, RN-03, tema, idempotencia, sesión vencida
└── api/                        # NUEVO: operaciones, matriz de acceso, CSRF, contrato OpenAPI
```

**Decisión de estructura**: se mantiene el monolito Django de [001] y [002] en la raíz (sin moverlo a `backend/`, para no romper importaciones, pruebas ni despliegue) y se agregan como hermanos `ui/` (diseño compartido), `frontend/` (Next.js) y `e2e/`, unidos por npm workspaces (R-22).

## Fases de implementación

Cada fase termina con `ruff check .` limpio y `pytest` en verde; desde la Etapa 1, también con los guiones E2E y axe de lo construido.

### Fase 0 — Cimientos (1 semana)

1. **Entorno paritario** (T001 del pedido): `compose.yaml` (PostgreSQL 16, Caddy), `.env.example` ampliado (`QUINI6_DB_*`, `QUINI6_ORIGEN_PUBLICO`, `QUINI6_RUTAS_NEXT`, `QUINI6_SENTRY_DSN`), CI con `pytest` en SQLite y en PostgreSQL 16 (R-21).
2. **Monorepo de Node**: `package.json` con workspaces, `.nvmrc`, Tailwind CLI, scripts `css`, `css:watch`, `vendor`, `e2e` (R-22).
3. **Tokens** (T004/T004b del pedido): `ui/tokens.css` según [tokens.md](contracts/tokens.md), `ui/base.css`, `ui/variantes.json` y la prueba de contraste (R-02, R-04).
4. **Catálogo de mensajes**: `dominio/mensajes.py` con todos los textos de [001], [002] y [003]; prueba contra [mensajes.md](contracts/mensajes.md); prueba de textos prohibidos (R-13). Se migran a él los textos dispersos y se actualizan las afirmaciones literales de las pruebas existentes.
5. **Base de la API v1 y sesión** (T003 del pedido): Django Ninja con `GET /sesion/`, Problem Details, `exportar_contratos`, prueba de deriva del OpenAPI y matriz de acceso de la API (R-16). Las operaciones de cada pantalla se agregan con su migración (contrato primero por pantalla, R-32).
6. **Extracciones en segundo plano** (T007 del pedido): ya cumplido por [002] R-01; solo se verifica que `consultas.avance` alcance para la API (R-30).
7. **Línea base**: Lighthouse CI y axe sobre las pantallas actuales; `preparar_e2e`; primer guion Playwright (ingresar y consultar resultados) contra Django (R-23, R-24).
8. **Recalcular el cronograma** con el tamaño real medido (pedido §12).

### Etapa 1 — Django mejorado (2–3 semanas)

Orden por prioridad de la spec; cada historia se entrega y prueba por separado.

1. **Base visual y estructura** (HU-05, HU-12, HU-13, RN-11, RN-12): `estilos/django.css` con Tailwind, `base.html` rediseñado (NavBar con sección activa, menú móvil, AccountMenu, SkipLink, ThemeSelect, región de avisos, pie), fragmentos `templates/ui/`, iconos, `/preferencias/tema/`, View Transitions, movimiento reducido, logotipo provisional (P-02).
2. **Lenguaje** (HU-11): todas las plantillas, formularios, servicios y JS toman sus textos del catálogo; "sorteo" en toda la interfaz.
3. **Extracción histórica** (HU-01, HU-02, HU-03, HU-09): `etiqueta_de`, listado con filtro, orden y paginación; StatusBadge; ActionMenu anclado; ConfirmDialog sobre la página de confirmación existente; RN-03 con su migración; avance con HTMX y aviso final; idempotencia al iniciar y eliminar.
4. **Fechas** (HU-04): DateField y DateRangePicker con Cally en extracción, estadísticas, búsqueda de resultados y administración de sorteos; atajos de RN-04.
5. **Validación previa y robustez** (FR-030 a FR-034): validador ligero, estados de trabajo de botones, `gral.sin_conexion` con "Reintentar", idempotencia en el resto de los formularios de creación, formulario pendiente al vencer la sesión.
6. **Ingreso y Crear cuenta** (HU-06): tarjeta centrada, PasswordField, autocompletado, "Ingresando…".
7. **Estadísticas** (HU-07, HU-10): filtros reorganizados, bloque "Consultar un número", gráfico SVG rediseñado, tabla ordenable, aviso informativo.
8. **Estados vacíos y tablas restantes** (HU-08, HU-09): EmptyState en todas las listas y consultas; tablas apiladas en Resultados, Mis jugadas y Administración.
9. **Cierre de la etapa**: guiones E2E de HU-01 a HU-13 (con y sin scripts, 360 px, zoom 200 %, ambos temas) + axe sin críticos ni graves + revisión manual con teclado y NVDA ([quickstart.md](quickstart.md) §4). Criterio de terminado (pedido §6, precisado el 21/11/2026, CHK012): **todas las historias P1 y P2 (HU-01 a HU-11) cumplidas**; HU-12 y HU-13 (P3) se entregan si entran en la etapa, sin bloquear el cierre; auditoría sin incidencias críticas ni graves; 360 px aprobado. Se implementa la spec completa también en Extracción histórica, aunque sea la primera pantalla en migrarse (CHK019, R-01).

### Etapa 2 — Next.js en paralelo (5–7 semanas)

1. **Proyecto y estructura común** (pantalla 0): `frontend/` con Next.js 16, TypeScript estricto, Tailwind 4 importando `ui/tokens.css` y `variantes.json`, shadcn/ui, Lucide, Sonner, Motion; `layout.tsx` (NavBar, AccountMenu, SkipLink, ThemeSelect con la cookie de R-14, pie); páginas 403/404/500; `apiServidor`/`apiNavegador` y tipos generados; `proxy.ts`; ESLint, Prettier, Vitest; Storybook con los componentes de la Etapa 1.
2. **Convivencia** (R-19, R-20, R-31, HU-14): Caddy con las reglas de [rutas.md](contracts/rutas.md) (incluida la vuelta automática a Django y el reparto de los POST con la marca `?_interfaz=django` de los formularios de Django) y `X-Interfaz`; `CSRF_TRUSTED_ORIGINS`, `USE_X_FORWARDED_HOST`; avisos compartidos (`GET /api/v1/avisos/`); página "Volver al formulario" (R-12); **prueba obligatoria T208** (sesión compartida, AC-14.1 y AC-14.2) antes de seguir.
3. **Pantallas en orden** (R-27), cada una con: operaciones de API completas en [api.md](contracts/api.md) y en el OpenAPI, implementación, historias en Storybook, guion E2E de la Etapa 1 pasando contra Next.js en el **entorno de pruebas** (Caddy local con la ruta en `QUINI6_RUTAS_NEXT`), guion de HU-14, axe, 360 px, presupuesto R-24 y reversa probada:
   1. Extracción histórica (mutaciones de API, TanStack Query para el avance, TanStack Table, rutas interceptadas para eliminar, DateRangePicker);
   2. Estadísticas (gráfico SVG como componente de servidor, filtros con React Hook Form + Zod);
   3. Mis jugadas (formularios con Server Actions, selector de números, idempotencia, formulario pendiente con `401`);
   4. Resultados y búsqueda (rendimiento para visitantes);
   5. Ingresar y Crear cuenta (Server Actions que reenvían `Set-Cookie`, `DELETE /sesion/` para salir);
   6. Administración de sorteos (sujeta a P-03; sus operaciones de API se especifican en [api.md](contracts/api.md) antes de empezar).

### Etapa 3 — Conmutación y cierre (2–3 semanas)

1. Por pantalla, en el orden de R-27 (R-28): guion E2E y HU-14 en el entorno de pruebas → patrón en `QUINI6_RUTAS_NEXT` un **martes o jueves de 10 a 12** → **14 días de estabilización** con los umbrales de reversa de R-28 → **aprobación explícita del responsable**, registrada en este plan → retiro de sus plantillas, fragmentos, vistas y rutas HTML de Django. No hay activación parcial por grupo de personas (CHK020).
2. Activar Sentry si se aprobó P-01 (R-25).
3. Al retirar la última pantalla: quitar HTMX, Alpine.js, Cally, `lucide-static`, `estilos/django.css`, `static/vendor/` y la compilación de Tailwind para Django; Django queda con la API, el CSV, el trabajador y los comandos.
4. Auditoría final con lector de pantalla y medición de SC-001 a SC-012 (las pruebas con usuarios las organiza el responsable, spec → Supuestos).
5. **Mantenimiento**: actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec (p. ej. "[003] …"). No incluir entradas por incluir: solo información transversal y relevante para el proyecto que puedan aprovechar futuras features (por ejemplo: stack y estructura `ui/`/`frontend/`/`e2e/`, catálogo único de mensajes, tokens únicos, API v1 con Ninja y Problem Details, mismo origen sin CORS, propiedad de rutas en Caddy, idempotencia y formulario pendiente, guion E2E único; y reemplazar las líneas que esta feature deja sin efecto, como "Sin SPA ni frameworks JS", "SQLite en desarrollo", "dependencias cerradas" y "gráfico SVG generado en el servidor").

## Riesgos y mitigación

| Riesgo | Mitigación |
|--------|------------|
| Doble implementación que diverge en aspecto o comportamiento | Tokens, variantes, iconos y textos compartidos por construcción (R-02 a R-05, R-13); un solo guion E2E por historia para ambas versiones (R-23) |
| Mejora progresiva difícil en React (menús, calendario) | SSR + Server Actions; enlaces y páginas aparte como versión básica; rutas interceptadas para el diálogo (R-18); guiones con scripts desactivados |
| La sesión compartida falla en producción (cabeceras del proxy, CSRF) | Prueba T208 bloqueante al iniciar la Etapa 2; mismo Caddyfile en desarrollo y producción (R-19, R-20) |
| La convivencia se prolonga indefinidamente | Orden y criterio de terminado por pantalla; reversa limitada a 14 días por pantalla; si se detiene tras la Etapa 1, la feature ya está completa (R-01) |
| Next.js cae o se despliega con una ruta conmutada | Caddy vuelve solo a Django mientras existan las plantillas; después, página estática de servicio no disponible (FR-044, R-20) |
| Una persona está a mitad de una tarea cuando se conmuta o se revierte su ruta | Los POST de formularios de Django llevan la marca `?_interfaz=django` y siguen yendo a Django; todos los demás van a Next.js (con o sin scripts), así un formulario abierto antes del cambio se envía igual (R-20, R-32) |
| Deriva entre API y tipos | OpenAPI versionado, prueba de deriva y regeneración de tipos en la CI (R-16, R-17) |
| Cambio masivo de textos rompe pruebas existentes | Catálogo único en la Fase 0; las pruebas pasan a afirmar sobre claves del catálogo o sobre el texto nuevo trazado en [mensajes.md](contracts/mensajes.md) |
| Rendimiento peor que Django para visitantes | Presupuestos por pantalla y Lighthouse CI; componentes de servidor por defecto (también el gráfico); carga diferida de Motion y TanStack Table (R-24) |

## Seguimiento de complejidad (Complexity Tracking)

| Complejidad agregada | Por qué se necesita | Alternativa más simple descartada porque |
|----------------------|---------------------|------------------------------------------|
| Segunda interfaz (Next.js) y convivencia de dos aplicaciones con un enrutador (Etapas 2–3) | **Decisión técnica del responsable** (pedido del 21/11/2026): adoptar un stack de interfaz moderno, con catálogo de componentes, tipado de punta a punta y ecosistema actual, sin reescritura de golpe | Quedarse solo en Django cumple la spec, pero contradice la decisión del responsable; reescribir todo de una vez concentra el riesgo y deja semanas sin entregas (R-01) |
| API v1 con Django Ninja + OpenAPI | Next.js debe consumir solo la API, con tipos generados (pedido §3.2 y §3.3) | Vistas `JsonResponse` a mano no generan contrato; DRF suma más dependencias (R-16) |
| Node, Tailwind y herramientas de construcción en la Etapa 1 | Tokens y clases idénticos en ambas etapas (pedido §6, §10) | CSS propio no se reutiliza en Next.js y duplicaría el sistema visual (R-03) |
| HTMX, Alpine.js y Cally (temporales) | Avance en vivo, menús con teclado, diálogo, calendario y validación previa de la spec sobre plantillas | JS propio para todo es más código a mantener para piezas que se retiran en la Etapa 3 (R-06, R-07) |
| Catálogo único de mensajes y su exportación | SC-007 y mismos textos en ambas interfaces, también en la validación del navegador | Textos literales en cada capa no se pueden auditar ni compartir (R-13) |
| PostgreSQL 16 y Caddy en desarrollo (compose) | Paridad de entornos y probar el enrutador y la sesión compartida igual que en producción | Solo SQLite y sin proxy no detecta los fallos de la convivencia (R-20, R-21) |

## Puntos a confirmar con el responsable

Detalle y recomendación en [research.md](research.md) § "Puntos que requieren confirmación del responsable":

Todos resueltos el 21/11/2026 (detalle en [research.md](research.md)):

- **P-01** — Sentry aprobado, sin datos personales (Etapa 3).
- **P-02** — Isotipo y logotipo tipográficos provisionales aprobados (RN-08); Figma se incorpora cuando exista.
- **P-03** — Administración de sorteos aprobada como pantalla 6.
- **P-04** — Textos ‡ aprobados; solo `form.trabajando_*` (agregado después) queda pendiente.

La spec 003 quedó **aprobada completa** el 21/11/2026 (C1 de `/speckit-analyze`).

Qué pasa si alguno no se aprueba: [research.md](research.md), columna "Si no se aprueba".

## Revisión del checklist de migración (21/11/2026)

[checklists/migracion.md](checklists/migracion.md) detectó 3 conflictos y varios huecos. El responsable decidió: spec completa en Django en todas las pantallas (CHK019); sin activación parcial ni cookie de vista previa (CHK020); gráfico SVG generado en el servidor también en Next.js, sin Recharts (CHK022); "Volver al formulario" para la sesión vencida entre aplicaciones (CHK010); avisos compartidos (CHK009); vuelta automática a Django si Next.js no responde (CHK030); umbrales concretos de reversa y estabilización (CHK017, CHK018); franja fija de conmutación y aprobación explícita para retirar plantillas (CHK016, CHK033); todas las P1 y P2 para cerrar la Etapa 1 (CHK012); aclaración de "no se guarda en el servidor" (CHK023, CHK024); Figma como fuente que manda (CHK040); y agregar HU-14 a la spec (CHK001). Las decisiones técnicas restantes están en R-32 y el contrato nuevo [contracts/formatos.md](contracts/formatos.md).

### Cierre de la Etapa 1 (22/11/2026, T148, CHK039)

Criterio de terminado cumplido: HU-01 a HU-13 implementadas en Django; `ruff` limpio; `pytest` en SQLite con 1380 pruebas en verde; `npm run e2e` en los cinco proyectos (276 en verde, axe sin críticos ni graves, 360 px y texto al 200 % sin desplazamiento horizontal); datos de negocio idénticos a `main` ([verificacion-etapa1.md](verificacion-etapa1.md)); línea base definitiva de R-24 en [linea-base.md](linea-base.md). Pendientes que no bloquean: la corrida de `pytest` contra PostgreSQL 16 queda a cargo del CI (decisión del responsable) y la revisión manual con NVDA de quickstart § 4 (T145).

**Decisión del responsable**: **continuar con las Etapas 2 y 3** (Next.js), empezando por la Fase 18 (estructura común y convivencia detrás del enrutador).

## Registro de conmutaciones (Etapa 3)

Se completa al conmutar cada pantalla (R-28). El retiro de plantillas exige la aprobación del responsable en esta tabla.

| Pantalla | Conmutada el | Reversas (fecha y motivo) | Estabilización cumplida el | Retiro aprobado por el responsable el |
|----------|--------------|---------------------------|----------------------------|---------------------------------------|
| 0 + 1 Estructura común y Extracción histórica | | | | |
| 2 Estadísticas | | | | |
| 3 Mis jugadas | | | | |
| 4 Resultados y búsqueda | | | | |
| 5 Ingresar y Crear cuenta | | | | |
| 6 Administración de sorteos (P-03) | | | | |

## Estado de la Etapa 2 (22/11/2026)

Contratos de las pantallas 1 a 6 aprobados por el responsable el 22/11/2026 (`contracts/api.md`), incluida la operación `POST /formularios/pendiente/` (AC-14.4). Las seis pantallas están implementadas en Next.js con su API, sus pruebas (`tests/api/`, `frontend/**/*.test.tsx`) y sus historias de Storybook, y los guiones E2E corren contra Next.js detrás de Caddy con todas las rutas conmutadas en el entorno de pruebas (`E2E_RUTAS_NEXT`). Decisiones técnicas en research.md § "Ajustes de la implementación de las Fases 19 a 24".

## Próximo paso

Etapa 3 en producción (Fase 25): conmutar las pantallas en el orden de R-27 con la franja de R-28, estabilizar 14 días cada una y retirar sus plantillas con la aprobación del responsable (tabla de arriba). Antes: crear la cuenta de Sentry y configurar el DSN solo en producción (T210), y medir la tasa de 5xx de referencia (T211).
