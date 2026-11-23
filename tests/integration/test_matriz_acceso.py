"""SC-004: matriz de acceso (visitante, usuaria A, usuario B, administrador) sobre las rutas de
nivel Sesión, Propietario y Admin de contracts/rutas.md, en GET y POST."""

from datetime import date
from decimal import Decimal

import pytest
from django.test import Client

from dominio.mensajes import MENSAJES
from dominio.tipos import Modalidad
from jugadas.models import Jugada
from resultados.models import Concurso, ModalidadConcurso, RegistroCambio, VersionNumeros
from tests.fabricas import cargar_numeros, crear_concurso, crear_usuario
from tests.paginas import es_ingreso_con_pendiente, es_reanudable, sin_variables

pytestmark = pytest.mark.django_db

SIN_PERMISO = MENSAJES["admin.sin_permiso"]
NO_EXISTE = "La jugada no existe o no está disponible"
A = "/administracion/concursos"

RUTAS_SESION = [
    ("GET", "/mis-jugadas/"),
    ("GET", "/mis-jugadas/nueva/"),
    ("POST", "/mis-jugadas/nueva/"),
    ("POST", "/salir/"),
]
RUTAS_PROPIETARIO = [
    ("GET", ""),
    ("GET", "editar/"),
    ("POST", "editar/"),
    ("GET", "eliminar/"),
    ("POST", "eliminar/"),
]
RUTAS_ADMIN = [
    ("GET", f"{A}/"),
    ("GET", f"{A}/nuevo/"),
    ("POST", f"{A}/nuevo/"),
    ("GET", f"{A}/1/"),
    ("GET", f"{A}/1/modificar/"),
    ("POST", f"{A}/1/modificar/"),
    ("GET", f"{A}/1/historial/"),
    ("GET", f"{A}/1/primer-sorteo/numeros/"),
    ("POST", f"{A}/1/primer-sorteo/numeros/"),
    ("GET", f"{A}/1/primer-sorteo/premios/"),
    ("POST", f"{A}/1/primer-sorteo/premios/"),
    *[
        ("POST", f"{A}/1/la-segunda/numeros/{accion}/")
        for accion in ("observar", "resolver", "revision", "quitar-revision", "corregir")
    ],
    ("GET", f"{A}/1/la-segunda/numeros/publicar/"),
    ("POST", f"{A}/1/la-segunda/numeros/publicar/"),
]
DATOS = {
    "numero": "2",
    "fecha_sorteo": "02/03/2025",
    "modalidades": ["PRIMER_SORTEO"],
    "n1": "01",
    "n2": "02",
    "n3": "03",
    "n4": "04",
    "n5": "05",
    "n6": "06",
    "fuente_descripcion": "x",
    "fuente_fecha_consulta": "03/03/2025",
    "motivo": "x",
    "cotejo": "on",
    "concurso": "1",
    "numeros": ["01", "02", "03", "04", "05", "06"],
    "costo": "10",
    "PRIMER_ganadores": "9",
}


@pytest.fixture
def escenario(db):
    ana = crear_usuario("ana@prueba.local")
    beto = crear_usuario("beto@prueba.local")
    admin = crear_usuario("admin@prueba.local", admin=True)
    concurso = crear_concurso(1, date(2025, 3, 2))
    cargar_numeros(
        concurso, Modalidad.LA_SEGUNDA, frozenset({7, 8, 9, 10, 11, 12}), estado="BORRADOR"
    )
    jugada = Jugada(usuario=ana, concurso=concurso, costo=Decimal("4242.42"))
    jugada.asignar_numeros({3, 8, 14, 21, 32, 40})
    jugada.save()
    clientes = {"visitante": Client()}
    for nombre, usuario in (("ana", ana), ("beto", beto), ("admin", admin)):
        clientes[nombre] = Client()
        clientes[nombre].force_login(usuario)
    return clientes, jugada


def _foto():
    return (
        Concurso.objects.count(),
        list(VersionNumeros.objects.values_list("id", "estado", "n1", "n6")),
        list(ModalidadConcurso.objects.values_list("id", "numeros_en_revision")),
        RegistroCambio.objects.count(),
        list(Jugada.objects.values_list("id", "n1", "n6", "costo")),
    )


def _sin_sesion(r, metodo, ruta):
    """Visitante: redirección al ingreso o, en un POST a un formulario reanudable, "Ingresar" con
    lo escrito firmado ([003] FR-032, R-12). En ningún caso cambia algún dato."""
    if metodo == "POST" and es_reanudable(ruta):
        assert es_ingreso_con_pendiente(r)
    else:
        assert r.status_code == 302 and r["Location"] == f"/ingresar/?next={ruta}"


def _pedir(cliente, metodo, ruta):
    if metodo == "GET":
        return cliente.get(ruta)
    return cliente.post(ruta, DATOS)


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_SESION)
def test_sesion_visitante(escenario, metodo, ruta):
    clientes, _ = escenario
    antes = _foto()
    r = _pedir(clientes["visitante"], metodo, ruta)
    _sin_sesion(r, metodo, ruta)
    assert _foto() == antes


@pytest.mark.parametrize("rol", ["visitante", "beto", "admin"])
@pytest.mark.parametrize(("metodo", "sufijo"), RUTAS_PROPIETARIO)
def test_propietario(escenario, rol, metodo, sufijo):
    clientes, jugada = escenario
    ruta = f"/mis-jugadas/{jugada.id}/{sufijo}"
    antes = _foto()
    r = _pedir(clientes[rol], metodo, ruta)
    if rol == "visitante":
        _sin_sesion(r, metodo, ruta)
    else:
        assert r.status_code == 404
        contenido = r.content.decode()
        assert NO_EXISTE in contenido
        assert "4.242,42" not in contenido and ">40<" not in contenido
        inexistente = _pedir(clientes[rol], metodo, f"/mis-jugadas/999999/{sufijo}")
        assert inexistente.status_code == 404
        assert sin_variables(contenido.split("<main", 1)[1]) == sin_variables(
            inexistente.content.decode().split("<main", 1)[1]
        )
    assert _foto() == antes


def test_propietaria_accede(escenario):
    clientes, jugada = escenario
    for sufijo in ("", "editar/", "eliminar/"):
        assert clientes["ana"].get(f"/mis-jugadas/{jugada.id}/{sufijo}").status_code == 200


@pytest.mark.parametrize("rol", ["visitante", "ana", "beto"])
@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_ADMIN)
def test_admin(escenario, rol, metodo, ruta):
    clientes, _ = escenario
    antes = _foto()
    r = _pedir(clientes[rol], metodo, ruta)
    if rol == "visitante":
        _sin_sesion(r, metodo, ruta)
    else:
        assert r.status_code == 403
        contenido = r.content.decode()
        assert SIN_PERMISO in contenido
        assert ">07<" not in contenido
    assert _foto() == antes


@pytest.mark.parametrize(("metodo", "ruta"), [r for r in RUTAS_ADMIN if r[0] == "GET"])
def test_admin_accede(escenario, metodo, ruta):
    clientes, _ = escenario
    r = clientes["admin"].get(ruta, follow=True)
    assert r.status_code == 200
