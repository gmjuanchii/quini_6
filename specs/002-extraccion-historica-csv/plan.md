# Plan de implementación (Implementation Plan): Extracción histórica de sorteos y exportación CSV

**Rama**: `002-extraccion-historica-csv` | **Fecha**: 19/11/2026 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación funcional aprobada de `specs/002-extraccion-historica-csv/spec.md`, con el relevamiento [analisis-fuentes.md](analisis-fuentes.md) y las respuestas del responsable a las cuatro preguntas de la planificación del 19/11/2026 (spec → Clarifications → "Session 2026-11-19 (planificación)").

**Marco normativo**: [Constitución QUINI_6 v1.1.0](../../.specify/memory/constitution.md). Se apoya en el plan de [001](../001-quini6-mvp/plan.md), cuyas decisiones siguen vigentes y se citan como `[001] R-xx`.

## Resumen (Summary)

Un administrador elige un período de hasta 12 meses y la aplicación recupera de tres fuentes públicas secundarias (F1, F2 y F3) los resultados y premios de cada sorteo. Consulta siempre todas las fuentes que cubren el sorteo, normaliza sus datos a una estructura común, los valida, los compara sin elegir valores cuando difieren y clasifica cada sorteo. *(Desde el 20/11/2026, F2 y F3 se consultan siempre y F1 solo como respaldo y desempate; ver "Cambios posteriores a la aprobación".)* Al terminar, muestra un resumen y el detalle de cada sorteo con la procedencia de cada dato, y ofrece un CSV versionado que será el contrato de una futura ingesta. **Nada llega a las tablas de resultados ni de jugadas.**

**Enfoque técnico.** Se mantiene el monolito Django de [001] y se agrega **una aplicación `extracciones`** y **un subpaquete puro `dominio/extraccion/`**, sin dependencias nuevas:

- La extracción la ejecuta un **proceso trabajador** (`manage.py procesar_extracciones`) que usa la base como cola. Así no se bloquea la solicitud web, el avance sobrevive a las recargas y un único proceso garantiza el ritmo máximo de una consulta cada 2 s por sitio ([002] R-01, R-03).
- Las consultas usan `urllib` y el HTML se lee con `html.parser`, ambos de la biblioteca estándar, con **un intérprete por fuente** que solo extrae textos. Toda regla de negocio (normalización, validación, consolidación, clasificación, resumen y CSV) vive en funciones puras probadas sin red ni base ([002] R-02, R-04, R-07).
- Cada extracción se **conserva** con sus sorteos e intentos, y el CSV se genera **una sola vez** al terminar y se guarda, así que toda descarga posterior es idéntica ([002] R-08, R-09).

El detalle está en [research.md](research.md).

## Contexto técnico (Technical Context)

| Aspecto | Decisión | Ref. |
|---------|----------|------|
| **Lenguaje y versión** | Python 3.12, Django 5.2 LTS (sin cambios) | [001] R-01 |
| **Dependencias principales** | Las de [001], **sin agregar ninguna**. Biblioteca estándar: `urllib.request`, `html.parser`, `json`, `csv`, `concurrent.futures`, `threading` y, solo en pruebas, `http.server` | [002] R-15 |
| **Almacenamiento** | PostgreSQL 16 en producción y SQLite en desarrollo y pruebas. Tres tablas nuevas en `extracciones`, con `JSONField` sin consultas dentro del JSON | [001] R-03, [002] R-08 |
| **Pruebas** | `pytest` + `pytest-django`: unitarias del dominio y de los intérpretes con copias de páginas, integración con un cliente HTTP falso, matriz de acceso, aislamiento y CSV; verificación manual con un servidor de fuentes de prueba y con las fuentes reales | [002] R-11, R-12 |
| **Plataforma objetivo** | La de [001]: servidor Linux con HTTPS, más un proceso trabajador como servicio del sistema | [001] R-16, [002] R-01 |
| **Tipo de proyecto** | Aplicación web monolítica renderizada en el servidor, con un comando de gestión de larga duración | [001] R-02 |
| **Objetivos de rendimiento** | SC-007: un mes en menos de 2 min y 12 meses en menos de 10 min. Estimado: unos 25 s y unos 4,5 min | [002] R-14 |
| **Restricciones** | Una consulta cada 2 s por sitio como máximo, sin eludir protecciones (NFR-005). Límite de espera de 10 s y ninguna falla detiene la extracción (NFR-006). Importes en `Decimal` (NFR-007). Contenido de las fuentes no confiable (NFR-010). Sin escrituras fuera de `extracciones` (RN-41). Pantalla en es-AR; CSV en formato técnico (NFR-001, D-11) | [002] R-02, R-03, R-09, R-13 |
| **Escala y alcance** | Unos 104 sorteos por año, hasta 3 fuentes por sorteo, pocos administradores. 5 rutas, 4 pantallas, 3 modelos y 1 comando | [contracts/rutas.md](contracts/rutas.md) |

