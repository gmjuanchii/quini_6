"""Administración de sorteos en la API v1 ([003] contracts/api.md § "Administración de sorteos",
pantalla 6, T207).

Una operación por cada vista de ``resultados/urls_admin.py``, todas de nivel A, con los mismos
formularios (``resultados/forms.py``), servicios (``resultados/servicios.py``) y avisos que las
vistas HTML (FR-043). Los formularios se describen campo por campo desde el propio formulario de
Django (``FormularioDTO``): la pantalla de Next.js muestra los mismos rótulos, opciones y valores, y
la validación la repite siempre Django (NFR-009).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.contrib import messages
from django.http import QueryDict
from ninja import Router, Schema, Status

from dominio.tipos import EstadoBloque, Modalidad, nombre_categoria
from quini6 import idempotencia
from quini6.api_base import FechaHora, ProblemaAPI, nivel
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
from resultados.templatetags.cambios import valor_cambio
from resultados.views_admin import (
    CLASE_ESTADO,
    NOMBRE_BLOQUE,
    TEXTO_ESTADO_ADMIN,
    _fuente_inicial,
)

router = Router(tags=["Administración de sorteos"])

NUMEROS, PREMIOS = consultas.NUMEROS, consultas.PREMIOS
BASE_HTML = "/administracion/concursos"


# -- DTO ----------------------------------------------------------------------------------------


class Opcion(Schema):
    valor: str
    texto: str


class CampoFormulario(Schema):
    nombre: str
    etiqueta: str
    tipo: str  # text | date | textarea | select | checkbox | checkbox-multiple
    valor: str | list[str] | bool | None
    opciones: list[Opcion] = []
    ayuda: str | None = None
    requerido: bool = False
    errores: list[str] = []


class FilaPremios(Schema):
    codigo: str
    nombre: str
    campos: list[str]


class FormularioDTO(Schema):
    campos: list[CampoFormulario]
    filas: list[FilaPremios] = []
    errores: list[str] = []


class EstadoAdmin(Schema):
    codigo: str
    texto: str
    clase: str


class VersionVigente(Schema):
    publicada_en: FechaHora | None
    fuente_descripcion: str
    numeros: list[int]


class VersionTrabajo(Schema):
    estado: str
    es_correccion: bool
    actualizada_en: FechaHora | None
    numeros: list[int]
    motivo_observacion: str


class BloqueAdmin(Schema):
    bloque: str
    nombre: str
    estado: EstadoAdmin
    en_revision: bool
    motivo_revision: str
    correccion_en_preparacion: bool
    vigente: VersionVigente | None
    trabajo: VersionTrabajo | None
    acciones: list[str]


class ModalidadAdmin(Schema):
    slug: str
    nombre: str
    tiene_extraccion_propia: bool


class FilaAdmin(Schema):
    modalidad: ModalidadAdmin
    bloques: list[BloqueAdmin]


class Completitud(Schema):
    codigo: str
    texto: str


class SorteoAdmin(Schema):
    numero: int
    fecha: date
    completitud: Completitud
    filas: list[FilaAdmin]


class PanelSorteo(SorteoAdmin):
    admite_jugadas: bool
    tiene_publicaciones: bool


class FormularioSorteo(Schema):
    numero: int | None
    formulario: FormularioDTO


class FormularioBloque(Schema):
    numero: int
    modalidad: ModalidadAdmin
    bloque: str
    es_correccion: bool
    formulario: FormularioDTO


class CategoriaRevision(Schema):
    nombre: str
    ganadores: int | None
    importe_categoria: str | None
    importe_individual: str | None
    pozo_vacante_acumulado: str | None


class RevisionPublicacion(Schema):
    numero: int
    modalidad: ModalidadAdmin
    bloque: str
    es_correccion: bool
    numeros: list[int]
    categorias: list[CategoriaRevision]
    sin_ganadores: bool
    aciertos_categoria_ganadora: int | None
    fuente_descripcion: str
    fuente_fecha_consulta: date | None
    motivo_correccion: str
    bloqueantes: list[str]
    advertencias: list[str]
    formulario: FormularioDTO


class CambioRegistrado(Schema):
    momento: FechaHora
    accion: str
    modalidad_y_bloque: str
    valor_anterior: str
    valor_nuevo: str
    autor: str
    motivo: str
    fuente: str


class DatosFormulario(Schema):
    """Lo enviado, con los nombres de los campos del formulario de Django."""

    campos: dict[str, str | list[str] | bool | None] = {}


# -- Formularios --------------------------------------------------------------------------------


def _tipo(campo: forms.Field) -> str:
    widget = campo.widget
    if isinstance(widget, forms.CheckboxSelectMultiple):
        return "checkbox-multiple"
    if isinstance(widget, forms.CheckboxInput):
        return "checkbox"
    if isinstance(widget, forms.Textarea):
        return "textarea"
    if isinstance(widget, forms.Select):
        return "select"
    if getattr(widget, "input_type", "") == "date" or isinstance(campo, forms.DateField):
        return "date"
    return "text"


def _valor(enlazado) -> Any:
    valor = enlazado.value()
    if isinstance(valor, date):
        return valor.isoformat()
    if isinstance(valor, list | tuple):
        return [str(v.value if hasattr(v, "value") else v) for v in valor]
    if isinstance(valor, bool):
        return valor
    return None if valor is None else str(valor)


def formulario_dto(form: forms.Form) -> dict:
    campos = []
    for enlazado in form:
        campo = enlazado.field
        opciones = [
            {"valor": str(v), "texto": str(t)} for v, t in getattr(campo, "choices", []) or []
        ]
        campos.append(
            {
                "nombre": enlazado.name,
                "etiqueta": str(enlazado.label),
                "tipo": _tipo(campo),
                "valor": _valor(enlazado),
                "opciones": opciones,
                "ayuda": str(campo.help_text) or None,
                "requerido": campo.required,
                "errores": [str(e) for e in enlazado.errors],
            }
        )
    filas = []
    if isinstance(form, PremiosForm):
        filas = [
            {"codigo": f["codigo"], "nombre": f["nombre"], "campos": [c.name for c in f["campos"]]}
            for f in form.filas_vista()
        ]
    return {
        "campos": campos,
        "filas": filas,
        "errores": [str(e) for e in form.non_field_errors()],
    }


def _datos(cuerpo: DatosFormulario) -> QueryDict:
    datos = QueryDict(mutable=True)
    for nombre, valor in cuerpo.campos.items():
        if isinstance(valor, list):
            datos.setlist(nombre, [str(v) for v in valor])
        elif isinstance(valor, bool):
            if valor:
                datos[nombre] = "on"
        elif valor is not None:
            datos[nombre] = str(valor)
    return datos


def _invalido(form: forms.Form, generales: list[str] | None = None, **extra) -> ProblemaAPI:
    errores = [
        {
            "campo": "" if campo == "__all__" else campo,
            "codigo": "api.dato_invalido",
            "mensaje": str(t),
        }
        for campo, lista in form.errors.items()
        for t in lista
    ]
    errores += [{"campo": "", "codigo": "api.dato_invalido", "mensaje": t} for t in generales or []]
    return ProblemaAPI(
        422,
        "api.detalle_validacion",
        tipo="validacion",
        errores=errores,
        formulario=formulario_dto(form),
        **extra,
    )


def _error_general(mensajes: list[str]) -> ProblemaAPI:
    return ProblemaAPI(
        422,
        "api.detalle_validacion",
        tipo="validacion",
        errores=[{"campo": "", "codigo": "api.dato_invalido", "mensaje": m} for m in mensajes],
    )


# -- Conversión ---------------------------------------------------------------------------------


def _modalidad(m: Modalidad) -> dict:
    return {
        "slug": m.slug,
        "nombre": m.nombre,
        "tiene_extraccion_propia": m.tiene_extraccion_propia,
    }


def _acciones(estado: EstadoBloque, trabajo, vigente) -> list[str]:
    """Las mismas acciones que ofrece `templates/resultados/admin/panel.html`."""
    acciones = []
    if trabajo is not None:
        acciones.append("editar")
    elif vigente is None:
        acciones.append("cargar")
    if trabajo is not None and trabajo.estado == "BORRADOR":
        acciones += ["publicar", "observar"]
    if trabajo is not None and trabajo.estado == "OBSERVADO":
        acciones.append("resolver")
    if vigente is not None and estado is not EstadoBloque.EN_REVISION:
        acciones.append("revision")
    if estado is EstadoBloque.EN_REVISION:
        acciones.append("quitar_revision")
    if vigente is not None and trabajo is None:
        acciones.append("corregir")
    return acciones


def _numeros_de(version) -> list[int]:
    return sorted(version.numeros) if version is not None and hasattr(version, "numeros") else []


def _bloque(mc, bloque: str) -> dict:
    estado = consultas.estado_bloque(mc, bloque)
    trabajo = consultas.version_en_trabajo(mc, bloque)
    vigente = consultas.version_vigente(mc, bloque)
    return {
        "bloque": bloque,
        "nombre": NOMBRE_BLOQUE[bloque],
        "estado": {
            "codigo": estado.value,
            "texto": TEXTO_ESTADO_ADMIN[estado],
            "clase": CLASE_ESTADO[estado],
        },
        "en_revision": estado is EstadoBloque.EN_REVISION,
        "motivo_revision": getattr(mc, f"{bloque}_motivo_revision") or "",
        "correccion_en_preparacion": vigente is not None and trabajo is not None,
        "vigente": None
        if vigente is None
        else {
            "publicada_en": vigente.publicada_en,
            "fuente_descripcion": vigente.fuente_descripcion or "",
            "numeros": _numeros_de(vigente),
        },
        "trabajo": None
        if trabajo is None
        else {
            "estado": trabajo.estado,
            "es_correccion": bool(trabajo.es_correccion),
            "actualizada_en": trabajo.actualizada_en,
            "numeros": _numeros_de(trabajo),
            "motivo_observacion": trabajo.motivo_observacion or "",
        },
        "acciones": _acciones(estado, trabajo, vigente),
    }


def _filas(concurso: Concurso) -> list[dict]:
    filas = []
    for mc in consultas._modalidades(concurso):
        m = mc.modalidad_enum
        bloques = ([_bloque(mc, NUMEROS)] if m.tiene_extraccion_propia else []) + [
            _bloque(mc, PREMIOS)
        ]
        filas.append({"modalidad": _modalidad(m), "bloques": bloques})
    return filas


def sorteo_dto(concurso: Concurso) -> dict:
    codigo = consultas.completitud(concurso)
    return {
        "numero": concurso.numero,
        "fecha": concurso.fecha_sorteo,
        "completitud": {"codigo": codigo, "texto": consultas.TEXTO_COMPLETITUD[codigo]},
        "filas": _filas(concurso),
    }


def panel_dto(concurso: Concurso) -> dict:
    return {
        **sorteo_dto(concurso),
        "admite_jugadas": consultas.admite_jugadas(concurso),
        "tiene_publicaciones": consultas.tiene_publicaciones(concurso),
    }


# -- Búsqueda de lo pedido (404 como las vistas HTML) ----------------------------------------------


def _concurso(numero: int) -> Concurso:
    concurso = consultas.cargar_concurso(numero)
    if concurso is None:
        raise ProblemaAPI(404, "api.detalle_no_encontrado", tipo="no-encontrado")
    return concurso


def _contexto(numero: int, slug: str, bloque: str):
    try:
        modalidad = Modalidad.desde_slug(slug)
    except (KeyError, ValueError):
        raise ProblemaAPI(404, "api.detalle_no_encontrado", tipo="no-encontrado") from None
    if bloque not in (NUMEROS, PREMIOS) or (
        bloque == NUMEROS and not modalidad.tiene_extraccion_propia
    ):
        raise ProblemaAPI(404, "api.detalle_no_encontrado", tipo="no-encontrado")
    concurso = _concurso(numero)
    mc = consultas.modalidad_concurso(concurso, modalidad)
    if mc is None:
        raise ProblemaAPI(404, "api.detalle_no_encontrado", tipo="no-encontrado")
    return concurso, modalidad, mc


def _panel(request, numero: int) -> dict:
    return panel_dto(_concurso(numero))


# -- Operaciones: sorteos ---------------------------------------------------------------------


@router.get("/admin/sorteos/", response=list[SorteoAdmin])
@nivel("A")
def listar(request):
    concursos = consultas.con_versiones(Concurso.objects.order_by("-fecha_sorteo", "-numero"))
    return [sorteo_dto(c) for c in concursos]


@router.get("/admin/sorteos/nuevo/", response=FormularioSorteo)
@nivel("A")
def formulario_nuevo(request):
    return {"numero": None, "formulario": formulario_dto(ConcursoForm())}


@router.post("/admin/sorteos/", response={201: PanelSorteo})
@nivel("A", ruta_pendiente=f"{BASE_HTML}/nuevo/")
def crear(request, datos: DatosFormulario):
    """[001] AC-2.1, AC-2.2. ⟳ ``Idempotency-Key``."""
    clave, anterior = idempotencia.anterior_api(request, "sorteo.crear")
    if anterior is not None:
        return Status(201, panel_dto(_concurso(int(anterior["resultado"]))))
    form = ConcursoForm(_datos(datos))
    if not form.is_valid():
        raise _invalido(form)
    try:
        concurso = servicios.crear_concurso(
            request.user,
            form.cleaned_data["numero"],
            form.cleaned_data["fecha_sorteo"],
            form.cleaned_data["modalidades"],
        )
    except servicios.ConcursoDuplicado as error:
        raise ProblemaAPI(
            422,
            "admin.concurso_duplicado",
            tipo="validacion",
            valores={"N": error.numero},
            existente={"id": error.numero, "url": f"{BASE_HTML}/{error.numero}/"},
        ) from None
    except servicios.ErrorResultados as error:
        for m in error.mensajes:
            form.add_error("modalidades", m)
        raise _invalido(form) from None
    messages.success(request, f"Se creó el sorteo N.º {concurso.numero}.")
    if clave is not None:
        idempotencia.registrar(request, clave, "sorteo.crear", str(concurso.numero))
    return Status(201, panel_dto(_concurso(concurso.numero)))


@router.get("/admin/sorteos/{numero}/", response=PanelSorteo)
@nivel("A")
def panel(request, numero: int):
    return _panel(request, numero)


@router.get("/admin/sorteos/{numero}/modificar/", response=FormularioSorteo)
@nivel("A")
def formulario_modificar(request, numero: int):
    concurso = _concurso(numero)
    inicial = {
        "fecha_sorteo": concurso.fecha_sorteo,
        "modalidades": [mc.modalidad for mc in concurso.modalidades.all()],
    }
    form = ConcursoForm(initial=inicial, modificar=True)
    return {"numero": numero, "formulario": formulario_dto(form)}


@router.put("/admin/sorteos/{numero}/", response=PanelSorteo)
@nivel("A", ruta_pendiente=f"{BASE_HTML}/{{numero}}/modificar/")
def modificar(request, numero: int, datos: DatosFormulario):
    """[001] AC-2.3, RN-14."""
    concurso = _concurso(numero)
    form = ConcursoForm(_datos(datos), modificar=True)
    if not form.is_valid():
        raise _invalido(form)
    try:
        servicios.modificar_concurso(
            request.user,
            concurso,
            form.cleaned_data["fecha_sorteo"],
            form.cleaned_data["modalidades"],
        )
    except servicios.ErrorResultados as error:
        raise _invalido(form, error.mensajes) from None
    messages.success(request, "Se guardaron los cambios del sorteo.")
    return _panel(request, numero)


@router.get("/admin/sorteos/{numero}/historial/", response=list[CambioRegistrado])
@nivel("A")
def historial(request, numero: int):
    """[001] US7, AC-7.x: del más reciente al más antiguo."""
    return [
        {
            "momento": c.fecha_hora,
            "accion": c.get_accion_display(),
            "modalidad_y_bloque": (f"{c.get_modalidad_display()} · " if c.modalidad else "")
            + str(c.get_bloque_display()),
            "valor_anterior": valor_cambio(c.valor_anterior),
            "valor_nuevo": valor_cambio(c.valor_nuevo),
            "autor": c.autor.email,
            "motivo": c.motivo or "—",
            "fuente": c.fuente or "—",
        }
        for c in consultas.historial_cambios(_concurso(numero))
    ]


# -- Operaciones: números y premios --------------------------------------------------------------


def _bloque_editable(mc, bloque: str):
    trabajo = consultas.version_en_trabajo(mc, bloque)
    if trabajo is None and consultas.version_vigente(mc, bloque) is not None:
        raise ProblemaAPI(409, "admin.bloque_publicado", tipo="conflicto")
    return trabajo


def _form_numeros(trabajo, datos=None) -> NumerosForm:
    inicial = _fuente_inicial(trabajo)
    if trabajo is not None:
        for i, n in enumerate(sorted(trabajo.numeros), start=1):
            inicial[f"n{i}"] = f"{n:02d}"
    es_correccion = bool(trabajo and trabajo.es_correccion)
    return NumerosForm(datos, initial=inicial, es_correccion=es_correccion)


def _form_premios(trabajo, modalidad, datos=None) -> PremiosForm:
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
                texto = str(valor) if campo == "ganadores" else f"{valor:.2f}".replace(".", ",")
                inicial[f"{cat.categoria}_{campo}"] = texto
    es_correccion = bool(trabajo and trabajo.es_correccion)
    return PremiosForm(datos, initial=inicial, modalidad=modalidad, es_correccion=es_correccion)


def _formulario_bloque(numero, modalidad, bloque, trabajo, form) -> dict:
    return {
        "numero": numero,
        "modalidad": _modalidad(modalidad),
        "bloque": bloque,
        "es_correccion": bool(trabajo and trabajo.es_correccion),
        "formulario": formulario_dto(form),
    }


@router.get("/admin/sorteos/{numero}/{modalidad}/numeros/", response=FormularioBloque)
@nivel("A")
def formulario_numeros(request, numero: int, modalidad: str):
    _, m, mc = _contexto(numero, modalidad, NUMEROS)
    trabajo = _bloque_editable(mc, NUMEROS)
    return _formulario_bloque(numero, m, NUMEROS, trabajo, _form_numeros(trabajo))


@router.put("/admin/sorteos/{numero}/{modalidad}/numeros/", response=PanelSorteo)
@nivel("A", ruta_pendiente=f"{BASE_HTML}/{{numero}}/{{modalidad}}/numeros/")
def guardar_numeros(request, numero: int, modalidad: str, datos: DatosFormulario):
    """[001] AC-2.4 a AC-2.6."""
    _, m, mc = _contexto(numero, modalidad, NUMEROS)
    trabajo = _bloque_editable(mc, NUMEROS)
    form = _form_numeros(trabajo, _datos(datos))
    if not form.is_valid():
        raise _invalido(form)
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
        raise _invalido(form, error.mensajes) from None
    messages.success(request, f"Se guardó el borrador de números de {m.nombre}.")
    return _panel(request, numero)


@router.get("/admin/sorteos/{numero}/{modalidad}/premios/", response=FormularioBloque)
@nivel("A")
def formulario_premios(request, numero: int, modalidad: str):
    _, m, mc = _contexto(numero, modalidad, PREMIOS)
    trabajo = _bloque_editable(mc, PREMIOS)
    return _formulario_bloque(numero, m, PREMIOS, trabajo, _form_premios(trabajo, m))


@router.put("/admin/sorteos/{numero}/{modalidad}/premios/", response=PanelSorteo)
@nivel("A", ruta_pendiente=f"{BASE_HTML}/{{numero}}/{{modalidad}}/premios/")
def guardar_premios(request, numero: int, modalidad: str, datos: DatosFormulario):
    """[001] AC-2.7 a AC-2.9."""
    _, m, mc = _contexto(numero, modalidad, PREMIOS)
    trabajo = _bloque_editable(mc, PREMIOS)
    form = _form_premios(trabajo, m, _datos(datos))
    if not form.is_valid():
        raise _invalido(form)
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
        raise _invalido(form, error.mensajes) from None
    messages.success(request, f"Se guardó el borrador de premios de {m.nombre}.")
    return _panel(request, numero)


# -- Operaciones: ciclo de publicación -----------------------------------------------------------


def _trabajo(mc, bloque: str):
    trabajo = consultas.version_en_trabajo(mc, bloque)
    if trabajo is None:
        raise _error_general(["No hay información en Borrador u Observado en este bloque."])
    return trabajo


def _motivo(datos: DatosFormulario, falta: str) -> str:
    form = MotivoForm(_datos(datos))
    if not form.is_valid():
        raise _error_general([falta])
    return form.cleaned_data["motivo"]


@router.post("/admin/sorteos/{numero}/{modalidad}/{bloque}/observar/", response=PanelSorteo)
@nivel("A")
def observar(request, numero: int, modalidad: str, bloque: str, datos: DatosFormulario):
    _, _, mc = _contexto(numero, modalidad, bloque)
    trabajo = _trabajo(mc, bloque)
    motivo = _motivo(datos, "Falta el motivo de la observación.")
    try:
        servicios.observar(request.user, trabajo, motivo)
    except servicios.ErrorResultados as error:
        raise _error_general(error.mensajes) from None
    messages.success(request, "La información quedó Observada.")
    return _panel(request, numero)


@router.post("/admin/sorteos/{numero}/{modalidad}/{bloque}/resolver/", response=PanelSorteo)
@nivel("A")
def resolver(request, numero: int, modalidad: str, bloque: str):
    _, _, mc = _contexto(numero, modalidad, bloque)
    trabajo = _trabajo(mc, bloque)
    try:
        servicios.resolver_observacion(request.user, trabajo)
    except servicios.ErrorResultados as error:
        raise _error_general(error.mensajes) from None
    messages.success(request, "Se resolvió la observación: la información volvió a Borrador.")
    return _panel(request, numero)


def _revision(numero, m, bloque, trabajo, form) -> dict:
    bloqueantes, advertencias = servicios.revisar_para_publicar(trabajo)
    categorias = []
    if bloque == PREMIOS:
        for c in sorted(trabajo.categorias.all(), key=lambda c: m.categorias.index(c.categoria)):
            categorias.append(
                {
                    "nombre": nombre_categoria(m, c.categoria, trabajo.aciertos_categoria_ganadora),
                    "ganadores": c.ganadores,
                    "importe_categoria": None
                    if c.importe_categoria is None
                    else f"{c.importe_categoria:.2f}",
                    "importe_individual": None
                    if c.importe_individual is None
                    else f"{c.importe_individual:.2f}",
                    "pozo_vacante_acumulado": None
                    if c.pozo_vacante_acumulado is None
                    else f"{c.pozo_vacante_acumulado:.2f}",
                }
            )
    return {
        "numero": numero,
        "modalidad": _modalidad(m),
        "bloque": bloque,
        "es_correccion": bool(trabajo.es_correccion),
        "numeros": _numeros_de(trabajo) if bloque == NUMEROS else [],
        "categorias": categorias,
        "sin_ganadores": bool(getattr(trabajo, "sin_ganadores", False)),
        "aciertos_categoria_ganadora": getattr(trabajo, "aciertos_categoria_ganadora", None),
        "fuente_descripcion": trabajo.fuente_descripcion or "",
        "fuente_fecha_consulta": trabajo.fuente_fecha_consulta,
        "motivo_correccion": trabajo.motivo_correccion or "",
        "bloqueantes": [b.texto for b in bloqueantes],
        "advertencias": [a.texto for a in advertencias],
        "formulario": formulario_dto(form),
    }


@router.get("/admin/sorteos/{numero}/{modalidad}/{bloque}/publicar/", response=RevisionPublicacion)
@nivel("A")
def revisar(request, numero: int, modalidad: str, bloque: str):
    """[001] RN-17, RN-22: lo que impide publicar y lo que exige confirmación."""
    _, m, mc = _contexto(numero, modalidad, bloque)
    trabajo = _trabajo(mc, bloque)
    return _revision(numero, m, bloque, trabajo, PublicarForm())


@router.post("/admin/sorteos/{numero}/{modalidad}/{bloque}/publicar/", response=PanelSorteo)
@nivel("A")
def publicar(request, numero: int, modalidad: str, bloque: str, datos: DatosFormulario):
    """[001] AC-2.10 a AC-2.12."""
    _, m, mc = _contexto(numero, modalidad, bloque)
    trabajo = _trabajo(mc, bloque)
    form = PublicarForm(_datos(datos))
    form.is_valid()
    try:
        servicios.publicar(
            request.user,
            trabajo,
            advertencias_confirmadas=form.cleaned_data.get("confirmar_advertencias", False),
            cotejo_confirmado=form.cleaned_data.get("cotejo", False),
        )
    except servicios.ErrorResultados as error:
        raise _error_general(error.mensajes) from None
    texto = "Se publicó la corrección" if trabajo.es_correccion else "Se publicó"
    messages.success(request, f"{texto}: {NOMBRE_BLOQUE[bloque].lower()} de {m.nombre}.")
    return _panel(request, numero)


@router.post("/admin/sorteos/{numero}/{modalidad}/{bloque}/revision/", response=PanelSorteo)
@nivel("A")
def poner_en_revision(request, numero: int, modalidad: str, bloque: str, datos: DatosFormulario):
    _, _, mc = _contexto(numero, modalidad, bloque)
    motivo = _motivo(datos, "Falta el motivo.")
    try:
        servicios.marcar_revision(request.user, mc, bloque, motivo)
    except servicios.ErrorResultados as error:
        raise _error_general(error.mensajes) from None
    messages.success(request, "El bloque quedó En revisión.")
    return _panel(request, numero)


@router.post("/admin/sorteos/{numero}/{modalidad}/{bloque}/quitar-revision/", response=PanelSorteo)
@nivel("A")
def quitar_revision(request, numero: int, modalidad: str, bloque: str, datos: DatosFormulario):
    _, _, mc = _contexto(numero, modalidad, bloque)
    motivo = _motivo(datos, "Falta el motivo.")
    try:
        servicios.quitar_revision(request.user, mc, bloque, motivo)
    except servicios.ErrorResultados as error:
        raise _error_general(error.mensajes) from None
    messages.success(request, "Se quitó la marca de revisión.")
    return _panel(request, numero)


@router.post("/admin/sorteos/{numero}/{modalidad}/{bloque}/corregir/", response=PanelSorteo)
@nivel("A")
def corregir(request, numero: int, modalidad: str, bloque: str, datos: DatosFormulario):
    """[001] US7: inicia la corrección; el público sigue viendo lo publicado."""
    _, _, mc = _contexto(numero, modalidad, bloque)
    form = CorreccionForm(_datos(datos))
    if not form.is_valid():
        raise _error_general([e for errores in form.errors.values() for e in errores])
    try:
        servicios.iniciar_correccion(
            request.user,
            mc,
            bloque,
            form.cleaned_data["motivo"],
            form.cleaned_data["fuente_descripcion"],
            form.cleaned_data["fuente_fecha_consulta"],
        )
    except servicios.ErrorResultados as error:
        raise _error_general(error.mensajes) from None
    messages.success(
        request, "Se inició la corrección. El público sigue viendo los valores publicados."
    )
    return _panel(request, numero)
