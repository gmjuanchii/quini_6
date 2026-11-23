"""Vistas de administración de resultados (US2, US7). Todas exigen permiso de administrador
en cada GET y POST (FR-011, Const. IV)."""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from cuentas.decoradores import administrador_requerido
from dominio.mensajes import MENSAJES
from dominio.tipos import EstadoBloque, Modalidad, nombre_categoria
from quini6.formulario_pendiente import con_pendiente, reanudable
from quini6.idempotencia import con_idempotencia
from resultados import consultas, servicios
from resultados.forms import (
    ConcursoForm,
    CorreccionForm,
    MotivoForm,
    NumerosForm,
    PremiosForm,
    PublicarForm,
)
from resultados.models import Concurso

NUMEROS = consultas.NUMEROS
PREMIOS = consultas.PREMIOS
BASE = "/administracion/concursos"

TEXTO_ESTADO_ADMIN = {
    EstadoBloque.SIN_CARGAR: "Sin cargar",
    EstadoBloque.BORRADOR: "Borrador",
    EstadoBloque.OBSERVADO: "Observado",
    EstadoBloque.PUBLICADO: "Publicado",
    EstadoBloque.EN_REVISION: "En revisión",
}
CLASE_ESTADO = {
    EstadoBloque.SIN_CARGAR: "estado--pendiente",
    EstadoBloque.BORRADOR: "estado--pendiente",
    EstadoBloque.OBSERVADO: "estado--revision",
    EstadoBloque.PUBLICADO: "estado--con-premio",
    EstadoBloque.EN_REVISION: "estado--revision",
}
NOMBRE_BLOQUE = {NUMEROS: "Números", PREMIOS: "Premios"}


def _url_panel(numero: int) -> str:
    return f"{BASE}/{numero}/"


def _concurso(numero: int) -> Concurso:
    concurso = consultas.cargar_concurso(numero)
    if concurso is None:
        raise Http404
    return concurso


def _contexto_bloque(numero: int, modalidad: Modalidad, bloque: str):
    if bloque == NUMEROS and not modalidad.tiene_extraccion_propia:
        raise Http404  # RN-15: premio-extra/numeros no existe
    concurso = _concurso(numero)
    mc = consultas.modalidad_concurso(concurso, modalidad)
    if mc is None:
        raise Http404
    return concurso, mc


def _info_bloque(mc, bloque: str) -> dict:
    estado = consultas.estado_bloque(mc, bloque)
    trabajo = consultas.version_en_trabajo(mc, bloque)
    vigente = consultas.version_vigente(mc, bloque)
    return {
        "bloque": bloque,
        "nombre": NOMBRE_BLOQUE[bloque],
        "estado": estado,
        "texto_estado": TEXTO_ESTADO_ADMIN[estado],
        "clase_estado": CLASE_ESTADO[estado],
        "trabajo": trabajo,
        "vigente": vigente,
        "correccion_en_preparacion": vigente is not None and trabajo is not None,
        "en_revision": estado is EstadoBloque.EN_REVISION,
        "motivo_revision": getattr(mc, f"{bloque}_motivo_revision"),
        "url": f"{BASE}/{mc.concurso.numero}/{mc.modalidad_enum.slug}/{bloque}",
    }


def _filas(concurso: Concurso) -> list[dict]:
    filas = []
    for mc in consultas._modalidades(concurso):
        bloques = []
        if mc.modalidad_enum.tiene_extraccion_propia:
            bloques.append(_info_bloque(mc, NUMEROS))
        bloques.append(_info_bloque(mc, PREMIOS))
        filas.append({"modalidad": mc.modalidad_enum, "mc": mc, "bloques": bloques})
    return filas


@administrador_requerido
def listado(request):
    concursos = consultas.con_versiones(Concurso.objects.order_by("-fecha_sorteo", "-numero"))
    datos = [
        {
            "concurso": c,
            "completitud": consultas.TEXTO_COMPLETITUD[consultas.completitud(c)],
            "filas": _filas(c),
        }
        for c in concursos
    ]
    return render(request, "resultados/admin/listado.html", {"concursos": datos})