No quedan marcas `NEEDS CLARIFICATION`. Los cuatro puntos funcionales detectados se consultaron y ya están en la spec. Los textos ‡ y las interpretaciones I-01 a I-08, que el plan dejó pendientes de confirmación, los aprobó el responsable el 19/11/2026 en el análisis, junto con I-09 e I-10 (ver "Puntos a confirmar").

## Verificación contra la Constitución (Constitution Check)

*Compuerta: se evaluó antes de la Fase 0 y se reevaluó después del diseño de la Fase 1.*

| Principio | Cómo lo cumple el plan | Antes | Después del diseño |
|-----------|------------------------|:-----:|:------------------:|
| **I. SDD (no negociable)** | Cada ruta, modelo, función y texto se vincula a un FR, RN o AC. Las cuatro ambigüedades funcionales detectadas se preguntaron y se registraron en la spec antes de diseñar. Los textos que el plan propone (‡) y las interpretaciones técnicas (I-xx) se elevan para confirmación y no se dan por aprobados. No se agrega cancelación, eliminación, programación automática ni edición de fuentes (Fuera del alcance). *Enmienda 20/11/2026*: la eliminación de extracciones terminadas se agregó por pedido del responsable, registrado en la spec (D-24). La ampliación sobre [001] ("integraciones con fuentes externas") queda autorizada por la aprobación de esta spec. | ✅ | ✅ |
| **II. Trazabilidad** | [contracts/rutas.md](contracts/rutas.md), [contracts/dominio.md](contracts/dominio.md), [contracts/csv.md](contracts/csv.md) y [contracts/mensajes.md](contracts/mensajes.md) citan el requisito de cada elemento. [quickstart.md](quickstart.md) vincula cada paso con sus AC. | ✅ | ✅ |
| **III. Acceso público / funciones personales** | La feature es solo de administración. No cambia ninguna ruta pública ni personal. | ✅ | ✅ |
| **IV. Aislamiento y seguridad** | `administrador_requerido` en las cinco rutas, en GET y POST, incluida la descarga; `no-store`; CSRF. Las direcciones consultadas salen solo de las fichas, nunca del contenido recibido. El HTML se escapa al mostrarse. Sin secretos nuevos. | ✅ | ✅ |
| **V. Sin apuestas ni pagos** | No hay ninguna operación económica. El CSV no incluye el precio del cartón. | ✅ | ✅ |
| **VI. Criterios verificables por personas no técnicas** | El servidor de fuentes de prueba permite provocar cada caso de las historias 2 a 4 y comprobarlo en la pantalla y en la planilla ([quickstart.md](quickstart.md) §5). | ✅ | ✅ |
| **VII. Español de Argentina** | Pantalla con los filtros `fecha_ar`, `fecha_hora_ar`, `pesos` y `dos_digitos`, y el catálogo de mensajes. El CSV usa formato técnico porque el responsable confirmó que no es contenido visible (D-11), con textos en español. | ✅ | ✅ |
| **VIII. Exactitud de las reglas y datos** | Ningún importe se calcula (RN-18). Las cuatro situaciones de RN-20 son un tipo explícito y nunca se convierten en cero. Rótulos por equivalencia exacta. Sorteos anteriores al 18/06/2024 con aviso. Premio Extra sin números propios. Ninguna fuente prevalece. *Enmienda 20/11/2026 (D-14 a D-21)*: las fuentes tienen prioridad (F2 → F3 → F1) y F1 desempata; el pozo de una categoría con ganadores se calcula como importe × ganadores y los números de Pozo Extra como la unión de las tres modalidades. Son excepciones aprobadas y siempre llevan la marca "Calculado" (research R-16, R-17). | ✅ | ✅ |
| **IX. Integridad y trazabilidad** | Cada intento guarda fuente, dirección y fecha y hora; cada dato consolidado guarda sus fuentes; discrepancias y observaciones con el valor original. Extracciones inmutables al terminar y archivo fijo (desde D-24 se pueden eliminar enteras, nunca modificar). `Decimal` de punta a punta. | ✅ | ✅ |
| **X. Experiencia visual** | Mismo CSS de [001], tablas apilables desde 360 px, estados con texto y color, estados de en curso, éxito, advertencia, error y vacío (NFR-011). Solo las pantallas de [contracts/rutas.md](contracts/rutas.md). | ✅ | ✅ |
| **XI. Simplicidad** | Sin dependencias ni servicios nuevos. La única pieza nueva de infraestructura es el trabajador, justificada en "Seguimiento de complejidad". | ✅ | ✅ |

