# Plan de implementación (Implementation Plan): QUINI_6 — MVP v0

**Rama**: `001-quini6-mvp` (el proyecto no es un repositorio git) | **Fecha**: 13/11/2026 | **Spec**: [spec.md](spec.md)

**Entrada**: especificación funcional de `specs/001-quini6-mvp/spec.md` e indicación del responsable para esta etapa: *"es una versión inicial del producto de software"*.

**Marco normativo**: [Constitución QUINI_6 v1.1.0](../../.specify/memory/constitution.md).

## Resumen (Summary)

El MVP es una aplicación web pública e informativa del Quini 6 con tres bloques de valor:

1. **Consulta pública sin registro**: resultados, premios y estadísticas de frecuencia (US1, US6).
2. **Carga, validación, publicación y corrección trazable de resultados** por administradores (US2, US7).
3. **Seguimiento personal**: jugadas registradas por usuarios con cuenta y comparadas con los resultados oficiales según las reglas de cada modalidad (US3, US4, US5).

**Enfoque técnico.** Por ser una versión inicial, se elige la arquitectura más simple que cumple la spec: un **monolito Django 5.2 LTS (Python 3.12)** con plantillas renderizadas en el servidor, **PostgreSQL** en producción y **SQLite** en desarrollo y pruebas. Las reglas de negocio (aciertos, premios por modalidad, Premio Extra, estados y estadísticas) viven en un paquete **`dominio/` de funciones puras**, probado con los ejemplos de referencia de la spec. Los resultados se guardan como **versiones inmutables por bloque** (números o premios de cada modalidad) más un **registro de cambios** de solo agregado. Así se cubren a la vez la publicación por bloque, las correcciones sin perder valores y la auditoría. Las comparaciones y estadísticas **no se guardan**: se calculan en cada consulta, por lo que siempre reflejan la información vigente. El detalle está en [research.md](research.md).

## Contexto técnico (Technical Context)

| Aspecto | Decisión | Ref. |
|---------|----------|------|
| **Lenguaje y versión** | Python 3.12 | R-01 |
| **Dependencias principales** | Django 5.2 LTS; `gunicorn`, `whitenoise` y `psycopg[binary]` (producción). Desarrollo: `pytest`, `pytest-django` y `ruff`. Ninguna otra. | R-01, R-14 |
| **Almacenamiento** | PostgreSQL 16 (producción) y SQLite (desarrollo y pruebas) | R-03 |
| **Pruebas** | `pytest` + `pytest-django`: unitarias del dominio, integración de recorridos y matriz de acceso, y verificación manual con [quickstart.md](quickstart.md) | R-13 |
| **Plataforma objetivo** | Servidor Linux con HTTPS. Los clientes son navegadores actuales de escritorio y móviles (sin aplicación nativa) | R-16 |
| **Tipo de proyecto** | Aplicación web monolítica renderizada en el servidor | R-02 |
| **Objetivos de rendimiento** | Contenido visible en menos de 3 s en el 95 % de las consultas de resultados, historial y estadísticas en 4G (NFR-004). Páginas livianas: sin frameworks de JavaScript y con CSS propio | R-02, R-12, R-17 |
| **Restricciones** | es-AR, ARS y `America/Argentina/Buenos_Aires` (Const. VII). Importes en `Decimal` (NFR-007). WCAG 2.1 AA y ancho mínimo de 360 px (NFR-002, NFR-003). Autorización en el servidor en cada solicitud (Const. IV). Sin pagos (Const. V). Sin envío de correos ni integraciones externas (alcance) | R-04, R-05, R-08, R-09 |
| **Escala y alcance** | Unos 104 concursos por año, con un historial inicial de 12 meses cargado a mano. Pocos administradores y un volumen de usuarios propio de un MVP. 7 módulos, unas 25 rutas y unas 15 pantallas | R-17, [contracts/rutas.md](contracts/rutas.md) |

