# Investigación técnica (Fase 0): Extracción histórica de sorteos y exportación CSV

**Fecha**: 19/11/2026 | **Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) | **Fuentes**: [analisis-fuentes.md](analisis-fuentes.md)

Este documento resuelve las incógnitas técnicas del plan. Los identificadores `R-xx` e `I-xx` son locales a la spec 002 y desde otros documentos se citan como `[002] R-xx`. Las decisiones de la spec 001 se citan como `[001] R-xx`.

Separación que exige la Constitución (Flujo de trabajo):

- **R-xx**: decisiones técnicas. No cambian el comportamiento aprobado.
- **I-xx**: interpretaciones técnicas de reglas aprobadas en casos límite que la spec no detalla. El plan las adoptó porque no agregan comportamiento y las sometió a confirmación (P-02 del plan). El responsable aprobó I-01 a I-10 el 19/11/2026 en el análisis.
- **Preguntas de la planificación**: cuatro puntos funcionales se consultaron al responsable el 19/11/2026 y ya están en [spec.md](spec.md) → Clarifications → "Session 2026-11-19 (planificación)".

No quedan marcas `NEEDS CLARIFICATION`.

---

## R-01 — Ejecución de la extracción fuera de la solicitud web

- **Decisión**: la extracción la ejecuta un **proceso trabajador** propio, el comando de gestión `python manage.py procesar_extracciones` ([contracts/comandos.md](contracts/comandos.md)). La vista solo valida el período y crea la `Extraccion` en estado "en curso". El trabajador toma las extracciones en curso por orden de inicio, las procesa de a una y guarda el avance en la base después de cada sorteo. La base de datos es la cola: no hay otro servicio.
- **Justificación**:
  - Una extracción de 12 meses tarda varios minutos por el ritmo de NFR-005 ([002] R-14). No cabe en una solicitud HTTP (el límite de `gunicorn` es de 30 s).
  - Un único trabajador garantiza **por construcción** el ritmo máximo por sitio de NFR-005, aunque varios administradores inicien extracciones a la vez: el límite es global y no por extracción.
  - El avance queda en la base, así que la pantalla lo muestra aunque se recargue (AC-1.11) y el trabajador puede **reanudar** una extracción interrumpida por un reinicio, sin estados nuevos (I-07).
- **Restricción operativa**: debe correr **una sola instancia** del trabajador. Se documenta en [quickstart.md](quickstart.md) y en el despliegue (servicio del sistema junto a `gunicorn`, [001] R-16).
- **Alternativas descartadas**:
  - *Celery o RQ con Redis*: dos dependencias y un servicio más. Complejidad que la spec no necesita (Const. XI) y que `CLAUDE.md` prohíbe sin justificación.
  - *Hilo lanzado desde la vista*: muere con el proceso de `gunicorn` que lo creó, no puede garantizar el ritmo global por sitio con varios procesos y deja extracciones colgadas tras un reinicio.
  - *Procesar de a tramos en cada recarga de la página*: la extracción se detendría si el administrador cierra la pestaña.

## R-02 — Cliente HTTP

- **Decisión**: `urllib.request` de la biblioteca estándar, encapsulado en `extracciones/cliente_http.py`:
  - Solo `GET` a direcciones armadas con la ficha de cada fuente ([contracts/fuentes.md](contracts/fuentes.md)). Nunca se consulta una dirección que provenga del contenido de una página.
  - Límite de espera de **10 s** por consulta (NFR-006). Sin reintentos: una falla queda registrada como intento "No disponible" y la extracción sigue.
  - Certificados TLS verificados. Las redirecciones solo se siguen dentro del mismo sitio.
  - Encabezado `User-Agent` fijo y genérico que identifica a la aplicación (`QUINI6-extraccion-historica/1.0`), sin datos personales.
  - Respuestas de más de 2 MB se descartan como "No disponible".
  - La codificación se toma del encabezado `Content-Type` o de la etiqueta `<meta charset>`, con UTF-8 como valor predeterminado.
