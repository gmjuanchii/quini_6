# Modelo de datos (Fase 1): QUINI_6 — MVP v0

**Fecha**: 13/11/2026 | **Plan**: [plan.md](plan.md) | **Decisiones**: [research.md](research.md) (R-06, R-08)

Convenciones:

- Los tipos se expresan en términos de Django (`DecimalField`, `SmallIntegerField`, etc.).
- Todo importe es `Decimal(16,2)`. `null` significa **"no disponible"**: nunca se completa con un valor estimado (Const. VIII, RN-27).
- Los números del Quini 6 se guardan como enteros de 0 a 45, **ordenados de forma ascendente** en `n1`…`n6`. La restricción `n1 < n2 < … < n6` garantiza a la vez el orden y que los seis sean distintos (RN-02, RN-03, RN-14). La presentación con dos dígitos (`07`) se hace al mostrarlos (RN-01).
- Las fechas y horas se guardan en UTC y se muestran en `America/Argentina/Buenos_Aires` (Const. VII). `fecha_sorteo` es una fecha sin hora (RN-12).

---

## Catálogos fijos (enumeraciones en código, no tablas)

### `Modalidad`

| Código | Nombre visible | ¿Extracción propia? | Categorías predefinidas (RN-26) |
|--------|----------------|---------------------|---------------------------------|
| `PRIMER_SORTEO` | Tradicional – Primer Sorteo | Sí | `PRIMER` (6), `SEGUNDO` (5), `TERCER` (4) — RN-49 |
| `LA_SEGUNDA` | Tradicional – La Segunda | Sí | `PRIMER` (6), `SEGUNDO` (5), `TERCER` (4) — RN-50 |
| `REVANCHA` | Revancha | Sí | `UNICO` (6) — RN-51 |
| `SIEMPRE_SALE` | Siempre Sale | Sí | `GANADORA` (aciertos según el extracto) — RN-52 |
| `PREMIO_EXTRA` | Premio Extra | **No** (RN-15) | `GANADORA` (6, 5 o 4, o sin ganadores) — RN-31 |

El administrador no puede agregar ni quitar categorías (AC-2.13). Al cargar premios, el formulario muestra exactamente las categorías de la modalidad.

### `EstadoVersion`

`BORRADOR`, `OBSERVADO`, `PUBLICADA`, `REEMPLAZADA`.

---

## Entidades persistidas

### `cuentas.Usuario` — Cuenta de usuario

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `email` | `EmailField`, único | Se normaliza a minúsculas. Es el identificador de la cuenta (FR-015, AC-3.3). |
| `password` | hash | Hasher de Django, nunca en texto plano (Const. IV). Mínimo 8 caracteres (NFR-005). |
| `es_administrador` | `bool`, por defecto `False` | Solo se cambia con los comandos `otorgar_admin` y `quitar_admin` (RN-37). |
| `fecha_alta` | `DateTimeField` | |
| `intentos_fallidos` | `SmallInteger`, por defecto 0 | Vuelve a 0 con cada inicio de sesión exitoso. |
| `bloqueado_hasta` | `DateTimeField`, `null` | Se fija a ahora + 15 min al llegar a 5 fallos consecutivos (NFR-005, AC-3.6). |

No se guarda ningún otro dato personal (RN-39).

### `resultados.Concurso`

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `numero` | `PositiveIntegerField`, único, indexado | RN-11 y RN-21. Si ya existe: "El concurso N.º X ya existe" (AC-2.2). |
| `fecha_sorteo` | `DateField`, indexado | RN-12. |
| `creado_por` | FK → Usuario (PROTECT) | |
| `creado_en` | `DateTimeField` | |

Relaciones: 1 → N `ModalidadConcurso` (las modalidades aplicables, RN-13); 1 → N `Jugada`; 1 → N `RegistroCambio`.

Validaciones al crear o modificar: al menos una modalidad aplicable. Si se marca Premio Extra, también deben marcarse Primer Sorteo, La Segunda y Revancha (**P-06, a confirmar**). Las modificaciones posteriores siguen **P-05, a confirmar**.

