# QUINI_6 — memoria técnica

**Qué es**: web pública e informativa del Quini 6 (Argentina) para consultar resultados, premios y estadísticas sin registro, y para que usuarios con cuenta sigan sus jugadas comparadas con los resultados oficiales.

## Stack y decisiones vigentes (ver `specs/*/plan.md` y `research.md`)
- **Django 5.2 LTS + Python 3.12** (dominio, API v1, plantillas mientras dure la convivencia) + **[003] Next.js 16 / React 19** en `frontend/` (componentes de servidor por defecto, Server Actions, shadcn/ui, TanStack Query solo para datos en vivo). Toda página funciona **sin scripts** (NFR-007); los scripts solo mejoran.
- Dependencias cerradas: `Django`, `gunicorn`, `whitenoise`, `django-ninja`, `psycopg[binary]` y `sentry-sdk` (prod) · dev: `pytest`, `pytest-django`, `ruff`; las de Node, en los `package.json` (`ui/`, `frontend/`, `e2e/`) según [003] research.md. **No agregar otras** sin justificarlo en el plan.
- BD: **PostgreSQL 16** en producción y en el entorno paritario (`docker compose up -d db`); **SQLite** para `pytest` y los recorridos E2E (`QUINI6_DB_NAME` vacía → SQLite; `QUINI6_DB_SQLITE=e2e.sqlite3`). Sin funciones exclusivas de un motor.
- Reglas de negocio en **`dominio/`: funciones puras sin Django**; errores como valores, no excepciones. Vistas: cargan datos → llaman al dominio → renderizan.
- Resultados como **versiones inmutables por bloque** (`VersionNumeros`, `VersionPremios`) + `RegistroCambio` de solo agregado. Comparaciones y estadísticas **no se guardan**: se calculan en cada consulta.
- Importes siempre `Decimal` / `DecimalField(16,2)`; nunca `float`.
- Auth: `cuentas.Usuario` con correo como identificador; bloqueo propio (5 fallos → 15 min); sesión 30 min de inactividad; `no-store` en páginas privadas. Admin = booleano + decorador `administrador_requerido`; se otorga con `manage.py otorgar_admin|quitar_admin`. **`django.contrib.admin` deshabilitado.**
- Config y secretos por variables de entorno `QUINI6_*` (lector propio de `.env` en `settings.py`); `.env` nunca se versiona.
- Desde 360 px, contraste AA, ambos temas; gráfico de estadísticas en SVG generado en el servidor (también en Next.js, como componente de servidor; sin bibliotecas de gráficos).
- [002] Tareas largas fuera de la solicitud web: proceso trabajador `manage.py procesar_extracciones` que usa la base como cola; **una sola instancia** (garantiza el ritmo por sitio) y reanuda lo que quedó en curso.
- [002] Fuentes externas (F1, F2, F3) solo con `urllib` + `html.parser`, sin dependencias nuevas; fichas inmutables en `extracciones/fuentes/fichas.py` (cambiarlas exige spec aprobada); los intérpretes solo extraen textos y el dominio los interpreta.
- [002] Ritmo fijo de **una consulta cada 2 s por sitio** (`INTERVALO_SEGUNDOS`, constante en el código, no configurable); sin reintentos ni evasión ante 403/429/anti-robots; límite de espera de 10 s.
- [002] Datos de fuentes con el tipo `Dato` de `dominio/extraccion/tipos.py` (valor · "No disponible" · "No corresponde" · "Sin determinar"), guardado en JSON con su estado explícito: un dato desconocido nunca es `null`→0.
- [002] El CSV de `extracciones` es el **contrato de la futura ingesta** (`specs/002-extraccion-historica-csv/contracts/csv.md`, v3.0): versión por fila y solo se agregan columnas al final; quitar o cambiar una columna es un cambio mayor que exige aprobación y sube la versión (los archivos guardados conservan la suya). La extracción nunca escribe en `resultados` ni `jugadas` (prueba estructural de imports).
- [002] `QUINI6_FUENTE_F1_URL`/`F2`/`F3` reemplazan la dirección base de las fuentes **solo** para el servidor de fuentes de prueba (`python -m tests.fuentes_prueba.servidor --escenario <nombre>`); vacías = sitios reales.
- [002] Prioridad de fuentes en `ORDEN_FUENTES`: F2 numerosganadores → F3 quiniya → F1 quini-6-resultados (respaldo y desempate: se consulta si falta un dato o F2 y F3 difieren, con la fecha que ellas informan; "No requerida" si no hace falta). Si 2 de 3 coinciden, ese valor gana (nota informativa, no inconsistencia). Los identificadores F1–F3 no indican la prioridad.
- [002] Todo valor calculado o corregido por el sistema lleva su marca (`DatoConsolidado.calculo`, notas informativas) y nunca se presenta como publicado. La extracción nombra las modalidades con `nombre_modalidad` ("Tradicional", "Pozo Extra"…), distinto de `Modalidad.nombre` de [001].
- [002] Acciones por fila de un listado: menú ⋮ con `<details class="menu-acciones">` (sin JS) y eliminación con página de confirmación GET + POST → 303 con mensaje; solo se eliminan entidades que ningún proceso está usando (p. ej. extracciones terminadas).
- [002] Campos de fecha del usuario como `<input type="date">` (calendario nativo, `max` cuando corresponda); el dominio acepta `AAAA-MM-DD` y `dd/mm/aaaa`, y el widget reconvierte a `AAAA-MM-DD` al volver a mostrar el formulario. No forzar el calendario con `showPicker()` al hacer clic: en Chrome/Edge toma las teclas y no deja escribir la fecha (D-27).
- [002] Las pruebas nunca consultan internet: `tests/extraccion_falsos.py` (`ClienteHttpFalso`, páginas armadas desde las copias reales de `tests/fixtures/fuentes/`).

