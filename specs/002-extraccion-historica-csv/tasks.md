---

description: "Lista de tareas de la feature 002: Extracción histórica de sorteos y exportación CSV"
---

# Tareas (Tasks): Extracción histórica de sorteos y exportación CSV

**Entrada**: documentos de diseño de `specs/002-extraccion-historica-csv/`

**Prerrequisitos**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Pruebas**: se incluyen. Las exigen la Constitución (XI: pruebas automatizadas de las reglas de negocio y de los recorridos principales), `CLAUDE.md` (`pytest` en verde) y el plan ([002] R-12, [contracts/dominio.md](contracts/dominio.md) → "Casos de prueba obligatorios"). Dentro de cada historia, las pruebas se escriben primero y deben fallar antes de implementar.

**Organización**: por historia de usuario. Las historias P1 van en el orden US1 → US3 → US5 → US6 y luego las P2, US2 → US4, siguiendo el "Orden de construcción sugerido" del plan.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: se puede hacer en paralelo (archivos distintos, sin dependencias pendientes).
- **[USn]**: historia de usuario de [spec.md](spec.md) a la que pertenece la tarea.
- "(requiere T005)": la tarea usa textos ‡ de [contracts/mensajes.md](contracts/mensajes.md) o interpretaciones I-xx de [research.md](research.md) que deben estar confirmados antes de implementarla.

## Convenciones para todas las tareas

- Código, nombres y textos en español de Argentina. Los textos visibles se copian **literalmente** de [contracts/mensajes.md](contracts/mensajes.md) y se definen como constantes en el módulo que los usa (como `SIN_PERMISO` en `cuentas/decoradores.py`).
- Docstrings y pruebas citan los IDs con el prefijo de la spec: `[002] RN-17`, `[002] AC-3.5`, `[001] RN-37`.
- `dominio/extraccion/` y `extracciones/fuentes/` **no importan Django**. Errores como valores, no excepciones. Importes siempre `Decimal`, nunca `float`.
- Ningún módulo de `extracciones/` ni de `dominio/extraccion/` importa modelos de `resultados` ni de `jugadas` (RN-41).
- Las plantillas nunca usan `|safe` sobre datos de las fuentes (NFR-010). Pantalla con los filtros `fecha_ar`, `fecha_hora_ar`, `pesos` y `dos_digitos` de `quini6/templatetags/formato_ar.py`.
- Las pruebas no hacen consultas reales a internet: usan el cliente HTTP falso de T018.

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: crear la aplicación, los paquetes y la configuración, y cerrar los puntos pendientes de confirmación del plan.

- [X] T001 Crear el esqueleto de paquetes con archivos `__init__.py` vacíos: `extracciones/__init__.py`, `extracciones/migrations/__init__.py`, `extracciones/fuentes/__init__.py`, `extracciones/management/__init__.py`, `extracciones/management/commands/__init__.py`, `dominio/extraccion/__init__.py`, `tests/unit/extraccion/__init__.py` (evita choques de nombre con `tests/unit/test_resumen.py`) y `tests/fuentes_prueba/__init__.py`; crear `extracciones/apps.py` con `ExtraccionesConfig` (`name = "extracciones"`, `default_auto_field` igual al de `resultados/apps.py`) y la carpeta `tests/fixtures/fuentes/`
- [X] T002 [P] Agregar `"extracciones"`, `"extracciones.fuentes"` y `"dominio.extraccion"` a `[tool.setuptools] packages` en `pyproject.toml`, sin agregar ninguna dependencia ([002] R-15)
- [X] T003 Agregar `"extracciones"` a `INSTALLED_APPS` y leer con `_env` las variables `QUINI6_FUENTE_F1_URL`, `QUINI6_FUENTE_F2_URL` y `QUINI6_FUENTE_F3_URL` en un diccionario `QUINI6_FUENTES_URL_BASE = {"F1": ..., "F2": ..., "F3": ...}` donde una variable vacía queda como `None` (se usan las direcciones reales) en `quini6/settings.py` ([002] R-05)
- [X] T004 [P] Documentar en `.env.example` las tres variables `QUINI6_FUENTE_F1_URL`, `QUINI6_FUENTE_F2_URL` y `QUINI6_FUENTE_F3_URL`, comentadas y sin valor, con la aclaración "solo para el servidor de fuentes de prueba (tests/fuentes_prueba)" ([contracts/comandos.md](contracts/comandos.md))
- [X] T005 Consultar al responsable del proyecto los puntos P-01 (textos ‡ de `specs/002-extraccion-historica-csv/contracts/mensajes.md`) y P-02 (interpretaciones I-01 a I-08 de `specs/002-extraccion-historica-csv/research.md`; I-09 e I-10 ya se aprobaron el 19/11/2026 en el análisis, pero el texto ‡ `obs.error_interprete` de I-09 sigue pendiente), sin darlos por aprobados; registrar la respuesta en esos dos archivos (quitar la marca ‡ de los textos aprobados o reemplazar su redacción, y marcar cada I-xx como confirmada o corregida). Bloquea las tareas marcadas "(requiere T005)" (Const. I)

---

## Fase 2: Base (prerrequisitos que bloquean todas las historias)

**Propósito**: relevamiento de las fuentes, tipos del dominio, fichas, modelos, serialización, lector de HTML, cliente HTTP y dobles de prueba.

**⚠️ CRÍTICO**: ninguna historia puede empezar hasta terminar esta fase.

