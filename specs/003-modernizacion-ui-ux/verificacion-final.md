# Verificación final de la feature 003

**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) (§ Criterios de éxito) | **Tareas**: T180, T186, T192, T197, T203, T209, T233 a T236 | **Fecha**: 22/11/2026

Entorno de pruebas: Django 5.2 en el puerto 8001 (base E2E de `preparar_e2e`, SQLite), Next.js 16 compilado (`next build` + `next start`) en el 3000 y Caddy con las seis pantallas en `QUINI6_RUTAS_NEXT` (puerto 8088). Para la reversa, un segundo enrutador con `QUINI6_RUTAS_NEXT` vacía (8087) y Django sin la variable; para la vuelta automática (AC-14.6), uno con Next.js detenido (8089).

## 1. Pruebas automáticas (T235)

| Verificación | Resultado |
|--------------|-----------|
| `ruff check .` | Sin observaciones |
| `pytest` en SQLite | 1739 pasaron, 41 omitidas (rutas con parámetros de la matriz de acceso, que se prueban en el archivo de cada pantalla) |
| `pytest` en PostgreSQL 16 | A cargo del CI por decisión del responsable (22/11/2026, [verificacion-etapa1.md](verificacion-etapa1.md) § 1): trabajo `python` de `.github/workflows/ci.yml` contra `postgres:16` |
| `npm run lint -w frontend` | Sin errores ni advertencias |
| `npm run typecheck -w frontend` | Sin errores |
| `npm run test -w frontend` | 53 pasaron (10 archivos) |
| `npm run test -w ui` | 62 pasaron (contraste de tokens, SC-009) |
| `npm run storybook:build -w frontend` | Compila |
| `npm run e2e` contra **Next.js** (seis pantallas conmutadas, `E2E_CONVIVENCIA=1`) | **310 pasaron**, 0 fallaron, 140 omitidos por proyecto |
| `npm run e2e` en la **reversa** (enrutador y Django sin rutas conmutadas) | **297 pasaron**, 0 fallaron, 153 omitidos por proyecto |

Correcciones hechas para llegar a cero fallos (detalle en [research.md](research.md) § "Ajustes al correr los guiones contra Next.js"):

- **Aplicación**: un aviso podía perderse por solicitudes simultáneas a la sesión (`quini6/sesiones.py`); sin scripts, la sesión vencida en un formulario de Mis jugadas perdía lo escrito (`x-quini6-accion`); SQLite fallaba con `database is locked` ante escrituras simultáneas (`transaction_mode: IMMEDIATE`).
- **Guiones**: espera de la transición entre documentos antes de un clic forzado y antes de cada auditoría de axe; "Ingresando…" observado sin retener una navegación de documento; dos guiones de convivencia que se omiten cuando la Extracción histórica no está conmutada.

## 2. Criterios de éxito (T234)

| Criterio | Medición | Resultado |
|----------|----------|-----------|
| **SC-004** axe 0 críticos y 0 graves | Cada guion E2E audita con axe (wcag2a/aa, 21aa, 22aa) en los proyectos `escritorio`, `movil` (360 px), `oscuro`, `sin-scripts` y `movimiento-reducido`; `hu12-tema` recorre siete pantallas en claro y en oscuro | **Cumple** en Next.js y en Django (corridas del § 1) |
| **SC-005** tareas principales con teclado y lector de pantalla | `zoom-teclado.spec.ts` (solo teclado) en verde | **Parcial**: la revisión con NVDA es manual (T145, T233) |
| **SC-006** 360 px y texto al 200 % sin desplazamiento horizontal | `zoom-teclado.spec.ts` (ocho pantallas) y `sinDesplazamientoHorizontal` en los guiones de cada historia | **Cumple** en ambas interfaces |
| **SC-007** tratamiento y nombres de columna coherentes | Catálogo único (`dominio/mensajes.py` → `contratos/mensajes.json`), `hu11-lenguaje.spec.ts`, `test_textos_prohibidos.py`, `test_botones_con_verbo.py`, `test_mensajes_catalogo.py` | **Cumple** (con la excepción ya registrada de `obs.premio_extra_no_coincide`, verificacion-etapa1 § 4) |
| **SC-009** contraste 4,5:1 texto y 3:1 iconos, bordes y foco | `npm run test -w ui` (62 combinaciones, ambos temas) | **Cumple** |
| **SC-010** formularios que no avanzan con datos inválidos, mensaje por campo y foco en el primero | `test_003_formularios_validacion.py`, `hu04-fechas`, `hu06-ingreso`, `robustez`, `admin-sorteos` | **Cumple** en ambas interfaces |
| **SC-011** mismos datos de negocio y CSV idéntico | Comparación contra `main` (verificacion-etapa1 § 3) y pruebas de paridad de la API (`tests/api/`, mismos casos que las vistas HTML) | **Cumple** |
| **SC-012** recorrido de AC-14.1 a AC-14.5 sin reingresar, sin avisos perdidos y con reversa | `sesion-compartida.spec.ts` y `hu14-convivencia.spec.ts` con las seis pantallas en Next.js, la vuelta automática (AC-14.6) y la corrida completa en la reversa | **Cumple en el entorno de pruebas**; en producción se verifica al conmutar cada pantalla (T212 a T229) |
| SC-001, SC-002, SC-003, SC-008 | Pruebas con usuarios | **Pendientes**: las organiza el responsable (spec, Supuestos) |

Rendimiento (R-24) de las pantallas en Next.js: [linea-base.md](linea-base.md) § "Etapa 2". LCP, CLS y TBT mejoran frente a Django en todas las pantallas; JavaScript de las privadas ≤ 200 kB; públicas sobre el piso de Next.js, según la desviación aprobada.

## 3. Pendiente (no se puede hacer desde el entorno de pruebas)

- **T145 y T233**: revisión manual con NVDA y solo teclado (quickstart § 4 y todas las pantallas en ambos temas y anchos).
- **T210**: el código de Sentry está listo (`quini6/observabilidad.py`, `lib/observabilidad.ts`, activo solo con `QUINI6_SENTRY_DSN`); falta crear la cuenta y el DSN con el responsable y configurarlo en producción.
- **T211 a T230**: medición de 5xx previa, conmutación en producción, 14 días de estabilización por pantalla y retiro de plantillas con aprobación del responsable.
- **Formularios de Administración sin scripts con la sesión vencida** en Next.js: no conservan lo escrito (Mis jugadas sí). Ver research.md.
