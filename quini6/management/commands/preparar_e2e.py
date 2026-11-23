"""Datos deterministas para los recorridos de Playwright ([003] R-23, T032).

Solo funciona con ``QUINI6_DEBUG=1`` y ``QUINI6_E2E=1``: **vacía la base** y crea cuentas, sorteos
publicados, jugadas y extracciones históricas en los cinco estados de [003] RN-01. Nunca se usa en
producción.

Las extracciones pasan por el proceso real de [002] (identificación, consolidación, clasificación,
resumen y CSV) con un cliente local que responde con las páginas de los escenarios de
``tests/fuentes_prueba/escenarios/`` (archivos de datos, sin red). Los sorteos y jugadas se escriben
con el ORM, como las fábricas de las pruebas, para no depender de los recorridos de carga.
"""

from __future__ import annotations

import json
import random
import secrets
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from cuentas.models import Usuario
from dominio.extraccion.tipos import EstadoExtraccion
from dominio.tipos import ORDEN_MODALIDADES, Modalidad
from extracciones.cliente_http import RespuestaHttp
from extracciones.fuentes.fichas import obtener_fichas
from extracciones.models import Extraccion
from extracciones.servicios import procesar_extraccion
from jugadas.models import Jugada
from resultados.models import Concurso, EstadoVersion, ModalidadConcurso, VersionNumeros

ESCENARIOS = Path(settings.BASE_DIR) / "tests" / "fuentes_prueba" / "escenarios"
CREDENCIALES = Path(settings.BASE_DIR) / "e2e" / ".credenciales.json"
BASES = {"F1": "http://e2e.local/f1", "F2": "http://e2e.local/f2", "F3": "http://e2e.local/f3"}
CUENTAS = {
    "admin": ("admin@e2e.local", True),
    "admin2": ("admin2@e2e.local", True),
    "usuaria": ("usuaria@e2e.local", False),
    "sinjugadas": ("sinjugadas@e2e.local", False),
}
#: Escenario de [002] → etiqueta que produce ([003] RN-01).
#: Período del quickstart de [002] (sorteos 3422 a 3426); el último, entre dos sorteos.
EXTRACCIONES = [
    ("normal", date(2026, 11, 1), date(2026, 11, 15)),
    ("discrepancias", date(2026, 11, 1), date(2026, 11, 15)),
    ("estructura", date(2026, 11, 1), date(2026, 11, 15)),
    ("fallas", date(2026, 11, 1), date(2026, 11, 15)),
    ("normal", date(2026, 11, 2), date(2026, 11, 3)),  # entre dos sorteos: sin sorteos
]
TOTAL_EXTRACCIONES = 25
FUENTE = ("Extracto oficial de prueba (e2e)", date(2026, 1, 10))


class ClienteEscenario:
    """Responde como el servidor de fuentes de prueba de [002] con los archivos del escenario."""

    def __init__(self, nombre: str):
        self.carpeta = ESCENARIOS / nombre
        datos = json.loads((self.carpeta / "escenario.json").read_text(encoding="utf-8"))
        self.rutas: dict[str, dict] = datos["rutas"]
        self.momento = datetime(2026, 11, 19, 13, 15, tzinfo=UTC)

    def obtener(self, fuente, url: str) -> RespuestaHttp:
        regla = self.rutas.get(urlsplit(url).path.replace("http://e2e.local", ""))
        if regla is None:
            return RespuestaHttp(404, "", None, self.momento)
        if regla.get("demora"):
            return RespuestaHttp(None, None, "TimeoutError: timed out", self.momento)
        texto = ""
        if regla.get("pagina"):
            texto = (self.carpeta / regla["pagina"]).read_text(encoding="utf-8")
        return RespuestaHttp(int(regla.get("codigo", 200)), texto, None, self.momento)


