"""Trabajador de la extracción histórica ([002] R-01, contracts/comandos.md).

Toma las extracciones en curso por orden de inicio y las procesa de a una, con un único
limitador por sitio compartido (NFR-005). **Debe correr una sola instancia**: es la que
garantiza el ritmo máximo de una consulta cada 2 s por sitio aunque varios administradores
inicien extracciones a la vez. Reanuda una extracción interrumpida (I-07).
"""

import time

from django.core.management.base import BaseCommand

from dominio.extraccion.tipos import EstadoExtraccion
from extracciones import servicios
from extracciones.cliente_http import LimitadorPorSitio
from extracciones.models import Extraccion

ESPERA_ENTRE_REVISIONES = 2


def extracciones_pendientes():
    return Extraccion.objects.filter(estado=EstadoExtraccion.EN_CURSO.value).order_by(
        "iniciada_en", "id"
    )


class Command(BaseCommand):
    help = "Procesa las extracciones históricas en curso (una sola instancia)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--una-vez",
            action="store_true",
            help="Procesa las extracciones en curso que haya y termina.",
        )

    def handle(self, *args, una_vez=False, **opciones):
        cliente, fichas = self.crear_cliente_y_fichas()
        while True:
            for extraccion in extracciones_pendientes():
                self.stdout.write(f"Extracción {extraccion.pk}: iniciada")
                servicios.procesar_extraccion(extraccion, cliente, fichas)
                extraccion.refresh_from_db()
                self.stdout.write(f"Extracción {extraccion.pk}: {extraccion.estado_enum.texto}")
            if una_vez:
                return
            time.sleep(ESPERA_ENTRE_REVISIONES)

    def crear_cliente_y_fichas(self):
        """Punto de inyección para las pruebas (cliente falso)."""
        return servicios.crear_cliente_y_fichas(LimitadorPorSitio())
