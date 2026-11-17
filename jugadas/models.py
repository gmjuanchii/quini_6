"""Jugadas personales (data-model.md, RN-04 a RN-10)."""

from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from resultados.models import Concurso


class Jugada(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jugadas", db_index=True
    )
    concurso = models.ForeignKey(Concurso, on_delete=models.PROTECT, related_name="jugadas")
    n1 = models.SmallIntegerField()
    n2 = models.SmallIntegerField()
    n3 = models.SmallIntegerField()
    n4 = models.SmallIntegerField()
    n5 = models.SmallIntegerField()
    n6 = models.SmallIntegerField()
    costo = models.DecimalField(max_digits=16, decimal_places=2)
    creada_en = models.DateTimeField(default=timezone.now)
    modificada_en = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=["usuario", "concurso"], name="jugada_usuario_concurso")]
        constraints = [
            models.CheckConstraint(
                condition=Q(n1__gte=0)
                & Q(n2__gt=F("n1"))
                & Q(n3__gt=F("n2"))
                & Q(n4__gt=F("n3"))
                & Q(n5__gt=F("n4"))
                & Q(n6__gt=F("n5"))
                & Q(n6__lte=45),
                name="jugada_rango_y_orden",
            ),
            models.CheckConstraint(condition=Q(costo__gte=0), name="jugada_costo_no_negativo"),
        ]

    def __str__(self) -> str:
        return f"Jugada {self.pk} — {self.concurso}"

    @property
    def numeros(self) -> frozenset[int]:
        return frozenset((self.n1, self.n2, self.n3, self.n4, self.n5, self.n6))

    @property
    def numeros_ordenados(self) -> list[int]:
        return sorted(self.numeros)

    def asignar_numeros(self, numeros) -> None:
        self.n1, self.n2, self.n3, self.n4, self.n5, self.n6 = sorted(numeros)
