"""[003] HU-05: sección activa, menú de cuenta, saltar al contenido, logotipo, favicon y caminos
de regreso (AC-5.1 a AC-5.7, FR-014 a FR-018, RN-08)."""

import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from dominio.extraccion.tipos import Fuente
from dominio.mensajes import MENSAJES, mensaje
from jugadas.models import Jugada
from quini6.templatetags.formato_ar import fecha_hora_ar
from tests.fabricas import crear_concurso

pytestmark = pytest.mark.django_db


def _nav(contenido: str) -> str:
    m = re.search(r'<nav\b[^>]*id="nav-principal".*?</nav>', contenido, re.S)
    assert m, "no está la navegación principal"
    return m.group(0)


def _activos(contenido: str) -> list[str]:
    return re.findall(r'<a\b[^>]*href="([^"]+)"[^>]*aria-current="page"', _nav(contenido))


def _sin_etiquetas(fragmento: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragmento)).strip()


@pytest.mark.parametrize(
    ("ruta", "activo"),
    [
        ("/resultados/", "/resultados/"),
        ("/estadisticas/", "/estadisticas/"),
        ("/mis-jugadas/", "/mis-jugadas/"),
        ("/administracion/concursos/", "/administracion/concursos/"),
        ("/administracion/extracciones/", "/administracion/concursos/"),
    ],
)
def test_ac_5_1_la_seccion_actual_se_anuncia(cliente_admin, ruta, activo):
    contenido = cliente_admin.get(ruta).content.decode()
    assert _activos(contenido) == [activo]


def test_ac_5_1_el_detalle_de_un_sorteo_pertenece_a_resultados(client):
    crear_concurso(3420, date(2026, 11, 1))
    assert _activos(client.get("/resultados/3420/").content.decode()) == ["/resultados/"]


def test_ac_5_3_salir_esta_en_el_menu_de_cuenta_con_el_correo(cliente_admin, admin):
    contenido = cliente_admin.get("/resultados/").content.decode()
    menu = re.search(r"<div\b[^>]*data-menu-cuenta.*?</form>", contenido, re.S)
    assert menu, "no está el menú de cuenta"
    assert admin.email in menu.group(0)
    assert f'aria-label="{mensaje("nav.cuenta", correo=admin.email)}"' in menu.group(0)
    assert 'action="/salir/?_interfaz=django"' in menu.group(0)
    assert MENSAJES["nav.salir"] in _sin_etiquetas(menu.group(0))
    lista = re.search(r"<ul\b[^>]*data-secciones.*?</ul>", contenido, re.S).group(0)
    assert MENSAJES["nav.salir"] not in _sin_etiquetas(lista)


def test_sin_sesion_ingresar_y_crear_cuenta(client):
    nav = _nav(client.get("/resultados/").content.decode())
    assert 'href="/ingresar/"' in nav and 'href="/registrarse/"' in nav
    assert "data-menu-cuenta" not in nav
    assert 'href="/mis-jugadas/"' not in nav


def test_ac_5_4_boton_menu_para_pantallas_chicas(client):
    contenido = client.get("/resultados/").content.decode()
    boton = re.search(r"<button\b[^>]*data-boton-menu[^>]*>", contenido).group(0)
    assert 'aria-controls="nav-principal"' in boton
    assert 'aria-expanded="false"' in boton
    assert MENSAJES["nav.menu"] in contenido


def test_ac_5_5_saltar_al_contenido_es_el_primer_enlace(client):
    contenido = client.get("/estadisticas/").content.decode()
    cuerpo = contenido.split("<body", 1)[1]
    primero = re.search(r"<a\b[^>]*>.*?</a>", cuerpo, re.S).group(0)
    assert 'href="#contenido"' in primero
    assert MENSAJES["nav.saltar"] in primero
    assert re.search(r'<main\b[^>]*id="contenido"[^>]*tabindex="-1"', contenido)


def test_ac_5_7_logotipo_y_favicon(client):
    contenido = client.get("/resultados/").content.decode()
    assert re.search(rf'<a\b[^>]*href="/"[^>]*aria-label="{MENSAJES["nav.logotipo"]}"', contenido)
    assert re.search(r'<link rel="icon" href="[^"]*marca/favicon\.svg"', contenido)


