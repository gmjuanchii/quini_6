"""Consolidación de las fuentes de un sorteo ([002] RN-07, RN-09, RN-12, RN-18, RN-22, RN-23,
RN-27 a RN-30, RN-32, I-03, I-06; Clarifications 20/11/2026, D-14 a D-19, D-29).

Cada dato se compara entre las fuentes que lo informan. Si difieren, prevalece el valor de la
fuente de mayor prioridad (RN-07) y la diferencia queda registrada como discrepancia, salvo los
importes: coinciden si difieren en menos de $ 1,00 (D-28); con una diferencia menor al 1 % se
toma el de mayor prioridad sin centavos, con una nota informativa; desde el 1 % quedan "Sin
determinar" (RN-30). Un dato que viola RN-26 no se compara (D-29). Los únicos
datos calculados (pozo con ganadores, importe individual de una vacante y números de Pozo Extra)
llevan el texto de su cálculo. No importa Django.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from decimal import ROUND_DOWN, Decimal

from dominio.extraccion.tipos import (
    CALCULO_POZO,
    CALCULO_POZO_EXTRA,
    CALCULO_VACANTE,
    MODALIDADES_PROPIAS,
    NO_CORRESPONDE,
    NO_DISPONIBLE,
    NO_DISPONIBLE_CONSOLIDADO,
    SIN_DETERMINAR,
    CategoriaConsolidada,
    Dato,
    DatoConsolidado,
    DatosFuente,
    Discrepancia,
    EstadoPozo,
    Ficha,
    Fuente,
    Modalidad,
    ModalidadConsolidada,
    Observacion,
    ResultadoIntento,
    SorteoConsolidado,
    TipoDiscrepancia,
    Valor,
    categorias_esperadas,
    orden_categorias,
    prioridad,
    viola_rn_26,
)
from dominio.tipos import FECHA_VIGENCIA_REGLAS, MODALIDADES_PREMIO_EXTRA, ORDEN_MODALIDADES

OBS_NO_CORRELATIVO = "El número y la fecha no son correlativos con el sorteo N.º {N}"

#: [002] RN-30: una diferencia de importes menor al 1 % del valor prioritario se tolera.
TOLERANCIA_IMPORTES = Decimal("0.01")
#: [002] RN-30, D-28: dos importes que difieren en menos de un peso coinciden.
_UN_PESO = Decimal("1")

CAMPOS_CATEGORIA = ("aciertos", "ganadores", "pozo_destinado", "importe_individual")
_CAMPOS_IMPORTE = ("pozo_destinado", "importe_individual")

Intento = tuple[Fuente, ResultadoIntento, DatosFuente | None]


def _comparar(candidatos: list[tuple[Fuente, Dato, bool, bool]]) -> DatoConsolidado:
    """[002] RN-07, RN-27, RN-28, RN-30. Cada candidato: (fuente, dato, publica por ficha,
    descartado).

    ``descartado`` indica que la fuente presentó el dato con un formato inválido: no es una
    omisión (ya tiene su observación, RN-16 y RN-24).
    """
    candidatos = sorted(candidatos, key=lambda c: prioridad(c[0]))
    valores = [(f, d.v) for f, d, _, _ in candidatos if isinstance(d, Valor)]
    if not valores:
        if any(d is NO_CORRESPONDE for _, d, _, _ in candidatos):
            return DatoConsolidado(NO_CORRESPONDE)
        return NO_DISPONIBLE_CONSOLIDADO
    omisiones = [
        (f, None)
        for f, d, publica, descartado in candidatos
        if publica and not descartado and d is NO_DISPONIBLE
    ]
    distintos = _distintos([v for _, v in valores])
    if not distintos and not omisiones:
        fuentes = tuple(f for f, _ in valores)
        return DatoConsolidado(Valor(valores[0][1]), fuentes, sin_corroborar=len(fuentes) == 1)
    referencia = valores[0][1]
    es_importe = all(isinstance(v, Decimal) for _, v in valores)
    por_mayoria = _mayoria(valores + omisiones, es_importe)
    if por_mayoria is not None:
        return por_mayoria
    if distintos and es_importe and not omisiones:
        # RN-30, D-28: coinciden si difieren en menos de $ 1,00; si no, se toleran diferencias
        # menores al 1 % de los importes sin centavos. El valor es el prioritario sin centavos.
        valor = Valor(_sin_centavos(referencia))
        fuentes = tuple(f for f, _ in valores)
        nota = Discrepancia(TipoDiscrepancia.CENTAVOS, tuple(valores))
        if all(_coinciden_en_pesos(referencia, v) for _, v in valores[1:]):
            # Sin nota solo si el importe prioritario es el publicado (no tenía centavos).
            sin_nota = valor.v == referencia
            return DatoConsolidado(valor, fuentes, diferencia_tolerada=None if sin_nota else nota)
        if _dentro_de_tolerancia([(f, _sin_centavos(v)) for f, v in valores]):
            # Diferencia menor al 1 %: valor prioritario sin centavos y nota informativa.
            return DatoConsolidado(valor, fuentes, diferencia_tolerada=nota)
    tipo = TipoDiscrepancia.VALOR_DISTINTO if distintos else TipoDiscrepancia.OMISION
    todos = sorted(valores + omisiones, key=lambda par: prioridad(par[0]))
    discrepancia = Discrepancia(tipo, tuple(todos))
    if distintos and es_importe:
        return DatoConsolidado(SIN_DETERMINAR, discrepancia=discrepancia)  # RN-30: 1 % o más
    # RN-07: prevalece la fuente de mayor prioridad; la diferencia sigue siendo discrepancia.
    fuentes = tuple(f for f, v in valores if v == referencia)
    return DatoConsolidado(
        Valor(referencia), fuentes, sin_corroborar=len(fuentes) == 1, discrepancia=discrepancia
    )


def _mayoria(todos: list[tuple[Fuente, object]], es_importe: bool) -> DatoConsolidado | None:
    """[002] RN-07, D-21: con tres o más fuentes, si dos o más coinciden en un valor y ningún
    otro valor reúne la misma cantidad, ese valor resuelve la diferencia, con una nota
    informativa. Una omisión (``None``) cuenta como una respuesta más, pero nunca gana. Dos
    importes coinciden si difieren en menos de $ 1,00 (RN-30, D-28): cada importe se suma al
    grupo del primero, en orden de prioridad, con el que coincide. ``None`` si no hay mayoría."""
    if len(todos) < 3:
        return None
    todos = sorted(todos, key=lambda par: prioridad(par[0]))
    grupos: list[list[tuple[Fuente, object]]] = []
    for fuente, v in todos:
        grupo = next((g for g in grupos if _misma_respuesta(g[0][1], v, es_importe)), None)
        if grupo is None:
            grupos.append([(fuente, v)])
        else:
            grupo.append((fuente, v))
    ordenados = sorted(grupos, key=len, reverse=True)  # estable: a igual tamaño, por prioridad
    grupo = ordenados[0]
    empate = len(ordenados) > 1 and len(ordenados[1]) == len(grupo)
    if grupo[0][1] is None or len(grupo) < 2 or empate or len(grupo) == len(todos):
        return None  # sin mayoría, o todas coinciden y no hay nada que desempatar
    crudos = [v for _, v in grupo]
    # Sin centavos solo si las fuentes de la mayoría no publican el mismo importe.
    valor = crudos[0] if not _distintos(crudos) else _sin_centavos(crudos[0])
    return DatoConsolidado(
        Valor(valor),
        tuple(f for f, _ in grupo),
        diferencia_tolerada=Discrepancia(TipoDiscrepancia.MAYORIA, tuple(todos)),
    )


def perdedoras_por_mayoria(sorteo: SorteoConsolidado) -> set[tuple[Fuente, Modalidad]]:
    """[002] D-21: (fuente, modalidad) en las que la fuente quedó en minoría en algún dato."""
    perdedoras = set()
    for modalidad, mc in sorteo.modalidades.items():
        datos = [mc.numeros] + [
            getattr(c, campo) for c in mc.categorias.values() for campo in CAMPOS_CATEGORIA
        ]
        for d in datos:
            mayoria = d.diferencia_tolerada
            if mayoria is not None and mayoria.tipo is TipoDiscrepancia.MAYORIA:
                perdedoras.update((f, modalidad) for f, _ in mayoria.valores if f not in d.fuentes)
    return perdedoras


#: Observaciones de RN-26 sobre la categoría ganadora (``normalizacion._validar_ganadora``).
_OBS_GANADORA_INVALIDA = ("obs.siempre_sale_invalida", "obs.premio_extra_invalida")


def _invalidas_superadas(
    sorteo: SorteoConsolidado, fuentes_datos: list[tuple[Fuente, DatosFuente]]
) -> set[tuple[Fuente, Modalidad]]:
    """[002] D-29: (fuente, modalidad) en las que cada dato que violaba RN-26 se descartó y el
    consolidado tiene el valor válido de otra fuente."""
    superado: dict[tuple[Fuente, Modalidad], bool] = {}
    for modalidad, mc in sorteo.modalidades.items():
        consolidada = mc.categorias.get("GANADORA")
        if consolidada is None:
            continue
        for fuente, datos in fuentes_datos:
            md = datos.modalidades.get(modalidad)
            cat = md.categorias.get("GANADORA") if md else None
            for campo in ("aciertos", "ganadores"):
                if cat and viola_rn_26(modalidad, "GANADORA", campo, getattr(cat, campo)):
                    con_valor = isinstance(getattr(consolidada, campo).dato, Valor)
                    clave = (fuente, modalidad)
                    superado[clave] = superado.get(clave, True) and con_valor
    return {clave for clave, si in superado.items() if si}


def _distintos(valores: list) -> bool:
    primero = valores[0]
    return any(v != primero for v in valores[1:])


def _misma_respuesta(a, b, es_importe: bool) -> bool:
    """[002] D-21, D-28: dos respuestas coinciden si son iguales o, si son importes, si difieren
    en menos de $ 1,00. Una omisión (``None``) solo coincide con otra omisión."""
    if a is None or b is None:
        return a is b
    return _coinciden_en_pesos(a, b) if es_importe else a == b


def _coinciden_en_pesos(a: Decimal, b: Decimal) -> bool:
    """[002] RN-30, D-28: unas fuentes redondean los centavos y otras los quitan, así que dos
    importes que difieren en menos de un peso son el mismo importe."""
    return abs(a - b) < _UN_PESO


def _sin_centavos(importe: Decimal) -> Decimal:
    """[002] RN-30, D-28: el importe sin centavos (se quitan, no se redondean)."""
    return importe.quantize(_UN_PESO, rounding=ROUND_DOWN)


def _dentro_de_tolerancia(valores: list[tuple[Fuente, Decimal]]) -> bool:
    """[002] RN-30: todos difieren del valor prioritario menos del 1 % de ese valor (sobre los
    importes sin centavos)."""
    referencia = valores[0][1]
    limite = abs(referencia) * TOLERANCIA_IMPORTES
    return all(abs(v - referencia) < limite for _, v in valores[1:])


def _estado_pozo(ganadores: DatoConsolidado) -> EstadoPozo:
    """[002] RN-19, I-06."""
    dato = ganadores.dato
    if isinstance(dato, Valor):
        return EstadoPozo.VACANTE if dato.v == 0 else EstadoPozo.CON_GANADORES
    if dato is SIN_DETERMINAR:
        return EstadoPozo.SIN_DETERMINAR
    return EstadoPozo.PENDIENTE


def _con_ganadores(categoria) -> bool | None:
    if categoria is None or not isinstance(categoria.ganadores, Valor):
        return None
    return categoria.ganadores.v > 0


def _consolidar_categoria(modalidad, codigo, fuentes_datos, fichas) -> CategoriaConsolidada:
    consolidados: dict[str, DatoConsolidado] = {}
    for campo in CAMPOS_CATEGORIA:
        candidatos = []
        for fuente, datos in fuentes_datos:
            md = datos.modalidades.get(modalidad)
            cat = md.categorias.get(codigo) if md else None
            ganadores_fuente = cat.ganadores if cat else NO_DISPONIBLE
            if campo in _CAMPOS_IMPORTE and (
                viola_rn_26(modalidad, codigo, "ganadores", ganadores_fuente)
                or _ganadores_en_conflicto(consolidados.get("ganadores"), ganadores_fuente)
            ):
                continue  # AC-4.9, D-29: sus importes tienen otro concepto (RN-17)
            dato = getattr(cat, campo) if cat else NO_DISPONIBLE
            # RN-28 / AC-4.2: hay omisión si la fuente presenta la tabla de premios de la
            # modalidad y le falta la categoría o el dato. Si no presenta la tabla, su intento es
            # "Incompleto" y lo que falta se completa con las demás fuentes (AC-2.5, AC-4.7).
            presenta_tabla = bool(md and md.categorias)
            publica = presenta_tabla and fichas[fuente].publica(
                campo, modalidad, _con_ganadores(cat)
            )
            # D-29: un dato que viola RN-26 se descarta como uno con formato inválido.
            invalido = viola_rn_26(modalidad, codigo, campo, dato)
            descartado = invalido or bool(cat and campo in _CAMPOS_IMPORTE and cat.texto_original)
            candidatos.append((fuente, NO_DISPONIBLE if invalido else dato, publica, descartado))
        consolidados[campo] = _comparar(candidatos)
    if consolidados["ganadores"].dato is SIN_DETERMINAR:
        # I-06: con ganadores en conflicto ningún importe se reclasifica.
        consolidados["pozo_destinado"] = DatoConsolidado(SIN_DETERMINAR)
        consolidados["importe_individual"] = DatoConsolidado(SIN_DETERMINAR)
    _calcular_importes(consolidados)
    return CategoriaConsolidada(
        aciertos=consolidados["aciertos"],
        ganadores=consolidados["ganadores"],
        pozo_destinado=consolidados["pozo_destinado"],
        importe_individual=consolidados["importe_individual"],
        estado_pozo=_estado_pozo(consolidados["ganadores"]),
    )


def _ganadores_en_conflicto(ganadores: DatoConsolidado | None, de_la_fuente: Dato) -> bool:
    """AC-4.9: la fuente informa una cantidad de ganadores distinta de la consolidada."""
    if ganadores is None or not isinstance(ganadores.dato, Valor):
        return False
    return isinstance(de_la_fuente, Valor) and de_la_fuente.v != ganadores.dato.v


def _calcular_importes(consolidados: dict[str, DatoConsolidado]) -> None:
    """[002] RN-18, D-16: importe individual 0,00 en una vacante y pozo = importe individual ×
    ganadores cuando ninguna fuente publica el pozo de una categoría con ganadores."""
    ganadores = consolidados["ganadores"].dato
    if not isinstance(ganadores, Valor):
        return
    if ganadores.v == 0:
        consolidados["importe_individual"] = DatoConsolidado(
            Valor(Decimal("0.00")), calculo=CALCULO_VACANTE
        )
        return
    pozo = consolidados["pozo_destinado"]
    if isinstance(pozo.dato, Valor) or pozo.discrepancia is not None:
        return  # pozo publicado por una fuente: no se calcula
    individual = consolidados["importe_individual"].dato
    if isinstance(individual, Valor):
        consolidados["pozo_destinado"] = DatoConsolidado(
            Valor(individual.v * ganadores.v), calculo=CALCULO_POZO
        )
    elif individual is SIN_DETERMINAR:
        consolidados["pozo_destinado"] = DatoConsolidado(SIN_DETERMINAR)


def _numeros_pozo_extra(modalidades: dict[Modalidad, ModalidadConsolidada]) -> DatoConsolidado:
    """[002] RN-12, D-19: unión de los números consolidados de Tradicional, La Segunda y
    Revancha; "No disponible" si falta alguno."""
    conjuntos = [modalidades[m].numeros.dato for m in MODALIDADES_PREMIO_EXTRA]
    if not all(isinstance(c, Valor) for c in conjuntos):
        return NO_DISPONIBLE_CONSOLIDADO
    return DatoConsolidado(
        Valor(frozenset().union(*(c.v for c in conjuntos))), calculo=CALCULO_POZO_EXTRA
    )


def _consolidar_modalidad(modalidad, fuentes_datos, fichas) -> ModalidadConsolidada:
    informada = any(modalidad in datos.modalidades for _, datos in fuentes_datos)
    if modalidad in MODALIDADES_PROPIAS:
        candidatos = []
        for fuente, datos in fuentes_datos:
            md = datos.modalidades.get(modalidad)
            dato = Valor(md.numeros) if md and md.numeros is not None else NO_DISPONIBLE
            # Números ausentes: el intento es "Incompleto" y se completan con las demás (AC-2.5).
            candidatos.append((fuente, dato, False, bool(md and md.numeros_descartados)))
        numeros = _comparar(candidatos) if informada else NO_DISPONIBLE_CONSOLIDADO
    else:
        numeros = NO_DISPONIBLE_CONSOLIDADO  # Pozo Extra: se calculan en ``consolidar`` (RN-12)
    if not informada:
        return ModalidadConsolidada(informada=False, numeros=numeros)
    codigos = set(categorias_esperadas(modalidad))
    for _, datos in fuentes_datos:
        md = datos.modalidades.get(modalidad)
        if md:
            codigos.update(md.categorias)
    categorias = {
        codigo: _consolidar_categoria(modalidad, codigo, fuentes_datos, fichas)
        for codigo in orden_categorias(modalidad, codigos)
    }
    return ModalidadConsolidada(informada=True, numeros=numeros, categorias=categorias)


def datos_consolidados(sorteo: SorteoConsolidado) -> Iterable[tuple[str, DatoConsolidado]]:
    """Todos los datos del consolidado con una clave estable (para I-03 y RN-32)."""
    yield "fecha", sorteo.fecha
    for modalidad, mc in sorteo.modalidades.items():
        yield f"{modalidad.value}.numeros", mc.numeros
        for codigo, cat in mc.categorias.items():
            for campo in CAMPOS_CATEGORIA:
                yield f"{modalidad.value}.{codigo}.{campo}", getattr(cat, campo)


def _combina_fuentes(sorteo: SorteoConsolidado, fuentes: Iterable[Fuente]) -> bool:
    """I-03: ninguna fuente por sí sola informa todos los datos presentes del consolidado. Los
    datos calculados no tienen fuente y no cuentan."""
    presentes = [
        d for _, d in datos_consolidados(sorteo) if isinstance(d.dato, Valor) and d.calculo is None
    ]
    if not presentes:
        return False
    return not any(all(f in d.fuentes for d in presentes) for f in fuentes)


def modalidades_no_informadas() -> dict[Modalidad, ModalidadConsolidada]:
    return {
        m: ModalidadConsolidada(informada=False, numeros=NO_DISPONIBLE_CONSOLIDADO)
        for m in ORDEN_MODALIDADES
    }


def consolidar(
    numero: int, intentos: Iterable[Intento], fichas: dict[Fuente, Ficha]
) -> SorteoConsolidado:
    """[002] contracts/dominio.md → ``consolidar``. El orden de los intentos no importa: la
    prioridad la fija ``ORDEN_FUENTES`` (RN-07)."""
    intentos = sorted(intentos, key=lambda i: prioridad(i[0]))
    resultados = {fuente: resultado for fuente, resultado, _ in intentos}
    fuentes_datos = [
        (fuente, datos)
        for fuente, resultado, datos in intentos
        if resultado.aporta_datos and datos is not None
    ]
    if not fuentes_datos:
        return SorteoConsolidado(
            numero=numero,
            fecha=NO_DISPONIBLE_CONSOLIDADO,
            modalidades=modalidades_no_informadas(),
            resultados=resultados,
        )
    fecha = _comparar([(f, Valor(d.fecha), True, False) for f, d in fuentes_datos])
    modalidades = {m: _consolidar_modalidad(m, fuentes_datos, fichas) for m in ORDEN_MODALIDADES}
    extra = modalidades[Modalidad.PREMIO_EXTRA]
    if extra.informada:
        numeros_extra = _numeros_pozo_extra(modalidades)  # RN-12, D-19
        modalidades[Modalidad.PREMIO_EXTRA] = replace(extra, numeros=numeros_extra)
    observaciones = tuple(o for _, d in fuentes_datos for o in d.observaciones)
    sorteo = SorteoConsolidado(
        numero=numero,
        fecha=fecha,
        modalidades=modalidades,
        resultados=resultados,
        observaciones=observaciones,
        reglas_no_verificadas=min(d.fecha for _, d in fuentes_datos) < FECHA_VIGENCIA_REGLAS,
    )
    # D-21: la observación de inconsistencia de una fuente que quedó en minoría en esa modalidad
    # queda superada por el desempate y pasa a ser informativa.
    perdedoras = perdedoras_por_mayoria(sorteo)
    # D-29: también la del dato inválido descartado cuando otra fuente aportó el valor válido.
    superadas = _invalidas_superadas(sorteo, fuentes_datos)
    observaciones = tuple(
        replace(o, es_inconsistencia=False, informativa=True)
        if o.es_inconsistencia
        and (
            (o.fuente, o.modalidad) in perdedoras
            or (o.codigo in _OBS_GANADORA_INVALIDA and (o.fuente, o.modalidad) in superadas)
        )
        else o
        for o in sorteo.observaciones
    )
    return replace(
        sorteo,
        observaciones=observaciones,
        combina_fuentes=_combina_fuentes(sorteo, [f for f, _ in fuentes_datos]),
        sin_corroborar=any(d.sin_corroborar for _, d in datos_consolidados(sorteo)),
    )


def revisar_correlatividad(sorteos: list[SorteoConsolidado]) -> list[SorteoConsolidado]:
    """[002] RN-23: un número mayor con una fecha anterior a la de uno menor agrega a ambos una
    observación de inconsistencia. Devuelve la lista en el mismo orden."""
    con_fecha = [s for s in sorteos if isinstance(s.fecha.dato, Valor)]
    agregar: dict[int, list[int]] = {}
    for menor in con_fecha:
        for mayor in con_fecha:
            if mayor.numero > menor.numero and mayor.fecha.dato.v < menor.fecha.dato.v:
                agregar.setdefault(menor.numero, []).append(mayor.numero)
                agregar.setdefault(mayor.numero, []).append(menor.numero)
    resultado = []
    for sorteo in sorteos:
        nuevas = [
            Observacion(
                codigo="obs.no_correlativo",
                texto=OBS_NO_CORRELATIVO.format(N=otro),
                es_inconsistencia=True,
            )
            for otro in sorted(set(agregar.get(sorteo.numero, ())))
        ]
        nuevas = [o for o in nuevas if o not in sorteo.observaciones]
        resultado.append(
            replace(sorteo, observaciones=sorteo.observaciones + tuple(nuevas))
            if nuevas
            else sorteo
        )
    return resultado
