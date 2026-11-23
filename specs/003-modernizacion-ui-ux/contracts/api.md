# Contrato de la API v1

**Plan**: [../plan.md](../plan.md) | **Modelo**: [../data-model.md](../data-model.md) § 5 | **Research**: R-11, R-12, R-16, R-17, R-19

Este documento es el **contrato aprobado** de la API. El esquema OpenAPI 3.1 que genera Django Ninja (`contratos/openapi.json`, versionado) debe coincidir con él; la prueba `tests/api/test_contrato_openapi.py` falla si el esquema cambia sin actualizarse en el repositorio, y la revisión de cada cambio compara el esquema con este documento. Cada pantalla se migra **solo después** de que sus operaciones estén implementadas, probadas y publicadas en el esquema (pedido §3.3).

## 1. Reglas comunes

| Aspecto | Regla |
|---------|-------|
| Base | `/api/v1/`, mismo origen que el sitio. Sin CORS |
| Autenticación | Sesión de Django (cookie `sessionid`). Sin tokens en el navegador |
| CSRF | Obligatorio en `POST`, `PUT`, `PATCH`, `DELETE`: cabecera `X-CSRFToken` con el valor de la cookie `csrftoken` (la entrega `GET /api/v1/sesion/`) |
| Autorización | Igual que las vistas HTML: **P** público, **U** usuario (`usuario=request.user`), **A** administrador (`es_administrador`). Una jugada ajena o inexistente responde `404` idéntico |
| Idempotencia | Las operaciones marcadas ⟳ aceptan `Idempotency-Key` (UUID); repetir la clave devuelve la misma respuesta sin repetir el efecto (R-11) |
| Formatos | Fechas `AAAA-MM-DD`; fecha y hora ISO 8601 con `-03:00`; importes como cadena decimal (`"1234.56"`); bolillas como enteros 0–45; `Dato` de [002] con estado explícito |
| Errores | `application/problem+json` (RFC 9457): `type`, `title`, `status`, `detail` y extensiones `errores: [{campo, codigo, mensaje}]`, `pendiente` (401 en mutaciones, R-12), `existente` (409 de RN-03). `mensaje` y `detail` salen del catálogo ([mensajes.md](mensajes.md)) |
| Códigos | `200`/`201`/`204` éxito · `401` sin sesión · `403` sin permisos · `404` inexistente · `409` conflicto de estado · `422` validación |
| Caché | Privadas: `Cache-Control: no-store`. Públicas: `Cache-Control: no-cache` (los resultados pueden corregirse) |
| Paginación | `?pagina=` (1 en adelante); respuesta `Pagina<T>` (data-model § 5) |
| Versionado | Cambios compatibles (agregar campos u operaciones) dentro de v1; quitar o cambiar un campo exige v2 y aprobación |

## 2. Operaciones

### Sesión y cuentas — Fase 0 (lectura) y pantalla 5

| Operación | Ruta | Nivel | Respuesta | Notas |
|-----------|------|:-----:|-----------|-------|
| Consultar sesión | `GET /sesion/` | P | `Sesion` o `{ "correo": null }`; fija la cookie `csrftoken` | Usada por Next.js para el encabezado y por la prueba T208 |
| Ingresar ⟳ | `POST /sesion/` | P | `Sesion` + `Set-Cookie` | `correo`, `contrasena`, `pendiente?`. Errores `cuenta.credenciales_incorrectas` (sin revelar si el correo existe, FR-020) y `cuenta.bloqueada` ([001] R-04) |
| Salir | `DELETE /sesion/` | U | `204` | |
| Crear cuenta ⟳ | `POST /cuentas/` | P | `201` `Sesion` | Mensajes de [001] AC-3.2, AC-3.3 (reescritos) |

### Avisos — desde la convivencia (Etapa 2, R-31)