- [X] T006 Relevar la estructura real de F1, F2 y F3 (P-03 del plan) consultando cada página a mano, como máximo una consulta cada 2 s por sitio y sin eludir protecciones (NFR-005): selectores HTML del número, la fecha, los rótulos de bloque, los números y las filas de premios de cada fuente; formato del bloque de datos embebido de F3; profundidad real del listado de F3; marcadores de una página anti-robots si alguno aparece; y la dirección de la página general de extractos de la Lotería de Santa Fe (F0). Antes de relevar, volver a leer las reglas para robots y las condiciones de uso de los tres sitios: si alguno publicó restricciones nuevas, detenerse y consultar al responsable (NFR-005, D-13). Completar cada marca "(relevar)" en `specs/002-extraccion-historica-csv/contracts/fuentes.md`. Si algo contradice `specs/002-extraccion-historica-csv/analisis-fuentes.md`, detenerse y consultar al responsable antes de seguir (RN-10, D-07); la dirección de F0 se confirma con el responsable
- [X] T007 Guardar copias recortadas de páginas reales relevadas en T006 en `tests/fixtures/fuentes/f1/`, `tests/fixtures/fuentes/f2/` y `tests/fixtures/fuentes/f3/`: el listado de cada fuente y al menos dos sorteos completos por fuente del mismo número (uno con alguna categoría vacante y otro con ganadores), con Premio Extra y Siempre Sale; en F1, un sorteo con el pozo de Premio Extra "N millones de pesos"; un `LEEME.md` en `tests/fixtures/fuentes/` indica la fecha del relevamiento y la dirección original de cada copia (depende de T006)
- [X] T008 [P] Crear los tipos del dominio en `dominio/extraccion/tipos.py` según [data-model.md](data-model.md) → "Catálogos fijos" y "Tipos del dominio", como `dataclass(frozen=True)` y `Enum`, reutilizando `Modalidad`, `ORDEN_MODALIDADES` y `FECHA_VIGENCIA_REGLAS` de `dominio/tipos.py`: `Dato` con las variantes `Valor(v)` ("`v` es `int`, `Decimal`, `date`, `bool` o un conjunto de números"), `NO_DISPONIBLE`, `NO_CORRESPONDE` y `SIN_DETERMINAR` ("un `Dato` nunca se crea a partir de un valor ausente convertido en cero"); `Fuente` (`F1`, `F2`, `F3`); `ResultadoIntento` con los siete códigos y textos de RN-08 y la propiedad `es_fallido` ("todos menos `OBTENIDO` y `FUERA_DE_COBERTURA`"); `EstadoSorteo` en orden de precedencia (`NO_RECUPERADO` → `CON_INCONSISTENCIAS` → `PARCIAL` → `RECUPERADO`) con sus textos; `EstadoExtraccion` (`EN_CURSO`, `FINALIZADA`, `CON_ADVERTENCIAS`, `SIN_SORTEOS`) con sus textos; `ClaveCategoria` (`PRIMER`, `SEGUNDO`, `TERCER`, `UNICO`, `GANADORA`, `ACIERTOS_N`) con nombres y aciertos de la tabla "Categorías por modalidad" y una función `categorias_esperadas(modalidad)` ("`ACIERTOS_N` nunca es esperada"); `PaginaCruda`, `BloqueCrudo` y `FilaPremioCruda` (solo textos: `numero_texto`, `fecha_texto`, `rotulo`, `numeros_textos`, `aciertos_texto`, `ganadores_texto`, `importe_texto`, `pozo_texto`); `DatosFuente`, `DatosModalidadFuente` (`numeros: Numeros | None`), `DatosCategoriaFuente` (con `texto_original`); `DatoConsolidado` (`dato`, `fuentes`, `sin_corroborar`, `discrepancia`); `Discrepancia` (`VALOR_DISTINTO` "Valor distinto", `OMISION` "Omisión", `CENTAVOS` "Diferencia de centavos o redondeo"); `Observacion` (`codigo`, `texto`, `fuente`, `es_inconsistencia`, `informativa`); `SorteoConsolidado`, `ModalidadConsolidada` (`informada`, `numeros`, `categorias`) y `CategoriaConsolidada` (`estado_pozo` ∈ "Con ganadores", "Vacante", "Pendiente", "Sin determinar"; `importe_trasladado` siempre `NO_DISPONIBLE`); y `Ficha` (estructura sin valores). Sin importar Django
- [X] T009 Crear las fichas de F1, F2 y F3 en `extracciones/fuentes/fichas.py` con los valores de `specs/002-extraccion-historica-csv/contracts/fuentes.md` completado en T006: nombre en el archivo (dominio del sitio), dirección base real, plantillas de dirección del listado y del sorteo (F1: `/quini6/sorteo-{N}-del-dia-{dd-mm-aaaa}.htm`, `exige_fecha_en_direccion=True`), cobertura (F2 desde el 2211 del 17/12/2014, F3 desde el 2787 del 09/09/2020, F1 por presencia en su listado, I-08), tabla exacta de rótulos de modalidad (comparación sin distinguir mayúsculas y con espacios normalizados; "LA SEGUNDA DEL QUINI 6 REVANCHA" es Revancha), significado de la columna de importe (RN-17), datos que publica y datos que **no publica por diseño** (pozo destinado con ganadores, "Se acumula según la fuente", importe trasladado; F1 no publica aciertos de Premio Extra; F2 y F3 no publican el pozo de Premio Extra y el texto fijo "85 millones de pesos" de F2 se ignora), códigos HTTP de "sorteo inexistente" (F1 y F3: 404 → `NO_ENCONTRADO`; F2: 500 → `NO_DISPONIBLE_O_NO_ENCONTRADO`) y marcadores anti-robots; la constante `PRIMER_CUBIERTO = (2211, date(2014, 12, 17))` y `ENLACE_EXTRACTO_OFICIAL` (F0). Una función `obtener_fichas(urls_base)` recibe las direcciones de reemplazo como parámetro (el módulo no importa Django) (depende de T006 y T008)
- [X] T010 [P] Crear el árbol mínimo de HTML sobre `html.parser.HTMLParser` en `extracciones/fuentes/html.py`: nodos con etiqueta, atributos, hijos y texto; búsqueda por etiqueta, clase e id; texto normalizado de un nodo; recorrido de tablas, filas y celdas; obtención del texto crudo de un bloque `<script>` de datos (para F3) sin ejecutarlo; nunca sigue enlaces (NFR-010, [002] R-04). Sin importar Django
- [X] T011 [P] Probar el árbol de HTML en `tests/unit/extraccion/test_html.py`: tablas anidadas, etiquetas sin cerrar, entidades HTML, texto con espacios irregulares, bloque de script de datos y HTML malformado sin excepción
- [X] T012 Crear los modelos `Extraccion`, `SorteoExtraido` e `IntentoConsulta` en `extracciones/models.py` según [data-model.md](data-model.md) → "Entidades persistidas", con choices tomados de los enums de T008. `Extraccion`: `creada_por` FK → `cuentas.Usuario` (PROTECT); `desde`, `hasta` `DateField`; `estado` indexado; `iniciada_en` `DateTimeField` indexado; `finalizada_en` `DateTimeField` `null` ("Obligatorio si el estado es final"); `numero_desde`, `numero_hasta` `PositiveIntegerField` `null`; `cobertura_desde` `DateField` `null`; `resumen` `JSONField` `null`; `archivo_csv` `TextField` vacío ("Vacío si el estado es `SIN_SORTEOS`"); `nombre_archivo` `CharField`; `version_contrato` `CharField` (`1.0`); restricciones `UniqueConstraint(creada_por, condition=estado = EN_CURSO)`, `CheckConstraint(desde <= hasta)`, `CheckConstraint` "`finalizada_en` es nulo si y solo si `estado = EN_CURSO`" y `CheckConstraint` "`numero_desde <= numero_hasta` cuando ambos existen"; propiedades derivadas `total_identificados`, `procesados` e `identificando`. `SorteoExtraido`: `extraccion` FK (CASCADE), `numero` `PositiveIntegerField` "Único junto con `extraccion`", `fecha` `DateField` `null`, `estado` indexado, `combina_fuentes` y `sin_corroborar` `bool`, `consolidado` `JSONField`, `procesado_en` `DateTimeField`. `IntentoConsulta`: `sorteo` FK (CASCADE), `fuente` "Único junto con `sorteo`", `resultado`, `url` `CharField(500)` vacío ("Vacía si es 'Fuera de cobertura'"), `consultado_en` `DateTimeField` `null`, `datos` `JSONField` `null`, `observaciones` `JSONField`. Sin funciones exclusivas de un motor (depende de T008)
- [X] T013 Generar la migración con `python manage.py makemigrations extracciones` en `extracciones/migrations/0001_initial.py` y comprobar que `python manage.py migrate` funciona en SQLite (depende de T012)
- [X] T014 Crear la conversión entre tipos del dominio y JSON en `extracciones/serializacion.py`: `Dato` con su estado explícito (`{"estado": "valor" | "no_disponible" | "no_corresponde" | "sin_determinar", "valor": ...}`), `Decimal` como texto con `dominio.importes.a_texto_decimal` (nunca `float`), fechas ISO, conjuntos de números como listas ordenadas, y funciones para `DatosFuente`, `Observacion`, `SorteoConsolidado` y el resumen ([002] R-08) (depende de T008)
- [X] T015 [P] Probar la ida y vuelta de la serialización en `tests/unit/extraccion/test_serializacion.py`: `Decimal("1100000000.00")` sin pérdida, `Valor(0)` distinto de `NO_DISPONIBLE`, `NO_CORRESPONDE` y `SIN_DETERMINAR` conservados, ningún `float` en el JSON (depende de T014)
- [X] T016 Crear el cliente HTTP y el limitador en `extracciones/cliente_http.py` ([002] R-02, R-03): `ClienteHttp.obtener(fuente, url) -> RespuestaHttp(codigo | None, texto | None, error | None, consultado_en)` solo con `GET` vía `urllib.request`, límite de espera de 10 s, certificados TLS verificados, redirecciones solo dentro del mismo sitio, `User-Agent` fijo `QUINI6-extraccion-historica/1.0`, respuestas de más de 2 MB descartadas como error, codificación desde `Content-Type` o `<meta charset>` con UTF-8 por omisión, sin reintentos y sin cambiar encabezados ni usar intermediarios ante 403 o 429 (NFR-005); `LimitadorPorSitio` seguro entre hilos (`threading.Lock`) que garantiza al menos `INTERVALO_SEGUNDOS = 2` entre el inicio de dos consultas al mismo sitio, constante fija en el código y no configurable por variable de entorno; el reloj y la espera se inyectan para las pruebas
- [X] T017 [P] Probar el cliente HTTP en `tests/unit/extraccion/test_cliente_http.py` con un `http.server` local levantado en un hilo de la prueba (sin internet): límite de espera vencido → error, más de 2 MB → error, redirección a otro sitio rechazada, codificación tomada del encabezado, `User-Agent` enviado, un 403 consultado una sola vez; y el limitador con reloj falso: dos consultas al mismo sitio separadas por 2 s y consultas a sitios distintos sin espera (depende de T016)
- [X] T018 Crear los dobles de prueba en `tests/extraccion_falsos.py`: `ClienteHttpFalso` que responde por dirección con (código, archivo de `tests/fixtures/fuentes/` o texto, error simulado de límite de espera) y registra las direcciones pedidas; `LimitadorSinEspera`; y una función `procesar_pendientes(cliente)` que ejecuta el trabajador una vez con ese cliente (depende de T016)

**Punto de control**: base lista. Las historias pueden empezar.

---

## Fase 3: Historia de usuario 1 — Ejecutar una extracción y ver su resumen (Prioridad: P1) 🎯 MVP

**Objetivo**: un administrador elige un período, inicia la extracción y ve el avance, el resumen, el detalle por sorteo y el listado de extracciones anteriores (FR-001 a FR-004, FR-007, FR-012, FR-013, FR-015).

**Prueba independiente**: con una sola fuente configurada (F2), un administrador extrae un período de dos semanas y verifica el avance, el resumen y el detalle por sorteo.

### Pruebas de la historia 1 (escribir primero; deben fallar)

