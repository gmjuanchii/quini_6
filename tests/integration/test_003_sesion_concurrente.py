"""[003] FR-043, R-31: un aviso agregado a la sesión no se pierde por otra solicitud simultánea.

Next.js pide a la vez `GET /api/v1/sesion/`, `GET /api/v1/avisos/` y las lecturas de cada página, y
una página puede redirigir a `…/avisar/` mientras esas lecturas siguen en curso. Con
`SESSION_SAVE_EVERY_REQUEST` (sesión de 30 minutos de inactividad), una solicitud que solo leyó la
sesión la volvía a escribir completa al terminar, con los datos que había leído antes, y borraba el
aviso que otra acababa de agregar (Toast de error ausente, hu10-avisos y hu13-acabado contra
Next.js). Una sesión que no cambió solo renueva su vencimiento.
"""

from importlib import import_module

import pytest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone

pytestmark = pytest.mark.django_db

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def _sesion_nueva() -> str:
    s = SessionStore()
    s["dato"] = "inicial"
    s.create()
    return s.session_key


def test_una_lectura_simultanea_no_pisa_el_aviso_agregado():
    clave = _sesion_nueva()
    lectora = SessionStore(session_key=clave)
    assert lectora["dato"] == "inicial"  # carga la sesión antes de que se agregue el aviso

    escritora = SessionStore(session_key=clave)
    escritora["_messages"] = "aviso"
    escritora.save()

    lectora.save()  # termina después, sin haber cambiado nada (SESSION_SAVE_EVERY_REQUEST)

    assert SessionStore(session_key=clave).get("_messages") == "aviso"


def test_una_sesion_sin_cambios_renueva_su_vencimiento():
    clave = _sesion_nueva()
    Session.objects.filter(session_key=clave).update(
        expire_date=timezone.now() + timezone.timedelta(seconds=60)
    )
    lectora = SessionStore(session_key=clave)
    assert lectora["dato"] == "inicial"
    lectora.save()
    vence = Session.objects.get(session_key=clave).expire_date
    assert vence > timezone.now() + timezone.timedelta(seconds=settings.SESSION_COOKIE_AGE - 60)


def test_una_sesion_modificada_se_guarda_completa():
    clave = _sesion_nueva()
    s = SessionStore(session_key=clave)
    s["dato"] = "cambiado"
    s.save()
    assert SessionStore(session_key=clave)["dato"] == "cambiado"


def test_una_sesion_borrada_no_revive_al_renovarla():
    """Si otra solicitud cerró la sesión (salir), una lectura simultánea no la vuelve a crear."""
    clave = _sesion_nueva()
    lectora = SessionStore(session_key=clave)
    assert lectora["dato"] == "inicial"
    SessionStore(session_key=clave).delete()
    lectora.save()
    assert not Session.objects.filter(session_key=clave).exists()
