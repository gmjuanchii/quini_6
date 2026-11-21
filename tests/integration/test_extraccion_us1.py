"""[002] Historia 1: ejecutar una extracción y ver su resumen, con una sola fuente (F2) (T026).

Sin internet: el trabajador usa ``ClienteHttpFalso`` con páginas armadas desde copias reales.
"""

from datetime import date

import pytest
from django.test import Client

from dominio.extraccion.tipos import Fuente
from extracciones import servicios
from extracciones.models import Extraccion
from tests.extraccion_falsos import (
    HOY,
    cliente_con_sorteos,
    fichas_de,
    pagina,
    procesar_pendientes,
    url_listado,
    url_sorteo,
)
from tests.fabricas import crear_usuario

pytestmark = pytest.mark.django_db

INICIO = "/administracion/extracciones/"
F2 = Fuente.F2
OCTUBRE_NOVIEMBRE = {
    3418: date(2026, 10, 18),
    3419: date(2026, 10, 21),
    3420: date(2026, 10, 25),
    3421: date(2026, 10, 28),
    3422: date(2026, 11, 1),
    3423: date(2026, 11, 4),
    3424: date(2026, 11, 8),
    3425: date(2026, 11, 11),
    3426: date(2026, 11, 15),
    3427: date(2026, 11, 18),
}


@pytest.fixture(autouse=True)
def hoy_fijo(monkeypatch):
    monkeypatch.setattr("extracciones.forms.hoy_buenos_aires", lambda: HOY)


def iniciar(cliente, inicio="01/11/2026", fin="15/11/2026"):
    return cliente.post(INICIO, {"inicio": inicio, "fin": fin})


def html(respuesta):
    return respuesta.content.decode()


def test_ac_1_1_acceso_y_pantalla(cliente_admin):
    assert 'href="/administracion/extracciones/"' in html(
        cliente_admin.get("/administracion/concursos/")
    )
    texto = html(cliente_admin.get(INICIO))
    for esperado in (
        "Extracción histórica de sorteos",
        "Fecha de inicio",
        "Fecha de finalización",
        "Iniciar extracción",
        'href="/administracion/concursos/"',
    ):
        assert esperado in texto


@pytest.mark.parametrize("inicio, fin, mensaje", [
    ("15/11/2026", "01/11/2026", "La fecha de inicio no puede ser posterior a la fecha de finalización"),  # noqa: E501
    ("", "15/11/2026", "Ingresá una fecha válida (dd/mm/aaaa)"),
    ("31/02/2026", "15/11/2026", "Ingresá una fecha válida (dd/mm/aaaa)"),
    ("01/11/2026", "20/11/2026", "La fecha de finalización no puede ser posterior a hoy"),
    ("01/11/2025", "01/11/2026", "El período no puede superar los 12 meses"),
])  # fmt: skip
def test_ac_1_3_a_1_6_errores_del_periodo(cliente_admin, inicio, fin, mensaje):
    respuesta = iniciar(cliente_admin, inicio, fin)
    assert respuesta.status_code == 200
    texto = html(respuesta)
    assert mensaje in texto
    # AC-1.20: el selector de fecha recibe AAAA-MM-DD y lo muestra como dd/mm/aaaa (D-25).
    assert f'value="{"-".join(reversed(fin.split("/")))}"' in texto
    assert Extraccion.objects.count() == 0


