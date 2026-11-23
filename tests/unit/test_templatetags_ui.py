"""[003] R-04, R-05, R-13: filtros de plantilla {% msg %}, {% clases %} e {% icono %}."""

import json

import pytest
from django.conf import settings
from django.template import Context, Template, TemplateSyntaxError


def _render(texto: str, **contexto) -> str:
    return Template("{% load ui %}" + texto).render(Context(contexto))


def _variantes():
    return json.loads((settings.BASE_DIR / "ui" / "variantes.json").read_text(encoding="utf-8"))


def test_msg_sin_variables():
    assert _render('{% msg "nav.menu" %}') == "Menú"


def test_msg_con_variables():
    assert _render('{% msg "pag.pagina" n=1 m=15 %}') == "Página 1 de 15"


def test_msg_con_clave_en_variable():
    assert _render("{% msg clave %}", clave="nav.salir") == "Salir"


def test_msg_escapa_los_valores():
    assert "&lt;b&gt;" in _render('{% msg "ext.filtro_aplicado" filtro=valor %}', valor="<b>")


def test_clases_base_mas_variante():
    v = _variantes()["boton"]
    salida = _render('{% clases "boton" variante="destructivo" %}')
    for clase in (v["base"] + " " + v["variantes"]["destructivo"]).split():
        assert clase in salida.split()


def test_clases_con_tamano_y_extra():
    v = _variantes()["boton"]
    salida = _render('{% clases "boton" variante="principal" tamano="sm" extra="w-full" %}').split()
    assert set(v["tamanos"]["sm"].split()) <= set(salida)
    assert "w-full" in salida


def test_clases_variante_inexistente_es_un_error():
    with pytest.raises(TemplateSyntaxError):
        _render('{% clases "boton" variante="no-existe" %}')


def test_icono_accesible():
    salida = _render('{% icono "circle-check" %}')
    assert salida.startswith("<svg")
    assert 'aria-hidden="true"' in salida
    assert 'focusable="false"' in salida


def test_icono_con_clase():
    assert 'class="size-4' in _render('{% icono "circle-check" clase="size-4" %}')


def test_icono_fuera_de_la_lista_es_un_error():
    with pytest.raises(TemplateSyntaxError):
        _render('{% icono "no-existe" %}')


def test_accion_formulario_agrega_la_marca_de_django():
    """[003] R-20: ``{% accion_formulario %}`` agrega la marca sin perder los parámetros."""
    from django.template import Context, Template
    from django.test import RequestFactory

    plantilla = Template(
        '{% load ui %}{% accion_formulario %}|{% accion_formulario "/salir/" %}|'
        '{% accion_formulario "/a/" 7 "/eliminar/?x=1" %}'
    )
    request = RequestFactory().get("/b/?pagina=2&_interfaz=django")
    assert plantilla.render(Context({"request": request})) == (
        "/b/?pagina=2&amp;_interfaz=django|/salir/?_interfaz=django|"
        "/a/7/eliminar/?x=1&amp;_interfaz=django"
    )


def test_los_enlaces_no_conservan_la_marca_de_los_formularios():
    from quini6.tablas import con_parametros

    assert con_parametros({"_interfaz": "django", "estado": "en-curso"}, pagina=2) == (
        "?estado=en-curso&pagina=2"
    )
