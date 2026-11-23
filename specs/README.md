# Estado del producto — QUINI_6

Cada feature tiene su carpeta con `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` y `tasks.md` (flujo SDD con Spec Kit). Las reglas de producto están en `.specify/memory/constitution.md`; las decisiones técnicas vigentes, resumidas en `CLAUDE.md`.

| Feature | Qué entrega | Estado |
|---------|-------------|--------|
| [001 — MVP](001-quini6-mvp/spec.md) | Consulta pública de resultados, premios y estadísticas; cuentas; jugadas comparadas con los resultados oficiales; administración de sorteos con versiones y correcciones | **Entregada** (en `main`) |
| [002 — Extracción histórica y CSV](002-extraccion-historica-csv/spec.md) | Extracción de sorteos pasados desde tres fuentes, consolidación con estado explícito por dato y exportación CSV (contrato v3.0) | **Entregada** (en `main`, merge `ff87063`) |
| [003 — Modernización visual y de experiencia de uso](003-modernizacion-ui-ux/spec.md) | Etapa 1: HU-01 a HU-13 en Django. Etapa 2: las seis pantallas en Next.js detrás de Caddy, con la sesión, los avisos y los textos de Django (HU-14). Etapa 3: conmutación en producción, estabilización y retiro de plantillas | **En curso** (rama `003-modernizacion-ui-ux`): Etapas 1 y 2 implementadas; Etapa 3 pendiente (producción) |

## 003 en detalle (22/11/2026)

- **Etapa 1 (Django mejorado)**: terminada y aprobada (T148); falta la revisión manual con NVDA de quickstart § 4 (T145), a cargo del responsable.
- **Etapa 2 (Next.js en paralelo)**: estructura común, convivencia y las pantallas 1 a 6 implementadas con sus contratos de API aprobados (`contracts/api.md`), pruebas de API, componentes con historias de Storybook y pruebas, y los guiones E2E en verde contra Next.js en el entorno de pruebas (310) y en la reversa a Django (297); presupuesto de rendimiento con la desviación aprobada para las pantallas públicas. Detalle en `003-modernizacion-ui-ux/verificacion-final.md` y `linea-base.md` § Etapa 2.
- **Etapa 3 (conmutación)**: pendiente; se hace en producción, pantalla por pantalla (R-28): conmutar un martes o jueves de 10 a 12, estabilizar 14 días y retirar las plantillas con la aprobación del responsable (`plan.md` § Registro de conmutaciones). Sentry queda listo en el código (P-01) y se activa con el DSN de producción.
- **Pendiente del responsable**: auditorías manuales con NVDA (T145, T233), la cuenta y el DSN de Sentry (T210), la Etapa 3 en producción (T211 a T230) y las pruebas con usuarios de SC-001 a SC-003 y SC-008.

## Pendientes no bloqueantes (registrados el 23/11/2026)

Tareas sin marcar en `tasks.md` que no impiden usar lo entregado. La aplicación se probó de forma manual y se considera correcta; estas verificaciones quedan para una etapa posterior.

- **001 — MVP**: T093 (`pytest` también contra PostgreSQL 16, paridad de motores) y T094 (escenarios A a H del quickstart, registrados en `checklists/validacion-quickstart.md`).
- **002 — Extracción histórica**: T087 (pantallas a 360 px y lector de contraste), T088 (`ruff` y `pytest` completo en verde), T089 (escenarios A a H con el servidor de fuentes de prueba), T090 (verificación con las fuentes reales: SC-003, SC-006, SC-007, SC-008, NFR-002/003), T091 (completar en `CLAUDE.md` las decisiones de [002]) y T100 (sorteo 3232 y caso «410.1156,25» con fuentes reales).
- **003 — Modernización**: T145 y T233 (revisión con NVDA y teclado), T210 (cuenta y DSN de Sentry, a cargo del responsable).
- **Checklists de calidad** en `specs/*/checklists/`: sin marcar. Son revisiones de redacción de la spec, no tareas de implementación.
