"""Concursos, versiones de resultados y registro de cambios (data-model.md, R-06).

Las versiones de números y de premios son inmutables una vez publicadas: una corrección
crea una versión nueva y la anterior pasa a ``REEMPLAZADA`` (RN-23). ``RegistroCambio``
es de solo agregado (NFR-006).
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from dominio.tipos import ORDEN_MODALIDADES, Modalidad

ModalidadChoices = models.TextChoices(
    "ModalidadChoices", {m.name: (m.value, m.nombre) for m in ORDEN_MODALIDADES}
)


class EstadoVersion(models.TextChoices):
    BORRADOR = "BORRADOR", "Borrador"
    OBSERVADO = "OBSERVADO", "Observado"
    PUBLICADA = "PUBLICADA", "Publicada"
    REEMPLAZADA = "REEMPLAZADA", "Reemplazada"


ESTADOS_EN_TRABAJO = (EstadoVersion.BORRADOR, EstadoVersion.OBSERVADO)


class Bloque(models.TextChoices):
    CONCURSO = "CONCURSO", "Sorteo"  # [003] D-04: "sorteo" en la interfaz; el valor no cambia
    NUMEROS = "NUMEROS", "Números"
    PREMIOS = "PREMIOS", "Premios"


class Accion(models.TextChoices):
    CREAR_CONCURSO = "CREAR_CONCURSO", "Crear sorteo"
    MODIFICAR_CONCURSO = "MODIFICAR_CONCURSO", "Modificar sorteo"
    GUARDAR_BORRADOR = "GUARDAR_BORRADOR", "Guardar borrador"
    OBSERVAR = "OBSERVAR", "Observar"
    RESOLVER_OBSERVACION = "RESOLVER_OBSERVACION", "Resolver observación"
    PUBLICAR = "PUBLICAR", "Publicar"
    MARCAR_REVISION = "MARCAR_REVISION", "Marcar en revisión"
    QUITAR_REVISION = "QUITAR_REVISION", "Quitar revisión"
    INICIAR_CORRECCION = "INICIAR_CORRECCION", "Iniciar corrección"
    PUBLICAR_CORRECCION = "PUBLICAR_CORRECCION", "Publicar corrección"


class Concurso(models.Model):
    numero = models.PositiveIntegerField(unique=True, db_index=True)
    fecha_sorteo = models.DateField(db_index=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-fecha_sorteo", "-numero"]

    def __str__(self) -> str:
        return f"Sorteo N.º {self.numero}"


class ModalidadConcurso(models.Model):
    concurso = models.ForeignKey(Concurso, on_delete=models.CASCADE, related_name="modalidades")
    modalidad = models.CharField(max_length=20, choices=ModalidadChoices.choices)
    numeros_en_revision = models.BooleanField(default=False)
    numeros_motivo_revision = models.TextField(blank=True, default="")
    premios_en_revision = models.BooleanField(default=False)
    premios_motivo_revision = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["concurso", "modalidad"], name="modalidad_unica_por_concurso"
            ),
            models.CheckConstraint(
                condition=Q(numeros_en_revision=False) | ~Q(numeros_motivo_revision=""),
                name="revision_numeros_con_motivo",
            ),
            models.CheckConstraint(
                condition=Q(premios_en_revision=False) | ~Q(premios_motivo_revision=""),
                name="revision_premios_con_motivo",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.concurso} — {self.modalidad_enum.nombre}"

    @property
    def modalidad_enum(self) -> Modalidad:
        return Modalidad(self.modalidad)

    def clean(self) -> None:
        if (
            self.numeros_en_revision
            and not self.versiones_numeros.filter(estado=EstadoVersion.PUBLICADA).exists()
        ):
            raise ValidationError("Solo se puede marcar en revisión un bloque publicado.")
        if (
            self.premios_en_revision
            and not self.versiones_premios.filter(estado=EstadoVersion.PUBLICADA).exists()
        ):
            raise ValidationError("Solo se puede marcar en revisión un bloque publicado.")


class VersionBase(models.Model):
    """Metadatos comunes de las versiones de números y de premios."""

    fuente_descripcion = models.CharField(max_length=300, blank=True, default="")
    fuente_fecha_consulta = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=12, choices=EstadoVersion.choices, default=EstadoVersion.BORRADOR
    )
    motivo_observacion = models.TextField(blank=True, default="")
    es_correccion = models.BooleanField(default=False)
    motivo_correccion = models.TextField(blank=True, default="")
    creada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+"
    )
    creada_en = models.DateTimeField(default=timezone.now)
    actualizada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+", null=True
    )
    actualizada_en = models.DateTimeField(default=timezone.now)
    publicada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    publicada_en = models.DateTimeField(null=True, blank=True)
    reemplazada_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def fuente_completa(self) -> bool:
        return bool(self.fuente_descripcion.strip()) and self.fuente_fecha_consulta is not None

    @property
    def en_trabajo(self) -> bool:
        return self.estado in ESTADOS_EN_TRABAJO


def _restricciones_version(prefijo: str) -> list:
    return [
        models.UniqueConstraint(
            fields=["modalidad_concurso"],
            condition=Q(estado=EstadoVersion.PUBLICADA),
            name=f"{prefijo}_una_publicada",
        ),
        models.UniqueConstraint(
            fields=["modalidad_concurso"],
            condition=Q(estado__in=[EstadoVersion.BORRADOR, EstadoVersion.OBSERVADO]),
            name=f"{prefijo}_una_en_trabajo",
        ),
        models.CheckConstraint(
            condition=~Q(estado=EstadoVersion.OBSERVADO) | ~Q(motivo_observacion=""),
            name=f"{prefijo}_observado_con_motivo",
        ),
        models.CheckConstraint(
            condition=Q(es_correccion=False) | ~Q(motivo_correccion=""),
            name=f"{prefijo}_correccion_con_motivo",
        ),
    ]


class VersionNumeros(VersionBase):
    modalidad_concurso = models.ForeignKey(
        ModalidadConcurso, on_delete=models.PROTECT, related_name="versiones_numeros"
    )
    n1 = models.SmallIntegerField()
    n2 = models.SmallIntegerField()
    n3 = models.SmallIntegerField()
    n4 = models.SmallIntegerField()
    n5 = models.SmallIntegerField()
    n6 = models.SmallIntegerField()

    class Meta:
        constraints = [
            *_restricciones_version("vnumeros"),
            models.CheckConstraint(
                condition=Q(n1__gte=0)
                & Q(n2__gt=F("n1"))
                & Q(n3__gt=F("n2"))
                & Q(n4__gt=F("n3"))
                & Q(n5__gt=F("n4"))
                & Q(n6__gt=F("n5"))
                & Q(n6__lte=45),
                name="vnumeros_rango_y_orden",
            ),
        ]

    @property
    def numeros(self) -> frozenset[int]:
        return frozenset((self.n1, self.n2, self.n3, self.n4, self.n5, self.n6))

    def asignar_numeros(self, numeros) -> None:
        self.n1, self.n2, self.n3, self.n4, self.n5, self.n6 = sorted(numeros)

    def clean(self) -> None:
        if self.modalidad_concurso.modalidad == Modalidad.PREMIO_EXTRA.value:
            raise ValidationError("Premio Extra no tiene números propios (RN-15).")

    def valor_json(self) -> dict:
        return {"numeros": sorted(self.numeros)}


class VersionPremios(VersionBase):
    modalidad_concurso = models.ForeignKey(
        ModalidadConcurso, on_delete=models.PROTECT, related_name="versiones_premios"
    )
    aciertos_categoria_ganadora = models.SmallIntegerField(null=True, blank=True)
    sin_ganadores = models.BooleanField(default=False)

    class Meta:
        constraints = [
            *_restricciones_version("vpremios"),
            models.CheckConstraint(
                condition=Q(sin_ganadores=False) | Q(aciertos_categoria_ganadora__isnull=True),
                name="vpremios_sin_ganadores_excluye_categoria",
            ),
        ]

    def valor_json(self) -> dict:
        from dominio.importes import a_texto_decimal

        return {
            "aciertos_categoria_ganadora": self.aciertos_categoria_ganadora,
            "sin_ganadores": self.sin_ganadores,
            "categorias": [
                {
                    "categoria": c.categoria,
                    "ganadores": c.ganadores,
                    "importe_categoria": a_texto_decimal(c.importe_categoria),
                    "importe_individual": a_texto_decimal(c.importe_individual),
                    "pozo_vacante_acumulado": a_texto_decimal(c.pozo_vacante_acumulado),
                }
                for c in self.categorias.all()
            ],
        }


def _no_negativo(campo: str) -> Q:
    return Q(**{f"{campo}__isnull": True}) | Q(**{f"{campo}__gte": 0})


class PremioCategoria(models.Model):
    version_premios = models.ForeignKey(
        VersionPremios, on_delete=models.CASCADE, related_name="categorias"
    )
    categoria = models.CharField(max_length=10)
    ganadores = models.PositiveIntegerField(null=True, blank=True)
    importe_categoria = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    importe_individual = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    pozo_vacante_acumulado = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["version_premios", "categoria"], name="categoria_unica_por_version"
            ),
            models.CheckConstraint(
                condition=_no_negativo("importe_categoria")
                & _no_negativo("importe_individual")
                & _no_negativo("pozo_vacante_acumulado"),
                name="premio_importes_no_negativos",
            ),
        ]

    def clean(self) -> None:
        modalidad = Modalidad(self.version_premios.modalidad_concurso.modalidad)
        if self.categoria not in modalidad.categorias:
            raise ValidationError("La categoría no pertenece a la modalidad.")


class RegistroCambioQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise PermissionError("El registro de cambios es de solo agregado.")

    def delete(self):
        raise PermissionError("El registro de cambios es de solo agregado.")


class RegistroCambio(models.Model):
    concurso = models.ForeignKey(Concurso, on_delete=models.PROTECT, related_name="cambios")
    modalidad = models.CharField(
        max_length=20, choices=ModalidadChoices.choices, null=True, blank=True
    )
    bloque = models.CharField(max_length=10, choices=Bloque.choices)
    accion = models.CharField(max_length=24, choices=Accion.choices)
    valor_anterior = models.JSONField(null=True, blank=True)
    valor_nuevo = models.JSONField(null=True, blank=True)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    fecha_hora = models.DateTimeField(default=timezone.now)
    motivo = models.TextField(blank=True, default="")
    fuente = models.TextField(blank=True, default="")

    objects = RegistroCambioQuerySet.as_manager()

    class Meta:
        ordering = ["-fecha_hora", "-id"]

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("El registro de cambios es de solo agregado.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("El registro de cambios es de solo agregado.")
