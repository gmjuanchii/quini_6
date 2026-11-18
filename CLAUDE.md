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

## Arranque y pruebas en local (PowerShell)
```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
python manage.py migrate; python manage.py runserver   # http://127.0.0.1:8000/
pytest                    # tests/unit (dominio) + tests/integration (recorridos, matriz de acceso)
ruff check .
```
Verificación manual por escenarios: `specs/001-quini6-mvp/quickstart.md`.

## Convenciones
- Flujo SDD con Spec Kit (`/speckit-*`): nada se implementa sin spec/plan/tareas; las ambigüedades se preguntan, no se suponen.
- Código, nombres y textos visibles en **español de Argentina** (sin i18n/`.po`); textos según `contracts/mensajes.md`; formatos con los filtros `fecha_ar`, `pesos`, `dos_digitos`, `porcentaje_ar`.
- Trazabilidad: docstrings y pruebas citan los IDs de la spec (FR-, RN-, AC-, NFR-, R-).
- Autorización en el servidor en cada GET y POST; jugadas siempre filtradas por `usuario=request.user` (404 idéntico si es ajena o no existe).
- Una app Django por módulo (`cuentas`, `resultados`, `jugadas`, `estadisticas`); lógica de estado en `servicios.py`, lecturas en `consultas.py`.
- `ruff` (py312, línea 100, reglas E F I B UP) limpio y `pytest` en verde antes de dar algo por terminado.

Las reglas de producto viven en .specify/memory/constitution.md y el estado del producto en specs/README.md