### `resultados.ModalidadConcurso` — modalidad aplicable de un concurso

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `concurso` | FK → Concurso (CASCADE) | |
| `modalidad` | `Modalidad` | Único junto con `concurso`. |
| `numeros_en_revision` | `bool` | Solo puede ser `True` si existe una `VersionNumeros` `PUBLICADA` (RN-16). |
| `numeros_motivo_revision` | texto | Obligatorio cuando `numeros_en_revision` es `True` (AC-7.1). |
| `premios_en_revision` | `bool` | Igual que `numeros_en_revision`, para el bloque de premios. |
| `premios_motivo_revision` | texto | |

Cada `ModalidadConcurso` tiene dos **bloques** que se publican por separado (RN-18):

- **Bloque de números**: versiones en `VersionNumeros`. No existe para `PREMIO_EXTRA` (RN-15).
- **Bloque de premios**: versiones en `VersionPremios`.

Las modalidades de una jugada **no se guardan**: son las `ModalidadConcurso` de su concurso (RN-05). Por eso, si cambian las modalidades del concurso, cambian las de sus jugadas.

### `resultados.VersionNumeros`

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `modalidad_concurso` | FK → ModalidadConcurso (PROTECT) | Solo para modalidades con extracción propia. |
| `n1` … `n6` | `SmallIntegerField` | `0 ≤ n ≤ 45` y `n1 < n2 < … < n6` (`CheckConstraint`). |
| `fuente_descripcion` | texto, obligatorio para publicar | Por ejemplo, "Extracto oficial del concurso N.º 3215" (RN-17 b, AC-1.15). |
| `fuente_fecha_consulta` | `DateField`, obligatorio para publicar | |
| `estado` | `EstadoVersion` | |
| `motivo_observacion` | texto | Obligatorio al pasar a `OBSERVADO` (AC-2.8). |
| `es_correccion` | `bool` | `True` si se creó para corregir una versión publicada (RN-23). |
| `motivo_correccion` | texto | Obligatorio si `es_correccion` (AC-7.2). |
| `creada_por`, `creada_en` | FK, fecha y hora | |
| `actualizada_por`, `actualizada_en` | FK, fecha y hora | Última edición del borrador. |
| `publicada_por`, `publicada_en` | FK, fecha y hora, `null` | Se completan al publicar. `publicada_en` de una corrección es la fecha de "Corregido el …" (RN-24). |
| `reemplazada_en` | fecha y hora, `null` | |

Restricciones de integridad (únicas parciales):

- Como máximo una versión `PUBLICADA` por `modalidad_concurso`.
- Como máximo una versión en trabajo (`BORRADOR` u `OBSERVADO`) por `modalidad_concurso`.

### `resultados.VersionPremios`

Tiene los mismos metadatos que `VersionNumeros` (fuente, estado, observación, corrección, autoría y fechas), más estos campos:

| Campo | Tipo | Reglas |
|-------|------|--------|
| `aciertos_categoria_ganadora` | `SmallIntegerField`, `null` | Solo en Siempre Sale (0 a 6, RN-22) y en Premio Extra (6, 5 o 4). `null` = no publicada o no disponible. |
| `sin_ganadores` | `bool` | Solo en Premio Extra. Excluye un valor en `aciertos_categoria_ganadora` (RN-26, RN-31 c). |

Relación: 1 → N `PremioCategoria`. Siempre hay exactamente una fila por categoría predefinida de la modalidad.

### `resultados.PremioCategoria`

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `version_premios` | FK → VersionPremios (CASCADE) | |
| `categoria` | código del catálogo | Único junto con `version_premios`. Debe pertenecer a la modalidad. |
| `ganadores` | `PositiveIntegerField`, `null` | `null` = "no disponible". Valor negativo: error bloqueante (RN-22). |
| `importe_categoria` | `Decimal(16,2)`, `null`, ≥ 0 | Importe destinado a la categoría. |
| `importe_individual` | `Decimal(16,2)`, `null`, ≥ 0 | Solo el valor publicado oficialmente. **Nunca se calcula** (RN-27). |
| `pozo_vacante_acumulado` | `Decimal(16,2)`, `null`, ≥ 0 | Pozo vacante o acumulado (AC-1.7, AC-1.10). |

