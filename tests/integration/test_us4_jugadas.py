"""US4 — Registrar y gestionar mis jugadas (AC-4.1 a AC-4.17; AC-3.9)."""

import re
from datetime import date
from decimal import Decimal

import pytest

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import Modalidad
from jugadas.models import Jugada
from tests.fabricas import cargar_numeros, crear_concurso
from tests.paginas import sin_variables

pytestmark = pytest.mark.django_db

PS, LS, RV, SS, PE = (
    Modalidad.PRIMER_SORTEO,
    Modalidad.LA_SEGUNDA,
    Modalidad.REVANCHA,
    Modalidad.SIEMPRE_SALE,
    Modalidad.PREMIO_EXTRA,
)
SEIS = ["03", "08", "14", "21", "32", "40"]
FIJA = MENSAJES["jugada.fija"]
NO_EXISTE = "La jugada no existe o no está disponible"
DUPLICADA = MENSAJES["jugada.duplicada"]


def _datos(concurso="9001", numeros=SEIS, costo="1500,50", **extra):
    return {"concurso": concurso, "numeros": list(numeros), "costo": costo, **extra}


def _registrar(cliente, **kwargs):
    return cliente.post("/mis-jugadas/nueva/", _datos(**kwargs), follow=True)


def _jugada(usuario, concurso, numeros=(3, 8, 14, 21, 32, 40), costo="100"):
    j = Jugada(usuario=usuario, concurso=concurso, costo=Decimal(costo))
    j.asignar_numeros(numeros)
    j.save()
    return j


@pytest.fixture
def concurso(db):
    return crear_concurso(9001, date(2025, 3, 2))


class TestRegistro:
    def test_ac_4_1_registrada(self, cliente_a, concurso, usuario_a):
        r = _registrar(cliente_a)
        contenido = r.content.decode()
        assert "Jugada registrada" in contenido
        for texto in (
            "N.º 9001",  # [003] HU-09: columna "Sorteo" de la tabla
            "02/03/2025",
            "$ 1.500,50",
            "Revancha",
            "Siempre Sale",
            "Premio Extra",
            ">03<",
            ">08<",
        ):
            assert texto in contenido
        jugada = Jugada.objects.get()
        assert jugada.usuario == usuario_a
        assert jugada.costo == Decimal("1500.50")
        assert jugada.numeros == frozenset({3, 8, 14, 21, 32, 40})

    def test_ac_4_2_faltan(self, cliente_a, concurso):
        r = _registrar(cliente_a, numeros=SEIS[:4])
        assert mensaje("jugada.faltan", n=2) in r.content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_3_sobran(self, cliente_a, concurso):
        r = _registrar(cliente_a, numeros=[*SEIS, "45"])
        assert "La jugada admite exactamente seis números" in r.content.decode()
        assert not Jugada.objects.exists()

    @pytest.mark.parametrize("valor", ["46", "abc"])
    def test_ac_4_4_fuera_de_rango(self, cliente_a, concurso, valor):
        r = _registrar(cliente_a, numeros=SEIS[:5], numero_escrito=valor)
        assert MENSAJES["jugada.fuera_de_rango"] in r.content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_5_repetido(self, cliente_a, concurso):
        r = _registrar(cliente_a, numeros=["07", "08", "14", "21", "32"], numero_escrito="7")
        assert mensaje("jugada.repetido", nn="07") in r.content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_6_sin_concurso(self, cliente_a, concurso):
        r = _registrar(cliente_a, concurso="")
        assert MENSAJES["jugada.elegi_concurso"] in r.content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_6_muestra_modalidades_sin_elegirlas(self, cliente_a, concurso):
        contenido = cliente_a.get("/mis-jugadas/nueva/?concurso=9001").content.decode()
        assert "Participará en" in contenido
        assert "Tradicional – Primer Sorteo" in contenido
        assert 'name="modalidad' not in contenido


