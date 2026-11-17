"""Estado resumido de una jugada en el historial (AC-5.13, P-04)."""

from decimal import Decimal

from dominio.comparacion import (
    Elegibilidad,
    EstadoResumido,
    EstadoValidacion,
    ResultadoModalidad,
    ResultadoPremio,
    resumir_jugada,
)
from dominio.tipos import Modalidad

PUB = EstadoValidacion.PUBLICADO


def _r(
    modalidad=Modalidad.PRIMER_SORTEO,
    estado=PUB,
    premio=ResultadoPremio.SIN_PREMIO,
    importe=None,
    pendiente=False,
    **kw,
):
    publicado = estado in (EstadoValidacion.PUBLICADO, EstadoValidacion.EN_REVISION)
    return ResultadoModalidad(
        modalidad=modalidad,
        estado_validacion=estado,
        aciertos=2 if publicado else None,
        resultado_premio=premio if publicado else None,
        importe=importe,
        importe_pendiente=pendiente,
        **kw,
    )


CON = ResultadoPremio.CON_PREMIO
PEND = ResultadoPremio.PENDIENTE_DETERMINACION


def test_con_premio_con_importe():
    assert resumir_jugada([_r(premio=CON, importe=Decimal("10"))]) is EstadoResumido.CON_PREMIO


def test_con_premio_importe_pendiente():
    resultados = [
        _r(premio=CON, importe=Decimal("10")),
        _r(Modalidad.LA_SEGUNDA, premio=CON, pendiente=True),
    ]
    assert resumir_jugada(resultados) is EstadoResumido.CON_PREMIO_IMPORTE_PENDIENTE


def test_pendiente_determinacion():
    resultados = [_r(), _r(Modalidad.SIEMPRE_SALE, premio=PEND)]
    assert resumir_jugada(resultados) is EstadoResumido.PENDIENTE_DETERMINACION


def test_resultado_pendiente():
    resultados = [_r(), _r(Modalidad.LA_SEGUNDA, estado=EstadoValidacion.RESULTADO_PENDIENTE)]
    assert resumir_jugada(resultados) is EstadoResumido.RESULTADO_PENDIENTE
    resultados = [_r(), _r(Modalidad.LA_SEGUNDA, estado=EstadoValidacion.PENDIENTE_VALIDACION)]
    assert resumir_jugada(resultados) is EstadoResumido.RESULTADO_PENDIENTE


def test_sin_premio():
    assert resumir_jugada([_r(), _r(Modalidad.REVANCHA)]) is EstadoResumido.SIN_PREMIO


def test_excluida_del_premio_extra_cuenta_como_sin_premio():
    excluida = _r(
        Modalidad.PREMIO_EXTRA,
        premio=None,
        elegibilidad=Elegibilidad.EXCLUIDA,
        excluida_por=Modalidad.PRIMER_SORTEO,
    )
    assert resumir_jugada([_r(), excluida]) is EstadoResumido.SIN_PREMIO


def test_sin_modalidades():
    assert resumir_jugada([]) is EstadoResumido.RESULTADO_PENDIENTE


class TestPrecedencia:
    def test_con_premio_gana_a_pendientes(self):
        resultados = [
            _r(premio=CON, importe=Decimal("1")),
            _r(Modalidad.SIEMPRE_SALE, premio=PEND),
            _r(Modalidad.REVANCHA, estado=EstadoValidacion.RESULTADO_PENDIENTE),
        ]
        assert resumir_jugada(resultados) is EstadoResumido.CON_PREMIO

    def test_importe_pendiente_gana_a_determinacion(self):
        resultados = [_r(premio=CON, pendiente=True), _r(Modalidad.SIEMPRE_SALE, premio=PEND)]
        assert resumir_jugada(resultados) is EstadoResumido.CON_PREMIO_IMPORTE_PENDIENTE

    def test_determinacion_gana_a_resultado_pendiente(self):
        resultados = [
            _r(Modalidad.SIEMPRE_SALE, premio=PEND),
            _r(Modalidad.REVANCHA, estado=EstadoValidacion.PENDIENTE_VALIDACION),
        ]
        assert resumir_jugada(resultados) is EstadoResumido.PENDIENTE_DETERMINACION

    def test_textos(self):
        assert EstadoResumido.CON_PREMIO.texto == "Con premio"
        assert EstadoResumido.CON_PREMIO_IMPORTE_PENDIENTE.texto == (
            "Con premio — información de premios pendiente de publicación"
        )
        assert EstadoResumido.PENDIENTE_DETERMINACION.texto == "Premio pendiente de determinación"
        assert EstadoResumido.RESULTADO_PENDIENTE.texto == "Resultado pendiente"
        assert EstadoResumido.SIN_PREMIO.texto == "Sin premio"
