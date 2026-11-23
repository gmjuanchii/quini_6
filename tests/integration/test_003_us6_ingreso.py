"""[003] HU-06: ingresar sin fricción (AC-6.1 a AC-6.7, FR-019 a FR-021; [001] AC-3.5, D-15)."""

import html
import json
import re

import pytest

from dominio.mensajes import MENSAJES
from tests.fabricas import CLAVE, crear_usuario

pytestmark = pytest.mark.django_db


def _entrada(contenido: str, nombre: str) -> dict[str, str]:
    m = re.search(rf'<input\b[^>]*\bname="{nombre}"[^>]*>', contenido)
    assert m, f"no está el campo {nombre}"
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', m.group(0))}


def _reglas(contenido: str, nombre: str) -> dict[str, dict]:
    return {r["regla"]: r for r in json.loads(_entrada(contenido, nombre)["data-validar"])}


def _texto(fragmento: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragmento)).strip()


@pytest.mark.parametrize(
    ("ruta", "autocompletar"),
    [("/ingresar/", "current-password"), ("/registrarse/", "new-password")],
)
def test_ac_6_5_autocompletado_para_gestores_de_contrasenas(client, ruta, autocompletar):
    contenido = client.get(ruta).content.decode()
    assert _entrada(contenido, "email")["autocomplete"] == "email"
    contrasena = _entrada(contenido, "password")
    assert contrasena["autocomplete"] == autocompletar
    assert contrasena["type"] == "password"


@pytest.mark.parametrize("ruta", ["/ingresar/", "/registrarse/"])
def test_ac_6_1_tarjeta_centrada_y_validacion_previa(client, ruta):
    contenido = client.get(ruta).content.decode()
    assert "data-tarjeta-cuenta" in contenido
    formulario = re.search(r"<form\b[^>]*>", contenido.split("<main", 1)[1]).group(0)
    assert "novalidate" in formulario and "data-validar-formulario" in formulario
    correo = _reglas(contenido, "email")
    assert correo["requerido"]["texto"] == MENSAJES["cuenta.falta_correo"]
    assert correo["correo"]["texto"] == MENSAJES["cuenta.correo_invalido"]
    assert (
        _reglas(contenido, "password")["requerido"]["texto"] == MENSAJES["cuenta.falta_contrasena"]
    )


def test_ac_6_2_mostrar_contrasena_sin_scripts_no_aparece(client):
    contenido = client.get("/ingresar/").content.decode()
    boton = re.search(r"<button\b[^>]*data-mostrar-contrasena[^>]*>", contenido).group(0)
    # Sin scripts no se muestra (html:not(.js) .solo-con-scripts); con scripts, desde el inicio.
    assert "solo-con-scripts" in boton and 'aria-pressed="false"' in boton
    assert 'aria-live="polite"' in contenido


def test_ac_6_3_sin_recuperacion_de_contrasena(client):
    contenido = client.get("/ingresar/").content.decode().lower()
    assert "olvid" not in contenido and "recuper" not in contenido


def test_ac_6_6_boton_con_estado_de_trabajo(client):
    contenido = client.get("/ingresar/").content.decode()
    assert f'data-texto-trabajando="{MENSAJES["cuenta.ingresando"]}"' in contenido
    contenido = client.get("/registrarse/").content.decode()
    assert f'data-texto-trabajando="{MENSAJES["form.trabajando_crear_cuenta"]}"' in contenido


def _alternativa(contenido: str) -> tuple[str, str]:
    bloque = re.search(r"<p\b[^>]*data-alternativa[^>]*>(.*?)</p>", contenido, re.S).group(1)
    return re.search(r'href="([^"]+)"', bloque).group(1), _texto(bloque)


def test_ac_6_7_alternativas_separadas_y_conservan_next(client):
    contenido = client.get("/ingresar/?next=/mis-jugadas/nueva/").content.decode()
    assert _alternativa(contenido) == (
        "/registrarse/?next=/mis-jugadas/nueva/",
        MENSAJES["cuenta.ir_a_registro"],
    )
    contenido = client.get("/registrarse/?next=/mis-jugadas/").content.decode()
    assert _alternativa(contenido) == (
        "/ingresar/?next=/mis-jugadas/",
        MENSAJES["cuenta.ir_a_ingreso"],
    )


def test_ac_6_4_credenciales_incorrectas_sin_revelar_cual(client):
    crear_usuario("ana@prueba.local")
    existente = client.post("/ingresar/", {"email": "ana@prueba.local", "password": "otra-clave"})
    inexistente = client.post("/ingresar/", {"email": "nadie@prueba.local", "password": CLAVE})
    for respuesta in (existente, inexistente):
        assert MENSAJES["cuenta.credenciales_incorrectas"] in respuesta.content.decode()
    assert existente.status_code == inexistente.status_code == 200


def test_ac_6_4_correo_invalido_junto_al_campo(client):
    contenido = client.post(
        "/registrarse/", {"email": "ana@", "password": "x" * 8}
    ).content.decode()
    error = re.search(r'<p\b[^>]*id="id_email_error"[^>]*>(.*?)</p>', contenido, re.S)
    assert _texto(error.group(1)) == MENSAJES["cuenta.correo_invalido"]


def test_faltan_datos_al_ingresar(client):
    contenido = client.post("/ingresar/", {"email": "", "password": ""}).content.decode()
    assert MENSAJES["cuenta.falta_correo"] in contenido
    assert MENSAJES["cuenta.falta_contrasena"] in contenido
