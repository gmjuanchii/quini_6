from django.apps import AppConfig


class ExtraccionesConfig(AppConfig):
    """Extracción histórica de sorteos y exportación CSV (spec 002)."""

    name = "extracciones"
    default_auto_field = "django.db.models.BigAutoField"