- [X] T019 [P] [US1] Probar `validar_periodo` y `mismo_dia_anio_siguiente` en `tests/unit/extraccion/test_periodo.py`: AC-1.3 (inicio posterior → `INICIO_POSTERIOR`), AC-1.4 (vacía y "31/02/2026" → `FECHA_INVALIDA` en el campo correspondiente), AC-1.5 (fin posterior a hoy → `FIN_FUTURA`), AC-1.6 (01/01/2026–01/01/2027 → `PERIODO_LARGO`; 01/01/2026–31/12/2026 válido), RN-01 (período de un solo día válido) e I-01 (del 29/02/2024 se puede pedir hasta el 28/02/2025 y no hasta el 01/03/2025) (requiere T005: I-01)
- [X] T020 [P] [US1] Probar `identificar_sorteos` en `tests/unit/extraccion/test_identificacion.py` con referencias y una función `fecha_de` falsas: AC-1.7 (3422 del 01/11/2026 a 3426 del 15/11/2026 → 5 identificados, incluidos el primer y el último día), AC-1.10 (`SinSorteos`), AC-1.16 (3423 sin fecha en ninguna fuente queda identificado), AC-1.17 (inicio 01/06/2014 → primer número 2211 y `cobertura_desde` 17/12/2014), un sorteo especial en un día no habitual incluido, un número cuya fecha cae fuera del período excluido, I-02 (incluido si alguna fuente informa una fecha dentro del período) y un período más antiguo que los listados resuelto pidiendo fechas por número; ninguna fecha se deduce del calendario (requiere T005: I-02)
- [X] T021 [P] [US1] Probar el intérprete de F2 en `tests/unit/extraccion/test_fuente_f2.py` con las copias de `tests/fixtures/fuentes/f2/`: el detalle produce una `PaginaCruda` con los textos sin interpretar de número, fecha, rótulos, números y filas de premios; el listado produce referencias (número, texto de fecha); una página sin número ni fecha reconocibles se informa como no reconocida sin excepción
- [X] T022 [P] [US1] Probar la normalización base en `tests/unit/extraccion/test_normalizacion.py` con la ficha de F2: página completa → `OBTENIDO` con las cinco modalidades y los números como conjunto ordenado; número o fecha irreconocibles → `ESTRUCTURA_NO_RECONOCIDA` sin datos (RN-10); categoría con 0 ganadores → importe como `pozo_destinado` e `importe_individual` `NO_CORRESPONDE`; con ganadores → `importe_individual` y `pozo_destinado` `NO_DISPONIBLE`; ganadores no disponibles → ambos `NO_DISPONIBLE`; falta un dato que la ficha declara → `INCOMPLETO` con la observación de qué falta (AC-2.5)
- [X] T023 [P] [US1] Probar la consolidación con una sola fuente en `tests/unit/extraccion/test_consolidacion.py`: cada dato informado queda `Valor` con `fuentes=(F2,)` y `sin_corroborar=True` (RN-32); dato no informado → `NO_DISPONIBLE` con `fuentes` vacía; siempre las cinco modalidades y sus categorías esperadas; `importe_trasladado` siempre `NO_DISPONIBLE`; `estado_pozo` derivado según RN-19; `reglas_no_verificadas` verdadero para el 17/06/2024 y falso para el 18/06/2024 (RN-25)
- [X] T024 [P] [US1] Probar `clasificar` en `tests/unit/extraccion/test_clasificacion.py`: precedencia de RN-31 (`NO_RECUPERADO` si ninguna fuente aportó datos válidos; `CON_INCONSISTENCIAS` con una discrepancia o una observación `es_inconsistencia`; `PARCIAL` si falta un dato esperado; `RECUPERADO` si no), el pozo de una categoría con ganadores no es esperado (AC-3.6), un importe `NO_DISPONIBLE` impide `RECUPERADO` (AC-3.8), una modalidad no informada impide `RECUPERADO` (AC-3.12), "Combina fuentes" y "Sin corroborar" no cambian el estado, y los motivos explican por qué no quedó `RECUPERADO`; I-10: con todas las fuentes que lo cubren en "No encontrado" o "No disponible o no encontrado", el motivo es "Ninguna fuente informa este número de sorteo"; con alguna en "No disponible" o "Estructura no reconocida", los motivos son el resultado de cada fuente
- [X] T025 [P] [US1] Probar `resumir` en `tests/unit/extraccion/test_resumen.py`: los cuatro estados suman los identificados (AC-1.8), `a_revisar` con número, fecha si se conoce, estado y motivos (AC-1.9), `huecos` solo con los números que son hueco según I-10 y no con los "No recuperado" por fallas de las fuentes (AC-1.16), `cobertura_desde` (AC-1.17), resultado global `FINALIZADA` solo si todos están `RECUPERADO` y `CON_ADVERTENCIAS` en otro caso (RN-33)
- [X] T026 [P] [US1] Probar el recorrido de la historia 1 en `tests/integration/test_extraccion_us1.py` con `ClienteHttpFalso` y solo F2: el listado de `/administracion/concursos/` tiene el enlace «Extracción histórica de sorteos» y la pantalla muestra "Fecha de inicio", "Fecha de finalización" e "Iniciar extracción" (AC-1.1); cada error de período muestra su texto literal, conserva las fechas y no crea ninguna `Extraccion` (AC-1.3 a AC-1.6); un período válido redirige con 303 a `/administracion/extracciones/<id>/`, que muestra "Extracción en curso", el período y "Identificando los sorteos del período…" (AC-1.2); con sorteos ya procesados muestra "N de M sorteos procesados" y el detalle de un sorteo ya procesado se puede abrir mientras la extracción sigue en curso ([contracts/rutas.md](contracts/rutas.md)); un segundo `POST` y la recarga de la pantalla llevan a la misma extracción sin formulario ni otra extracción (AC-1.11); tras `procesar_pendientes`, el resumen informa identificados, los cuatro estados, las fuentes utilizadas, el resultado global y la lista a revisar (AC-1.7 a AC-1.9), el hueco (AC-1.16) y la cobertura (AC-1.17); un período sin sorteos muestra "No se identificaron sorteos en el período consultado" (AC-1.10); el detalle muestra por fuente el resultado, la dirección y la fecha y hora de consulta, cada dato con sus fuentes y el enlace "Ver extracto oficial (Lotería de Santa Fe)" (AC-1.12, AC-1.13); "Extracciones anteriores" lista de la más reciente a la más antigua con quién la ejecutó, fecha y hora de inicio, período y estado, y otro administrador abre el resumen y el detalle (AC-1.14, AC-1.15); un número que no pertenece a la extracción da 404 con "La página que buscás no existe"
- [X] T027 [P] [US1] Probar el comando en `tests/integration/test_extraccion_comando.py` con `call_command("procesar_extracciones", "--una-vez")` y el cliente falso inyectado: procesa las extracciones en curso por orden de `iniciada_en`; reanuda una extracción con sorteos ya guardados sin duplicarlos y repitiendo las consultas del sorteo a medias con una nueva fecha y hora (I-07); I-09 (a): una excepción del intérprete de una fuente deja ese intento "Estructura no reconocida" con "La página de la fuente no se pudo interpretar" y los datos se toman de las demás; I-09 (b): una excepción en otra parte del tratamiento deja el sorteo "No recuperado" con "Error inesperado al procesar el sorteo", la extracción continúa, el avance llega al total y los cuatro estados suman los identificados (NFR-006, RN-33); imprime una línea al iniciar y otra al terminar cada extracción con su número y su resultado global (requiere T005: I-07)

### Implementación de la historia 1

