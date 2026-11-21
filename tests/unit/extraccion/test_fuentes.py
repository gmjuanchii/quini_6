"""Intérpretes de F1, F2 y F3 con copias de páginas reales ([002] R-04; T021, T064, T065).

Los intérpretes solo extraen textos sin interpretar y nunca lanzan excepciones.
"""

import pytest

from dominio.extraccion.tipos import FilaPremioCruda, NoReconocida, PaginaCruda
from extracciones.fuentes import f1, f2, f3
from tests.extraccion_falsos import leer


def bloque(pagina: PaginaCruda, rotulo: str, con_filas=None):
    for b in pagina.bloques:
        if b.rotulo == rotulo and (con_filas is None or (b.filas_premios is not None) == con_filas):
            return b
    raise AssertionError(f"Sin bloque {rotulo}")


# -- F2 (T021) --------------------------------------------------------------------


def test_f2_detalle_devuelve_textos_sin_interpretar():
    pagina = f2.interpretar_sorteo(leer("f2/sorteo-3426.html"))
    assert isinstance(pagina, PaginaCruda)
    assert pagina.numero_texto == "3426"
    assert pagina.fecha_texto == "15/11/2026"
    assert [b.rotulo for b in pagina.bloques] == [
        "TRADICIONAL", "LA SEGUNDA", "REVANCHA", "SIEMPRE SALE", "POZO EXTRA",
    ]  # fmt: skip
    tradicional = bloque(pagina, "TRADICIONAL")
    assert tradicional.numeros_textos == ("02", "01", "39", "13", "10", "38")
    assert tradicional.filas_premios[0] == FilaPremioCruda("6", "Vacante", "1.100.000.000")
    assert tradicional.filas_premios[1] == FilaPremioCruda("5", "18", "3.013.912")
    extra = bloque(pagina, "POZO EXTRA")
    assert "" not in extra.numeros_textos  # el <span> vacío de F2 se descarta


def test_f2_listado_devuelve_numero_y_fecha():
    referencias = f2.interpretar_listado(leer("f2/listado.html"))
    assert len(referencias) == 20
    assert (referencias[0].numero_texto, referencias[0].fecha_texto) == ("3427", "18/11/2026")
    assert (referencias[-1].numero_texto, referencias[-1].fecha_texto) == ("3408", "13/09/2026")


@pytest.mark.parametrize("modulo", [f1, f2, f3])
@pytest.mark.parametrize("html", ["", "<html><body><h1>Otra cosa</h1></body></html>", "<<<", None])
def test_pagina_irreconocible_sin_excepcion(modulo, html):
    assert isinstance(modulo.interpretar_sorteo(html), NoReconocida)
    assert modulo.interpretar_listado(html) == []


def test_f2_pagina_de_error_500_no_se_reconoce():
    assert isinstance(f2.interpretar_sorteo(leer("f2/inexistente-500.html")), NoReconocida)


# -- F1 (T064) --------------------------------------------------------------------


def test_f1_listado():
    referencias = f1.interpretar_listado(leer("f1/listado.html"))
    pares = [(r.numero_texto, r.fecha_texto) for r in referencias]
    assert ("3422", "01-11-2026") in pares and ("3405", "02-09-2026") in pares
    assert len(pares) == 23


def test_f1_detalle_con_bloques_de_numeros_y_de_premios():
    pagina = f1.interpretar_sorteo(leer("f1/sorteo-3426.html"))
    assert pagina.numero_texto == "3426"
    assert "15-11-2026" in pagina.fecha_texto
    tradicional = bloque(pagina, "SORTEO TRADICIONAL", con_filas=False)
    assert tradicional.numeros_textos == ("01 - 02 - 10 - 13 - 38 - 39",)
    premios = bloque(pagina, "SORTEO TRADICIONAL", con_filas=True)
    assert premios.filas_premios[0] == FilaPremioCruda("6", "Vacante", "$ 1.100.000.000")
    revancha = bloque(pagina, "LA SEGUNDA DEL QUINI 6 REVANCHA", con_filas=True)
    assert len(revancha.filas_premios) == 1
    # Premio Extra: pozo en el rótulo, sin números propios y aciertos "-".
    extra = bloque(pagina, "POZO EXTRA")
    assert extra.pozo_texto == "55 millones de pesos"
    assert extra.numeros_textos is None
    assert bloque(pagina, "QUINI 6 POZO EXTRA").filas_premios[0].aciertos_texto == "-"


# -- F3 (T065) --------------------------------------------------------------------


def test_f3_listado_agrupado_por_mes():
    referencias = f3.interpretar_listado(leer("f3/listado.html"))
    pares = {(r.numero_texto, r.fecha_texto) for r in referencias}
    assert ("3427", "18/11/2026") in pares  # tarjetas recientes
    assert ("3324", "23/11/2025") in pares  # tabla del histórico, "d/m/aaaa"
    assert len(referencias) == 104


def test_f3_detalle():
    pagina = f3.interpretar_sorteo(leer("f3/sorteo-3398.html"))
    assert pagina.numero_texto == "3398"
    assert pagina.fecha_texto == "domingo 09 de agosto de 2026"
    assert [b.rotulo for b in pagina.bloques] == [
        "Tradicional Primer Sorteo", "La Segunda del Quini", "Revancha", "Siempre Sale",
        "Pozo Extra",
    ]  # fmt: skip
    tradicional = bloque(pagina, "Tradicional Primer Sorteo")
    assert tradicional.filas_premios[1] == FilaPremioCruda("5", "232", "494,443,71")
    assert tradicional.filas_premios[0].ganadores_texto == "Pozo Vacante"


def test_f3_bloque_de_datos_que_no_coincide_con_el_html():
    html = leer("f3/sorteo-3427.html").replace('"name":"Sorteo 3427"', '"name":"Sorteo 3400"')
    assert isinstance(f3.interpretar_sorteo(html), NoReconocida)


def test_f3_sin_bloque_de_datos_o_ilegible_no_es_error():
    sin_bloque = leer("f3/sorteo-3427.html").replace("application/ld+json", "text/plain")
    assert isinstance(f3.interpretar_sorteo(sin_bloque), PaginaCruda)
    roto = leer("f3/sorteo-3427.html").replace('{"@context"', '{roto "@context"')
    assert isinstance(f3.interpretar_sorteo(roto), PaginaCruda)
