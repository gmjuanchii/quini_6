# Investigación técnica (Fase 0): QUINI_6 — MVP v0

**Fecha**: 13/11/2026 | **Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md)

Este documento resuelve las incógnitas técnicas del plan. Indicación del responsable para esta etapa: **"es una versión inicial del producto de software"**. Por eso, cada decisión busca la opción más simple que cumpla la especificación (Const. XI) y deja de lado la infraestructura que el MVP no necesita.

Separación exigida por la Constitución (Flujo de trabajo):

- **Secciones R-xx**: decisiones técnicas. No cambian el comportamiento aprobado.
- **Sección "Interpretaciones a confirmar" (P-xx)**: puntos en los que la especificación es ambigua o incompleta. El plan propone una interpretación, pero **no la da por aprobada**. Hay que confirmarlas antes de implementar las tareas afectadas.
- **Sección "Decisiones pendientes de la spec"**: cómo trata el plan las decisiones D-12 a D-15, que siguen abiertas.

---

## R-01 — Lenguaje y framework

- **Decisión**: Python 3.12 con Django 5.2 LTS (soporte hasta abril de 2028).
- **Justificación**: Django resuelve con piezas nativas casi todo lo transversal que exige la spec: cuentas con contraseña hasheada (Const. IV), sesiones con vencimiento por inactividad (NFR-005), protección CSRF, ORM con migraciones, `DecimalField` para importes (NFR-007), soporte de zona horaria y plantillas renderizadas en el servidor. Es un monolito: un solo proceso, un solo despliegue y un solo lenguaje. Python 3.12.2 ya está instalado en la máquina de desarrollo.
- **Alternativas consideradas**:
  - *Next.js + TypeScript + Prisma*: es moderno, pero obliga a armar a mano la autenticación, las sesiones y el CSRF, y suma un paso de compilación del frontend. Es más complejo sin una ganancia que la spec necesite.
  - *API REST + SPA (React)*: dos proyectos, dos despliegues y autorización duplicada. La spec no tiene interacciones que justifiquen una SPA.
  - *Django 6.0*: es más nuevo, pero tiene un ciclo de soporte más corto. Para una versión inicial conviene la LTS.

## R-02 — Renderizado de la interfaz

- **Decisión**: plantillas de Django renderizadas en el servidor. Se usa JavaScript sin frameworks solo como mejora progresiva en el selector de números (R-10) y en la confirmación de acciones.
- **Justificación**: los recorridos son formularios y consultas. El HTML del servidor carga rápido en 4G (NFR-004) y la autorización se resuelve una sola vez, en el servidor (Const. IV).
- **Alternativas**: HTMX o Alpine.js (una dependencia más sin necesidad concreta) y SPA (descartada en R-01).

## R-03 — Almacenamiento

- **Decisión**: PostgreSQL 16 en producción y SQLite en desarrollo local y en las pruebas automatizadas. El modelo no usa funciones exclusivas de ningún motor. Las restricciones únicas parciales y los `CheckConstraint` funcionan en ambos.
- **Justificación**: SQLite permite arrancar en Windows sin instalar un servidor de base de datos. PostgreSQL da escrituras concurrentes y respaldos robustos en producción.
- **Riesgo y mitigación**: puede haber diferencias entre motores. Antes de cada publicación a producción, la suite completa se ejecuta contra PostgreSQL (ver [quickstart.md](quickstart.md), paso opcional).
- **Alternativas**: SQLite también en producción (exige un disco persistente y limita la concurrencia de escritura) y PostgreSQL en todos los entornos (más fricción para empezar a desarrollar).

## R-04 — Autenticación, sesiones y bloqueo

- **Decisión**:
  - Modelo de usuario propio (`cuentas.Usuario`) con el correo electrónico como identificador. El correo se normaliza a minúsculas para que sea único (FR-015) y solo se piden correo y contraseña (RN-39).
  - Hasher de contraseñas predeterminado de Django (PBKDF2). Validador de longitud mínima de 8 caracteres (NFR-005).
  - Sesiones en base de datos con `SESSION_COOKIE_AGE = 1800` y `SESSION_SAVE_EVERY_REQUEST = True`: vencen tras 30 minutos sin actividad (AC-3.10). Cookies `HttpOnly`, `Secure` (en producción) y `SameSite=Lax`.
  - Bloqueo por cuenta implementado en el propio servicio de inicio de sesión: los campos `intentos_fallidos` y `bloqueado_hasta` en el usuario. Con 5 fallos consecutivos, la cuenta queda bloqueada 15 minutos y un acierto pone el contador en cero (AC-3.6). El mensaje indica la hora en que se puede volver a intentar.
  - Las páginas personales y administrativas responden con `Cache-Control: no-store`, para que el botón "Atrás" no muestre datos después de cerrar la sesión (AC-3.7).
  - El parámetro `next` se valida con `url_has_allowed_host_and_scheme` para volver a la página que se quería abrir sin habilitar redirecciones abiertas (AC-3.8, AC-3.9, FR-017).