- **Correspondencia con RN-08**:

  | Situación | Resultado del intento |
  |-----------|-----------------------|
  | 200 y la página se reconoce completa | Obtenido |
  | 200 y faltan datos que la ficha declara | Incompleto |
  | 200 y no se reconocen número y fecha (o no coinciden con lo pedido, RN-21) | Estructura no reconocida |
  | 404 en F1 y F3 | No encontrado |
  | 500 en F2 | No disponible o no encontrado |
  | Otro 5xx, 403, 429, error de conexión, TLS o límite de espera | No disponible |
  | 200 con una página de verificación anti-robots conocida | No disponible (AC-2.9) |
  | Sorteo anterior a la cobertura de la ficha | Fuera de cobertura (no se consulta) |

- **NFR-005**: ante un 403, un 429 o una verificación anti-robots, la aplicación **no** cambia de encabezados, no usa intermediarios ni reintenta. El intento queda "No disponible".
- **Alternativa descartada**: `requests` o `httpx`. Agregan una dependencia para lo que la biblioteca estándar resuelve con unas decenas de líneas.

## R-03 — Ritmo por sitio y consultas en paralelo

- **Decisión**: un limitador por fuente dentro del trabajador. Entre el inicio de dos consultas al mismo sitio pasan **al menos 2 s**, incluidas las páginas de listado y las consultas de identificación. Para cada sorteo, las consultas a F1, F2 y F3 se hacen **en paralelo**, una por sitio, con `concurrent.futures.ThreadPoolExecutor` (NFR-005 permite consultar sitios distintos al mismo tiempo). Los hilos solo hacen HTTP; las escrituras en la base las hace el hilo principal.
- **Enmienda (20/11/2026, D-14 y D-21)**: en paralelo se consultan solo F2 y F3. F1 (respaldo y desempate) se consulta después, y solo si hace falta (ver R-16). Si no hace falta, su intento es "No requerida", sin consulta. El ritmo de 2 s por sitio no cambia.
- **Valor fijo en el código**: el intervalo de 2 s no se configura por variable de entorno, para que no se pueda bajar por error. Las pruebas automatizadas inyectan un limitador sin espera y no hacen consultas reales.

## R-04 — Lectura del HTML de las fuentes

- **Decisión**: `html.parser.HTMLParser` de la biblioteca estándar, con un pequeño constructor de árbol propio (`extracciones/fuentes/html.py`) que permite recorrer tablas, filas y textos. Para F3, que además publica datos estructurados embebidos, se usa `json` de la biblioteca estándar sobre ese bloque y se cotejan con el HTML.
- **Un intérprete por fuente** (`extracciones/fuentes/f1.py`, `f2.py`, `f3.py`): recibe el HTML y devuelve una `PaginaCruda` con **textos sin interpretar** (número, fecha, rótulos de bloques, números y filas de premios). La conversión de esos textos a valores la hace el dominio ([002] R-07), con la ficha de la fuente como parámetro.
- **Regla de seguridad (NFR-010)**: el HTML se trata como dato no confiable. No se ejecuta JavaScript, no se siguen enlaces de la página y los textos se muestran con el escape automático de las plantillas, nunca con `|safe`.
- **Pruebas**: cada intérprete se prueba con copias recortadas de páginas reales, guardadas en `tests/fixtures/fuentes/`, y con variantes editadas que provocan cada resultado de RN-08.
- **Datos a relevar al implementar**: los selectores exactos de cada página y la profundidad real del listado de F3. Se registran en la ficha de cada fuente ([contracts/fuentes.md](contracts/fuentes.md)). Si la estructura real contradice [analisis-fuentes.md](analisis-fuentes.md), se consulta al responsable antes de adaptar la ficha (RN-10, D-07).
- **Alternativa descartada**: `beautifulsoup4` o `lxml`. Son más cómodas, pero agregan dependencias. Las páginas tienen tablas simples y el analizador estándar alcanza.

