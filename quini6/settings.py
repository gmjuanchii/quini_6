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
            "NAME": BASE_DIR / "db.sqlite3",
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
SESSION_ENGINE = "django.contrib.sessions.backends.db"
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
STATICFILES_DIRS = [BASE_DIR / "static"]
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