### `resultados.RegistroCambio` — auditoría (solo agregado)

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | |
| `concurso` | FK → Concurso (PROTECT) | |
| `modalidad` | `Modalidad`, `null` | `null` para las acciones sobre el concurso. |
| `bloque` | `CONCURSO`, `NUMEROS` o `PREMIOS` | |
| `accion` | `CREAR_CONCURSO`, `MODIFICAR_CONCURSO`, `GUARDAR_BORRADOR`, `OBSERVAR`, `RESOLVER_OBSERVACION`, `PUBLICAR`, `MARCAR_REVISION`, `QUITAR_REVISION` (**P-01**), `INICIAR_CORRECCION`, `PUBLICAR_CORRECCION` | |
| `valor_anterior` | JSON, `null` | Copia del valor publicado anterior. Los importes se guardan como texto decimal (`"1500.50"`) para no perder precisión. |
| `valor_nuevo` | JSON, `null` | |
| `autor` | FK → Usuario (PROTECT) | |
| `fecha_hora` | `DateTimeField` | |
| `motivo` | texto | Obligatorio en `OBSERVAR`, `MARCAR_REVISION`, `QUITAR_REVISION`, `INICIAR_CORRECCION` y `PUBLICAR_CORRECCION`. |
| `fuente` | texto | Descripción y fecha de la fuente vigente al momento del cambio. |

No hay ninguna operación de actualización ni de borrado sobre esta tabla (NFR-006, AC-7.3).

### `jugadas.Jugada`

| Campo | Tipo | Reglas |
|-------|------|--------|
| `id` | PK | Las rutas usan el `id`. La pertenencia se verifica siempre en el servidor (RN-36). |
| `usuario` | FK → Usuario (CASCADE), indexado | RN-04. |
| `concurso` | FK → Concurso (PROTECT) | RN-04 y RN-07. |
| `n1` … `n6` | `SmallIntegerField` | Las mismas restricciones que `VersionNumeros` (RN-01 a RN-03). |
| `costo` | `Decimal(16,2)`, obligatorio, ≥ 0 | RN-09 y AC-4.16. |
| `creada_en`, `modificada_en` | fecha y hora | |

Índice: `(usuario, concurso)`. **No** hay restricción de unicidad sobre los números: se permiten jugadas idénticas si el usuario las confirma (RN-06).

---

## Estados derivados (no se guardan)

### Estado de un bloque según RN-16, visto por el administrador

| Versiones existentes del bloque | `en_revision` | Estado RN-16 |
|---------------------------------|---------------|--------------|
| Ninguna | — | **Sin cargar** |
| Solo una en `BORRADOR` | — | **Borrador** |
| Solo una en `OBSERVADO` | — | **Observado** |
| Una `PUBLICADA` (con o sin corrección en trabajo) | `False` | **Publicado** (+ "corrección en preparación" si hay una versión en trabajo) |
| Una `PUBLICADA` (con o sin corrección en trabajo) | `True` | **En revisión** |

### Transiciones permitidas (servicio de resultados)

```text
Sin cargar ──guardar──▶ Borrador ──observar(motivo)──▶ Observado
                          ▲  │                            │
                          │  └──────publicar (RN-17)──┐   │
                          └──resolver observación─────┼───┘
                                                      ▼
                     ┌──────────────────────────── Publicado ◀──────────────┐
                     │ marcar revisión(motivo)        │                    │
                     ▼                                │ iniciar corrección │ publicar corrección
                En revisión ──iniciar corrección──────┴──▶ (versión en     │ (RN-17 + motivo + fuente)
                     │                                     trabajo, es_correccion) ─┘
                     └──quitar revisión(motivo) [P-01]──▶ Publicado
```

- Para publicar se exige RN-17: versión en `BORRADOR` (no `OBSERVADO`), fuente completa, sin errores bloqueantes de RN-22, advertencias confirmadas y la casilla "Confirmo que cotejé esta información con la fuente".
- Al publicar una corrección, la versión que estaba `PUBLICADA` pasa a `REEMPLAZADA`, la corrección pasa a `PUBLICADA` y `en_revision` vuelve a `False` (**P-01**). Todo ocurre en una sola transacción, con bloqueo de la fila `ModalidadConcurso`.
- **No existe** la transición "despublicar". Una vez publicado, un bloque siempre tiene una versión visible. Por eso los cortes de RN-07 y RN-08 son definitivos.

