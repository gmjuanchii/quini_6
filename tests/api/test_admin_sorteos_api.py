"""[003] T206: administración de sorteos en la API v1 (contracts/api.md § "Administración de
sorteos").

Los casos de tests/integration/test_us2_admin.py y test_us7_correccion.py por la API: mismos
resultados y mensajes (NFR-009), solo administración, CSRF e idempotencia al crear.
"""

import json
import uuid
from datetime import date

import pytest
from django.test import Client

from dominio.mensajes import MENSAJES, mensaje
from dominio.tipos import EstadoBloque, Modalidad
from resultados import consultas
from resultados.models import Concurso, ModalidadConcurso, VersionPremios
from tests.api.conftest import token_csrf
from tests.fabricas import cargar_numeros, crear_concurso, crear_usuario

pytestmark = pytest.mark.django_db

API = "/api/v1/admin/sorteos/"
FECHA = date(2025, 3, 2)


@pytest.fixture
def admin(db):
    cliente = Client(enforce_csrf_checks=True)
    cliente.force_login(crear_usuario("admin@sorteos.local", admin=True))
    return cliente


def _enviar(cliente, metodo, ruta, campos=None, clave=None, csrf=True):
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)} if csrf else {}
    if clave:
        extra["HTTP_IDEMPOTENCY_KEY"] = clave
    cuerpo = json.dumps({"campos": campos or {}})
    return cliente.generic(metodo, ruta, data=cuerpo, content_type="application/json", **extra)


def _numeros(valores=("03", "08", "14", "21", "32", "40"), fuente="Extracto oficial N.º 3215"):
    campos = {f"n{i}": v for i, v in enumerate(valores, start=1)}
    campos.update({"fuente_descripcion": fuente, "fuente_fecha_consulta": "03/03/2025"})
    return campos


def _mc(numero, modalidad):
    return ModalidadConcurso.objects.get(concurso__numero=numero, modalidad=modalidad.value)


def test_crear_201_aviso_e_idempotencia(admin):
    clave = str(uuid.uuid4())
    campos = {
        "numero": "3215",
        "fecha_sorteo": "02/03/2025",
        "modalidades": ["PRIMER_SORTEO", "REVANCHA"],
    }
    respuesta = _enviar(admin, "POST", API, campos, clave)
    assert respuesta.status_code == 201
    panel = respuesta.json()
    assert panel["numero"] == 3215 and panel["fecha"] == "2025-03-02"
    assert [f["modalidad"]["slug"] for f in panel["filas"]] == ["primer-sorteo", "revancha"]
    assert panel["filas"][0]["bloques"][0]["acciones"] == ["cargar"]
    assert _enviar(admin, "POST", API, campos, clave).status_code == 201
    assert Concurso.objects.count() == 1
    assert admin.get("/api/v1/avisos/").json() == [
        {"tipo": "exito", "texto": "Se creó el sorteo N.º 3215."}
    ]


def test_crear_duplicado_y_errores(admin):
    crear_concurso(3215, FECHA)
    duplicado = _enviar(
        admin,
        "POST",
        API,
        {"numero": "3215", "fecha_sorteo": "02/03/2025", "modalidades": ["PRIMER_SORTEO"]},
    )
    assert duplicado.status_code == 422
    assert duplicado.json()["detail"] == mensaje("admin.concurso_duplicado", N=3215)
    assert duplicado.json()["existente"]["url"] == "/administracion/concursos/3215/"
    vacio = _enviar(admin, "POST", API, {})
    textos = {(e["campo"], e["mensaje"]) for e in vacio.json()["errores"]}
    assert ("numero", MENSAJES["admin.falta_numero_sorteo"]) in textos
    assert ("modalidades", MENSAJES["admin.falta_modalidad"]) in textos
    assert vacio.json()["formulario"]["campos"][0]["nombre"] == "numero"


def test_formularios_describen_los_campos_de_django(admin):
    nuevo = admin.get(f"{API}nuevo/").json()["formulario"]["campos"]
    assert [c["nombre"] for c in nuevo] == ["numero", "fecha_sorteo", "modalidades"]
    assert nuevo[2]["tipo"] == "checkbox-multiple" and len(nuevo[2]["opciones"]) == 5
    crear_concurso(1, FECHA)
    premios = admin.get(f"{API}1/primer-sorteo/premios/").json()["formulario"]
    assert [f["nombre"] for f in premios["filas"]] == [
        "Primer Premio",
        "Segundo Premio",
        "Tercer Premio",
    ]
    numeros = admin.get(f"{API}1/primer-sorteo/numeros/").json()["formulario"]
    assert [c["nombre"] for c in numeros["campos"]][:6] == ["n1", "n2", "n3", "n4", "n5", "n6"]