- **Alternativas**: django-allauth (agrega flujos de correo y de proveedores externos que están fuera del alcance), django-axes (bloquea por IP o usuario con más configuración de la necesaria) y JWT (complejidad sin beneficio en una aplicación renderizada en el servidor).

## R-05 — Autorización

- **Decisión**: en el servidor, en cada vista:
  - Funciones personales: `login_required` lleva a iniciar sesión conservando `next`.
  - Jugadas: todas las consultas parten de `Jugada.objects.filter(usuario=request.user)`. Una jugada ajena o inexistente devuelve la misma página 404, con "La jugada no existe o no está disponible" (RN-36, AC-4.12).
  - Administración: un decorador propio, `administrador_requerido`. Sin sesión, lleva a iniciar sesión (AC-2.12). Con una sesión sin permiso, devuelve 403 con "No tenés permisos para acceder a esta sección" (AC-2.11). Se verifica en GET y en POST (FR-011).
- **Justificación**: hay un único rol (RN-37), así que un campo booleano basta. Los grupos y permisos de Django serían complejidad innecesaria.
- **Verificación**: una matriz automatizada de acceso (visitante, usuario A, usuario B, administrador) × (todas las rutas privadas y administrativas) cubre SC-004.

## R-05b — Otorgamiento del permiso de administrador

- **Decisión**: dos comandos de gestión, `otorgar_admin <correo>` y `quitar_admin <correo>`, que ejecuta el responsable del proyecto en el servidor. La cuenta se crea antes por el registro público. **No se habilita `django.contrib.admin`**.
- **Justificación**: RN-37 dice que el permiso lo otorga el responsable y que no hay pantalla de gestión de permisos. El panel de Django agregaría pantallas no especificadas (Const. I y X).

## R-06 — Ciclo de vida de los resultados (estados, publicación y correcciones)

- **Decisión**: **versiones inmutables por bloque** y un **registro de cambios** aparte, de solo agregado.
  - Cada modalidad aplicable de un concurso (`ModalidadConcurso`) tiene un bloque de números (salvo Premio Extra, RN-15) y un bloque de premios.
  - Cada carga crea una versión (`VersionNumeros` o `VersionPremios`) con estado `BORRADOR`, `OBSERVADO`, `PUBLICADA` o `REEMPLAZADA`. Por bloque puede haber como máximo una versión `PUBLICADA` y una en trabajo (`BORRADOR` u `OBSERVADO`), lo que se garantiza con restricciones únicas parciales.
  - Una corrección (RN-23) es una nueva versión en trabajo, marcada como corrección, que convive con la publicada. El público sigue viendo la publicada hasta que la corrección cumple RN-17 y se publica. En ese momento, la anterior pasa a `REEMPLAZADA`.
  - El estado de RN-16 que ve el administrador y el estado público de RN-20 **se derivan** de esas versiones y del indicador `en_revision` del bloque. Ver [data-model.md](data-model.md).
- **Justificación**: cubre RN-16, RN-17, RN-18, RN-23 y NFR-006 sin perder valores anteriores (Const. IX). Las versiones permiten calcular la comparación con valores previos (P-03).
- **Alternativas**: columnas "borrador" y "publicado" en una misma fila (pierde el historial de valores), event sourcing (desproporcionado) y django-simple-history (historia genérica fila por fila, que no expresa el flujo de publicación).

## R-07 — Reglas de negocio como funciones puras

- **Decisión**: un paquete `dominio/` sin dependencias de Django, con funciones puras para validar números, contar aciertos, armar el conjunto de Premio Extra, determinar premios por modalidad (RN-28 a RN-33 y RN-49 a RN-54), calcular estadísticas (RN-40 a RN-45) y parsear y formatear importes. Las vistas cargan los datos, llaman al dominio y renderizan. Su interfaz está en [contracts/dominio.md](contracts/dominio.md).
- **Justificación**: separa la lógica de negocio de la presentación y de la infraestructura (Const. XI). Permite probar las reglas con los tres ejemplos de referencia y los escenarios AC-5.14 a AC-5.32 sin base de datos (SC-005). La comparación de jugadas no se guarda: se calcula en cada consulta, así que siempre refleja la información vigente (RN-32, FR-014).
- **Alternativas**: guardar la comparación calculada (habría que invalidarla ante cada corrección o edición, con riesgo de mostrar datos viejos) y poner la lógica en los modelos (la mezcla con el ORM).