| Operación | Ruta | Nivel | Respuesta | Notas |
|-----------|------|:-----:|-----------|-------|
| Leer avisos pendientes | `GET /avisos/` | P | `[{tipo: "exito" \| "info" \| "advertencia" \| "error", texto}]` | Los entrega y los marca como leídos (mensajes de Django en la sesión); `no-store` |
| Agregar un aviso | `POST /avisos/` | P | `204` | Solo `tipo` y `clave` del catálogo con sus variables (nunca texto libre); lo usan las Server Actions antes de redirigir (FR-043) |

### Resultados — pantalla 4 (lectura desde la Fase 0)

| Operación | Ruta | Nivel | Respuesta |
|-----------|------|:-----:|-----------|
| Últimos resultados | `GET /sorteos/ultimo/` | P | `SorteoPublico` o `404` `resultados.sin_publicar` |
| Listado | `GET /sorteos/?pagina=` | P | `Pagina<SorteoResumen>` |
| Buscar | `GET /sorteos/buscar/?numero=&fecha=` | P | `Pagina<SorteoResumen>` o `422` |
| Detalle | `GET /sorteos/{numero}/` | P | `SorteoPublico` (modalidades, números sorteados, premios, avisos de corrección y revisión, fuente) |

### Estadísticas — pantalla 2 (lectura desde la Fase 0)

| Operación | Ruta | Nivel | Respuesta |
|-----------|------|:-----:|-----------|
| Frecuencias | `GET /estadisticas/?modalidad=&desde=&hasta=&numero=` | P | `Frecuencias` (por número: frecuencia y porcentaje como cadena decimal; sorteos considerados; sorteos sin información; número consultado) o `422` |
| Atajos de período | `GET /periodos/atajos/?formulario=estadisticas\|extraccion` | P (estadísticas) / A (extracción) | `[Atajo]` (data-model § 2) |

### Mis jugadas — pantalla 3

| Operación | Ruta | Nivel | Respuesta |
|-----------|------|:-----:|-----------|
| Listado | `GET /jugadas/` | U | `[JugadaResumen]` con su comparación por sorteo |
| Sorteos disponibles | `GET /jugadas/sorteos-disponibles/` | U | Sorteos para los que se puede registrar una jugada ([001] AC-4.7, AC-4.8) |
| Registrar ⟳ | `POST /jugadas/` | U | `201` `Jugada`; `409` `jugada.duplicada` con `confirmar: true` para guardarla igual (RN-06 de [001]) |
| Detalle | `GET /jugadas/{id}/` | U | `Jugada` con comparación, o `404` |
| Modificar ⟳ | `PUT /jugadas/{id}/` | U | `Jugada`; `409` `jugada.fija` si su sorteo ya se publicó |
| Eliminar ⟳ | `DELETE /jugadas/{id}/` | U | `204`; `409` `jugada.fija` |

### Extracción histórica — pantalla 1

| Operación | Ruta | Nivel | Respuesta |
|-----------|------|:-----:|-----------|
| Listado | `GET /extracciones/?estado=&orden=&pagina=` | A | `Pagina<ExtraccionResumen>` (data-model § 2 y § 5) |
| Iniciar ⟳ | `POST /extracciones/` | A | `201` `ExtraccionResumen`; `422` validación del período ([002] RN-01 a RN-04); `409` `ext.periodo_en_curso` con `existente: {id, url}` (RN-03) o con la extracción en curso del mismo administrador ([002] AC-1.11) |
| Detalle | `GET /extracciones/{id}/` | A | `Extraccion` (resumen RN-33, fuentes, sorteos que requieren revisión, etiqueta, enlace al CSV) |
| Avance | `GET /extracciones/{id}/avance/` | A | `Avance` (data-model § 5); se consulta cada 3 s mientras `en_curso` (R-10) |
| Sorteo extraído | `GET /extracciones/{id}/sorteos/{numero}/` | A | `SorteoExtraido` con intentos por fuente, datos consolidados (`Dato` con estado y `calculo`), discrepancias y observaciones |
| Eliminar ⟳ | `DELETE /extracciones/{id}/` | A | `204`; `409` `ext.eliminar_en_curso`; `404` `ext.no_existe` |
| Descargar CSV | `GET /administracion/extracciones/{id}/csv/` | A | Ruta HTML de [002] sin cambios (no es parte de `/api/v1/`) |

