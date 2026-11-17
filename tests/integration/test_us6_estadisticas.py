"""US6 — Estadísticas históricas de frecuencia (AC-6.1 a AC-6.11; RN-41, RN-46, RN-47)."""

import re
from datetime import date

import pytest

from dominio.tipos import Modalidad
from tests.fabricas import cargar_numeros, crear_concurso, marcar_en_revision

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)
LEYENDA = "Estadística descriptiva de sorteos pasados. No predice resultados futuros."


@pytest.fixture
def sorteos(db):
    """Ocho concursos de enero de 2025. En Primer Sorteo, el 14 sale una sola vez."""
    for i in range(8):
        c = crear_concurso(100 + i, date(2025, 1, 1 + i * 3), modalidades=[PS, LS])
        ps = {14, 1, 2, 3, 4, 5} if i == 0 else {20 + i, 1, 2, 3, 4, 5}
        cargar_numeros(c, PS, frozenset(ps))
        cargar_numeros(c, LS, frozenset({40, 41, 42, 43, 44, 14}))
    return None


def _get(client, **params):
    r = client.get("/estadisticas/", params)
    assert r.status_code == 200
    return r.content.decode()


def _fila(contenido, numero):
    m = re.search(rf'<tr id="frecuencia-{numero:02d}">(.*?)</tr>', contenido, re.S)
    assert m, f"no está la fila de {numero:02d}"
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()


class TestConsulta:
    def test_ac_6_1_predeterminado(self, client, sorteos):
        contenido = _get(client)
        assert "Tradicional – Primer Sorteo" in contenido
        assert "<svg" in contenido and 'role="img"' in contenido
        assert contenido.count('<tr id="frecuencia-') == 46
        assert "8 sorteos considerados" in contenido
        assert "01/01/2025" in contenido and "22/01/2025" in contenido
        assert _fila(contenido, 1) == "01 8 100,00 %"
        assert LEYENDA in contenido

    def test_ac_6_2_cambio_de_modalidad(self, client, sorteos):
        contenido = _get(client, modalidad="LA_SEGUNDA")
        assert _fila(contenido, 14) == "14 8 100,00 %"
        assert _fila(contenido, 1) == "01 0 0,00 %"

    def test_ac_6_3_periodo(self, client, sorteos):
        contenido = _get(client, desde="04/01/2025", hasta="10/01/2025")
        assert "3 sorteos considerados" in contenido
        assert _fila(contenido, 14) == "14 0 0,00 %"

    def test_ac_6_5_numero_sin_apariciones(self, client, sorteos):
        assert _fila(_get(client), 45) == "45 0 0,00 %"


class TestMensajes:
    def test_ac_6_4_sin_sorteos(self, client, sorteos):
        contenido = _get(client, desde="01/06/2025")
        assert (
            "No hay sorteos publicados de Tradicional – Primer Sorteo en el período seleccionado"
        ) in contenido
        assert "<svg" not in contenido and 'id="frecuencia-' not in contenido
        assert LEYENDA in contenido

    def test_ac_6_4_sin_datos(self, client, db):
        contenido = _get(client)
        assert (
            "No hay sorteos publicados de Tradicional – Primer Sorteo en el período seleccionado"
        ) in contenido

    def test_ac_6_6_numero(self, client, sorteos):
        contenido = _get(client, numero="14")
        bloque = contenido[contenido.index('id="numero-consultado"') :][:400]
        assert "salió en 1 de 8 sorteos" in bloque
        assert "12,50 %" in bloque

    def test_ac_6_7_concursos_sin_informacion(self, client, sorteos):
        crear_concurso(200, date(2025, 1, 30), modalidades=[PS])
        otro = crear_concurso(201, date(2025, 1, 31), modalidades=[PS])
        cargar_numeros(otro, PS, frozenset({1, 2, 3, 4, 5, 6}), estado="BORRADOR")
        crear_concurso(202, date(2025, 1, 31), modalidades=[LS])  # no aplica a Primer Sorteo
        contenido = _get(client)
        assert (
            "El período incluye 2 concursos sin información disponible para esta modalidad"
            in contenido
        )

    def test_ac_6_8_periodo_invalido_repite_consulta_anterior(self, client, sorteos):
        contenido = _get(
            client,
            modalidad="PRIMER_SORTEO",
            desde="10/01/2025",
            hasta="01/01/2025",
            numero="",
            anterior_modalidad="LA_SEGUNDA",
            anterior_desde="04/01/2025",
            anterior_hasta="10/01/2025",
            anterior_numero="14",
        )
        assert (
            "La fecha desde no puede ser posterior a la fecha hasta. Corregí el período."
            in contenido
        )
        assert "3 sorteos considerados" in contenido
        assert _fila(contenido, 14) == "14 3 100,00 %"
        assert 'name="anterior_modalidad" value="LA_SEGUNDA"' in contenido
        assert 'name="anterior_desde" value="04/01/2025"' in contenido
        assert 'name="anterior_numero" value="14"' in contenido

    def test_ac_6_8_sin_consulta_anterior_usa_predeterminados(self, client, sorteos):
        contenido = _get(client, desde="10/01/2025", hasta="01/01/2025")
        assert "La fecha desde no puede ser posterior a la fecha hasta." in contenido
        assert "8 sorteos considerados" in contenido

    def test_campos_ocultos_con_la_consulta_mostrada(self, client, sorteos):
        contenido = _get(client, modalidad="LA_SEGUNDA", numero="7")
        assert 'name="anterior_modalidad" value="LA_SEGUNDA"' in contenido
        assert 'name="anterior_numero" value="07"' in contenido


class TestDatos:
    def test_ac_6_11_valores_corregidos(self, client, db):
        c = crear_concurso(1, date(2025, 1, 1), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 7}), es_correccion=True)
        contenido = _get(client)
        assert _fila(contenido, 6) == "06 0 0,00 %"
        assert _fila(contenido, 7) == "07 1 100,00 %"

    def test_rn_41_revision_entra_borrador_no(self, client, db):
        a = crear_concurso(1, date(2025, 1, 1), modalidades=[PS])
        cargar_numeros(a, PS, frozenset({1, 2, 3, 4, 5, 6}))
        marcar_en_revision(a, PS, "numeros", "Revisar")
        b = crear_concurso(2, date(2025, 1, 2), modalidades=[PS])
        cargar_numeros(b, PS, frozenset({40, 41, 42, 43, 44, 45}), estado="BORRADOR")
        contenido = _get(client)
        assert "1 sorteo considerado" in contenido
        assert _fila(contenido, 1) == "01 1 100,00 %"
        assert _fila(contenido, 45) == "45 0 0,00 %"

    def test_rn_46_premio_extra_no_se_ofrece(self, client, sorteos):
        contenido = _get(client, modalidad="PREMIO_EXTRA")
        assert "Premio Extra no se ofrece en las estadísticas" in contenido
        assert 'value="PREMIO_EXTRA"' not in contenido
        assert "8 sorteos considerados" in contenido

    def test_rn_47_sin_recomendaciones(self, client, sorteos):
        contenido = _get(client).lower()
        for palabra in ("recomendado", "caliente", "frío", "frio"):
            assert palabra not in contenido


def test_grafico_sin_decimales_localizados(client, sorteos):
    """Los atributos del SVG usan punto decimal aunque la página esté en es-AR."""
    contenido = _get(client, desde="04/01/2025", hasta="10/01/2025")
    svg = contenido[contenido.index("<svg") : contenido.index("</svg>")]
    assert not re.search(r'(?:x|y|width|height)="[\d.]*,', svg)
    assert svg.count('class="barra') == 46