## R-08 — Importes

- **Decisión**: `decimal.Decimal` de punta a punta y `DecimalField(max_digits=16, decimal_places=2)` en la base. El parseo de entrada en formato argentino acepta `1500,50`, `1.500,50` y `1500` y rechaza el valor vacío, los negativos, lo no numérico y más de dos decimales (AC-4.16). La salida usa un filtro propio que muestra `$ 1.500,50`. Nunca se usa `float`.
- **Justificación**: Const. IX y NFR-007. No depender de la configuración regional del sistema operativo hace que el formato sea determinista.
- **Alternativas**: enteros en centavos (igual de exactos, pero obligan a convertir en cada borde) y `float` (descartado por errores de redondeo).

## R-09 — Localización

- **Decisión**: `LANGUAGE_CODE = "es-ar"`, `TIME_ZONE = "America/Argentina/Buenos_Aires"` y `USE_TZ = True`. Filtros de plantilla propios: `fecha_ar` (`dd/mm/aaaa`), `fecha_hora_ar`, `pesos` (`$ 1.234,56`), `dos_digitos` (`07`) y `porcentaje_ar` (`12,50 %`). Todos los textos visibles están escritos directamente en español de Argentina, sin catálogos de traducción, porque el MVP tiene un solo idioma. El catálogo de mensajes está en [contracts/mensajes.md](contracts/mensajes.md).
- **Alternativas**: el sistema i18n de Django con archivos `.po` (no hace falta con un solo idioma) y los formatos regionales automáticos (menos predecibles entre versiones).

## R-10 — Selector de números de la jugada

- **Decisión**: una grilla de 46 casillas (`00` a `45`) presentadas como botones conmutables. Sin JavaScript, son casillas de verificación comunes y el servidor valida todo. Con JavaScript (mejora progresiva):
  - un campo "Escribí un número" con el botón "Agregar", que cubre la carga por teclado y los casos de valor fuera de rango, no numérico o repetido (AC-4.4, AC-4.5);
  - un contador "Te faltan N números" (AC-4.2);
  - el bloqueo de un séptimo número con su mensaje (AC-4.3);
  - la vista previa de las modalidades del concurso elegido (AC-4.6).

  El servidor repite **todas** las validaciones (RN-01 a RN-03), así que una solicitud manipulada no puede saltarlas.
- **Justificación**: es la solución más simple que hace observables desde la interfaz todos los criterios AC-4.2 a AC-4.5 (Const. VI) y deja el servidor como autoridad (Const. IV).

## R-11 — Gráfico de estadísticas

- **Decisión**: un gráfico de barras en SVG generado en el servidor, que se muestra junto con la tabla de los 46 números (FR-028). Cada barra tiene su texto accesible y la tabla es la alternativa equivalente (NFR-003).
- **Alternativas**: Chart.js o una biblioteca similar, que agregan una dependencia y JavaScript para un único gráfico estático.

## R-12 — Estilos y accesibilidad

- **Decisión**: una sola hoja de estilos propia con variables CSS (colores, tipografía y espacios), diseño fluido que empieza en 360 px (NFR-002) y contraste AA (NFR-003). Cada estado (con premio, sin premio, pendiente, en revisión, corregido) se comunica con texto además de color. Hay estados de carga, éxito, error y vacío en cada pantalla (NFR-008).
- **Alternativas**: Tailwind (necesita un paso de compilación) y Bootstrap (pesado para pocas pantallas y difícil de ajustar a una identidad propia).

## R-13 — Pruebas

- **Decisión**: `pytest` + `pytest-django`, en tres niveles:
  1. **Unitarias** sobre `dominio/`: los tres ejemplos de referencia, AC-5.14 a AC-5.32, los estados de RN-29, RN-33, las estadísticas con conteo manual (SC-006) y el parseo y formato de importes.
  2. **Integración** con el cliente de pruebas de Django: los recorridos de cada historia, la matriz de acceso (SC-004), la no visibilidad de lo no publicado (SC-003) y la propagación de las correcciones (SC-008).
  3. **Verificación funcional manual** desde la interfaz, siguiendo [quickstart.md](quickstart.md) (Const. VI: las pruebas automatizadas no reemplazan la verificación funcional).
