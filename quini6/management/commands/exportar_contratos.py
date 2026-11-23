"""Exporta los contratos versionados de contratos/ ([003] R-13, R-16, contracts/formatos.md).

- ``openapi.json``: esquema OpenAPI de /api/v1/ (fuente de los tipos de Next.js, R-17).
- ``mensajes.json``: catálogo único de textos (dominio/mensajes.py).
- ``formatos-casos.json``: casos de la tabla compartida de formatos es-AR.

``--verificar`` compara sin escribir y falla si algún archivo difiere (lo usa la CI).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from dominio.mensajes import MENSAJES

RUTA = Path(settings.BASE_DIR) / "contratos"
_CONTRATO_FORMATOS = (
    Path(settings.BASE_DIR) / "specs" / "003-modernizacion-ui-ux" / "contracts" / "formatos.md"
)


def _json(datos) -> str:
    return json.dumps(datos, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def casos_de_formatos() -> list[dict[str, str]]:
    """Filas de "Casos mínimos de la tabla compartida" de contracts/formatos.md."""
    texto = _CONTRATO_FORMATOS.read_text(encoding="utf-8")
    seccion = texto.split("## Casos mínimos de la tabla compartida", 1)[1]
    casos = []
    for linea in seccion.splitlines():
        coincidencia = re.match(r"^\|\s*([a-z_]+)\s*\|\s*`([^`]*)`\s*\|\s*`([^`]*)`\s*\|$", linea)
        if coincidencia:
            tipo, entrada, salida = coincidencia.groups()
            casos.append({"tipo": tipo, "entrada": entrada, "salida": salida})
    return casos


def generar() -> dict[str, str]:
    from quini6.api import api

    return {
        "openapi.json": _json(api.get_openapi_schema()),
        "mensajes.json": _json(MENSAJES),
        "formatos-casos.json": _json(casos_de_formatos()),
    }


class Command(BaseCommand):
    help = "Exporta (o verifica con --verificar) los contratos versionados de contratos/."

    def add_arguments(self, parser):
        parser.add_argument("--verificar", action="store_true", help="Compara sin escribir.")

    def handle(self, *args, verificar: bool = False, **opciones):
        from quini6.management.commands import exportar_contratos as modulo

        ruta: Path = modulo.RUTA
        distintos = []
        for nombre, contenido in generar().items():
            destino = ruta / nombre
            actual = destino.read_text(encoding="utf-8") if destino.is_file() else None
            if verificar:
                if actual != contenido:
                    distintos.append(nombre)
                continue
            ruta.mkdir(parents=True, exist_ok=True)
            destino.write_text(contenido, encoding="utf-8", newline="\n")
            self.stdout.write(f"contratos/{nombre}")
        if distintos:
            raise CommandError(
                "Contratos desactualizados: "
                + ", ".join(distintos)
                + '. Ejecutar "python manage.py exportar_contratos" y versionar contratos/.'
            )