- [X] T028 [P] [US1] Implementar `validar_periodo(inicio_texto, fin_texto, hoy)` y `mismo_dia_anio_siguiente(fecha)` en `dominio/extraccion/periodo.py`: textos `dd/mm/aaaa`, devuelve `Periodo(desde, hasta)` o la lista de `ErrorPeriodo` (`FECHA_INVALIDA` por campo, `INICIO_POSTERIOR`, `FIN_FUTURA`, `PERIODO_LARGO`) con los textos de `ext.fecha_invalida`, `ext.inicio_posterior`, `ext.fin_futura` y `ext.periodo_largo` (RN-01 a RN-04) (requiere T005: I-01)
- [X] T029 [P] [US1] Implementar `identificar_sorteos(periodo, referencias, fecha_de, primer_cubierto) -> Identificacion | SinSorteos` en `dominio/extraccion/identificacion.py` según [002] R-06 y [contracts/dominio.md](contracts/dominio.md): primer y último número con fecha informada dentro del período, estimación de dos sorteos por semana solo para elegir qué número pedir, búsqueda que avanza o retrocede según la fecha informada, `cobertura_desde` cuando el inicio es anterior a `primer_cubierto` (RN-05) (requiere T005: I-02)
- [X] T030 [P] [US1] Implementar el intérprete de F2 en `extracciones/fuentes/f2.py` con los selectores relevados en T006: `interpretar_sorteo(html) -> PaginaCruda | NoReconocida` y `interpretar_listado(html) -> list[(numero_texto, fecha_texto)]`; solo extrae textos, no interpreta valores ni lanza excepciones ante HTML inesperado (R-04)
- [X] T031 [US1] Implementar la base de `normalizar(pagina, ficha, numero_pedido, fecha_pedida) -> (ResultadoIntento, DatosFuente | None)` y `parsear_importe_fuente(texto)` (quita "$" y espacios y delega en `dominio.importes.parsear_pesos`) en `dominio/extraccion/normalizacion.py`: pasos 1, 2, 3, 4, 5 y 7 de [contracts/dominio.md](contracts/dominio.md) → `normalizacion.py` (número y fecha, rótulos por la tabla exacta de la ficha con `obs.rotulo_desconocido`, seis números válidos como conjunto, categorías del catálogo vigente de RN-14, ganadores según RN-15 y concepto del importe según RN-17 y RN-20, `INCOMPLETO` con `obs.falta`); reutiliza `dominio.numeros` para la validación de seis números (requiere T005: textos ‡)
- [X] T032 [P] [US1] Implementar la base de `consolidar(numero, intentos, fichas) -> SorteoConsolidado` en `dominio/extraccion/consolidacion.py`: datos coincidentes como `Valor` con la lista de fuentes, `sin_corroborar` si los informa una sola fuente (RN-32), `NO_DISPONIBLE` si ninguna, las cinco modalidades con `informada`, `numeros` `NO_CORRESPONDE` en Premio Extra (RN-12), `estado_pozo` (RN-19), `importe_trasladado` `NO_DISPONIBLE`, `reglas_no_verificadas` (RN-25) y `sin_corroborar` del sorteo
- [X] T033 [P] [US1] Implementar `clasificar(sorteo) -> (EstadoSorteo, motivos)` en `dominio/extraccion/clasificacion.py` según RN-31 y [contracts/dominio.md](contracts/dominio.md) → `clasificacion.py`; los motivos de un sorteo `NO_RECUPERADO` son "{fuente}: {resultado del intento}" y, si es un hueco según I-10 (todas las fuentes que lo cubren respondieron "No encontrado" o "No disponible o no encontrado"), `obs.sin_fuente` "Ninguna fuente informa este número de sorteo"
- [X] T034 [P] [US1] Implementar `resumir(identificacion, sorteos, intentos_por_fuente) -> Resumen` en `dominio/extraccion/resumen.py` con las claves de [data-model.md](data-model.md) → "Resumen guardado" (`identificados`, `por_estado`, `fuentes`, `huecos` según I-10, `cobertura_desde`, `a_revisar`) y el resultado global de RN-33
- [X] T035 [US1] Implementar `iniciar_extraccion(usuario, periodo)` y `procesar_extraccion(extraccion, cliente, fichas, limitador)` en `extracciones/servicios.py` ([002] R-01, R-06): `iniciar_extraccion` devuelve la extracción en curso del usuario si existe (y ante `IntegrityError` de la restricción única, la existente) o crea una `EN_CURSO`; `procesar_extraccion` lee los listados de las fuentes con intérprete, identifica con `identificar_sorteos` guardando en memoria las páginas de detalle obtenidas para reutilizarlas como intentos, guarda `numero_desde`, `numero_hasta` y `cobertura_desde` o termina en `SIN_SORTEOS` con `finalizada_en`; por cada número no procesado (I-07) consulta las fuentes que lo cubren (las que no, registran `FUERA_DE_COBERTURA` sin dirección ni fecha), normaliza, consolida y clasifica, y guarda `SorteoExtraido` (con `fecha` nula si la fecha consolidada no es un `Valor`) y todos sus `IntentoConsulta` en **una sola transacción**; al final guarda `resumen`, `estado` y `finalizada_en`. Errores inesperados según I-09 (NFR-006), registrados siempre en el log: (a) una excepción del intérprete de una fuente deja ese intento `ESTRUCTURA_NO_RECONOCIDA` con `obs.error_interprete` y las demás fuentes siguen; (b) una excepción en otra parte del tratamiento del sorteo deja el sorteo `NO_RECUPERADO` con el motivo `motivo.error_inesperado` "Error inesperado al procesar el sorteo", sin datos de ninguna fuente, guardado en su propia transacción, y la extracción continúa con el número siguiente. Un registro `INTERPRETES = {Fuente.F2: f2}` define las fuentes con intérprete (en esta historia, solo F2). `crear_cliente_y_fichas()` arma el cliente real y las fichas con `settings.QUINI6_FUENTES_URL_BASE`. Solo escribe en tablas de `extracciones` (RN-41) (requiere T005: I-07 y el texto ‡ `obs.error_interprete`; I-09 ya aprobada)
- [X] T036 [P] [US1] Implementar las lecturas en `extracciones/consultas.py`: listado de extracciones de la más reciente a la más antigua con `select_related("creada_por")` (AC-1.14), extracción en curso de un usuario, datos de la página de una extracción (avance, identificando, resumen deserializado, lista de sorteos con estado) y detalle de un sorteo con sus intentos deserializados; `Http404` si la extracción no existe o el número no pertenece a sus identificados
- [X] T037 [P] [US1] Implementar el formulario del período en `extracciones/forms.py` con los campos de texto "Fecha de inicio" y "Fecha de finalización" (`dd/mm/aaaa`); `clean()` delega en `dominio.extraccion.periodo.validar_periodo` con la fecha de hoy en `America/Argentina/Buenos_Aires`, ubica cada error junto a su campo o como error general y conserva los valores ingresados
- [X] T038 [US1] Implementar las vistas `inicio` (GET y POST), `extraccion` (GET) y `sorteo` (GET) con `@administrador_requerido` en `extracciones/views.py`, y las rutas `administracion/extracciones/`, `administracion/extracciones/<int:id>/` y `administracion/extracciones/<int:id>/sorteos/<int:numero>/` en `extracciones/urls.py`, incluidas desde `quini6/urls.py`; el `POST` válido redirige con 303 a la página de la extracción; con una extracción en curso, el `POST` lleva a ella sin crear otra ([contracts/rutas.md](contracts/rutas.md)) (depende de T035, T036 y T037)
- [X] T039 [P] [US1] Crear `templates/extracciones/inicio.html` (extiende `base.html`): título «Extracción histórica de sorteos», enlace de regreso a «Concursos», el formulario con `templates/_campo.html` o, si el administrador tiene una extracción en curso, su avance (`_avance.html`) y un enlace a ella; debajo, "Extracciones anteriores" como tabla apilable desde 360 px con quién la ejecutó, fecha y hora de inicio (`fecha_hora_ar`), período (`fecha_ar`) y estado como texto, cada una con enlace a su página
- [X] T040 [P] [US1] Crear `templates/extracciones/_avance.html`: región con `id` estable y `aria-live="polite"` con "Extracción en curso", el período y "Identificando los sorteos del período…" o "{n} de {m} sorteos procesados", y un atributo que indique que la extracción sigue en curso ([002] R-10, NFR-003)
- [X] T041 [P] [US1] Crear `templates/extracciones/extraccion.html`: en curso, incluye `_avance.html` y carga `static/js/avance-extraccion.js`; terminada, muestra "Extracción finalizada" o "Extracción finalizada con advertencias que requieren revisión", el aviso de cobertura `ext.sin_cobertura`, el aviso de huecos `ext.huecos`, el resumen con los rótulos de RN-33 ("Período consultado", "Sorteos identificados", "Recuperados", "Recuperados parcialmente", "Con inconsistencias", "No recuperados", "Fuentes utilizadas", "Sorteos aportados", "Intentos fallidos", "Sorteos que requieren revisión"), la lista a revisar y la lista de todos los sorteos con su estado y enlace a su detalle; sin sorteos, solo "No se identificaron sorteos en el período consultado". Los estados se comunican con texto y no solo con color (NFR-003, NFR-011) (requiere T005: `ext.huecos`)
- [X] T042 [P] [US1] Crear `templates/extracciones/sorteo.html`: por fuente, el texto del resultado del intento, la dirección consultada como texto y la fecha y hora (`fecha_hora_ar`); por modalidad y categoría, cada dato con su valor (`dos_digitos`, `pesos`, `fecha_ar`) o su estado de RN-20 ("No disponible", "No corresponde", "Sin determinar"), las fuentes que lo respaldan y la marca "Sin corroborar"; estado del sorteo e indicaciones "Combina fuentes" y "Reglas del período no verificadas"; y el enlace "Ver extracto oficial (Lotería de Santa Fe)" a `ENLACE_EXTRACTO_OFICIAL` con `target="_blank" rel="noopener noreferrer"` (AC-1.12, AC-1.13); sin `|safe`
- [X] T043 [P] [US1] Crear `static/js/avance-extraccion.js` como mejora progresiva ([002] R-10): cada 5 s pide la misma dirección, reemplaza solo el bloque de `_avance.html` y, cuando la respuesta ya no trae la marca de "en curso", reemplaza la página completa con el resumen; sin el bloque en la página no hace nada; sin dependencias
- [X] T044 [P] [US1] Agregar el enlace «Extracción histórica de sorteos» hacia `/administracion/extracciones/` en `templates/resultados/admin/listado.html`, sin tocar la navegación principal (AC-1.1, [contracts/rutas.md](contracts/rutas.md))
- [X] T045 [US1] Implementar el comando `procesar_extracciones` en `extracciones/management/commands/procesar_extracciones.py` según [contracts/comandos.md](contracts/comandos.md): toma las extracciones `EN_CURSO` por orden de `iniciada_en` y las procesa de a una con `crear_cliente_y_fichas()` y un único `LimitadorPorSitio` compartido; `--una-vez` procesa las pendientes y termina; sin el argumento revisa cada 2 s; imprime una línea por extracción iniciada y terminada con su número y su resultado global; docstring con la restricción de una sola instancia (depende de T035)

**Punto de control**: con F2, la historia 1 funciona y se puede demostrar sola.

---

## Fase 4: Historia de usuario 3 — Normalizar y validar números y premios (Prioridad: P1)

**Objetivo**: los datos de todas las fuentes quedan en la estructura común y validada, sin confundir pozo con premio individual ni dato desconocido con cero (FR-008, FR-009, FR-011).

**Prueba independiente**: con páginas de prueba con vacantes, ganadores, datos faltantes e importes inválidos, se comparan la pantalla y los valores esperados.

### Pruebas de la historia 3 (escribir primero; deben fallar)

- [X] T046 [P] [US3] Probar `parsear_importe_fuente` en `tests/unit/extraccion/test_importe_fuente.py`: "$ 1.100.000.000" → `Decimal("1100000000")`, "3.013.912", "12.060,13", "5.547,85", "494,443,71" → error con el texto original (RN-16), "55 millones de pesos" y "1,5 millones de pesos" → 55000000.00 y 1500000.00 solo con `permite_millones=True` y error sin él (RN-17), un importe sin decimales no recibe centavos estimados y ningún resultado es `float`
- [X] T047 [US3] Agregar a `tests/unit/extraccion/test_normalizacion.py` los casos de la historia 3 con las fichas de F1, F2 y F3: AC-3.1 ("SORTEO TRADICIONAL", "TRADICIONAL" y "Tradicional Primer Sorteo" → Tradicional – Primer Sorteo; "LA SEGUNDA DEL QUINI 6 REVANCHA" → Revancha); AC-3.2 ("02 01 39 13 10 38" y "01 - 02 - 10 - 13 - 38 - 39" → el mismo conjunto); AC-3.3 y AC-3.13 (Premio Extra sin números propios y observación si no coinciden con la unión de las tres extracciones de la misma fuente, también con repetidos en F2); AC-3.4 ("Vacante" con 1.100.000.000); AC-3.5 (18 ganadores y 3.013.912); AC-3.7; AC-3.8 ("494,443,71" → `NO_DISPONIBLE` y la observación «494,443,71»); AC-3.9 (número repetido, "46" y cinco números → descartados, `INCOMPLETO` y la observación con el motivo); AC-3.10 (Siempre Sale con 5 aciertos y 17 ganadores); RN-25 (sorteo del 17/06/2024 con una categoría fuera del catálogo → `ACIERTOS_N` "Categoría de N aciertos"; del 18/06/2024 → observación `obs.categoria_fuera_catalogo` y no se asigna); AC-3.14 (0 ganadores y "0,00" → `NO_CORRESPONDE`); AC-3.15 (`se_acumula` `NO_DISPONIBLE`); RN-17 (F1 "55 millones de pesos" → 55000000.00 con la observación informativa; F2 "85 millones de pesos" ignorado); RN-21 (F1 con número o fecha distintos de la dirección → `ESTRUCTURA_NO_RECONOCIDA`); RN-26 (Siempre Sale inválida, Premio Extra inválida, valor negativo y dos extracciones con los mismos seis números como advertencia); SC-002 (ningún importe es producto ni cociente de otros y ningún dato desconocido queda como 0 o vacante) (depende de T022)
- [X] T048 [US3] Agregar a `tests/unit/extraccion/test_consolidacion.py` los casos de `revisar_correlatividad` (RN-23: un número mayor con fecha anterior a la de uno menor agrega `obs.no_correlativo` con `es_inconsistencia=True` a ambos), de modalidad no informada por ninguna fuente (`informada=False`, AC-3.12) y de categoría con ganadores cuyo pozo `NO_DISPONIBLE` no genera discrepancia (AC-3.6) (depende de T023)
- [X] T049 [P] [US3] Probar la pantalla de la historia 3 en `tests/integration/test_extraccion_us3.py` con variantes editadas de las copias de F2 guardadas en `tests/fixtures/fuentes/f2/variantes/`: el detalle muestra "Tradicional – Primer Sorteo", 01, 02, 10, 13, 38, 39, "$ 1.100.000.000,00", "No corresponde", "Vacante", "$ 3.013.912,00", "No disponible", "Con ganadores", "Pendiente", "Importe con formato no reconocido: «494,443,71»", "Reglas del período no verificadas", "No informada por las fuentes" y "Se acumula según la fuente"; y el sorteo con el importe inválido no figura "Recuperado"

