"""US1 — Consultar resultados sin registrarse (AC-1.1 a AC-1.16), siempre sin sesión."""

from datetime import date

import pytest

from dominio.tipos import Modalidad
from tests.fabricas import (
    cargar_numeros,
    cargar_premios,
    crear_concurso,
    marcar_en_revision,
)

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)
PREMIOS_PENDIENTES = "Información de premios pendiente de publicación"


def _texto(client, url):
    r = client.get(url)
    assert r.status_code == 200
    return r.content.decode()


class TestUltimosResultados:
    def test_ac_1_13_sin_resultados(self, client):
        contenido = _texto(client, "/resultados/")
        assert "Todavía no hay resultados publicados" in contenido
        assert "$ " not in contenido
        assert "bolilla" not in contenido

    def test_inicio_redirige(self, client):
        r = client.get("/")
        assert r.status_code == 302 and r["Location"] == "/resultados/"

    def test_ac_1_1_ultimos_resultados(self, client):
        c = crear_concurso(3215, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({40, 7, 3, 21, 14, 32}))
        contenido = _texto(client, "/resultados/")
        assert "Concurso N.º 3215" in contenido
        assert "02/03/2025" in contenido
        posiciones = [contenido.index(f">{n}<") for n in ("03", "07", "14", "21", "32", "40")]
        assert posiciones == sorted(posiciones)
        assert "/ingresar/?" not in contenido

    def test_ac_1_2_pendiente_aparte(self, client):
        viejo = crear_concurso(3215, date(2025, 3, 2))
        cargar_numeros(viejo, PS, frozenset({1, 2, 3, 4, 5, 6}))
        crear_concurso(3216, date(2025, 3, 5))
        contenido = _texto(client, "/resultados/")
        bloque_pendiente = contenido[contenido.index('id="concurso-actual"') :]
        assert "Concurso N.º 3216" in bloque_pendiente[:400]
        assert "Resultados pendientes" in bloque_pendiente[:600]
        bloque_ultimos = contenido[contenido.index('id="ultimos-resultados"') :]
        assert "Concurso N.º 3215" in bloque_ultimos[:400]


class TestBusquedas:
    def test_ac_1_3_por_numero(self, client):
        crear_concurso(3215, date(2025, 3, 2))
        r = client.get("/resultados/buscar/", {"numero": "3215"})
        assert r.status_code == 302 and r["Location"] == "/resultados/3215/"

    def test_ac_1_3_por_fecha(self, client):
        crear_concurso(3215, date(2025, 3, 2))
        crear_concurso(3216, date(2025, 3, 5))
        contenido = _texto(client, "/resultados/buscar/?fecha=02/03/2025")
        assert "/resultados/3215/" in contenido
        assert "/resultados/3216/" not in contenido

    def test_ac_1_4_numero_inexistente(self, client):
        crear_concurso(3215, date(2025, 3, 2))
        contenido = _texto(client, "/resultados/buscar/?numero=9999")
        assert "No hay información del concurso N.º 9999" in contenido
        assert "3215" not in contenido

    def test_p07_fecha_sin_concursos(self, client):
        crear_concurso(3215, date(2025, 3, 2))
        contenido = _texto(client, "/resultados/buscar/?fecha=01/01/2025")
        assert "No hay información de concursos del 01/01/2025" in contenido
        assert "3215" not in contenido

    @pytest.mark.parametrize("consulta", ["numero=abc", "fecha=2025-03-02", "fecha=31/02/2025"])
    def test_formato_invalido(self, client, consulta):
        contenido = _texto(client, f"/resultados/buscar/?{consulta}")
        assert "Ingresá" in contenido

    def test_detalle_inexistente_404(self, client):
        r = client.get("/resultados/9999/")
        assert r.status_code == 404
        assert "La página que buscás no existe" in r.content.decode()


