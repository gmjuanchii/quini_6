"""[002] R-04, NFR-010: árbol mínimo de HTML sobre html.parser (T011)."""

from extracciones.fuentes.html import analizar, bloques_de_datos


def test_tablas_anidadas_no_mezclan_filas():
    raiz = analizar(
        "<table id='a'><tr><td>1</td><td><table id='b'><tr><td>x</td></tr></table></td></tr>"
        "<tr><td>2</td></tr></table>"
    )
    externa = raiz.buscar("table", id="a")
    filas = externa.filas()
    assert len(filas) == 2
    assert [c.texto() for c in filas[1].celdas()] == ["2"]
    interna = raiz.buscar("table", id="b")
    assert [f.texto() for f in interna.filas()] == ["x"]


def test_etiquetas_sin_cerrar():
    raiz = analizar("<table><tr><td>6<td>Vacante<td>1.100<tr><td>5<td>18<td>3.013</table>")
    filas = raiz.buscar("table").filas()
    assert [[c.texto() for c in f.celdas()] for f in filas] == [
        ["6", "Vacante", "1.100"],
        ["5", "18", "3.013"],
    ]


def test_entidades_y_espacios_irregulares():
    raiz = analizar("<p class='lead'>  mi&#233;rcoles\n\n 18 &amp;   noviembre<br/>2026 </p>")
    assert raiz.buscar("p", clase="lead").texto() == "miércoles 18 & noviembre 2026"


def test_busqueda_por_clase_e_id():
    raiz = analizar("<div class='card mb-3' id='x'><h3 class='card-title'>TRADICIONAL</h3></div>")
    assert raiz.buscar(clase="card").attr("id") == "x"
    assert raiz.buscar("h3", clase="card-title").texto() == "TRADICIONAL"
    assert raiz.buscar(id="x").etiqueta == "div"


def test_bloque_de_script_de_datos_sin_ejecutarlo():
    raiz = analizar(
        '<script type="application/ld+json">{"name": "Sorteo 3427", "x": "<b>"}</script>'
        "<script>alert(1)</script><p>texto</p>"
    )
    assert bloques_de_datos(raiz) == ['{"name": "Sorteo 3427", "x": "<b>"}']
    assert raiz.texto() == "texto"


def test_html_malformado_no_lanza_excepcion():
    for html in ["", "<<<>>>", "</div></p>", "<table><tr><td>", "<a href='x'", None]:
        raiz = analizar(html)
        assert raiz.etiqueta == "#documento"


def test_ancestro_y_siguiente_elemento():
    raiz = analizar("<div class='shadow'><h2>Revancha</h2><div class='draw-numbers'>07</div></div>")
    numeros = raiz.buscar("div", clase="draw-numbers")
    assert numeros.ancestro("div", clase="shadow") is not None
    assert raiz.buscar("h2").siguiente_elemento() is numeros
