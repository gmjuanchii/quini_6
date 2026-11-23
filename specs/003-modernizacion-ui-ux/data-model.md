# Modelo de datos (Data Model): Modernización visual y de experiencia de uso

**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) → "Entidades clave" | **Research**: [research.md](research.md)

Esta feature **no agrega datos de negocio** (spec, NFR-009). No hay tablas nuevas. El único cambio persistente es una restricción de unicidad (RN-03). El resto son valores derivados que no se guardan, estados efímeros que viven en la sesión del servidor o en un token firmado, y una cookie de preferencia.

---

## 1. Cambio en una entidad existente

### `extracciones.Extraccion` ([002] data-model.md)

| Cambio | Detalle | Requisito |
|--------|---------|-----------|
| Restricción única parcial nueva `extraccion_periodo_unico_en_curso` | `UniqueConstraint(fields=["desde", "hasta"], condition=Q(estado="EN_CURSO"))` | RN-03, AC-3.5, FR-006, [003] R-09 |

- Migración: `extracciones/migrations/0003_extraccion_periodo_unico_en_curso.py`. Antes de crearla, la migración no necesita limpiar datos: [002] ya impide dos extracciones en curso del mismo administrador, y si hubiera dos de distintos administradores con el mismo período en curso, la migración se detiene con un mensaje claro (caso que no debería existir; se documenta en [quickstart.md](quickstart.md)).
- Se conserva `extraccion_una_en_curso_por_admin` ([002] AC-1.11).
- `EstadoExtraccion` **no cambia** (EN_CURSO, FINALIZADA, CON_ADVERTENCIAS, SIN_SORTEOS).

---

## 2. Valores derivados (no se guardan)

### `EtiquetaEstado` — `dominio/extraccion/etiqueta.py`

Enumeración pura (sin Django) con la etiqueta visible de RN-01.

| Valor | Texto | Variante de `StatusBadge` | Icono | Se obtiene cuando |
|-------|-------|---------------------------|-------|-------------------|
| `EN_CURSO` | En curso | `info` | `loader-circle` (gira; sin giro con movimiento reducido) | `estado == EN_CURSO` (incluye "en espera de turno") |
| `FINALIZADA` | Finalizada | `success` | `circle-check` | `estado == FINALIZADA` |
| `CON_ADVERTENCIAS` | Con advertencias | `warning` | `triangle-alert` | `estado == CON_ADVERTENCIAS` y **ningún** sorteo `NO_RECUPERADO` |
| `SIN_SORTEOS` | Sin sorteos | `neutral` | `circle-dashed` | `estado == SIN_SORTEOS` |
| `CON_ERROR` | Con error | `danger` | `circle-x` | `estado == CON_ADVERTENCIAS` y **al menos un** sorteo `NO_RECUPERADO` (precedencia sobre "Con advertencias") |

Función: `etiqueta_de(estado: EstadoExtraccion, tiene_no_recuperados: bool) -> EtiquetaEstado`. Cada valor tiene su `explicacion` (RN-02, claves `etiqueta.*.explicacion` del catálogo) y su `slug` para la dirección (`en-curso`, `finalizada`, `con-advertencias`, `sin-sorteos`, `con-error`).

Por definición de [002] RN-33, `FINALIZADA` implica cero sorteos no recuperados, así que `(FINALIZADA, True)` no puede ocurrir; la función lo trata como `CON_ERROR` por seguridad (la información de error nunca se oculta, Const. IX) y la prueba unitaria lo documenta.

**Orden por la columna "Estado"** (AC-9.1): `EN_CURSO` < `CON_ERROR` < `CON_ADVERTENCIAS` < `SIN_SORTEOS` < `FINALIZADA` (ascendente = primero lo que requiere atención). En la consulta se obtiene con `Case/When` sobre `estado` y la anotación `tiene_no_recuperados = Exists(SorteoExtraido.objects.filter(extraccion=OuterRef("pk"), estado="NO_RECUPERADO"))`.