- **Alternativas**: pruebas E2E con Playwright, que quedan diferidas porque suman un navegador y su mantenimiento. Se pueden proponer más adelante si la verificación manual resulta insuficiente.

## R-14 — Calidad de código

- **Decisión**: `ruff` (lint y formato). Las dependencias se fijan en `pyproject.toml`.
- **Dependencias de ejecución**: `Django`, `psycopg[binary]` (solo producción), `gunicorn` y `whitenoise` (archivos estáticos sin servidor aparte). **Desarrollo**: `pytest`, `pytest-django` y `ruff`. No hay otras.

## R-15 — Configuración y secretos

- **Decisión**: la configuración sensible (`SECRET_KEY`, credenciales de base de datos, `ALLOWED_HOSTS`, `DEBUG`) se lee de variables de entorno. Se versiona solo un archivo `.env.example` sin valores reales y `.env` queda en `.gitignore` (Const. IV).

## R-16 — Despliegue

- **Decisión**: un servidor Linux con Python 3.12, `gunicorn` detrás de un proxy con HTTPS, PostgreSQL 16 y `whitenoise` para los estáticos. El proveedor concreto queda fuera de este plan. No afecta el comportamiento y se decide al preparar el lanzamiento.
- **Nota**: la carga del historial inicial de 12 meses (FR-010) se hace **a mano** desde la aplicación ya desplegada, con el flujo de US2. No hay scripts de importación.

## R-17 — Volumen y rendimiento

- **Escala estimada**: alrededor de 104 concursos por año (dos sorteos semanales), con 4 extracciones de 6 números cada uno. Pocos administradores y un volumen de usuarios propio de un MVP.
- **Decisión**: las estadísticas y comparaciones se calculan en memoria con el dominio puro sobre los datos publicados del período (unos cientos de filas). Hay índices en `Concurso.fecha_sorteo`, `Concurso.numero` y `Jugada(usuario, concurso)`. El listado público de concursos no se pagina en el MVP. Se revisa si crece lo suficiente como para afectar NFR-004.

---

## Interpretaciones a confirmar (aprobadas el 13/11/2026)

La spec no resuelve del todo estos puntos. El plan propone una interpretación y la diseña para que cambiarla sea barato. **Se pide la confirmación del responsable antes de implementar las tareas indicadas** (Const. I: "ante una ambigüedad, el agente se detiene y consulta"). Cada decisión se incorpora a [spec.md](spec.md) (Clarifications y la RN o el AC que corresponda), y aquí solo se anota la referencia (decisión del responsable, 13/11/2026).

### P-01 — Cómo sale una modalidad del estado "En revisión"

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-01).

RN-16 define la entrada a "En revisión", pero no la salida.

- **Propuesta**: (a) al publicar una corrección, el bloque deja de estar en revisión; (b) el administrador puede quitar la marca indicando un motivo ("Revisión cerrada sin cambios"), sin modificar valores. Las dos acciones quedan en el registro de cambios.
- **Si no se aprueba (b)**: la única salida es publicar una corrección, aunque los valores no cambien. En ese caso aparecería "Corregido el …" sin un cambio real.
- **Afecta**: US7 (AC-7.1) y AC-1.12.

### P-02 — Seis aciertos frente a una categoría ganadora publicada menor, o "sin ganadores"

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-02).

En Siempre Sale, RN-52 (a) dice que 6 aciertos dan "Con premio" y RN-52 (e) dice que, si los aciertos superan la categoría ganadora publicada, el resultado es "Premio pendiente de determinación" con aviso. Las dos reglas chocan cuando la jugada tiene 6 aciertos y la categoría publicada es 5 o menos. En Premio Extra pasa lo mismo entre RN-31 (a) y RN-31 (c) y (e) cuando el extracto informa "sin ganadores" o una categoría de 4 o 5.

- **Propuesta**: (a) se aplica mientras la categoría ganadora no esté publicada o sea 6. Si está publicada con un valor menor (o "sin ganadores" en Premio Extra), prevalece (e): "Premio pendiente de determinación" con el aviso de RN-52 e, porque los datos de la jugada contradicen el extracto oficial (Const. VIII).
- **Afecta**: US5 (AC-5.21, AC-5.24, AC-5.30) y las pruebas de SC-005.

### P-03 — Cuándo mostrar "Actualizado por corrección del resultado oficial el dd/mm/aaaa"

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-03).