### Implementación de la historia 3

- [X] T050 [US3] Completar `dominio/extraccion/normalizacion.py`: `parsear_importe_fuente(texto, permite_millones=False)` con "N millones de pesos" (N entero o con coma decimal → N × 1.000.000 exactos) solo para el pozo de Premio Extra de F1 y la observación informativa `obs.pozo_premio_extra_texto`; `obs.importe_invalido` con el texto original (RN-16); `obs.concepto_importe` cuando la ficha no permite determinar el concepto (RN-17); control de RN-12 con `obs.premio_extra_no_coincide`; observaciones de RN-24 (`obs.numeros_cantidad`, `obs.numeros_repetido`, `obs.numeros_rango`); RN-25 (`ACIERTOS_N` antes del 18/06/2024 y `obs.categoria_fuera_catalogo` desde esa fecha); controles de RN-26 (`obs.siempre_sale_invalida`, `obs.premio_extra_invalida`, `obs.negativo`, `obs.extracciones_iguales` como advertencia); RN-21 (`obs.direccion_no_coincide` y `ESTRUCTURA_NO_RECONOCIDA` cuando la ficha exige fecha en la dirección); RN-20 ("0,00" con 0 ganadores → `NO_CORRESPONDE`) (requiere T005: textos ‡)
- [X] T051 [US3] Implementar `revisar_correlatividad(sorteos) -> list[SorteoConsolidado]` en `dominio/extraccion/consolidacion.py` con `obs.no_correlativo` "El número y la fecha no son correlativos con el sorteo N.º {N}" (RN-23) (requiere T005: texto ‡)
- [X] T052 [US3] En `extracciones/servicios.py`, al terminar de procesar los sorteos y antes de resumir, aplicar `revisar_correlatividad` a todos los `SorteoConsolidado` de la extracción, volver a clasificar los afectados y actualizar su `estado`, `consolidado` y motivos en una transacción (RN-23, [contracts/dominio.md](contracts/dominio.md))
- [X] T053 [US3] Completar `templates/extracciones/sorteo.html`: observaciones con su fuente y los textos originales entre « » (escapados), modalidad "No informada por las fuentes", categorías "Categoría de N aciertos", aciertos de la categoría ganadora de Siempre Sale y Premio Extra ("Sin ganadores"), números de Premio Extra como "No corresponde", "Se acumula según la fuente" e importe trasladado "No disponible"

**Punto de control**: las historias 1 y 3 funcionan con F2.

---

## Fase 5: Historia de usuario 5 — Descargar el CSV unificado (Prioridad: P1)

**Objetivo**: el administrador descarga un único CSV versionado con los datos consolidados, sus estados y su procedencia, siempre idéntico (FR-014, FR-015).

**Prueba independiente**: se descarga el archivo de una extracción terminada, se abre con una planilla y se compara con el resumen y el detalle de la pantalla.

### Pruebas de la historia 5 (escribir primero; deben fallar)

- [X] T054 [P] [US5] Probar `generar_csv` y `nombre_archivo` en `tests/unit/extraccion/test_archivo_csv.py` contra [contracts/csv.md](contracts/csv.md): los 26 encabezados exactos y en orden; `version_contrato` `1.0` en cada fila; fechas `AAAA-MM-DD`, fecha y hora de consulta `AAAA-MM-DD HH:MM:SS` en `America/Argentina/Buenos_Aires`, importes `1100000000.00`, números `00`–`45`, `Sí`/`No`; orden de filas (sorteo ascendente; Primer Sorteo, La Segunda, Revancha, Siempre Sale, Premio Extra; Primer, Segundo y Tercer Premio; "Categoría de N aciertos" al final por aciertos descendentes); nueve filas por sorteo recuperado, parcial o con inconsistencias (AC-5.8); una sola fila para un sorteo "No recuperado" y para una modalidad no informada (RN-39); ningún par repetido de sorteo, modalidad y categoría (AC-5.5); sin columna de precio del cartón (AC-5.6); ninguna celda de valor vacía y "No corresponde", "No disponible" y "Sin determinar" distinguibles (AC-5.7, RN-36); gramáticas de `procedencia`, `discrepancias` (el ejemplo literal de AC-4.1), `observaciones` y `sorteo_motivos`; apóstrofo delante de celdas que empiezan con `=`, `+`, `-`, `@`, tabulación o retorno de carro (AC-5.9); fin de línea `\r\n`, sin BOM, comillas solo cuando hacen falta; misma entrada → mismo texto; nombre `quini6-extraccion-{id}-{AAAA-MM-DD}-a-{AAAA-MM-DD}.csv`
- [X] T055 [P] [US5] Probar la descarga en `tests/integration/test_extraccion_csv.py`: tras una extracción terminada, "Descargar CSV" devuelve `Content-Type: text/csv; charset=utf-8` y `Content-Disposition: attachment; filename="quini6-extraccion-{id}-{desde}-a-{hasta}.csv"` (AC-5.1); dos descargas tienen los mismos bytes y otro administrador obtiene el mismo contenido (AC-5.10, AC-1.15); cada sorteo figura con el mismo estado que en la pantalla y las cantidades por estado coinciden con el resumen (AC-5.3); cada dato con valor tiene fuente, dirección y fecha y hora en `procedencia` (AC-5.4); un texto de la fuente que empieza con "=" figura con apóstrofo (AC-5.9); en curso o sin sorteos responde 404 y no se ofrece el botón

### Implementación de la historia 5

- [X] T056 [US5] Implementar `generar_csv(sorteos, intentos, fichas) -> str`, `nombre_archivo(id, desde, hasta)` y `VERSION_CONTRATO = "1.0"` en `dominio/extraccion/archivo_csv.py` con el módulo `csv` y exactamente las reglas de [contracts/csv.md](contracts/csv.md) (RN-34 a RN-39, RN-43, NFR-008 a NFR-010); función determinista y sin Django
- [X] T057 [US5] En `extracciones/servicios.py`, al terminar una extracción en `FINALIZADA` o `CON_ADVERTENCIAS`, generar el CSV una sola vez y guardar `archivo_csv`, `nombre_archivo` y `version_contrato` en la misma transacción que el estado final; en `SIN_SORTEOS`, `archivo_csv` queda vacío (RN-44, [002] R-08, R-09)
- [X] T058 [US5] Implementar la vista `descargar_csv` con `@administrador_requerido` en `extracciones/views.py` y la ruta `administracion/extracciones/<int:id>/csv/` en `extracciones/urls.py`: devuelve `archivo_csv` guardado codificado en UTF-8 sin BOM con los encabezados de [contracts/rutas.md](contracts/rutas.md); 404 si la extracción está en curso o terminó sin sorteos
- [X] T059 [US5] Agregar el botón "Descargar CSV" en `templates/extracciones/extraccion.html`, solo para una extracción terminada con al menos un sorteo identificado

**Punto de control**: primer incremento completo de la spec con una fuente (plan, paso 4): historias 1, 3 y 5.

---

## Fase 6: Historia de usuario 6 — Acceso restringido y sin ingesta (Prioridad: P1)

**Objetivo**: solo los administradores usan la extracción y nada extraído llega a los datos de la aplicación (FR-001, FR-016, RN-41, RN-42).

**Prueba independiente**: con una matriz de accesos y una extracción que incluye un concurso publicado y uno inexistente en la aplicación, se verifica que nada cambia.

### Pruebas de la historia 6

- [X] T060 [P] [US6] Probar la matriz de acceso de las cinco rutas en `tests/integration/test_extraccion_acceso.py`, con el estilo de `tests/integration/test_matriz_acceso.py`: visitante → redirección a `/ingresar/?next=…` y, al iniciar sesión desde esa redirección con una cuenta sin permiso de administrador, 403 con el mensaje de AC-6.1 (AC-6.2); usuario registrado sin permiso → 403 con "No tenés permisos para acceder a esta sección" y ningún dato de extracciones en la respuesta, también para el listado, una extracción de otro y su CSV (AC-6.1, AC-6.2, AC-6.6); administrador → 200, 303 o archivo; `Cache-Control: no-store` en todas las respuestas, incluida la descarga (NFR-004); el `POST` sin token CSRF se rechaza (`Client(enforce_csrf_checks=True)`); el 100 % de los accesos no autorizados se rechaza (SC-005)
- [X] T061 [P] [US6] Probar el aislamiento en `tests/integration/test_extraccion_aislamiento.py` con `tests/fabricas.py`: con el 3426 inexistente en la aplicación, después de extraer la consulta pública sigue mostrando "No hay información del concurso N.º 3426" y el listado de administración no lo incluye (AC-6.3); el 3425 publicado con valores distintos muestra los mismos valores, sin "Corregido el …" ni "Información en revisión", y su `RegistroCambio` no tiene entradas nuevas (AC-6.4); la jugada de un usuario y su comparación no cambian (AC-6.5); las cantidades y el contenido de todas las tablas de `resultados`, `jugadas` y `cuentas` son iguales antes y después (SC-004)
- [X] T062 [P] [US6] Crear la prueba estructural en `tests/unit/extraccion/test_estructura_aislamiento.py`: analizando con `ast` todos los módulos de `extracciones/` y `dominio/extraccion/`, ninguno importa `resultados` ni `jugadas` (RN-41), y ninguno de `dominio/extraccion/` ni de `extracciones/fuentes/` importa `django` ([002] R-07)