def test_ac_1_2_y_1_11_inicio_avance_y_recarga(cliente_admin, admin):
    respuesta = iniciar(cliente_admin)
    extraccion = Extraccion.objects.get()
    assert respuesta.status_code == 303
    assert respuesta["Location"] == f"{INICIO}{extraccion.pk}/"
    texto = html(cliente_admin.get(respuesta["Location"]))
    assert "Extracción en curso" in texto
    assert "01/11/2026 al 15/11/2026" in texto
    assert "Identificando los sorteos del período…" in texto
    assert 'aria-live="polite"' in texto and "data-en-curso" in texto
    assert "<progress" not in texto  # AC-1.21: sin barra mientras se identifica
    # AC-1.11: un segundo POST y la recarga llevan a la misma extracción.
    otra = iniciar(cliente_admin, "01/10/2026", "15/10/2026")
    assert otra.status_code == 303 and otra["Location"] == respuesta["Location"]
    assert Extraccion.objects.count() == 1
    inicio = html(cliente_admin.get(INICIO))
    assert "Iniciar extracción" not in inicio and "Extracción en curso" in inicio

    # Con un sorteo ya procesado: avance y detalle disponibles mientras sigue en curso.
    cliente = cliente_con_sorteos(OCTUBRE_NOVIEMBRE)
    extraccion.numero_desde, extraccion.numero_hasta = 3422, 3426
    extraccion.save()
    estado = servicios._Estado(cliente, fichas_de(F2), servicios.INTERPRETES)
    servicios._leer_listados(estado)
    servicios.procesar_sorteo(extraccion, estado, 3422)
    texto = html(cliente_admin.get(respuesta["Location"]))
    assert "1 de 5 sorteos procesados" in texto
    # AC-1.21 (D-26): barra de progreso con la misma proporción, nombrada por el texto.
    assert 'value="1" max="5" aria-labelledby="avance-texto"' in texto
    assert cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3422/").status_code == 200

    procesar_pendientes(cliente, fichas_de(F2))
    texto = html(cliente_admin.get(respuesta["Location"]))
    assert "Extracción finalizada" in texto and "data-en-curso" not in texto
    assert extraccion.sorteos.count() == 5  # reanudada sin duplicar


def test_ac_1_7_a_1_9_resumen_con_hueco(cliente_admin):
    sin_3423 = {n: f for n, f in OCTUBRE_NOVIEMBRE.items() if n != 3423}
    cliente = cliente_con_sorteos(sin_3423)
    cliente.responder(url_sorteo(F2, 3423), 500, "Error.")
    iniciar(cliente_admin)
    procesar_pendientes(cliente, fichas_de(F2))
    extraccion = Extraccion.objects.get()
    texto = html(cliente_admin.get(f"{INICIO}{extraccion.pk}/"))
    assert "Extracción finalizada con advertencias que requieren revisión" in texto
    for rotulo, valor in (
        ("Período consultado", "01/11/2026 al 15/11/2026"),
        ("Sorteos identificados", "5"),
        ("Recuperados", "4"),
        ("Recuperados parcialmente", "0"),
        ("Con inconsistencias", "0"),
        ("No recuperados", "1"),
    ):
        assert f'<th scope="row">{rotulo}</th><td>{valor}</td>' in texto
    assert "Fuentes utilizadas" in texto and "numerosganadores.com.ar" in texto
    assert "Sorteos que requieren revisión" in texto
    assert "Ninguna fuente informa este número de sorteo" in texto
    assert "Hay números de sorteo que ninguna fuente informa: 3423" in texto  # AC-1.16
    assert "Descargar CSV" in texto


def test_ac_1_10_periodo_sin_sorteos(cliente_admin):
    iniciar(cliente_admin, "05/11/2026", "07/11/2026")
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    extraccion = Extraccion.objects.get()
    texto = html(cliente_admin.get(f"{INICIO}{extraccion.pk}/"))
    assert "No se identificaron sorteos en el período consultado" in texto
    assert "Descargar CSV" not in texto
    assert extraccion.estado == "SIN_SORTEOS" and extraccion.archivo_csv == ""