#### DTO de la pantalla 1 (T172, R-32) — **aprobado por el responsable el 22/11/2026**

Origen: `extracciones/consultas.py` (las mismas funciones que usan las vistas HTML, NFR-009). Ningún campo es `null` salvo donde se indica; "texto" = ya resuelto desde el catálogo.

**`Etiqueta`** (`dominio/extraccion/etiqueta.py :: EtiquetaEstado`)

| Campo | Tipo | Nulo | Origen |
|-------|------|:----:|--------|
| `valor` | `"en_curso" \| "finalizada" \| "con_advertencias" \| "sin_sorteos" \| "con_error"` | no | `EtiquetaEstado.value` |
| `slug` | texto (`en-curso`, …) | no | `EtiquetaEstado.slug` (para `?estado=`) |
| `texto` | texto | no | `mensaje(clave_texto)` |
| `explicacion` | texto | no | `mensaje(clave_explicacion)` (RN-02) |
| `variante` | `"info" \| "success" \| "warning" \| "neutral" \| "danger"` | no | `EtiquetaEstado.variante` |
| `requiere_revision` | booleano | no | `EtiquetaEstado.requiere_revision` (AC-1.3) |

**`AvanceDatos`** (también es la respuesta de `GET /extracciones/{id}/avance/`, `Avance` de data-model § 5)

| Campo | Tipo | Nulo | Origen |
|-------|------|:----:|--------|
| `en_curso` | booleano | no | `consultas.avance()["en_curso"]` |
| `identificando` | booleano | no | `["identificando"]` |
| `procesados` | entero | no | `["procesados"]` |
| `total` | entero | **sí** (todavía identificando) | `["total"]` |
| `etiqueta` | `Etiqueta` | no | `["etiqueta"]` |
| `aviso_final` | `{tipo: "success" \| "warning" \| "error" \| "info", texto, enlace}` | **sí** (en curso) | `["aviso_final"]` (`ext.termino_*`) |

**`ExtraccionResumen`** (fila del listado)

| Campo | Tipo | Nulo | Origen |
|-------|------|:----:|--------|
| `id` | entero | no | `Extraccion.pk` |
| `iniciada_en` | fecha y hora ISO `-03:00` | no | `iniciada_en` |
| `desde`, `hasta` | `AAAA-MM-DD` | no | `desde`, `hasta` |
| `creada_por` | texto (correo) | no | `creada_por.email` ([002] AC-1.14; la API es solo nivel A) |
| `etiqueta` | `Etiqueta` | no | `etiqueta_de_extraccion()` |
| `en_curso` | booleano | no | `en_curso` |
| `avance` | `AvanceDatos` | no | `consultas.avance()` |
| `eliminable` | booleano | no | `not en_curso` (AC-2.6) |
| `descargable` | booleano | no | `consultas.puede_descargar()` |
| `url_csv` | texto | **sí** (si no es descargable) | `/administracion/extracciones/{id}/csv/` |
| `nombre_acciones` | texto | no | `mensaje("ext.acciones", fecha_hora=…)` (nombre accesible del menú ⋮) |

**`PaginaExtracciones`** = `Pagina<ExtraccionResumen>` (data-model § 5): `elementos`, `pagina`, `paginas`, `total`, `orden` (uno de `fecha`, `-fecha`, `periodo`, `-periodo`, `estado`, `-estado`; inválido → `-fecha`), `filtro` (`slug` o `null` = todos), `tiene_anterior`, `tiene_siguiente`; además `en_curso_propia` (`ExtraccionResumen` o `null`: la del administrador que consulta, para el panel de avance y para ocultar el formulario, AC-1.11).