class TestEstados:
    def test_ac_1_5_incompleto_y_pendientes(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS, LS, RV])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_numeros(c, LS, frozenset({11, 12, 13, 14, 15, 16}), estado="BORRADOR")
        contenido = _texto(client, "/resultados/1/")
        assert "Incompleto" in contenido
        assert "Resultado pendiente" in contenido  # Revancha sin cargar
        assert "Pendiente de validación" in contenido  # La Segunda en Borrador
        assert ">11<" not in contenido and ">16<" not in contenido

    def test_ac_1_6_completo(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_premios(c, PS)
        assert "Completo" in _texto(client, "/resultados/1/")

    def test_ac_1_16_no_aplicable(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_premios(c, PS)
        contenido = _texto(client, "/resultados/1/")
        assert "Revancha" not in contenido
        assert "Siempre Sale" not in contenido
        assert "Completo" in contenido


class TestPremios:
    def test_ac_1_7_rotulos_por_dato(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_premios(
            c,
            PS,
            {
                "SEGUNDO": {
                    "ganadores": 3,
                    "importe_categoria": "4501.50",
                    "importe_individual": "1500.50",
                    "pozo_vacante_acumulado": "100",
                }
            },
        )
        contenido = _texto(client, "/resultados/1/")
        for rotulo in (
            "Ganadores",
            "Importe destinado a la categoría",
            "Importe individual por ganador",
            "Pozo vacante o acumulado",
            "Segundo Premio",
            "5 aciertos",
        ):
            assert rotulo in contenido
        assert "$ 1.500,50" in contenido and "$ 4.501,50" in contenido
        assert "3 ganadores" in contenido

    def test_ac_1_8_premios_pendientes(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_premios(c, PS, {"PRIMER": {"ganadores": 9}}, estado="BORRADOR")
        contenido = _texto(client, "/resultados/1/")
        assert PREMIOS_PENDIENTES in contenido
        assert "9 ganadores" not in contenido

    def test_ac_1_9_sin_importe_individual(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[RV])
        cargar_numeros(c, RV, frozenset({1, 2, 3, 4, 5, 6}))
        cargar_premios(c, RV, {"UNICO": {"ganadores": 2, "importe_categoria": "1000"}})
        contenido = _texto(client, "/resultados/1/")
        assert PREMIOS_PENDIENTES in contenido
        assert "$ 500,00" not in contenido
        assert "Importe individual no disponible" not in contenido

    def test_ac_1_10_cero_ganadores(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS, RV])
        cargar_premios(c, PS, {"PRIMER": {"ganadores": 0, "pozo_vacante_acumulado": "1000000"}})
        cargar_premios(c, RV, {"UNICO": {"ganadores": 0}})
        contenido = _texto(client, "/resultados/1/")
        assert "0 ganadores" in contenido
        assert "$ 1.000.000,00" in contenido
        assert contenido.count("Pozo vacante o acumulado") == 1


class TestRevisionYCorreccion:
    def test_ac_1_11_corregido(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}), publicada_en=date(2025, 3, 3))
        cargar_numeros(
            c, PS, frozenset({1, 2, 3, 4, 5, 7}), es_correccion=True, publicada_en=date(2025, 3, 6)
        )
        contenido = _texto(client, "/resultados/1/")
        assert "Corregido el 06/03/2025" in contenido
        assert ">07<" in contenido

    def test_ac_1_12_en_revision(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}))
        marcar_en_revision(c, PS, "numeros", "Posible error")
        contenido = _texto(client, "/resultados/1/")
        assert "Información en revisión" in contenido
        assert ">06<" in contenido
        assert "Posible error" not in contenido


class TestPremioExtraYFuente:
    def _concurso(self):
        return crear_concurso(1, date(2025, 3, 2))

    def test_ac_1_14_conjunto(self, client):
        c = self._concurso()
        cargar_numeros(c, PS, frozenset({2, 9, 16, 25, 34, 45}))
        cargar_numeros(c, LS, frozenset({2, 11, 16, 23, 35, 42}))
        cargar_numeros(c, RV, frozenset({5, 9, 18, 23, 31, 42}))
        cargar_premios(
            c,
            PE,
            {"GANADORA": {"ganadores": 4, "importe_individual": "250000"}},
            aciertos_categoria_ganadora=6,
        )
        contenido = _texto(client, "/resultados/1/")
        assert "Conjunto de números del Premio Extra" in contenido
        assert "13 números distintos" in contenido
        assert "$ 250.000,00" in contenido

    def test_ac_1_14_la_segunda_sin_cargar(self, client):
        c = self._concurso()
        cargar_numeros(c, PS, frozenset({2, 9, 16, 25, 34, 45}))
        cargar_numeros(c, RV, frozenset({5, 9, 18, 23, 31, 42}))
        cargar_premios(
            c,
            PE,
            {"GANADORA": {"ganadores": 4, "importe_individual": "250000"}},
            aciertos_categoria_ganadora=6,
        )
        contenido = _texto(client, "/resultados/1/")
        seccion = contenido[contenido.index('id="modalidad-premio-extra"') :]
        assert "Resultado pendiente" in seccion
        assert "Conjunto de números del Premio Extra" not in seccion
        assert "$ 250.000,00" in seccion

    def test_ac_1_14_revancha_en_borrador(self, client):
        c = self._concurso()
        cargar_numeros(c, PS, frozenset({2, 9, 16, 25, 34, 45}))
        cargar_numeros(c, LS, frozenset({2, 11, 16, 23, 35, 42}))
        cargar_numeros(c, RV, frozenset({5, 9, 18, 23, 31, 42}), estado="BORRADOR")
        contenido = _texto(client, "/resultados/1/")
        seccion = contenido[contenido.index('id="modalidad-premio-extra"') :]
        assert "Pendiente de validación" in seccion
        assert "números distintos" not in seccion

    def test_ac_1_15_fuente(self, client):
        c = crear_concurso(1, date(2025, 3, 2), modalidades=[PS])
        cargar_numeros(
            c,
            PS,
            frozenset({1, 2, 3, 4, 5, 6}),
            fuente=("Extracto oficial N.º 3215", date(2025, 3, 3)),
        )
        contenido = _texto(client, "/resultados/1/")
        assert "Extracto oficial N.º 3215" in contenido
        assert "03/03/2025" in contenido