**Resultado de la compuerta: APROBADA.** No hay violaciones. Los puntos P-01 a P-03 no son violaciones: se elevan al responsable como exige la Constitución.

## Estructura del proyecto (Project Structure)

### Documentación (esta funcionalidad)

```text
specs/002-extraccion-historica-csv/
├── spec.md              # Especificación funcional (aprobada; Clarifications de la planificación incorporadas)
├── analisis-fuentes.md  # Relevamiento de fuentes del 18/11/2026
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas (R-01 a R-15) e interpretaciones (I-01 a I-08)
├── data-model.md        # Fase 1: tipos del dominio, modelos y estados
├── quickstart.md        # Fase 1: puesta en marcha y escenarios de validación
├── contracts/
│   ├── rutas.md         # Rutas nuevas, acceso y respuestas
│   ├── mensajes.md      # Textos visibles (†, ‡)
│   ├── csv.md           # Contrato del archivo, versión 1.0
│   ├── fuentes.md       # Fichas de F1, F2, F3 y enlace a F0
│   ├── dominio.md       # Funciones puras y casos de prueba obligatorios
│   └── comandos.md      # Comando del trabajador
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2: lo genera /speckit-tasks (no lo crea este comando)
```

### Código fuente (raíz del repositorio)

Solo se muestran los archivos nuevos o modificados.

```text
pyproject.toml                       # MODIFICADO: paquetes extracciones, extracciones.fuentes, dominio.extraccion
.env.example                         # MODIFICADO: QUINI6_FUENTE_F1_URL, F2, F3 comentadas
quini6/
├── settings.py                      # MODIFICADO: INSTALLED_APPS + "extracciones"; lectura de las URL de prueba
└── urls.py                          # MODIFICADO: include("extracciones.urls")
dominio/extraccion/                  # NUEVO: reglas puras (sin Django)
├── tipos.py                         # Dato, DatosFuente, DatoConsolidado, SorteoConsolidado, ...
├── periodo.py                       # RN-01 a RN-04
├── identificacion.py                # RN-05
├── normalizacion.py                 # RN-11 a RN-20, RN-24, RN-26
├── consolidacion.py                 # RN-22, RN-23, RN-27 a RN-30, RN-32
├── clasificacion.py                 # RN-31
├── resumen.py                       # RN-10, RN-33
└── archivo_csv.py                   # RN-34 a RN-39, RN-43
extracciones/                        # NUEVO: aplicación Django
├── models.py                        # Extraccion, SorteoExtraido, IntentoConsulta
├── migrations/0001_initial.py
├── fuentes/                         # adaptadores sin Django
│   ├── fichas.py                    # fichas F1, F2, F3 y enlace F0 (contracts/fuentes.md)
│   ├── html.py                      # árbol mínimo sobre html.parser
│   ├── f1.py · f2.py · f3.py        # HTML → PaginaCruda, listados → referencias
├── cliente_http.py                  # urllib, límite de espera, limitador por sitio, RN-08
├── servicios.py                     # iniciar_extraccion, procesar_extraccion (orquestación)
├── serializacion.py                 # tipos del dominio ↔ JSON (Decimal como texto)
├── consultas.py                     # listado, página, detalle, archivo
├── forms.py                         # período (delegando en dominio.extraccion.periodo)
├── views.py                         # 5 vistas con administrador_requerido
├── urls.py
└── management/commands/procesar_extracciones.py
templates/extracciones/              # NUEVO
├── inicio.html                      # formulario o avance propio + "Extracciones anteriores"
├── extraccion.html                  # en curso / resumen / sin sorteos
├── _avance.html                     # bloque reemplazable por JS, con la barra <progress> (D-26)
├── _dato.html                       # valor o estado de un dato del detalle
├── eliminar.html                    # confirmación de eliminación (D-24)
└── sorteo.html                      # detalle por sorteo
templates/resultados/admin/listado.html  # MODIFICADO: enlace «Extracción histórica de sorteos» (AC-1.1)
static/js/avance-extraccion.js       # NUEVO: mejora progresiva ([002] R-10)
static/css/app.css                   # MODIFICADO: estados, menú ⋮ (D-24) y barra de avance (D-26)

tests/
├── unit/extraccion/                 # dominio puro e intérpretes
├── integration/test_extraccion_*.py # recorridos, acceso, aislamiento, CSV
├── fixtures/fuentes/                # copias recortadas de páginas reales
└── fuentes_prueba/                  # servidor de fuentes de prueba y escenarios (nunca se despliega)
```

