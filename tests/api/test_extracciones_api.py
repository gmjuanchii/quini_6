"""[003] T173: Extracción histórica en la API v1 (contracts/api.md § "Extracción histórica").

Matriz de acceso, CSRF, ``Idempotency-Key``, 409 de RN-03 y de [002] AC-1.11, 422 por campo y
paridad con la vista HTML (mismos datos y mensajes, NFR-009).
"""

import uuid
from datetime import date

import pytest
from django.test import Client

from dominio.extraccion.tipos import Fuente
from dominio.mensajes import mensaje
from extracciones import consultas, servicios
from extracciones.models import Extraccion
from quini6.fechas import hoy_buenos_aires
from quini6.templatetags.formato_ar import fecha_ar, fecha_hora_ar
from tests.api.conftest import token_csrf
from tests.extraccion_estados import crear_extraccion
from tests.extraccion_falsos import cliente_con_sorteos, fichas_de, procesar_pendientes
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

API = "/api/v1/extracciones/"
SORTEOS = {
    3421: date(2026, 10, 28),
    3422: date(2026, 11, 1),
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
}


@pytest.fixture
def admin_api(db):
    cliente = Client(enforce_csrf_checks=True)
    usuario = crear_usuario("admin@extracciones.local", admin=True)
    cliente.force_login(usuario)
    cliente.usuario = usuario
    return cliente


def _post(cliente, datos, clave=None, csrf=True):
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)} if csrf else {}
    if clave:
        extra["HTTP_IDEMPOTENCY_KEY"] = clave
    return cliente.post(API, data=datos, content_type="application/json", **extra)


def _delete(cliente, id_, clave=None, csrf=True):
    extra = {"HTTP_X_CSRFTOKEN": token_csrf(cliente)} if csrf else {}
    if clave:
        extra["HTTP_IDEMPOTENCY_KEY"] = clave
    return cliente.delete(f"{API}{id_}/", **extra)


# -- Matriz de acceso -------------------------------------------------------------------


@pytest.mark.parametrize(
    "ruta",
    [
        API,
        f"{API}1/",
        f"{API}1/avance/",
        f"{API}1/sorteos/3422/",
        "/api/v1/periodos/atajos/?formulario=extraccion",
    ],
)
def test_visitante_401_y_usuario_403(visitante, usuario, ruta):
    assert visitante.get(ruta).status_code == 401
    respuesta = usuario.get(ruta)
    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == mensaje("admin.sin_permiso")


def test_usuario_no_puede_iniciar_ni_eliminar(usuario):
    assert _post(usuario, {"inicio": "2026-11-01", "fin": "2026-11-15"}).status_code == 403
    assert _delete(usuario, 1).status_code == 403
    assert Extraccion.objects.count() == 0


def test_mutaciones_sin_csrf_403(admin_api):
    extraccion = crear_extraccion(admin_api.usuario, "finalizada")
    assert (
        _post(admin_api, {"inicio": "2026-11-01", "fin": "2026-11-15"}, csrf=False).status_code
        == 403
    )
    assert _delete(admin_api, extraccion.pk, csrf=False).status_code == 403
    assert Extraccion.objects.count() == 1


def test_privadas_no_store(admin_api):
    assert admin_api.get(API)["Cache-Control"] == "no-store"


def test_401_de_iniciar_lleva_el_pendiente(visitante):
    """[003] R-12: sin sesión, el 401 lleva lo enviado firmado para reanudarlo tras ingresar."""
    from quini6.formulario_pendiente import ruta_de

    respuesta = _post(visitante, {"inicio": "2026-11-01", "fin": "2026-11-15"})
    assert respuesta.status_code == 401
    assert ruta_de(respuesta.json()["pendiente"]) == "/administracion/extracciones/"


# -- Listado ----------------------------------------------------------------------------


def test_listado_con_etiqueta_filtro_orden_y_paginacion(admin_api):
    admin = admin_api.usuario
    for etiqueta in ("finalizada", "con-error", "con-advertencias", "sin-sorteos"):
        crear_extraccion(admin, etiqueta)
    datos = admin_api.get(API).json()
    assert datos["total"] == 4 and datos["pagina"] == 1 and datos["orden"] == "-fecha"
    assert datos["filtro"] is None and datos["en_curso_propia"] is None
    fila = datos["elementos"][0]
    assert set(fila) >= {"id", "iniciada_en", "desde", "hasta", "creada_por", "etiqueta"}
    assert fila["creada_por"] == "admin@extracciones.local"
    assert fila["iniciada_en"].endswith("-03:00")
    con_error = admin_api.get(API, {"estado": "con-error"}).json()
    assert con_error["filtro"] == "con-error" and con_error["total"] == 1
    etiqueta = con_error["elementos"][0]["etiqueta"]
    assert etiqueta == {
        "valor": "con_error",
        "slug": "con-error",
        "texto": mensaje("etiqueta.con_error"),
        "explicacion": mensaje("etiqueta.con_error.explicacion"),
        "variante": "danger",
        "requiere_revision": True,
    }
    # Inválidos: filtro ignorado, orden por defecto, página fuera de rango → la última.
    invalido = admin_api.get(API, {"estado": "otra", "orden": "x", "pagina": "99"}).json()
    assert invalido["filtro"] is None and invalido["orden"] == "-fecha"
    assert invalido["pagina"] == invalido["paginas"] == 1
    por_estado = admin_api.get(API, {"orden": "estado"}).json()["elementos"]
    assert [e["etiqueta"]["valor"] for e in por_estado] == [
        "con_error",
        "con_advertencias",
        "sin_sorteos",
        "finalizada",
    ]