No quedan marcas `NEEDS CLARIFICATION` técnicas: todas se resolvieron en [research.md](research.md). Siguen abiertas **interpretaciones funcionales** (P-01 a P-07) que el plan no da por aprobadas (ver "Puntos a confirmar").

## Verificación contra la Constitución (Constitution Check)

*Compuerta: se evaluó antes de la Fase 0 y se reevaluó después del diseño de la Fase 1.*

| Principio | Cómo lo cumple el plan | Antes | Después del diseño |
|-----------|------------------------|:-----:|:------------------:|
| **I. SDD (no negociable)** | Cada ruta, entidad y función se vincula a un FR, una RN o un AC. Las decisiones D-12 a D-15 se implementan solo en su parte aprobada. Las ambigüedades se elevan como P-01 a P-07 en lugar de resolverse por suposición. No se habilita `django.contrib.admin` para no agregar pantallas no especificadas. | ✅ | ✅ |
| **II. Trazabilidad** | [contracts/rutas.md](contracts/rutas.md) indica el requisito de cada ruta. [contracts/dominio.md](contracts/dominio.md) vincula cada función con sus RN y casos de prueba. [quickstart.md](quickstart.md) vincula cada paso con sus AC. | ✅ | ✅ |
| **III. Acceso público / funciones personales** | Resultados y estadísticas son rutas públicas sin sesión. Las jugadas exigen sesión y pertenencia. | ✅ | ✅ |
| **IV. Aislamiento y seguridad** | Autorización en el servidor en cada GET y POST. Las consultas de jugadas se filtran por la cuenta, con 404 idéntico para jugadas ajenas e inexistentes. Contraseñas hasheadas. Bloqueo y vencimiento de sesión. CSRF. `no-store` en páginas privadas. `next` validado. Secretos en variables de entorno. Solo se pide correo y contraseña. | ✅ | ✅ |
| **V. Sin apuestas ni pagos** | Ninguna integración de pago. El costo de la jugada es un dato declarado. | ✅ | ✅ |
| **VI. Criterios verificables por personas no técnicas** | [quickstart.md](quickstart.md) define escenarios manuales desde la interfaz para cada historia. Las pruebas automatizadas son complementarias. | ✅ | ✅ |
| **VII. Español de Argentina** | `es-ar`, zona horaria de Buenos Aires, filtros propios de fecha, importe, dos dígitos y porcentaje, y el catálogo de [contracts/mensajes.md](contracts/mensajes.md). | ✅ | ✅ |
| **VIII. Exactitud de las reglas** | Las reglas por modalidad están en funciones puras probadas con los ejemplos de la spec. El importe es solo el publicado (nunca estimado). RN-33 se respeta con el corte del 18/06/2024. Premio Extra se calcula sobre su conjunto, sin Siempre Sale. | ✅ | ✅ |
| **IX. Integridad y trazabilidad** | Las versiones son inmutables, el registro de cambios es de solo agregado y hay fuente obligatoria para publicar. Las restricciones de base de datos impiden números inválidos y estados contradictorios. Importes en `Decimal`. | ✅ | ✅ |
| **X. Experiencia visual** | CSS propio con variables, diseño adaptable desde 360 px, AA y estados de carga, éxito, error y vacío. No se agregan pantallas ni componentes funcionales fuera de [contracts/rutas.md](contracts/rutas.md). | ✅ | ✅ |
| **XI. Simplicidad** | Un monolito, cuatro dependencias de ejecución, sin SPA, sin servicios extra y sin cachés. Toda complejidad adicional está justificada en "Seguimiento de complejidad". | ✅ | ✅ |

**Resultado de la compuerta: APROBADA.** No hay violaciones. Las interpretaciones P-01 a P-07 no son violaciones: son puntos abiertos que se elevan al responsable, como exige la Constitución.

## Estructura del proyecto (Project Structure)

### Documentación (esta funcionalidad)