## R-05 — Fichas de las fuentes como configuración en el código

- **Decisión**: las fichas de F1, F2 y F3 son estructuras inmutables en `extracciones/fuentes/fichas.py`: identificador, nombre (el dominio del sitio), direcciones, cobertura, tabla exacta de rótulos de modalidad (RN-11), significado de cada columna y lista de datos que la fuente publica o no publica por diseño (RN-17, RN-28). Su contenido está en [contracts/fuentes.md](contracts/fuentes.md).
- **Justificación**: RN-06 fija una lista cerrada que no se configura desde la interfaz. Cambiar una ficha requiere una spec aprobada, así que no hace falta una tabla en la base.
- **Fuentes de prueba**: la dirección base de cada fuente se puede reemplazar con `QUINI6_FUENTE_F1_URL`, `QUINI6_FUENTE_F2_URL` y `QUINI6_FUENTE_F3_URL`, solo para apuntar al servidor de fuentes de prueba ([002] R-11). Vacías, se usan las direcciones reales.

## R-06 — Identificación de los sorteos del período (RN-05)

- **Decisión**: una función pura del dominio, `identificar_sorteos`, que recibe el período, las referencias conocidas `(número, fecha, fuente)` y una función para pedir la fecha de un número. La orquestación con HTTP vive en el servicio. Pasos:
  1. Se leen los listados: F1 (`/quini6/sorteos-anteriores.aspx`, unos 3 meses), F2 (`/sorteos`, últimos 20) y F3 (`/sorteos`). Cada fila es una referencia `(número, fecha)`.
  2. Si las referencias ya cubren el inicio del período, el primer y el último número salen de ellas.
  3. Si no, se estima el número del inicio a razón de dos sorteos por semana desde la referencia más antigua y se **ajusta** pidiendo páginas de detalle por número a F2 (desde el 2211) o a F3 (desde el 2787), con una búsqueda que avanza o retrocede según la fecha informada. Cada página de detalle obtenida se conserva en memoria durante la extracción y se reutiliza como intento de ese sorteo, así que las consultas dentro del período no se repiten.
  4. Si el inicio es anterior al primer sorteo cubierto por alguna fuente (2211, 17/12/2014, según [analisis-fuentes.md](analisis-fuentes.md)), el primero identificado es ese y se guarda el aviso "Las fuentes no cubren el período anterior al 17/12/2014" (AC-1.17).
  5. Se consideran identificados todos los números entre el primero y el último. Los que ninguna fuente informe quedan "No recuperado" y se informan como huecos (AC-1.16).
  6. Si ningún sorteo tiene fecha dentro del período, la extracción termina "sin sorteos" (AC-1.10).
- Las fechas nunca se deducen del calendario: la estimación del paso 3 solo elige qué número consultar, y la pertenencia al período la decide siempre la fecha informada (RN-05).
- **Costo**: unas pocas consultas fuera del período, solo cuando el período es más antiguo que los listados.

## R-07 — Reglas de la extracción como funciones puras

- **Decisión**: un subpaquete `dominio/extraccion/` sin Django, con la misma convención que el resto de `dominio/` (errores como valores, `Decimal`, sin acceso a la base). Contiene la validación del período (RN-01 a RN-04), la identificación (RN-05), la normalización con la ficha como parámetro (RN-11 a RN-20), la validación (RN-21 a RN-26), la consolidación entre fuentes (RN-27 a RN-30, RN-32), la clasificación (RN-31), el resumen (RN-33) y la generación del CSV (RN-34 a RN-39, RN-43). Interfaz en [contracts/dominio.md](contracts/dominio.md).
- **Reutilización**: `Modalidad`, sus nombres visibles y `FECHA_VIGENCIA_REGLAS` de `dominio/tipos.py`; las reglas de seis números de 00 a 45 de `dominio/numeros.py`. El formato argentino de importes de `dominio/importes.parsear_pesos` **no** se reutiliza tal cual para las fuentes, porque acepta el símbolo "$" y textos como "55 millones de pesos" solo en el intérprete de la extracción. Se agrega `parsear_importe_fuente`, que delega en `parsear_pesos` una vez limpio el texto.
- **Justificación**: las reglas de exactitud (Const. VIII) se prueban sin base de datos ni red, con casos tomados de los criterios de aceptación (SC-001, SC-002).