**`IniciarExtraccion`** (cuerpo de `POST /extracciones/`): `inicio`, `fin` (texto `AAAA-MM-DD` o `dd/mm/aaaa`, como el formulario). Errores `422` por campo con los mismos mensajes que `PeriodoForm` (`fecha.falta_inicio`, `fecha.falta_fin`, `fecha.inexistente`, `fecha.fin_anterior`, `ext.fin_futura`, RN-04 de [002]), con `campo` = `inicio` \| `fin` \| `""` (error general). `409` `ext.periodo_en_curso` con `existente: {id, url}`; si el administrador ya tiene una en curso, `409` con `detail` = `ext.en_curso` ("Extracción en curso", sin texto nuevo en el catálogo) y `existente` = la propia (AC-1.11; la vista HTML redirige a ella). `existente.url` = `/administracion/extracciones/{id}/`.

**`Extraccion`** (detalle)

| Campo | Tipo | Nulo | Origen (`consultas.datos_pagina`) |
|-------|------|:----:|--------|
| todos los de `ExtraccionResumen` | | | |
| `finalizada_en` | fecha y hora | **sí** | `finalizada_en` |
| `estado_texto` | texto | no | `estado_texto` ([002]) |
| `ninguna_fuente` | booleano | no | `ninguna_fuente` (AC-3.4, `ext.ninguna_fuente`) |
| `resumen` | `ResumenExtraccion` | **sí** (en curso o sin sorteos) | `resumen` |
| `sorteos` | `[{numero, fecha (nulo), estado, estado_texto}]` | no (lista vacía) | `sorteos` |

`ResumenExtraccion` ([002] RN-33): `identificados`, `recuperados`, `parciales`, `inconsistencias`, `no_recuperados` (enteros); `fuentes: [{fuente, nombre, aportados, fallidos: [{texto, cantidad}], requiere_mantenimiento}]`; `huecos: [entero]`; `cobertura_desde` (`AAAA-MM-DD` o `null`); `a_revisar: [{numero, fecha (nulo), estado, estado_texto, motivos: [texto]}]`. Los campos de cada fuente se copian del JSON guardado sin renombrar.

**`SorteoExtraido`** (`consultas.detalle_sorteo`)

| Campo | Tipo | Nulo |
|-------|------|:----:|
| `numero` | entero | no |
| `fecha` | `DatoConsolidado` | no |
| `estado`, `estado_texto` | texto | no |
| `motivos` | `[texto]` | no |
| `combina_fuentes`, `sin_corroborar`, `reglas_no_verificadas` | booleano | no |
| `fuentes` | `[{nombre, resultado (texto), url, consultado_en (nulo), observaciones: [texto]}]` en el orden de `ORDEN_FUENTES` | no |
| `modalidades` | `[{nombre, informada, propia, numeros: DatoConsolidado, categorias: [{nombre, estado_pozo, datos: [{rotulo, …DatoConsolidado}]}]}]` | no |
| `observaciones` | `[{fuente (nulo), texto}]` | no |

*`enlace_oficial` se quitó el 23/11/2026 ([002] D-33): el cotejo se hace con el `url` de cada fuente.*

`Dato` (data-model § 5): `{estado: "valor" | "no_disponible" | "no_corresponde" | "sin_determinar", tipo: "entero" | "importe" | "fecha" | "numeros" | "texto" | null, valor, texto}` — `valor` es entero, cadena decimal (importe), `AAAA-MM-DD`, lista de enteros o texto cuando `estado = "valor"`, y `null` en los demás; `texto` es el texto de [002] del estado ("No disponible", …) o `null`. Nunca `null`→0.
`DatoConsolidado` = `Dato` + `fuentes: [texto]`, `sin_corroborar`, `discrepancia` y `diferencia_tolerada` (`{tipo, valores: [{fuente, valor: Dato}]}` o `null`), `calculo` (texto o `null`; marca de valor calculado, Const. de [002]).

**`Atajo`** (`GET /periodos/atajos/`): `{clave, texto, desde, hasta}` con `desde`/`hasta` en `AAAA-MM-DD` (data-model § 2). `formulario` inválido → `422`.