def test_listado_paridad_con_la_consulta_de_la_vista(admin_api):
    admin = admin_api.usuario
    terminada = crear_extraccion(admin, "finalizada")
    datos = admin_api.get(API).json()["elementos"][0]
    pagina = consultas.listado_extracciones()
    assert datos["id"] == pagina.elementos[0].pk == terminada.pk
    assert datos["eliminable"] is True
    assert datos["nombre_acciones"] == mensaje(
        "ext.acciones", fecha_hora=fecha_hora_ar(terminada.iniciada_en)
    )


def test_listado_con_la_propia_en_curso(admin_api):
    propia = crear_extraccion(admin_api.usuario, "en-curso")
    datos = admin_api.get(API).json()
    assert datos["en_curso_propia"]["id"] == propia.pk
    assert datos["en_curso_propia"]["eliminable"] is False
    assert datos["en_curso_propia"]["avance"]["en_curso"] is True
    assert datos["en_curso_propia"]["avance"]["aviso_final"] is None


# -- Iniciar ----------------------------------------------------------------------------


def test_iniciar_201_e_idempotencia(admin_api):
    clave = str(uuid.uuid4())
    hoy = hoy_buenos_aires()
    inicio = date(hoy.year, 1, 1).isoformat()
    respuesta = _post(admin_api, {"inicio": inicio, "fin": hoy.isoformat()}, clave)
    assert respuesta.status_code == 201
    creada = respuesta.json()
    assert creada["en_curso"] is True and creada["etiqueta"]["valor"] == "en_curso"
    assert creada["avance"]["identificando"] is True and creada["avance"]["total"] is None
    otra = _post(admin_api, {"inicio": inicio, "fin": hoy.isoformat()}, clave)
    assert otra.status_code == 201 and otra.json()["id"] == creada["id"]
    assert Extraccion.objects.count() == 1


def test_iniciar_con_la_propia_en_curso_409_ac_1_11(admin_api):
    propia = crear_extraccion(admin_api.usuario, "en-curso")
    respuesta = _post(admin_api, {"inicio": "2026-10-01", "fin": "2026-10-15"})
    assert respuesta.status_code == 409
    cuerpo = respuesta.json()
    assert cuerpo["detail"] == mensaje("ext.en_curso")
    assert cuerpo["existente"] == {
        "id": propia.pk,
        "url": f"/administracion/extracciones/{propia.pk}/",
    }
    assert Extraccion.objects.count() == 1


def test_iniciar_periodo_identico_de_otro_admin_409_rn_03(admin_api):
    otro = crear_usuario("otro@extracciones.local", admin=True)
    existente = crear_extraccion(otro, "en-curso")
    respuesta = _post(admin_api, {"inicio": "01/11/2026", "fin": "15/11/2026"})
    assert respuesta.status_code == 409
    cuerpo = respuesta.json()
    assert cuerpo["detail"] == mensaje(
        "ext.periodo_en_curso", desde=fecha_ar(existente.desde), hasta=fecha_ar(existente.hasta)
    )
    assert cuerpo["existente"]["id"] == existente.pk


@pytest.mark.parametrize(
    ("inicio", "fin", "esperados"),
    [
        ("", "", {("inicio", "fecha.falta_inicio"), ("fin", "fecha.falta_fin")}),
        ("31/02/2026", "2026-03-10", {("inicio", "fecha.inexistente")}),
        ("2026-03-10", "2026-03-01", {("", "ext.inicio_posterior"), ("fin", "fecha.fin_anterior")}),
        ("2024-01-01", "2025-06-01", {("", "ext.periodo_largo")}),
    ],
)
def test_iniciar_422_con_errores_por_campo_iguales_al_formulario(admin_api, inicio, fin, esperados):
    from extracciones.forms import PeriodoForm

    respuesta = _post(admin_api, {"inicio": inicio, "fin": fin})
    assert respuesta.status_code == 422
    errores = respuesta.json()["errores"]
    assert {(e["campo"], e["codigo"]) for e in errores} == esperados
    form = PeriodoForm({"inicio": inicio, "fin": fin})
    assert not form.is_valid()
    textos_form = {str(m) for lista in form.errors.values() for m in lista}
    assert {e["mensaje"] for e in errores} == textos_form  # NFR-009: mismos mensajes
    assert Extraccion.objects.count() == 0


def test_iniciar_fin_futura_422(admin_api):
    hoy = hoy_buenos_aires()
    futura = date(hoy.year + 1, 1, 1).isoformat()
    respuesta = _post(admin_api, {"inicio": hoy.isoformat(), "fin": futura})
    assert ("fin", "ext.fin_futura") in {
        (e["campo"], e["codigo"]) for e in respuesta.json()["errores"]
    }