## R-08 — Persistencia de las extracciones (RN-44)

- **Decisión**: una aplicación Django nueva, `extracciones`, con tres modelos ([data-model.md](data-model.md)):
  - `Extraccion`: el pedido, su estado, su avance, el resumen y el **archivo CSV generado**, guardado como texto en la base al terminar.
  - `SorteoExtraido`: un registro por número identificado, con su estado y su consolidado en un campo JSON.
  - `IntentoConsulta`: un registro por sorteo y fuente, con la dirección, la fecha y hora, el resultado de RN-08, los datos normalizados y las observaciones.
- **El CSV se genera una sola vez**, al terminar, y la descarga devuelve siempre esos mismos bytes (AC-5.10, RN-44). Un cambio posterior en el código del generador no altera los archivos ya conservados.
- **JSON sin consultas dentro del JSON**: los campos `JSONField` funcionan igual en SQLite y PostgreSQL, y nunca se filtra por su contenido, así que no se usa ninguna función exclusiva de un motor (CLAUDE.md). Los importes se guardan en el JSON como texto decimal (`"1100000000.00"`), con `dominio.importes.a_texto_decimal`, nunca como `float`.
- **Inmutabilidad**: una extracción terminada no se modifica. Solo el trabajador escribe y solo mientras está en curso. No hay ruta para editar. **Enmienda (20/11/2026, D-24)**: un administrador puede eliminar una extracción terminada, con sus sorteos, intentos y archivo (`servicios.eliminar_extraccion`, confirmación GET + POST → 303). La que está en curso no se puede eliminar, porque el trabajador la está usando.
- **Volumen**: unas 100 filas de sorteo, 300 intentos y un CSV de alrededor de 1,5 MB por cada extracción de 12 meses. El crecimiento sin límite es un supuesto aceptado de la spec.
- **Alternativas descartadas**: tablas relacionales para cada dato, discrepancia y observación (nadie las consulta por separado y multiplican el modelo); el archivo CSV en el disco (exige almacenamiento persistente y respaldos aparte de la base).

## R-09 — Archivo CSV

- **Decisión**: módulo `csv` de la biblioteca estándar. UTF-8 **sin** marca BOM, separador coma, comillas solo cuando hacen falta, fin de línea `\r\n` (RFC 4180). La primera fila tiene los encabezados del contrato y cada fila declara la versión del contrato en la columna `version_contrato` (NFR-009). El contrato completo está en [contracts/csv.md](contracts/csv.md).
- **Protección contra fórmulas (NFR-010, AC-5.9)**: toda celda que empieza con `=`, `+`, `-`, `@`, tabulación o retorno de carro se antepone con un apóstrofo (`'`). Ninguna celda de valores del contrato empieza con esos caracteres, así que la protección solo alcanza a textos provenientes de las fuentes.
- **Nombre del archivo**: `quini6-extraccion-{id}-{AAAA-MM-DD}-a-{AAAA-MM-DD}.csv`, con el período consultado (AC-5.1) y el identificador de la extracción, para distinguir dos extracciones del mismo período.
- **Sin BOM**: el contrato es para una ingesta automática, y la marca BOM se cuela en el primer encabezado de muchos lectores. AC-5.2 y SC-008 ya indican importar declarando UTF-8.

## R-10 — Avance en pantalla (Clarifications 19/11/2026, planificación)