### `ConsultaListado` — parámetros del listado de extracciones

Viven en la dirección, no se guardan (NFR-008).

| Parámetro | Valores | Por defecto | Inválido |
|-----------|---------|-------------|----------|
| `estado` | slug de `EtiquetaEstado` o vacío ("Todos los estados") | vacío | se ignora y se muestra "Todos los estados" |
| `orden` | `fecha`, `-fecha`, `periodo`, `-periodo`, `estado`, `-estado` | `-fecha` ([002] RN-44) | se usa el por defecto |
| `pagina` | entero ≥ 1 | 1 | fuera de rango → última página con datos (Casos límite) |

`periodo` ordena por `desde` y luego `hasta`. Todos desempatan por `-id`. Tamaño de página: 20 (RN-07).

### `AtajoPeriodo` — `dominio/periodos.py`

Función pura `atajos(hoy: date, formulario: Literal["extraccion", "estadisticas"], primer_sorteo: date | None) -> list[Atajo]`, con `Atajo(clave, texto, desde, hasta)`.

| Clave | Texto | Desde | Hasta | Formularios |
|-------|-------|-------|-------|-------------|
| `anio_en_curso` | Año en curso | 01/01 del año de `hoy` | `hoy` (el 01/01, igual al inicio) | extracción, estadísticas |
| `anio_anterior` | Año anterior | 01/01 del año anterior | 31/12 del año anterior | extracción, estadísticas |
| `todo_el_historial` | Todo el historial | `primer_sorteo` | `hoy` | solo estadísticas; se omite si no hay sorteos publicados |

`hoy` se calcula en el servidor con `America/Argentina/Buenos_Aires` (RN-04). Ambos atajos de la extracción caben en los 12 meses de [002] RN-04.

### `Mensaje` — `dominio/mensajes.py`

Diccionario `clave → texto` con todos los textos visibles ([contracts/mensajes.md](contracts/mensajes.md)). Los textos con variables usan `{nombre}` y se completan con `mensaje(clave, **valores)`. No depende de Django.

---

## 3. Estados efímeros

### `ClaveIdempotencia` — en la sesión del servidor (FR-031, [003] R-11)

| Campo | Tipo | Regla |
|-------|------|-------|
| `clave` | UUID (texto) | La genera el servidor al mostrar el formulario; llega como campo oculto `clave_idempotencia` o cabecera `Idempotency-Key` |
| `accion` | texto | Nombre de la acción (`jugada.registrar`, `extraccion.iniciar`, …); una clave usada con otra acción se rechaza |
| `resultado` | texto | Dirección de destino (HTML) o identificador creado (API) |
| `usada_en` | fecha y hora | Para descartar las más viejas |

Se guarda en `request.session["claves_idempotencia"]` (lista de las últimas 50). Vence con la sesión (30 min de inactividad, [001] NFR-005). Un pedido sin clave se procesa normalmente (compatibilidad con clientes sin scripts que no la envían: el formulario HTML siempre la trae).

### `FormularioPendiente` — token firmado (FR-032, [003] R-12)

| Campo (dentro del token) | Tipo | Regla |
|--------------------------|------|-------|
| `ruta` | texto | Ruta destino; debe resolver a una vista de `FORMULARIOS_REANUDABLES`, si no, el token se ignora |
| `campos` | objeto `nombre → lista de valores` | Lo enviado, **sin** `csrfmiddlewaretoken`, `clave_idempotencia` ni campos de contraseña |
| `emitido` | marca de tiempo (de la firma) | Vigencia: 60 min; vencido o alterado → se ignora y se muestra el formulario vacío |

Firmado con `django.core.signing.TimestampSigner` (sal `quini6.formulario_pendiente`) y comprimido. Viaja como campo oculto `pendiente` en el formulario de ingreso; no se guarda en el navegador ni en el servidor. Tamaño máximo: 8 KB (si lo excede, se ignora y se informa que hay que volver a completar el formulario).

