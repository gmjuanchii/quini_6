---

description: "Lista de tareas de la feature 003: Modernización visual y de experiencia de uso"
---

# Tareas (Tasks): Modernización visual y de experiencia de uso

**Entrada**: documentos de diseño de `specs/003-modernizacion-ui-ux/`

**Prerrequisitos**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md), [checklists/migracion.md](checklists/migracion.md)

**Pruebas**: se incluyen. Las exigen la Constitución (XI: pruebas automatizadas de reglas y recorridos principales), `CLAUDE.md` (`ruff` y `pytest` en verde) y el plan ([003] R-23: un guion Playwright por historia, que corre igual contra Django y contra Next.js). Dentro de cada historia, las pruebas se escriben primero y deben fallar antes de implementar.

**Organización**:

- **Fase 1 y Fase 2** = Fase 0 del plan (cimientos).
- **Fases 3 a 15** = Etapa 1 del plan (Django mejorado), una fase por historia, en orden de prioridad: P1 (US1 a US5), P2 (US6 a US11), P3 (US12, US13).
- **Fase 16** = robustez transversal (FR-030 a FR-034) y **Fase 17** = cierre de la Etapa 1.
- **Fases 18 a 24** = Etapa 2 (Next.js), una fase por pantalla de R-27. **Fase 25** = Etapa 3 (conmutación). Todas llevan `[US14]`: implementan FR-039 a FR-044 (paridad y convivencia).
- **Fase 26** = cierre final.

**Desviación respecto del plan**: el plan § Fase 0 paso 5 ubicaba la API de lectura de Resultados y Estadísticas en la Fase 0. R-32 (CHK003) decidió después que "contrato primero" se aplica por pantalla; por eso aquí la Fase 2 solo crea la base de la API y `GET /sesion/`, y cada operación se agrega en la fase de su pantalla (18 a 24).

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes).
- **[USn]**: historia de usuario de [spec.md](spec.md): US1 = HU-01 … US14 = HU-14.
- **"(requiere T001)"**: la tarea usa textos de [contracts/mensajes.md](contracts/mensajes.md) o depende de P-01 a P-04 de [research.md](research.md), que deben estar confirmados antes (Const. I). T001 quedó hecha el 21/11/2026, así que esas tareas ya no están bloqueadas (salvo T138, por `form.trabajando_*`).

## Convenciones para todas las tareas

- Código, nombres y textos en español de Argentina. **Todo texto visible sale de `dominio/mensajes.py`** por su clave de [contracts/mensajes.md](contracts/mensajes.md): en plantillas con `{% msg "clave" %}`, en Python con `mensaje("clave", **valores)`, en Next.js con `msg("clave", valores)`. Nunca se escribe un texto visible literal fuera del catálogo.
- Docstrings y pruebas citan los IDs con prefijo: `[003] AC-2.3`, `[003] R-11`, `[002] RN-44`, `[001] AC-3.5`.
- `dominio/` no importa Django; errores como valores; importes `Decimal` (en la API, cadena decimal; en TypeScript, `string`, nunca `number`).
- Clases visuales solo con tokens semánticos de [contracts/tokens.md](contracts/tokens.md) y variantes de `ui/variantes.json` (filtro `{% clases %}` en Django, `cva` en React). Iconos solo de la lista de [contracts/componentes.md](contracts/componentes.md) § 2, con `aria-hidden="true"` y siempre junto a texto.
- Cada componente sigue su fila de [contracts/componentes.md](contracts/componentes.md) (estados, teclado, nombre accesible) y su versión sin scripts de § 4.
- Mejora progresiva: toda página funciona sin scripts (NFR-007). Ningún permiso se decide en el navegador ni en Next.js; Django verifica en cada GET, POST y operación de API (Const. IV).
- Guiones E2E con `getByRole`/`getByLabel` y textos del catálogo, **nunca** con clases CSS; cada guion corre axe (0 críticos y 0 graves) y comprueba que no haya desplazamiento horizontal a 360 px.
- Al terminar cada tarea: `ruff check .` limpio y `pytest` en verde; desde la Fase 18, también `npm run lint -w frontend`, `npm run typecheck -w frontend` y `npm run test -w frontend`.

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: herramientas de Node, entorno paritario y puntos pendientes de confirmación.

- [X] T001 Consultar al responsable P-01 (Sentry), P-02 (Figma, logotipo, isotipo y favicon), P-03 (Administración de sorteos como pantalla 6) y P-04 (textos ‡ de `specs/003-modernizacion-ui-ux/contracts/mensajes.md`), y la aprobación de la spec 003, sin darlos por aprobados; registrar cada respuesta en `research.md` § "Puntos que requieren confirmación" y en `spec.md`. **Hecho el 21/11/2026**: spec aprobada completa; P-01 Sentry sin datos personales; P-02 isotipo tipográfico provisional; P-03 pantalla 6 sí; P-04 textos aprobados (pasaron a †). Queda pendiente solo `form.trabajando_*` (ver T138) (Const. I)
- [X] T002 [P] Agregar `"django-ninja==1.*"` a `dependencies` y `"quini6.management"`, `"quini6.management.commands"`, `"quini6.templatetags"` a `[tool.setuptools] packages` en `pyproject.toml`; crear `quini6/management/__init__.py` y `quini6/management/commands/__init__.py` vacíos ([003] R-16, R-26)
- [X] T003 [P] Crear `package.json` en la raíz con `"private": true`, `"workspaces": ["ui", "e2e"]` (se agrega `"frontend"` en T155), `"engines": {"node": ">=24"}`, `devDependencies` `tailwindcss@4`, `@tailwindcss/cli@4`, `htmx.org@2`, `alpinejs@3`, `@alpinejs/anchor@3`, `@alpinejs/focus@3`, `cally`, `lucide-static`, y scripts `css` (`tailwindcss -i estilos/django.css -o static/css/app.css --minify`), `css:watch` (igual con `--watch`), `vendor` (`node scripts/vendor.mjs`), `iconos` (`node scripts/iconos.mjs`), `e2e` (`npm run test -w e2e`), `lhci` (`lhci autorun`); crear `.nvmrc` con `24` ([003] R-22)
- [X] T004 [P] Agregar a `.gitignore`: `node_modules/`, `static/css/app.css`, `static/vendor/`, `e2e/test-results/`, `e2e/playwright-report/`, `e2e/.credenciales.json`, `frontend/.next/`, `frontend/storybook-static/`, `.lighthouseci/`; mover el contenido actual de `static/css/app.css` a `estilos/legado.css` (se importa en T019 y se elimina en T141) y quitar `static/css/app.css` del índice con `git rm --cached static/css/app.css` ([003] R-03)
- [X] T005 [P] Crear `scripts/vendor.mjs` que copie a `static/vendor/`: `node_modules/htmx.org/dist/htmx.min.js`, `node_modules/alpinejs/dist/cdn.min.js` → `alpine.min.js`, `node_modules/@alpinejs/anchor/dist/cdn.min.js` → `alpine-anchor.min.js`, `node_modules/@alpinejs/focus/dist/cdn.min.js` → `alpine-focus.min.js`, y el módulo de `cally` → `cally.js` ([003] R-06, R-07)
- [X] T006 [P] Crear `compose.yaml` con el servicio `db` (`postgres:16`, volumen `quini6-pg`, variables `POSTGRES_DB`/`POSTGRES_USER`/`POSTGRES_PASSWORD` tomadas de `QUINI6_DB_*`, puerto `5432`) y el servicio `proxy` (`caddy:2`, monta `infra/Caddyfile` en `/etc/caddy/Caddyfile` e `infra/no-disponible.html`, puerto `8080:8080`, `extra_hosts: host.docker.internal:host-gateway`, variables `QUINI6_DJANGO_UPSTREAM`, `QUINI6_NEXT_UPSTREAM`, `QUINI6_RUTAS_NEXT`) ([003] R-20, R-21)
- [X] T007 [P] Crear `infra/Caddyfile` versión Etapa 1: sitio `:8080`, todo a `reverse_proxy {$QUINI6_DJANGO_UPSTREAM:host.docker.internal:8000}` con `header X-Interfaz django`; dejar comentado el esquema de reglas 1 a 5 de `specs/003-modernizacion-ui-ux/contracts/rutas.md` § 3 (se activa en T153) ([003] R-20)
- [X] T008 [P] Ampliar `.env.example` con `QUINI6_DB_NAME=quini6`, `QUINI6_DB_USER=quini6`, `QUINI6_DB_PASSWORD=` (vacía, a completar), `QUINI6_DB_HOST=127.0.0.1`, `QUINI6_ORIGEN_PUBLICO=http://localhost:8080`, `QUINI6_RUTAS_NEXT=` (vacía), `QUINI6_RUTAS_NEXT_SIN_RESPALDO=` (vacía; pantallas cuyas plantillas ya se retiraron), `QUINI6_DJANGO_UPSTREAM=host.docker.internal:8000`, `QUINI6_NEXT_UPSTREAM=host.docker.internal:3000`, `QUINI6_API_INTERNA=http://127.0.0.1:8000`, `QUINI6_SENTRY_DSN=` (vacía = apagado), `QUINI6_E2E=` (vacía), cada una con su comentario ([003] R-19 a R-21, R-25)
- [X] T009 Leer en `quini6/settings.py`: `CSRF_TRUSTED_ORIGINS` = lista de `QUINI6_ORIGEN_PUBLICO` (vacía si no está), `USE_X_FORWARDED_HOST = True`, `QUINI6_RUTAS_NEXT` y `QUINI6_RUTAS_NEXT_SIN_RESPALDO` como listas de patrones (separados por espacio) y `QUINI6_E2E` como booleano ([003] R-12, R-19)
- [X] T010 [P] Crear `.github/workflows/ci.yml` con los trabajos: `python` (matriz SQLite y servicio `postgres:16`; `pip install -e ".[dev,prod]"`, `ruff check .`, `pytest`, `python manage.py exportar_contratos --verificar`), `node` (`npm ci`, `npm run css`, `npm run test -w ui`) y `e2e` (levanta Django con `preparar_e2e` y ejecuta `npm run e2e`) ([003] R-21, R-23)

---

## Fase 2: Base (prerrequisitos que bloquean todas las historias)

**Propósito**: tokens, variantes, iconos, catálogo de mensajes, filtros de plantilla, idempotencia, base de la API, contratos exportados, datos y arnés E2E, línea base.

**⚠️ CRÍTICO**: ninguna historia empieza antes de terminar esta fase.

### Pruebas de la base

- [X] T011 [P] Escribir `tests/unit/test_mensajes_catalogo.py`: lee las tablas de `specs/003-modernizacion-ui-ux/contracts/mensajes.md` (§ 2, § 3, § 4) y de los catálogos de [001] y [002] para las claves que [003] no reescribe, y exige que `dominio.mensajes.MENSAJES` tenga exactamente esas claves con esos textos (sin las marcas ✓/‡ ni las notas entre paréntesis); `mensaje("jugada.faltan", n=2)` → `"Faltan 2 números"`; clave inexistente → `KeyError` ([003] R-13)
- [X] T012 [P] Escribir `tests/unit/test_templatetags_ui.py`: `{% msg "nav.menu" %}` → `Menú`; `{% msg "pag.pagina" n=1 m=15 %}` → `Página 1 de 15`; `{% clases "boton" variante="destructivo" %}` devuelve la base + la variante de `ui/variantes.json`; variante inexistente → error en `DEBUG`; `{% icono "circle-check" %}` incluye el SVG con `aria-hidden="true"` y `focusable="false"`; icono fuera de la lista → error ([003] R-04, R-05)
- [X] T013 [P] Escribir `tests/integration/test_idempotencia.py` con una vista de prueba decorada con `con_idempotencia("prueba.crear")`: dos POST con la misma `clave_idempotencia` ejecutan una sola vez y devuelven el mismo 303; la misma clave con otra acción → 400; POST sin clave se procesa normalmente; la sesión guarda como máximo 50 claves con `clave`, `accion`, `resultado`, `usada_en` ([003] R-11, data-model § 3)
- [X] T014 [P] Escribir `tests/api/__init__.py`, `tests/api/conftest.py` (clientes `visitante`, `usuario`, `otro_usuario`, `administrador` reutilizando `tests/fabricas.py`, y un ayudante que obtiene `csrftoken` con `GET /api/v1/sesion/`) y `tests/api/test_sesion.py`: `GET /api/v1/sesion/` sin sesión → `{"correo": null}` y fija `csrftoken`; con sesión → `correo`, `es_administrador`, `vence_en`; respuesta con `Cache-Control: no-store` ([003] contracts/api.md § 2)
- [X] T015 [P] Escribir `tests/api/test_problemas.py`: un error de validación responde `422` `application/problem+json` con `type`, `title`, `status`, `detail` y `errores: [{campo, codigo, mensaje}]`; mutación sin `X-CSRFToken` → `403`; `401`, `403` y `404` con el mismo formato ([003] R-16)
- [X] T016 [P] Escribir `tests/api/test_contratos_exportados.py`: `exportar_contratos --verificar` falla si `contratos/openapi.json`, `contratos/mensajes.json` o `contratos/formatos-casos.json` difieren de lo generado ([003] R-13, R-16, contracts/formatos.md)
- [X] T017 [P] Escribir `tests/api/test_matriz_acceso_api.py`: recorre todas las operaciones registradas en `quini6.api.api` y compara cada una con una tabla `NIVEL_ESPERADO` (P/U/A) definida en la prueba; una operación sin fila en la tabla hace fallar la prueba; verifica 401/403/404 por perfil como en `tests/integration/test_matriz_acceso.py` de [001] ([003] contracts/api.md § 4)

### Implementación de la base

