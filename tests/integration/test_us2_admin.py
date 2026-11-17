"""US2 — Incorporar, validar y publicar resultados (AC-2.1 a AC-2.14) por las rutas."""

from datetime import date

import pytest

from dominio.tipos import EstadoBloque, Modalidad
from resultados import consultas
from resultados.models import (
    Accion,
    Concurso,
    EstadoVersion,
    ModalidadConcurso,
    RegistroCambio,
    VersionNumeros,
    VersionPremios,
)
from tests.fabricas import cargar_numeros, crear_concurso

pytestmark = pytest.mark.django_db

BASE = "/administracion/concursos"
SIN_PERMISO = "No tenés permisos para acceder a esta sección"
FECHA = date(2025, 3, 2)


def _numeros(
    valores=("03", "08", "14", "21", "32", "40"),
    fuente="Extracto oficial N.º 3215",
    fecha="03/03/2025",
):
    datos = {f"n{i}": v for i, v in enumerate(valores, start=1)}
    datos.update({"fuente_descripcion": fuente, "fuente_fecha_consulta": fecha})
    return datos


def _vista(numero):
    return consultas.vista_publica_concurso(consultas.cargar_concurso(numero))


def _mc(numero, modalidad):
    return ModalidadConcurso.objects.get(concurso__numero=numero, modalidad=modalidad.value)