- **Decisión**: la página de la extracción se renderiza en el servidor con el estado del momento. Mientras está en curso, `static/js/avance-extraccion.js`, como mejora progresiva, pide la **misma dirección** cada 5 s, reemplaza solo el bloque de avance (una región `aria-live="polite"`) y, cuando la respuesta ya trae el resumen, reemplaza la página completa. Sin JavaScript, el avance se actualiza al recargar.
- **Barra de progreso (21/11/2026, D-26)**: el bloque de avance incluye un `<progress value="N" max="M">` nativo, nombrado con `aria-labelledby` por el texto "N de M sorteos procesados"; no se muestra mientras se identifican los sorteos. Como está dentro del bloque reemplazado, se actualiza con el mismo mecanismo, sin cambios en el JS. Estilo propio en `app.css` con las variables de color.
- **Justificación**: no agrega rutas ni formatos de respuesta. El avance se anuncia de forma accesible sin mover el foco (NFR-003).

- **Sin forzar el calendario (21/11/2026, D-27)**: los campos de fecha son `<input type="date">` nativos. No se llama a `showPicker()` al hacer clic, porque en Chrome y Edge el calendario abierto toma las teclas y no deja escribir la fecha. El calendario queda en el ícono del campo. Se quitó `static/js/selector-fecha.js` (D-25).

## R-11 — Fuentes de prueba para la verificación manual

- **Decisión**: un servidor local hecho con `http.server` de la biblioteca estándar, en `tests/fuentes_prueba/servidor.py`, que nunca se despliega. Sirve **escenarios**: carpetas con páginas HTML (copias recortadas y editadas de páginas reales) y un archivo `escenario.json` que indica, para cada dirección, qué página devolver, con qué código y con qué demora. Escenarios previstos: `normal`, `fallas` (500, 404, demora mayor al límite, 403), `estructura` (rótulos y páginas irreconocibles), `discrepancias` (valores distintos, centavos, fechas, omisiones) y `normalizacion` (vacantes, ganadores, importes inválidos, números inválidos, Premio Extra).
- **Uso**: se inicia con `python -m tests.fuentes_prueba.servidor --escenario <nombre>` y se apunta la aplicación con las variables de [002] R-05. Quien verifica puede editar las páginas del escenario para provocar otros casos (Supuestos de la spec).

## R-12 — Pruebas

- **Unitarias** (`tests/unit/extraccion/`): todas las funciones de `dominio/extraccion/` con un caso o más por criterio de las historias 2 a 5 (SC-001, SC-002), y los intérpretes de cada fuente con sus copias de páginas.
- **Integración** (`tests/integration/test_extraccion_*.py`): recorrido completo con un cliente HTTP falso inyectado en el servicio (sin red): inicio, avance, recarga, resumen, detalle, descarga y listado. Matriz de acceso de las cinco rutas nuevas (SC-005). Aislamiento: después de extraer, los concursos, versiones, registros de cambio y jugadas no cambian (SC-004, AC-6.3 a AC-6.5). Contenido del CSV: encabezados, formato, duplicados, celdas con fórmulas y descargas idénticas (SC-008, AC-5.x).
- **Prueba estructural de aislamiento**: ningún módulo de `extracciones/` ni de `dominio/extraccion/` importa modelos de `resultados` ni de `jugadas` (RN-41).
- **Manual**: [quickstart.md](quickstart.md), con el servidor de fuentes de prueba y con las fuentes reales (SC-003, SC-006, SC-007).

## R-13 — Acceso y caché

- Todas las rutas usan `administrador_requerido` ([001] R-05), que ya responde "No tenés permisos para acceder a esta sección" con 403, lleva a iniciar sesión sin sesión y agrega `Cache-Control: no-store` (NFR-004), también en la descarga del CSV.
- La descarga se sirve con `Content-Type: text/csv; charset=utf-8` y `Content-Disposition: attachment`.

## R-14 — Volumen y tiempos (SC-007)

- Unos 104 sorteos por año. Por sorteo hay hasta tres consultas en paralelo, cada una limitada a una cada 2 s por sitio: el tiempo por sorteo es de unos 2 a 3 s.
- **12 meses**: unos 104 × 2,5 s ≈ 4,5 min, más los listados y la identificación (menos de 30 s). Queda por debajo de los 10 min de SC-007.
- **1 mes**: unos 9 × 2,5 s ≈ 25 s, más los listados. Queda por debajo de los 2 min.
- Con un sitio que no responde, cada consulta espera hasta 10 s. SC-007 se mide con todas las fuentes disponibles.

