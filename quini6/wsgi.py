"""Configuración WSGI de QUINI_6 (gunicorn quini6.wsgi)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quini6.settings")

application = get_wsgi_application()