- [X] T018 [P] Crear el paquete `ui/` (`ui/package.json` con nombre `@quini6/ui`, `devDependencies` `vitest`), `ui/tokens.css` con **todos** los valores de `specs/003-modernizacion-ui-ux/contracts/tokens.md` como `@theme` de Tailwind 4 y variables semánticas (`--color-background`, `--color-surface`, `--color-foreground`, `--color-muted-foreground`, `--color-primary`, `--color-primary-foreground`, `--color-primary-hover`, `--color-accent`, `--color-accent-text`, `--color-accent-icon`, `--color-success`, `--color-success-text`, `--color-success-icon`, `--color-danger`, `--color-danger-text`, `--color-danger-icon`, `--color-destructive`, `--color-destructive-foreground`, `--color-warning-text`, `--color-warning-icon`, `--color-border`, `--color-border-input`, `--color-ring`, fondos y textos de las variantes `success`/`warning`/`danger`/`info`/`neutral`, radios, sombras, alturas, duraciones), redefinidas en `:root[data-theme="oscuro"]` y en `@media (prefers-color-scheme: dark) { :root:not([data-theme="claro"]) {…} }`; y `ui/base.css` (anillo de foco de 2 px + 2 px de separación con `--color-ring`, `@view-transition { navigation: auto; }`, `prefers-reduced-motion: reduce` → duraciones 0 y sin desplazamientos, `tabular-nums` en `.cifras`, estilos de "Saltar al contenido") ([003] R-02, R-14, R-15, R-29)
- [X] T019 [P] Crear `ui/variantes.json` con `boton` (base: altura 44 px, radio de control, foco, deshabilitado, `aria-busy`; variantes `principal`, `secundario`, `destructivo`, `fantasma`, `enlace`; tamaños `md`, `sm`), `insignia` (`info`, `success`, `warning`, `danger`, `neutral`), `aviso` (`info`, `success`, `warning`, `danger`), `toast` (`success`, `info`, `warning`, `error`) y `vacio` (`sin_datos`, `sin_resultados`); crear `estilos/django.css` con `@import "tailwindcss"; @import "../ui/tokens.css"; @import "../ui/base.css"; @import "./legado.css" layer(legado); @source "../templates"; @source "../ui/variantes.json"; @source "../static/js";` ([003] R-03, R-04)
- [X] T020 Escribir `ui/tokens.test.ts` (Vitest) que lee `ui/tokens.css`, calcula el contraste WCAG de cada par de las tablas de `contracts/tokens.md` en ambos temas y exige ≥ 4,5:1 para texto y ≥ 3:1 para iconos, bordes de campos y foco; agregar el script `test` en `ui/package.json` ([003] SC-009, T004b del pedido)
- [X] T021 [P] Crear `scripts/iconos.mjs` que copia de `node_modules/lucide-static/icons/` a `templates/ui/iconos/` exactamente los iconos de `contracts/componentes.md` § 2 (`loader-circle`, `circle-check`, `triangle-alert`, `circle-dashed`, `circle-x`, `info`, `menu`, `x`, `circle-user-round`, `sun`, `moon`, `monitor`, `ticket`, `list-ordered`, `calendar`, `ellipsis-vertical`, `trash-2`, `download`, `arrow-right`, `arrow-left`, `arrow-up`, `arrow-down`, `arrow-up-down`, `eye`, `eye-off`, `wifi-off`, `rotate-cw`, `chart-column`, `filter-x`, `plus`), quitando `width`/`height` fijos; ejecutarlo y **versionar** los SVG junto con `templates/ui/iconos/LICENCIA-lucide.txt` (ISC) ([003] R-05)
- [X] T022 Crear `dominio/mensajes.py` (sin Django) con `MENSAJES: dict[str, str]` que reúne todas las claves de [001], [002] y [003] según T011 —los textos reescritos de § 2 y § 3 y los nuevos de § 4 de `contracts/mensajes.md`— y `mensaje(clave: str, **valores) -> str` con `str.format_map`; la existencia del catálogo no cambia todavía ningún texto visible (eso lo hace US11) (requiere T001 para los ‡) ([003] R-13)
- [X] T023 Crear `quini6/templatetags/ui.py` con `{% msg "clave" var=valor %}` (simple_tag sobre `dominio.mensajes.mensaje`), `{% clases "componente" variante="…" tamano="…" extra="…" %}` (lee `settings.BASE_DIR / "ui" / "variantes.json"` una vez y lo guarda en memoria) y `{% icono "nombre" clase="size-5" %}` (incluye `ui/iconos/<nombre>.svg` agregando `class`, `aria-hidden="true"`, `focusable="false"`; nombre fuera de la lista → `TemplateSyntaxError`) hasta pasar T012 ([003] R-04, R-05)
- [X] T024 [P] Crear los fragmentos compartidos `templates/ui/_boton.html` (Button: `<button>` o `<a>` según `href`, icono opcional a la izquierda, texto obligatorio, `data-texto-trabajando` opcional), `templates/ui/_aviso.html` (Callout: icono + texto, variante, `rol` opcional `status`/`alert`), `templates/ui/_esqueleto.html` (Skeleton: `aria-hidden="true"`, alto reservado por parámetro) y ampliar `templates/_campo.html` (Field: `<label for>`, ayuda en `id="<campo>_ayuda"`, error en `id="<campo>_error"` con icono `circle-x`, `aria-describedby` con ambos, `aria-invalid` si hay error), según `contracts/componentes.md` ([003] FR-033, RN-11)
- [X] T025 Ajustar `templates/base.html`: cargar `{% static 'css/app.css' %}` (generado), los scripts `defer` de `static/vendor/` (`htmx.min.js`, `alpine-anchor.min.js`, `alpine-focus.min.js`, `alpine.min.js`) y `static/js/ui.js`, y `<script type="module" src="{% static 'vendor/cally.js' %}">`; mantener el encabezado actual (se rediseña en US5) y el indicador "Cargando…" existente ([003] R-06)
- [X] T026 Crear `static/js/ui.js` con el registro de componentes Alpine (`document.addEventListener("alpine:init", …)`), el agregado de `X-CSRFToken` (leído de la cookie `csrftoken`) a cada pedido HTMX en `htmx:configRequest`, y la configuración HTMX `htmx.config.defaultSwapStyle = "outerHTML"`, `htmx.config.historyCacheSize = 0` (páginas privadas sin caché, NFR-008) ([003] R-06)
- [X] T027 Crear `quini6/idempotencia.py`: `nueva_clave() -> str` (UUID v4), `{% campo_idempotencia %}` en `quini6/templatetags/ui.py` (campo oculto `clave_idempotencia`), y el decorador `con_idempotencia(accion: str)` para vistas POST que lee `request.POST["clave_idempotencia"]` o la cabecera `Idempotency-Key`, guarda en `request.session["claves_idempotencia"]` las últimas 50 entradas `{clave, accion, resultado, usada_en}` y ante una clave repetida devuelve el mismo resultado (303 a `resultado`) sin ejecutar la vista, hasta pasar T013 ([003] R-11, FR-031)
- [X] T028 Crear `quini6/api.py` con `NinjaAPI(title="QUINI_6 API", version="1", csrf=True, urls_namespace="api")`, manejadores que convierten errores de validación, `Http404`, permisos y conflictos a Problem Details (`application/problem+json`, extensión `errores`), autenticación por sesión (`django_auth`) y el decorador `nivel("P"|"U"|"A")` que aplica las mismas reglas que `cuentas/decoradores.py` y agrega `Cache-Control: no-store` en U y A; montar `path("api/v1/", api.urls)` en `quini6/urls.py` ([003] R-16)
- [X] T029 Crear `cuentas/api.py` con el router de `GET /sesion/` (nivel P, `ensure_csrf_cookie`, DTO `Sesion` de `data-model.md` § 5) y registrarlo en `quini6/api.py`, hasta pasar T014, T015 y T017 ([003] contracts/api.md § 2)
- [X] T030 Crear `quini6/management/commands/exportar_contratos.py`: escribe `contratos/openapi.json` (`api.get_openapi_schema()`, claves ordenadas, indentación 2), `contratos/mensajes.json` (`MENSAJES`) y `contratos/formatos-casos.json` (casos de `specs/003-modernizacion-ui-ux/contracts/formatos.md` § "Casos mínimos"); con `--verificar` compara sin escribir y sale con código 1 si difieren; ejecutar y versionar `contratos/` hasta pasar T016 ([003] R-13, R-16)
- [X] T031 Escribir `tests/unit/test_formatos_contrato.py`: aplica los filtros `fecha_ar`, `fecha_hora_ar`, `pesos`, `porcentaje_ar` y `dos_digitos` de `quini6/templatetags/formato_ar.py` a cada caso de `contratos/formatos-casos.json` y exige la salida esperada; para "importe negativo" registra la salida real actual en el JSON (sin cambiar el filtro) ([003] contracts/formatos.md)
- [X] T032 Crear `quini6/management/commands/preparar_e2e.py`: se niega (código 1, mensaje claro) salvo con `DEBUG` y `QUINI6_E2E`; vacía y crea datos deterministas usando los servicios de cada app (no `tests/`): cuentas `admin@e2e.local` (administrador), `usuaria@e2e.local` (con jugadas), `sinjugadas@e2e.local`, con contraseñas aleatorias que imprime y escribe en `e2e/.credenciales.json`; sorteos publicados de 2025 y 2026 con todas sus modalidades; jugadas de `usuaria@e2e.local`; 25 extracciones terminadas que cubren las cinco etiquetas de RN-01 (incluida una `CON_ADVERTENCIAS` con un sorteo `NO_RECUPERADO` y otra sin ninguno) y una `EN_CURSO` de otra cuenta administradora ([003] R-23)
- [X] T033 [P] Crear el paquete `e2e/`: `e2e/package.json` (`@playwright/test`, `@axe-core/playwright`, script `test`), `e2e/playwright.config.ts` (`baseURL` de `E2E_BASE_URL`, por defecto `http://127.0.0.1:8000`; proyectos `escritorio` 1280×800, `movil` 360×740, `sin-scripts` con `javaScriptEnabled: false`, `oscuro` con `colorScheme: "dark"`, `movimiento-reducido` con `reducedMotion: "reduce"`), `e2e/apoyo/sesion.ts` (`ingresarComo(page, "admin" | "usuaria" | "sinjugadas")` con `e2e/.credenciales.json`), `e2e/apoyo/accesibilidad.ts` (`sinIncidenciasGraves(page)` con axe, falla ante `critical` o `serious`), `e2e/apoyo/desborde.ts` (`sinDesplazamientoHorizontal(page)`: `scrollWidth <= clientWidth`), `e2e/apoyo/mensajes.ts` (`msg(clave, valores)` desde `contratos/mensajes.json`) ([003] R-23)
- [X] T034 [P] Escribir `e2e/recorridos/linea-base.spec.ts`: ingresar como usuaria, consultar Resultados, Estadísticas y Mis jugadas; sin aserciones de diseño (sirve para validar el arnés contra el Django actual) ([003] plan § Fase 0)
- [X] T035 [P] Crear `lighthouserc.json` (perfil móvil por defecto, 5 corridas, URLs `/resultados/`, `/estadisticas/`, `/mis-jugadas/`, `/administracion/extracciones/` con sesión vía script de `puppeteerScript` que usa `e2e/.credenciales.json`); ejecutar sobre el Django actual y registrar LCP, CLS, INP y JavaScript inicial en `specs/003-modernizacion-ui-ux/linea-base.md` como referencia histórica ([003] R-24)
- [X] T036 Recalcular el cronograma del plan con el tamaño real medido (plantillas, textos a reescribir, resultados de T034 y T035) y actualizar `specs/003-modernizacion-ui-ux/plan.md` § Contexto técnico, fila "Cronograma orientativo" ([003] plan § Fase 0 paso 8)

**Punto de control**: base lista; las historias pueden empezar.

---

## Fase 3: Historia de usuario 1 — Distinguir el estado de cada extracción (Prioridad: P1) 🎯 MVP

**Objetivo**: cada extracción muestra una etiqueta con texto, icono y color (RN-01), con su explicación (RN-02), se destacan las que requieren revisión y se puede filtrar por estado.

