"""[002] contracts/csv.md (versión 1.0), RN-34 a RN-39, RN-43, NFR-008 a NFR-010 (T054)."""

import csv
import io
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal

from dominio.extraccion.archivo_csv import (
    ENCABEZADOS,
    VERSION_CONTRATO,
    generar_csv,
    nombre_archivo,
)
from dominio.extraccion.clasificacion import aplicar_clasificacion
from dominio.extraccion.consolidacion import consolidar
from dominio.extraccion.tipos import (
    Fuente,
    Modalidad,
    Observacion,
    ResultadoIntento,
    Valor,
)
from extracciones.fuentes.fichas import FICHAS
from tests.unit.extraccion.ayudas import (
    cambiar_categoria,
    datos_reales,
    intento,
    quitar_modalidad,
)

F1, F2, F3 = Fuente.F1, Fuente.F2, Fuente.F3
R = ResultadoIntento
M = Modalidad
MOMENTO = datetime(2026, 11, 19, 13, 15, 2, tzinfo=UTC)  # 10:15:02 en Buenos Aires
URL = {
    F1: "https://www.quini-6-resultados.com.ar/quini6/sorteo-3426-del-dia-15-11-2026.htm",
    F2: "https://numerosganadores.com.ar/sorteos/3426",
    F3: "https://quiniya.com.ar/sorteos/3426",
}


def sorteo(numero, *intentos):
    return aplicar_clasificacion(consolidar(numero, intentos, FICHAS))


def procedencia(*numeros):
    return {n: {f: (URL[f].replace("3426", str(n)), MOMENTO) for f in URL} for n in numeros}


def filas(texto):
    return list(csv.DictReader(io.StringIO(texto)))


def recuperado():
    return sorteo(3426, intento(datos_reales(F2)), intento(datos_reales(F3)))


def no_recuperado():
    return sorteo(3423, (F2, R.NO_DISPONIBLE_O_NO_ENCONTRADO, None), (F3, R.NO_ENCONTRADO, None))


def test_encabezados_exactos_y_en_orden():
    texto = generar_csv([recuperado()], procedencia(3426))
    assert texto.split("\r\n")[0] == ",".join(ENCABEZADOS)
    assert len(ENCABEZADOS) == 25 and ENCABEZADOS[-1] == "numeros_pozo_extra"  # v2.0 al final
    # v3.0 (D-22): sin acumulación ni importe trasladado.
    assert "se_acumula_segun_fuente" not in ENCABEZADOS and "importe_trasladado" not in ENCABEZADOS
    assert "precio" not in texto.split("\r\n")[0]  # AC-5.6


def test_formatos_tecnicos():
    fila = filas(generar_csv([recuperado()], procedencia(3426)))[0]
    assert fila["version_contrato"] == VERSION_CONTRATO == "3.0"
    assert fila["sorteo_fecha"] == "2026-11-15"
    assert fila["modalidad"] == "Tradicional"
    assert [fila[f"numero_{i}"] for i in range(1, 7)] == ["01", "02", "10", "13", "38", "39"]
    assert fila["categoria"] == "Primer Premio" and fila["aciertos"] == "6"
    assert fila["ganadores"] == "0" and fila["estado_pozo"] == "Vacante"
    assert fila["pozo_destinado"] == "1100000000.00"
    assert fila["importe_individual"] == "0.00"  # vacante (RN-18, D-16)
    assert fila["numeros_pozo_extra"] == "No corresponde"
    assert fila["sorteo_combina_fuentes"] == "No" and fila["sorteo_sin_corroborar"] == "No"


def test_ac_5_4_procedencia_con_fuente_direccion_y_fecha_hora_local():
    fila = filas(generar_csv([recuperado()], procedencia(3426)))[0]
    assert (
        "ganadores: numerosganadores.com.ar https://numerosganadores.com.ar/sorteos/3426 "
        "2026-11-19 10:15:02; quiniya.com.ar https://quiniya.com.ar/sorteos/3426 "
        "2026-11-19 10:15:02"
    ) in fila["procedencia"]


