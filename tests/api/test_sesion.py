"""[003] contracts/api.md § 2: GET /api/v1/sesion/."""


def test_visitante_sin_sesion(visitante):
    respuesta = visitante.get("/api/v1/sesion/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"correo": None, "es_administrador": False, "vence_en": None}
    assert "csrftoken" in respuesta.cookies
    assert respuesta["Cache-Control"] == "no-store"


def test_usuario_con_sesion(usuario):
    datos = usuario.get("/api/v1/sesion/").json()
    assert datos["correo"] == "usuaria@api.local"
    assert datos["es_administrador"] is False
    assert datos["vence_en"]


def test_administrador(administrador):
    assert administrador.get("/api/v1/sesion/").json()["es_administrador"] is True