**Prueba independiente**: con `preparar_e2e`, un administrador abre "Extracción histórica", identifica las extracciones con advertencias o con error y filtra por "Con advertencias" ([quickstart.md](quickstart.md) #1 y #2).

### Pruebas de la historia 1

- [X] T037 [P] [US1] Escribir `tests/unit/extraccion/test_etiqueta.py`: `etiqueta_de` para los cinco casos de `data-model.md` § 2 (incluida la precedencia de `CON_ERROR` sobre `CON_ADVERTENCIAS` y el caso `(FINALIZADA, True)` → `CON_ERROR`), los `slug` (`en-curso`, `finalizada`, `con-advertencias`, `sin-sorteos`, `con-error`), la clave de `texto` y de `explicacion` de cada valor, la variante e icono de cada uno y el orden `EN_CURSO < CON_ERROR < CON_ADVERTENCIAS < SIN_SORTEOS < FINALIZADA` ([003] RN-01, RN-02)
- [X] T038 [P] [US1] Escribir `tests/integration/test_003_us1_estados.py`: con extracciones en los cinco estados, el listado muestra en cada fila la etiqueta con su texto y su icono y la explicación asociada por `aria-describedby`; las filas "Con advertencias" y "Con error" llevan la marca de revisión; `?estado=con-advertencias` muestra solo esas y "Filtro aplicado: Con advertencias"; `?estado=desconocido` muestra todas con "Todos los estados"; el detalle muestra la misma etiqueta y debajo el resultado de [002] RN-33 ([003] AC-1.1 a AC-1.5)

### Implementación de la historia 1

- [X] T039 [US1] Crear `dominio/extraccion/etiqueta.py` (sin Django) con el `Enum` `EtiquetaEstado` (`EN_CURSO`, `FINALIZADA`, `CON_ADVERTENCIAS`, `SIN_SORTEOS`, `CON_ERROR`) y sus propiedades `slug`, `clave_texto` (`etiqueta.<valor>`), `clave_explicacion` (`etiqueta.<valor>.explicacion`), `variante` (`info`, `success`, `warning`, `neutral`, `danger`), `icono` (`loader-circle`, `circle-check`, `triangle-alert`, `circle-dashed`, `circle-x`) y `orden`; `etiqueta_de(estado: EstadoExtraccion, tiene_no_recuperados: bool) -> EtiquetaEstado` y `desde_slug(slug: str) -> EtiquetaEstado | None`, hasta pasar T037 ([003] RN-01, data-model § 2)
- [X] T040 [US1] Modificar `extracciones/consultas.py :: listado_extracciones(filtro: EtiquetaEstado | None = None)` para anotar `tiene_no_recuperados = Exists(SorteoExtraido.objects.filter(extraccion=OuterRef("pk"), estado="NO_RECUPERADO"))`, filtrar por etiqueta con expresiones del ORM (sin consultar ningún `JSONField`, [002] R-08) y devolver cada fila con su `etiqueta`; agregar `etiqueta` a `datos_pagina` ([003] R-08)
- [X] T041 [P] [US1] Crear `templates/ui/_insignia_estado.html` (StatusBadge): `{% clases "insignia" variante=etiqueta.variante %}`, icono de la etiqueta (`loader-circle` con `motion-safe:animate-spin`), texto `{% msg etiqueta.clave_texto %}`, elemento enfocable (`tabindex="0"`) con `aria-describedby` hacia un *tooltip* visible al cursor y al foco (`group-hover`/`group-focus-within`) con `{% msg etiqueta.clave_explicacion %}` ([003] FR-001, FR-002, contracts/componentes.md)
- [X] T042 [US1] Modificar `extracciones/views.py :: inicio` para leer `?estado=` con `desde_slug` (inválido → sin filtro) y pasar `filtro` al contexto; modificar `templates/extracciones/inicio.html`: columna "Estado" con `_insignia_estado.html`, marca de revisión en las filas `CON_ADVERTENCIAS`/`CON_ERROR` (borde izquierdo del color de la variante + texto oculto "Requiere revisión"), formulario GET con el campo "Estado" (`ext.filtro_estado`) y la opción "Todos los estados" (`ext.filtro_todos`) y la indicación `ext.filtro_aplicado` cuando hay filtro, hasta pasar T038 ([003] AC-1.1, AC-1.3, AC-1.4)
- [X] T043 [US1] Modificar `templates/extracciones/extraccion.html`: la misma insignia en el encabezado del detalle, la explicación visible debajo y, debajo de ella, el resultado completo de [002] RN-33 sin cambios ([003] AC-1.5)
- [X] T044 [P] [US1] Escribir `e2e/recorridos/hu01-estados.spec.ts`: identifica por texto e icono las cinco etiquetas, lee la explicación al enfocar una etiqueta con el teclado, filtra por "Con advertencias" y vuelve a "Todos los estados"; en `movil` y `oscuro` sin incidencias de axe ([003] quickstart #1, #2)

**Punto de control**: US1 funcional y probable por separado.

---

## Fase 4: Historia de usuario 2 — Eliminar con confirmación (Prioridad: P1)

**Objetivo**: menú ⋮ anclado y operable con teclado, y una confirmación que nombra la extracción, con "Cancelar" predeterminado y sin "Deshacer".

**Prueba independiente**: con ratón y con teclado, abrir el ⋮, elegir "Eliminar", cancelar, repetir y confirmar ([quickstart.md](quickstart.md) #3).

### Pruebas de la historia 2

- [X] T045 [P] [US2] Escribir `tests/integration/test_003_us2_eliminar.py`: `GET /administracion/extracciones/<id>/eliminar/` con `HX-Request: true` responde solo el contenido del diálogo (sin `<html>`), con `ext.eliminar_confirmar` (fecha y hora con `fecha_hora_ar` y período con `fecha_ar`), `ext.eliminar_consecuencias`, "Cancelar" con `autofocus` y "Eliminar" con la variante destructiva; sin la cabecera, la página completa; POST elimina y deja el mensaje `ext.eliminada` con la fecha y hora; POST sobre una extracción inexistente → mensaje `ext.no_existe` y 303 al listado; el menú de una extracción en curso no ofrece "Eliminar"; dos POST con la misma `clave_idempotencia` → un solo efecto y el mismo 303; una ruta A pedida con `HX-Request` por una cuenta sin permisos → 403 completo ([003] AC-2.3 a AC-2.6, FR-008, FR-009, FR-031)

### Implementación de la historia 2

- [X] T046 [US2] Modificar `extracciones/views.py :: eliminar`: con `HX-Request` renderiza `templates/extracciones/_eliminar_contenido.html`; inexistente → `messages.error(ext.no_existe)` y 303 al listado (en GET y POST); decorar el POST con `con_idempotencia("extraccion.eliminar")`; al eliminar, `messages.success(mensaje("ext.eliminada", fecha_hora=…))`; agregar `Vary: HX-Request` ([003] FR-009, Casos límite)
- [X] T047 [US2] Extraer `templates/extracciones/_eliminar_contenido.html` (título `ext.eliminar_titulo`, `ext.eliminar_confirmar`, `ext.eliminar_consecuencias`, formulario POST con `{% csrf_token %}` y `{% campo_idempotencia %}`, botón "Cancelar" `secundario` con `autofocus` que en la página aparte enlaza al listado, botón "Eliminar" `destructivo` con icono `trash-2`) y usarlo desde `templates/extracciones/eliminar.html`, hasta pasar T045 ([003] AC-2.3)
- [X] T048 [P] [US2] Crear `templates/ui/_menu_acciones.html` (ActionMenu): `<details>` como base sin scripts; con Alpine (`x-data="menuAcciones"`), botón con icono `ellipsis-vertical` y nombre accesible `ext.acciones` (con la fecha y hora), lista con `role="menu"` anclada con `x-anchor.bottom-end` dentro de la pantalla; y el componente `menuAcciones` en `static/js/ui.js`: Intro o Espacio abre y enfoca la primera opción, flechas arriba/abajo recorren, Escape cierra y devuelve el foco al botón, clic afuera cierra, abrir uno cierra el anterior (evento `menu-abierto` en `window`) ([003] AC-2.1, AC-2.2, FR-007)
- [X] T049 [US2] Crear `templates/ui/_dialogo_confirmar.html` (`<dialog>` vacío con `aria-labelledby`) y el componente `dialogoConfirmar` en `static/js/ui.js`: intercepta el clic en el enlace "Eliminar", carga el contenido con `htmx.ajax("GET", href, {target})`, abre con `showModal()`, deja el foco en "Cancelar", y con Escape, "Cancelar" o clic en el fondo cierra sin efecto y devuelve el foco al botón ⋮ de la fila; sin scripts el enlace lleva a la página aparte ([003] AC-2.3, AC-2.4)
- [X] T050 [US2] Modificar `templates/extracciones/inicio.html` para usar `_menu_acciones.html` en cada fila con "Ver detalle", "Descargar CSV" (solo si `puede_descargar`) y "Eliminar" (solo si no está en curso, enlazado a la página de confirmación), e incluir `_dialogo_confirmar.html` una vez en la página ([003] AC-2.1, AC-2.6)
- [X] T051 [P] [US2] Escribir `e2e/recorridos/hu02-eliminar.spec.ts`: abrir el ⋮ con ratón y con Intro, recorrer con flechas, Escape devuelve el foco, "Eliminar" → confirmación con "Cancelar" enfocado, Escape y clic afuera no eliminan, confirmar elimina y muestra "Se eliminó la extracción del …" sin "Deshacer"; en `sin-scripts`, la página aparte funciona ([003] quickstart #3)

**Punto de control**: US1 y US2 funcionan juntas y por separado.

---

## Fase 5: Historia de usuario 3 — Ver el avance de una extracción en curso (Prioridad: P1)

**Objetivo**: botón con estado de trabajo, avance en vivo sin recargar, aviso al terminar, mensaje ante error y bloqueo de períodos idénticos (RN-03).

**Prueba independiente**: iniciar la extracción de un año con el servidor de fuentes de prueba y seguir su avance sin recargar hasta que termina ([quickstart.md](quickstart.md) #4 a #6).

### Pruebas de la historia 3

- [X] T052 [P] [US3] Escribir `tests/integration/test_003_us3_periodo_unico.py`: con una extracción en curso del 01/01/2024 al 31/12/2024 de otra cuenta administradora, iniciar el mismo período → no se crea y se ve `ext.periodo_en_curso` con el enlace `ext.ver_existente` a esa extracción; iniciar 01/01/2024–30/06/2024 → se crea; la misma cuenta con una en curso → sigue redirigiendo a la suya ([002] AC-1.11); un `IntegrityError` de la restricción nueva se informa con el mismo mensaje; la migración 0003 se aplica y se revierte ([003] RN-03, AC-3.5, R-09, CHK034)
- [X] T053 [P] [US3] Escribir `tests/integration/test_003_us3_avance.py`: `GET /administracion/extracciones/<id>/` con `HX-Request` y extracción en curso → solo el fragmento `#avance-extraccion` con `hx-trigger="every 3s"`; identificando → `ext.identificando`; con total → `ext.avance` y `<progress>`; terminada → fragmento final sin `hx-trigger` y cabecera `HX-Trigger` con `{"aviso": {"tipo": …, "texto": …}}` usando `ext.termino_finalizada`, `ext.termino_advertencias` (con `n`), `ext.termino_error` (con `n`) o `ext.termino_sin_sorteos`; `Vary: HX-Request` y `Cache-Control: no-store`; la fila en curso del listado se actualiza igual; una extracción con error en la que ninguna fuente respondió muestra `ext.ninguna_fuente` en el detalle ([003] AC-3.2 a AC-3.4, R-10)

### Implementación de la historia 3

- [X] T054 [US3] Agregar a `extracciones/models.py :: Extraccion.Meta.constraints` `models.UniqueConstraint(fields=["desde", "hasta"], condition=Q(estado="EN_CURSO"), name="extraccion_periodo_unico_en_curso")` (se conserva `extraccion_una_en_curso_por_admin`) y generar `extracciones/migrations/0003_extraccion_periodo_unico_en_curso.py` ([003] data-model § 1)
- [X] T055 [US3] Modificar `extracciones/servicios.py :: iniciar_extraccion` para que devuelva `Extraccion | ErrorInicio` (error como valor, `ErrorInicio(clave="ext.periodo_en_curso", existente: Extraccion)`): dentro de la transacción, si existe otra `EN_CURSO` con el mismo `desde` y `hasta`, devuelve el error; captura `IntegrityError` de la restricción nueva y devuelve el mismo error; actualizar los llamadores existentes ([003] RN-03, R-09)
- [X] T056 [US3] Modificar `extracciones/views.py :: inicio` (POST): decorar con `con_idempotencia("extraccion.iniciar")`; ante `ErrorInicio`, volver a mostrar el formulario con `_aviso.html` `warning` que contiene `ext.periodo_en_curso` (con `desde` y `hasta`) y el enlace `ext.ver_existente`; agregar `{% campo_idempotencia %}` al formulario. **Con scripts** (decisión del 21/11/2026, I3), el formulario se envía con `hx-post` a la misma dirección y, si llega `HX-Request`, la vista responde 200 con el listado actualizado (la fila nueva "En curso" con su sondeo) y el panel de avance de la propia, sin cambiar de página (`hx-target` en el contenedor de la pantalla, `hx-swap="outerHTML"`); sin scripts, sigue el 303 al detalle de [002]. Agregar ese caso a T053, hasta pasar T052 ([003] FR-004, FR-006, AC-3.1, AC-3.5)
- [X] T057 [US3] Ampliar `extracciones/consultas.py :: avance` con `etiqueta` y `aviso_final` (tipo y texto de `ext.termino_*` según la etiqueta, con la cantidad de sorteos que requieren revisión o no recuperados) y una función `ninguna_fuente_respondio(extraccion) -> bool` a partir del resumen ([002] RN-33: todas las fuentes con 0 sorteos aportados) ([003] AC-3.3, AC-3.4)
- [X] T058 [US3] Modificar `extracciones/views.py :: extraccion` e `:: inicio` (GET) para responder solo el fragmento cuando llega `HX-Request` (`templates/extracciones/_avance.html` en el detalle, `templates/extracciones/_fila.html` para la fila en curso del listado), con `Vary: HX-Request` y, si terminó, la cabecera `HX-Trigger` con el aviso, hasta pasar T053 ([003] R-10)
- [X] T059 [US3] Rediseñar `templates/extracciones/_avance.html` como ProgressPanel: región `role="status"`, alto reservado (sin saltos), `hx-get` a la misma dirección con `hx-trigger="every 3s"` y `hx-swap="outerHTML"` solo mientras está en curso, icono `loader-circle` con `ext.identificando` mientras identifica, `<progress>` con nombre `ext.avance` cuando hay total, sin animación con movimiento reducido; extraer la fila del listado a `templates/extracciones/_fila.html` con el mismo sondeo cuando está en curso; mostrar `_aviso.html` `danger` con `ext.ninguna_fuente` en `templates/extracciones/extraccion.html` cuando corresponde ([003] AC-3.2, AC-3.4, AC-13.3)
- [X] T060 [US3] Agregar a `static/js/ui.js` el comportamiento `trabajando` para todo `<form data-trabajando>`: al enviar (si la validación previa lo permite), deshabilita el botón de envío, pone `aria-busy="true"`, muestra el icono `loader-circle` y reemplaza su texto por `data-texto-trabajando`; restaurar en `pageshow`; aplicarlo al formulario de inicio con `ext.boton_iniciar_trabajando` ("Iniciando…") en `templates/extracciones/inicio.html` ([003] AC-3.1, FR-004, FR-034)
- [X] T061 [US3] Crear `templates/ui/_avisos.html` (región de Toasts, `aria-live="polite"` y una segunda `role="alert"` para errores) e incluirla en `templates/base.html`; agregar a `static/js/ui.js` el componente `avisos` que escucha el evento HTMX `aviso` (de `HX-Trigger`) y muestra un Toast con `{% clases "toast" %}`, icono del tipo, botón "Cerrar aviso" (`aviso.cerrar`), cierre a los 6 s salvo `error`, sin robar el foco; el aviso final de la extracción enlaza a su detalle ([003] AC-3.3, RN-09)
- [X] T062 [US3] Eliminar `static/js/avance-extraccion.js` y sus `<script>` en `templates/extracciones/inicio.html` y `templates/extracciones/extraccion.html` ([003] R-10)
- [X] T063 [P] [US3] Escribir `e2e/recorridos/hu03-avance.spec.ts` que levanta (`globalSetup`) `python -m tests.fuentes_prueba.servidor --escenario estructura` y `python manage.py procesar_extracciones` con `QUINI6_FUENTE_F*_URL` apuntando al servidor de prueba: "Año anterior" → "Iniciar extracción" → "Iniciando…" no pulsable → fila "En curso" → "Identificando…" → "N de M sorteos procesados" → aviso final y etiqueta final sin recargar; cerrar y volver muestra el estado real ([003] quickstart #4 a #6)

**Punto de control**: las tres historias de Extracción histórica (US1 a US3) completas.

---

## Fase 6: Historia de usuario 4 — Elegir fechas de forma simple y coherente (Prioridad: P1)

**Objetivo**: un único DateField y DateRangePicker en toda la aplicación, con atajos (RN-04), calendario en español desde el lunes y validación junto al campo.

**Prueba independiente**: completar un período escribiendo, con el calendario y con un atajo, en teléfono y escritorio ([quickstart.md](quickstart.md) #7).

### Pruebas de la historia 4

- [X] T064 [P] [US4] Escribir `tests/unit/test_periodos.py`: con `hoy = 21/11/2026`, "Año en curso" = 01/01/2026–21/11/2026 y "Año anterior" = 01/01/2025–31/12/2025; con `hoy = 01/01/2026`, "Año en curso" con inicio igual a fin; `formulario="extraccion"` nunca incluye `todo_el_historial`; `formulario="estadisticas"` lo incluye desde `primer_sorteo` hasta `hoy` y lo omite si `primer_sorteo` es `None` ([003] RN-04, data-model § 2)
- [X] T065 [P] [US4] Escribir `tests/integration/test_003_us4_fechas.py`: los formularios de extracción, estadísticas, búsqueda de resultados y carga de sorteo renderizan cada fecha con `templates/ui/_campo_fecha.html` (`type="date"`, `min`/`max` donde corresponde, `data-validar`); `?atajo=anio_anterior` en `/administracion/extracciones/` y `/estadisticas/` precarga las fechas; `/estadisticas/` ofrece los tres atajos y la extracción solo dos; 31/02/2025 → `fecha.inexistente` junto al campo; 29/02/2025 → `fecha.inexistente`; 29/02/2024 aceptado; fin anterior al inicio → `fecha.fin_anterior` junto al campo de finalización (el mensaje general de [001]/[002] se mantiene en el resumen del formulario); fecha vacía obligatoria → `fecha.falta_inicio`/`fecha.falta_fin` ([003] AC-4.4, AC-4.5, AC-4.7, FR-012)

### Implementación de la historia 4

- [X] T066 [US4] Crear `dominio/periodos.py` (sin Django) con `Atajo(clave, desde, hasta)` y `atajos(hoy: date, formulario: Literal["extraccion", "estadisticas"], primer_sorteo: date | None) -> list[Atajo]` según `data-model.md` § 2, hasta pasar T064 ([003] RN-04)
- [X] T067 [US4] Agregar `resultados/consultas.py :: fecha_primer_sorteo_publicado() -> date | None` (fecha del sorteo publicado más antiguo, con el mismo criterio de publicado que `_q_publicado`) ([003] RN-04)
- [X] T068 [P] [US4] Crear `templates/ui/_campo_fecha.html` (DateField): sin scripts, `<input type="date" name id value="AAAA-MM-DD" min max>` dentro de `_campo.html`, con ancho `w-[11ch]` + botón; con Alpine (`x-data="campoFecha"`), el componente en `static/js/ui.js` lo convierte en campo de texto con máscara `dd/mm/aaaa` (barras automáticas, `inputmode="numeric"`, sin `showPicker()`, [002] D-27) y agrega el botón con icono `calendar` y nombre `fecha.abrir_calendario` que abre un *popover* anclado (`x-anchor.bottom-start`, que se voltea hacia arriba si no hay lugar y nunca tapa el campo) con `<calendar-date locale="es-AR" first-day-of-week="1" min max>`; Escape cierra y devuelve el foco al campo; elegir un día escribe `dd/mm/aaaa` ([003] AC-4.1, AC-4.2, AC-4.6, AC-4.7, FR-010, FR-013)
- [X] T069 [US4] Crear `templates/ui/_periodo.html` (DateRangePicker): dos `_campo_fecha.html` con sus etiquetas, un único `<calendar-range>` en el *popover* con el rango resaltado, y los atajos como **enlaces** `?atajo=<clave>` (sin scripts recargan el formulario precargado; con scripts, el componente `periodo` de `static/js/ui.js` completa ambos campos sin navegar y deja modificarlos) ([003] AC-4.3, AC-4.4, FR-011)
- [X] T070 [US4] Agregar a `estilos/django.css` los estilos de Cally con tokens (`calendar-date::part(...)`, `calendar-month::part(button)`, días deshabilitados con `--color-muted-foreground` y tachado, día elegido y rango con `--color-primary`/`--color-primary-foreground`, foco con `--color-ring`, ambos temas) ([003] AC-4.2, AC-12.4)
- [X] T071 [US4] Crear en `static/js/ui.js` el validador previo `validador` para todo `<form novalidate data-validar-formulario>`: lee en cada campo `data-validar` (JSON con reglas `requerido`, `fecha`, `max`, `min`, `fin_no_anterior_a`, `rango_00_45`, `correo` y su texto ya resuelto por el servidor), valida al salir del campo y al enviar, escribe el mensaje en `#<campo>_error` con el mismo marcado que `_campo.html`, pone `aria-invalid`, y al enviar con errores impide el envío, muestra `form.no_avanza` con la cantidad y lleva el foco al primer campo con error ([003] FR-033, R-13)
- [X] T072 [US4] Ampliar `templates/_campo.html` y crear el filtro `{% reglas campo %}` en `quini6/templatetags/ui.py` que arma `data-validar` a partir de los atributos del campo del formulario de Django (`required`, `widget.attrs` `min`/`max`, y reglas extra declaradas en el formulario como `campo.reglas_previas`) con los textos del catálogo ([003] FR-033)
- [X] T073 [US4] Modificar `extracciones/forms.py :: PeriodoForm`, `estadisticas/forms.py` y `resultados/forms.py` (búsqueda por fecha y carga de sorteo) para: declarar las reglas previas de cada fecha; devolver junto al campo `fecha.inexistente` (con la fecha escrita), `fecha.fin_anterior` (con la fecha de inicio), `fecha.falta_inicio`/`fecha.falta_fin` y `gral.fecha_invalida`, conservando el mensaje general vigente en el resumen; sin cambiar ninguna regla de [001] ni de [002] ([003] AC-4.5, FR-012)
- [X] T074 [US4] Modificar `extracciones/views.py :: inicio` y `estadisticas/views.py :: index` para leer `?atajo=` y precargar las fechas con `dominio.periodos.atajos(timezone.localdate(), …, fecha_primer_sorteo_publicado())`, y pasar los atajos al contexto ([003] AC-4.4)
- [X] T075 [US4] Reemplazar los campos de fecha en `templates/extracciones/inicio.html` (`_periodo.html` con dos atajos y `max` = hoy), `templates/estadisticas/index.html` (`_periodo.html` con tres atajos, etiquetas "Desde"/"Hasta"), `templates/resultados/_busqueda_form.html` (`_campo_fecha.html`) y `templates/resultados/admin/concurso_form.html` (`_campo_fecha.html`); agregar `novalidate data-validar-formulario` a esos formularios, hasta pasar T065 ([003] FR-010)
- [X] T076 [P] [US4] Escribir `e2e/recorridos/hu04-fechas.spec.ts`: escribir 01012025 → 01/01/2025; abrir el calendario (semana desde el lunes, "enero", "lunes"), elegir un rango, usar "Año en curso" y modificarlo; 31/02/2025, 29/02/2025, 29/02/2024 y fin anterior al inicio con sus mensajes; días futuros deshabilitados en la extracción; Escape devuelve el foco; en `movil` el campo no desborda; en `sin-scripts`, el calendario del navegador y los atajos como enlaces ([003] quickstart #7)

**Punto de control**: fechas unificadas en toda la aplicación.

---

## Fase 7: Historia de usuario 5 — Saber dónde estoy y moverme con comodidad (Prioridad: P1)

**Objetivo**: encabezado con sección activa, menú de cuenta, menú móvil, saltar al contenido, caminos de regreso, logotipo y favicon.

**Prueba independiente**: recorrer todas las secciones con ratón, teclado y a 360 px ([quickstart.md](quickstart.md) #8).

### Pruebas de la historia 5

- [X] T077 [P] [US5] Escribir `tests/integration/test_003_us5_navegacion.py`: en `/resultados/`, `/estadisticas/`, `/mis-jugadas/` y `/administracion/…` el enlace de su sección tiene `aria-current="page"` y los demás no; "Salir" está dentro del menú de cuenta (con el correo) y no en la lista de secciones; "Saltar al contenido" es el primer enlace del `<body>` y apunta a `#contenido`; el logotipo enlaza a `/` con nombre `nav.logotipo`; `<link rel="icon">` apunta al favicon; los detalles muestran su camino de regreso: sorteo (`nav.volver_sorteos`), extracción (`nav.volver_extracciones`), sorteo extraído (`nav.volver_extraccion` con la fecha y hora), jugada (`nav.volver_jugadas`), sorteo de administración (`nav.volver_sorteos`) ([003] AC-5.1 a AC-5.7)

### Implementación de la historia 5

- [X] T078 [P] [US5] Crear `ui/marca/isotipo.svg`, `ui/marca/logotipo.svg` y `ui/marca/favicon.svg` provisionales (tipográficos "QUINI_6" con `--color-primary`, sin imitar marcas oficiales, RN-08) y agregar `("marca", BASE_DIR / "ui" / "marca")` a `STATICFILES_DIRS` en `quini6/settings.py` (P-02 aprobado el 21/11/2026 con este criterio) ([003] FR-018, RN-08)
- [X] T079 [US5] Crear `quini6/navegacion.py` con el procesador de contexto `navegacion(request)` que devuelve `seccion_activa` (`resultados` para `/` y `/resultados/…`, `estadisticas`, `jugadas` para `/mis-jugadas/…`, `administracion` para `/administracion/…`) y registrarlo en `TEMPLATES[0]["OPTIONS"]["context_processors"]` de `quini6/settings.py` ([003] FR-014)
- [X] T080 [P] [US5] Crear `templates/ui/_menu_cuenta.html` (AccountMenu): botón con icono `circle-user-round` y el correo truncado (`truncate max-w-[16ch]`, completo en `title` y en el nombre accesible `nav.cuenta`), menú Alpine con Escape y clic afuera, y dentro el formulario POST "Salir"; sin scripts, el correo y "Salir" visibles ([003] AC-5.3, FR-015, FR-030)
- [X] T081 [P] [US5] Crear `templates/ui/_volver.html` (BackLink: icono `arrow-left` + texto del catálogo) ([003] AC-5.6)
- [X] T082 [US5] Rediseñar el encabezado de `templates/base.html` (NavBar): "Saltar al contenido" (`nav.saltar`) como primer elemento; logotipo enlazado a `/`; enlaces sin subrayado, área de 44 × 44 px, estados de cursor, foco y pulsado; sección activa con fondo tenue + marca inferior y `aria-current="page"`; `_menu_cuenta.html` con sesión o "Ingresar"/"Crear cuenta" sin sesión; debajo de 768 px, botón "Menú" (`nav.menu`, icono `menu`/`x`, `aria-expanded`, `aria-controls`, Escape cierra y devuelve el foco) con Alpine; sin scripts, la lista visible; `<link rel="icon" href="{% static 'marca/favicon.svg' %}">` ([003] AC-5.1 a AC-5.5, AC-5.7, FR-014 a FR-017)
- [X] T083 [US5] Agregar `_volver.html` a `templates/resultados/detalle.html`, `templates/extracciones/extraccion.html`, `templates/extracciones/sorteo.html`, `templates/jugadas/detalle.html` y `templates/resultados/admin/panel.html`, `numeros.html`, `premios.html`, `publicar.html`, `historial.html` (reemplazando los "←" existentes), hasta pasar T077 ([003] AC-5.6, FR-017)
- [X] T084 [P] [US5] Escribir `e2e/recorridos/hu05-navegacion.spec.ts`: Tab inicial muestra "Saltar al contenido" y lleva el foco a `main`; sección actual anunciada; menú de cuenta con teclado; en `movil`, "Menú" con Intro y Escape; caminos de regreso en cada página interna ([003] quickstart #8)

**Punto de control**: todas las historias P1 completas en Django (MVP de la Etapa 1).

---

## Fase 8: Historia de usuario 6 — Ingresar sin fricción (Prioridad: P2)

**Objetivo**: ingreso y registro centrados en una tarjeta, mostrar/ocultar contraseña, autocompletado, errores antes de enviar y botón en estado de trabajo.

**Prueba independiente**: ingresar con un gestor de contraseñas, mostrar y ocultar la contraseña, cometer errores y crear una cuenta ([quickstart.md](quickstart.md) #9).

### Pruebas de la historia 6

- [X] T085 [P] [US6] Escribir `tests/integration/test_003_us6_ingreso.py`: "Ingresar" y "Crear cuenta" con `autocomplete="email"` y `current-password`/`new-password`; sin enlace de recuperación de contraseña; enlaces alternativos `cuenta.ir_a_registro` y `cuenta.ir_a_ingreso` con estilo secundario y conservando `next`; credenciales incorrectas → `cuenta.credenciales_incorrectas` sin revelar si el correo existe; formularios con `novalidate` y `data-validar` (correo con `cuenta.correo_invalido`) ([003] AC-6.3 a AC-6.7, FR-019 a FR-021, [001] AC-3.5)

### Implementación de la historia 6

- [X] T086 [P] [US6] Crear `templates/ui/_campo_contrasena.html` (PasswordField) y el componente `campoContrasena` en `static/js/ui.js`: botón "Mostrar"/"Ocultar" (`cuenta.mostrar`/`cuenta.ocultar`, iconos `eye`/`eye-off`, `aria-pressed`) que cambia `type` y anuncia `cuenta.contrasena_visible`/`cuenta.contrasena_oculta` en una región `aria-live="polite"`; sin scripts, sin botón ([003] AC-6.2)
- [X] T087 [US6] Rediseñar `templates/cuentas/ingresar.html` y `templates/cuentas/registrarse.html`: tarjeta centrada `max-w-[28rem]` (en móvil, todo el ancho con los márgenes), `_campo.html` para el correo y `_campo_contrasena.html`, botón principal "Ingresar"/"Crear cuenta" con `data-texto-trabajando` `cuenta.ingresando`, alternativa separada debajo con estilo secundario; agregar `autocomplete` a los widgets en `cuentas/forms.py` y las reglas previas (`requerido`, `correo`), hasta pasar T085 ([003] AC-6.1, AC-6.5 a AC-6.7)
- [X] T088 [P] [US6] Escribir `e2e/recorridos/hu06-ingreso.spec.ts`: tarjeta centrada en escritorio; "Mostrar"/"Ocultar"; correo inválido al salir del campo; credenciales incorrectas; "Ingresando…"; ir a "Crear cuenta" y volver ([003] quickstart #9)

---

## Fase 9: Historia de usuario 7 — Filtros de estadísticas claros (Prioridad: P2)

**Objetivo**: filtros legibles y alineados, "Consultar un número" separado, validación inmediata del número, gráfico rediseñado y tabla ordenable.

**Prueba independiente**: configurar Estadísticas en escritorio y a 360 px, consultar 46 y ordenar la tabla ([quickstart.md](quickstart.md) #10).

### Pruebas de la historia 7

- [X] T089 [P] [US7] Escribir `tests/integration/test_003_us7_estadisticas.py`: etiquetas "Número", "Modalidad", "Desde", "Hasta"; ayuda `est.numero_ayuda` asociada al número; sección con encabezado `est.consultar_numero` separada del período; todas las opciones de modalidad con su texto completo (incluida "Tradicional – Primer Sorteo"); `?orden=frecuencia`, `-frecuencia`, `numero`, `-numero` ordenan la tabla con `aria-sort` en el encabezado y orden inválido → por número ascendente; `numero=46` → `jugada.fuera_de_rango` junto al campo y la consulta anterior; la leyenda `est.leyenda` en un aviso `info` con icono antes de los resultados; el gráfico con `role="img"` y descripción; los cálculos y valores son idénticos a los de antes ([003] AC-7.1 a AC-7.6, AC-10.1, NFR-009)

### Implementación de la historia 7

- [X] T090 [US7] Modificar `estadisticas/forms.py`: etiquetas breves, ayuda `est.numero_ayuda`, reglas previas (`rango_00_45` con `jugada.fuera_de_rango`), parámetro `orden` con los cuatro valores válidos; `estadisticas/views.py :: index`: ordenar la lista de frecuencias para la tabla según `orden` (solo presentación, sin tocar `dominio/estadisticas.py`) y pasar el orden actual ([003] AC-7.3, AC-7.5, AC-7.6)
- [X] T091 [US7] Extraer el gráfico a `templates/estadisticas/_grafico.html` con `role="img"`, `<title>`/`<desc>` y colores de tokens (`fill-primary`, número consultado con `fill-accent` y su rótulo con `text-accent-text`), y rediseñar `templates/estadisticas/index.html`: barra de filtros en una línea base en escritorio (`md:flex md:items-end`) y en filas a 360 px, selector de modalidad sin recortes (`min-w-0`, ancho al contenido), bloque `est.consultar_numero` separado, `_aviso.html` `info` con `est.leyenda`, tabla con encabezados ordenables como enlaces (`_encabezado_ordenable.html` de T106 o, si aún no existe, uno local que T106 reemplaza), hasta pasar T089 ([003] AC-7.1, AC-7.2, AC-7.4, AC-7.5, AC-10.1)
- [X] T092 [P] [US7] Escribir `e2e/recorridos/hu07-estadisticas.spec.ts`: opciones completas; misma línea base en `escritorio` y sin superposición en `movil`; 46 → mensaje inmediato sin enviar; ordenar por frecuencia; aviso visible ([003] quickstart #10)

---

## Fase 10: Historia de usuario 8 — Estados vacíos que orientan (Prioridad: P2)

**Objetivo**: estado vacío con icono, título, explicación y acción según el perfil, distinto del "sin resultados para el filtro".

**Prueba independiente**: con la base vacía, recorrer como visitante, usuaria y administración, y aplicar filtros sin resultados ([quickstart.md](quickstart.md) #11).

### Pruebas de la historia 8

- [X] T093 [P] [US8] Escribir `tests/integration/test_003_us8_vacios.py`: "Mis jugadas" sin jugadas → `vacio.jugadas` con icono `ticket` y el botón "Registrar mi primera jugada"; Resultados sin sorteos → `vacio.resultados` y, **solo** para administración, "Cargar sorteo", "Extracción histórica" y `vacio.resultados_nota_admin`; "Extracción histórica" sin extracciones → `vacio.extracciones`; con filtro sin resultados → `vacio.filtro` con el filtro nombrado y "Limpiar filtros" (enlace sin parámetros); búsqueda de resultados sin coincidencias → `vacio.filtro`; Estadísticas sin sorteos → `vacio.estadisticas` ([003] AC-8.1 a AC-8.4, FR-025, FR-026)

### Implementación de la historia 8

- [X] T094 [P] [US8] Crear `templates/ui/_estado_vacio.html` (EmptyState): icono decorativo grande, título como `<h2>`, explicación, acción opcional (`_boton.html`) y variantes `sin_datos`/`sin_resultados` (esta última con icono `filter-x`, el filtro y "Limpiar filtros") ([003] RN-06)
- [X] T095 [US8] Aplicar `_estado_vacio.html` en `templates/jugadas/lista.html`, `templates/resultados/index.html` (con accesos de administración solo si `user.es_administrador`), `templates/resultados/busqueda.html`, `templates/extracciones/inicio.html` (vacío y filtro), `templates/estadisticas/index.html` y `templates/resultados/admin/listado.html` (`admin.sin_concursos`), reemplazando los cuadros punteados, hasta pasar T093 ([003] FR-025, FR-026)
- [X] T096 [P] [US8] Escribir `e2e/recorridos/hu08-vacios.spec.ts` contra una base vacía (`preparar_e2e --vacio`, opción que agrega solo las cuentas) recorriendo como visitante, usuaria y administración ([003] quickstart #11)
- [X] T097 [US8] Agregar a `quini6/management/commands/preparar_e2e.py` la opción `--vacio` (solo crea las tres cuentas) usada por T096 ([003] R-23)

---

## Fase 11: Historia de usuario 9 — Tablas cómodas en cualquier pantalla (Prioridad: P2)

**Objetivo**: orden por columna, paginación de 20, tarjetas a 360 px, fila entera clicable y nombres de columnas uniformes.

**Prueba independiente**: con 0, 1 y 300 extracciones, ordenar, paginar y abrir filas en escritorio y teléfono ([quickstart.md](quickstart.md) #2 y #12).

### Pruebas de la historia 9

- [X] T098 [P] [US9] Escribir `tests/integration/test_003_us9_tablas.py`: con 300 extracciones, `pagina=1` muestra 20 y `pag.pagina` "Página 1 de 15"; `orden` ∈ {`fecha`, `-fecha`, `periodo`, `-periodo`, `estado`, `-estado`} ordena según `data-model.md` § 2 (desempate `-id`) con `aria-sort`; inválido → `-fecha`; filtro y orden se conservan en los enlaces de paginación; `pagina=99` → última página con datos; con 1 extracción no hay paginación; cada fila tiene un enlace "Ver detalle →" (`ext.ver_detalle`) que cubre la fila salvo el ⋮ ([003] AC-9.1, AC-9.2, AC-9.4, RN-07)
- [X] T099 [P] [US9] Escribir `tests/integration/test_003_us9_columnas.py`: los encabezados `<th>` de Extracción histórica, Resultados, Mis jugadas, Administración y el detalle de extracción usan solo los nombres de `contracts/mensajes.md` § 5 para cada dato ("Fecha", "Período", "Estado", "Fecha del sorteo", "Sorteo", "Modalidad", "Frecuencia", "Porcentaje", "Aciertos") y las fechas con formato `dd/mm/aaaa` o `dd/mm/aaaa HH:MM` ([003] AC-9.5, RN-05)

### Implementación de la historia 9

- [X] T100 [US9] Ampliar `extracciones/consultas.py :: listado_extracciones(filtro, orden: str = "-fecha", pagina: int = 1)` con el orden de `data-model.md` § 2 (`Case/When` sobre `estado` + `tiene_no_recuperados` para `estado`; `desde`, `hasta` para `periodo`; `iniciada_en` para `fecha`; siempre `-id` al final) y `Paginator(…, 20)` con `get_page` (fuera de rango → última), devolviendo `Pagina` (elementos, pagina, paginas, total, orden, filtro) ([003] AC-9.1, AC-9.2, RN-07)
- [X] T101 [P] [US9] Crear `templates/ui/_paginacion.html` (Pagination: `<nav aria-label="Paginación">`, "Página N de M", "Anterior"/"Siguiente" como enlaces que conservan los demás parámetros, `aria-disabled` en los extremos) y el filtro `{% url_con request parametro=valor %}` en `quini6/templatetags/ui.py` que reemplaza un parámetro conservando los demás ([003] RN-07)
- [X] T102 [P] [US9] Crear `templates/ui/_encabezado_ordenable.html` (`<th aria-sort>` con enlace que alterna ascendente/descendente, icono `arrow-up`/`arrow-down`/`arrow-up-down` y texto oculto `tabla.orden_asc`/`tabla.orden_desc`) ([003] AC-9.1)
- [X] T103 [US9] Agregar a `estilos/django.css` el patrón de tabla apilable: debajo de `md`, `table.apilable` muestra cada `<tr>` como tarjeta (`rounded-card shadow-1 bg-surface`) y cada `<td data-rotulo>` como bloque con su rótulo (`before:content-[attr(data-rotulo)]`), sin desplazamiento horizontal; y el patrón de fila clicable (`.fila-enlace` con el enlace "Ver detalle →" estirado con `after:absolute after:inset-0` y el ⋮ por encima con `relative z-10`) ([003] AC-9.3, AC-9.4, FR-027)
- [X] T104 [US9] Modificar `extracciones/views.py :: inicio` para leer `orden` y `pagina` y rediseñar la tabla de `templates/extracciones/inicio.html` y `_fila.html` con `apilable`, `data-rotulo`, `_encabezado_ordenable.html` en "Fecha", "Período" y "Estado", `fila-enlace` y `_paginacion.html`, hasta pasar T098 ([003] FR-027)
- [X] T105 [US9] Aplicar `apilable`, `data-rotulo` y los nombres de columna de RN-05 a `templates/resultados/_listado.html`, `templates/jugadas/lista.html`, `templates/resultados/admin/listado.html` y la tabla de sorteos de `templates/extracciones/extraccion.html`, hasta pasar T099 ([003] AC-9.3, AC-9.5)
- [X] T106 [US9] Reemplazar el encabezado ordenable local de `templates/estadisticas/index.html` (T091) por `_encabezado_ordenable.html` ([003] AC-7.5)
- [X] T107 [P] [US9] Escribir `e2e/recorridos/hu09-tablas.spec.ts`: ordenar por cada columna, paginar conservando filtro y orden, clic en la fila abre el detalle, en `movil` tarjetas rotuladas sin desplazamiento horizontal ([003] quickstart #12)

---

## Fase 12: Historia de usuario 10 — Avisos importantes que se noten (Prioridad: P2)

**Objetivo**: los cuatro tipos de mensajes con el mismo icono, color, forma y ubicación, anunciados, y el pie legal legible.

**Prueba independiente**: recorrer Estadísticas y el pie a 360 px y provocar mensajes de éxito, advertencia, error e información ([quickstart.md](quickstart.md) #13).

### Pruebas de la historia 10

- [X] T108 [P] [US10] Escribir `tests/integration/test_003_us10_avisos.py`: los mensajes de Django `success`, `info`, `warning` y `error` se renderizan con la variante, el icono y el rol correspondientes (`status` o `alert`) en la región de avisos de `base.html`, con su versión sin scripts como `Callout` dentro de `<main>`; el pie contiene `pie.legal` con `text-sm text-muted-foreground` ([003] AC-10.2, AC-10.3, RN-09)

### Implementación de la historia 10

- [X] T109 [US10] Modificar `templates/base.html`: los `messages` de Django se emiten como `_aviso.html` dentro de `<main>` (sin scripts) con `data-aviso` y el componente `avisos` de `static/js/ui.js` los pasa a Toasts al cargar (6 s salvo error, botón "Cerrar aviso"); mapeo de etiquetas `success`→`success`, `info`→`info`, `warning`→`warning`, `error`→`danger`; pie rediseñado con `pie.legal` en 14 px y `--color-muted-foreground`, hasta pasar T108 ([003] AC-10.2, AC-10.3)
- [X] T110 [P] [US10] Escribir `e2e/recorridos/hu10-avisos.spec.ts`: provocar éxito (registrar jugada), advertencia (extracción con advertencias), error (credenciales incorrectas) e información; comparar icono, rol y ubicación; el aviso de éxito se cierra a los 6 s y el de error no; pie legible en `movil` y `oscuro` ([003] quickstart #13)

---

## Fase 13: Historia de usuario 11 — Lenguaje de interfaz uniforme (Prioridad: P2)

**Objetivo**: todos los textos visibles salen del catálogo, en forma neutra, con "sorteo" en lugar de "concurso".

**Prueba independiente**: revisar todos los textos visibles de todas las pantallas ([quickstart.md](quickstart.md) #14).

### Pruebas de la historia 11

- [X] T111 [P] [US11] Escribir `tests/unit/test_textos_prohibidos.py` según `contracts/mensajes.md` § 1.5: busca en los valores de `dominio.mensajes.MENSAJES`, en el texto visible de `templates/**/*.html` (sin etiquetas HTML ni de plantilla, sin atributos `class`/`id`/`href`/`name`) y en `static/js/*.js` las formas `\b(tenés|podés|querés|elegís|buscás|ingresá|elegí|creá|corregí|verificá|intentá|registrá|registraste|iniciá|escribí|volvé|indicaste|hiciste)\b`, `\btus?\b`, `\bconcursos?\b` y `\bextracci[oó]n\b` que no forme parte de "Extracción histórica"/"extracción histórica" ni de los textos de estado de [002] ("Extracción finalizada…", "Extracción en curso", "la extracción del {fecha_hora}"); falla con la lista de apariciones ([003] AC-11.1, AC-11.3, SC-007)
- [X] T112 [P] [US11] Escribir `tests/unit/test_botones_con_verbo.py`: todo `<button>` y enlace con estilo de botón en `templates/` tiene texto (o `{% msg %}`) que no es "Aceptar" ni "OK" y empieza con un verbo en infinitivo de una lista permitida (`Ingresar`, `Crear`, `Registrar`, `Iniciar`, `Consultar`, `Eliminar`, `Cancelar`, `Guardar`, `Descargar`, `Cargar`, `Publicar`, `Ver`, `Volver`, `Limpiar`, `Mostrar`, `Ocultar`, `Reintentar`, `Cerrar`, `Salir`, `Abrir`, `Modificar`, `Corregir`, `Resolver`, `Observar`, `Quitar`, `Buscar`) ([003] AC-11.2)

### Implementación de la historia 11

- [X] T113 [P] [US11] Reemplazar los textos literales por `mensaje("clave")` en `cuentas/decoradores.py` (`SIN_PERMISO` → `admin.sin_permiso`), `cuentas/forms.py` y `cuentas/views.py` (`cuenta.*`), y actualizar las afirmaciones de `tests/integration/test_us3_cuentas.py`, `tests/integration/test_matriz_acceso.py`, `tests/integration/test_seguridad.py` y `tests/integration/test_extraccion_acceso.py` para que comparen con `MENSAJES[clave]` (requiere T001) ([003] FR-035)
- [X] T114 [P] [US11] Reemplazar los textos literales en `jugadas/forms.py`, `jugadas/servicios.py`, `jugadas/views.py`, `dominio/numeros.py`, `dominio/importes.py`, `dominio/comparacion.py` y `static/js/selector-numeros.js` (que pasa a leer sus textos de atributos `data-msg-*` que escribe el servidor), y actualizar `tests/integration/test_us4_jugadas.py`, `tests/integration/test_us5_comparacion.py`, `tests/unit/test_numeros.py`, `tests/unit/test_importes.py` y `tests/unit/test_comparacion.py` (mismos casos y resultados; solo cambia el texto esperado) (requiere T001) ([003] FR-035, R-13)
- [X] T115 [P] [US11] Reemplazar los textos literales en `resultados/forms.py`, `resultados/servicios.py`, `resultados/views_admin.py`, `resultados/views_publicas.py`, `dominio/consistencia.py`, `estadisticas/forms.py`, `dominio/estadisticas.py`, y actualizar `tests/integration/test_us1_consulta.py`, `tests/integration/test_us2_admin.py`, `tests/integration/test_us6_estadisticas.py`, `tests/integration/test_us7_correccion.py`, `tests/unit/test_consistencia.py` y `tests/unit/test_estadisticas.py` (requiere T001) ([003] FR-035)
- [X] T116 [P] [US11] Reemplazar los textos literales en `extracciones/consultas.py`, `extracciones/servicios.py`, `extracciones/forms.py`, `dominio/extraccion/periodo.py` y `quini6/vistas_error.py`, y actualizar `tests/integration/test_extraccion_us1.py` a `test_extraccion_us4.py` y `tests/unit/extraccion/` donde afirman textos (requiere T001) ([003] FR-035)
- [X] T117 [P] [US11] Reemplazar por `{% msg %}` todos los textos visibles de `templates/resultados/**`, incluidas las plantillas de administración (título `admin.titulo_listado`, botón `admin.crear` "Cargar sorteo", "Sorteo N.º {N}", "Historial del sorteo N.º {N}", "Modificar sorteo", "Ir al sorteo existente", `admin.ayuda_modalidades`, `admin.corregir_bloqueantes`) (requiere T001) ([003] D-04, RN-10)
- [X] T118 [P] [US11] Reemplazar por `{% msg %}` todos los textos visibles de `templates/jugadas/**` (`jugada.intro`, `jugada.campo_sorteo`, `jugada.ayuda_modalidades`, `jugada.elegir_numeros`, `jugada.escribir_numero`, `jugada.duplicada`, `jugada.confirmar_eliminacion`, `comp.tu_jugada`, `comp.numeros_resaltados`), `templates/cuentas/**`, `templates/estadisticas/**` (`est.ayuda_periodo`), `templates/extracciones/**` y `templates/403.html`, `404.html`, `500.html`, `templates/base.html` (requiere T001) ([003] D-01, D-04)
- [X] T119 [US11] Ejecutar `pytest` completo hasta que T111 y T112 pasen y ninguna prueba de reglas haya cambiado sus casos ni sus resultados esperados (solo textos), y agregar al inicio de `specs/001-quini6-mvp/contracts/mensajes.md` y `specs/002-extraccion-historica-csv/contracts/mensajes.md` la nota "Desde [003], los textos vigentes son los de `specs/003-modernizacion-ui-ux/contracts/mensajes.md` y `dominio/mensajes.py`" ([003] R-13)
- [X] T120 [P] [US11] Escribir `e2e/recorridos/hu11-lenguaje.spec.ts`: recorre todas las pantallas con cada perfil y falla si el texto visible (`innerText`) contiene alguna forma prohibida de T111 ([003] quickstart #14, SC-007)

**Punto de control**: todas las historias P1 y P2 completas (criterio de terminado de la Etapa 1, CHK012).

---

## Fase 14: Historia de usuario 12 — Elegir tema claro u oscuro (Prioridad: P3)

**Objetivo**: tema según el dispositivo, selector "Claro"/"Oscuro"/"Según el dispositivo" recordado en el navegador, contrastes en ambos temas.

**Prueba independiente**: abrir con el dispositivo en oscuro, cambiar a claro, cerrar y volver; probar sin scripts ([quickstart.md](quickstart.md) #15).

### Pruebas de la historia 12

- [X] T121 [P] [US12] Escribir `tests/integration/test_003_us12_tema.py`: `POST /preferencias/tema/` con `tema=oscuro` fija `quini6_tema=oscuro` (`Path=/`, `SameSite=Lax`, `Max-Age` de 400 días, sin `HttpOnly`) y responde 303 a `next`; `tema=dispositivo` borra la cookie; `tema` inválido se ignora; `next` externo (`https://otro.sitio/`) o ausente → `/`; sin CSRF → 403; con la cookie `claro`/`oscuro`, `<html data-theme>` tiene ese valor; sin cookie o con valor inválido, sin `data-theme`; visitante y usuaria por igual; la vista no escribe nada en la base ni en la sesión ([003] FR-036, AC-12.1 a AC-12.3, NFR-008, data-model § 4)

### Implementación de la historia 12

- [X] T122 [US12] Crear `quini6/tema.py` con la vista `preferencia_tema` (POST, CSRF, valida `next` con `url_has_allowed_host_and_scheme`) y el procesador de contexto `tema(request)` (`tema_actual` ∈ {`claro`, `oscuro`, `dispositivo`}); agregar `path("preferencias/tema/", …)` en `quini6/urls.py` y el procesador en `quini6/settings.py`; escribir `data-theme="{{ tema_actual }}"` en `<html>` de `templates/base.html` solo si no es `dispositivo`, hasta pasar T121 ([003] R-14)
- [X] T123 [US12] Crear `templates/ui/_selector_tema.html` (ThemeSelect: grupo de radio "Tema" con `tema.claro`, `tema.oscuro`, `tema.dispositivo` e iconos `sun`/`moon`/`monitor`, formulario POST con botón "Guardar tema" visible solo sin scripts) e incluirlo en el pie de `templates/base.html` (visible también para visitantes); componente `selectorTema` en `static/js/ui.js` que al cambiar aplica `data-theme` al instante (o lo quita), escribe la cookie igual que el servidor y no recarga ([003] AC-12.2, AC-12.3)
- [X] T124 [P] [US12] Escribir `e2e/recorridos/hu12-tema.spec.ts`: en `oscuro` sin cookie la página se ve oscura (`prefers-color-scheme`); elegir "Claro" cambia sin perder lo escrito en un formulario; nueva página conserva el tema; en `sin-scripts` el formulario lo cambia; axe sin incidencias en ambos temas en todas las pantallas ([003] quickstart #15, AC-12.4)

---

## Fase 15: Historia de usuario 13 — Interfaz con sensación de calidad (Prioridad: P3)

**Objetivo**: transiciones breves que respetan "reducir movimiento", marcadores de posición y un único sistema visual.

**Prueba independiente**: recorrer la aplicación con y sin "reducir movimiento" ([quickstart.md](quickstart.md) #16).

- [X] T125 [US13] Agregar a `estilos/django.css` las transiciones con tokens: menús y *popovers* (opacidad y escala 150 ms), `<dialog>` y su fondo (200 ms con `@starting-style`), Toasts (entrada y salida 200 ms); todas anuladas por `prefers-reduced-motion: reduce` desde `ui/base.css` ([003] AC-13.1, AC-13.2, R-15)
- [X] T126 [US13] Usar `_esqueleto.html` como contenido inicial de `#avance-extraccion` y de la fila "En curso" mientras llega la primera respuesta HTMX (`hx-indicator`), reservando el alto final ([003] AC-13.3, NFR-004)
- [X] T127 [US13] Revisar todas las plantillas y reemplazar las clases de `estilos/legado.css` todavía en uso por utilidades con tokens (`rounded-control`, `rounded-card`, `shadow-1`, `h-control`, escala de texto de `contracts/tokens.md`), dejando un único botón principal por pantalla ([003] AC-13.4, RN-11)
- [X] T128 [P] [US13] Escribir `tests/unit/test_iconos_con_texto.py`: en `templates/`, todo `{% icono %}` dentro de un `<button>` o `<a>` convive con texto visible o con `aria-label`/`{% msg %}` (solo el ⋮ puede no tener texto visible, y siempre con nombre accesible) ([003] AC-13.5)
- [X] T129 [P] [US13] Escribir `e2e/recorridos/hu13-acabado.spec.ts`: en `movimiento-reducido`, `getComputedStyle` de menú, diálogo y Toast con `transition-duration: 0s`; la barra de progreso sin animación; con movimiento normal, ninguna transición supera 250 ms; respuesta visible en menos de 100 ms: entre el clic y el cambio de estado del botón "Iniciar extracción" y entre el clic en el ⋮ y la apertura del menú, medido con `performance.now()` en la página (NFR-005, hallazgo G1 de `/speckit-analyze`) ([003] quickstart #16)

---

## Fase 16: Robustez de la interacción (transversal, FR-030 a FR-034)

**Propósito**: textos largos, reintentos sin duplicar, sesión vencida con formulario pendiente, validación previa y estados de trabajo en **todos** los formularios.

### Pruebas

- [X] T130 [P] Escribir `tests/integration/test_003_formulario_pendiente.py`: POST a `/mis-jugadas/nueva/` sin sesión → 200 con la pantalla "Ingresar", `cuenta.sesion_vencida` y el campo oculto `pendiente` (token firmado que no contiene `csrfmiddlewaretoken`, `clave_idempotencia` ni contraseñas), `Cache-Control: no-store`; ingresar con ese `pendiente` → responde el formulario de jugada precargado y **no** crea ninguna jugada; con otra cuenta, al enviar, la jugada queda para esa cuenta; token alterado, vencido (más de 60 min) o mayor a 8 KB → se ignora y se muestra el formulario vacío; POST a una vista de administración sin sesión e ingreso con una cuenta sin permisos → página de sin permisos; GET sin sesión sigue redirigiendo como antes ([003] FR-032, data-model § 3)
- [X] T131 [P] Escribir `tests/integration/test_003_idempotencia_formularios.py`: dos POST idénticos con la misma `clave_idempotencia` a registrar jugada, eliminar jugada, crear cuenta y crear sorteo producen un único efecto y el mismo destino ([003] FR-031)
- [X] T132 [P] Escribir `tests/integration/test_003_formularios_validacion.py`: todos los formularios de `templates/` (jugadas, cuentas, administración de sorteos, extracción, estadísticas, búsqueda) tienen `novalidate`, `data-validar-formulario`, `data-trabajando` y `data-validar` en cada campo obligatorio ([003] FR-033, FR-034, SC-010)

### Implementación

- [X] T133 Crear `quini6/formulario_pendiente.py`: `firmar(ruta, post) -> str` (`TimestampSigner` con sal `quini6.formulario_pendiente`, JSON comprimido, excluye `csrfmiddlewaretoken`, `clave_idempotencia` y todo campo cuyo nombre contenga `password` o `contrasena`, máximo 8 KB), `leer(token) -> FormularioPendiente | None` (vigencia 60 min), y el registro `@reanudable(nombre)` que marca las vistas que aceptan un modo "reanudar" (renderizan su formulario con `initial` = campos del token) ([003] R-12, data-model § 3)
- [X] T134 Modificar `cuentas/decoradores.py :: sesion_requerida` y `:: administrador_requerido`: ante un POST sin sesión a una vista `@reanudable`, renderizar `templates/cuentas/ingresar.html` con `cuenta.sesion_vencida`, el `pendiente` firmado y `next`, código 200 y `no-store` (los GET siguen con `redirect_to_login`) ([003] FR-032)
- [X] T135 Modificar `cuentas/views.py :: ingresar` y `templates/cuentas/ingresar.html` (campo oculto `pendiente`): tras un ingreso correcto con `pendiente` válido, resolver la ruta con `django.urls.resolve` y, si su vista es `@reanudable`, responder esa vista en modo reanudar (verificando permisos con la cuenta recién ingresada; sin permisos → página de sin permisos), `no-store`; si no, seguir con `next` como hoy; marcar con `@reanudable` las vistas `jugadas.views.nueva` y `:: editar`, `extracciones.views.inicio` y `resultados.views_admin.nuevo`, `:: modificar`, `:: numeros`, `:: premios`, hasta pasar T130 ([003] FR-032)
- [X] T136 Decorar con `con_idempotencia` los POST de `jugadas/views.py :: nueva` (`jugada.registrar`) y `:: eliminar` (`jugada.eliminar`), `cuentas/views.py :: registrarse` (`cuenta.crear`) y `resultados/views_admin.py :: nuevo` (`sorteo.crear`), y agregar `{% campo_idempotencia %}` a sus plantillas, hasta pasar T131 ([003] FR-031)
- [X] T137 Agregar a `static/js/ui.js` el manejo de falta de conexión: al enviar un formulario con `navigator.onLine === false`, o ante `htmx:sendError`, impedir el envío y mostrar un `Callout` `danger` con icono `wifi-off`, `gral.sin_conexion` y el botón "Reintentar" (`gral.reintentar`, icono `rotate-cw`) que reenvía el mismo formulario con la misma `clave_idempotencia` ([003] FR-031, Casos límite)
- [X] T138 Agregar `novalidate data-validar-formulario data-trabajando` y las reglas previas de cada campo a los formularios de `templates/jugadas/formulario.html`, `templates/cuentas/*.html`, `templates/resultados/admin/*.html` y `templates/resultados/_busqueda_form.html`, con `data-texto-trabajando` en cada botón principal con las claves `form.trabajando_*` de `contracts/mensajes.md` § 4 (agregarlas a `dominio/mensajes.py`), hasta pasar T132. **Antes de implementar, pedir al responsable la aprobación de esos textos** (marcados ‡ en el contrato) y quitar la marca ([003] FR-033, FR-034)
- [X] T139 Aplicar `truncate` + `title` + texto completo accesible a correos, períodos y motivos largos en `templates/ui/_menu_cuenta.html`, `templates/extracciones/inicio.html`, `templates/extracciones/extraccion.html` y `templates/extracciones/sorteo.html`, sin romper filas ni tarjetas a 360 px ([003] FR-030)
- [X] T140 [P] Escribir `e2e/recorridos/robustez.spec.ts`: sin conexión (`context.setOffline(true)`) al registrar una jugada, "Reintentar" tras reconectar crea **una** jugada; sesión vencida (borrar la cookie `sessionid`) con el formulario completo, ingresar y ver el formulario precargado sin enviarse; correo de 80 caracteres sin desbordes a 360 px ([003] quickstart #17, #18)

---

## Fase 17: Cierre de la Etapa 1

**Propósito**: comprobar el criterio de terminado de la Etapa 1 (plan § Etapa 1, CHK012) y fijar la línea base para la Etapa 2.

- [X] T141 Eliminar `estilos/legado.css` y su `@import` en `estilos/django.css` una vez que T127 dejó de usar sus clases; verificar con `npm run css` y una revisión visual de todas las pantallas ([003] RN-11)
- [X] T142 [P] Escribir `e2e/recorridos/sin-scripts.spec.ts` (solo proyecto `sin-scripts`): filtro y paginación de extracciones, confirmación de eliminación en página aparte, calendario del navegador, ingreso, registro de jugada, tema ([003] quickstart #19, NFR-007)
- [X] T143 [P] Escribir `e2e/recorridos/zoom-teclado.spec.ts`: con `document.documentElement.style.fontSize = "200%"` en cada pantalla, sin desplazamiento horizontal ni contenido oculto; recorrido solo con teclado de las tareas de SC-005 ([003] SC-005, SC-006)
- [X] T144 Escribir antes `e2e/recorridos/admin-sorteos.spec.ts` (tarea T205 adelantada: recorridos de administración de `specs/001-quini6-mvp/quickstart.md` contra Django, para que SC-004 cubra también esas pantallas; hallazgo D1). Ejecutar `npm run e2e` en todos los proyectos (`escritorio`, `movil`, `sin-scripts`, `oscuro`, `movimiento-reducido`) contra Django, `pytest` en SQLite y PostgreSQL 16 y `ruff check .`, todo en verde; corregir lo que falle ([003] SC-004, SC-006)
- [ ] T145 Hacer la revisión manual de `specs/003-modernizacion-ui-ux/quickstart.md` § 4 (escenarios 1 a 21) con teclado y NVDA, y registrar el resultado de cada escenario en `specs/003-modernizacion-ui-ux/verificacion-etapa1.md` ([003] SC-005, Const. VI)
- [X] T146 Medir con `npm run lhci` la **línea base definitiva** de R-24 sobre el Django de la Etapa 1 (perfil móvil, 5 corridas, mediana, datos de `preparar_e2e`) y registrarla en `specs/003-modernizacion-ui-ux/linea-base.md` § "Etapa 1" ([003] R-24, CHK015)
- [X] T147 Comparar los datos de Resultados, Estadísticas, Mis jugadas y un CSV de extracción contra `main` con los mismos datos y registrar en `verificacion-etapa1.md` que no hay diferencias de negocio ([003] NFR-009, SC-011, quickstart #21)
- [X] T148 Presentar al responsable el cierre de la Etapa 1 (criterio cumplido, `verificacion-etapa1.md`, `linea-base.md`) y registrar en `specs/003-modernizacion-ui-ux/plan.md` § "Revisión del checklist de migración" su decisión de continuar o no con las Etapas 2 y 3 (CHK039). **Si decide no continuar, pasar a la Fase 26 y ejecutar T232 a T238 omitiendo lo propio de las Etapas 2 y 3** (hallazgo G2: el informe de la Const. II y las pruebas finales no se saltan)

**Punto de control**: Etapa 1 entregada; la feature cumple HU-01 a HU-13.

---

## Fase 18: Historia de usuario 14 — Estructura común y convivencia (Etapa 2, pantalla 0) (Prioridad: P1 durante la renovación)

**Objetivo**: proyecto Next.js con la estructura común, el enrutador con vuelta automática, la sesión compartida, los avisos compartidos y "Volver al formulario".

**Prueba independiente**: guion de sesión compartida (T169) y guion de convivencia (T170) en el entorno de pruebas ([quickstart.md](quickstart.md) #22 a #28).

### Pruebas de la convivencia

- [X] T149 [P] [US14] Escribir `tests/api/test_avisos.py`: `GET /api/v1/avisos/` devuelve los mensajes de Django pendientes de la sesión con `tipo` y `texto` y los marca como leídos (un segundo GET devuelve `[]`); `POST /api/v1/avisos/` con `clave` del catálogo y variables agrega un mensaje que luego muestra una plantilla de Django; clave fuera del catálogo → 422; sin CSRF → 403; `no-store` ([003] R-31, FR-043)
- [X] T150 [P] [US14] Escribir `tests/integration/test_003_volver_formulario.py`: con `QUINI6_RUTAS_NEXT` que incluye `/mis-jugadas/*`, ingresar con un `pendiente` cuya ruta es `/mis-jugadas/nueva/` responde la página `templates/cuentas/volver_formulario.html` con `cuenta.volver_formulario_texto` y un formulario POST a `/mis-jugadas/nueva/` con el token y el botón "Volver al formulario"; la página no crea ninguna jugada; sin la ruta en `QUINI6_RUTAS_NEXT`, se mantiene el comportamiento de T135 ([003] AC-14.4, R-12)

### Implementación de la convivencia (Django y enrutador)

- [X] T151 [US14] Crear `quini6/api_avisos.py` con el router de `GET /avisos/` y `POST /avisos/` (nivel P, sobre `django.contrib.messages`) y registrarlo en `quini6/api.py`; agregar sus filas a `NIVEL_ESPERADO` de `tests/api/test_matriz_acceso_api.py`, hasta pasar T149 ([003] R-31)
- [X] T152 [US14] Crear `templates/cuentas/volver_formulario.html` y modificar `cuentas/views.py :: ingresar` para responderla cuando la ruta del `pendiente` coincide con un patrón de `settings.QUINI6_RUTAS_NEXT`, hasta pasar T150 ([003] AC-14.4)
- [X] T153 [US14] Completar `infra/Caddyfile` con las reglas 1 a 5 de `specs/003-modernizacion-ui-ux/contracts/rutas.md` § 3: `@django_siempre path /api/* /static/* /administracion/extracciones/*/csv/`; `@next_assets path /_next/*`; `@post_django` (`path {$QUINI6_RUTAS_NEXT}`, `method POST`, `query _interfaz=django`; decisión del 21/11/2026, I1 e I2); `@next path {$QUINI6_RUTAS_NEXT}` con `reverse_proxy {$QUINI6_NEXT_UPSTREAM} {$QUINI6_DJANGO_UPSTREAM} { lb_policy first; health_uri /; health_port 3000; health_interval 5s; fail_duration 10s }`; resto a Django; `header X-Interfaz next|django` en cada `handle`; `handle_errors` 502/503/504 que sirve `infra/no-disponible.html`; y la regla 4b de `QUINI6_RUTAS_NEXT_SIN_RESPALDO` (Next.js sin Django como segundo destino); además, crear el filtro `{% accion_formulario %}` en `quini6/templatetags/ui.py` (devuelve la dirección actual o la indicada con `?_interfaz=django`, conservando los demás parámetros) y usarlo en el `action` de **todos** los formularios POST de `templates/`, con una prueba en `tests/integration/test_003_formularios_validacion.py` que lo exija ([003] R-20, FR-044)
- [X] T154 [P] [US14] Crear `infra/no-disponible.html` estático (estilos en línea con los valores de `ui/tokens.css`, ambos temas por `prefers-color-scheme`, logotipo, `gral.no_disponible` y `pie.legal`, sin recursos externos) ([003] AC-14.6)

### Implementación de la estructura común (Next.js)

- [X] T155 [US14] Crear `frontend/` con `frontend/package.json` (`next@16`, `react@19`, `react-dom@19`, `typescript@5`, `tailwindcss@4`, `@tailwindcss/postcss@4`, `@radix-ui/*` que pida shadcn/ui, `class-variance-authority`, `tailwind-merge`, `clsx`, `tw-animate-css`, `lucide-react`, `sonner`, `motion`, `@tanstack/react-query@5`, `react-hook-form@7`, `zod@4`, `@hookform/resolvers`, `date-fns@4`, `react-day-picker`, `openapi-fetch`; dev: `openapi-typescript`, `vitest`, `@testing-library/react`, `jsdom`, `eslint`, `eslint-config-next`, `prettier`, `prettier-plugin-tailwindcss`; scripts `dev`, `build`, `start`, `lint`, `typecheck`, `test`, `api:tipos`), `frontend/tsconfig.json` (`strict: true`, `noUncheckedIndexedAccess: true`, alias `@/*` → `src/*`), `frontend/postcss.config.mjs`; agregar `"frontend"` a `workspaces` del `package.json` raíz ([003] R-18, R-22, R-26)
- [X] T156 [US14] Crear `frontend/next.config.ts`: `trailingSlash: true`, `output: "standalone"`, `poweredByHeader: false`, `experimental.serverActions.allowedOrigins = [QUINI6_ORIGEN_PUBLICO sin esquema]`, `experimental.staleTimes.dynamic = 0`, `headers()` con `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `X-Frame-Options: DENY` en todas las rutas ([003] R-18, R-19, R-32)
- [X] T157 [US14] Crear `frontend/src/app/globals.css` con `@import "tailwindcss"; @import "tw-animate-css"; @import "../../../ui/tokens.css"; @import "../../../ui/base.css"; @source "../../../ui/variantes.json";` y `frontend/src/components/ui/variantes.ts` que construye con `cva` las variantes `boton`, `insignia`, `aviso`, `toast` y `vacio` a partir de `ui/variantes.json` ([003] R-02, R-04)
- [X] T158 [US14] Inicializar shadcn/ui (`components.json` con `src/components/ui`) y agregar `button`, `dialog`, `alert-dialog`, `dropdown-menu`, `popover`, `calendar`, `skeleton`, `tooltip`; ajustar `button.tsx` para usar `variantes.ts` en lugar de sus clases por defecto ([003] R-04)
- [X] T159 [US14] Crear `frontend/src/api/servidor.ts` (`apiServidor()`: `openapi-fetch` con `baseUrl = process.env.QUINI6_API_INTERNA + "/api/v1"`, reenvía la cabecera `cookie` de `cookies()`, agrega `X-CSRFToken` desde la cookie `csrftoken` y `Origin = QUINI6_ORIGEN_PUBLICO`, `cache: "no-store"`) y `frontend/src/api/navegador.ts` (`apiNavegador`: `baseUrl = "/api/v1"`, `credentials: "same-origin"`, `X-CSRFToken`); ejecutar `npm run api:tipos -w frontend` (`openapi-typescript ../contratos/openapi.json -o src/api/esquema.d.ts`) y versionar `esquema.d.ts` ([003] R-17, R-19)
- [X] T160 [P] [US14] Crear `frontend/src/lib/mensajes.ts` (`msg(clave, valores)` desde `contratos/mensajes.json`, con tipo literal de las claves) y `frontend/src/lib/formato.ts` (`fecha`, `fechaHora` con `timeZone: "America/Argentina/Buenos_Aires"`, `pesos` desde `string` sin `parseFloat`, `porcentaje`, `dosDigitos`, `cantidad`) con `frontend/src/lib/formato.test.ts` que recorre `contratos/formatos-casos.json` ([003] contracts/formatos.md, R-13)
- [X] T161 [US14] Crear `frontend/src/app/layout.tsx` (`<html lang="es-AR" data-theme>` según la cookie `quini6_tema` leída con `cookies()`, `<main id="contenido" tabIndex={-1}>`, `QueryClientProvider`, `Toaster` de Sonner configurado según RN-09, `MotionConfig reducedMotion="user"`) y `frontend/src/app/template.tsx` (entrada con opacidad 200 ms con Motion) ([003] R-14, R-15, R-18)
- [X] T162 [P] [US14] Crear en `frontend/src/app/_componentes/`: `nav-bar.tsx` (servidor: sección activa con `aria-current`, logotipo, menú móvil cliente con `aria-expanded` y Escape; mismos textos, iconos y variantes que `templates/base.html`), `account-menu.tsx` (DropdownMenu con el correo truncado y "Salir" como formulario POST a `/salir/` con `csrfmiddlewaretoken`), `skip-link.tsx`, `theme-select.tsx` (formulario POST a `/preferencias/tema/`; con scripts, aplica `data-theme` y la cookie al instante), `pie.tsx` (`pie.legal`) y `avisos.tsx` (servidor: lee `GET /api/v1/avisos/` y los pasa a Sonner; sin scripts, `Callout` en `<main>`) ([003] AC-14.1, AC-14.3, FR-039, FR-043, contracts/componentes.md)
- [X] T163 [P] [US14] Crear `frontend/src/app/not-found.tsx` (`gral.pagina_inexistente`), `frontend/src/app/error.tsx` (`gral.error`) y `frontend/src/components/sin-permisos.tsx` (`admin.sin_permiso`), con el mismo diseño que `templates/404.html`, `500.html` y `403.html` ([003] FR-041)
- [X] T164 [US14] Crear `frontend/src/proxy.ts` (middleware de Next.js): para `/mis-jugadas/*` y `/administracion/*` sin cookie `sessionid` → redirección a `/ingresar/?next=<ruta>`; agrega `Cache-Control: no-store` a esas rutas; no decide permisos ([003] R-19, CHK006)
- [X] T165 [US14] Crear `frontend/src/lib/sesion.ts` (`obtenerSesion()` con `GET /api/v1/sesion/`; `exigirSesion(nivel)` que ante `401` redirige a `/ingresar/?next=…` y ante `403` muestra `sin-permisos.tsx`) y `frontend/src/lib/acciones.ts` (envoltorio de Server Actions: genera y reenvía `Idempotency-Key`, traduce `422` a errores por campo, ante `401` redirige a la pantalla "Ingresar" de Django con el `pendiente` (R-12), ante éxito agrega el aviso con `POST /api/v1/avisos/` y redirige) ([003] R-11, R-12, R-31, CHK011)
- [X] T166 [P] [US14] Configurar Storybook (`frontend/.storybook/main.ts` con `@storybook/nextjs-vite` y `@storybook/addon-a11y`, `preview.tsx` que importa `globals.css` y agrega el selector de tema) y el script `storybook` ([003] pedido § 7.3)
- [X] T167 [P] [US14] Agregar a `.github/workflows/ci.yml` el trabajo `frontend`: `npm ci`, `npm run api:tipos -w frontend` + `git diff --exit-code frontend/src/api/esquema.d.ts`, `lint`, `typecheck`, `test`, `build`, y `npx storybook build` ([003] R-17, R-23)
- [X] T168 [US14] Agregar a `compose.yaml` la variable `QUINI6_NEXT_UPSTREAM` y documentar en `specs/003-modernizacion-ui-ux/quickstart.md` § 2 que, para el entorno de pruebas, `QUINI6_RUTAS_NEXT` lleva la ruta de la pantalla en prueba ([003] R-20)

### Guiones de la convivencia

- [X] T169 [P] [US14] Escribir `e2e/recorridos/sesion-compartida.spec.ts` (prueba obligatoria de sesión compartida que el pedido de planificación numeraba "T208"; bloqueante): con `/administracion/extracciones/*` servida por Next.js en el entorno de pruebas, ingresar en Django, abrir la pantalla de Next.js sin volver a ingresar y con el mismo encabezado, volver a Django, salir y comprobar que Next.js redirige a "Ingresar"; con `sinjugadas@e2e.local`, "Sin permisos para acceder a esta sección" en ambas ([003] AC-14.1, AC-14.2, R-19)
- [X] T170 [P] [US14] Escribir `e2e/recorridos/hu14-convivencia.spec.ts`: aviso de una acción que termina en la otra aplicación (AC-14.3); sesión vencida en un formulario de Next.js → "Volver al formulario" → formulario precargado sin enviar (AC-14.4); detener Next.js (`QUINI6_E2E_DETENER_NEXT`) → la pantalla la sirve Django (AC-14.6); formulario de Django abierto antes de agregar su ruta a `QUINI6_RUTAS_NEXT` y recargar Caddy → se envía sin errores, y formulario de Next.js enviado **sin scripts** (proyecto `sin-scripts`) en una ruta conmutada → lo procesa Next.js (R-20) ([003] quickstart #25 a #28)
- [X] T171 [US14] Ejecutar T169 en el entorno de pruebas y no avanzar a la Fase 19 hasta que pase ([003] plan § Etapa 2 paso 2)

**Punto de control**: convivencia probada; las pantallas pueden migrarse.

---

## Fase 19: Historia de usuario 14 — Pantalla 1: Extracción histórica en Next.js

**Objetivo**: Extracción histórica (inicio, detalle, sorteo extraído, eliminar) en Next.js con el mismo comportamiento que la Etapa 1.

**Prueba independiente**: los guiones de HU-01 a HU-04, HU-08, HU-09 y HU-14 pasan contra Next.js en el entorno de pruebas.

- [X] T172 [US14] Completar en `specs/003-modernizacion-ui-ux/contracts/api.md` los DTO `ExtraccionResumen`, `Extraccion`, `Avance`, `SorteoExtraido` y `Atajo` campo por campo (nombre, tipo, nulabilidad, origen en `extracciones/consultas.py`) y obtener la aprobación del responsable antes de seguir (compuerta "contrato primero", R-32, CHK003)
- [X] T173 [P] [US14] Escribir `tests/api/test_extracciones_api.py`: las seis operaciones de `contracts/api.md` § Extracción histórica; matriz de acceso (filas en `NIVEL_ESPERADO`); CSRF; `Idempotency-Key` en iniciar y eliminar; `409` con `existente` (RN-03) y con la propia en curso ([002] AC-1.11); `422` del período con `errores` por campo; paridad con la vista HTML (mismos datos, etiquetas y mensajes para el mismo caso, NFR-009); `GET /periodos/atajos/?formulario=extraccion` nivel A ([003] contracts/api.md)
- [X] T174 [US14] Crear `extracciones/api.py` con esas operaciones (delgadas: `consultas` → dominio → `servicios`) y `GET /periodos/atajos/` en `quini6/api_periodos.py` (nivel según `formulario`); registrar en `quini6/api.py`; `python manage.py exportar_contratos` y `npm run api:tipos -w frontend`, hasta pasar T173 ([003] R-16)
- [X] T175 [P] [US14] Crear en `frontend/src/components/` `status-badge.tsx`, `callout.tsx`, `empty-state.tsx`, `back-link.tsx`, `field.tsx`, `skeleton` (de shadcn), `pagination.tsx` (enlaces) y `data-table.tsx` (TanStack Table en modo manual, encabezados ordenables como enlaces con `aria-sort`, tarjetas debajo de 768 px, fila entera enlazada salvo el menú) siguiendo `contracts/componentes.md`, con su historia en `*.stories.tsx` (todos los estados) y prueba `*.test.tsx` ([003] FR-041)
- [X] T176 [P] [US14] Crear `frontend/src/components/action-menu.tsx` (DropdownMenu con nombre `ext.acciones`), `confirm-dialog.tsx` (AlertDialog con foco inicial en "Cancelar") y `progress-panel.tsx` (cliente: `useQuery(["extraccion", id, "avance"], …, { refetchInterval: (q) => q.state.data?.en_curso ? 3000 : false })`, al terminar invalida el listado y muestra el aviso con Sonner), con historias y pruebas ([003] R-10, R-18)
- [X] T177 [P] [US14] Crear `frontend/src/components/date-field.tsx` y `date-range-picker.tsx` (servidor renderiza `<input type="date">`; al hidratar, campo con máscara `dd/mm/aaaa` + `Popover` con `Calendar` de shadcn/ui, `locale={es}`, `weekStartsOn={1}`, `mode="range"` en el período, `disabled` fuera de `min`/`max`, mismo ancho reservado; atajos como enlaces `?atajo=` que con scripts completan los campos) y `frontend/src/lib/esquemas/periodo.ts` (Zod con los mensajes de `mensajes.json`: `fecha.inexistente`, `fecha.fin_anterior`, `fecha.falta_inicio`, `fecha.falta_fin`), con historias y pruebas ([003] R-07, R-13)
- [X] T178 [US14] Crear `frontend/src/app/administracion/extracciones/page.tsx` (servidor: listado con filtro, orden y paginación de `searchParams`, formulario de inicio con `date-range-picker`, `progress-panel` de la propia en curso), `acciones.ts` (Server Actions `iniciarExtraccion` y `eliminarExtraccion` con `lib/acciones.ts`; formularios con `useActionState` + React Hook Form `mode: "onBlur"` + `periodo.ts`), `[id]/page.tsx` (detalle con insignia, explicación, resumen de RN-33, `ext.ninguna_fuente`, enlace al CSV de Django), `[id]/sorteos/[numero]/page.tsx` y `[id]/eliminar/page.tsx` (confirmación completa, sin scripts) ([003] FR-041)
- [X] T179 [US14] Crear la ruta interceptada `frontend/src/app/administracion/extracciones/@modal/(.)[id]/eliminar/page.tsx` (muestra `confirm-dialog` con el mismo contenido) y `@modal/default.tsx`, y el `layout.tsx` del segmento que recibe el slot `modal` ([003] R-18)
- [X] T180 [US14] Ejecutar contra Next.js en el entorno de pruebas (`QUINI6_RUTAS_NEXT="/administracion/extracciones/ /administracion/extracciones/*"`) los guiones `hu01-estados`, `hu02-eliminar`, `hu03-avance`, `hu04-fechas` (partes de extracción), `hu08-vacios`, `hu09-tablas`, `hu13-acabado`, `sin-scripts`, `sesion-compartida` y `hu14-convivencia`, más `npm run lhci` contra la línea base de T146, y probar la reversa (quitar la ruta y recargar Caddy); corregir hasta que todo pase ([003] R-27, criterio de terminado)

---

## Fase 20: Historia de usuario 14 — Pantalla 2: Estadísticas en Next.js

**Prueba independiente**: los guiones de HU-04 (estadísticas), HU-07, HU-08 y HU-10 pasan contra Next.js en el entorno de pruebas.

- [X] T181 [US14] Completar en `contracts/api.md` el DTO `Frecuencias` campo por campo y aprobarlo (compuerta R-32)
- [X] T182 [P] [US14] Escribir `tests/api/test_estadisticas_api.py`: `GET /estadisticas/` con los mismos casos que `tests/integration/test_us6_estadisticas.py` (mismos valores, porcentajes como cadena decimal, sorteos sin información, consulta anterior ante error), `422` con `errores`, `GET /periodos/atajos/?formulario=estadisticas` nivel P con "Todo el historial" ([003] NFR-009)
- [X] T183 [US14] Crear `estadisticas/api.py` (delgada sobre `dominio/estadisticas.py`) y registrarla; exportar contratos y tipos, hasta pasar T182
- [X] T184 [P] [US14] Crear `frontend/src/components/frequency-chart.tsx` como **componente de servidor** que genera el SVG con el mismo cálculo de `estadisticas/views.py :: _grafico` (ancho de barra 10, alto 120, margen inferior 22, rótulo cada 5 y en el número consultado), `role="img"`, `<title>`/`<desc>`, colores de tokens; `frequency-chart.test.tsx` con los mismos casos que el cálculo de Django; historia en Storybook ([003] R-18, CHK022)
- [X] T185 [US14] Crear `frontend/src/app/estadisticas/page.tsx` (servidor: filtros con `date-range-picker` y tres atajos, bloque "Consultar un número" con validación Zod `rango_00_45`, `callout` `info` con `est.leyenda`, `frequency-chart`, tabla ordenable con `data-table`) ([003] FR-041)
- [X] T186 [US14] Ejecutar contra Next.js en el entorno de pruebas `hu04-fechas` (estadísticas), `hu07-estadisticas`, `hu08-vacios`, `hu10-avisos`, `sin-scripts` y `lhci`; probar la reversa ([003] R-27)

---

## Fase 21: Historia de usuario 14 — Pantalla 3: Mis jugadas en Next.js

**Prueba independiente**: los guiones de registro y consulta de jugadas, HU-08, HU-10 y `robustez` pasan contra Next.js en el entorno de pruebas.

- [X] T187 [US14] Completar en `contracts/api.md` los DTO `JugadaResumen`, `Jugada` (con comparación por sorteo y modalidad, importes como cadena decimal) y `SorteoDisponible`, y aprobarlos (compuerta R-32)
- [X] T188 [P] [US14] Escribir `tests/api/test_jugadas_api.py`: las seis operaciones; jugada ajena o inexistente → `404` idéntico; `409` `jugada.duplicada` con `confirmar`; `409` `jugada.fija`; `Idempotency-Key`; `401` con `pendiente` en registrar y modificar (R-12); paridad con `tests/integration/test_us4_jugadas.py` y `test_us5_comparacion.py` ([003] contracts/api.md, Const. IV)
- [X] T189 [US14] Crear `jugadas/api.py` (filtrando siempre por `usuario=request.user`) y registrarla; exportar contratos y tipos, hasta pasar T188
- [X] T190 [P] [US14] Crear `frontend/src/components/selector-numeros.tsx` (mismo comportamiento que `static/js/selector-numeros.js`: seis números de 00 a 45, mensajes `jugada.faltan`, `jugada.repetido`, `jugada.fuera_de_rango`; sin scripts, casillas del formulario) con historia y prueba ([003] FR-041)
- [X] T191 [US14] Crear `frontend/src/app/mis-jugadas/page.tsx`, `nueva/page.tsx`, `[id]/page.tsx`, `[id]/editar/page.tsx`, `[id]/eliminar/page.tsx` y `acciones.ts` (registrar, modificar con confirmación de duplicada, eliminar; con `lib/acciones.ts`), con `empty-state` `vacio.jugadas` y `back-link` `nav.volver_jugadas` ([003] FR-041)
- [X] T192 [US14] Ejecutar contra Next.js en el entorno de pruebas los guiones de jugadas, `hu08-vacios`, `hu10-avisos`, `robustez`, `hu14-convivencia` (sesión vencida → "Volver al formulario"), `sin-scripts` y `lhci`; probar la reversa ([003] R-27)

---

## Fase 22: Historia de usuario 14 — Pantalla 4: Resultados y búsqueda en Next.js

**Prueba independiente**: los guiones de consulta pública, búsqueda, HU-08 y HU-09 pasan contra Next.js; presupuesto de pantallas públicas (≤ 120 kB de JavaScript inicial).

- [X] T193 [US14] Completar en `contracts/api.md` los DTO `SorteoResumen` y `SorteoPublico` (modalidades, números sorteados, premios con `Dato` y estado de publicación, avisos de corrección y revisión, fuente) y aprobarlos (compuerta R-32)
- [X] T194 [P] [US14] Escribir `tests/api/test_resultados_api.py`: las cuatro operaciones con los casos de `tests/integration/test_us1_consulta.py` y `test_no_publicado.py` (nada no publicado se expone), `no-cache`, paridad de datos ([003] NFR-009, Const. VIII)
- [X] T195 [US14] Crear `resultados/api.py` (lectura pública) y registrarla; exportar contratos y tipos, hasta pasar T194
- [X] T196 [US14] Crear `frontend/src/app/page.tsx` (inicio), `resultados/page.tsx`, `resultados/buscar/page.tsx` y `resultados/[numero]/page.tsx` como componentes de servidor sin JavaScript de cliente salvo el encabezado, con `empty-state` `vacio.resultados` y accesos de administración solo si la sesión es de administración ([003] FR-041, FR-026)
- [X] T197 [US14] Ejecutar contra Next.js en el entorno de pruebas los guiones de resultados, `hu05-navegacion`, `hu08-vacios`, `hu09-tablas`, `sin-scripts` y `lhci` (presupuesto público); probar la reversa ([003] R-24, R-27)

---

## Fase 23: Historia de usuario 14 — Pantalla 5: Ingresar y Crear cuenta en Next.js

**Prueba independiente**: los guiones de HU-06, `sesion-compartida`, `robustez` y `hu12-tema` pasan contra Next.js.

- [X] T198 [P] [US14] Escribir `tests/api/test_cuentas_api.py`: `POST /sesion/` (credenciales incorrectas sin revelar si el correo existe, bloqueo tras 5 fallos con `cuenta.bloqueada`, `pendiente`), `DELETE /sesion/`, `POST /cuentas/` (mensajes de [001] AC-3.2 y AC-3.3 reescritos, `Idempotency-Key`), todos con CSRF; usan `cuentas.servicios` igual que las vistas HTML ([003] CHK026, FR-020)
- [X] T199 [US14] Agregar a `cuentas/api.py` `POST /sesion/`, `DELETE /sesion/` y `POST /cuentas/`; exportar contratos y tipos, hasta pasar T198
- [X] T200 [P] [US14] Crear `frontend/src/components/password-field.tsx` (mostrar/ocultar con `aria-pressed` y anuncio) con historia y prueba ([003] AC-6.2)
- [X] T201 [US14] Crear `frontend/src/app/ingresar/page.tsx`, `registrarse/page.tsx` y `acciones.ts` (Server Actions que llaman a `POST /sesion/` y `POST /cuentas/` y **reenvían al navegador las `Set-Cookie`** de Django; con `pendiente`, muestran el formulario destino precargado dentro de Next.js), y reemplazar "Salir" de `account-menu.tsx` por una Server Action que llama a `DELETE /sesion/` ([003] R-19, FR-040)
- [X] T202 [US14] Crear `frontend/src/app/preferencias/tema/route.ts` (POST con la misma validación de `next` y la misma cookie que `quini6/tema.py`) y `frontend/src/app/salir/route.ts` (POST → `DELETE /api/v1/sesion/` y 303 a `/`) ([003] R-14)
- [X] T203 [US14] Ejecutar contra Next.js en el entorno de pruebas `hu06-ingreso`, `sesion-compartida`, `robustez`, `hu12-tema`, `hu14-convivencia` y `sin-scripts`; probar la reversa ([003] R-27)

---

## Fase 24: Historia de usuario 14 — Pantalla 6: Administración de sorteos en Next.js (P-03 aprobado el 21/11/2026)

**Prueba independiente**: los guiones de carga, publicación y corrección de sorteos de [001] pasan contra Next.js.

- [X] T204 [US14] Especificar en `contracts/api.md` § "Administración de sorteos" una operación por cada vista de `resultados/urls_admin.py` (listado, nuevo, panel, modificar, historial, números, premios, observar, resolver, publicar, revisión, quitar revisión, corregir) con sus DTO, niveles (A) y mensajes, y obtener la aprobación del responsable
- [X] T205 [P] [US14] Revisar `e2e/recorridos/admin-sorteos.spec.ts` (escrito en T144) y ampliarlo con todo lo que se especificó en T204, ejecutándolo contra Django antes de migrar ([003] FR-041)
- [X] T206 [P] [US14] Escribir `tests/api/test_admin_sorteos_api.py` con los casos de `tests/integration/test_us2_admin.py`, `test_us7_correccion.py` y `test_servicios_resultados.py` (mismos resultados, solo administración, CSRF, idempotencia al crear) (después de T204)
- [X] T207 [US14] Crear `resultados/api_admin.py` y registrarla; exportar contratos y tipos, hasta pasar T206
- [X] T208 [US14] Crear `frontend/src/app/administracion/concursos/` con una página por vista de administración y sus Server Actions, reutilizando los componentes existentes ([003] FR-041)
- [X] T209 [US14] Ejecutar contra Next.js en el entorno de pruebas `admin-sorteos`, `hu04-fechas` (carga de sorteo), `hu05-navegacion`, `hu08-vacios`, `hu09-tablas`, `hu11-lenguaje` y `sin-scripts`; probar la reversa ([003] R-27)

---

## Fase 25: Historia de usuario 14 — Etapa 3: conmutación, estabilización y retiro

**Objetivo**: conmutar cada pantalla para todo el público con reversa disponible, estabilizarla 14 días y retirar sus plantillas con aprobación del responsable (R-28).

**Prueba independiente**: SC-012 por pantalla y [quickstart.md](quickstart.md) #22 a #30 en producción.

- [ ] T210 [US14] Activar Sentry (P-01 aprobado el 21/11/2026): `sentry-sdk` en `pyproject.toml` (`prod`) con inicialización en `quini6/settings.py` solo si `QUINI6_SENTRY_DSN` tiene valor (`send_default_pii=False`, `traces_sample_rate=0.1`, `before_send` que elimina correos, cookies, cabeceras de autenticación y cuerpos de formularios), y `@sentry/nextjs` en `frontend/` con la misma configuración y sin reproducción de sesiones; crear la cuenta y el DSN con el responsable y configurarlo solo en producción ([003] R-25)
- [ ] T211 [US14] Medir en producción, para cada pantalla, la tasa de respuestas 5xx de Django en las dos semanas previas a su conmutación y registrarla en `plan.md` § Registro de conmutaciones (referencia del umbral de R-28)
- [ ] T212 [US14] Conmutar las pantallas 0 + 1 (Extracción histórica): agregar sus patrones de `contracts/rutas.md` § 3 a `QUINI6_RUTAS_NEXT` en producción un martes o jueves entre las 10 y las 12, `caddy reload`, ejecutar `sesion-compartida` y `hu14-convivencia` contra producción con una cuenta de prueba, y registrar la fecha en `plan.md` § Registro de conmutaciones ([003] R-28)
- [ ] T213 [US14] Estabilizar las pantallas 0 + 1 durante 14 días con los umbrales de R-28 (reversa inmediata en menos de 15 minutos ante una tarea principal imposible, un dato o permiso distinto o una incidencia crítica de accesibilidad; registrar cada reversa con fecha y motivo) y registrar la fecha de estabilización cumplida
- [ ] T214 [US14] Con la **aprobación explícita del responsable** registrada en `plan.md`, retirar de Django las vistas HTML, rutas, plantillas y fragmentos exclusivos de Extracción histórica (`extracciones/views.py` salvo `descargar_csv`, `extracciones/urls.py` salvo la ruta del CSV, `templates/extracciones/`), mover sus patrones a `QUINI6_RUTAS_NEXT_SIN_RESPALDO` y adaptar las pruebas de integración HTML de esa pantalla a la API (las de dominio y CSV no cambian) ([003] R-28, CHK033)
- [ ] T215 [US14] Conmutar la pantalla 2 (Estadísticas) como en T212
- [ ] T216 [US14] Estabilizar la pantalla 2 como en T213
- [ ] T217 [US14] Retirar la pantalla 2 de Django como en T214 (`estadisticas/views.py`, `estadisticas/urls.py`, `templates/estadisticas/`), con aprobación del responsable
- [ ] T218 [US14] Conmutar la pantalla 3 (Mis jugadas) como en T212
- [ ] T219 [US14] Estabilizar la pantalla 3 como en T213
- [ ] T220 [US14] Retirar la pantalla 3 de Django como en T214 (`jugadas/views.py`, `jugadas/urls.py`, `templates/jugadas/`, `static/js/selector-numeros.js`), con aprobación del responsable
- [ ] T221 [US14] Conmutar la pantalla 4 (Resultados y búsqueda) como en T212
- [ ] T222 [US14] Estabilizar la pantalla 4 como en T213
- [ ] T223 [US14] Retirar la pantalla 4 de Django como en T214 (`resultados/views_publicas.py`, `resultados/urls.py`, `templates/resultados/*.html` públicas), con aprobación del responsable
- [ ] T224 [US14] Conmutar la pantalla 5 (Ingresar y Crear cuenta, `/salir/`, `/preferencias/*`) como en T212 y quitar la página "Volver al formulario" (`templates/cuentas/volver_formulario.html`) al estabilizarse, porque el ingreso y los formularios ya viven en la misma aplicación ([003] R-12)
- [ ] T225 [US14] Estabilizar la pantalla 5 como en T213
- [ ] T226 [US14] Retirar la pantalla 5 de Django como en T214 (`cuentas/views.py`, `cuentas/urls.py`, `templates/cuentas/`, `quini6/tema.py` vista HTML), con aprobación del responsable; el procesamiento del formulario pendiente queda solo en la API
- [ ] T227 [US14] Conmutar la pantalla 6 (Administración de sorteos) como en T212
- [ ] T228 [US14] Estabilizar la pantalla 6 como en T213
- [ ] T229 [US14] Retirar la pantalla 6 de Django como en T214 (`resultados/views_admin.py`, `resultados/urls_admin.py`, `templates/resultados/admin/`), con aprobación del responsable
- [ ] T230 [US14] Al retirar la última pantalla: quitar `templates/base.html`, `templates/ui/`, `templates/_campo.html`, las páginas de error HTML de Django salvo una respuesta mínima, `static/js/`, `estilos/django.css`, `scripts/vendor.mjs`, `scripts/iconos.mjs`, las dependencias `htmx.org`, `alpinejs`, `@alpinejs/*`, `cally`, `lucide-static`, `@tailwindcss/cli` del `package.json` raíz y los scripts `css`, `css:watch`, `vendor`, `iconos`; mantener la API, el CSV, el trabajador y los comandos; `pytest` y `npm run e2e` en verde ([003] R-28)

---

## Fase 26: Cierre final y aspectos transversales

- [X] T231 [P] Revisar `contracts/api.md` contra `contratos/openapi.json` operación por operación y corregir cualquier diferencia ([003] R-16)
- [X] T232 [P] Actualizar `specs/003-modernizacion-ui-ux/quickstart.md` con los comandos definitivos (scripts reales, variables usadas) y quitar lo que ya no aplique tras el retiro
- [ ] T233 Hacer la auditoría final con NVDA y solo teclado de todas las pantallas en ambos temas y anchos, y registrar el resultado en `specs/003-modernizacion-ui-ux/verificacion-final.md` ([003] SC-004, SC-005)
- [X] T234 Medir SC-004, SC-006, SC-007, SC-009, SC-010, SC-011 y SC-012 y registrar los valores en `verificacion-final.md`; dejar constancia de que SC-001 a SC-003 y SC-008 requieren las pruebas con usuarios que organiza el responsable (spec, Supuestos)
- [X] T235 Ejecutar `ruff check .`, `pytest` (SQLite y PostgreSQL 16), `npm run lint -w frontend`, `npm run typecheck -w frontend`, `npm run test -w frontend`, `npm run test -w ui`, `npm run e2e` y `npx storybook build`, todo en verde
- [X] T236 Informar al responsable qué requisitos se implementaron, cómo se verifican desde la interfaz y qué desviaciones o criterios quedan pendientes (Const. II)
- [X] T237 [P] Actualizar `specs/README.md` (si existe; si no, crearlo con el estado de 001, 002 y 003) con el estado de la feature 003
- [X] T238 **Mantenimiento**: actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec ("[003] …"), solo información transversal y relevante para futuras features: stack y estructura (`ui/`, `frontend/`, `e2e/`, `contratos/`, `infra/`); catálogo único de mensajes en `dominio/mensajes.py` exportado a `contratos/mensajes.json`; tokens únicos en `ui/tokens.css` (Figma manda) y variantes en `ui/variantes.json`; API v1 con Django Ninja, Problem Details e importes como cadena decimal; mismo origen sin CORS y sesión de Django compartida; propiedad de rutas en Caddy con `QUINI6_RUTAS_NEXT` y vuelta automática; idempotencia con `clave_idempotencia`/`Idempotency-Key` en la sesión; formulario pendiente firmado; guion E2E único por historia con roles y textos accesibles; formatos es-AR por `contracts/formatos.md`. Reemplazar las líneas que esta feature deja sin efecto ("Sin SPA ni frameworks JS", "SQLite en desarrollo", "Dependencias cerradas", "gráfico SVG generado en el servidor" pasa a "también en Next.js", el arranque en local con Node y compose) y quitar las que dejen de ser ciertas tras el retiro de plantillas. Si la Etapa 2 no se ejecutó (T148), registrar solo las decisiones de la Fase 0 y la Etapa 1

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Fase 1 (Preparación)**: sin dependencias. T001 bloquea las tareas "(requiere T001)".
- **Fase 2 (Base)**: depende de la Fase 1. **Bloquea todas las historias.**
- **Fases 3 a 7 (P1: US1 a US5)**: dependen de la Fase 2. US1 → US2 → US3 comparten `templates/extracciones/inicio.html` y `extracciones/views.py`, por eso van en ese orden; US4 y US5 pueden ir en paralelo con ellas (archivos distintos salvo `templates/extracciones/inicio.html` en T075, que se hace después de T050).
- **Fases 8 a 13 (P2: US6 a US11)**: dependen de la Fase 2. US7 usa `_periodo.html` (US4); US9 amplía el listado de US1; US10 usa la región de avisos de US3 (T061); **US11 conviene hacerla al final de las P2**, porque toca las plantillas de todas las demás.
- **Fases 14 y 15 (P3: US12, US13)**: dependen de la Fase 2; US13 (T127) después de las P1 y P2.
- **Fase 16 (Robustez)**: depende de US4 (validador T071), US3 (trabajando T060) y US6 (ingreso).
- **Fase 17 (Cierre de la Etapa 1)**: depende de todas las anteriores. T148 decide si se continúa.
- **Fase 18 (Convivencia)**: depende de T148 = continuar. **T171 (sesión compartida) bloquea las Fases 19 a 24.**
- **Fases 19 a 24 (pantallas)**: en orden 1 → 6 (R-27); cada una empieza por la compuerta de contrato (T172, T181, T187, T193, T204). La Fase 24 requiere P-03.
- **Fase 25 (Etapa 3)**: cada conmutación depende de la fase de su pantalla; cada retiro, de su estabilización y de la aprobación del responsable; T230 de todos los retiros.
- **Fase 26 (Cierre final)**: depende de todo lo que se haya ejecutado; si no se continúa tras T148, se ejecutan T232 a T238 sin lo propio de las Etapas 2 y 3. T238 es siempre la última tarea.

### Dependencias entre historias

| Historia | Depende de | Probar por separado |
|----------|------------|---------------------|
| US1 | Base | Sí |
| US2 | US1 (fila del listado) | Sí |
| US3 | US1 (etiqueta y listado) | Sí |
| US4 | Base | Sí |
| US5 | Base | Sí |
| US6 | Base (validador de US4 para la validación previa) | Sí |
| US7 | US4 (`_periodo.html`) | Sí |
| US8 | Base (filtro de US1 para la variante "sin resultados") | Sí |
| US9 | US1 | Sí |
| US10 | US3 (`_avisos.html`) | Sí |
| US11 | Todas las anteriores (toca sus plantillas) | Sí |
| US12 | Base | Sí |
| US13 | P1 y P2 | Sí |
| US14 | Etapa 1 completa (T148) | Sí, por pantalla |

### Dentro de cada historia

Pruebas primero (deben fallar) → dominio → consultas y servicios → vistas → plantillas y componentes → guion E2E.

---

## Ejemplos de trabajo en paralelo

### Fase 2 (Base)

```text
T011 test_mensajes_catalogo.py · T012 test_templatetags_ui.py · T013 test_idempotencia.py
T014 tests/api/test_sesion.py · T015 test_problemas.py · T016 test_contratos_exportados.py · T017 test_matriz_acceso_api.py
T018 ui/tokens.css + base.css · T019 ui/variantes.json + estilos/django.css · T021 iconos   (T020 después de T018)
T033 arnés e2e · T035 lighthouserc.json
```

### Historia 1

```text
T037 test_etiqueta.py · T038 test_003_us1_estados.py   (juntas, antes de implementar)
T041 _insignia_estado.html  (en paralelo con T039/T040)
T044 hu01-estados.spec.ts
```

### Historia 4

```text
T064 test_periodos.py · T065 test_003_us4_fechas.py
T068 _campo_fecha.html, luego T069 _periodo.html (ambas tocan static/js/ui.js)
```

### Historia 11

```text
T113 cuentas · T114 jugadas + dominio · T115 resultados + estadísticas · T116 extracciones
T117 plantillas de resultados · T118 resto de plantillas   (todas en paralelo; archivos distintos)
```

### Fase 18 (Convivencia)

```text
T149 test_avisos.py · T150 test_003_volver_formulario.py
T154 no-disponible.html · T160 mensajes.ts + formato.ts · T162 estructura común · T163 páginas de error · T166 Storybook · T167 CI
T169 sesion-compartida.spec.ts · T170 hu14-convivencia.spec.ts
```

---

## Estrategia de implementación

### MVP primero (solo la Historia 1)

1. Fase 1 y Fase 2.
2. Fase 3 (US1): etiquetas de estado y filtro.
3. **Detenerse y validar**: [quickstart.md](quickstart.md) #1 y #2 con un administrador. Es el problema de mayor riesgo operativo de la spec.

### Entrega incremental (Etapa 1)

1. Base → US1 → US2 → US3: Extracción histórica completa (las tres historias P1 de mayor riesgo).
2. US4 y US5: fechas y navegación (completan las P1 = MVP de la Etapa 1).
3. US6 a US10 en cualquier orden respetando las dependencias; **US11 al final de las P2**.
4. US12 y US13 (P3) si entran en la etapa, sin bloquear el cierre (CHK012).
5. Fase 16 (robustez) y Fase 17 (cierre): criterio de terminado y decisión del responsable (T148).

### Etapas 2 y 3 (si el responsable decide continuar)

1. Fase 18 y su compuerta T171 (sesión compartida).
2. Una pantalla por vez (Fases 19 a 24), cada una con su compuerta de contrato y su criterio de terminado.
3. Fase 25: conmutar → estabilizar 14 días → retirar con aprobación, pantalla por pantalla.
4. Fase 26 y T238 (CLAUDE.md).

### Con varias personas

Terminada la Base: una persona en Extracción histórica (US1 → US2 → US3 → US9), otra en US4 → US7, otra en US5 → US6 → US10 → US12; US11 la hace una sola persona al final, coordinando con las demás.

---

## Notas

- [P] = archivos distintos, sin dependencias pendientes.
- [USn] vincula cada tarea con su historia para la trazabilidad (Const. II).
- Una tarea no termina porque compila o pasan las pruebas: debe cumplir sus criterios verificables desde la interfaz (Const., Flujo de trabajo).
- Hacer commit al terminar cada tarea o grupo lógico; detenerse en cada punto de control para validar la historia por separado.
- Evitar: tareas vagas, dos tareas sobre el mismo archivo marcadas [P], dependencias entre historias que rompan su independencia.