### Implementación de la historia 6

- [X] T063 [US6] Revisar `extracciones/views.py` y `templates/extracciones/`: cada vista tiene `@administrador_requerido` para todos los métodos, los formularios `POST` llevan `{% csrf_token %}`, las extracciones o sorteos inexistentes dan `Http404` y ninguna plantilla usa `|safe`; corregir lo que falle en T060 a T062

**Punto de control**: todas las historias P1 terminadas.

---

## Fase 7: Historia de usuario 2 — Recuperar desde varias fuentes con respaldo (Prioridad: P2)

**Objetivo**: la extracción consulta F1, F2 y F3, registra el resultado de cada intento según RN-08 y usa las demás fuentes cuando una falla (FR-005, FR-006).

**Prueba independiente**: con una fuente forzada a fallar, se extrae un período y se verifica que los sorteos se recuperan de las demás.

### Pruebas de la historia 2 (escribir primero; deben fallar)

- [X] T064 [P] [US2] Probar el intérprete de F1 en `tests/unit/extraccion/test_fuente_f1.py` con `tests/fixtures/fuentes/f1/`: listado → referencias con número y fecha; detalle → `PaginaCruda` con los rótulos de la ficha, aciertos "-" en Premio Extra y el pozo de Premio Extra como texto; página irreconocible → no reconocida sin excepción
- [X] T065 [P] [US2] Probar el intérprete de F3 en `tests/unit/extraccion/test_fuente_f3.py` con `tests/fixtures/fuentes/f3/`: listado agrupado por mes → referencias; detalle → `PaginaCruda`; el bloque de datos embebido se coteja con el HTML y una diferencia entre ambos se informa como no reconocida o con observación según lo relevado en T006
- [X] T066 [US2] Agregar a `tests/unit/extraccion/test_cliente_http.py` la correspondencia de RN-08 de `resultado_por_respuesta(respuesta, ficha)` ([002] R-02): 404 en F1 y F3 → "No encontrado"; 500 en F2 → "No disponible o no encontrado"; otro 5xx, 403, 429, error de conexión, TLS o límite de espera → "No disponible"; 200 con página anti-robots conocida → "No disponible" (AC-2.9); y la cobertura: F2 antes del 2211, F3 antes del 2787 y F1 fuera de su listado → "Fuera de cobertura" sin consulta (I-08) (depende de T017; requiere T005: I-08)
- [X] T067 [US2] Agregar a `tests/unit/extraccion/test_resumen.py`: intentos fallidos por tipo sin contar `OBTENIDO` ni `FUERA_DE_COBERTURA` e `INCOMPLETO` como tipo aparte; sorteos aportados por fuente según I-05; `requiere_mantenimiento` solo si la fuente cubre al menos un sorteo y quedó "Estructura no reconocida" en todos los que cubre (AC-2.10) (depende de T025; requiere T005: I-05)
- [X] T068 [P] [US2] Probar el recorrido de la historia 2 en `tests/integration/test_extraccion_us2.py` con `ClienteHttpFalso` y las tres fuentes: F1 con 500 → "No disponible" y datos de las demás (AC-2.2); F3 con 404 → "No encontrado" y F2 con 500 → "No disponible o no encontrado" (AC-2.3); página con otra estructura → "Estructura no reconocida" y ningún dato de ella (AC-2.4); bloque faltante → "Incompleto", qué falta y lo faltante tomado de otra fuente (AC-2.5); sorteo anterior al 2787 → F3 "Fuera de cobertura" sin contar como falla (AC-2.6); las tres fallan → "No recuperado" con el motivo de cada fuente y sin números ni importes (AC-2.7); límite de espera simulado → "No disponible" y el avance sigue (AC-2.8); 403 o página anti-robots → "No disponible" y una sola consulta a esa dirección (AC-2.9); el resumen muestra cada fuente con sorteos aportados e intentos fallidos por tipo (AC-2.1) y "Requiere mantenimiento" (AC-2.10); se consultan todas las fuentes que cubren el sorteo aunque la primera aporte todo (AC-4.8)

### Implementación de la historia 2

- [X] T069 [P] [US2] Implementar el intérprete de F1 en `extracciones/fuentes/f1.py` (`interpretar_sorteo`, `interpretar_listado`) con los selectores relevados en T006, solo textos y sin excepciones ante HTML inesperado
- [X] T070 [P] [US2] Implementar el intérprete de F3 en `extracciones/fuentes/f3.py` (`interpretar_sorteo`, `interpretar_listado`) con los selectores relevados en T006, leyendo el bloque de datos embebido con `json` y cotejándolo con el HTML ([002] R-04)
- [X] T071 [US2] Implementar `resultado_por_respuesta(respuesta, ficha) -> ResultadoIntento | None` en `extracciones/cliente_http.py` con la tabla de RN-08 de [002] R-02 y la detección de páginas anti-robots por los marcadores de la ficha; `None` significa "respuesta 200 para interpretar"
- [X] T072 [US2] Ampliar `extracciones/servicios.py` a las tres fuentes: `INTERPRETES` con F1, F2 y F3; listados de las tres como referencias; la fecha de F1 se toma de su propio listado o de las otras fuentes (RN-05, I-08); cobertura de cada ficha; por cada sorteo, consultas a F1, F2 y F3 en paralelo con `concurrent.futures.ThreadPoolExecutor(max_workers=3)`, una por sitio, pasando por el `LimitadorPorSitio` compartido, donde los hilos solo hacen HTTP y las escrituras en la base las hace el hilo principal ([002] R-03); resultado de cada intento con `resultado_por_respuesta` o `normalizar` (requiere T005: I-08)
- [X] T073 [US2] Completar `resumir` en `dominio/extraccion/resumen.py` con los intentos fallidos por tipo, los sorteos aportados (I-05) y la marca `requiere_mantenimiento` (RN-10, RN-33) (requiere T005: I-05)
- [X] T074 [US2] Mostrar en `templates/extracciones/extraccion.html` cada fuente utilizada con sus sorteos aportados, sus intentos fallidos por tipo y "Requiere mantenimiento" destacado con texto y estilo; y en `templates/extracciones/sorteo.html` los textos "No disponible o no encontrado", "Fuera de cobertura" e "Incompleto" con la observación de qué falta

**Punto de control**: la historia 2 funciona con las tres fuentes y las historias P1 siguen pasando.

---

## Fase 8: Historia de usuario 4 — Detectar discrepancias y conservar la procedencia (Prioridad: P2)

**Objetivo**: comparar las fuentes dato por dato, registrar coincidencias y discrepancias sin elegir valores, y marcar "Combina fuentes" y "Sin corroborar" (FR-010, FR-012).

**Prueba independiente**: dos fuentes publican valores distintos para un mismo dato y se verifican la pantalla y el archivo.

### Pruebas de la historia 4 (escribir primero; deben fallar)

- [X] T075 [US4] Agregar a `tests/unit/extraccion/test_consolidacion.py`: AC-4.1 (5.015 frente a 5.547,85 → `SIN_DETERMINAR`, `VALOR_DISTINTO` y ambos valores con su fuente); AC-4.2 (vacante en una fuente y la categoría ausente en otra que la publica según su ficha, con intento obtenido o incompleto → `OMISION`); AC-4.3 (pozo de una categoría con ganadores sin discrepancia); AC-4.4 (fechas distintas → discrepancia en `fecha`); AC-4.5 (12.060 frente a 12.060,13 → `CENTAVOS`, I-04: diferencia menor que $ 1,00); AC-4.6 (coincidencia → lista de fuentes); AC-4.7 (números de una fuente y premios de otra → `combina_fuentes`; una fuente completa y otra parcial → no combina, I-03); AC-4.8 (dato de una sola fuente → `sin_corroborar`); AC-3.2 (números en distinto orden sin discrepancia); I-06 (ganadores en conflicto → `estado_pozo` e importes "Sin determinar"); el orden de los intentos no cambia el resultado (RN-07) (depende de T048; requiere T005: I-03, I-04, I-06)
- [X] T076 [US4] Agregar a `tests/unit/extraccion/test_clasificacion.py`: una discrepancia de cualquier tipo deja el sorteo `CON_INCONSISTENCIAS` (AC-4.1, AC-4.4, AC-4.5) y un sorteo que combina fuentes sin diferencias puede quedar `RECUPERADO` (AC-4.7) (depende de T024)
- [X] T077 [P] [US4] Probar la historia 4 en `tests/integration/test_extraccion_us4.py` con `ClienteHttpFalso` y variantes editadas: el detalle muestra "Con inconsistencias", "Sin determinar", los dos valores con su fuente en formato argentino, "Omisión", "Diferencia de centavos o redondeo", las dos fechas, "Combina fuentes" y "Sin corroborar"; el CSV descargado tiene en `discrepancias` `importe_individual: Valor distinto — 5015.00 (numerosganadores.com.ar); 5547.85 (quiniya.com.ar)` y los datos de una sola fuente en `datos_sin_corroborar` (AC-4.1, AC-4.8) (depende de T058)

### Implementación de la historia 4

- [X] T078 [US4] Completar `consolidar` en `dominio/extraccion/consolidacion.py`: comparación de cada dato entre las fuentes que lo informan (números como conjunto), `SIN_DETERMINAR` con `Discrepancia` `VALOR_DISTINTO` o `CENTAVOS` según I-04 y todos los valores con su fuente (RN-27, RN-30); `OMISION` solo si la ficha declara que la fuente publica el dato y su intento fue obtenido o incompleto (RN-28); discrepancia de fechas (RN-22); `combina_fuentes` según I-03 (RN-29); `estado_pozo` e importes "Sin determinar" con ganadores en conflicto, sin reclasificar importes (I-06); ninguna fuente prevalece (RN-07) (requiere T005: I-03, I-04, I-06)
- [X] T079 [US4] Completar `templates/extracciones/sorteo.html` con la sección de discrepancias: tipo ("Valor distinto", "Omisión", "Diferencia de centavos o redondeo") y cada valor en formato argentino con su fuente ("No disponible" para la fuente que omite el dato, según el catálogo de mensajes), el valor consolidado "Sin determinar", "Combina fuentes" y "Sin corroborar" por dato y por sorteo (AC-4.1 a AC-4.8)