**Eliminar**: `DELETE /extracciones/{id}/` → `204` y agrega el aviso `ext.eliminada` a la sesión (lo muestra la pantalla siguiente, FR-043); `409` `ext.eliminar_en_curso`; `404` `ext.no_existe`. Con `Idempotency-Key` repetida → `204` sin efecto.

### Formulario pendiente — convivencia (Etapa 2, R-12, AC-14.4)

| Operación | Ruta | Nivel | Respuesta |
|-----------|------|:-----:|-----------|
| Leer formulario pendiente | `POST /formularios/pendiente/` | U | `{ruta, campos: {nombre: [valor]}}`; `422` `api.dato_invalido` si el token es inválido, venció (60 min) o su ruta no es la pedida |

Cuerpo: `{pendiente, ruta}`. La usa Next.js cuando "Volver al formulario" de Django le envía el token por POST: Next.js lo pasa a esta operación, que lo verifica con la firma de Django y devuelve lo escrito, y la página muestra su formulario precargado **sin enviarlo**. No registra nada ni guarda el token (NFR-008). Es POST para que el token no viaje en la dirección.

### Administración de sorteos ([001]) — pantalla 6 (P-03 aprobado el 21/11/2026)

Una operación por cada vista de `resultados/urls_admin.py`, todas nivel **A**, con los mismos servicios (`resultados/servicios.py`), validaciones (`resultados/forms.py`) y mensajes que las vistas HTML. `{modalidad}` = slug (`primer-sorteo`, `la-segunda`, `revancha`, `siempre-sale`, `premio-extra`); `{bloque}` = `numeros` \| `premios`. Las mutaciones exitosas agregan a la sesión el mismo aviso de la vista HTML (FR-043).

| Operación | Ruta | Respuesta |
|-----------|------|-----------|
| Listado | `GET /admin/sorteos/` | `[SorteoAdmin]` |
| Crear ⟳ | `POST /admin/sorteos/` | `201` `SorteoAdmin`; `422` por campo (`numero`, `fecha_sorteo`, `modalidades`) |
| Panel | `GET /admin/sorteos/{numero}/` | `PanelSorteo` |
| Modificar | `PUT /admin/sorteos/{numero}/` | `PanelSorteo`; `422`; `409` si ya tiene publicaciones (mismo mensaje) |
| Historial | `GET /admin/sorteos/{numero}/historial/` | `[CambioRegistrado]` |
| Formulario de números | `GET /admin/sorteos/{numero}/{modalidad}/numeros/` | `BorradorNumeros` (valores iniciales); `409` `admin.bloque_publicado` |
| Guardar números | `PUT /admin/sorteos/{numero}/{modalidad}/numeros/` | `BorradorNumeros`; `422` por campo (`n1`…`n6`, `fuente_descripcion`, `fuente_fecha_consulta`, `motivo_correccion`) |
| Formulario de premios | `GET /admin/sorteos/{numero}/{modalidad}/premios/` | `BorradorPremios`; `409` `admin.bloque_publicado` |
| Guardar premios | `PUT /admin/sorteos/{numero}/{modalidad}/premios/` | `BorradorPremios`; `422` por campo (`{categoria}_ganadores`, `{categoria}_importe_categoria`, …) |
| Observar | `POST /admin/sorteos/{numero}/{modalidad}/{bloque}/observar/` | `PanelSorteo`; `422` `motivo` |
| Resolver observación | `POST …/{bloque}/resolver/` | `PanelSorteo` |
| Revisar para publicar | `GET …/{bloque}/publicar/` | `RevisionPublicacion` (bloqueantes, advertencias, datos a cotejar) |
| Publicar | `POST …/{bloque}/publicar/` | `PanelSorteo`; `422` con los mensajes de `servicios.ErrorResultados` |
| Poner en revisión | `POST …/{bloque}/revision/` | `PanelSorteo`; `422` `motivo` |
| Quitar revisión | `POST …/{bloque}/quitar-revision/` | `PanelSorteo` |
| Corregir | `POST …/{bloque}/corregir/` | `PanelSorteo`; `422` (`motivo`, `fuente_descripcion`, `fuente_fecha_consulta`) |