def test_ac_1_17_periodo_anterior_a_la_cobertura(cliente_admin):
    cliente = cliente_con_sorteos(OCTUBRE_NOVIEMBRE)
    fechas = [
        date(2014, 12, 17), date(2014, 12, 21), date(2014, 12, 24), date(2014, 12, 28),
        date(2014, 12, 31), date(2015, 1, 4), date(2015, 1, 7), date(2015, 1, 11),
    ]  # fmt: skip
    for numero, fecha in zip(range(2211, 2219), fechas, strict=True):
        cliente.responder(url_sorteo(F2, numero), 200, pagina(F2, numero, fecha, base=2211))
    iniciar(cliente_admin, "01/06/2014", "31/12/2014")
    procesar_pendientes(cliente, fichas_de(F2))
    extraccion = Extraccion.objects.get()
    assert (extraccion.numero_desde, extraccion.numero_hasta) == (2211, 2215)
    texto = html(cliente_admin.get(f"{INICIO}{extraccion.pk}/"))
    assert "Las fuentes no cubren el período anterior al 17/12/2014" in texto
    detalle = html(cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/2211/"))
    assert "Reglas del período no verificadas" in detalle  # AC-3.11


def test_ac_1_12_y_1_13_detalle_del_sorteo(cliente_admin):
    iniciar(cliente_admin)
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    extraccion = Extraccion.objects.get()
    texto = html(cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3426/"))
    assert "numerosganadores.com.ar" in texto
    assert "Obtenido" in texto
    assert "https://numerosganadores.com.ar/sorteos/3426" in texto
    assert "19/11/2026 10:15" in texto  # fecha y hora de la consulta, en Buenos Aires
    assert "<h2>Tradicional</h2>" in texto and "01, 02, 10, 13, 38, 39" in texto
    assert "$ 1.100.000.000,00" in texto and "Sin corroborar" in texto
    assert "Ver extracto oficial (Lotería de Santa Fe)" in texto
    assert 'target="_blank" rel="noopener noreferrer"' in texto
    # D-23: las fuentes solo figuran en "Fuentes consultadas", no junto a cada dato.
    assert 'data-rotulo="Fuentes"' not in texto
    assert "(numerosganadores.com.ar" not in texto
    assert "Calculado: importe individual" not in texto
    # D-22: sin acumulación ni importe trasladado.
    assert "Se acumula según la fuente" not in texto and "Importe trasladado" not in texto


def test_ac_1_14_y_1_15_extracciones_anteriores_y_otro_administrador(cliente_admin, admin):
    iniciar(cliente_admin, "01/10/2026", "31/10/2026")
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    iniciar(cliente_admin)
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    otro = Client()
    otro.force_login(crear_usuario("admin2@prueba.local", admin=True))
    texto = html(otro.get(INICIO))
    assert "Extracciones anteriores" in texto
    assert texto.index("01/11/2026 al 15/11/2026") < texto.index("01/10/2026 al 31/10/2026")
    assert admin.email in texto and "Extracción finalizada" in texto
    reciente = Extraccion.objects.order_by("-iniciada_en", "-id").first()
    assert otro.get(f"{INICIO}{reciente.pk}/").status_code == 200
    assert otro.get(f"{INICIO}{reciente.pk}/sorteos/3422/").status_code == 200
    assert (
        otro.get(f"{INICIO}{reciente.pk}/csv/").content
        == cliente_admin.get(f"{INICIO}{reciente.pk}/csv/").content
    )


def test_numero_que_no_pertenece_a_la_extraccion_da_404(cliente_admin):
    iniciar(cliente_admin)
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    extraccion = Extraccion.objects.get()
    respuesta = cliente_admin.get(f"{INICIO}{extraccion.pk}/sorteos/3427/")
    assert respuesta.status_code == 404
    assert "La página que buscás no existe" in html(respuesta)
    assert cliente_admin.get(f"{INICIO}999/").status_code == 404


def test_listado_inaccesible_no_detiene_la_extraccion(cliente_admin):
    cliente = cliente_con_sorteos(OCTUBRE_NOVIEMBRE)
    cliente.responder(url_listado(F2), 503, "")
    iniciar(cliente_admin)
    procesar_pendientes(cliente, fichas_de(F2))
    assert Extraccion.objects.get().estado != "EN_CURSO"


def test_ac_1_20_campos_de_fecha_con_calendario(cliente_admin):
    """D-25, D-27: ``type="date"`` sin días futuros (calendario nativo en el ícono), sin script que
    lo abra al hacer clic (tomaba las teclas) y fechas AAAA-MM-DD o dd/mm/aaaa."""
    texto = html(cliente_admin.get(INICIO))
    assert texto.count('type="date"') == 2 and texto.count('max="2026-11-19"') == 2
    assert "data-calendario" not in texto and "selector-fecha.js" not in texto
    respuesta = cliente_admin.post(INICIO, {"inicio": "2026-11-01", "fin": "2026-11-15"})
    assert respuesta.status_code == 303
    extraccion = Extraccion.objects.get()
    assert (extraccion.desde, extraccion.hasta) == (date(2026, 11, 1), date(2026, 11, 15))


def test_ac_1_14_columna_fecha_y_menu_de_acciones(cliente_admin):
    """D-24: la columna se llama "Fecha" y solo las terminadas ofrecen "Eliminar"."""
    iniciar(cliente_admin, "01/10/2026", "31/10/2026")
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    terminada = Extraccion.objects.get()
    iniciar(cliente_admin)
    en_curso = Extraccion.objects.exclude(pk=terminada.pk).get()
    texto = html(cliente_admin.get(INICIO))
    assert '<th scope="col">Fecha</th>' in texto and '<th scope="col">Inicio</th>' not in texto
    assert f'href="{INICIO}{terminada.pk}/eliminar/"' in texto
    assert f'href="{INICIO}{en_curso.pk}/eliminar/"' not in texto
    assert 'aria-label="Acciones de la extracción del' in texto


def test_ac_1_18_eliminar_extraccion_terminada(cliente_admin, admin):
    iniciar(cliente_admin)
    procesar_pendientes(cliente_con_sorteos(OCTUBRE_NOVIEMBRE), fichas_de(F2))
    extraccion = Extraccion.objects.get()
    otro = Client()
    otro.force_login(crear_usuario("admin2@prueba.local", admin=True))
    confirmacion = otro.get(f"{INICIO}{extraccion.pk}/eliminar/")
    texto = html(confirmacion)
    assert confirmacion.status_code == 200 and confirmacion["Cache-Control"] == "no-store"
    for esperado in (
        "Eliminar extracción",
        "¿Querés eliminar esta extracción? Se borran su resumen, el detalle de sus sorteos y su "
        "archivo CSV. Esta acción no se puede deshacer.",
        "01/11/2026 al 15/11/2026",
        admin.email,
        "Cancelar",
    ):
        assert esperado in texto
    assert Extraccion.objects.count() == 1  # el GET no elimina
    respuesta = otro.post(f"{INICIO}{extraccion.pk}/eliminar/")
    assert respuesta.status_code == 303 and respuesta["Location"] == INICIO
    assert "Extracción eliminada" in html(otro.get(INICIO))
    assert not Extraccion.objects.exists()
    from extracciones.models import IntentoConsulta, SorteoExtraido

    assert not SorteoExtraido.objects.exists() and not IntentoConsulta.objects.exists()
    for ruta in ("", "sorteos/3422/", "csv/", "eliminar/"):
        assert otro.get(f"{INICIO}{extraccion.pk}/{ruta}").status_code == 404


def test_ac_1_19_no_se_elimina_una_extraccion_en_curso(cliente_admin):
    iniciar(cliente_admin)
    extraccion = Extraccion.objects.get()
    for respuesta in (
        cliente_admin.get(f"{INICIO}{extraccion.pk}/eliminar/"),
        cliente_admin.post(f"{INICIO}{extraccion.pk}/eliminar/"),
    ):
        assert respuesta.status_code == 303 and respuesta["Location"] == INICIO
    assert "No se puede eliminar una extracción en curso" in html(cliente_admin.get(INICIO))
    assert Extraccion.objects.get().en_curso
    assert servicios.eliminar_extraccion(extraccion) == servicios.NO_ELIMINABLE_EN_CURSO