def test_orden_de_filas_y_nueve_por_sorteo_recuperado():
    texto = generar_csv([recuperado(), no_recuperado()], procedencia(3423, 3426))
    datos = filas(texto)
    assert [f["sorteo_numero"] for f in datos][:1] == ["3423"]  # sorteo ascendente
    del_3426 = [(f["modalidad"], f["categoria"]) for f in datos if f["sorteo_numero"] == "3426"]
    assert del_3426 == [
        ("Tradicional", "Primer Premio"),
        ("Tradicional", "Segundo Premio"),
        ("Tradicional", "Tercer Premio"),
        ("La Segunda", "Primer Premio"),
        ("La Segunda", "Segundo Premio"),
        ("La Segunda", "Tercer Premio"),
        ("Revancha", "Premio Revancha"),
        ("Siempre Sale", "Categoría ganadora"),
        ("Pozo Extra", "Categoría ganadora"),
    ]


def test_categoria_de_n_aciertos_al_final_por_aciertos_descendentes():
    d = datos_reales(F2)
    md = d.modalidades[M.PRIMER_SORTEO]
    base = md.categorias["TERCER"]
    categorias = {**md.categorias, "ACIERTOS_2": base, "ACIERTOS_3": base}
    d = replace(
        d,
        fecha=date(2024, 6, 17),
        modalidades={**d.modalidades, M.PRIMER_SORTEO: replace(md, categorias=categorias)},
    )
    datos = filas(generar_csv([sorteo(3426, intento(d))], procedencia(3426)))
    primer = [f["categoria"] for f in datos if f["modalidad"] == "Tradicional"]
    assert primer[-2:] == ["Categoría de 3 aciertos", "Categoría de 2 aciertos"]
    assert "Reglas del período no verificadas" in datos[0]["observaciones"]


def test_ac_5_8_no_recuperado_en_una_sola_fila_sin_numeros_ni_importes():
    datos = filas(generar_csv([no_recuperado()], procedencia(3423)))
    assert len(datos) == 1
    fila = datos[0]
    assert fila["sorteo_estado"] == "No recuperado"
    assert fila["sorteo_motivos"] == "Ninguna fuente informa este número de sorteo"
    assert fila["sorteo_fecha"] == "No disponible"
    for columna in ENCABEZADOS[7:20]:  # de modalidad a importe_individual
        assert fila[columna] == "No disponible", columna


def test_rn_39_modalidad_no_informada_en_una_fila():
    s = sorteo(3426, intento(quitar_modalidad(datos_reales(F2), M.REVANCHA), R.INCOMPLETO))
    revancha = [
        f for f in filas(generar_csv([s], procedencia(3426))) if f["modalidad"] == "Revancha"
    ]
    assert len(revancha) == 1
    assert revancha[0]["categoria"] == "No disponible"
    assert revancha[0]["observaciones"].startswith("No informada por las fuentes")
    assert revancha[0]["sorteo_estado"] == "Recuperado parcialmente"


def test_ac_5_5_sin_filas_duplicadas():
    datos = filas(generar_csv([recuperado(), no_recuperado()], procedencia(3423, 3426)))
    claves = [(f["sorteo_numero"], f["modalidad"], f["categoria"]) for f in datos]
    assert len(claves) == len(set(claves))


def test_ac_5_7_estados_distinguibles_y_ninguna_celda_de_valor_vacia():
    datos = filas(generar_csv([recuperado(), no_recuperado()], procedencia(3423, 3426)))
    for fila in datos:
        for columna in (*ENCABEZADOS[:20], "numeros_pozo_extra"):
            if columna == "sorteo_motivos":
                continue
            assert fila[columna] != "", columna
    assert "No corresponde" in {f["numero_1"] for f in datos}  # Pozo Extra (RN-20)
    assert "No disponible" in {f["ganadores"] for f in datos}  # no recuperado
    assert "0.00" in {f["importe_individual"] for f in datos}  # vacante: un valor, no vacío


def test_ac_3_17_numeros_de_pozo_extra_en_su_columna():
    """[002] RN-12, D-19: unión de Tradicional, La Segunda y Revancha, calculada."""
    datos = filas(generar_csv([recuperado()], procedencia(3426)))
    extra = next(f for f in datos if f["modalidad"] == "Pozo Extra")
    assert [extra[f"numero_{i}"] for i in range(1, 7)] == ["No corresponde"] * 6
    assert extra["numeros_pozo_extra"] == ("01 02 10 11 13 16 17 19 21 27 28 33 37 38 39 40")
    assert (
        "numeros_pozo_extra: Calculado: unión de Tradicional, La Segunda y Revancha"
        in extra["procedencia"]
    )


