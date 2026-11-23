"""[003] HU-09: nombres de columnas uniformes y fechas dd/mm/aaaa (AC-9.3, AC-9.5, RN-05;
contracts/mensajes.md § 5)."""

import re
from datetime import date, datetime
from decimal import Decimal

import pytest
from django.utils import timezone

from dominio.tipos import Modalidad
from jugadas.models import Jugada
from tests.extraccion_estados import crear_extraccion
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

#: RN-05: un mismo dato, un mismo nombre en todas las pantallas.
NOMBRES_UNICOS = {
    "Fecha",
    "Período",
    "Estado",
    "Fecha del sorteo",
    "Sorteo",
    "Modalidad",
    "Frecuencia",
    "Porcentaje",
    "Aciertos",
}
#: Formas que RN-05 reemplaza por un nombre único.
PROHIBIDOS = {
    "Período consultado",
    "Concurso",
    "Número de concurso",
    "Apariciones",
    "Fecha de sorteo",
    "Fecha del concurso",
}


def _encabezados_de_columna(contenido: str) -> list[str]:
    celdas = re.findall(r'<th\b[^>]*scope="col"[^>]*>(.*?)</th>', contenido, re.S)
    textos = []
    for celda in celdas:
        celda = re.sub(r'<span class="visualmente-oculto">.*?</span>', "", celda, flags=re.S)
        texto = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", celda)).strip()
        if texto:
            textos.append(texto)
    return textos


@pytest.fixture
def datos(admin, usuario_a):
    concurso = crear_concurso(3300, date(2025, 3, 2), modalidades=[Modalidad.PRIMER_SORTEO])
    cargar_numeros(concurso, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
    jugada = Jugada(usuario=usuario_a, concurso=concurso, costo=Decimal("100"))
    jugada.asignar_numeros((1, 2, 3, 10, 11, 12))
    jugada.save()
    momento = timezone.make_aware(datetime(2026, 11, 21, 12, 15))
    return crear_extraccion(admin, "con-advertencias", momento)


def _paginas(cliente_admin, cliente_a, extraccion) -> dict[str, str]:
    return {
        "Extracción histórica": cliente_admin.get("/administracion/extracciones/"),
        "Detalle de extracción": cliente_admin.get(
            f"/administracion/extracciones/{extraccion.pk}/"
        ),
        "Resultados": cliente_a.get("/resultados/"),
        "Mis jugadas": cliente_a.get("/mis-jugadas/"),
        "Administración": cliente_admin.get("/administracion/concursos/"),
    }


def test_rn_05_encabezados_con_nombres_unicos(cliente_admin, cliente_a, datos):
    for pantalla, respuesta in _paginas(cliente_admin, cliente_a, datos).items():
        assert respuesta.status_code == 200, pantalla
        encabezados = _encabezados_de_columna(respuesta.content.decode())
        assert encabezados, f"{pantalla}: sin tabla"
        assert not set(encabezados) & PROHIBIDOS, (pantalla, encabezados)


@pytest.mark.parametrize(
    ("pantalla", "esperados"),
    [
        ("Extracción histórica", {"Fecha", "Período", "Estado"}),
        ("Detalle de extracción", {"Sorteo", "Fecha del sorteo", "Estado"}),
        ("Resultados", {"Sorteo", "Fecha del sorteo", "Estado"}),
        ("Mis jugadas", {"Sorteo", "Fecha del sorteo", "Aciertos"}),
        ("Administración", {"Sorteo", "Fecha del sorteo", "Modalidad"}),
    ],
)
def test_ac_9_5_cada_pantalla_usa_los_nombres(cliente_admin, cliente_a, datos, pantalla, esperados):
    contenido = _paginas(cliente_admin, cliente_a, datos)[pantalla].content.decode()
    assert esperados <= set(_encabezados_de_columna(contenido)) & NOMBRES_UNICOS


def test_ac_9_3_tablas_apilables_con_rotulos(cliente_admin, cliente_a, datos):
    for pantalla, respuesta in _paginas(cliente_admin, cliente_a, datos).items():
        contenido = respuesta.content.decode()
        tablas = re.findall(r"<table\b[^>]*>", contenido)
        assert any("apilable" in t for t in tablas), pantalla
        assert re.search(r'<td\b[^>]*data-rotulo="[^"]+"', contenido), pantalla


def test_ac_9_5_fechas_con_formato_uniforme(cliente_admin, cliente_a, datos):
    paginas = _paginas(cliente_admin, cliente_a, datos)
    assert "21/11/2026 12:15" in paginas["Extracción histórica"].content.decode()
    for pantalla in ("Resultados", "Mis jugadas", "Administración"):
        assert "02/03/2025" in paginas[pantalla].content.decode(), pantalla
    for respuesta in paginas.values():
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", _visible(respuesta.content.decode()))


def _visible(contenido: str) -> str:
    """Texto visible aproximado: sin etiquetas ni valores de atributos (las fechas ISO de los
    campos de fecha y de los atributos data- no se muestran)."""
    sin_scripts = re.sub(r"<(script|template|style)\b.*?</\1>", " ", contenido, flags=re.S)
    return re.sub(r"<[^>]+>", " ", sin_scripts)