Si la ruta del token pertenece a Next.js mientras "Ingresar" sigue en Django, el token viaja una vez más, en un POST explícito de la persona ("Volver al formulario"), hacia esa ruta (AC-14.4, R-12). "No se guarda en el servidor" significa que ningún servidor lo registra ni lo conserva después de responder (NFR-008, aclarado el 21/11/2026).

Vistas reanudables: registrar jugada, editar jugada, iniciar extracción histórica y, de [001], crear y modificar sorteo y cargar números y premios. Los formularios de eliminación no se reanudan (no tienen datos que perder).

---

### `Aviso` — mensajes de Django en la sesión (FR-043, [003] R-31)

Sin cambios de almacenamiento: es el sistema de mensajes de Django que ya se usa. Lo nuevo es que Next.js los lee (`GET /api/v1/avisos/`, se marcan como leídos) y los agrega (`POST /api/v1/avisos/`, solo por clave del catálogo), así un aviso sobrevive a una redirección entre aplicaciones.

## 4. Preferencia de tema — cookie (FR-036, [003] R-14)

| Atributo | Valor |
|----------|-------|
| Nombre | `quini6_tema` |
| Valores | `claro`, `oscuro`; sin cookie = "Según el dispositivo". Otro valor se ignora |
| Duración | 400 días |
| `Path` / `SameSite` / `Secure` / `HttpOnly` | `/` / `Lax` / en producción / no (la cambia el script) |
| Uso en el servidor | Solo para escribir `data-theme` en `<html>`; no se registra ni se asocia a la cuenta |

---

## 5. Representación en la API (DTO)

Formas que expone `/api/v1/` ([contracts/api.md](contracts/api.md)). Reglas comunes: fechas ISO 8601 (`AAAA-MM-DD`; fecha y hora con `-03:00`), importes como cadena decimal con dos decimales, números de bolillas como enteros (la interfaz los muestra con dos dígitos), y los datos de [002] con estado explícito (`Dato` → `{ "estado": "valor" | "no_disponible" | "no_corresponde" | "sin_determinar", "valor": … }`), nunca `null` en lugar de un dato desconocido.

| DTO | Campos principales | Fuente |
|-----|--------------------|--------|
| `Sesion` | `correo`, `es_administrador`, `vence_en` | `request.user`, sesión |
| `ExtraccionResumen` | `id`, `iniciada_en`, `desde`, `hasta`, `etiqueta` (`EtiquetaEstado` + `texto` + `explicacion`), `en_curso`, `avance` (`identificando`, `procesados`, `total`), `eliminable`, `creada_por` (solo administradores, [002]) | `consultas.listado_extracciones` + `etiqueta_de` |
| `Pagina<T>` | `elementos`, `pagina`, `paginas`, `total`, `orden`, `filtro` | Paginador de Django |
| `Avance` | `en_curso`, `identificando`, `procesados`, `total`, `etiqueta`, `aviso_final` (texto de `ext.termino_*` cuando terminó) | `consultas.avance` |
| `Problema` | `type`, `title`, `status`, `detail`, `errores: [{campo, codigo, mensaje}]`, `pendiente?` (R-12), `existente?` (RN-03) | RFC 9457 |

Los DTO de Resultados, Jugadas, Estadísticas y Administración de sorteos reflejan exactamente lo que hoy muestran sus plantillas (NFR-009) y se fijan en el contrato antes de migrar cada pantalla (pedido §3.3).

---

## 6. Lo que no cambia

- Ningún modelo de `cuentas`, `resultados`, `jugadas` ni `estadisticas`.
- `SorteoExtraido`, `IntentoConsulta`, el resumen y el CSV de [002] (contrato v3.0 sin cambios, SC-011).
- Nombres internos, direcciones y columnas del CSV: el cambio de "concurso" a "sorteo" (D-04) es solo de textos visibles. Las rutas `/administracion/concursos/…` se conservan.
