"""[003] R-25: el filtro de Sentry quita correos, cookies, autenticación y formularios."""

from quini6.observabilidad import OCULTO, filtrar_evento


def test_filtra_datos_personales_y_formularios():
    evento = {
        "request": {
            "url": "https://quini6.local/mis-jugadas/",
            "cookies": {"sessionid": "x"},
            "data": {"costo": "100"},
            "query_string": "next=/x",
            "headers": {"Cookie": "a", "Authorization": "b", "X-CSRFToken": "c", "User-Agent": "d"},
        },
        "user": {"email": "ana@correo.com"},
        "message": "Falló para ana@correo.com",
    }
    filtrado = filtrar_evento(evento)
    pedido = filtrado["request"]
    assert "cookies" not in pedido and "data" not in pedido and "query_string" not in pedido
    assert pedido["headers"] == {"User-Agent": "d"}
    assert "user" not in filtrado
    assert filtrado["message"] == f"Falló para {OCULTO}"