## R-15 — Dependencias

- **Ninguna nueva**. Se usan `urllib.request`, `html.parser`, `json`, `csv`, `concurrent.futures`, `threading` y `http.server` (solo pruebas) de la biblioteca estándar. Se cumple la lista cerrada de `CLAUDE.md`.
- `pyproject.toml` agrega a `[tool.setuptools] packages` los paquetes nuevos: `extracciones`, `extracciones.fuentes` y `dominio.extraccion`.

---

## R-16 — Prioridad de fuentes y desempate (Clarifications 20/11/2026, D-14 y D-21)

- **Decisión**: la prioridad vive en `ORDEN_FUENTES` (F2 → F3 → F1) y F1 está en `FUENTES_RESPALDO`. `servicios.consultar_sorteo` consulta F2 y F3, consolida en forma parcial y llama a `requiere_respaldo`. F1 se consulta si el sorteo queda "No recuperado", le falta un dato esperado, F2 y F3 difieren en un dato o una de ellas publica un dato inválido. En ese caso se le pide el sorteo con la fecha que informan las otras dos, aunque no figure en su listado (I-08 ampliada). Si no hace falta, su intento es `NO_REQUERIDA`: no cuenta como fallido ni como hueco.
- **Consolidación**: si 2 de 3 fuentes coinciden, ese valor gana. Se guarda como `diferencia_tolerada` de tipo `MAYORIA` ("Resuelto por coincidencia de 2 de 3 fuentes"), que es informativa. Si no hay mayoría, la diferencia se registra como discrepancia y el sorteo queda "Con inconsistencias" (Const. IX).
- **Justificación**: F2 y F3 son las más completas. F1 exige la fecha exacta en la dirección, así que usarla solo como respaldo ahorra consultas y respeta el ritmo de NFR-005.

## R-17 — Valores calculados y corregidos (Clarifications 20/11/2026, D-16 a D-20)

- **Decisión**: todo valor que calcula el sistema lleva `DatoConsolidado.calculo` con el texto del cálculo (`CALCULO_POZO` "importe individual × ganadores", `CALCULO_VACANTE`, `CALCULO_POZO_EXTRA` "unión de Tradicional, La Segunda y Revancha") y no tiene fuentes. Así nunca se presenta como publicado. La marca va siempre en la procedencia del CSV; en la pantalla solo se ve la de Pozo Extra (D-23).
- **Importes entre fuentes (D-17, D-28)**: dos importes coinciden si difieren en menos de $ 1,00 (también al agrupar la coincidencia de 2 de 3, D-21), y el consolidado toma el prioritario sin centavos; hay nota solo si ese importe tenía centavos. Si no coinciden y, sin centavos, difieren menos del 1 % del valor prioritario, se usa ese valor sin centavos y la diferencia queda en `diferencia_tolerada` de tipo `CENTAVOS`, que es informativa. Desde el 1 % hay discrepancia.
- **Importes mal cargados (D-18, D-20, D-31, D-32)**: el dominio corrige la coma corrida (último grupo de cuatro dígitos), los tres o más decimales, los puntos de miles mal puestos (tríos desde la derecha en la parte entera, si el último grupo tiene tres dígitos) y la coma en todos los separadores (dos o más comas, ningún punto y dos dígitos después de la última, que son los decimales), redondeando a centavos, con la observación informativa `obs.importe_corregido`.
- **Números de Pozo Extra (D-19)**: se calculan como la unión de los números de las tres modalidades y van en la columna `numeros_pozo_extra` del CSV, al final (contrato v2.0; v3.0 desde D-22).

## Interpretaciones técnicas de reglas aprobadas (aprobadas por el responsable el 19/11/2026, análisis)

