"""[002] RN-10, RN-33, I-05, I-10: resumen de una extracción (T025, T067)."""

from datetime import date

from dominio.extraccion.clasificacion import aplicar_clasificacion
from dominio.extraccion.consolidacion import consolidar
from dominio.extraccion.identificacion import Identificacion
from dominio.extraccion.resumen import resumir
from dominio.extraccion.tipos import Fuente, ResultadoIntento
from extracciones.fuentes.fichas import FICHAS
from tests.unit.extraccion.ayudas import datos_reales, intento

F1, F2, F3 = Fuente.F1, Fuente.F2, Fuente.F3
R = ResultadoIntento
FUENTES = (F1, F2, F3)


def sorteo(numero, *intentos):
    return aplicar_clasificacion(consolidar(numero, intentos, FICHAS))


def recuperado(numero):
    return sorteo(numero, (F1, R.FUERA_DE_COBERTURA, None), intento(datos_reales(F2)),
                  (F3, R.NO_ENCONTRADO, None))  # fmt: skip


def hueco(numero):
    return sorteo(
        numero,
        (F1, R.FUERA_DE_COBERTURA, None),
        (F2, R.NO_DISPONIBLE_O_NO_ENCONTRADO, None),
        (F3, R.NO_ENCONTRADO, None),
    )


def caido(numero):
    return sorteo(numero, (F1, R.FUERA_DE_COBERTURA, None), (F2, R.NO_DISPONIBLE, None),
                  (F3, R.ESTRUCTURA_NO_RECONOCIDA, None))  # fmt: skip


def test_ac_1_8_los_cuatro_estados_suman_los_identificados():
    r = resumir(Identificacion(3422, 3424), [recuperado(3422), hueco(3423), caido(3424)], FUENTES)
    assert r["identificados"] == 3
    assert sum(r["por_estado"].values()) == 3
    assert r["por_estado"]["RECUPERADO"] == 1 and r["por_estado"]["NO_RECUPERADO"] == 2


def test_ac_1_9_lista_a_revisar_con_numero_fecha_estado_y_motivos():
    r = resumir(Identificacion(3422, 3423), [recuperado(3422), hueco(3423)], FUENTES)
    assert r["a_revisar"] == [
        {
            "numero": 3423,
            "fecha": None,
            "estado": "NO_RECUPERADO",
            "motivos": ["Ninguna fuente informa este número de sorteo"],
        }
    ]
    assert r["resultado"] == "CON_ADVERTENCIAS"


def test_ac_1_16_huecos_solo_segun_i_10():
    r = resumir(Identificacion(3422, 3424), [recuperado(3422), hueco(3423), caido(3424)], FUENTES)
    assert r["huecos"] == [3423]


def test_ac_1_17_cobertura():
    r = resumir(Identificacion(2211, 2211, date(2014, 12, 17)), [recuperado(2211)], FUENTES)
    assert r["cobertura_desde"] == "2014-12-17"


def test_rn_33_finalizada_solo_si_todos_recuperados():
    r = resumir(Identificacion(3422, 3422), [recuperado(3422)], FUENTES)
    assert r["resultado"] == "FINALIZADA"


def test_ac_2_1_intentos_fallidos_por_tipo_y_sorteos_aportados():
    incompleto = sorteo(3424, intento(datos_reales(F2), R.INCOMPLETO), (F3, R.NO_DISPONIBLE, None))
    r = resumir(Identificacion(3422, 3424), [recuperado(3422), hueco(3423), incompleto], FUENTES)
    por_fuente = {f["fuente"]: f for f in r["fuentes"]}
    assert por_fuente["F2"]["aportados"] == 2  # I-05
    assert por_fuente["F2"]["fallidos"] == {
        "INCOMPLETO": 1, "NO_DISPONIBLE_O_NO_ENCONTRADO": 1,
    }  # fmt: skip
    assert por_fuente["F3"]["fallidos"] == {"NO_ENCONTRADO": 2, "NO_DISPONIBLE": 1}
    assert por_fuente["F1"]["fallidos"] == {}  # "Fuera de cobertura" no es falla (AC-2.6)
    assert por_fuente["F1"]["aportados"] == 0


def test_ac_2_10_requiere_mantenimiento():
    r = resumir(Identificacion(3424, 3425), [caido(3424), caido(3425)], FUENTES)
    por_fuente = {f["fuente"]: f for f in r["fuentes"]}
    assert por_fuente["F3"]["requiere_mantenimiento"]
    assert not por_fuente["F2"]["requiere_mantenimiento"]
    assert not por_fuente["F1"]["requiere_mantenimiento"]  # no cubre ningún sorteo