- [003] Estructura: `ui/` (diseño común: `tokens.css` —Figma manda—, `variantes.json`, `base.css`, `dominio.css`, importados por Django y Next.js), `frontend/` (Next.js), `e2e/` (Playwright), `contratos/` (generados por `manage.py exportar_contratos`: `openapi.json`, `mensajes.json`, `formatos-casos.json`; versionados y verificados por `pytest`), `infra/` (Caddyfile, página "no disponible").
- [003] Catálogo único de textos en `dominio/mensajes.py` (claves de `contracts/mensajes.md`): Django `{% msg "clave" %}` / `mensaje()`, Next.js `msg()`. Ningún texto visible literal; los rótulos que se migran se catalogan (`rot.*`) **sin cambiar la redacción**.
- [003] Variantes visuales solo desde `ui/variantes.json` (`{% clases %}` en Django, `cva` en React) y tokens semánticos; iconos de la lista de `contracts/componentes.md` § 2, siempre con texto. Cada componente existe en Django y en React con el **mismo marcado, rol y nombre accesible** (menús ⋮ y de cuenta con `<details>`/panel, no Radix), para que un mismo guion E2E sirva en ambas.
- [003] API v1 (`/api/v1/`, Django Ninja, `quini6/api.py`): **contrato primero** (`specs/003-…/contracts/api.md` aprobado antes de implementar), Problem Details con errores por campo y claves del catálogo, nivel `@nivel("P"|"U"|"A")` (CSRF en mutaciones, `no-store`/`no-cache`), importes y porcentajes como **cadena decimal**, fecha y hora con `-03:00`, `Dato` de [002] con estado explícito. Tras cambiar la API: `exportar_contratos` + `npm run api:tipos -w frontend`. Los nombres de esquema no se repiten entre módulos.
- [003] Mismo origen sin CORS: Next.js usa la **sesión de Django** (cookie reenviada por `apiServidor()`, con cuerpo completo y `Content-Length`) y **nunca decide permisos**: `proxy.ts` solo presenta lo que responde Django y cada operación de la API autoriza.
- [003] Caddy decide quién atiende cada ruta con `QUINI6_RUTAS_NEXT` (vuelta automática a Django si Next.js no responde; `X-Interfaz`); los formularios de Django llevan `?_interfaz=django` (`{% accion_formulario %}`). Conmutar o revertir una pantalla = cambiar la variable y recargar Caddy (contracts/rutas.md § 3).
- [003] Formularios: `clave_idempotencia` / `Idempotency-Key` (últimas 50 en la sesión, FR-031); sesión vencida → token `pendiente` firmado (sin contraseñas, 60 min) y "Volver al formulario" entre aplicaciones; validación previa con los mismos textos que repite el servidor; estado "…ando…" en el botón.
- [003] Sesiones con `SESSION_ENGINE = "quini6.sesiones"`: una sesión que la solicitud no modificó solo renueva su vencimiento (no reescribe datos), así las solicitudes simultáneas de Next.js no borran un aviso recién agregado; no volver al almacén de Django sin resolver esa carrera.
- [003] Avisos = mensajes de Django en la sesión (`MESSAGE_STORAGE` de sesión), compartidos con Next.js por `GET/POST /api/v1/avisos/` (solo claves del catálogo); sin scripts se ven en la página, con scripts como Toast. Una página de Next.js no agrega avisos mientras se dibuja: redirige a un `…/avisar/route.ts`; y toda redirección de un manejador de ruta es **relativa**.
- [003] E2E: un guion por historia con `getByRole`/`getByLabel` y textos del catálogo, axe sin incidencias críticas ni graves y sin desplazamiento horizontal a 360 px; corre contra Django y detrás de Caddy contra Next.js (`E2E_RUTAS_NEXT` = rutas conmutadas).
- [003] Presupuesto de JavaScript (R-24, desviación aprobada): privadas ≤ 200 kB comprimidos; públicas, lo más bajo posible sobre el piso de Next.js (≈ 130 kB). Nada en la estructura común que no se use en todas las pantallas; lo pesado, bajo demanda (calendario, Sonner) y lo que no corre en el navegador, como componente de servidor. Medir con `npm run lhci -- --base <enrutador> --ingreso <Django directo>`.
- [003] Formatos es-AR según `contracts/formatos.md` (filtros de Django y `lib/formato.ts`, con los casos compartidos de `contratos/formatos-casos.json`); fecha y hora siempre en America/Argentina/Buenos_Aires.