class TestConcursoDeLaJugada:
    def test_ac_4_7_inexistente(self, cliente_a, concurso):
        r = cliente_a.get("/mis-jugadas/nueva/?concurso=1234")
        assert MENSAJES["jugada.concurso_no_disponible"] in r.content.decode()
        r = _registrar(cliente_a, concurso="1234")
        assert MENSAJES["jugada.concurso_no_disponible"] in r.content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_8_cerrado(self, cliente_a, concurso):
        cargar_numeros(concurso, SS, frozenset({1, 2, 3, 4, 5, 6}))
        texto = MENSAJES["jugada.concurso_cerrado"]
        assert texto in cliente_a.get("/mis-jugadas/nueva/?concurso=9001").content.decode()
        assert texto in _registrar(cliente_a).content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_8_pasado_con_borradores_acepta(self, cliente_a):
        c = crear_concurso(9001, date(2024, 12, 1))
        cargar_numeros(c, PS, frozenset({1, 2, 3, 4, 5, 6}), estado="BORRADOR")
        r = _registrar(cliente_a)
        assert "Jugada registrada" in r.content.decode()

    def test_ac_4_9_resultado_pendiente(self, cliente_a, concurso):
        r = _registrar(cliente_a)
        assert "Resultado pendiente" in r.content.decode()


class TestEdicionYEliminacion:
    def test_ac_4_10_editar(self, cliente_a, concurso, usuario_a):
        j = _jugada(usuario_a, concurso)
        r = cliente_a.post(
            f"/mis-jugadas/{j.id}/editar/",
            _datos(numeros=["01", "02", "03", "04", "05", "06"], costo="200"),
            follow=True,
        )
        contenido = r.content.decode()
        assert "Jugada actualizada" in contenido
        j.refresh_from_db()
        assert j.numeros == frozenset({1, 2, 3, 4, 5, 6})
        assert j.costo == Decimal("200")
        assert ">01<" in contenido

    def test_ac_4_11_eliminar(self, cliente_a, concurso, usuario_a):
        j = _jugada(usuario_a, concurso)
        r = cliente_a.get(f"/mis-jugadas/{j.id}/eliminar/")
        assert MENSAJES["jugada.confirmar_eliminacion"] in r.content.decode()
        assert Jugada.objects.exists()
        r = cliente_a.post(f"/mis-jugadas/{j.id}/eliminar/", follow=True)
        assert "Jugada eliminada" in r.content.decode()
        assert not Jugada.objects.exists()

    def test_ac_4_17_fija(self, cliente_a, concurso, usuario_a):
        j = _jugada(usuario_a, concurso)
        cargar_numeros(concurso, PS, frozenset({1, 2, 3, 4, 5, 6}))
        contenido = cliente_a.get(f"/mis-jugadas/{j.id}/").content.decode()
        assert FIJA in contenido
        assert f"/mis-jugadas/{j.id}/editar/" not in contenido
        assert f"/mis-jugadas/{j.id}/eliminar/" not in contenido
        for metodo, ruta, datos in [
            ("get", "editar", None),
            ("post", "editar", _datos(numeros=["01", "02", "03", "04", "05", "06"])),
            ("get", "eliminar", None),
            ("post", "eliminar", {}),
        ]:
            r = getattr(cliente_a, metodo)(f"/mis-jugadas/{j.id}/{ruta}/", datos, follow=True)
            assert FIJA in r.content.decode()
        j.refresh_from_db()
        assert j.numeros == frozenset({3, 8, 14, 21, 32, 40})


class TestAislamiento:
    @pytest.mark.parametrize(
        ("metodo", "sufijo"),
        [
            ("get", ""),
            ("get", "editar/"),
            ("post", "editar/"),
            ("get", "eliminar/"),
            ("post", "eliminar/"),
        ],
    )
    def test_ac_4_12_ajena_e_inexistente(self, cliente_a, usuario_b, concurso, metodo, sufijo):
        ajena = _jugada(usuario_b, concurso, costo="777")
        respuestas = []
        for id_ in (ajena.id, 999999):
            r = getattr(cliente_a, metodo)(
                f"/mis-jugadas/{id_}/{sufijo}",
                _datos(numeros=["01", "02", "03", "04", "05", "06"]) if metodo == "post" else None,
            )
            assert r.status_code == 404
            contenido = r.content.decode()
            assert NO_EXISTE in contenido
            assert "777" not in contenido
            respuestas.append(sin_variables(contenido.split("<main", 1)[1]))
        assert respuestas[0] == respuestas[1]
        ajena.refresh_from_db()
        assert ajena.numeros == frozenset({3, 8, 14, 21, 32, 40})