**Decisión de estructura**: una aplicación Django nueva, como el resto de los módulos (`CLAUDE.md`: una app por módulo), porque la extracción tiene modelos, vistas y ciclo de vida propios y no comparte tablas con `resultados`. Las reglas van en `dominio/extraccion/` para mantener la separación de [001] R-07. Los intérpretes de HTML quedan en `extracciones/fuentes/` porque son adaptadores de infraestructura (conocen el HTML de cada sitio) y no reglas de negocio; tampoco importan Django.

## Correspondencia entre historias y código

| Historia | Código principal | FR |
|----------|------------------|----|
| US1 Ejecutar y ver el resumen | `views.py`, `forms.py`, `servicios.py`, `dominio/extraccion/periodo.py`, `identificacion.py`, `resumen.py`, plantillas, `avance-extraccion.js` | FR-001 a FR-004, FR-012, FR-013, FR-015 |
| US2 Varias fuentes con respaldo | `cliente_http.py`, `fuentes/`, `servicios.py` | FR-005 a FR-007 |
| US3 Normalizar y validar | `dominio/extraccion/normalizacion.py`, `fuentes/fichas.py` | FR-008, FR-009, FR-011 |
| US4 Discrepancias y procedencia | `dominio/extraccion/consolidacion.py`, `clasificacion.py`, `sorteo.html` | FR-010, FR-012 |
| US5 CSV unificado | `dominio/extraccion/archivo_csv.py`, vista de descarga | FR-014, FR-015 |
| US6 Acceso y sin ingesta | `administrador_requerido`, prueba estructural de imports, pruebas de aislamiento | FR-001, FR-016 |

## Orden de construcción sugerido (insumo para `/speckit-tasks`)

1. **Base**: aplicación `extracciones`, modelos y migración, rutas con `administrador_requerido` y la matriz de acceso de las cinco rutas (US6, SC-005).
2. **Dominio puro y sus pruebas**: tipos, período, normalización, consolidación, clasificación, resumen y CSV, con los casos de [contracts/dominio.md](contracts/dominio.md). Es la parte de mayor riesgo funcional (Const. VIII) y no depende de la red.
3. **Fuentes**: relevar la estructura real de F1, F2 y F3 y completar las marcas "(relevar)" de [contracts/fuentes.md](contracts/fuentes.md); guardar las copias de páginas; intérpretes y sus pruebas; cliente HTTP con límite de espera, limitador por sitio y la tabla de RN-08.
4. **US1 + US3 + US5 con una sola fuente** (P1): identificación, trabajador, pantalla, avance, resumen, detalle y descarga. Es el primer incremento que se puede mostrar (prueba independiente de US1).
5. **US2 + US4** (P2): las tres fuentes en paralelo, respaldo, discrepancias, "Combina fuentes", "Sin corroborar" y "Requiere mantenimiento".
6. **Servidor de fuentes de prueba** y sus escenarios ([002] R-11), para la verificación manual.
7. **Transversal**: pruebas de aislamiento (SC-004, AC-6.3 a AC-6.5), revisión de NFR-002, NFR-003 y NFR-011, verificación completa con [quickstart.md](quickstart.md), incluidas las fuentes reales (SC-003, SC-006, SC-007, SC-008).
8. **Mantenimiento de la documentación**: Actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec (p. ej. '[002] ...'). No incluyas entradas por incluir, asegúrate siempre de que es información transversal y relevante para el proyecto que pueden aprovechar futuras features.

## Cambios posteriores a la aprobación (20/11/2026 y 21/11/2026)

El responsable pidió cambios después de usar la extracción. Cada uno está en la spec (Clarifications), tiene sus tareas en [tasks.md](tasks.md) (fases 11 a 14) y enmienda este plan como se indica:

| Decisión | Cambio | Impacto en el diseño | Detalle |
|----------|--------|----------------------|---------|
| D-14, D-21 | Prioridad F2 → F3 → F1; F1 solo de respaldo y desempate; 2 de 3 coincidentes resuelven | `ORDEN_FUENTES` y `FUENTES_RESPALDO`; `consultar_sorteo` en dos pasos; resultado `NO_REQUERIDA`; `diferencia_tolerada` de tipo `MAYORIA` | research R-03, R-16; data-model |
| D-15 | Nombres de las modalidades en la extracción ("Tradicional", "Pozo Extra"…) | `nombre_modalidad` en la pantalla y en el CSV, distinto de `Modalidad.nombre` de [001] | contracts/csv.md |
| D-16, D-19 | Pozo calculado (importe × ganadores) y números de Pozo Extra calculados | `DatoConsolidado.calculo`; columna `numeros_pozo_extra` (CSV v2.0) | research R-17; data-model |
| D-17 | Tolerancia del 1 % y redondeo a pesos | `diferencia_tolerada` de tipo `CENTAVOS`, informativa; I-04 reemplazada | research R-17, I-04 |
| D-18, D-20 | Corrección de importes mal cargados | Normalización con la observación informativa `obs.importe_corregido` | research R-17; contracts/mensajes.md |
| D-22 | Sin "Se acumula" ni importe trasladado | Se quitan del dominio y del CSV (v3.0) | contracts/csv.md; data-model |
| D-23 | Detalle sin fuentes por dato | `sorteo.html` y `consultas.py` | contracts/rutas.md |
| D-24 | Eliminar extracciones terminadas | Nueva ruta `/<id>/eliminar/` (GET + POST → 303), `servicios.eliminar_extraccion`, `eliminar.html`, menú ⋮ con `<details>` | research R-08; contracts/rutas.md; data-model |
| D-25, D-27 | Fechas con calendario nativo y escritas con el teclado | `<input type="date">` con `max`; sin forzar `showPicker()` (se quitó `selector-fecha.js`) | research R-10 |
| D-26 | Barra de progreso del avance | `<progress>` nativo en `_avance.html`, actualizado por el mismo `avance-extraccion.js`; estilos `.barra-avance` | research R-10 |

## Puntos a confirmar con el responsable (no bloquean el plan)

| ID | Tema | Detalle | Hay que resolverlo antes de |
|----|------|---------|-----------------------------|
| P-01 | Textos ‡ | Observaciones y motivos que la spec pide sin fijar su redacción ([contracts/mensajes.md](contracts/mensajes.md)). **Resuelto el 19/11/2026 (análisis)**: aprobados tal como están | — |
| P-02 | Interpretaciones I-01 a I-08 | Casos límite de reglas aprobadas: 29/02, fecha en el borde del período, "Combina fuentes", umbral de centavos, "aportó", pozo con ganadores en conflicto, reanudación del trabajador y cobertura de F1 ([research.md](research.md)). **Resuelto el 19/11/2026 (análisis)**: aprobadas, junto con I-09 e I-10 | — |
| P-03 | Datos a relevar | Dirección exacta de la página oficial de extractos (F0), que [analisis-fuentes.md](analisis-fuentes.md) no registra, y la estructura real de las páginas | El paso 3 |

Observación sobre la documentación (spec, "Relación con la especificación 001", punto 9): `CLAUDE.md` remite a `specs/README.md`, que no existe. Queda fuera del alcance de este plan; se menciona para que el responsable decida.

## Seguimiento de complejidad (Complexity Tracking)

No hay violaciones de la Constitución. Se documentan los elementos que superan el mínimo, como pide Const. XI:

| Elemento | Por qué se necesita | Alternativa más simple descartada porque |
|----------|---------------------|------------------------------------------|
| Proceso trabajador aparte (`procesar_extracciones`) | Una extracción dura minutos (SC-007) y el ritmo de NFR-005 es por sitio y global. El avance debe sobrevivir a recargas (AC-1.11). | Ejecutar en la solicitud excede el límite de `gunicorn`; un hilo en la vista no garantiza el ritmo global con varios procesos ni sobrevive a un reinicio. |
| Consultas en paralelo por sitio (3 hilos, solo HTTP) | En paralelo, cada sorteo tarda lo que la respuesta más lenta (unos 2,5 s). En serie tarda la suma de las tres: con respuestas de 2 a 3 s, 12 meses superan los 10 min de SC-007. NFR-005 permite consultar sitios distintos a la vez. | Consultas en serie: más simples, pero SC-007 dependería de la velocidad de los sitios. |
| Consolidado en `JSONField` | El detalle por dato (valor, estado, fuentes, discrepancias) es una estructura anidada que solo se lee completa y nunca se filtra. | Tablas por dato, discrepancia y observación: multiplican modelos y consultas sin que nadie las use por separado. |
| Constructor de árbol propio sobre `html.parser` | Leer tablas del HTML sin agregar dependencias (`CLAUDE.md`). | `beautifulsoup4`/`lxml`: más cómodas, pero son dependencias nuevas para páginas simples. |
| Servidor de fuentes de prueba en `tests/` | La spec exige verificar desde la pantalla casos de falla, demora, estructura y discrepancias (Supuestos, Const. VI), imposibles de provocar con los sitios reales. | Probar solo con pruebas automatizadas: no cumple Const. VI. |
