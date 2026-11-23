"""Configuración de QUINI_6 (R-01, R-03, R-04, R-09, R-15).

Los valores sensibles se leen de variables de entorno ``QUINI6_*``. Si existe un archivo
``.env`` en la raíz del proyecto, se cargan sus líneas ``CLAVE=valor`` sin pisar las
variables de entorno ya definidas.
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def _cargar_env(ruta: Path) -> None:
    """Lector mínimo de .env: ignora líneas vacías y comentarios; no pisa el entorno."""
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip('"').strip("'")
        if clave and clave not in os.environ:
            os.environ[clave] = valor


_cargar_env(BASE_DIR / ".env")


def _env(nombre: str, defecto: str = "") -> str:
    return os.environ.get(nombre, defecto)


DEBUG = _env("QUINI6_DEBUG", "0").strip().lower() in {"1", "true", "si", "sí", "yes"}

SECRET_KEY = _env("QUINI6_SECRET_KEY")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "Falta la variable QUINI6_SECRET_KEY (obligatoria cuando QUINI6_DEBUG es falso)."
        )
    SECRET_KEY = "solo-desarrollo-no-usar-en-produccion"

ALLOWED_HOSTS = [h.strip() for h in _env("QUINI6_ALLOWED_HOSTS").split(",") if h.strip()]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

# [003] R-19: convivencia detrás del enrutador (mismo origen para Django y Next.js).
QUINI6_ORIGEN_PUBLICO = _env("QUINI6_ORIGEN_PUBLICO").strip()
CSRF_TRUSTED_ORIGINS = [QUINI6_ORIGEN_PUBLICO] if QUINI6_ORIGEN_PUBLICO else []
USE_X_FORWARDED_HOST = True


def _patrones(nombre: str) -> list[str]:
    return [p for p in _env(nombre).split() if p]


# [003] R-12, R-20: rutas que atiende Next.js (contracts/rutas.md § 3).
QUINI6_RUTAS_NEXT = _patrones("QUINI6_RUTAS_NEXT")
QUINI6_RUTAS_NEXT_SIN_RESPALDO = _patrones("QUINI6_RUTAS_NEXT_SIN_RESPALDO")

# [003] R-23: habilita el comando preparar_e2e (solo junto con DEBUG).
QUINI6_E2E = _env("QUINI6_E2E", "0").strip().lower() in {"1", "true", "si", "sí", "yes"}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "quini6",
    "cuentas",
    "resultados",
    "jugadas",
    "estadisticas",
    "extracciones",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "quini6.urls"
CSRF_FAILURE_VIEW = "quini6.vistas_error.csrf_fallido"
WSGI_APPLICATION = "quini6.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "quini6.navegacion.navegacion",  # [003] FR-014
                "quini6.tema.tema",  # [003] FR-036, R-14
            ],
        },
    },
]

if _env("QUINI6_DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _env("QUINI6_DB_NAME"),
            "USER": _env("QUINI6_DB_USER"),
            "PASSWORD": _env("QUINI6_DB_PASSWORD"),
            "HOST": _env("QUINI6_DB_HOST"),
            "PORT": _env("QUINI6_DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            # [003] R-23: QUINI6_DB_SQLITE permite una base aparte para los recorridos E2E
            # (preparar_e2e vacía la base), sin tocar db.sqlite3.
            "NAME": BASE_DIR / (_env("QUINI6_DB_SQLITE").strip() or "db.sqlite3"),
            # [003] Con Next.js llegan escrituras simultáneas (sesión, avisos, la operación): una
            # transacción que primero lee y después escribe fallaba con "database is locked". Con
            # IMMEDIATE toma el bloqueo de escritura al empezar y espera su turno (Django 5.1+).
            "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 20},
        }
    }

AUTH_USER_MODEL = "cuentas.Usuario"
LOGIN_URL = "/ingresar/"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
]

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# Sesiones (NFR-005: vencen tras 30 minutos sin actividad).
# [003] FR-043: el de la base de Django, pero una sesión sin cambios solo renueva su vencimiento y
# no pisa lo que otra solicitud simultánea agregó (un aviso, quini6/sesiones.py).
SESSION_ENGINE = "quini6.sesiones"
# [003] R-31: los avisos viven en la sesión (servidor), así Next.js los lee y los marca como leídos
# con /api/v1/avisos/ sin depender de una cookie que solo el navegador podría borrar.
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

STATIC_URL = "static/"
# [003] RN-08: logotipo, isotipo y favicon en ui/marca (compartidos con la Etapa 2).
STATICFILES_DIRS = [BASE_DIR / "static", ("marca", BASE_DIR / "ui" / "marca")]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# [002] R-05, R-11: direcciones base de reemplazo de las fuentes, SOLO para el servidor de
# fuentes de prueba (tests/fuentes_prueba). Vacías (None) → se usan las direcciones reales.
QUINI6_FUENTES_URL_BASE = {
    clave: (_env(f"QUINI6_FUENTE_{clave}_URL").strip() or None) for clave in ("F1", "F2", "F3")
}

# [003] R-25 (P-01): Sentry solo en producción, cuando QUINI6_SENTRY_DSN tiene valor.
if _env("QUINI6_SENTRY_DSN").strip():
    from quini6.observabilidad import iniciar_sentry

    iniciar_sentry(_env("QUINI6_SENTRY_DSN").strip(), _env("QUINI6_SENTRY_ENTORNO", "produccion"))