**Punto de control**: todas las historias funcionan con las tres fuentes.

---

## Fase 9: Servidor de fuentes de prueba (verificación manual, Const. VI)

**Propósito**: permitir que una persona no técnica provoque desde la pantalla los casos de las historias 2 a 5 ([002] R-11, [quickstart.md](quickstart.md) §5). Nunca se despliega.

- [X] T080 Crear el servidor de fuentes de prueba en `tests/fuentes_prueba/servidor.py` con `http.server`: argumentos `--escenario` y `--puerto` (8765 por omisión), escucha solo en `127.0.0.1`, atiende `/f1/…`, `/f2/…` y `/f3/…` según `tests/fuentes_prueba/escenarios/<escenario>/escenario.json` (por dirección: página, código HTTP y demora en segundos), 404 para direcciones no declaradas, ejecutable con `python -m tests.fuentes_prueba.servidor`; no se agrega a los paquetes de `pyproject.toml`
- [X] T081 [P] Crear el escenario `tests/fuentes_prueba/escenarios/normal/` (escenario.json y páginas de las tres fuentes) con los sorteos 3422 a 3427 de noviembre de 2026 coherentes entre fuentes, sus listados, un período sin sorteos y los sorteos necesarios para el aviso de cobertura del 17/12/2014 (quickstart §5, escenarios C y D)
- [X] T082 [P] Crear el escenario `tests/fuentes_prueba/escenarios/fallas/` con 500, 404, demora de 15 s, 403, página anti-robots, el 3423 ausente en las tres fuentes, un sorteo en que fallan las tres, una página sin la tabla de una modalidad y un sorteo anterior al 2787 (quickstart §5, escenarios D y E)
- [X] T083 [P] Crear el escenario `tests/fuentes_prueba/escenarios/estructura/` con rótulos desconocidos y una fuente irreconocible en todos los sorteos que cubre (AC-2.4, AC-2.10)
- [X] T084 [P] Crear el escenario `tests/fuentes_prueba/escenarios/discrepancias/` con 5.015 frente a 5.547,85, vacante frente a omisión, fechas distintas, 12.060 frente a 12.060,13, números en una fuente y premios en otra, y un dato de una sola fuente (quickstart §5, escenario G)
- [X] T085 [P] Crear el escenario `tests/fuentes_prueba/escenarios/normalizacion/` con los casos de quickstart §5, escenario F: rótulos equivalentes, números desordenados, Premio Extra, vacante de 1.100.000.000, 18 ganadores con 3.013.912, ganadores ausentes, "494,443,71", números inválidos, Siempre Sale 5/17, sorteo anterior al 18/06/2024, modalidad ausente, Premio Extra que no coincide, "0,00", "55 millones de pesos" y un texto que empieza con "="
- [X] T086 Probar en `tests/unit/extraccion/test_escenarios_prueba.py` que cada `escenario.json` es válido y que todas las páginas que declara existen, y que el servidor responde el código y la página declarados para una dirección de ejemplo (depende de T080 a T085)

---

## Fase 10: Terminaciones y aspectos transversales

**Propósito**: calidad, verificación desde la aplicación y documentación.

- [ ] T087 [P] Revisar las tres pantallas a 360 px y con lector de contraste: sin desplazamiento horizontal (NFR-002), estados con texto además de color y contraste AA (NFR-003), estados de en curso, éxito, advertencia, error y vacío diferenciados (NFR-011); modificar `static/css/app.css` solo si hace falta un estado visual nuevo, reutilizando sus variables
- [ ] T088 Ejecutar `ruff check .` y `pytest` (suite completa, incluida la de 001) y dejar ambos en verde
- [ ] T089 Verificar a mano los escenarios A a H de `specs/002-extraccion-historica-csv/quickstart.md` §5 con el servidor de fuentes de prueba y el trabajador en marcha, revisando la pantalla y el CSV en una planilla; informar al responsable qué criterios de aceptación se verificaron y qué desviaciones o pendientes quedan (Const. II)
- [ ] T090 Verificar a mano con las fuentes reales `specs/002-extraccion-historica-csv/quickstart.md` §6: SC-003 (10 sorteos comparados con la página citada en `procedencia`), SC-007 (un mes en menos de 2 min y 12 meses en menos de 10 min, sin otras extracciones en curso), SC-006 (3 administradores), SC-008 (dos planillas) y NFR-002 y NFR-003; informar los resultados al responsable
- [ ] T091 Actualizar `CLAUDE.md` con las decisiones de diseño y convenciones nuevas de esta feature, una línea por decisión, con referencia a la spec (p. ej. '[002] ...'). No incluyas entradas por incluir, asegúrate siempre de que es información transversal y relevante para el proyecto que pueden aprovechar futuras features. Candidatas a evaluar: el trabajador `manage.py procesar_extracciones` en una sola instancia (también en "Arranque y pruebas en local"); el tipo `Dato` de cuatro estados de RN-20; fuentes externas solo con `urllib` y `html.parser` y fichas en código; el ritmo fijo de una consulta cada 2 s por sitio; las variables `QUINI6_FUENTE_*`; el CSV versionado como contrato de la futura ingesta; y el servidor de fuentes de prueba (plan, paso 8)

---

## Fase 11: Correcciones del responsable (Clarifications 20/11/2026, D-14 a D-19)

**Propósito**: aplicar las seis correcciones pedidas por el responsable tras usar la extracción con las fuentes reales.

- [x] T092 Actualizar `spec.md` (Clarifications 2026-11-20; RN-06 a RN-09, RN-11, RN-12, RN-16 a RN-20, RN-30, RN-43; FR-005, FR-011, NFR-007; criterios nuevos y modificados; D-14 a D-19), `contracts/csv.md` (versión 2.0), `contracts/mensajes.md` y `contracts/fuentes.md` (prioridad)
- [x] T093 [US2] Prioridad F2 → F3 → F1 en `dominio/extraccion/tipos.py` (`ORDEN_FUENTES`, `FUENTES_RESPALDO`, `ResultadoIntento.NO_REQUERIDA`) y consulta en dos tiempos en `extracciones/servicios.py`, con `requiere_respaldo` en `dominio/extraccion/clasificacion.py` (RN-09, AC-2.11)
- [x] T094 [US3] Nombres de modalidad de la extracción (`nombre_modalidad`) en el dominio, la pantalla y el CSV (RN-11, AC-3.1)
- [x] T095 [US3] [US4] En `dominio/extraccion/consolidacion.py`: valor de la fuente prioritaria (RN-07, AC-4.9), tolerancia del 1 % con redondeo a pesos enteros (RN-30, AC-4.5), pozo calculado e importe individual 0,00 en vacantes (RN-18, AC-3.4, AC-3.5) y números de Pozo Extra calculados (RN-12, AC-3.17); `DatoConsolidado.calculo` y `DatoConsolidado.diferencia_tolerada` serializados en `extracciones/serializacion.py`
- [x] T096 [US3] Corrección de importes con cuatro dígitos en el último grupo en `dominio/extraccion/normalizacion.py` (RN-16, AC-3.16)
- [x] T097 [US5] CSV versión 2.0 en `dominio/extraccion/archivo_csv.py`: columna `numeros_pozo_extra`, tramos `Calculado` en `procedencia` y diferencias toleradas en `observaciones`
- [x] T098 [US1] Detalle del sorteo (`extracciones/consultas.py`, `templates/extracciones/sorteo.html`): marca "Calculado" y nota de diferencia tolerada
- [x] T099 Actualizar las pruebas afectadas y agregar las de AC-2.11, AC-3.16, AC-3.17 y AC-4.9; `ruff check .` y `pytest` en verde
- [x] T101 [US3] Redondeo a centavos de importes con tres o más decimales, con la nota "Importe corregido" (RN-16, D-20, AC-3.18), en `corregir_importe_mal_cargado` de `dominio/extraccion/normalizacion.py`, con sus pruebas
- [x] T102 [US2] [US4] Desempate con la tercera fuente (D-21): F1 se consulta también ante diferencias o datos inválidos de F2 y F3 y se le pide cualquier sorteo con la fecha informada (`extracciones/servicios.py`, `requiere_respaldo`); mayoría de 2 de 3 en `_comparar` con la nota `TipoDiscrepancia.MAYORIA` y la observación de la fuente en minoría como informativa (`dominio/extraccion/consolidacion.py`); pruebas de AC-4.10 y AC-4.11
- [ ] T100 Verificar a mano con las fuentes reales el sorteo 3232 de los ejemplos del responsable (pozo vacante y pozo = importe individual × ganadores) y un sorteo con «410.1156,25»; informar al responsable

---

## Fase 12: Ajustes de pantalla del responsable (Clarifications 20/11/2026, D-22 a D-25)

**Propósito**: aplicar los cuatro ajustes de la pantalla de extracción pedidos por el responsable como administrador.