@administrador_requerido
@reanudable("sorteo.crear")
@require_http_methods(["GET", "POST"])
@con_idempotencia("sorteo.crear")  # [003] FR-031
def nuevo(request):
    inicial = con_pendiente(request, {}, ConcursoForm)  # [003] FR-032
    form = ConcursoForm(request.POST or None, initial=inicial)
    duplicado = None
    if request.method == "POST" and form.is_valid():
        try:
            concurso = servicios.crear_concurso(
                request.user,
                form.cleaned_data["numero"],
                form.cleaned_data["fecha_sorteo"],
                form.cleaned_data["modalidades"],
            )
        except servicios.ConcursoDuplicado as error:
            duplicado = error.numero
        except servicios.ErrorResultados as error:
            for mensaje in error.mensajes:
                form.add_error("modalidades", mensaje)
        else:
            messages.success(request, f"Se creó el sorteo N.º {concurso.numero}.")
            return redirect(_url_panel(concurso.numero))
    return render(
        request,
        "resultados/admin/concurso_form.html",
        {"form": form, "duplicado": duplicado, "modificar": False},
    )


@administrador_requerido
@reanudable("sorteo.modificar")
@require_http_methods(["GET", "POST"])
def modificar(request, numero: int):
    concurso = _concurso(numero)
    inicial = {
        "fecha_sorteo": concurso.fecha_sorteo,
        "modalidades": [mc.modalidad for mc in concurso.modalidades.all()],
    }
    inicial = con_pendiente(request, inicial, ConcursoForm)  # [003] FR-032
    form = ConcursoForm(request.POST or None, initial=inicial, modificar=True)
    if request.method == "POST" and form.is_valid():
        try:
            servicios.modificar_concurso(
                request.user,
                concurso,
                form.cleaned_data["fecha_sorteo"],
                form.cleaned_data["modalidades"],
            )
        except servicios.ErrorResultados as error:
            for mensaje in error.mensajes:
                form.add_error(None, mensaje)
        else:
            messages.success(request, "Se guardaron los cambios del sorteo.")
            return redirect(_url_panel(numero))
    return render(
        request,
        "resultados/admin/concurso_form.html",
        {"form": form, "modificar": True, "concurso": concurso},
    )


@administrador_requerido
def panel(request, numero: int):
    concurso = _concurso(numero)
    return render(
        request,
        "resultados/admin/panel.html",
        {
            "concurso": concurso,
            "completitud": consultas.TEXTO_COMPLETITUD[consultas.completitud(concurso)],
            "filas": _filas(concurso),
            "admite_jugadas": consultas.admite_jugadas(concurso),
        },
    )


def _redirigir_publicado(request, numero):
    messages.error(request, MENSAJES["admin.bloque_publicado"])
    return redirect(_url_panel(numero))


def _fuente_inicial(version) -> dict:
    if version is None:
        return {}
    return {
        "fuente_descripcion": version.fuente_descripcion,
        "fuente_fecha_consulta": version.fuente_fecha_consulta,
        "motivo_correccion": version.motivo_correccion,
    }


@administrador_requerido
@reanudable("sorteo.numeros")
@require_http_methods(["GET", "POST"])
def numeros(request, numero: int, modalidad: Modalidad):
    concurso, mc = _contexto_bloque(numero, modalidad, NUMEROS)
    trabajo = consultas.version_en_trabajo(mc, NUMEROS)
    if trabajo is None and consultas.version_vigente(mc, NUMEROS) is not None:
        return _redirigir_publicado(request, numero)
    inicial = _fuente_inicial(trabajo)
    if trabajo is not None:
        for i, n in enumerate(sorted(trabajo.numeros), start=1):
            inicial[f"n{i}"] = f"{n:02d}"
    es_correccion = bool(trabajo and trabajo.es_correccion)
    inicial = con_pendiente(request, inicial, NumerosForm)  # [003] FR-032
    form = NumerosForm(request.POST or None, initial=inicial, es_correccion=es_correccion)
    if request.method == "POST" and form.is_valid():
        try:
            servicios.guardar_borrador_numeros(
                request.user,
                mc,
                form.cleaned_data["numeros"],
                form.cleaned_data.get("fuente_descripcion") or "",
                form.cleaned_data.get("fuente_fecha_consulta"),
                form.cleaned_data.get("motivo_correccion") or "",
            )
        except servicios.ErrorResultados as error:
            for mensaje in error.mensajes:
                form.add_error(None, mensaje)
        else:
            messages.success(request, f"Se guardó el borrador de números de {modalidad.nombre}.")
            return redirect(_url_panel(numero))
    return render(
        request,
        "resultados/admin/numeros.html",
        {
            "form": form,
            "concurso": concurso,
            "modalidad": modalidad,
            "trabajo": trabajo,
            "es_correccion": es_correccion,
        },
    )


