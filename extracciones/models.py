"""Modelos de la extracción histórica ([002] data-model.md → "Entidades persistidas", R-08).

Solo se escribe en estas tablas ([002] RN-41). Una extracción terminada no se modifica (RN-44).
Los ``JSONField`` nunca se filtran por su contenido: no se usa ninguna función exclusiva de un
motor de base de datos.
"""

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from dominio.extraccion.tipos import (
    EstadoExtraccion,
    EstadoSorteo,
    Fuente,
    ResultadoIntento,
)


def _choices(enum) -> list[tuple[str, str]]:
    return [(m.value, getattr(m, "texto", m.value)) for m in enum]


class Extraccion(models.Model):
    """Entidad Extracción: el pedido, su estado, su avance, el resumen y el archivo."""

    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="extracciones"
    )
    desde = models.DateField()
    hasta = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=_choices(EstadoExtraccion),
        default=EstadoExtraccion.EN_CURSO.value,
        db_index=True,
    )
    iniciada_en = models.DateTimeField(db_index=True)
    finalizada_en = models.DateTimeField(null=True, blank=True)
    numero_desde = models.PositiveIntegerField(null=True, blank=True)
    numero_hasta = models.PositiveIntegerField(null=True, blank=True)
    cobertura_desde = models.DateField(null=True, blank=True)
    resumen = models.JSONField(null=True, blank=True)
    archivo_csv = models.TextField(blank=True, default="")
    nombre_archivo = models.CharField(max_length=120, blank=True, default="")
    version_contrato = models.CharField(max_length=10, blank=True, default="")

    class Meta:
        ordering = ["-iniciada_en", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["creada_por"],
                condition=Q(estado="EN_CURSO"),
                name="extraccion_una_en_curso_por_admin",
            ),
            models.CheckConstraint(
                condition=Q(desde__lte=F("hasta")), name="extraccion_desde_menor_o_igual_hasta"
            ),
            models.CheckConstraint(
                condition=(
                    Q(estado="EN_CURSO", finalizada_en__isnull=True)
                    | (~Q(estado="EN_CURSO") & Q(finalizada_en__isnull=False))
                ),
                name="extraccion_finalizada_si_y_solo_si_terminada",
            ),
            models.CheckConstraint(
                condition=(
                    Q(numero_desde__isnull=True)
                    | Q(numero_hasta__isnull=True)
                    | Q(numero_desde__lte=F("numero_hasta"))
                ),
                name="extraccion_numeros_ordenados",
            ),
        ]

    def __str__(self) -> str:
        return f"Extracción {self.pk} ({self.desde} a {self.hasta})"

    @property
    def estado_enum(self) -> EstadoExtraccion:
        return EstadoExtraccion(self.estado)

    @property
    def en_curso(self) -> bool:
        return self.estado == EstadoExtraccion.EN_CURSO.value

    @property
    def identificando(self) -> bool:
        return self.numero_desde is None

    @property
    def total_identificados(self) -> int | None:
        if self.numero_desde is None or self.numero_hasta is None:
            return None
        return self.numero_hasta - self.numero_desde + 1

    @property
    def procesados(self) -> int:
        return self.sorteos.count()


class SorteoExtraido(models.Model):
    """Un número identificado y su resultado consolidado."""

    extraccion = models.ForeignKey(Extraccion, on_delete=models.CASCADE, related_name="sorteos")
    numero = models.PositiveIntegerField()
    fecha = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=_choices(EstadoSorteo), db_index=True)
    combina_fuentes = models.BooleanField(default=False)
    sin_corroborar = models.BooleanField(default=False)
    consolidado = models.JSONField()
    procesado_en = models.DateTimeField()

    class Meta:
        ordering = ["numero"]
        constraints = [
            models.UniqueConstraint(
                fields=["extraccion", "numero"], name="sorteo_extraido_unico_por_extraccion"
            )
        ]

    def __str__(self) -> str:
        return f"Sorteo {self.numero} de la extracción {self.extraccion_id}"

    @property
    def estado_enum(self) -> EstadoSorteo:
        return EstadoSorteo(self.estado)


class IntentoConsulta(models.Model):
    """Entidad Intento de consulta: un registro por sorteo y fuente ([002] FR-006, RN-08)."""

    sorteo = models.ForeignKey(SorteoExtraido, on_delete=models.CASCADE, related_name="intentos")
    fuente = models.CharField(max_length=2, choices=[(f.value, f.nombre) for f in Fuente])
    resultado = models.CharField(max_length=40, choices=_choices(ResultadoIntento))
    url = models.CharField(max_length=500, blank=True, default="")
    consultado_en = models.DateTimeField(null=True, blank=True)
    datos = models.JSONField(null=True, blank=True)
    observaciones = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["fuente"]
        constraints = [
            models.UniqueConstraint(
                fields=["sorteo", "fuente"], name="intento_unico_por_sorteo_y_fuente"
            )
        ]

    def __str__(self) -> str:
        return f"{self.fuente} · sorteo {self.sorteo_id}"

    @property
    def fuente_enum(self) -> Fuente:
        return Fuente(self.fuente)

    @property
    def resultado_enum(self) -> ResultadoIntento:
        return ResultadoIntento(self.resultado)