class TestHistorial:
    def test_ac_4_13_vacio(self, cliente_a):
        contenido = cliente_a.get("/mis-jugadas/").content.decode()
        assert MENSAJES["vacio.jugadas.titulo"] in contenido
        assert 'href="/mis-jugadas/nueva/"' in contenido

    def test_ac_4_14_duplicado(self, cliente_a, concurso):
        _registrar(cliente_a)
        r = _registrar(cliente_a, numeros=["01", "02", "03", "04", "05", "06"])
        assert DUPLICADA not in r.content.decode()
        assert Jugada.objects.count() == 2
        r = _registrar(cliente_a, numeros=list(reversed(SEIS)))
        contenido = r.content.decode()
        assert DUPLICADA in contenido
        assert "Guardar igual" in contenido and "Cancelar" in contenido
        assert Jugada.objects.count() == 2
        _registrar(cliente_a, confirmar_duplicado="1")
        assert Jugada.objects.count() == 3

    def test_ac_4_14_duplicado_al_editar(self, cliente_a, concurso, usuario_a):
        _jugada(usuario_a, concurso)
        otra = _jugada(usuario_a, concurso, numeros=(1, 2, 3, 4, 5, 6))
        r = cliente_a.post(f"/mis-jugadas/{otra.id}/editar/", _datos())
        assert DUPLICADA in r.content.decode()
        otra.refresh_from_db()
        assert otra.numeros == frozenset({1, 2, 3, 4, 5, 6})
        cliente_a.post(f"/mis-jugadas/{otra.id}/editar/", _datos(confirmar_duplicado="1"))
        otra.refresh_from_db()
        assert otra.numeros == frozenset({3, 8, 14, 21, 32, 40})

    def test_ac_4_15_orden(self, cliente_a, usuario_a):
        viejo = crear_concurso(1, date(2025, 1, 1))
        nuevo = crear_concurso(2, date(2025, 2, 1))
        j_viejo = _jugada(usuario_a, viejo)
        j_nuevo = _jugada(usuario_a, nuevo)
        contenido = cliente_a.get("/mis-jugadas/").content.decode()
        # [003] HU-09: una fila por jugada (id="jugada-<pk>"), de la más reciente a la más antigua.
        assert contenido.index(f'id="jugada-{j_nuevo.pk}"') < contenido.index(
            f'id="jugada-{j_viejo.pk}"'
        )


class TestCosto:
    def test_ac_4_16_vacio(self, cliente_a, concurso):
        r = _registrar(cliente_a, costo="")
        assert MENSAJES["jugada.costo_vacio"] in r.content.decode()
        assert not Jugada.objects.exists()

    @pytest.mark.parametrize("costo", ["-1", "abc", "10,505"])
    def test_ac_4_16_invalido(self, cliente_a, concurso, costo):
        r = _registrar(cliente_a, costo=costo)
        assert MENSAJES["jugada.costo_invalido"] in r.content.decode()
        assert not Jugada.objects.exists()


class TestRegistrarDesdeElConcurso:
    def test_ac_3_9_boton(self, client, concurso):
        contenido = client.get("/resultados/9001/").content.decode()
        assert 'href="/mis-jugadas/nueva/?concurso=9001"' in contenido
        assert "Registrar una jugada" in contenido
        r = client.get("/mis-jugadas/nueva/?concurso=9001")
        assert r["Location"] == "/ingresar/?next=/mis-jugadas/nueva/%3Fconcurso%3D9001"

    def test_ac_3_9_sin_boton_si_cerrado(self, client, concurso):
        cargar_numeros(concurso, PS, frozenset({1, 2, 3, 4, 5, 6}))
        assert "Registrar una jugada" not in client.get("/resultados/9001/").content.decode()

    def test_ac_3_9_preselecciona(self, cliente_a, concurso):
        crear_concurso(9002, date(2025, 3, 5))
        contenido = cliente_a.get("/mis-jugadas/nueva/?concurso=9001").content.decode()
        assert re.search(r'<option value="9001"[^>]*selected', contenido)
        assert not re.search(r'<option value="9002"[^>]*selected', contenido)