Las rutas HTML (`/administracion/concursos/…`) no cambian; la API usa `/admin/sorteos/…` (D-04: "sorteo" en lo visible y en lo nuevo).

Agregados compatibles al implementar (T207, 22/11/2026): `GET /admin/sorteos/nuevo/` y `GET /admin/sorteos/{numero}/modificar/` devuelven el formulario vacío o con los valores actuales. Los cuerpos de las mutaciones son `{campos: {nombre: valor}}` con los **nombres de los campos de los formularios de Django** (`numero`, `fecha_sorteo`, `modalidades`, `n1`…`n6`, `{categoria}_{dato}`, `motivo`, `cotejo`, …), y cada formulario se describe campo por campo (`FormularioDTO`: `nombre`, `etiqueta`, `tipo`, `valor`, `opciones`, `ayuda`, `requerido`, `errores`; en premios, además, `filas` por categoría). Así la pantalla muestra los mismos rótulos y opciones que Django y la validación es siempre la de `resultados/forms.py`. Un `422` incluye `formulario` con lo enviado y sus errores. El sorteo duplicado responde `422` `admin.concurso_duplicado` con `existente`.

#### DTO de las pantallas 2 a 6 (T181, T187, T193, T204, R-32) — **aprobados por el responsable el 22/11/2026**

Reglas comunes a todos: textos visibles ya resueltos desde el catálogo o los dominios de [001] y [002] (`texto`, `*_texto`); fechas `AAAA-MM-DD`; importes y porcentajes como cadena decimal; bolillas como enteros; nunca se expone información no publicada en las operaciones públicas (Const. VIII).

**Pantalla 2 — `Frecuencias`** (`estadisticas/views.py :: index` + `dominio/estadisticas.py`)

| Campo | Tipo | Nulo | Origen |
|-------|------|:----:|--------|
| `consulta` | `{modalidad (valor del formulario HTML, p. ej. `LA_SEGUNDA`), modalidad_nombre, desde, hasta, numero}` | `desde`, `hasta`, `numero` sí | la consulta mostrada (`Consulta`) |
| `modalidades` | `[{valor, nombre}]` | no | `estadisticas.forms.MODALIDADES` (sin Premio Extra) |
| `cantidad_sorteos` | entero | no | `Frecuencias.cantidad_sorteos` (0 si `SinSorteos`) |
| `primera_fecha`, `ultima_fecha` | fecha | sí (sin sorteos) | `Frecuencias` |
| `sorteos_sin_informacion` | entero | no | `concursos_sin_informacion` |
| `numeros` | `[{numero, frecuencia, porcentaje}]` del 00 al 45, por número | no (vacía sin sorteos) | `Frecuencias.numeros` |
| `numero_consultado` | `{numero, frecuencia, porcentaje}` | sí | `Frecuencias.numero(n)` |
| `avisos` | `[texto]` | no | `EstadisticasForm.avisos` (Premio Extra no se ofrece) |

Parámetros: `modalidad`, `desde`, `hasta` (`dd/mm/aaaa` o `AAAA-MM-DD`), `numero`, y `anterior_modalidad`, `anterior_desde`, `anterior_hasta`, `anterior_numero` (la consulta que se estaba mostrando, como los campos ocultos del formulario HTML). Con errores: `422` con `errores` por campo (`desde`, `hasta`, `numero`; mismos textos que `errores_campo`), `detail` = el primer error general ([001] AC-6.8) y la extensión `resultado` = `Frecuencias` de la consulta anterior (se sigue mostrando, [001] AC-6.8). El orden de la tabla (`?orden=`) es solo presentación y lo aplica la pantalla (NFR-009).

**Pantalla 3 — Mis jugadas** (`jugadas/views.py`, `dominio/comparacion.py`)

`JugadaResumen`: `id`, `sorteo` (`{numero, fecha}`), `numeros` (6 enteros ordenados), `costo` (decimal), `modalidades` (`[nombre]`), `estado` (`{texto, clase}` de `resumir_jugada`: "Con premio", "Sin premio", …), `modificable` (RN-08).