## Arranque y pruebas en local (PowerShell)
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
python manage.py migrate; python manage.py runserver   # http://127.0.0.1:8000/
python manage.py procesar_extracciones                 # [002] trabajador, en otra terminal
npm ci; npm run css                                    # [003] Node 24: estilos de Django (Tailwind)
npm run dev -w frontend                                # [003] Next.js en :3000; Caddy: docker compose up -d proxy
pytest                    # tests/unit + tests/integration + tests/api
ruff check .
npm run lint -w frontend; npm run typecheck -w frontend; npm run test -w frontend; npm run e2e
```
Verificación manual por escenarios: `specs/001-quini6-mvp/quickstart.md`, `specs/002-extraccion-historica-csv/quickstart.md` y `specs/003-modernizacion-ui-ux/quickstart.md` (entorno con Caddy y Next.js en § 2).

## Convenciones
- Flujo SDD con Spec Kit (`/speckit-*`): nada se implementa sin spec/plan/tareas; las ambigüedades se preguntan, no se suponen.
- Código, nombres y textos visibles en **español de Argentina** (sin i18n/`.po`); textos según `contracts/mensajes.md`; formatos con los filtros `fecha_ar`, `pesos`, `dos_digitos`, `porcentaje_ar`.
- Trazabilidad: docstrings y pruebas citan los IDs de la spec (FR-, RN-, AC-, NFR-, R-).
- Autorización en el servidor en cada GET y POST; jugadas siempre filtradas por `usuario=request.user` (404 idéntico si es ajena o no existe).
- Una app Django por módulo (`cuentas`, `resultados`, `jugadas`, `estadisticas`, `extracciones`); lógica de estado en `servicios.py`, lecturas en `consultas.py`.
- `ruff` (py312, línea 100, reglas E F I B UP) limpio y `pytest` en verde antes de dar algo por terminado; en `frontend/`, además `lint`, `typecheck` y `test`.

Las reglas de producto viven en .specify/memory/constitution.md y el estado del producto en specs/README.md

## Spec-kit

- Antes de ejecutar el flujo de `/speckit-specify`, SIEMPRE ejecuta primero el hook `before_specify` (skill `speckit-git-feature`) para crear la rama de la feature, y espera su resultado antes de crear la spec.
- Tras completar `/speckit.specify`, verifica con `git branch --show-current` que estamos en la rama `NNN-nombre-feature` y no en `main`. Si no es así, avísame antes de continuar.
- Al ejecutar `/speckit-plan`, SIEMPRE incluye en `plan.md`, como último paso de la fase final, un paso de mantenimiento: “Actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec (p. ej. ‘[003] ...’). No incluyas entradas por incluir, asegúrate siempre de que es información transversal y relevante para el proyecto que pueden aprovechar futuras features.”