RN-32 dice "si cambian por una corrección publicada".

- **Propuesta**: el aviso aparece en una modalidad de la jugada solo si alguna corrección publicada de los bloques que usa esa modalidad **cambió alguno de los cinco datos de RN-29**. La fecha que se muestra es la de la corrección más reciente que produjo un cambio. Se calcula comparando la versión publicada antes y después de cada corrección.
- **Alternativa más simple**: mostrar el aviso siempre que algún bloque usado tenga una corrección publicada, aunque la jugada no cambie. Puede inducir a error.
- **Afecta**: AC-5.9 y AC-7.5.

### P-04 — Estado resumido de cada jugada en el historial (AC-5.13)

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-04).

- **Propuesta**, en orden de precedencia:
  1. Alguna modalidad "Con premio" y todas esas con importe publicado → **"Con premio"**.
  2. Alguna modalidad "Con premio" sin importe publicado → **"Con premio — información de premios pendiente de publicación"**.
  3. Alguna "Premio pendiente de determinación" → **"Premio pendiente de determinación"**.
  4. Alguna modalidad sin publicar → **"Resultado pendiente"**.
  5. En cualquier otro caso → **"Sin premio"**.
- **Afecta**: AC-5.13 y SC-009.

### P-05 — Modificar un concurso ya creado

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-05).

RN-05 menciona que un administrador puede cambiar las modalidades aplicables, pero ningún FR ni AC define esa operación.

- **Propuesta**: el administrador puede modificar la fecha del sorteo y las modalidades aplicables de un concurso. Puede agregar modalidades siempre. Solo puede quitar una modalidad si no tiene información cargada, y solo puede cambiar la fecha mientras ninguna extracción esté publicada. Cada cambio queda en el registro de cambios.
- **Afecta**: US2 y RN-05.

### P-06 — Premio Extra exige sus tres extracciones

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-06).

- **Propuesta**: al crear o modificar un concurso, si se marca Premio Extra, deben estar marcadas también Primer Sorteo, La Segunda y Revancha (de ellas sale su conjunto, RN-31). Si no lo están, la operación se rechaza con el mensaje "Premio Extra requiere Primer Sorteo, La Segunda y Revancha".
- **Afecta**: AC-2.1 y RN-13.

### P-07 — Búsqueda por fecha sin resultados

> **Decisión del responsable (13/11/2026)**: se aprueba la propuesta. Registrada en [spec.md](spec.md) → Clarifications (P-07).

AC-1.4 define el mensaje solo para la búsqueda por número.

- **Propuesta**: aplicar el mismo criterio a la búsqueda por fecha, con "No hay información de concursos del dd/mm/aaaa".
- **Afecta**: AC-1.3.

---

## Decisiones pendientes de la spec (D-12 a D-15): tratamiento en el plan

La spec las marca como no bloqueantes. El plan implementa **solo lo ya aprobado** y no adelanta ninguna opción no decidida.

| Decisión | Lo que implementa el plan | Qué cambia si se decide otra cosa |
|----------|---------------------------|-----------------------------------|
| D-12 — Visibilidad de "Pendiente de validación" | La interpretación escrita en la spec: el público ve el **estado**, nunca los valores sin validar (RN-17, RN-20). | Nada estructural. Solo cambian los textos. |
| D-13 — Detalle público de las correcciones | Solo "Corregido el dd/mm/aaaa" (lo aprobado en RN-24). | Si se elige B, se muestra el valor anterior, que ya existe en la versión `REEMPLAZADA`. No hace falta cambiar el modelo. |
| D-14 — Alcance de las estadísticas | Período por fechas, sin umbral mínimo, Primer Sorteo como modalidad predeterminada (RN-42 y RN-44, aprobadas "sujetas a D-14"). **No** se implementa la comparación lado a lado (RN-48 sigue pendiente). Cambiar el período y volver a consultar ya permite comparar uno después del otro. | Si se elige B, se agrega una vista nueva que usa la misma función del dominio. |
| D-15 — Recuperación de contraseña | **No se implementa** ninguna recuperación ni envío de correos, porque el envío de correos está fuera del alcance. | Si se aprueba B, hace falta una spec o enmienda con el flujo y un proveedor de correo. |

---

## Observación editorial sobre la spec

En `spec.md`, línea 177, AC-4.12 quedó pegado al final de AC-4.11 por un salto de línea faltante. No cambia el contenido. Se sugiere corregirlo en la próxima edición de la spec.