`Jugada` = `JugadaResumen` + `creada_en`, `modificada_en` (nulo), `comparacion: [ComparacionModalidad]`, `resumen` (`{texto, clase}`).

`ComparacionModalidad` (`ResultadoModalidad`): `modalidad` (`{slug, nombre}`), `publicado`, `estado_validacion` (`{codigo, texto}`), `aciertos` (nulo), `numeros_acertados` (`[entero]`, nulo), `numeros_oficiales` (nulo), `conjunto` (nulo; solo Premio Extra), `elegibilidad` (`"participa"` \| `"excluida"` \| nulo), `excluida_por` (nombre, nulo), `resultado_premio` (`{codigo, texto}`, nulo), `categoria` (nulo), `importe` (decimal, nulo), `importe_pendiente`, `avisos` (`[texto]`), `actualizado_el` (fecha, nulo: corrección del resultado oficial).

`SorteoDisponible`: `numero`, `fecha`, `modalidades: [{slug, nombre}]` (`servicios.concursos_disponibles`).

`GuardarJugada` (cuerpo de `POST /jugadas/` y `PUT /jugadas/{id}/`): `sorteo` (número), `numeros` (`[texto]`, como las casillas del formulario), `costo` (texto `1234,56` o `1234.56`, como el formulario), `confirmar_duplicado` (booleano). Errores `422` por campo con los textos de `JugadaForm` (`concurso` → `sorteo`, `numeros`, `costo`); `409` `jugada.duplicada` con `confirmar: true`; `409` `jugada.fija`; jugada ajena o inexistente → `404` con el mismo texto que la vista HTML ("La jugada no existe o no está disponible").

**Pantalla 4 — Resultados** (`resultados/views_publicas.py`, `consultas.vista_publica_concurso`)

`SorteoResumen`: `numero`, `fecha`, `completitud` (`{codigo, texto}` de `TEXTO_COMPLETITUD`).

`SorteoPublico`: `numero`, `fecha`, `completitud`, `admite_jugadas` (enlace "Registrar una jugada"), `modalidades: [ModalidadPublica]`.

`ModalidadPublica`: `slug`, `nombre`, `es_premio_extra`, `estado_numeros` (`{codigo, texto}` de `texto_estado_publico`, RN-20), `numeros` (`[entero]` o `null` si no está publicado), `conjunto` (solo Premio Extra, o `null`), `fuente_numeros` (`{descripcion, fecha_consulta}` o `null`), `revision_numeros`, `corregido_numeros` (fecha o `null`), `estado_premios`, `categorias: [{codigo, nombre, condicion, ganadores (nulo), importe_categoria, importe_individual, pozo_vacante_acumulado}]` (importes `Dato`: cadena decimal o `null` con estado "No disponible"), `sin_ganadores`, `fuente_premios`, `revision_premios`, `corregido_premios`. Solo lo **publicado** (vigente o en revisión): nada en borrador u observado.

`GET /sorteos/` devuelve todos los sorteos en una sola página (`paginas = 1`), como el listado HTML actual; `pagina` se acepta por compatibilidad. `GET /sorteos/ultimo/` responde `{ultimo: SorteoPublico | null, pendiente: SorteoResumen | null}` (`pendiente`: el sorteo más reciente sin publicar, [001] RN-25); sin sorteos publicados, `ultimo` es `null` (la pantalla muestra su estado vacío) en lugar del `404` de la tabla. `GET /sorteos/buscar/`: `numero` existente → `SorteoPublico` con `redirigir: "/resultados/{numero}/"`; inexistente → `200` con `elementos: []` y `mensaje` (`resultados.concurso_inexistente`); `fecha` → `Pagina<SorteoResumen>` o `mensaje` (`resultados.fecha_sin_concursos`); `422` por campo (`numero`: `admin.numero_sorteo_invalido`; `fecha`: mensaje de `error_de_fecha`).