class Command(BaseCommand):
    help = "Vacía la base y crea datos deterministas para Playwright (solo desarrollo y CI)."

    def add_arguments(self, parser):
        parser.add_argument("--vacio", action="store_true", help="Solo crea las cuentas (T097).")

    def handle(self, *args, vacio: bool = False, **opciones):
        if not (settings.DEBUG and getattr(settings, "QUINI6_E2E", False)):
            raise CommandError(
                "preparar_e2e solo funciona con QUINI6_DEBUG=1 y QUINI6_E2E=1: vacía la base."
            )
        call_command("flush", interactive=False, verbosity=0)
        azar = random.Random(3250)
        with transaction.atomic():
            cuentas = self._cuentas()
            if not vacio:
                sorteos = self._sorteos(cuentas["admin"][0], azar)
                self._jugadas(cuentas["usuaria"][0], sorteos, azar)
        if not vacio:
            self._extracciones(cuentas["admin"][0], cuentas["admin2"][0])
        CREDENCIALES.parent.mkdir(parents=True, exist_ok=True)
        CREDENCIALES.write_text(
            json.dumps(
                {clave: {"correo": u.email, "contrasena": c} for clave, (u, c) in cuentas.items()},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        for clave, (usuario, contrasena) in cuentas.items():
            self.stdout.write(f"{clave}: {usuario.email} / {contrasena}")
        ruta = CREDENCIALES
        if ruta.is_relative_to(settings.BASE_DIR):
            ruta = ruta.relative_to(settings.BASE_DIR)
        self.stdout.write(f"Credenciales en {ruta}")

    def _cuentas(self) -> dict[str, tuple[Usuario, str]]:
        cuentas = {}
        for clave, (correo, admin) in CUENTAS.items():
            contrasena = secrets.token_urlsafe(12)
            usuario = Usuario.objects.create_user(
                email=correo, password=contrasena, es_administrador=admin
            )
            cuentas[clave] = (usuario, contrasena)
        return cuentas

    def _sorteos(self, autor: Usuario, azar: random.Random) -> list[Concurso]:
        """20 sorteos publicados (miércoles y domingos) de 2025 y 2026, con sus números."""
        sorteos = []
        fecha = date(2025, 3, 2)
        for indice in range(20):
            concurso = Concurso.objects.create(
                numero=3300 + indice, fecha_sorteo=fecha, creado_por=autor
            )
            for modalidad in ORDEN_MODALIDADES:
                mc = ModalidadConcurso.objects.create(concurso=concurso, modalidad=modalidad.value)
                if modalidad is Modalidad.PREMIO_EXTRA:
                    continue
                self._publicar_numeros(mc, autor, sorted(azar.sample(range(46), 6)), fecha)
            sorteos.append(concurso)
            fecha += timedelta(days=3 if fecha.weekday() == 6 else 4)
            if indice == 9:
                fecha = date(2026, 3, 1)
        # [003] HU-10, Fase 16: un sorteo próximo, sin números publicados, que admite jugadas
        # ([001] RN-07), fuera de la lista devuelta (las jugadas de ejemplo usan los publicados).
        proximo = Concurso.objects.create(
            numero=3320, fecha_sorteo=date(2026, 12, 2), creado_por=autor
        )
        for modalidad in ORDEN_MODALIDADES:
            ModalidadConcurso.objects.create(concurso=proximo, modalidad=modalidad.value)
        return sorteos

    def _publicar_numeros(self, mc, autor, numeros, fecha: date) -> None:
        momento = timezone.make_aware(datetime(fecha.year, fecha.month, fecha.day, 23, 0))
        version = VersionNumeros(
            modalidad_concurso=mc,
            estado=EstadoVersion.PUBLICADA,
            fuente_descripcion=FUENTE[0],
            fuente_fecha_consulta=FUENTE[1],
            creada_por=autor,
            actualizada_por=autor,
            publicada_por=autor,
            publicada_en=momento,
        )
        version.asignar_numeros(numeros)
        version.save()

    def _jugadas(self, usuaria: Usuario, sorteos: list[Concurso], azar: random.Random) -> None:
        for concurso in sorteos[-3:]:
            jugada = Jugada(usuario=usuaria, concurso=concurso, costo=Decimal("1500.00"))
            jugada.asignar_numeros(azar.sample(range(46), 6))
            jugada.save()

    def _extracciones(self, admin: Usuario, admin2: Usuario) -> None:
        fichas = obtener_fichas(BASES)
        base = timezone.make_aware(datetime(2026, 11, 1, 9, 0))
        for indice in range(TOTAL_EXTRACCIONES):
            escenario, desde, hasta = EXTRACCIONES[indice % len(EXTRACCIONES)]
            extraccion = Extraccion.objects.create(
                creada_por=admin,
                desde=desde,
                hasta=hasta,
                estado=EstadoExtraccion.EN_CURSO.value,
                iniciada_en=base + timedelta(hours=indice * 7),
            )
            procesar_extraccion(extraccion, ClienteEscenario(escenario), fichas)
        # Una extracción en curso de otra cuenta administradora (RN-03, AC-3.5): queda en espera.
        Extraccion.objects.create(
            creada_por=admin2,
            # Período cubierto por los escenarios (el trabajador lo resuelve en segundos si corre).
            desde=date(2026, 11, 4),
            hasta=date(2026, 11, 11),
            estado=EstadoExtraccion.EN_CURSO.value,
            iniciada_en=base + timedelta(days=10),
        )