```text
specs/001-quini6-mvp/
├── spec.md              # Especificación funcional (aprobada)
├── plan.md              # Este archivo
├── research.md          # Fase 0: decisiones técnicas e interpretaciones a confirmar
├── data-model.md        # Fase 1: entidades, restricciones y estados derivados
├── quickstart.md        # Fase 1: puesta en marcha y escenarios de validación
├── contracts/
│   ├── rutas.md         # Rutas web, niveles de acceso y respuestas de error
│   ├── dominio.md       # Interfaz de las reglas puras y casos de prueba obligatorios
│   ├── mensajes.md      # Catálogo de textos visibles (es-AR)
│   └── comandos.md      # Comandos de gestión (permiso de administrador)
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2: lo genera /speckit-tasks (no lo crea este comando)
```

### Código fuente (raíz del repositorio)

```text
manage.py
pyproject.toml                 # dependencias fijadas, configuración de pytest y ruff
.env.example                   # variables de entorno sin valores reales
quini6/                        # configuración del proyecto Django
├── settings.py                # es-ar, zona horaria, sesiones, seguridad y base por variables de entorno
├── urls.py
└── wsgi.py
dominio/                       # reglas de negocio puras (sin Django)
├── tipos.py
├── numeros.py                 # RN-01 a RN-03, RN-14
├── importes.py                # RN-09, RN-43, NFR-007
├── consistencia.py            # RN-22
├── comparacion.py             # RN-28 a RN-33, RN-49 a RN-54
└── estadisticas.py            # RN-40 a RN-47
cuentas/                       # M4: Usuario, registro, ingreso, bloqueo y salida
├── models.py
├── servicios.py               # ingreso con bloqueo (NFR-005)
├── views.py
├── forms.py
├── decoradores.py             # administrador_requerido, no_store
└── management/commands/       # otorgar_admin, quitar_admin
resultados/                    # M1, M2, M3: concursos, versiones y registro de cambios
├── models.py
├── servicios.py               # transiciones de estado, publicación (RN-17) y correcciones (RN-23)
├── consultas.py               # carga de DatosConcurso para el dominio y RN-19, RN-20, RN-25
├── views_publicas.py
├── views_admin.py
└── forms.py
jugadas/                       # M5, M6: jugadas personales y comparación
├── models.py
├── servicios.py               # RN-06, RN-07, RN-08
├── views.py
└── forms.py
estadisticas/                  # M7
└── views.py
templates/                     # plantillas por módulo + base.html + errores 403, 404 y 500
static/
├── css/app.css
└── js/selector-numeros.js     # mejora progresiva (R-10)

tests/
├── unit/                      # dominio: ejemplos de referencia, AC-5.14 a AC-5.32, estadísticas, importes
├── integration/               # recorridos por historia, matriz de acceso, publicación y corrección
└── conftest.py                # fixtures (incluye los ejemplos de referencia)
```

**Decisión de estructura**: un único proyecto Django con cuatro aplicaciones por módulo funcional y un paquete de dominio independiente. No se separan frontend y backend porque la interfaz se renderiza en el servidor (R-02). La administración de resultados comparte modelos con la consulta pública y por eso vive en la misma aplicación, `resultados`, con vistas separadas.

## Correspondencia entre módulos y requisitos

| Módulo de la spec | Código | FR | Historias |
|-------------------|--------|----|-----------|
| M1 Consulta pública | `resultados/views_publicas.py`, `resultados/consultas.py` | FR-001 a FR-005 | US1 |
| M2 Administración | `resultados/views_admin.py`, `resultados/servicios.py`, `dominio/consistencia.py` | FR-006 a FR-011 | US2 |
| M3 Corrección | `resultados/servicios.py` (correcciones), `RegistroCambio` | FR-012 a FR-014 | US7 |
| M4 Cuentas | `cuentas/` | FR-015 a FR-018 | US3 |
| M5 Jugadas | `jugadas/`, `dominio/numeros.py`, `dominio/importes.py` | FR-019 a FR-022 | US4 |
| M6 Comparación | `jugadas/views.py`, `dominio/comparacion.py` | FR-023 a FR-025 | US5 |
| M7 Estadísticas | `estadisticas/views.py`, `dominio/estadisticas.py` | FR-026 a FR-028 | US6 |

