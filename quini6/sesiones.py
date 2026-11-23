"""Almacén de sesiones en la base ([003] FR-043, R-19, R-31).

Igual que `django.contrib.sessions.backends.db`, salvo al guardar una sesión que la solicitud solo
leyó. La sesión vence a los 30 minutos de inactividad (`SESSION_SAVE_EVERY_REQUEST`), así que cada
solicitud la guarda al terminar; el almacén de Django la escribe completa, con los datos que leyó al
empezar. Con la sesión compartida, Next.js hace varias solicitudes simultáneas (sesión, avisos, las
lecturas de la página) y una que terminaba después borraba el aviso que otra acababa de agregar.

Aquí, una sesión sin cambios solo renueva su vencimiento; nunca reescribe sus datos ni revive una
sesión que otra solicitud cerró. Una sesión modificada se guarda como siempre.
"""

from django.contrib.sessions.backends.db import SessionStore as SessionStoreBase


class SessionStore(SessionStoreBase):
    def save(self, must_create=False):
        if must_create or self.modified or self.session_key is None:
            return super().save(must_create=must_create)
        self.model.objects.filter(session_key=self.session_key).update(
            expire_date=self.get_expiry_date()
        )
