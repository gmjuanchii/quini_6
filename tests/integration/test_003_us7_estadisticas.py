"""[003] HU-07: filtros de Estadísticas claros (AC-7.1 a AC-7.6, AC-10.1, RN-05, NFR-009)."""

import html
import json
import re
from datetime import date

import pytest

from dominio.mensajes import MENSAJES
from dominio.tipos import Modalidad
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

PS, LS = Modalidad.PRIMER_SORTEO, Modalidad.LA_SEGUNDA


@pytest.fixture
def sorteos(db):
    """Cuatro sorteos de Primer Sorteo: el 01 sale 4 veces, el 14 una, el 30 dos."""
    juegos = [
        {1, 14, 30, 2, 3, 4},
        {1, 30, 5, 6, 7, 8},
        {1, 9, 10, 11, 12, 13},
        {1, 15, 16, 17, 18, 19},
    ]
    for i, numeros in enumerate(juegos):
        c = crear_concurso(500 + i, date(2025, 2, 1 + i), modalidades=[PS, LS])
        cargar_numeros(c, PS, frozenset(numeros))
        cargar_numeros(c, LS, frozenset({40, 41, 42, 43, 44, 45}))


def _get(client, **params) -> str:
    respuesta = client.get("/estadisticas/", params)
    assert respuesta.status_code == 200
    return respuesta.content.decode()


def _texto(fragmento: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragmento))).strip()


def _etiqueta(contenido: str, id_campo: str) -> str:
    m = re.search(rf'<label\b[^>]*for="{id_campo}"[^>]*>(.*?)</label>', contenido, re.S)
    assert m, f"sin etiqueta para {id_campo}"
    return _texto(m.group(1))


def _entrada(contenido: str, id_campo: str) -> dict[str, str]:
    m = re.search(rf'<input\b[^>]*\bid="{id_campo}"[^>]*>', contenido)
    assert m, f"sin campo {id_campo}"
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', m.group(0))}


def _filas(contenido: str) -> list[str]:
    return re.findall(r'<tr id="frecuencia-(\d\d)">', contenido)


def _encabezados(contenido: str) -> list[str]:
    tabla = contenido[contenido.index("<table") : contenido.index("</thead>")]
    celdas = re.findall(r"<th\b[^>]*>(.*?)</th>", tabla, re.S)
    sin_ocultos = [re.sub(r'<span class="visualmente-oculto">.*?</span>', "", c) for c in celdas]
    return [_texto(c) for c in sin_ocultos]


def test_ac_7_3_etiquetas_breves_y_ayuda_del_numero(client, sorteos):
    contenido = _get(client)
    assert _etiqueta(contenido, "est-modalidad") == "Modalidad"
    assert _etiqueta(contenido, "est-desde") == "Desde"
    assert _etiqueta(contenido, "est-hasta") == "Hasta"
    assert _etiqueta(contenido, "est-numero") == "Número"
    ayuda = re.search(r'<p\b[^>]*id="est-numero_ayuda"[^>]*>(.*?)</p>', contenido, re.S)
    assert _texto(ayuda.group(1)) == MENSAJES["est.numero_ayuda"]
    assert "est-numero_ayuda" in _entrada(contenido, "est-numero")["aria-describedby"]


def test_ac_7_6_numero_con_validacion_previa(client, sorteos):
    reglas = json.loads(_entrada(_get(client), "est-numero")["data-validar"])
    assert {"regla": "rango_00_45", "texto": MENSAJES["jugada.fuera_de_rango"]} in reglas


def test_ac_7_4_consultar_un_numero_separado_del_periodo(client, sorteos):
    contenido = _get(client)
    m = re.search(r"<fieldset\b[^>]*data-consultar-numero[^>]*>(.*?)</fieldset>", contenido, re.S)
    assert m, "falta el bloque «Consultar un número»"
    bloque = m.group(1)
    legend = re.search(r"<legend\b[^>]*>(.*?)</legend>", bloque, re.S)
    assert _texto(legend.group(1)) == MENSAJES["est.consultar_numero"]
    assert 'id="est-numero"' in bloque
    assert 'name="desde"' not in bloque and 'name="modalidad"' not in bloque


def test_ac_7_1_opciones_de_modalidad_completas(client, sorteos):
    contenido = _get(client)
    seleccion = re.search(r'<select\b[^>]*id="est-modalidad"[^>]*>(.*?)</select>', contenido, re.S)
    opciones = [_texto(o) for o in re.findall(r"<option\b[^>]*>(.*?)</option>", seleccion.group(1))]
    assert opciones == [
        "Tradicional – Primer Sorteo",
        "Tradicional – La Segunda",
        "Revancha",
        "Siempre Sale",
    ]