- [x] T103 Actualizar `spec.md` (Clarifications 2026-11-20, ajustes de pantalla; RN-18, RN-19, RN-35, RN-44; FR-015; AC-1.12, AC-1.14, AC-2.2, AC-3.5; quitar AC-3.15; agregar AC-1.18 a AC-1.20; Supuestos; D-08 y D-12), `contracts/csv.md` (versión 3.0), `contracts/rutas.md`, `contracts/mensajes.md`, `contracts/fuentes.md`, `data-model.md` y `quickstart.md`
- [x] T104 [US3] [US5] Quitar `se_acumula` e `importe_trasladado` del dominio (`dominio/extraccion/tipos.py`, `normalizacion.py`, `consolidacion.py`, `clasificacion.py`), de `extracciones/serializacion.py` (las claves de sorteos ya guardados se ignoran al leer) y del CSV, que pasa a la versión 3.0 en `dominio/extraccion/archivo_csv.py` (D-22)
- [x] T105 [US1] Detalle del sorteo sin fuentes por dato en `templates/extracciones/sorteo.html` y `extracciones/consultas.py`: sin la columna "Fuentes", sin las fuentes junto a la fecha y los números, sin la marca "Calculado" de pozo e importe individual; "Sin corroborar" junto al valor; se conserva la marca de los números de Pozo Extra (D-23)
- [x] T106 [US1] Eliminar extracciones terminadas: `servicios.eliminar_extraccion`, vista y ruta `/administracion/extracciones/<id>/eliminar/` (GET confirmación, POST elimina), plantilla `templates/extracciones/eliminar.html`, menú ⋮ con `<details>` en "Extracciones anteriores" y columna "Fecha"; estilos del menú en `static/css/app.css` (AC-1.18, AC-1.19, D-24)
- [x] T107 [US1] Campos de fecha con calendario: `type="date"` en `extracciones/forms.py`, con `max` = hoy; el formulario acepta `AAAA-MM-DD` y `dd/mm/aaaa`; `static/js/selector-fecha.js` abre el calendario al hacer clic en el campo (mejora progresiva) (AC-1.20, D-25)
- [x] T108 Actualizar las pruebas afectadas y agregar las de AC-1.18, AC-1.19, AC-1.20 y D-22/D-23; actualizar `CLAUDE.md` (CSV versión 3.0); `ruff check .` y `pytest` en verde

---

## Fase 13: Barra de progreso del avance (Clarifications 21/11/2026, D-26)

**Propósito**: mostrar, junto al texto del avance, una barra que crece a medida que se procesan los sorteos.

- [x] T109 Actualizar `spec.md` (Clarifications 2026-11-21, FR-003, AC-1.21), `research.md` (R-10) y `quickstart.md`
- [x] T110 [US1] Agregar a `templates/extracciones/_avance.html` un `<progress>` con `value` = procesados y `max` = identificados, nombrado por el texto del avance, solo cuando el total es conocido; estilos `.barra-avance` en `static/css/app.css` (AC-1.21, NFR-003, D-26)
- [x] T111 [US1] Probar AC-1.21 en `tests/integration/test_extraccion_us1.py` (sin barra mientras se identifica; `value="1" max="5"` con un sorteo procesado); `ruff check .` y `pytest` en verde

---

## Fase 14: Fechas escritas con el teclado (Clarifications 21/11/2026, D-27)

**Propósito**: que el calendario no impida escribir la fecha a mano.

- [x] T112 Actualizar `spec.md` (Clarifications 2026-11-21, D-27; AC-1.20) y `quickstart.md` (Escenario I)
- [x] T113 [US1] Quitar `static/js/selector-fecha.js`, su carga en `templates/extracciones/inicio.html` y el atributo `data-calendario` de `extracciones/forms.py`; el calendario queda en el ícono nativo del campo `type="date"` (AC-1.20, D-27)
- [x] T114 [US1] Actualizar la prueba de AC-1.20 en `tests/integration/test_extraccion_us1.py`; `ruff check .` y `pytest` en verde

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (fase 1)**: sin dependencias. T005 puede correr en paralelo con el resto, pero bloquea las tareas marcadas "(requiere T005)".
- **Base (fase 2)**: depende de la fase 1. **Bloquea todas las historias.** T006 (relevamiento) bloquea T007, T009 y los intérpretes.
- **Historia 1 (fase 3)**: depende de la fase 2. Construye la cadena completa (servicio, trabajador, pantallas) con F2; las demás historias la amplían.
- **Historia 3 (fase 4)**: depende de la historia 1 (amplía `normalizacion.py`, `consolidacion.py`, `servicios.py` y `sorteo.html`).
- **Historia 5 (fase 5)**: depende de la historia 1. Es independiente de la historia 3, aunque sus filas reflejan lo que normaliza la historia 3.
- **Historia 6 (fase 6)**: depende de las historias 1 y 5 (la matriz incluye la ruta de descarga).
- **Historia 2 (fase 7)**: depende de la historia 1. Se puede hacer en paralelo con las historias 3, 5 y 6 si se coordinan los cambios en `servicios.py`.
- **Historia 4 (fase 8)**: depende de la historia 1 para la consolidación y de la historia 5 para la prueba del CSV (T077). Su valor real requiere la historia 2 (más de una fuente).
- **Servidor de fuentes de prueba (fase 9)**: depende solo de la fase 2 para el código y de T007 para las páginas base; se necesita para T089.
- **Terminaciones (fase 10)**: dependen de todas las historias.
- **Cambios del responsable (fases 11 a 14)**: dependen de la fase 10 y se aplican en orden. Cada fase empieza por actualizar la spec y los artefactos y termina con `ruff` y `pytest` en verde.

### Orden de las historias

```text
Fase 1 → Fase 2 → US1 (P1, MVP) ─┬─→ US3 (P1)
                                 ├─→ US5 (P1) ─→ US6 (P1)
                                 └─→ US2 (P2) ─→ US4 (P2, también requiere US5)
                    Fase 9 (en paralelo desde la fase 2) ─→ Fase 10
```

### Dentro de cada historia

- Las pruebas se escriben primero y fallan antes de implementar.
- Dominio puro antes que servicio; servicio antes que vistas; vistas antes que plantillas.
- `extracciones/servicios.py`, `dominio/extraccion/normalizacion.py`, `dominio/extraccion/consolidacion.py` y las plantillas se modifican en varias historias: esas tareas no son paralelas entre sí.

### Oportunidades de paralelismo

- Fase 1: T002 y T004.
- Fase 2: T008, T010 y T011 en paralelo; T015 y T017 en cuanto existan T014 y T016.
- Historia 1: las nueve pruebas (T019 a T027) en paralelo; T028, T029, T030, T032, T033 y T034 en paralelo; T036 y T037 en paralelo; las plantillas y el JS (T039 a T044) en paralelo.
- Historia 3: T046 y T049 en paralelo.
- Historia 5: T054 y T055 en paralelo.
- Historia 6: T060, T061 y T062 en paralelo.
- Historia 2: T064, T065 y T068 en paralelo; T069 y T070 en paralelo.
- Fase 9: los cinco escenarios (T081 a T085) en paralelo.

---

## Ejemplo de paralelismo: historia 1

```text
# Pruebas de la historia 1, todas juntas:
Tarea: "T019 Probar validar_periodo en tests/unit/extraccion/test_periodo.py"
Tarea: "T020 Probar identificar_sorteos en tests/unit/extraccion/test_identificacion.py"
Tarea: "T021 Probar el intérprete de F2 en tests/unit/extraccion/test_fuente_f2.py"
Tarea: "T024 Probar clasificar en tests/unit/extraccion/test_clasificacion.py"
Tarea: "T026 Probar el recorrido en tests/integration/test_extraccion_us1.py"

# Dominio puro de la historia 1, todo junto:
Tarea: "T028 dominio/extraccion/periodo.py"
Tarea: "T029 dominio/extraccion/identificacion.py"
Tarea: "T030 extracciones/fuentes/f2.py"
Tarea: "T033 dominio/extraccion/clasificacion.py"
Tarea: "T034 dominio/extraccion/resumen.py"
```

## Ejemplo de paralelismo: historia 2

```text
Tarea: "T064 Probar el intérprete de F1 en tests/unit/extraccion/test_fuente_f1.py"
Tarea: "T065 Probar el intérprete de F3 en tests/unit/extraccion/test_fuente_f3.py"
Tarea: "T068 Probar el recorrido en tests/integration/test_extraccion_us2.py"
# Después:
Tarea: "T069 extracciones/fuentes/f1.py"
Tarea: "T070 extracciones/fuentes/f3.py"
```

## Ejemplo de paralelismo: historia 6

```text
Tarea: "T060 Matriz de acceso en tests/integration/test_extraccion_acceso.py"
Tarea: "T061 Aislamiento en tests/integration/test_extraccion_aislamiento.py"
Tarea: "T062 Prueba estructural en tests/unit/extraccion/test_estructura_aislamiento.py"
```

---

## Estrategia de implementación

### Primero el MVP (solo la historia 1)

1. Fase 1: preparación, incluida la consulta T005 al responsable.
2. Fase 2: base, empezando por el relevamiento T006 (si contradice el análisis de fuentes, se detiene y se consulta).
3. Fase 3: historia 1 con F2.
4. **Detenerse y validar**: un administrador extrae dos semanas y ve el avance, el resumen, el detalle y el listado.

### Entrega incremental

1. Preparación + base → cimientos listos.
2. Historia 1 → demostración del recorrido con una fuente (MVP).
3. Historias 3 y 5 → primer incremento completo del plan (paso 4): datos exactos y CSV descargable.
4. Historia 6 → condición de seguridad y aislamiento verificada: todas las P1 terminadas.
5. Historias 2 y 4 → tres fuentes, respaldo, discrepancias y procedencia completa.
6. Fase 9 → verificación manual de todos los criterios desde la pantalla.
7. Fase 10 → `ruff` y `pytest` en verde, verificación con fuentes reales y `CLAUDE.md`.

Una funcionalidad no se da por terminada solo porque pasan las pruebas: debe cumplir sus criterios de aceptación verificados desde la pantalla (Constitución, "Flujo de trabajo").

---

## Notas

- [P] = archivos distintos y sin dependencias pendientes.
- La etiqueta [USn] vincula cada tarea con su historia para la trazabilidad (Const. II).
- Hacer un commit por tarea o por grupo lógico.
- Detenerse en cada punto de control para validar la historia.
- No agregar rutas, pantallas, estados, dependencias ni comportamientos que no figuren en la spec, el plan o los contratos (Const. I). Ante una contradicción o un caso no cubierto, consultar al responsable.