# -- Detalle, avance y sorteo -----------------------------------------------------------


def test_detalle_avance_y_sorteo_de_una_extraccion_real(admin_api):
    extraccion = servicios.iniciar_extraccion(
        admin_api.usuario, servicios.Periodo(date(2026, 11, 1), date(2026, 11, 11))
    )
    procesar_pendientes(cliente_con_sorteos(SORTEOS), fichas_de(Fuente.F2))
    extraccion.refresh_from_db()

    detalle = admin_api.get(f"{API}{extraccion.pk}/").json()
    pantalla = consultas.datos_pagina(extraccion)
    assert detalle["estado_texto"] == pantalla["estado_texto"]
    assert detalle["en_curso"] is False and detalle["descargable"] is True
    assert detalle["url_csv"] == f"/administracion/extracciones/{extraccion.pk}/csv/"
    assert [s["numero"] for s in detalle["sorteos"]] == [3422, 3423, 3424, 3425]
    assert detalle["resumen"]["identificados"] == pantalla["resumen"]["identificados"]
    assert detalle["ninguna_fuente"] is False

    avance = admin_api.get(f"{API}{extraccion.pk}/avance/").json()
    assert avance["en_curso"] is False and avance["procesados"] == 4
    assert avance["aviso_final"]["texto"] == consultas.avance(extraccion)["aviso_final"]["texto"]

    sorteo = admin_api.get(f"{API}{extraccion.pk}/sorteos/3422/").json()
    vista = consultas.detalle_sorteo(extraccion, 3422)
    assert sorteo["numero"] == 3422 and sorteo["estado_texto"] == vista["estado_texto"]
    assert sorteo["fecha"]["estado"] == "valor" and sorteo["fecha"]["valor"] == "2026-11-01"
    assert [m["nombre"] for m in sorteo["modalidades"]] == [
        m["nombre"] for m in vista["modalidades"]
    ]
    numeros = sorteo["modalidades"][0]["numeros"]
    assert numeros["tipo"] == "numeros" and len(numeros["valor"]) == 6
    for modalidad in sorteo["modalidades"]:
        for categoria in modalidad["categorias"]:
            for dato in categoria["datos"]:
                if dato["estado"] != "valor":
                    assert dato["valor"] is None and dato["texto"]  # nunca null→0
                elif dato["tipo"] == "importe":
                    assert isinstance(dato["valor"], str) and "." in dato["valor"]
    assert admin_api.get(f"{API}{extraccion.pk}/sorteos/9999/").status_code == 404


def test_detalle_inexistente_404(admin_api):
    respuesta = admin_api.get(f"{API}999/")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == mensaje("ext.no_existe")


# -- Eliminar ---------------------------------------------------------------------------


def test_eliminar_204_aviso_e_idempotencia(admin_api):
    extraccion = crear_extraccion(admin_api.usuario, "finalizada")
    momento = fecha_hora_ar(extraccion.iniciada_en)
    clave = str(uuid.uuid4())
    assert _delete(admin_api, extraccion.pk, clave).status_code == 204
    assert not Extraccion.objects.exists()
    assert _delete(admin_api, extraccion.pk, clave).status_code == 204  # sin efecto ni error
    avisos = admin_api.get("/api/v1/avisos/").json()
    assert avisos == [{"tipo": "exito", "texto": mensaje("ext.eliminada", fecha_hora=momento)}]


def test_eliminar_en_curso_409_e_inexistente_404(admin_api):
    en_curso = crear_extraccion(admin_api.usuario, "en-curso")
    respuesta = _delete(admin_api, en_curso.pk)
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == mensaje("ext.eliminar_en_curso")
    inexistente = _delete(admin_api, 9999)
    assert inexistente.status_code == 404
    assert inexistente.json()["detail"] == mensaje("ext.no_existe")


def test_idempotency_key_de_otra_accion_422(admin_api):
    extraccion = crear_extraccion(admin_api.usuario, "finalizada")
    clave = str(uuid.uuid4())
    assert _delete(admin_api, extraccion.pk, clave).status_code == 204
    respuesta = _post(admin_api, {"inicio": "2026-11-01", "fin": "2026-11-15"}, clave)
    assert respuesta.status_code == 422


# -- Atajos -----------------------------------------------------------------------------


def test_atajos_de_la_extraccion(admin_api, visitante):
    hoy = hoy_buenos_aires()
    atajos = admin_api.get("/api/v1/periodos/atajos/", {"formulario": "extraccion"}).json()
    assert [a["clave"] for a in atajos] == ["anio_en_curso", "anio_anterior"]
    assert atajos[0]["desde"] == date(hoy.year, 1, 1).isoformat()
    assert atajos[0]["hasta"] == hoy.isoformat()
    assert atajos[0]["texto"] == mensaje("ext.atajo_anio_en_curso")
    assert visitante.get("/api/v1/periodos/atajos/", {"formulario": "otro"}).status_code == 422