def test_numeros_borrador_publicar_y_bloque_publicado(admin):
    crear_concurso(1, FECHA)
    respuesta = _enviar(admin, "PUT", f"{API}1/primer-sorteo/numeros/", _numeros())
    assert respuesta.status_code == 200
    bloque = respuesta.json()["filas"][0]["bloques"][0]
    assert bloque["estado"]["codigo"] == "BORRADOR"
    assert bloque["trabajo"]["numeros"] == [3, 8, 14, 21, 32, 40]
    assert set(bloque["acciones"]) >= {"editar", "publicar", "observar"}
    revision = admin.get(f"{API}1/primer-sorteo/numeros/publicar/").json()
    assert revision["numeros"] == [3, 8, 14, 21, 32, 40] and revision["bloqueantes"] == []
    publicado = _enviar(admin, "POST", f"{API}1/primer-sorteo/numeros/publicar/", {"cotejo": True})
    assert publicado.status_code == 200
    assert (
        consultas.estado_bloque(_mc(1, Modalidad.PRIMER_SORTEO), "numeros")
        is EstadoBloque.PUBLICADO
    )
    otra = admin.get(f"{API}1/primer-sorteo/numeros/")
    assert otra.status_code == 409 and otra.json()["detail"] == MENSAJES["admin.bloque_publicado"]


def test_numeros_invalidos_422(admin):
    crear_concurso(1, FECHA)
    respuesta = _enviar(
        admin,
        "PUT",
        f"{API}1/primer-sorteo/numeros/",
        _numeros(("01", "01", "02", "03", "04", "46")),
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["errores"]


def test_publicar_sin_cotejo_no_publica(admin):
    crear_concurso(1, FECHA)
    _enviar(admin, "PUT", f"{API}1/primer-sorteo/numeros/", _numeros())
    respuesta = _enviar(admin, "POST", f"{API}1/primer-sorteo/numeros/publicar/", {})
    assert respuesta.status_code == 422
    assert (
        consultas.estado_bloque(_mc(1, Modalidad.PRIMER_SORTEO), "numeros") is EstadoBloque.BORRADOR
    )


def test_observar_resolver(admin):
    crear_concurso(1, FECHA)
    _enviar(admin, "PUT", f"{API}1/primer-sorteo/numeros/", _numeros())
    sin_motivo = _enviar(admin, "POST", f"{API}1/primer-sorteo/numeros/observar/", {"motivo": ""})
    assert sin_motivo.status_code == 422
    observado = _enviar(
        admin, "POST", f"{API}1/primer-sorteo/numeros/observar/", {"motivo": "Revisar"}
    )
    assert observado.json()["filas"][0]["bloques"][0]["acciones"] == ["editar", "resolver"]
    resuelto = _enviar(admin, "POST", f"{API}1/primer-sorteo/numeros/resolver/")
    assert resuelto.json()["filas"][0]["bloques"][0]["estado"]["codigo"] == "BORRADOR"


def test_premios_con_no_disponible(admin):
    crear_concurso(1, FECHA)
    campos = {
        "PRIMER_ganadores": "0",
        "PRIMER_pozo_vacante_acumulado": "1.000.000,00",
        "SEGUNDO_ganadores": "3",
        "SEGUNDO_importe_individual": "1.500,50",
        "fuente_descripcion": "Extracto",
        "fuente_fecha_consulta": "03/03/2025",
    }
    assert _enviar(admin, "PUT", f"{API}1/primer-sorteo/premios/", campos).status_code == 200
    version = VersionPremios.objects.get()
    assert version.categorias.get(categoria="TERCER").ganadores is None


def test_revision_correccion_e_historial(admin):
    concurso = crear_concurso(1, FECHA)
    cargar_numeros(concurso, Modalidad.PRIMER_SORTEO, frozenset({1, 2, 3, 4, 5, 6}))
    revision = _enviar(
        admin, "POST", f"{API}1/primer-sorteo/numeros/revision/", {"motivo": "Dudas"}
    )
    bloque = revision.json()["filas"][0]["bloques"][0]
    assert bloque["en_revision"] is True and "quitar_revision" in bloque["acciones"]
    _enviar(admin, "POST", f"{API}1/primer-sorteo/numeros/quitar-revision/", {"motivo": "Listo"})
    correccion = _enviar(
        admin,
        "POST",
        f"{API}1/primer-sorteo/numeros/corregir/",
        {
            "motivo": "Error",
            "fuente_descripcion": "Extracto",
            "fuente_fecha_consulta": "04/03/2025",
        },
    )
    assert correccion.json()["filas"][0]["bloques"][0]["correccion_en_preparacion"] is True
    historial = admin.get(f"{API}1/historial/").json()
    assert historial and {"momento", "accion", "autor"} <= historial[0].keys()


def test_premio_extra_sin_numeros_404(admin):
    crear_concurso(1, FECHA)
    assert admin.get(f"{API}1/premio-extra/numeros/").status_code == 404
    assert admin.get(f"{API}999/").status_code == 404


def test_solo_administracion_y_csrf(usuario, visitante, admin):
    crear_concurso(1, FECHA)
    assert usuario.get(API).status_code == 403
    assert visitante.get(f"{API}1/").status_code == 401
    assert _enviar(admin, "POST", API, {"numero": "2"}, csrf=False).status_code == 403