def test_ac_3_5_pozo_calculado_con_su_tramo_de_procedencia():
    """[002] RN-18, SC-002: 18 × 3.013.912 = 54.250.416, marcado "Calculado"."""
    datos = filas(generar_csv([recuperado()], procedencia(3426)))
    segundo = next(
        f for f in datos if f["modalidad"] == "Tradicional" and f["categoria"] == "Segundo Premio"
    )
    assert segundo["pozo_destinado"] == "54250416.00"
    assert "pozo_destinado: Calculado: importe individual × ganadores" in segundo["procedencia"]
    assert "pozo_destinado" not in segundo["datos_sin_corroborar"]


def test_ac_4_5_diferencia_tolerada_va_en_observaciones_y_no_en_discrepancias():
    f2 = cambiar_categoria(
        datos_reales(F2), M.PRIMER_SORTEO, "PRIMER", pozo_destinado=Valor(Decimal("657151589"))
    )
    f3 = cambiar_categoria(
        datos_reales(F3), M.PRIMER_SORTEO, "PRIMER", pozo_destinado=Valor(Decimal("657000000.80"))
    )
    fila = filas(generar_csv([sorteo(3426, intento(f2), intento(f3))], procedencia(3426)))[0]
    assert fila["pozo_destinado"] == "657151589.00"
    assert fila["discrepancias"] == ""
    assert fila["observaciones"] == (
        "pozo_destinado: Diferencia de centavos o redondeo (menor al 1 %) — "
        "657151589.00 (numerosganadores.com.ar); 657000000.80 (quiniya.com.ar)"
    )
    assert fila["sorteo_estado"] == "Recuperado"


def test_ac_4_1_gramatica_de_discrepancias():
    f2 = cambiar_categoria(
        datos_reales(F2), M.LA_SEGUNDA, "TERCER", importe_individual=Valor(Decimal("5015"))
    )
    f3 = cambiar_categoria(
        datos_reales(F3), M.LA_SEGUNDA, "TERCER", importe_individual=Valor(Decimal("5547.85"))
    )
    datos = filas(generar_csv([sorteo(3426, intento(f2), intento(f3))], procedencia(3426)))
    fila = next(
        f for f in datos if f["modalidad"] == "La Segunda" and f["categoria"] == "Tercer Premio"
    )
    assert fila["discrepancias"] == (
        "importe_individual: Valor distinto — 5015.00 (numerosganadores.com.ar); "
        "5547.85 (quiniya.com.ar)"
    )
    assert fila["importe_individual"] == "Sin determinar"
    assert fila["sorteo_estado"] == "Con inconsistencias"


def test_datos_sin_corroborar_y_observaciones_con_fuente():
    s = sorteo(3426, intento(datos_reales(F1)), intento(datos_reales(F2)))
    datos = filas(generar_csv([s], procedencia(3426)))
    extra = next(f for f in datos if f["modalidad"] == "Pozo Extra")
    assert "pozo_destinado" in extra["datos_sin_corroborar"].split("; ")
    assert (
        "quini-6-resultados.com.ar: Pozo Extra publicado como «55 millones de pesos»"
        in extra["observaciones"]
    )


def test_ac_5_9_proteccion_contra_formulas():
    s = recuperado()
    s = replace(
        s,
        observaciones=(Observacion("obs.x", "=HYPERLINK(1)", None),),
        motivos=("+malicioso", "@otro"),
    )
    texto = generar_csv([s], procedencia(3426))
    fila = filas(texto)[0]
    assert fila["observaciones"] == "'=HYPERLINK(1)"
    assert fila["sorteo_motivos"] == "'+malicioso | @otro"


def test_formato_del_archivo_y_determinismo():
    texto = generar_csv([recuperado()], procedencia(3426))
    assert texto.endswith("\r\n") and "\n" not in texto.replace("\r\n", "")
    assert not texto.startswith("﻿")
    assert generar_csv([recuperado()], procedencia(3426)) == texto
    assert '"' not in texto.split("\r\n")[1] or "," in texto.split("\r\n")[1]


def test_nombre_del_archivo():
    assert (
        nombre_archivo(7, date(2026, 11, 1), date(2026, 11, 15))
        == "quini6-extraccion-7-2026-11-01-a-2026-11-15.csv"
    )