@pytest.mark.parametrize("archivo", ["favicon.svg", "logotipo.svg", "isotipo.svg"])
def test_ac_5_7_la_marca_se_publica_en_marca(archivo):
    """ui/marca se publica con el prefijo "marca/" (lo usan collectstatic y WhiteNoise)."""
    from django.contrib.staticfiles.finders import FileSystemFinder

    carpetas = {prefijo: Path(ruta) for prefijo, ruta in FileSystemFinder().locations}
    assert (carpetas["marca"] / archivo).is_file()


def _volver(contenido: str) -> tuple[str, str]:
    m = re.search(r'<a\b[^>]*data-volver[^>]*href="([^"]+)"[^>]*>(.*?)</a>', contenido, re.S)
    assert m, "no está el camino de regreso"
    return m.group(1), _sin_etiquetas(m.group(2))


def _sin_flecha(clave: str, **valores) -> str:
    return mensaje(clave, **valores).removeprefix("← ")


def test_ac_5_6_detalle_de_un_sorteo(client):
    crear_concurso(3420, date(2026, 11, 1))
    destino, texto = _volver(client.get("/resultados/3420/").content.decode())
    assert (destino, texto) == ("/resultados/", _sin_flecha("nav.volver_sorteos"))


def test_ac_5_6_detalle_de_una_extraccion_y_de_un_sorteo_extraido(cliente_admin, monkeypatch):
    from extracciones.models import Extraccion
    from tests.extraccion_falsos import HOY, cliente_con_sorteos, fichas_de, procesar_pendientes

    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)
    cliente_admin.post(
        "/administracion/extracciones/", {"inicio": "01/11/2026", "fin": "15/11/2026"}
    )
    sorteos = {3418 + i: date(2026, 10, 18) + timedelta(days=3 * i) for i in range(10)}
    procesar_pendientes(cliente_con_sorteos(sorteos), fichas_de(Fuente.F2))
    extraccion = Extraccion.objects.get()
    assert extraccion.sorteos.exists(), (extraccion.estado, extraccion.resumen)
    contenido = cliente_admin.get(f"/administracion/extracciones/{extraccion.pk}/").content.decode()
    assert _volver(contenido) == (
        "/administracion/extracciones/",
        _sin_flecha("nav.volver_extracciones"),
    )
    sorteo = extraccion.sorteos.first()
    ruta = f"/administracion/extracciones/{extraccion.pk}/sorteos/{sorteo.numero}/"
    destino, texto = _volver(cliente_admin.get(ruta).content.decode())
    assert destino == f"/administracion/extracciones/{extraccion.pk}/"
    assert texto == _sin_flecha(
        "nav.volver_extraccion", fecha_hora=fecha_hora_ar(extraccion.iniciada_en)
    )


def test_ac_5_6_detalle_de_una_jugada(cliente_a, usuario_a):
    concurso = crear_concurso(3420, date(2026, 11, 1))
    jugada = Jugada.objects.create(
        usuario=usuario_a, concurso=concurso, n1=1, n2=2, n3=3, n4=4, n5=5, n6=6,
        costo=Decimal("1500.00"),
    )  # fmt: skip
    contenido = cliente_a.get(f"/mis-jugadas/{jugada.pk}/").content.decode()
    assert _volver(contenido) == ("/mis-jugadas/", _sin_flecha("nav.volver_jugadas"))


def test_ac_5_6_sorteo_de_administracion(cliente_admin):
    crear_concurso(3420, date(2026, 11, 1))
    contenido = cliente_admin.get("/administracion/concursos/3420/").content.decode()
    assert _volver(contenido) == ("/administracion/concursos/", _sin_flecha("nav.volver_sorteos"))


def test_ac_5_6_la_flecha_es_un_icono_decorativo(client):
    crear_concurso(3420, date(2026, 11, 1))
    contenido = client.get("/resultados/3420/").content.decode()
    enlace = re.search(r"<a\b[^>]*data-volver.*?</a>", contenido, re.S).group(0)
    assert "←" not in enlace and 'aria-hidden="true"' in enlace