### Estado público de cada modalidad (RN-20)

| Bloque de números | Lo que ve el público |
|-------------------|----------------------|
| Sin cargar | "Resultado pendiente" |
| Borrador u Observado | "Pendiente de validación" (D-12: solo el estado, nunca los valores) |
| Publicado | Números publicados |
| En revisión | Números publicados + "Información en revisión" |
| Con alguna corrección publicada | + "Corregido el dd/mm/aaaa" (fecha de la última corrección publicada; D-13 = A) |

El bloque de premios sigue la misma lógica. Mientras no esté publicado, se muestra "Información de premios pendiente de publicación" (AC-1.8). Ese mismo texto reemplaza el importe individual de una categoría publicada sin ese dato (AC-1.9).

**Premio Extra** no tiene bloque de números: el estado de su conjunto se deriva de los bloques de números de Primer Sorteo, La Segunda y Revancha. Si alguno está sin cargar, es "Resultado pendiente"; si no, y alguno está en Borrador u Observado, es "Pendiente de validación"; si los tres están publicados, se muestra el conjunto, con "Información en revisión" si alguno lo está. Nunca se muestra un conjunto parcial. Su bloque de premios se muestra según la regla general (RN-18, RN-20).

### Completitud del concurso (RN-19)

Elementos del concurso: el bloque de números de cada modalidad aplicable con extracción propia, más el bloque de premios de cada modalidad aplicable.

- **Sin resultados**: ningún elemento publicado. En el listado se muestra "Resultados pendientes".
- **Incompleto**: al menos uno publicado y al menos uno sin publicar.
- **Completo**: todos publicados.

### Concurso abierto para jugadas (RN-07 y RN-08)

`admite_jugadas(concurso)` es verdadero si **ninguna** `VersionNumeros` `PUBLICADA` pertenece a una de sus modalidades. Una versión `REEMPLAZADA` implica que hubo una publicada, así que también lo cierra. La misma condición define si una jugada es editable o eliminable.

### Últimos resultados (RN-25)

- **Concurso de "últimos resultados"**: el de `fecha_sorteo` más reciente con al menos un elemento publicado.
- **Concurso actual pendiente**: el de `fecha_sorteo` más reciente si no tiene elementos publicados y es posterior al anterior.

### Conjunto de Premio Extra (RN-31)

Se calcula como la unión de los números publicados vigentes de Primer Sorteo, La Segunda y Revancha: entre 6 y 18 números distintos. **No** incluye Siempre Sale.

### Comparación de jugada (RN-29)

Es el resultado de `dominio.comparacion.comparar_jugada(...)`, calculado en cada consulta a partir de la versión vigente de la jugada y de las versiones `PUBLICADA` vigentes. Ver [contracts/dominio.md](contracts/dominio.md).

### Estadística de frecuencia (RN-40 a RN-46)

Es el resultado de `dominio.estadisticas.calcular_frecuencias(...)` sobre las `VersionNumeros` `PUBLICADA` (incluidas las que están en revisión) de las modalidades aplicables del período.

---

## Correspondencia con las entidades de la spec

| Entidad de la spec | Implementación |
|--------------------|----------------|
| Cuenta de usuario | `cuentas.Usuario` |
| Concurso | `resultados.Concurso` + `ModalidadConcurso` (modalidades aplicables) |
| Resultado de modalidad | `ModalidadConcurso` + `VersionNumeros` |
| Categoría de premio | `VersionPremios` + `PremioCategoria` |
| Conjunto de números del Premio Extra | Derivado (dominio) |
| Fuente de información | Campos `fuente_*` de cada versión (valor incorporado en la versión) + `RegistroCambio.fuente` |
| Registro de cambio | `resultados.RegistroCambio` + las propias versiones `REEMPLAZADA` |
| Jugada | `jugadas.Jugada` |
| Comparación de jugada | Derivada (dominio) |
| Estadística de frecuencia | Derivada (dominio) |