**Pantalla 5 — Sesión y cuentas**: sin DTO nuevos (`Sesion`, ya aprobado). `POST /sesion/`: `{correo, contrasena, pendiente?}` → `Sesion` + `Set-Cookie`; con `pendiente` válido, además `reanudar: {ruta, campos}` (lo que la pantalla destino precarga). `POST /cuentas/`: `{correo, contrasena}` con los errores de `RegistroForm` por campo (`contrasena_repetida` se acepta y se ignora: el formulario de [001] no la pide). Credenciales incorrectas, cuenta bloqueada y correo existente responden `422` con el mensaje del catálogo en `detail` (no `401`, reservado para "sin sesión").

**Pantalla 6 — Administración de sorteos** (`resultados/views_admin.py`)

`SorteoAdmin`: `numero`, `fecha`, `completitud` (`{codigo, texto}`), `filas: [{modalidad: {slug, nombre}, numeros: EstadoBloqueAdmin, premios: EstadoBloqueAdmin}]` (`_filas`).
`EstadoBloqueAdmin` (`_info_bloque`): `estado` (`{codigo, texto}`), `en_trabajo` (booleano), `correccion_en_preparacion`, `acciones: [codigo]` (las que la vista HTML ofrece: `cargar`, `observar`, `resolver`, `publicar`, `revision`, `quitar_revision`, `corregir`).
`PanelSorteo` = `SorteoAdmin` + `modalidades_elegibles`, `tiene_publicaciones`, `modificable`.
`BorradorNumeros`: `n1`…`n6` (texto), `fuente_descripcion`, `fuente_fecha_consulta` (nulo), `motivo_correccion` (nulo), `es_correccion`.
`BorradorPremios`: `categorias: [{codigo, nombre, ganadores, importe_categoria, importe_individual, pozo_vacante_acumulado}]` (texto, como el formulario), `aciertos_categoria_ganadora` (nulo; opciones según la modalidad), `sin_ganadores`, fuente y motivo como en números.
`RevisionPublicacion`: `bloqueantes: [texto]`, `advertencias: [texto]`, `requiere_cotejo` (booleano), `datos` (los números o las categorías a cotejar). Cuerpo de publicar: `{confirmar_advertencias, cotejo}`.
`CambioRegistrado` (`historial_cambios`): `momento` (fecha y hora), `usuario` (correo), `modalidad`, `bloque`, `accion` (texto), `motivo` (nulo).

### Revisión contra el esquema (T231, 22/11/2026)

Las 30 rutas de `contratos/openapi.json` están en este documento. Nombres de los DTO en el esquema que difieren del texto: `Frecuencias` → `FrecuenciasDTO`, `Jugada` → `JugadaDTO`, `Pagina<ExtraccionResumen>` → `PaginaExtracciones`, `Pagina<SorteoResumen>` → `PaginaSorteos`, `Formulario` de administración → `FormularioDTO`; los estados con código y texto se llaman `EstadoPublico` (Resultados), `EstadoJugada` y `CodigoComparacion` (Mis jugadas) y `EstadoAdmin` (Administración). Django Ninja nombra cada esquema por su clase y `tests/api/test_contratos_exportados.py` exige que no se repitan entre módulos.

## 3. Ejemplo de error

```json
{
  "type": "https://quini6.local/problemas/validacion",
  "title": "Datos inválidos",
  "status": 422,
  "detail": "Hay campos con errores.",
  "errores": [
    { "campo": "hasta", "codigo": "ext.inicio_posterior", "mensaje": "La fecha de inicio no puede ser posterior a la fecha de finalización" }
  ]
}
```

## 4. Pruebas exigidas por operación

- Matriz de acceso: visitante, usuario, otro usuario y administrador contra cada operación (extiende `tests/integration/test_matriz_acceso.py` de [001]).
- CSRF: toda mutación sin `X-CSRFToken` responde `403`.
- Idempotencia: repetir la clave no duplica (dos jugadas, dos extracciones) ni falla (eliminar).
- Paridad con la vista HTML: mismos datos y mismos mensajes para el mismo caso (NFR-009).