@administrador_requerido
@reanudable("sorteo.premios")
@require_http_methods(["GET", "POST"])
def premios(request, numero: int, modalidad: Modalidad):
    concurso, mc = _contexto_bloque(numero, modalidad, PREMIOS)
    trabajo = consultas.version_en_trabajo(mc, PREMIOS)
    if trabajo is None and consultas.version_vigente(mc, PREMIOS) is not None:
        return _redirigir_publicado(request, numero)
    inicial = _fuente_inicial(trabajo)
    if trabajo is not None:
        if trabajo.sin_ganadores:
            inicial["aciertos_categoria_ganadora"] = "SIN"
        elif trabajo.aciertos_categoria_ganadora is not None:
            inicial["aciertos_categoria_ganadora"] = str(trabajo.aciertos_categoria_ganadora)
        for cat in trabajo.categorias.all():
            for campo in servicios.CAMPOS_PREMIO:
                valor = getattr(cat, campo)
                if valor is None:
                    continue
                if campo == "ganadores":
                    inicial[f"{cat.categoria}_{campo}"] = str(valor)
                else:
                    inicial[f"{cat.categoria}_{campo}"] = f"{valor:.2f}".replace(".", ",")
    es_correccion = bool(trabajo and trabajo.es_correccion)
    inicial = con_pendiente(request, inicial, PremiosForm)  # [003] FR-032
    form = PremiosForm(
        request.POST or None, initial=inicial, modalidad=modalidad, es_correccion=es_correccion
    )
    if request.method == "POST" and form.is_valid():
        try:
            servicios.guardar_borrador_premios(
                request.user,
                mc,
                form.cleaned_data["datos_por_categoria"],
                form.cleaned_data["aciertos"],
                form.cleaned_data["sin_ganadores"],
                form.cleaned_data.get("fuente_descripcion") or "",
                form.cleaned_data.get("fuente_fecha_consulta"),
                form.cleaned_data.get("motivo_correccion") or "",
            )
        except servicios.ErrorResultados as error:
            for mensaje in error.mensajes:
                form.add_error(None, mensaje)
        else:
            messages.success(request, f"Se guardó el borrador de premios de {modalidad.nombre}.")
            return redirect(_url_panel(numero))
    return render(
        request,
        "resultados/admin/premios.html",
        {
            "form": form,
            "concurso": concurso,
            "modalidad": modalidad,
            "trabajo": trabajo,
            "es_correccion": es_correccion,
        },
    )


def _trabajo_o_error(request, mc, bloque):
    trabajo = consultas.version_en_trabajo(mc, bloque)
    if trabajo is None:
        messages.error(request, "No hay información en Borrador u Observado en este bloque.")
    return trabajo


@administrador_requerido
@require_POST
def observar(request, numero: int, modalidad: Modalidad, bloque: str):
    _, mc = _contexto_bloque(numero, modalidad, bloque)
    trabajo = _trabajo_o_error(request, mc, bloque)
    if trabajo is not None:
        form = MotivoForm(request.POST)
        try:
            if not form.is_valid():
                raise servicios.ErrorResultados("Falta el motivo de la observación.")
            servicios.observar(request.user, trabajo, form.cleaned_data["motivo"])
        except servicios.ErrorResultados as error:
            for mensaje in error.mensajes:
                messages.error(request, mensaje)
        else:
            messages.success(request, "La información quedó Observada.")
    return redirect(_url_panel(numero))


@administrador_requerido
@require_POST
def resolver(request, numero: int, modalidad: Modalidad, bloque: str):
    _, mc = _contexto_bloque(numero, modalidad, bloque)
    trabajo = _trabajo_o_error(request, mc, bloque)
    if trabajo is not None:
        try:
            servicios.resolver_observacion(request.user, trabajo)
        except servicios.ErrorResultados as error:
            for mensaje in error.mensajes:
                messages.error(request, mensaje)
        else:
            messages.success(
                request, "Se resolvió la observación: la información volvió a Borrador."
            )
    return redirect(_url_panel(numero))