| ID | Caso | Interpretación adoptada | Base |
|----|------|-------------------------|------|
| I-01 | RN-04 con inicio el 29/02 | "La misma fecha del año siguiente" es el 01/03. Del 29/02/2024 se puede pedir hasta el 28/02/2025. | RN-04 |
| I-02 | Fuentes que discrepan sobre la fecha de un sorteo en el borde del período | El número se incluye si **alguna** fuente informa una fecha dentro del período. La discrepancia de fechas lo deja "Con inconsistencias" (RN-22). Así no se pierde un sorteo por la fecha errónea de una fuente. | RN-05, RN-22 |
| I-03 | Cuándo un sorteo "Combina fuentes" | Cuando **ninguna fuente por sí sola** informa todos los datos presentes del consolidado. Si una fuente informa todo y otra solo una parte, no combina: corrobora. | RN-29 |
| I-04 | Límite entre "Valor distinto" y "Diferencia de centavos o redondeo" | ~~Es de centavos o redondeo cuando la diferencia absoluta es menor que $ 1,00. Ambos casos son discrepancias y dejan el valor "Sin determinar"; solo cambia el tipo informado.~~ **Reemplazada el 20/11/2026 por D-17** (ver R-17): los importes se redondean a pesos enteros y se comparan; una diferencia menor al 1 % es una nota informativa y no una discrepancia. | RN-27, RN-30 |
| I-05 | Qué sorteos "aportó" una fuente (resumen, AC-2.1) | Los sorteos en los que la fuente respalda al menos un dato del consolidado. | RN-33 |
| I-06 | Estado del pozo y aciertos cuando la cantidad de ganadores es "Sin determinar" | El estado del pozo también es "Sin determinar". Ningún importe se reclasifica entre pozo e importe individual mientras los ganadores estén en conflicto: el importe queda "Sin determinar". | RN-19, RN-20 |
| I-07 | Interrupción del trabajador (reinicio del servidor) | La extracción sigue "en curso" y el trabajador la reanuda al volver a iniciarse: conserva los sorteos ya procesados y repite las consultas del sorteo que quedó a medias, registrando la fecha y hora de la nueva consulta. No hay estado nuevo. | RN-44, Supuestos |
| I-08 | Cobertura de F1 | F1 cubre un sorteo si figura en su listado de sorteos anteriores o si F2 y F3 informan su fecha: como F1 exige la fecha exacta en la dirección, se usa la de su listado o, si no figura, la que informan las otras dos (ampliada el 20/11/2026, D-21; se verificó que F1 publica sorteos de 2025, como el 3235 y el 3308). Sin fecha conocida, el intento es "Fuera de cobertura". | RN-08, [analisis-fuentes.md](analisis-fuentes.md) |
| I-09 | Error inesperado mientras se procesa un sorteo | **Aprobada por el responsable el 19/11/2026 (análisis).** (a) Si el intérprete de una fuente lanza una excepción, ese intento queda "Estructura no reconocida" con la observación `obs.error_interprete` y las demás fuentes siguen. (b) Si falla otra parte del tratamiento del sorteo (normalización, consolidación, clasificación o guardado), el sorteo se guarda "No recuperado" con el motivo `motivo.error_inesperado`, sin datos de ninguna fuente, y la extracción continúa. El error se registra en el log. Así el avance llega al total y los cuatro estados suman los identificados. | RN-10, RN-31, RN-33, NFR-006 |
| I-10 | Cuándo un número es un hueco en la numeración | **Aprobada por el responsable el 19/11/2026 (análisis).** Es hueco ("Ninguna fuente informa este número de sorteo") solo si todas las fuentes que lo cubren respondieron "No encontrado" o "No disponible o no encontrado". Si alguna quedó "No disponible" o "Estructura no reconocida", el sorteo es "No recuperado" con el motivo de cada fuente y no se cuenta como hueco, porque no se sabe si esa fuente lo informa. | RN-05, RN-08, AC-1.16, AC-2.7 |