class TestConcursos:
    def test_ac_2_1_crear(self, cliente_admin):
        r = cliente_admin.post(
            f"{BASE}/nuevo/",
            {
                "numero": "3215",
                "fecha_sorteo": "02/03/2025",
                "modalidades": [
                    "PRIMER_SORTEO",
                    "LA_SEGUNDA",
                    "REVANCHA",
                    "SIEMPRE_SALE",
                    "PREMIO_EXTRA",
                ],
            },
        )
        assert r.status_code == 302
        assert r["Location"] == f"{BASE}/3215/"
        c = Concurso.objects.get(numero=3215)
        assert c.fecha_sorteo == FECHA
        assert c.modalidades.count() == 5
        publico = cliente_admin.get("/resultados/").content.decode()
        assert "Resultados pendientes" in publico

    def test_ac_2_1_p06_premio_extra(self, cliente_admin):
        r = cliente_admin.post(
            f"{BASE}/nuevo/",
            {
                "numero": "1",
                "fecha_sorteo": "02/03/2025",
                "modalidades": ["PRIMER_SORTEO", "PREMIO_EXTRA"],
            },
        )
        assert "Premio Extra requiere Primer Sorteo, La Segunda y Revancha" in r.content.decode()
        assert not Concurso.objects.exists()

    def test_ac_2_2_duplicado(self, cliente_admin):
        crear_concurso(3215, FECHA)
        r = cliente_admin.post(
            f"{BASE}/nuevo/",
            {
                "numero": "3215",
                "fecha_sorteo": "02/03/2025",
                "modalidades": ["PRIMER_SORTEO"],
            },
        )
        contenido = r.content.decode()
        assert "El concurso N.º 3215 ya existe" in contenido
        assert f'href="{BASE}/3215/"' in contenido
        assert Concurso.objects.count() == 1

    def test_ac_2_14_modificar(self, cliente_admin):
        crear_concurso(1, FECHA, modalidades=[Modalidad.PRIMER_SORTEO])
        r = cliente_admin.post(
            f"{BASE}/1/modificar/",
            {
                "fecha_sorteo": "05/03/2025",
                "modalidades": ["PRIMER_SORTEO", "LA_SEGUNDA"],
            },
        )
        assert r.status_code == 302
        c = Concurso.objects.get(numero=1)
        assert c.fecha_sorteo == date(2025, 3, 5)
        assert c.modalidades.count() == 2
        assert RegistroCambio.objects.filter(accion=Accion.MODIFICAR_CONCURSO).exists()

    def test_listado_y_panel(self, cliente_admin):
        c = crear_concurso(1, FECHA)
        cargar_numeros(c, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
        r = cliente_admin.get(f"{BASE}/")
        assert r.status_code == 200 and "Publicado" in r.content.decode()
        r = cliente_admin.get(f"{BASE}/1/")
        contenido = r.content.decode()
        assert "Sin cargar" in contenido and "Publicado" in contenido
        assert "02/03/2025" in contenido


class TestNumeros:
    def test_ac_2_3_numeros_invalidos(self, cliente_admin):
        crear_concurso(1, FECHA)
        r = cliente_admin.post(
            f"{BASE}/1/primer-sorteo/numeros/", _numeros(("03", "03", "14", "21", "32", "40"))
        )
        assert "El 03 está repetido en la extracción" in r.content.decode()
        r = cliente_admin.post(
            f"{BASE}/1/primer-sorteo/numeros/", _numeros(("03", "08", "14", "21", "32", "46"))
        )
        assert "Ingresá números entre 00 y 45" in r.content.decode()
        assert not VersionNumeros.objects.exists()

    def test_ac_2_4_borrador_no_publico(self, cliente_admin):
        crear_concurso(1, FECHA)
        r = cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/", _numeros())
        assert r.status_code == 302
        vista = _vista(1).modalidad(Modalidad.PRIMER_SORTEO)
        assert vista.estado_numeros == EstadoBloque.BORRADOR
        assert vista.numeros is None
        publico = cliente_admin.get("/resultados/1/").content.decode()
        assert "Pendiente de validación" in publico

    def test_ac_2_10_borrador_sin_fuente(self, cliente_admin):
        crear_concurso(1, FECHA)
        r = cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/", _numeros(fuente="", fecha=""))
        assert r.status_code == 302
        assert VersionNumeros.objects.get().estado == EstadoVersion.BORRADOR

    def test_ac_2_5_publicar_sin_fuente_informa(self, cliente_admin):
        crear_concurso(1, FECHA)
        cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/", _numeros(fuente="", fecha=""))
        url = f"{BASE}/1/primer-sorteo/numeros/publicar/"
        assert (
            "Falta registrar la descripción de la fuente" in cliente_admin.get(url).content.decode()
        )
        r = cliente_admin.post(url, {"cotejo": "on"})
        assert "Falta registrar la descripción de la fuente" in r.content.decode()
        assert VersionNumeros.objects.get().estado == EstadoVersion.BORRADOR

    def test_ac_2_6_y_2_7_publicar(self, cliente_admin):
        crear_concurso(1, FECHA)
        cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/", _numeros())
        r = cliente_admin.get(f"{BASE}/1/primer-sorteo/numeros/publicar/")
        assert "Confirmo que cotejé esta información con la fuente oficial" in r.content.decode()
        r = cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/publicar/", {"cotejo": "on"})
        assert r.status_code == 302
        vista = _vista(1)
        assert vista.modalidad(Modalidad.PRIMER_SORTEO).numeros == [3, 8, 14, 21, 32, 40]
        assert vista.modalidad(Modalidad.LA_SEGUNDA).estado_numeros == EstadoBloque.SIN_CARGAR
        assert RegistroCambio.objects.filter(accion=Accion.PUBLICAR).count() == 1
        publico = cliente_admin.get("/resultados/1/").content.decode()
        assert "Resultado pendiente" in publico and "Incompleto" in publico

    def test_ac_2_8_observado_bloquea(self, cliente_admin):
        crear_concurso(1, FECHA)
        cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/", _numeros())
        r = cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/observar/", {"motivo": ""})
        assert VersionNumeros.objects.get().estado == EstadoVersion.BORRADOR
        cliente_admin.post(
            f"{BASE}/1/primer-sorteo/numeros/observar/",
            {"motivo": "El 40 no coincide con el extracto"},
        )
        assert VersionNumeros.objects.get().estado == EstadoVersion.OBSERVADO
        r = cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/publicar/", {"cotejo": "on"})
        assert VersionNumeros.objects.get().estado == EstadoVersion.OBSERVADO
        assert "Observad" in r.content.decode()
        cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/resolver/")
        assert VersionNumeros.objects.get().estado == EstadoVersion.BORRADOR

    def test_ac_2_9_advertencia_numeros_iguales(self, cliente_admin):
        crear_concurso(1, FECHA)
        cliente_admin.post(f"{BASE}/1/primer-sorteo/numeros/", _numeros())
        cliente_admin.post(f"{BASE}/1/la-segunda/numeros/", _numeros())
        url = f"{BASE}/1/la-segunda/numeros/publicar/"
        r = cliente_admin.get(url)
        assert "Los seis números son iguales a los de Tradicional – Primer Sorteo" in (
            r.content.decode()
        )
        cliente_admin.post(url, {"cotejo": "on"})
        assert consultas.estado_bloque(_mc(1, Modalidad.LA_SEGUNDA), "numeros") == (
            EstadoBloque.BORRADOR
        )
        cliente_admin.post(url, {"cotejo": "on", "confirmar_advertencias": "on"})
        assert consultas.estado_bloque(_mc(1, Modalidad.LA_SEGUNDA), "numeros") == (
            EstadoBloque.PUBLICADO
        )

    def test_premio_extra_numeros_404(self, cliente_admin):
        crear_concurso(1, FECHA)
        assert cliente_admin.get(f"{BASE}/1/premio-extra/numeros/").status_code == 404
        assert cliente_admin.post(f"{BASE}/1/premio-extra/numeros/publicar/").status_code == 404


class TestPremios:
    def test_ac_2_13_categorias_fijas_y_no_disponible(self, cliente_admin):
        crear_concurso(1, FECHA)
        r = cliente_admin.get(f"{BASE}/1/primer-sorteo/premios/")
        contenido = r.content.decode()
        for nombre in ("Primer Premio", "Segundo Premio", "Tercer Premio"):
            assert nombre in contenido
        assert "no disponible" in contenido
        r = cliente_admin.post(
            f"{BASE}/1/primer-sorteo/premios/",
            {
                "PRIMER_ganadores": "0",
                "PRIMER_pozo_vacante_acumulado": "1.000.000,00",
                "SEGUNDO_ganadores": "3",
                "SEGUNDO_importe_individual": "1.500,50",
                "fuente_descripcion": "Extracto",
                "fuente_fecha_consulta": "03/03/2025",
            },
        )
        assert r.status_code == 302
        version = VersionPremios.objects.get()
        assert version.categorias.count() == 3
        assert version.categorias.get(categoria="TERCER").ganadores is None

    def test_ac_2_13_siempre_sale_y_premio_extra(self, cliente_admin):
        crear_concurso(1, FECHA)
        r = cliente_admin.get(f"{BASE}/1/siempre-sale/premios/")
        assert "aciertos de la categoría ganadora" in r.content.decode()
        cliente_admin.post(
            f"{BASE}/1/siempre-sale/premios/",
            {
                "aciertos_categoria_ganadora": "5",
                "GANADORA_ganadores": "2",
            },
        )
        assert VersionPremios.objects.get().aciertos_categoria_ganadora == 5
        r = cliente_admin.get(f"{BASE}/1/premio-extra/premios/")
        assert "Sin ganadores" in r.content.decode()
        cliente_admin.post(
            f"{BASE}/1/premio-extra/premios/",
            {
                "aciertos_categoria_ganadora": "SIN",
            },
        )
        pe = VersionPremios.objects.get(modalidad_concurso__modalidad="PREMIO_EXTRA")
        assert pe.sin_ganadores is True and pe.aciertos_categoria_ganadora is None

    def test_importe_invalido(self, cliente_admin):
        crear_concurso(1, FECHA)
        r = cliente_admin.post(f"{BASE}/1/revancha/premios/", {"UNICO_importe_individual": "-5"})
        assert "El importe no puede ser negativo" in r.content.decode()
        assert not VersionPremios.objects.exists()


class TestPermisos:
    RUTAS_GET = [
        "",
        "nuevo/",
        "1/",
        "1/modificar/",
        "1/primer-sorteo/numeros/",
        "1/primer-sorteo/premios/",
        "1/primer-sorteo/numeros/publicar/",
    ]
    RUTAS_POST = [
        "nuevo/",
        "1/modificar/",
        "1/primer-sorteo/numeros/",
        "1/primer-sorteo/premios/",
        "1/primer-sorteo/numeros/observar/",
        "1/primer-sorteo/numeros/resolver/",
        "1/primer-sorteo/numeros/publicar/",
    ]

    @pytest.mark.parametrize("ruta", RUTAS_GET)
    def test_ac_2_11_get_sin_permiso(self, cliente_a, ruta):
        crear_concurso(1, FECHA)
        r = cliente_a.get(f"{BASE}/{ruta}")
        assert r.status_code == 403
        assert SIN_PERMISO in r.content.decode()

    @pytest.mark.parametrize("ruta", RUTAS_POST)
    def test_ac_2_11_post_sin_permiso(self, cliente_a, ruta):
        c = crear_concurso(1, FECHA)
        cargar_numeros(c, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}), estado="BORRADOR")
        datos = {
            **_numeros(),
            "numero": "2",
            "fecha_sorteo": "02/03/2025",
            "modalidades": ["PRIMER_SORTEO"],
            "motivo": "x",
            "cotejo": "on",
        }
        r = cliente_a.post(f"{BASE}/{ruta}", datos)
        assert r.status_code == 403
        assert SIN_PERMISO in r.content.decode()
        assert Concurso.objects.count() == 1
        assert VersionNumeros.objects.get().estado == EstadoVersion.BORRADOR
        assert VersionNumeros.objects.get().numeros == frozenset({1, 2, 3, 4, 5, 6})
        assert not RegistroCambio.objects.exists()

    @pytest.mark.parametrize("ruta", ["", "nuevo/", "1/primer-sorteo/numeros/"])
    def test_ac_2_12_visitante(self, client, ruta):
        crear_concurso(1, FECHA)
        r = client.get(f"{BASE}/{ruta}")
        assert r.status_code == 302
        assert r["Location"] == f"/ingresar/?next={BASE}/{ruta}"