@administrador_requerido
@require_http_methods(["GET", "POST"])
def publicar(request, numero: int, modalidad: Modalidad, bloque: str):
    concurso, mc = _contexto_bloque(numero, modalidad, bloque)
    trabajo = _trabajo_o_error(request, mc, bloque)
    if trabajo is None:
        return redirect(_url_panel(numero))
    form = PublicarForm(request.POST or None)
    errores = []
    if request.method == "POST" and form.is_valid():
        try:
            servicios.publicar(
                request.user,
                trabajo,
                advertencias_confirmadas=form.cleaned_data["confirmar_advertencias"],
                cotejo_confirmado=form.cleaned_data["cotejo"],
            )
        except servicios.ErrorResultados as error:
            errores = error.mensajes
        else:
            texto = "Se publicó la corrección" if trabajo.es_correccion else "Se publicó"
            messages.success(
                request, f"{texto}: {NOMBRE_BLOQUE[bloque].lower()} de {modalidad.nombre}."
            )
            return redirect(_url_panel(numero))
    bloqueantes, advertencias = servicios.revisar_para_publicar(trabajo)
    contexto = {
        "form": form,
        "concurso": concurso,
        "modalidad": modalidad,
        "bloque": bloque,
        "nombre_bloque": NOMBRE_BLOQUE[bloque],
        "trabajo": trabajo,
        "bloqueantes": bloqueantes,
        "advertencias": advertencias,
        "errores": errores,
    }
    if bloque == PREMIOS:
        contexto["categorias"] = [
            {
                "nombre": nombre_categoria(
                    modalidad, c.categoria, trabajo.aciertos_categoria_ganadora
                ),
                "datos": c,
            }
            for c in sorted(
                trabajo.categorias.all(), key=lambda c: modalidad.categorias.index(c.categoria)
            )
        ]
    return render(request, "resultados/admin/publicar.html", contexto)


# --- US7: revisión, corrección e historial ---------------------------------------------


def _con_motivo(request, accion, *args):
    form = MotivoForm(request.POST)
    try:
        if not form.is_valid():
            raise servicios.ErrorResultados("Falta el motivo.")
        accion(request.user, *args, form.cleaned_data["motivo"])
    except servicios.ErrorResultados as error:
        for mensaje in error.mensajes:
            messages.error(request, mensaje)
        return False
    return True


@administrador_requerido
@require_POST
def revision(request, numero: int, modalidad: Modalidad, bloque: str):
    _, mc = _contexto_bloque(numero, modalidad, bloque)
    if _con_motivo(request, servicios.marcar_revision, mc, bloque):
        messages.success(request, "El bloque quedó En revisión.")
    return redirect(_url_panel(numero))


@administrador_requerido
@require_POST
def quitar_revision(request, numero: int, modalidad: Modalidad, bloque: str):
    _, mc = _contexto_bloque(numero, modalidad, bloque)
    if _con_motivo(request, servicios.quitar_revision, mc, bloque):
        messages.success(request, "Se quitó la marca de revisión.")
    return redirect(_url_panel(numero))


@administrador_requerido
@require_POST
def corregir(request, numero: int, modalidad: Modalidad, bloque: str):
    _, mc = _contexto_bloque(numero, modalidad, bloque)
    form = CorreccionForm(request.POST)
    try:
        if not form.is_valid():
            mensajes = [e for errores in form.errors.values() for e in errores]
            raise servicios.ErrorResultados(mensajes)
        servicios.iniciar_correccion(
            request.user,
            mc,
            bloque,
            form.cleaned_data["motivo"],
            form.cleaned_data["fuente_descripcion"],
            form.cleaned_data["fuente_fecha_consulta"],
        )
    except servicios.ErrorResultados as error:
        for mensaje in error.mensajes:
            messages.error(request, mensaje)
        return redirect(_url_panel(numero))
    messages.success(
        request, "Se inició la corrección. El público sigue viendo los valores publicados."
    )
    return redirect(f"{BASE}/{numero}/{modalidad.slug}/{bloque}/")


@administrador_requerido
def historial(request, numero: int):
    concurso = _concurso(numero)
    return render(
        request,
        "resultados/admin/historial.html",
        {"concurso": concurso, "cambios": consultas.historial_cambios(concurso)},
    )
