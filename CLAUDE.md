# QUINI_6 — memoria técnica

**Qué es**: web pública e informativa del Quini 6 (Argentina) para consultar resultados, premios y estadísticas sin registro, y para que usuarios con cuenta sigan sus jugadas comparadas con los resultados oficiales.

## Stack y decisiones vigentes (ver `specs/*/plan.md` y `research.md`)
- Monolito **Django 5.2 LTS + Python 3.12**, plantillas renderizadas en el servidor. Sin SPA ni frameworks JS: JS puro solo como mejora progresiva (`static/js/selector-numeros.js`).
- Dependencias cerradas: `Django`, `gunicorn`, `whitenoise`, `psycopg[binary]` (prod) · dev: `pytest`, `pytest-django`, `ruff`. **No agregar otras** sin justificarlo en el plan.
- BD: **SQLite** en desarrollo/pruebas, **PostgreSQL 16** en producción (`QUINI6_DB_NAME` vacía → SQLite). Sin funciones exclusivas de un motor.
- Reglas de negocio en **`dominio/`: funciones puras sin Django**; errores como valores, no excepciones. Vistas: cargan datos → llaman al dominio → renderizan.
- Resultados como **versiones inmutables por bloque** (`VersionNumeros`, `VersionPremios`) + `RegistroCambio` de solo agregado. Comparaciones y estadísticas **no se guardan**: se calculan en cada consulta.
- Importes siempre `Decimal` / `DecimalField(16,2)`; nunca `float`.
- Auth: `cuentas.Usuario` con correo como identificador; bloqueo propio (5 fallos → 15 min); sesión 30 min de inactividad; `no-store` en páginas privadas. Admin = booleano + decorador `administrador_requerido`; se otorga con `manage.py otorgar_admin|quitar_admin`. **`django.contrib.admin` deshabilitado.**
- Config y secretos por variables de entorno `QUINI6_*` (lector propio de `.env` en `settings.py`); `.env` nunca se versiona.
- CSS propio con variables, desde 360 px, contraste AA; gráfico de estadísticas en SVG generado en el servidor.
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

## Arranque y pruebas en local (PowerShell)
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
python manage.py migrate; python manage.py runserver   # http://127.0.0.1:8000/
python manage.py procesar_extracciones                 # [002] trabajador, en otra terminal
pytest                    # tests/unit (dominio) + tests/integration (recorridos, matriz de acceso)
ruff check .
```
Verificación manual por escenarios: `specs/001-quini6-mvp/quickstart.md` y `specs/002-extraccion-historica-csv/quickstart.md`.

## Convenciones
- Flujo SDD con Spec Kit (`/speckit-*`): nada se implementa sin spec/plan/tareas; las ambigüedades se preguntan, no se suponen.
- Código, nombres y textos visibles en **español de Argentina** (sin i18n/`.po`); textos según `contracts/mensajes.md`; formatos con los filtros `fecha_ar`, `pesos`, `dos_digitos`, `porcentaje_ar`.
- Trazabilidad: docstrings y pruebas citan los IDs de la spec (FR-, RN-, AC-, NFR-, R-).
- Autorización en el servidor en cada GET y POST; jugadas siempre filtradas por `usuario=request.user` (404 idéntico si es ajena o no existe).
- Una app Django por módulo (`cuentas`, `resultados`, `jugadas`, `estadisticas`, `extracciones`); lógica de estado en `servicios.py`, lecturas en `consultas.py`.
- `ruff` (py312, línea 100, reglas E F I B UP) limpio y `pytest` en verde antes de dar algo por terminado.

Las reglas de producto viven en .specify/memory/constitution.md y el estado del producto en specs/README.md

## Spec-kit

- Antes de ejecutar el flujo de `/speckit-specify`, SIEMPRE ejecuta primero el hook `before_specify` (skill `speckit-git-feature`) para crear la rama de la feature, y espera su resultado antes de crear la spec.
- Tras completar `/speckit.specify`, verifica con `git branch --show-current` que estamos en la rama `NNN-nombre-feature` y no en `main`. Si no es así, avísame antes de continuar.
- Al ejecutar `/speckit-plan`, SIEMPRE incluye en `plan.md`, como último paso de la fase final, un paso de mantenimiento: “Actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec (p. ej. ‘[003] ...’). No incluyas entradas por incluir, asegúrate siempre de que es información transversal y relevante para el proyecto que pueden aprovechar futuras features.”