def test_ac_10_1_leyenda_en_aviso_informativo_antes_de_los_resultados(client, sorteos):
    contenido = _get(client)
    m = re.search(r'<div\b[^>]*id="est-leyenda"[^>]*>(.*?)</div>\s*</div>', contenido, re.S)
    assert m and MENSAJES["est.leyenda"] in _texto(m.group(1))
    assert "<svg" in m.group(1)  # icono "info"
    assert contenido.index('id="est-leyenda"') < contenido.index("<table")
    assert 'role="alert"' not in m.group(0) and "<em>" not in m.group(0)


def test_ac_7_5_grafico_accesible_con_titulo_y_descripcion(client, sorteos):
    contenido = _get(client)
    inicio = contenido.index("<svg viewBox=")
    svg = contenido[inicio : contenido.index("</svg>", inicio)]
    assert 'role="img"' in svg and "aria-labelledby=" in svg
    assert re.search(r"<title id=\"grafico-titulo\">[^<]+</title>", svg)
    assert re.search(r"<desc id=\"grafico-descripcion\">[^<]+</desc>", svg)


def test_rn_05_nombres_de_columnas(client, sorteos):
    assert _encabezados(_get(client)) == ["Número", "Frecuencia", "Porcentaje"]


@pytest.mark.parametrize(
    ("orden", "primeros", "columna", "sentido"),
    [
        ("numero", ["00", "01", "02"], "Número", "ascending"),
        ("-numero", ["45", "44", "43"], "Número", "descending"),
        ("-frecuencia", ["01", "30", "02"], "Frecuencia", "descending"),
        ("frecuencia", ["00", "20", "21"], "Frecuencia", "ascending"),
    ],
)
def test_ac_7_5_tabla_ordenable(client, sorteos, orden, primeros, columna, sentido):
    contenido = _get(client, orden=orden)
    assert _filas(contenido)[:3] == primeros
    assert len(_filas(contenido)) == 46
    encabezado = re.search(rf'<th\b[^>]*aria-sort="{sentido}"[^>]*>(.*?)</th>', contenido, re.S)
    assert encabezado and _texto(encabezado.group(1)).startswith(columna)
    assert contenido.count("aria-sort=") == 1


def test_ac_7_5_encabezados_son_enlaces_que_conservan_la_consulta(client, sorteos):
    contenido = _get(client, modalidad="LA_SEGUNDA", orden="-frecuencia")
    enlaces = re.findall(r'<th\b[^>]*>\s*<a href="([^"]+)"', contenido)
    assert len(enlaces) == 2  # "Porcentaje" ordena igual que "Frecuencia": no se ofrece
    for enlace in enlaces:
        assert "modalidad=LA_SEGUNDA" in html.unescape(enlace)
    # La columna ordenada ofrece el sentido contrario; las demás empiezan ascendente.
    assert "orden=frecuencia" in html.unescape(enlaces[1])
    assert "orden=numero" in html.unescape(enlaces[0])


def test_orden_invalido_por_numero_ascendente(client, sorteos):
    contenido = _get(client, orden="cualquiera")
    assert _filas(contenido)[:2] == ["00", "01"]
    assert 'aria-sort="ascending"' in contenido


def test_ac_7_6_numero_fuera_de_rango_junto_al_campo_y_consulta_anterior(client, sorteos):
    contenido = _get(client, numero="46", anterior_modalidad="LA_SEGUNDA", anterior_numero="")
    error = re.search(r'<p\b[^>]*id="est-numero_error"[^>]*>(.*?)</p>', contenido, re.S)
    assert error and " hidden" not in error.group(0).split(">", 1)[0]
    assert _texto(error.group(1)) == MENSAJES["jugada.fuera_de_rango"]
    assert _entrada(contenido, "est-numero")["aria-invalid"] == "true"
    # [001] AC-6.8: se repite la consulta anterior (La Segunda: el 45 salió 4 veces).
    fila = re.search(r'<tr id="frecuencia-45">(.*?)</tr>', contenido, re.S).group(1)
    assert _texto(fila) == "45 4 100,00 %"


def test_nfr_009_mismos_valores_que_antes(client, sorteos):
    """El orden es solo presentación: cada fila conserva su frecuencia y porcentaje."""
    por_numero = _get(client)
    por_frecuencia = _get(client, orden="-frecuencia")
    for numero in ("01", "14", "30", "45"):
        patron = rf'<tr id="frecuencia-{numero}">(.*?)</tr>'
        a = _texto(re.search(patron, por_numero, re.S).group(1))
        b = _texto(re.search(patron, por_frecuencia, re.S).group(1))
        assert a == b
    assert _texto(re.search(r'<tr id="frecuencia-01">(.*?)</tr>', por_numero, re.S).group(1)) == (
        "01 4 100,00 %"
    )