## Orden de construcción sugerido (insumo para `/speckit-tasks`)

1. **Base**: proyecto, configuración es-AR, plantilla base y CSS, modelo `Usuario`, decoradores de acceso y páginas de error.
2. **Dominio puro y sus pruebas**: números, importes, consistencia, comparación y estadísticas. Es la parte de mayor riesgo funcional y no depende de la interfaz.
3. **US2 + US1** (P1): concursos, versiones, publicación y consulta pública. Es el primer incremento que se puede mostrar.
4. **US3 → US4 → US5** (P2): cuentas, jugadas y comparación.
5. **US7** (P2): revisión, corrección e historial. Depende de P-01 y P-03.
6. **US6** (P3): estadísticas.
7. **Transversal**: matriz de acceso (SC-004), revisión de NFR-001 a NFR-003 y NFR-008, y validación completa con [quickstart.md](quickstart.md).

## Puntos a confirmar con el responsable (no bloquean el plan)

Detalle completo en [research.md → "Interpretaciones a confirmar"](research.md#interpretaciones-a-confirmar-no-aprobadas). Hay que resolverlos antes de implementar las tareas indicadas:

| ID | Tema | Bloquea las tareas de |
|----|------|-----------------------|
| P-01 | Salida del estado "En revisión" (¿se puede quitar la marca sin corregir?) | US7 |
| P-02 | Seis aciertos frente a una categoría ganadora publicada menor, o "sin ganadores" (Siempre Sale y Premio Extra) | US5 (dominio) |
| P-03 | Cuándo mostrar "Actualizado por corrección…" | US5 y US7 |
| P-04 | Precedencia del estado resumido en el historial | US5 |
| P-05 | Modificar la fecha y las modalidades de un concurso creado | US2 |
| P-06 | Premio Extra exige Primer Sorteo, La Segunda y Revancha | US2 |
| P-07 | Mensaje de búsqueda por fecha sin resultados | US1 |

Siguen abiertas en la spec, con este tratamiento: **D-12** (se implementa la interpretación escrita), **D-13** (solo "Corregido el …"), **D-14** (período por fechas y sin comparación lado a lado) y **D-15** (sin recuperación de contraseña).

## Seguimiento de complejidad (Complexity Tracking)

No hay violaciones de la Constitución. Se documentan los únicos elementos que superan el mínimo absoluto, como pide Const. XI:

| Elemento | Por qué se necesita | Alternativa más simple descartada porque |
|----------|---------------------|------------------------------------------|
| Versiones inmutables por bloque (`VersionNumeros`, `VersionPremios`) en lugar de una fila editable | RN-23 exige que una corrección en preparación conviva con el valor publicado y que se conserve el valor anterior. RN-18 exige publicar números y premios por separado. | Una fila con columnas "borrador" y "publicado" pierde el historial de valores y complica las correcciones sucesivas. |
| Paquete `dominio/` separado de las aplicaciones Django | Las reglas de premios son la parte más delicada (Const. VIII) y deben probarse sin base de datos contra los ejemplos de la spec (SC-005). | Poner la lógica en modelos o vistas mezcla la regla con el ORM y la hace más difícil de probar y de revisar. |
| Dos motores de base de datos (SQLite y PostgreSQL) | Arranque sin instalaciones en Windows y robustez en producción. | Un solo motor en todos los entornos: PostgreSQL agrega fricción local y SQLite limita la producción. El riesgo se mitiga con el paso 4 de [quickstart.md](quickstart.md). |
