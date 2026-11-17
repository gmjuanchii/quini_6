---

description: "Lista de tareas para implementar QUINI_6 — MVP v0"
---

# Tareas (Tasks): QUINI_6 — MVP v0

**Entrada**: documentos de diseño de `specs/001-quini6-mvp/`

**Prerrequisitos**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/rutas.md](contracts/rutas.md), [contracts/dominio.md](contracts/dominio.md), [contracts/mensajes.md](contracts/mensajes.md), [contracts/comandos.md](contracts/comandos.md), [quickstart.md](quickstart.md)

**Pruebas**: **SÍ se incluyen**. La Constitución (XI) exige pruebas automatizadas de las reglas de negocio y de los recorridos principales, y SC-005 exige un conjunto de pruebas con los ejemplos de referencia. En cada historia, las pruebas se escriben **primero** y deben **fallar** antes de implementar. Las pruebas no reemplazan la verificación manual de [quickstart.md](quickstart.md) (Const. VI).

**Organización**: las tareas se agrupan por historia de usuario para que cada una se pueda implementar y probar de forma independiente.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias con tareas incompletas).
- **[USn]**: historia de usuario a la que pertenece la tarea (US1 a US7 de [spec.md](spec.md)).
- Cada descripción incluye la ruta exacta del archivo.

## Convenciones de rutas

Proyecto Django único en la raíz del repositorio (`quini_6/`): `manage.py`, `quini6/`, `dominio/`, `cuentas/`, `resultados/`, `jugadas/`, `estadisticas/`, `templates/`, `static/` y `tests/` (ver [plan.md → Estructura del proyecto](plan.md#estructura-del-proyecto-project-structure)).

## Reglas obligatorias para quien implemente

1. **Textos visibles**: se usan **literalmente** los de [contracts/mensajes.md](contracts/mensajes.md). Los marcados con † fueron aprobados por el responsable el 13/11/2026 y se usan tal cual. También están aprobados los valores de NFR-005.
2. **Puntos a confirmar (P-01 a P-07)**: cada historia afectada empieza con una **tarea de compuerta**. No se implementa la tarea bloqueada hasta cerrar la compuerta. Cada decisión se **incorpora a [spec.md](spec.md)**: una entrada en Clarifications y el cambio en la regla (RN) o el criterio (AC) que corresponda. [research.md](research.md) solo la referencia. Si el responsable decide algo distinto de la propuesta, se ajustan la tarea y su prueba antes de implementarlas (Const. I).
3. **Decisiones abiertas de la spec**: se implementa solo lo aprobado. D-12: el público ve el **estado** "Pendiente de validación", nunca los valores. D-13: solo "Corregido el dd/mm/aaaa". D-14: período por fechas, sin umbral y **sin** comparación lado a lado (RN-48 no se implementa). D-15: **sin** recuperación de contraseña ni envío de correos.
4. **Prohibido agregar**: `django.contrib.admin`, rutas que no estén en [contracts/rutas.md](contracts/rutas.md), dependencias fuera de R-14 (Django, gunicorn, whitenoise, psycopg; pytest, pytest-django y ruff en desarrollo), importación de archivos o carga masiva (FR-010), predicciones o recomendaciones de números (RN-47) y cualquier pago (Const. V).
5. **Importes**: siempre `decimal.Decimal`, nunca `float`. Nunca se calcula ni se estima un importe individual (RN-27).
6. **Autorización**: se verifica en el servidor en **cada** `GET` y `POST` (Const. IV). La información no publicada (Borrador u Observado) nunca llega a una vista pública, a una comparación ni a una estadística (RN-17, SC-003).
7. **Reglas de negocio**: viven solo en `dominio/` (funciones puras, sin importar Django). Las vistas y los servicios las invocan y no repiten la lógica ([contracts/dominio.md](contracts/dominio.md)).

---

## Fase 1: Preparación (infraestructura compartida)

**Propósito**: crear el proyecto y su configuración básica.

- [X] T001 Crear la estructura de paquetes de plan.md con archivos `__init__.py` vacíos en `quini6/`, `quini6/templatetags/`, `dominio/`, `cuentas/`, `cuentas/management/`, `cuentas/management/commands/`, `resultados/`, `jugadas/`, `estadisticas/`, `tests/`, `tests/unit/` y `tests/integration/`, y crear las carpetas vacías `templates/`, `static/css/` y `static/js/` en la raíz del repositorio
- [X] T002 Crear `pyproject.toml` con: `requires-python = ">=3.12,<3.13"`. Dependencias de ejecución fijadas: `Django==5.2.*`, `gunicorn==23.*` y `whitenoise==6.*`. Extra `prod`: `psycopg[binary]==3.2.*`. Extra `dev`: `pytest==8.*`, `pytest-django==4.*` y `ruff==0.*`, sin ninguna otra (R-14). Usar el backend `setuptools` con la lista explícita de paquetes (`quini6`, `dominio`, `cuentas`, `resultados`, `jugadas` y `estadisticas`) para que funcione `pip install -e ".[dev]"`. En `[tool.pytest.ini_options]`: `DJANGO_SETTINGS_MODULE = "quini6.settings"`, `testpaths = ["tests"]` y `pythonpath = ["."]`. En `[tool.ruff]`: `target-version = "py312"`, `line-length = 100` y reglas `E`, `F`, `I`, `B` y `UP`
- [X] T003 [P] Crear `manage.py` (con `DJANGO_SETTINGS_MODULE=quini6.settings`), `quini6/wsgi.py` y `quini6/urls.py` con `urlpatterns = []`. No incluir `django.contrib.admin` (R-05b)
- [X] T004 [P] Crear `.env.example` **sin valores reales**, con comentarios en español, con estas variables: `QUINI6_SECRET_KEY=`, `QUINI6_DEBUG=1`, `QUINI6_ALLOWED_HOSTS=127.0.0.1,localhost`, `QUINI6_DB_NAME=` (vacía: se usa SQLite), `QUINI6_DB_USER=`, `QUINI6_DB_PASSWORD=`, `QUINI6_DB_HOST=` y `QUINI6_DB_PORT=5432` (R-15)
- [X] T005 [P] Crear `.gitignore` con `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, `staticfiles/`, `.pytest_cache/` y `.ruff_cache/` (R-15)

---

## Fase 2: Base (prerrequisitos que bloquean todas las historias)

**Propósito**: configuración, tipos y reglas compartidas del dominio, modelos persistidos de resultados, estados derivados, plantilla base y datos de prueba. Todo lo usa más de una historia.

**⚠️ CRÍTICO**: ninguna historia puede empezar hasta terminar esta fase.

- [X] T006 Implementar `quini6/settings.py` (R-01, R-03, R-04, R-09, R-15):
  1. Lector mínimo de `.env` escrito a mano, sin dependencias: líneas `CLAVE=valor`, ignora las vacías y las que empiezan con `#`, y no pisa variables de entorno ya definidas.
  2. `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` se leen de `QUINI6_*`. Si falta `QUINI6_SECRET_KEY` con `DEBUG` falso, se lanza `ImproperlyConfigured`.
  3. `INSTALLED_APPS`: `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles`, `quini6`, `cuentas`, `resultados`, `jugadas` y `estadisticas`, **sin** `django.contrib.admin`.
  4. Middleware de seguridad, `whitenoise.middleware.WhiteNoiseMiddleware`, sesiones, CSRF, autenticación, mensajes y clickjacking.
  5. `DATABASES`: PostgreSQL si `QUINI6_DB_NAME` tiene valor; si no, SQLite en `BASE_DIR / "db.sqlite3"`.
  6. `AUTH_USER_MODEL = "cuentas.Usuario"`, `LOGIN_URL = "/ingresar/"` y, en `AUTH_PASSWORD_VALIDATORS`, solo `MinimumLengthValidator` con `min_length: 8` (NFR-005).
  7. `LANGUAGE_CODE = "es-ar"`, `TIME_ZONE = "America/Argentina/Buenos_Aires"` y `USE_TZ = True`.
  8. Sesiones en base de datos con `SESSION_COOKIE_AGE = 1800`, `SESSION_SAVE_EVERY_REQUEST = True`, `SESSION_COOKIE_HTTPONLY = True` y `SESSION_COOKIE_SAMESITE = "Lax"`. `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` y HSTS solo cuando `DEBUG` es falso.
  9. `TEMPLATES` con `DIRS = [BASE_DIR / "templates"]`, `STATICFILES_DIRS = [BASE_DIR / "static"]`, `STATIC_ROOT = BASE_DIR / "staticfiles"` y `STORAGES` con `whitenoise.storage.CompressedManifestStaticFilesStorage` cuando `DEBUG` es falso (con `DEBUG` verdadero, el almacenamiento estándar).
  10. `DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"`.
- [X] T007 [P] Implementar `dominio/tipos.py` según [contracts/dominio.md](contracts/dominio.md) y data-model.md "Catálogos fijos", sin importar Django:
  - `Modalidad` (Enum `PRIMER_SORTEO`, `LA_SEGUNDA`, `REVANCHA`, `SIEMPRE_SALE` y `PREMIO_EXTRA`) con estas propiedades:
    - `nombre`: "Tradicional – Primer Sorteo", "Tradicional – La Segunda", "Revancha", "Siempre Sale" y "Premio Extra".
    - `slug`: `primer-sorteo`, `la-segunda`, `revancha`, `siempre-sale` y `premio-extra`.
    - `tiene_extraccion_propia`: falso solo en `PREMIO_EXTRA` (RN-15).
    - `categorias`: `PRIMER`/`SEGUNDO`/`TERCER` en las dos tradicionales, `UNICO` en Revancha y `GANADORA` en Siempre Sale y Premio Extra.
  - `ORDEN_MODALIDADES` en ese orden (AC-5.31).
  - `NOMBRE_CATEGORIA`: `PRIMER` = "Primer Premio" (6), `SEGUNDO` = "Segundo Premio" (5), `TERCER` = "Tercer Premio" (4) y `UNICO` = "Premio Revancha" (6).
  - Enum `EstadoBloque` (`SIN_CARGAR`, `BORRADOR`, `OBSERVADO`, `PUBLICADO` y `EN_REVISION`).
  - Dataclasses inmutables `BloqueNumerosVista(estado, numeros)`, `CategoriaPublicada(codigo, ganadores, importe_categoria, importe_individual, pozo_vacante_acumulado)`, `BloquePremiosVista(estado, categorias, aciertos_categoria_ganadora, sin_ganadores)` y `DatosConcurso(fecha_sorteo, modalidades, numeros, premios)`.
  - La constante `FECHA_VIGENCIA_REGLAS = date(2024, 6, 18)` (RN-33).
- [X] T008 [P] Escribir las pruebas (deben fallar) en `tests/unit/test_numeros.py` (RN-01 a RN-03, RN-14 y RN-31):
  - `parsear_numero`: `"07"` → 7; `"46"` y `"-1"` → `FUERA_DE_RANGO`; `"abc"` y `""` → `NO_NUMERICO`.
  - `validar_jugada`: cuatro valores → `FALTAN_N(2)`; siete → `SOBRAN`; dos `7` → `REPETIDO(7)`; seis válidos → `frozenset`.
  - `validar_extraccion` con los mismos casos.
  - `formatear(7) == "07"` y `formatear(45) == "45"`.
  - `misma_combinacion`: devuelve verdadero sin importar el orden.
  - `conjunto_premio_extra`: 8 números en el Ejemplo 1, 9 en el Ejemplo 2 y 13 en el Ejemplo 3 de la spec. Recibe solo Primer Sorteo, La Segunda y Revancha (AC-5.26, AC-5.28).
- [X] T009 [P] Escribir las pruebas (deben fallar) en `tests/unit/test_importes.py` (RN-09, RN-43, NFR-007):
  - `parsear_pesos`: `"1500,50"`, `"1.500,50"` y `"1500"` dan `Decimal("1500.50")` o `Decimal("1500")`. `"0"` es válido. `""` → `VACIO`; `"-1"` → `NEGATIVO`; `"abc"`, `"1500.50"` y `"1.50.0"` → `NO_NUMERICO`; `"10,505"` → `DEMASIADOS_DECIMALES`.
  - `formatear_pesos`: `Decimal("1500.50")` → `"$ 1.500,50"`, `Decimal("1234567.5")` → `"$ 1.234.567,50"` y `Decimal("0")` → `"$ 0,00"`.
  - `formatear_porcentaje(Decimal("12.5")) == "12,50 %"`, con redondeo `ROUND_HALF_UP`.
  - Pasar un `float` a cualquiera de estas funciones lanza `TypeError`.
- [X] T010 Implementar `dominio/numeros.py` hasta que pase `tests/unit/test_numeros.py`: `parsear_numero`, `validar_jugada`, `validar_extraccion`, `formatear`, `misma_combinacion` y `conjunto_premio_extra(primer_sorteo, la_segunda, revancha) -> frozenset` (unión sin repetidos; **nunca** incluye Siempre Sale, RN-31). Los errores son valores (`ErrorNumero` con código y número), no excepciones (depende de T007 y T008)
- [X] T011 [P] Implementar `dominio/importes.py` hasta que pase `tests/unit/test_importes.py`. Regla de parseo: la coma es el separador decimal. El punto solo se acepta como separador de miles con grupos de tres dígitos. Se permiten hasta dos decimales. Funciones: `parsear_pesos`, `formatear_pesos` y `formatear_porcentaje` (R-08; depende de T009)
- [X] T012 Implementar los filtros de plantilla de R-09 en `quini6/templatetags/formato_ar.py`, delegando en `dominio/`: `fecha_ar` (convierte a la hora local y da `dd/mm/aaaa`), `fecha_hora_ar` (`dd/mm/aaaa HH:MM`), `pesos` (`$ 1.234,56`; con `None` devuelve cadena vacía), `dos_digitos` (`07`) y `porcentaje_ar` (`12,50 %`) (depende de T010 y T011)
- [X] T013 Implementar `cuentas.Usuario` en `cuentas/models.py` sobre `AbstractBaseUser`, con `USERNAME_FIELD = "email"` y `REQUIRED_FIELDS = []`, y un `UsuarioManager` con `create_user(email, password)` que normaliza con `email.strip().lower()`. Campos de data-model.md:
  - `email`: `EmailField`, único. "Se normaliza a minúsculas."
  - `es_administrador`: `bool`, "por defecto `False`". "Solo se cambia con los comandos `otorgar_admin` y `quitar_admin`" (RN-37).
  - `fecha_alta`: `DateTimeField`.
  - `intentos_fallidos`: `SmallInteger`, "por defecto 0".
  - `bloqueado_hasta`: `DateTimeField`, `null`.

  No agregar ningún otro dato personal (RN-39). Generar `cuentas/migrations/0001_initial.py` con `python manage.py makemigrations cuentas` (depende de T006)
- [X] T014 Implementar los modelos de `resultados/models.py` según data-model.md, con `TextChoices` construidas desde `dominio.tipos.Modalidad`, y generar `resultados/migrations/0001_initial.py` (depende de T007 y T013). Restricciones literales:
  - **`Concurso`**: `numero` `PositiveIntegerField`, "único, indexado"; `fecha_sorteo` `DateField`, "indexado"; `creado_por` FK → Usuario (PROTECT); `creado_en`.
  - **`ModalidadConcurso`**: `concurso` FK (CASCADE); `modalidad` "Único junto con `concurso`"; `numeros_en_revision` y `premios_en_revision` (`bool`); `numeros_motivo_revision` y `premios_motivo_revision` (texto). Las reglas del modelo de datos se cumplen así:
    - "Obligatorio cuando `numeros_en_revision` es `True`" (y lo mismo para premios): con un `CheckConstraint` por bloque, que exige un motivo no vacío cuando la marca es `True`.
    - "Solo puede ser `True` si existe una `VersionNumeros` `PUBLICADA`" (y `VersionPremios` para premios): depende de otra tabla, así que se valida en `clean()` y en el servicio `marcar_revision` (T072).
  - **Clase abstracta `VersionBase`** con los metadatos comunes:
    - `fuente_descripcion` ("obligatorio para publicar") y `fuente_fecha_consulta` (`DateField`, "obligatorio para publicar");
    - `estado` (`BORRADOR`, `OBSERVADO`, `PUBLICADA` y `REEMPLAZADA`);
    - `motivo_observacion` ("Obligatorio al pasar a `OBSERVADO`");
    - `es_correccion` y `motivo_correccion` ("Obligatorio si `es_correccion`");
    - `creada_por`/`creada_en`, `actualizada_por`/`actualizada_en`, `publicada_por`/`publicada_en` (`null`) y `reemplazada_en` (`null`).
  - **`VersionNumeros(VersionBase)`**: FK `modalidad_concurso` (PROTECT); `n1`…`n6` `SmallIntegerField` con `CheckConstraint` "`0 ≤ n ≤ 45` y `n1 < n2 < … < n6`"; `clean()` rechaza la modalidad `PREMIO_EXTRA` (RN-15).
  - **`VersionPremios(VersionBase)`**: FK `modalidad_concurso` (PROTECT); `aciertos_categoria_ganadora` `SmallIntegerField` `null` ("Solo en Siempre Sale (0 a 6, RN-22) y en Premio Extra (6, 5 o 4). `null` = no publicada o no disponible"); `sin_ganadores` `bool` ("Solo en Premio Extra. Excluye un valor en `aciertos_categoria_ganadora`").
  - **En ambas versiones**: restricción única parcial "Como máximo una versión `PUBLICADA` por `modalidad_concurso`" y otra "Como máximo una versión en trabajo (`BORRADOR` u `OBSERVADO`) por `modalidad_concurso`".
  - **`PremioCategoria`**: FK `version_premios` (CASCADE); `categoria` "Único junto con `version_premios`. Debe pertenecer a la modalidad"; `ganadores` `PositiveIntegerField` `null`; `importe_categoria`, `importe_individual` y `pozo_vacante_acumulado` `Decimal(16,2)`, `null`, "≥ 0" (`CheckConstraint`).
  - **`RegistroCambio`**: `concurso` FK (PROTECT); `modalidad` `null`; `bloque` (`CONCURSO`, `NUMEROS` o `PREMIOS`); `accion` (`CREAR_CONCURSO`, `MODIFICAR_CONCURSO`, `GUARDAR_BORRADOR`, `OBSERVAR`, `RESOLVER_OBSERVACION`, `PUBLICAR`, `MARCAR_REVISION`, `QUITAR_REVISION`, `INICIAR_CORRECCION` y `PUBLICAR_CORRECCION`); `valor_anterior` y `valor_nuevo` (JSON `null`, importes como texto decimal `"1500.50"`); `autor` FK (PROTECT); `fecha_hora`; `motivo`; `fuente`. Sobrescribir `save()` para rechazar actualizaciones y `delete()` para rechazar borrados: es una tabla de solo agregado (NFR-006).
  - **Propiedad de las versiones de números**: `numeros` devuelve un `frozenset`, y un método asigna `n1`…`n6` ordenados a partir de un conjunto.
- [X] T015 [P] Implementar `cuentas/decoradores.py` (R-05, [contracts/rutas.md](contracts/rutas.md) "Niveles de acceso"):
  - `no_store`: agrega `Cache-Control: no-store` a la respuesta.
  - `sesion_requerida`: combina `login_required` (redirige a `/ingresar/?next=<ruta>`) con `no_store`.
  - `administrador_requerido`: sin sesión, redirige a `/ingresar/?next=<ruta>`; con una sesión sin `es_administrador`, renderiza `templates/403.html` con estado 403 y el texto "No tenés permisos para acceder a esta sección". Siempre aplica `no_store`.

  Los tres se verifican en `GET` y en `POST` (depende de T013)
- [X] T016 Crear `templates/base.html` y `static/css/app.css` (R-12, NFR-001 a NFR-004 y NFR-008):
  - **Página**: `<html lang="es-AR">`, `meta viewport`, enlace "Saltar al contenido", zona de mensajes de `django.contrib.messages` con `role="status"` y un indicador "Cargando…" que aparece al navegar o enviar formularios (script en línea mínimo, sin archivos nuevos).
  - **Navegación**, con rutas literales de [contracts/rutas.md](contracts/rutas.md) para no depender de rutas que todavía no existen: "Resultados" (`/resultados/`) y "Estadísticas" (`/estadisticas/`). Sin sesión: "Ingresar" y "Crear cuenta". Con sesión: "Mis jugadas" y un formulario `POST` a `/salir/` con CSRF. Con `es_administrador`: "Administración".
  - **CSS** con variables de color, tipografía y espacios; diseño fluido desde 360 px sin desplazamiento horizontal; contraste AA; foco visible; y clases de estado (`estado--con-premio`, `--sin-premio`, `--pendiente`, `--revision` y `--corregido`) que siempre acompañan un texto y nunca lo reemplazan (NFR-003).
- [X] T017 [P] Crear `templates/403.html` ("No tenés permisos para acceder a esta sección"), `templates/404.html` ("La página que buscás no existe") y `templates/500.html` ("Ocurrió un error. Intentá de nuevo en unos minutos.", autónoma: no extiende `base.html` ni usa contexto). Ninguna muestra detalles técnicos ([contracts/rutas.md](contracts/rutas.md) "Páginas de error")
- [X] T018 Crear `tests/fabricas.py` y `tests/conftest.py` (depende de T014):
  - **`tests/fabricas.py`**, funciones que escriben directamente con el ORM, sin pasar por los servicios de US2, para que cada historia se pruebe sola:
    - `crear_usuario(email, admin=False)`;
    - `crear_concurso(numero, fecha, modalidades=TODAS)`;
    - `cargar_numeros(concurso, modalidad, numeros, estado="PUBLICADA", fuente=..., es_correccion=False, publicada_en=None)`;
    - `cargar_premios(concurso, modalidad, categorias: dict, aciertos_categoria_ganadora=None, sin_ganadores=False, estado="PUBLICADA")`;
    - `marcar_en_revision(concurso, modalidad, bloque, motivo)`;
    - `EJEMPLOS_REFERENCIA`: los tres ejemplos de la spec, con la jugada y los números de cada modalidad, y una fábrica `crear_concurso_ejemplo(n, numero, fecha)` que los publica.
  - **`tests/conftest.py`**:
    - fixtures `usuario_a`, `usuario_b`, `admin`, `cliente_a`, `cliente_b` y `cliente_admin` (con `force_login`);
    - una fixture `autouse` que cambia `settings.STORAGES["staticfiles"]` a `django.contrib.staticfiles.storage.StaticFilesStorage` para no exigir `collectstatic` en las pruebas.
- [X] T019 Escribir las pruebas (deben fallar) en `tests/integration/test_consultas.py` para los estados derivados de data-model.md:
  - `estado_bloque`: sin versiones → `SIN_CARGAR`; solo `BORRADOR` → `BORRADOR`; solo `OBSERVADO` → `OBSERVADO`; `PUBLICADA` → `PUBLICADO`; `PUBLICADA` con revisión → `EN_REVISION`; `PUBLICADA` más una corrección en trabajo → `PUBLICADO` con la marca "corrección en preparación".
  - `completitud` (RN-19): sin resultados, incompleto y completo; una modalidad no aplicable no cuenta (AC-1.16).
  - `admite_jugadas` (RN-07): Borrador u Observado no lo cierran; una versión `PUBLICADA` o `REEMPLAZADA` sí.
  - `ultimos_resultados` (RN-25): el concurso con publicaciones y, por separado, el concurso pendiente más reciente.
  - `datos_concurso`: nunca expone números de una versión `BORRADOR` u `OBSERVADO` (SC-003).
  - `fecha_ultima_correccion`.

  Depende de T018.
- [X] T020 Implementar `resultados/consultas.py` hasta que pase `tests/integration/test_consultas.py` (depende de T014 y T019). Funciones:
  - `estado_bloque(modalidad_concurso, bloque) -> EstadoBloque` y `correccion_en_preparacion(...)`;
  - `version_vigente(modalidad_concurso, bloque)`: la versión `PUBLICADA` o `None`;
  - `completitud(concurso)`: los elementos son el bloque de números de cada modalidad aplicable con extracción propia más el bloque de premios de cada modalidad aplicable;
  - `admite_jugadas(concurso)`: verdadero si **ninguna** `VersionNumeros` está `PUBLICADA` o `REEMPLAZADA`;
  - `ultimos_resultados() -> (concurso_ultimos, concurso_actual_pendiente)`;
  - `datos_concurso(concurso) -> DatosConcurso`: solo valores publicados vigentes; `numeros` es `None` si el estado no es `PUBLICADO` ni `EN_REVISION`;
  - `fecha_ultima_correccion(modalidad_concurso, bloque) -> date | None`: el `publicada_en` local de la última versión con `es_correccion` que llegó a publicarse;
  - `vista_publica_concurso(concurso)`: por cada modalidad aplicable, en `ORDEN_MODALIDADES`, el estado público de números y de premios (RN-20), los números ordenados de forma ascendente (solo si están publicados), la fuente, la revisión, la fecha de corrección y, en Premio Extra, el estado derivado de RN-20 (`SIN_CARGAR` si alguna de Primer Sorteo, La Segunda o Revancha está sin cargar; si no, `BORRADOR` si alguna está en Borrador u Observado; `EN_REVISION` si las tres están publicadas y alguna en revisión; si no, `PUBLICADO`) y el conjunto de `dominio.numeros.conjunto_premio_extra` **solo** si las tres están publicadas: nunca un conjunto parcial. El bloque de premios de Premio Extra se informa por separado (RN-18).

  Usar `prefetch_related` para no hacer consultas por modalidad (NFR-004).

**Punto de control**: la base está lista. US3 y US1 pueden empezar en paralelo. US2 necesita US3 (ver "Dependencias").

---

## Fase 3: Historia de usuario 3 — Crear una cuenta y acceder a las funciones personales (Prioridad: P2) — habilitante

> **Se adelanta a las historias P1** porque los administradores de US2 y US7 necesitan iniciar sesión, y según R-05b su cuenta se crea por el registro público y luego se promueve con `otorgar_admin`. No cambia la prioridad funcional: es una dependencia técnica.

**Objetivo**: registro con correo y contraseña, inicio de sesión con bloqueo, cierre de sesión, vencimiento por inactividad, retorno a la página solicitada y comandos para otorgar y quitar el permiso de administrador.

**Prueba independiente**: crear una cuenta, iniciar sesión, llegar a `/mis-jugadas/` (área personal, por ahora vacía), cerrar sesión y comprobar que `/mis-jugadas/` vuelve a pedir el inicio de sesión (quickstart, escenario B).

### Pruebas de la historia 3 ⚠️ (escribir primero; deben fallar)

- [X] T021 [P] [US3] Escribir `tests/integration/test_us3_cuentas.py`:
  - **AC-3.1**: el registro válido crea la cuenta, inicia la sesión y lleva a `/mis-jugadas/`. El correo se guarda en minúsculas.
  - **AC-3.2**: un correo inválido muestra "Ingresá un correo electrónico válido." y una contraseña de 7 caracteres, "La contraseña debe tener al menos 8 caracteres.". En ambos casos no se crea la cuenta.
  - **AC-3.3**: con un correo existente, sin importar mayúsculas, aparece "Ya existe una cuenta con este correo electrónico. Iniciá sesión." y no se crea una segunda cuenta.
  - **AC-3.4**: el ingreso correcto da acceso a las funciones personales.
  - **AC-3.5**: con un correo inexistente o una contraseña incorrecta aparece "Correo electrónico o contraseña incorrectos", el mismo texto en los dos casos.
  - **AC-3.6**: cinco fallos muestran ese mensaje. El sexto intento, aun con la contraseña correcta, muestra "Por seguridad, bloqueamos el acceso por 15 minutos. Podés volver a intentar a las {hora}.". Pasados los 15 minutos (manipulando `bloqueado_hasta`), se puede ingresar y el contador vuelve a 0.
  - **AC-3.7**: `POST /salir/` lleva a `/resultados/`; después, `/mis-jugadas/` redirige a `/ingresar/?next=/mis-jugadas/`. Las páginas personales llevan `Cache-Control: no-store`.
  - **AC-3.8**: tras ingresar con `next`, se llega a la ruta pedida. Un `next` externo (`https://otro.sitio/`) se ignora y se usa `/mis-jugadas/`.
  - **AC-3.9**: `next=/mis-jugadas/nueva/?concurso=9001` se conserva al pasar de "Ingresar" a "Crear cuenta" y viceversa.
  - **AC-3.10**: con la sesión vencida (`expire_date` de la sesión en el pasado), una página personal pide iniciar sesión.
  - `GET /salir/` no cierra la sesión: solo `POST` con CSRF.
- [X] T022 [P] [US3] Escribir `tests/integration/test_comandos_admin.py` ([contracts/comandos.md](contracts/comandos.md)):
  - `otorgar_admin <correo>` pone `es_administrador = True` e imprime "Se otorgó el permiso de administrador a <correo>.".
  - Con un correo inexistente imprime "No existe una cuenta con el correo <correo>." y termina con el código de salida 1.
  - `quitar_admin` produce los mensajes equivalentes.

### Implementación de la historia 3

- [X] T023 [P] [US3] Implementar `cuentas/servicios.py` (R-04, NFR-005):
  - `registrar(email, password) -> Usuario | ErrorRegistro(CORREO_EXISTENTE)`, que normaliza el correo y usa el hasher de Django.
  - `ingresar(request, email, password) -> Ingreso(OK | CREDENCIALES_INCORRECTAS | BLOQUEADO(hasta))`:
    - si `bloqueado_hasta > ahora`, devuelve `BLOQUEADO` sin verificar la contraseña;
    - una contraseña incorrecta suma 1 a `intentos_fallidos`; al llegar a 5, fija `bloqueado_hasta = ahora + 15 min` y pone el contador en 0, pero ese quinto intento todavía responde `CREDENCIALES_INCORRECTAS`;
    - un correo inexistente responde `CREDENCIALES_INCORRECTAS`;
    - un acierto pone `intentos_fallidos = 0` y `bloqueado_hasta = None`, y llama a `django.contrib.auth.login`.

  Actualizar el contador con `select_for_update` dentro de `transaction.atomic`.
- [X] T024 [P] [US3] Implementar `cuentas/forms.py`. `RegistroForm` (correo y contraseña; solo esos dos datos, RN-39) usa los mensajes † "Ingresá un correo electrónico válido." y "La contraseña debe tener al menos 8 caracteres.". `IngresoForm` (correo y contraseña) solo valida que los campos no estén vacíos
- [X] T025 [US3] Implementar `cuentas/views.py`:
  - `registrarse` (`GET`/`POST`, público): si `registrar` devuelve `CORREO_EXISTENTE`, muestra "Ya existe una cuenta con este correo electrónico. Iniciá sesión." con un enlace a `/ingresar/?next=…`; si no, inicia la sesión y redirige a `next` o a `/mis-jugadas/`.
  - `ingresar` (`GET`/`POST`, público): muestra los textos de AC-3.5 y AC-3.6 con `{hora}` en formato `HH:MM` local y redirige a `next` o a `/mis-jugadas/`.
  - `salir` (solo `POST`): cierra la sesión y redirige a `/resultados/`.

  `next` se valida con `url_has_allowed_host_and_scheme` (FR-017) (depende de T023 y T024).
- [X] T026 [P] [US3] Crear `templates/cuentas/registrarse.html` y `templates/cuentas/ingresar.html`, que extienden `base.html`. Cada una tiene etiquetas `<label>` asociadas, errores junto a cada campo con `aria-describedby`, `next` en un campo oculto y un enlace cruzado ("¿No tenés cuenta? Creá una" / "¿Ya tenés cuenta? Ingresá") que conserva `next` (AC-3.9)
- [X] T027 [US3] Crear el área personal mínima: la vista `lista` en `jugadas/views.py`, decorada con `sesion_requerida`, que por ahora solo muestra "Todavía no registraste jugadas" y un acceso a `/mis-jugadas/nueva/`. Crear también `jugadas/urls.py` (`mis-jugadas/`) y `templates/jugadas/lista.html`. US4 la completa (T053)
- [X] T028 [US3] Crear `cuentas/urls.py` (`registrarse/`, `ingresar/` y `salir/`) e incluir `cuentas.urls` y `jugadas.urls` en `quini6/urls.py` (depende de T025 y T027)
- [X] T029 [P] [US3] Implementar los comandos `cuentas/management/commands/otorgar_admin.py` y `cuentas/management/commands/quitar_admin.py` según [contracts/comandos.md](contracts/comandos.md): buscan el correo normalizado, imprimen los mensajes exactos y terminan con el código 1 si no existe la cuenta (`CommandError` con `returncode=1`)

**Punto de control**: US3 funciona sola. Se pueden crear cuentas y otorgar el permiso de administrador desde la terminal.

---

## Fase 4: Historia de usuario 2 — Incorporar, validar y publicar resultados (Prioridad: P1) 🎯 MVP

**Objetivo**: un administrador crea concursos, carga números y premios por modalidad, los observa, resuelve observaciones y publica cada bloque por separado cuando cumple RN-17, y cada acción queda en el registro de cambios.

**Prueba independiente**: como administrador, crear un concurso, cargar el Primer Sorteo sin fuente, intentar publicar (se bloquea), observar, resolver, completar la fuente, confirmar el cotejo y publicar. En la base, la versión queda `PUBLICADA` y aparece la entrada `PUBLICAR` en `RegistroCambio` (quickstart, escenarios C1 a C3 y D1 a D4 y D6 a D7, en la parte administrativa).

### Compuerta de la historia 2

- [X] T030 [US2] **Compuerta P-05 y P-06**: confirmar con el responsable las propuestas P-05 (modificar la fecha y las modalidades de un concurso creado) y P-06 (Premio Extra exige Primer Sorteo, La Segunda y Revancha), e incorporar la decisión a `specs/001-quini6-mvp/spec.md`: Clarifications, RN-05, RN-13 y AC-2.1, más un criterio nuevo para modificar un concurso si se aprueba P-05. Agregar una referencia en `research.md`. Bloquea T035 y T038 en lo referido a "modificar" y a la validación de Premio Extra

### Pruebas de la historia 2 ⚠️ (escribir primero; deben fallar)

- [X] T031 [P] [US2] Escribir `tests/unit/test_consistencia.py` (RN-22):
  - **Bloqueantes en números**: 5 o 7 números, un número repetido, un número fuera de rango y falta de fuente (descripción o fecha).
  - **Bloqueantes en premios**: ganadores o importes negativos; categoría ganadora de Siempre Sale fuera de 0 a 6; categoría ganadora de Siempre Sale con `ganadores == 0`; categoría ganadora de Premio Extra que no sea 6, 5, 4 ni "sin ganadores"; `sin_ganadores` junto con un valor en `aciertos_categoria_ganadora`; falta de fuente.
  - **Advertencias**: los mismos seis números en otra modalidad del concurso; una categoría con ganadores sin importe individual; fecha del sorteo posterior a hoy al publicar números.
  - **Caso sin observaciones**: datos completos y correctos no dan bloqueantes ni advertencias.
- [X] T032 [P] [US2] Escribir `tests/integration/test_servicios_resultados.py`:
  - **Concurso**: `crear_concurso` crea las `ModalidadConcurso`, rechaza un número duplicado (RN-21) y aplica P-06.
  - **Borradores**: `guardar_borrador_numeros` crea o actualiza la única versión en trabajo; `guardar_borrador_premios` crea exactamente una `PremioCategoria` por categoría predefinida (AC-2.13).
  - **Observación**: `observar` exige un motivo; `resolver_observacion` vuelve a `BORRADOR`.
  - **Publicación**: `publicar` rechaza sin fuente, con bloqueantes, con advertencias sin confirmar, sin la casilla de cotejo o en estado `OBSERVADO`, y acepta cuando cumple RN-17. Publicar el bloque de números no publica el de premios (RN-18).
  - **Registro de cambios**: cada acción crea su entrada en `RegistroCambio` con autor, fecha y hora, y fuente (NFR-006).
  - **Restricción única**: un segundo borrador simultáneo del mismo bloque es imposible.
  - **Restricción de revisión**: guardar una `ModalidadConcurso` con `numeros_en_revision=True` y sin motivo lanza `IntegrityError`, y lo mismo para premios.
- [X] T033 [P] [US2] Escribir `tests/integration/test_us2_admin.py` sobre las rutas de administración:
  - **AC-2.1**: se crea el concurso con número, fecha y modalidades.
  - **AC-2.2**: con un número duplicado aparece "El concurso N.º {N} ya existe" con un enlace al panel existente.
  - **AC-2.3**: los números inválidos muestran el error concreto.
  - **AC-2.4**: el borrador no es visible para el público, lo que se verifica con `vista_publica_concurso`.
  - **AC-2.5**: publicar sin fuente informa qué falta.
  - **AC-2.6**: la publicación correcta pasa a "Publicado".
  - **AC-2.7**: se publica una modalidad y las demás siguen pendientes.
  - **AC-2.8**: Observado bloquea la publicación.
  - **AC-2.9**: los números iguales a los de otra modalidad exigen confirmar la advertencia.
  - **AC-2.10**: el bloque puede quedar en Borrador sin fuente.
  - **AC-2.11**: el usuario sin permiso recibe 403 con "No tenés permisos para acceder a esta sección" en `GET` y en `POST`, y nada cambia.
  - **AC-2.12**: el visitante es redirigido a `/ingresar/?next=…`.
  - **AC-2.13**: las categorías son fijas, se acepta "no disponible" en cada dato y Siempre Sale y Premio Extra piden la categoría ganadora (Premio Extra admite "sin ganadores").
  - `premio-extra/numeros` responde 404 (RN-15).

### Implementación de la historia 2

- [X] T034 [US2] Implementar `dominio/consistencia.py` hasta que pase `tests/unit/test_consistencia.py`: `revisar_numeros(numeros, otras_modalidades_del_concurso, fecha_sorteo, hoy, fuente)` y `revisar_premios(modalidad, categorias, aciertos_categoria_ganadora, sin_ganadores, fuente)`, que devuelven `(bloqueantes, advertencias)` con códigos y textos en español que indican qué falta o qué es inconsistente (AC-2.5) (depende de T031)
- [X] T035 [US2] Implementar en `resultados/servicios.py` las operaciones sobre concursos:
  - `crear_concurso(autor, numero, fecha_sorteo, modalidades)`:
    - exige al menos una modalidad;
    - aplica P-06 según la compuerta T030, con el texto † "Premio Extra requiere Primer Sorteo, La Segunda y Revancha";
    - rechaza duplicados con "El concurso N.º {N} ya existe";
    - crea las `ModalidadConcurso` y registra `CREAR_CONCURSO`.
  - `modificar_concurso(autor, concurso, fecha_sorteo, modalidades)`, según P-05 aprobada:
    - se pueden agregar modalidades siempre;
    - solo se quita una modalidad sin versiones;
    - la fecha solo cambia si `admite_jugadas(concurso)`;
    - registra `MODIFICAR_CONCURSO` con los valores anterior y nuevo.

  Todo dentro de `transaction.atomic` (depende de T020 y T030).
- [X] T036 [US2] Implementar en `resultados/servicios.py` el ciclo de vida de los bloques (data-model.md "Transiciones permitidas"):
  - `guardar_borrador_numeros(autor, modalidad_concurso, numeros, fuente_descripcion, fuente_fecha_consulta)`: valida con `dominio.numeros.validar_extraccion` y rechaza Premio Extra.
  - `guardar_borrador_premios(autor, modalidad_concurso, datos_por_categoria, aciertos_categoria_ganadora, sin_ganadores, fuente...)`: una fila por categoría predefinida y `null` = "no disponible".
  - `observar(autor, version, motivo)` y `resolver_observacion(autor, version)`.
  - `revisar_para_publicar(version) -> (bloqueantes, advertencias)`, que delega en `dominio/consistencia.py`.
  - `publicar(autor, version, advertencias_confirmadas: bool, cotejo_confirmado: bool)`: exige RN-17 (a) a (e); fija `publicada_por` y `publicada_en`; corre en `transaction.atomic` con `select_for_update` sobre la `ModalidadConcurso`.

  Cada operación crea su `RegistroCambio` (`GUARDAR_BORRADOR`, `OBSERVAR`, `RESOLVER_OBSERVACION` o `PUBLICAR`) con `valor_nuevo` en JSON (importes como texto decimal) y la fuente (depende de T034 y T035).
- [X] T037 [P] [US2] Implementar `resultados/forms.py`:
  - `ConcursoForm`: número, fecha `dd/mm/aaaa` y casillas de modalidades.
  - `NumerosForm`: seis campos de número de 00 a 45, fuente y fecha de consulta.
  - `PremiosForm`: un subformulario fijo por categoría de la modalidad, con ganadores, importe destinado, importe individual y pozo vacante o acumulado. Cada campo puede quedar vacío ("no disponible") y los importes se parsean con `dominio.importes.parsear_pesos`. Siempre Sale agrega la categoría ganadora (0 a 6 o "no publicada") y Premio Extra agrega 6, 5, 4, "sin ganadores" o "no publicada".
  - `MotivoForm`.
  - `PublicarForm`: la casilla "Confirmo que cotejé esta información con la fuente oficial" y la casilla para confirmar las advertencias.
- [X] T038 [US2] Implementar en `resultados/views_admin.py`, todas con `administrador_requerido`, las vistas de concurso:
  - `listado`: concursos con el estado RN-16 de cada bloque;
  - `nuevo`: AC-2.1 y AC-2.2, con un enlace al concurso existente;
  - `modificar`: P-05;
  - `panel`: cada modalidad con sus bloques, su estado, "corrección en preparación" y las acciones disponibles según el estado.

  Depende de T035 y T037.
- [X] T039 [US2] Implementar en `resultados/views_admin.py` las vistas de bloque, todas con `administrador_requerido`:
  - `numeros` (`GET`/`POST`);
  - `premios` (`GET`/`POST`);
  - `observar` (`POST`, con motivo);
  - `resolver` (`POST`);
  - `publicar`: el `GET` muestra los bloqueantes, las advertencias y la casilla de cotejo; el `POST` publica si se cumple RN-17 y, si no, vuelve a mostrar qué falta.

  Usar `messages` para los resultados de éxito y error (NFR-008) (depende de T036 y T038).
- [X] T040 [US2] Crear las rutas de administración de [contracts/rutas.md](contracts/rutas.md) en `resultados/urls_admin.py`:
  - `administracion/concursos/`, `nuevo/`, `<numero>/`, `<numero>/modificar/`, `<numero>/<modalidad>/numeros/`, `<numero>/<modalidad>/premios/` y `<numero>/<modalidad>/<bloque>/{observar,resolver,publicar}/`;
  - convertidores registrados para `<modalidad>` (los 5 *slugs*) y `<bloque>` (`numeros` o `premios`);
  - la combinación `premio-extra` + `numeros` responde 404.

  Incluirlas en `quini6/urls.py` (depende de T039).
- [X] T041 [P] [US2] Crear `templates/resultados/admin/listado.html`, `templates/resultados/admin/concurso_form.html` (nuevo y modificar) y `templates/resultados/admin/panel.html`, con los estados RN-16 escritos en texto ("Sin cargar", "Borrador", "Observado", "Publicado", "En revisión" y "corrección en preparación"), las fechas con `fecha_ar` y estados vacíos y de error visibles (NFR-008)
- [X] T042 [P] [US2] Crear `templates/resultados/admin/numeros.html`, `templates/resultados/admin/premios.html` (tabla accesible por categoría con "no disponible" explícito) y `templates/resultados/admin/publicar.html` (lista de bloqueantes, lista de advertencias con su casilla de confirmación y casilla de cotejo)

**Punto de control**: US2 funciona sola. Los administradores pueden cargar y publicar el historial inicial (FR-010).

---

## Fase 5: Historia de usuario 1 — Consultar resultados del Quini 6 sin registrarse (Prioridad: P1) 🎯 MVP

**Objetivo**: consulta pública de los últimos resultados, el listado, las búsquedas por número y por fecha y el detalle con números, premios, fuente, completitud, revisión y corrección.

**Prueba independiente**: con concursos publicados por las fábricas de `tests/fabricas.py` en distintos estados (completo, incompleto, pendiente, en revisión y corregido), una persona sin cuenta recorre `/resultados/` y el detalle sin que se le pida iniciar sesión (quickstart, escenario A y lo público de D y F).

### Compuerta de la historia 1

- [X] T043 [US1] **Compuerta P-07**: confirmar con el responsable el mensaje de búsqueda por fecha sin resultados († "No hay información de concursos del {fecha}") e incorporar la decisión a `specs/001-quini6-mvp/spec.md` (Clarifications y AC-1.3 o un AC nuevo junto a AC-1.4), con una referencia en `research.md`. El texto ya está aprobado (K2); falta confirmar el comportamiento. Bloquea la parte de búsqueda por fecha de T045

### Pruebas de la historia 1 ⚠️ (escribir primero; deben fallar)

- [X] T044 [P] [US1] Escribir `tests/integration/test_us1_consulta.py`, todo sin sesión:
  - **Últimos resultados**:
    - AC-1.1: `/resultados/` muestra el número, la fecha `dd/mm/aaaa` y los números con dos dígitos en orden ascendente, sin pedir el inicio de sesión.
    - AC-1.2: el concurso más reciente sin publicar aparece con "Resultados pendientes" y aparte, rotulado con su número y fecha, el último concurso publicado.
    - AC-1.13: sin concursos publicados aparece "Todavía no hay resultados publicados", sin números ni importes.
    - `/` redirige a `/resultados/`.
  - **Búsquedas**:
    - AC-1.3: la búsqueda por número redirige a `/resultados/N/` y la búsqueda por fecha lista los concursos de esa fecha.
    - AC-1.4: aparece "No hay información del concurso N.º {N}" y no se muestra ningún otro concurso.
    - P-07: aparece el mensaje de la fecha sin concursos.
  - **Estados de las modalidades y del concurso**:
    - AC-1.5: "Resultado pendiente" (sin cargar), "Pendiente de validación" (Borrador u Observado, sin mostrar sus valores) e "Incompleto".
    - AC-1.6: "Completo".
    - AC-1.16: una modalidad no aplicable no aparece ni afecta la completitud.
  - **Premios**:
    - AC-1.7: cada dato de cada categoría tiene su propio rótulo.
    - AC-1.8: "Información de premios pendiente de publicación".
    - AC-1.9: una categoría publicada sin importe individual muestra en ese dato "Información de premios pendiente de publicación" y ningún importe calculado. El texto "Importe individual no disponible" no aparece en ninguna pantalla.
    - AC-1.10: "0 ganadores", y el pozo vacante solo si fue publicado.
  - **Revisión y corrección**:
    - AC-1.11: "Corregido el dd/mm/aaaa".
    - AC-1.12: "Información en revisión".
  - **Premio Extra y fuente**:
    - AC-1.14: Premio Extra muestra su conjunto de números distintos y sus premios, nunca como seis números propios. Con La Segunda sin cargar muestra "Resultado pendiente"; con Revancha en Borrador muestra "Pendiente de validación". En los dos casos no aparece ningún conjunto parcial, y sus premios publicados se ven igual.
    - AC-1.15 y SC-007: se muestra la fuente de cada modalidad publicada.

### Implementación de la historia 1

- [X] T045 [US1] Implementar `resultados/views_publicas.py`, todas públicas y sin decoradores de sesión:
  - `inicio`: redirige a `/resultados/`.
  - `resultados`: usa `ultimos_resultados()` y `vista_publica_concurso()` y lista todos los concursos ordenados por `fecha_sorteo` descendente, cada uno con su completitud.
  - `buscar`:
    - `?numero=N` existente → redirige a `/resultados/N/`;
    - `?numero=N` inexistente → "No hay información del concurso N.º {N}";
    - `?fecha=dd/mm/aaaa` → concursos de esa fecha o el mensaje de P-07;
    - fecha o número con formato inválido → mensaje de error de formato.
  - `detalle(numero)`: responde 404 con "La página que buscás no existe" si no existe el concurso.

  Depende de T020 y T043.
- [X] T046 [US1] Crear `resultados/urls.py` con `""` → `inicio`, `resultados/`, `resultados/buscar/` y `resultados/<int:numero>/`, e incluirlo en `quini6/urls.py` (depende de T045)
- [X] T047 [P] [US1] Crear `templates/resultados/index.html`: bloque "Últimos resultados", bloque separado del concurso actual pendiente ("Resultados pendientes"), formulario de búsqueda por número y por fecha, listado de concursos y estado vacío "Todavía no hay resultados publicados". Crear también `templates/resultados/busqueda.html` con los mensajes de AC-1.4 y P-07
- [X] T048 [P] [US1] Crear `templates/resultados/detalle.html` y el parcial `templates/resultados/_modalidad.html`:
  - Encabezado con el número, la fecha y la completitud ("Completo", "Incompleto" o "Resultados pendientes").
  - Por cada modalidad aplicable, en orden:
    - el estado público (RN-20), los números con `dos_digitos`, la fuente, "Información en revisión" y "Corregido el {fecha}";
    - la tabla de premios por categoría, con los rótulos separados para ganadores, importe destinado, importe individual (o "Información de premios pendiente de publicación") y pozo vacante o acumulado (solo si fue publicado), o "Información de premios pendiente de publicación";
    - en Premio Extra, "Conjunto de números del Premio Extra" con la cantidad real de números distintos, solo si sus tres extracciones están publicadas; si no, su estado ("Resultado pendiente" o "Pendiente de validación") en lugar del conjunto.

  Los estados siempre se indican con texto (NFR-003).

**Punto de control**: US1 y US2 funcionan. Es el **primer incremento que se puede mostrar** (MVP): un administrador publica y cualquier persona consulta.

---

## Fase 6: Historia de usuario 4 — Registrar y gestionar mis jugadas (Prioridad: P2)

**Objetivo**: registrar jugadas con seis números, un concurso abierto y un costo; ver el historial y el detalle; editar y eliminar mientras el concurso no tenga números publicados; y aislar las jugadas entre cuentas.

**Prueba independiente**: con una cuenta y concursos creados por las fábricas, registrar jugadas válidas e inválidas, editarlas y eliminarlas, verificar el historial vacío y comprobar que la jugada de otra cuenta responde "La jugada no existe o no está disponible" (quickstart, escenarios C4 a C8 y D5).

### Pruebas de la historia 4 ⚠️ (escribir primero; deben fallar)

- [X] T049 [P] [US4] Escribir `tests/integration/test_us4_jugadas.py`:
  - **Registro y validaciones**:
    - AC-4.1: aparece "Jugada registrada" y el historial muestra el concurso, la fecha, "$ 1.500,50", las modalidades del concurso y los números con dos dígitos.
    - AC-4.2: con cuatro números aparece "Te faltan 2 números".
    - AC-4.3: con siete números aparece "La jugada admite exactamente seis números".
    - AC-4.4: con `46` o `abc` aparece "Ingresá un número entre 00 y 45".
    - AC-4.5: aparece "El 07 ya está en tu jugada" y la jugada no se guarda.
    - AC-4.6: sin concurso aparece "Elegí el concurso de tu jugada"; el formulario no ofrece elegir modalidades y muestra las del concurso.
  - **Concurso de la jugada**:
    - AC-4.7: con `?concurso=` inexistente aparece "Este concurso todavía no está disponible para registrar jugadas".
    - AC-4.8: con un concurso que tiene una extracción publicada aparece "Ya no se pueden registrar jugadas para este concurso porque sus resultados fueron publicados"; un concurso pasado con todo en Borrador acepta la jugada.
    - AC-4.9: la jugada nueva figura como "Resultado pendiente".
  - **Edición y eliminación**:
    - AC-4.10: aparece "Jugada actualizada".
    - AC-4.11: el `GET` pide confirmación y el `POST` muestra "Jugada eliminada"; si se cancela, no cambia nada.
    - AC-4.17: con una extracción publicada no aparecen las opciones de editar ni de eliminar y se muestra "Esta jugada no se puede modificar ni eliminar porque los resultados de su concurso ya fueron publicados"; la dirección directa de edición o eliminación, por `GET` o `POST`, muestra el mismo aviso y no cambia nada.
  - **Aislamiento entre cuentas**:
    - AC-4.12: la usuaria A recibe 404 con "La jugada no existe o no está disponible" al ver, editar o eliminar (`GET` y `POST`) una jugada de B y una inexistente. La respuesta es idéntica en los dos casos y la jugada de B no cambia.
  - **Historial**:
    - AC-4.13: sin jugadas aparece "Todavía no registraste jugadas" con un acceso para registrar la primera.
    - AC-4.14: una segunda jugada distinta se guarda sin advertencia; una idéntica muestra "Ya registraste una jugada con estos números para este concurso. ¿Querés guardarla igual?" y se guarda solo con `confirmar_duplicado=1`. Lo mismo ocurre al editar.
    - AC-4.15: orden por fecha del sorteo descendente.
  - **Costo** (AC-4.16): vacío → "Ingresá el costo de tu jugada"; negativo, no numérico o con tres decimales → "Ingresá un importe válido, mayor o igual a cero y con hasta dos decimales (por ejemplo, 1500,50)".
  - **AC-3.9**: el detalle público de un concurso abierto muestra "Registrar una jugada" y no lo muestra si está cerrado.

### Implementación de la historia 4

- [X] T050 [US4] Implementar `jugadas.Jugada` en `jugadas/models.py` según data-model.md:
  - `usuario`: FK → Usuario (CASCADE), indexado.
  - `concurso`: FK → Concurso (PROTECT).
  - `n1`…`n6`: `SmallIntegerField` con "Las mismas restricciones que `VersionNumeros`" (`0 ≤ n ≤ 45` y `n1 < n2 < … < n6`).
  - `costo`: `Decimal(16,2)`, "obligatorio, ≥ 0" (`CheckConstraint`).
  - `creada_en` y `modificada_en`.
  - Índice `(usuario, concurso)`. "**No** hay restricción de unicidad sobre los números".
  - Propiedad `numeros` y asignación ordenada.

  Generar `jugadas/migrations/0001_initial.py` (depende de T014).
- [X] T051 [US4] Implementar `jugadas/servicios.py` (RN-04 a RN-10):
  - `concursos_disponibles()`: los concursos con `admite_jugadas`, ordenados por fecha.
  - `resolver_concurso(numero) -> Concurso | ErrorConcurso(NO_DISPONIBLE | CERRADO)`.
  - `hay_duplicado(usuario, concurso, numeros, excluir_id=None)`, con `misma_combinacion`.
  - `registrar_jugada(usuario, concurso, numeros, costo, confirmar_duplicado)` y `editar_jugada(jugada, concurso, numeros, costo, confirmar_duplicado)`. Ambas vuelven a verificar RN-07 sobre el concurso destino y devuelven `REQUIERE_CONFIRMACION` si hay un duplicado sin confirmar.
  - `es_modificable(jugada)`: `admite_jugadas(jugada.concurso)`.
  - `eliminar_jugada(jugada)`: rechaza la eliminación si la jugada no es modificable (RN-08).

  Depende de T050.
- [X] T052 [US4] Implementar `jugadas/forms.py` (`JugadaForm`) (R-10):
  - `concurso`: el número, elegido entre `concursos_disponibles()`.
  - `numeros`: selección múltiple de 00 a 45, renderizada como 46 casillas.
  - `numero_escrito`: opcional, para la carga por teclado.
  - `costo`: texto.
  - `confirmar_duplicado`: oculto.

  La validación del servidor usa `dominio.numeros.validar_jugada` y `dominio.importes.parsear_pesos` y produce exactamente los textos de [contracts/mensajes.md](contracts/mensajes.md) "Jugadas" (depende de T051).
- [X] T053 [US4] Completar `jugadas/views.py`:
  - `lista` (`sesion_requerida`): jugadas de `Jugada.objects.filter(usuario=request.user)` ordenadas por `concurso__fecha_sorteo` y luego por `creada_en`, ambos de forma descendente. Cada una muestra su concurso, su fecha, su costo con `pesos`, sus modalidades y el estado "Resultado pendiente" si el concurso no tiene números publicados (US5 lo reemplaza por el estado resumido).
  - `nueva` (`GET`/`POST`): preselecciona `?concurso=N` o muestra el error de AC-4.7 o AC-4.8; el segundo envío confirma un duplicado.
  - `detalle`.
  - `editar` (`GET`/`POST`) y `eliminar` (`GET` de confirmación y `POST`): si la jugada no es modificable, redirigen al detalle con el mensaje de AC-4.17 sin cambiar nada.
  - Helper `_jugada_propia(request, id)`: renderiza `templates/jugadas/no_existe.html` con estado 404 y "La jugada no existe o no está disponible", tanto para una jugada ajena como para una inexistente (RN-36).

  Depende de T052.
- [X] T054 [US4] Agregar a `jugadas/urls.py` las rutas `mis-jugadas/nueva/`, `mis-jugadas/<int:id>/`, `mis-jugadas/<int:id>/editar/` y `mis-jugadas/<int:id>/eliminar/` (depende de T053)
- [X] T055 [P] [US4] Crear o actualizar las plantillas de jugadas:
  - `templates/jugadas/lista.html`: estado vacío con acceso a la primera jugada y lista con estados en texto.
  - `templates/jugadas/formulario.html`: grilla de 46 casillas con `<fieldset>` y `<legend>`, vista previa "Participará en: …" con las modalidades del concurso elegido y bloque de advertencia de duplicado con los botones "Guardar igual" y "Cancelar".
  - `templates/jugadas/detalle.html`: datos de la jugada; opciones de editar y eliminar solo si es modificable y, si no, el aviso de AC-4.17.
  - `templates/jugadas/eliminar.html`: "¿Querés eliminar esta jugada? Esta acción no se puede deshacer." con "Eliminar" y "Cancelar".
  - `templates/jugadas/no_existe.html`.
- [X] T056 [P] [US4] Crear `static/js/selector-numeros.js` como mejora progresiva (R-10). El servidor repite **todas** las validaciones, y sin JavaScript el formulario funciona con las casillas:
  - contador "Te faltan {n} números" (AC-4.2);
  - bloqueo del séptimo número con "La jugada admite exactamente seis números" (AC-4.3);
  - campo "Escribí un número" con el botón "Agregar", que rechaza los valores fuera de rango o no numéricos con "Ingresá un número entre 00 y 45" (AC-4.4) y los repetidos con "El {nn} ya está en tu jugada" (AC-4.5);
  - actualización de la vista previa de modalidades al cambiar el concurso (AC-4.6);
  - mensajes en una región `aria-live="polite"`.
- [X] T057 [US4] Agregar a `templates/resultados/detalle.html` el botón "Registrar una jugada", que enlaza a `/mis-jugadas/nueva/?concurso={numero}`, visible solo si `admite_jugadas(concurso)` (AC-3.9). La vista `detalle` de `resultados/views_publicas.py` pasa ese dato al contexto (depende de T048)

**Punto de control**: US3 y US4 funcionan juntas. Un usuario registra y gestiona sus jugadas.

---

## Fase 7: Historia de usuario 5 — Comparar mis jugadas con los resultados oficiales (Prioridad: P2)

**Objetivo**: mostrar para cada jugada y cada modalidad los cinco datos de RN-29 con las reglas de RN-28 a RN-33 y RN-49 a RN-54, y un estado resumido en el historial.

**Prueba independiente**: con los tres ejemplos de referencia cargados por las fábricas, el detalle de cada jugada muestra exactamente los aciertos, la elegibilidad y el resultado de premio de la spec (quickstart, escenario E; SC-005).

### Compuerta de la historia 5

- [X] T058 [US5] **Compuerta P-02 y P-04**: confirmar con el responsable P-02 (seis aciertos frente a una categoría ganadora publicada menor o "sin ganadores": prevalece "Premio pendiente de determinación" con aviso) y P-04 (precedencia del estado resumido), e incorporar la decisión a `specs/001-quini6-mvp/spec.md` (Clarifications, RN-52, RN-31 y AC-5.13, más los criterios de AC-5.21 y AC-5.24 que correspondan), con una referencia en `research.md`. Bloquea T063, T064 y T065

### Pruebas de la historia 5 ⚠️ (escribir primero; deben fallar)

- [X] T059 [P] [US5] Escribir `tests/unit/test_comparacion.py` ([contracts/dominio.md](contracts/dominio.md) "Casos de prueba obligatorios"; SC-005):
  - **Ejemplos de referencia (AC-5.33)**:
    - los tres ejemplos de la spec, en todas las modalidades;
    - en Siempre Sale, cada variante de categoría ganadora indicada en ellos: 3, 4, 5 o 6 publicada, no publicada y menor que los aciertos.
  - **Primer Sorteo, La Segunda y Revancha**:
    - AC-5.14 a AC-5.17: Primer, Segundo y Tercer Premio en ambas tradicionales; 3 aciertos → sin premio;
    - AC-5.18: 3 + 3 aciertos no se suman;
    - AC-5.19 y AC-5.20: Revancha solo premia 6.
  - **Siempre Sale**:
    - AC-5.21: 6 aciertos sin categoría publicada → "Siempre Sale (6 aciertos)";
    - AC-5.22: 5 frente a una categoría de 6 → sin premio; 5 frente a 5 → con premio;
    - AC-5.23: 4 frente a 4 → con premio; categoría no publicada → pendiente de determinación;
    - AC-5.30: 5 frente a una categoría de 4 → pendiente de determinación con `AVISO_ACIERTOS_SUPERAN_CATEGORIA`.
  - **Premio Extra**:
    - AC-5.24: participa con 6 aciertos repartidos;
    - AC-5.25: excluida, con `excluida_por` igual a la extracción con 6 aciertos;
    - AC-5.26: un número repetido entre extracciones cuenta una vez;
    - AC-5.27: 5 o 4 aciertos frente a una categoría de 6, 5 o 4, no publicada, y 3 o menos;
    - AC-5.28: Siempre Sale no cuenta;
    - AC-5.29: con una de las tres extracciones sin publicar, su estado y ningún acierto;
    - P-02: 6 aciertos frente a una categoría de 5 y frente a "sin ganadores".
  - **Varias modalidades**:
    - AC-5.31: un resultado por modalidad aplicable, en orden;
    - AC-5.32: premios simultáneos.
  - **Estados de validación (RN-29)**: cada combinación de sin cargar, borrador, observado, publicado y en revisión. Sin publicar, los datos 2 a 5 son `None` (AC-5.1 y AC-5.2). En revisión, aparece `AVISO_EN_REVISION` (AC-5.12).
  - **Importe**:
    - AC-5.3: números publicados sin premios publicados → resultado de premio e `importe_pendiente`;
    - AC-5.6 y AC-5.7: con premio, el importe individual si está publicado y, si no, `importe_pendiente`; nunca un cálculo.
  - **RN-33**: un concurso del 17/06/2024 da `PENDIENTE_DETERMINACION` con aciertos, y uno del 18/06/2024 aplica las reglas (AC-5.11).
- [X] T060 [P] [US5] Escribir `tests/unit/test_resumen.py` para `resumir_jugada`, siguiendo la precedencia de P-04 aprobada en T058: "Con premio", "Con premio — información de premios pendiente de publicación", "Premio pendiente de determinación", "Resultado pendiente" y "Sin premio", con un caso por cada nivel y casos mixtos (AC-5.13)
- [X] T061 [P] [US5] Escribir `tests/integration/test_us5_comparacion.py`:
  - **Detalle de las jugadas de ejemplo** (AC-5.33): con los concursos de los ejemplos 1 a 3 publicados por las fábricas, el detalle muestra un bloque por modalidad con los textos exactos de [contracts/mensajes.md](contracts/mensajes.md) "Comparación":
    - "{n} aciertos — Sin premio", "Con premio — {categoría}" y "Premio pendiente de determinación". Un premio sin importe individual muestra "Información de premios pendiente de publicación" (AC-5.7);
    - "Excluida del Premio Extra: obtuvo 6 aciertos en {sorteo}" y "Participa";
    - "Información en revisión: el resultado podría cambiar" y "Los aciertos de tu jugada superan la categoría ganadora publicada. Verificá los números y el concurso de tu jugada.".
  - **Números acertados**: aparecen resaltados con texto accesible.
  - **Importes**: el importe oficial aparece en formato `$ 1.234,56` solo si fue publicado (AC-5.6).
  - **Historial**: muestra el estado resumido de cada jugada (AC-5.13).
  - **Información no publicada** (SC-003): un bloque en Borrador nunca aporta aciertos.

### Implementación de la historia 5

- [X] T062 [US5] Implementar en `dominio/comparacion.py` el tipo `ResultadoModalidad` de [contracts/dominio.md](contracts/dominio.md) y la base de `comparar_jugada(jugada, concurso: DatosConcurso)`:
  - un resultado por modalidad aplicable, en `ORDEN_MODALIDADES`;
  - el estado de validación (regla 1, incluido Premio Extra según sus tres bloques), con los datos 2 a 5 en `None` si el bloque no está publicado;
  - los aciertos y `numeros_acertados` por extracción (RN-28);
  - Primer Sorteo y La Segunda (RN-49 y RN-50) y Revancha (RN-51);
  - RN-33 con `FECHA_VIGENCIA_REGLAS`;
  - el importe según RN-27, sin dividir ni estimar nunca;
  - `AVISO_EN_REVISION`.

  Depende de T059.
- [X] T063 [US5] Implementar Siempre Sale en `dominio/comparacion.py`: los casos (a) a (e) de RN-52, con la precedencia de P-02 aprobada en T058, el nombre de categoría "Siempre Sale ({n} aciertos)" y `AVISO_ACIERTOS_SUPERAN_CATEGORIA` en el caso (e) (depende de T058 y T062)
- [X] T064 [US5] Implementar Premio Extra en `dominio/comparacion.py`:
  - el conjunto viene de `dominio.numeros.conjunto_premio_extra` y nunca incluye Siempre Sale;
  - la exclusión de RN-53 completa `excluida_por` con la primera extracción con 6 aciertos, en orden, y deja el resultado de premio en `None`;
  - la elegibilidad es `PARTICIPA` o `EXCLUIDA`;
  - los casos (a) a (e) de RN-31 siguen P-02 aprobada, con el nombre "Premio Extra ({n} aciertos)";
  - `sin_ganadores` da "Sin premio" (RN-31 c), salvo lo que decida P-02 para 6 aciertos.

  Depende de T063.
- [X] T065 [US5] Implementar `resumir_jugada(resultados) -> EstadoResumido` en `dominio/comparacion.py` según P-04 aprobada en T058, hasta que pasen `tests/unit/test_comparacion.py` y `tests/unit/test_resumen.py` (depende de T060 y T064)
- [X] T066 [US5] Integrar la comparación en `jugadas/views.py`:
  - `detalle` obtiene `datos_concurso(jugada.concurso)` y `comparar_jugada(jugada.numeros, datos)`;
  - `lista` calcula `resumir_jugada` para cada jugada y reemplaza el estado provisorio de T053;
  - cada `DatosConcurso` se carga una sola vez por concurso, con `prefetch_related`, para no hacer consultas por jugada (NFR-004).

  Depende de T065.
- [X] T067 [P] [US5] Crear el parcial `templates/jugadas/_comparacion.html`, un bloque por modalidad con:
  - el nombre de la modalidad y el estado de validación;
  - los aciertos y los números de la jugada, con los acertados resaltados (marca visual y texto oculto "acertado" para lectores de pantalla);
  - la elegibilidad, solo en Premio Extra, y el conjunto de Premio Extra con los números de la jugada resaltados (AC-5.24);
  - el resultado de premio, el importe con `pesos` o "Información de premios pendiente de publicación", y los avisos.

  Incluirlo en `templates/jugadas/detalle.html` y mostrar el estado resumido en `templates/jugadas/lista.html`.
- [X] T068 [P] [US5] Agregar a `static/css/app.css` los estilos de la comparación: un bloque por modalidad apilado a 360 px, el resaltado de números acertados con contraste AA que no depende solo del color (borde y peso de fuente) y los rótulos del estado resumido (NFR-002, NFR-003)

**Punto de control**: US5 funciona. El recorrido personal completo (registrar → seguir → conocer el resultado) está disponible.

---

## Fase 8: Historia de usuario 7 — Corregir información publicada con trazabilidad (Prioridad: P2)

**Objetivo**: marcar en revisión, corregir con motivo y fuente, publicar la corrección conservando el valor anterior, consultar el historial y propagar las correcciones a la consulta pública y a las comparaciones.

**Prueba independiente**: publicar un resultado, marcarlo "En revisión", iniciar una corrección sin publicarla (el público ve el valor anterior), publicarla y verificar el historial, el detalle público y la comparación de una jugada afectada (quickstart, escenario F).

### Compuerta de la historia 7

- [X] T069 [US7] **Compuerta P-01 y P-03**: confirmar con el responsable P-01 (salida de "En revisión": al publicar una corrección y, además, quitando la marca con un motivo) y P-03 ("Actualizado por corrección…" solo si la corrección cambió alguno de los cinco datos de RN-29), e incorporar la decisión a `specs/001-quini6-mvp/spec.md` (Clarifications, RN-16, RN-32, AC-5.9 y AC-7.1), con una referencia en `research.md`. Bloquea T072 (`quitar_revision`), T074 y T076 (ruta `quitar-revision`)

### Pruebas de la historia 7 ⚠️ (escribir primero; deben fallar)

- [X] T070 [P] [US7] Escribir `tests/unit/test_cambio_por_correccion.py` para `cambio_por_correccion(jugada, historial_de_versiones)`:
  - una corrección que cambia los aciertos o el resultado → la fecha de esa corrección;
  - una corrección que no cambia ninguno de los cinco datos de RN-29 → `None` (P-03);
  - varias correcciones → la fecha de la más reciente que produjo un cambio;
  - una corrección en Revancha que altera el conjunto de Premio Extra → aviso en Premio Extra.
- [X] T071 [P] [US7] Escribir `tests/integration/test_us7_correccion.py`:
  - **Revisión** (AC-7.1): marcar "En revisión" exige un motivo; el público ve los valores publicados y "Información en revisión". Intentar marcar un bloque sin versión `PUBLICADA` (sin cargar, en Borrador u Observado) se rechaza, tanto por la ruta como llamando al servicio, y no cambia nada.
  - **Corrección en preparación** (AC-7.2): iniciar una corrección exige motivo y fuente; mientras no se publique, el público y la comparación siguen con los valores anteriores.
  - **Historial** (AC-7.3): muestra el valor anterior, el valor nuevo, la fecha y hora, el autor, el motivo y la fuente.
  - **Corrección publicada**:
    - AC-7.4: el público ve el valor nuevo y "Corregido el {fecha}";
    - AC-7.5 y AC-5.9: la jugada afectada muestra la comparación recalculada y "Actualizado por corrección del resultado oficial el {fecha}";
    - SC-008: lo anterior se verifica en la consulta siguiente.
  - **Estado de los bloques**:
    - la versión anterior queda `REEMPLAZADA` y conserva sus valores;
    - el bloque deja de estar en revisión;
    - P-01: quitar la revisión exige un motivo y registra `QUITAR_REVISION`, sin "Corregido el".
  - **Permisos** (AC-7.6): un usuario sin permiso que intenta revisar, corregir o ver el historial recibe 403 y nada cambia.

### Implementación de la historia 7

- [X] T072 [US7] Implementar en `resultados/servicios.py`:
  - `marcar_revision(autor, modalidad_concurso, bloque, motivo)`: solo sobre un bloque con versión `PUBLICADA` (si no la tiene, lo rechaza con un error y no cambia nada; regla de data-model.md, U2); exige un motivo no vacío; pone `*_en_revision = True` y `*_motivo_revision` y registra `MARCAR_REVISION`.
  - `quitar_revision(autor, modalidad_concurso, bloque, motivo)`: según P-01; registra `QUITAR_REVISION`.
  - `iniciar_correccion(autor, modalidad_concurso, bloque, motivo, fuente)`: crea una versión en trabajo con `es_correccion=True` copiando los valores de la publicada (y sus `PremioCategoria`) y registra `INICIAR_CORRECCION`.

  En el guardado de un borrador de corrección, `guardar_borrador_*` exige `motivo_correccion` y la fuente (depende de T036 y T069).
- [X] T073 [US7] Extender `publicar` en `resultados/servicios.py` para las correcciones, en una sola transacción con `select_for_update` sobre la `ModalidadConcurso`:
  - la versión `PUBLICADA` anterior pasa a `REEMPLAZADA` con `reemplazada_en`;
  - la corrección pasa a `PUBLICADA`;
  - `*_en_revision` vuelve a `False`;
  - se registra `PUBLICAR_CORRECCION` con `valor_anterior`, `valor_nuevo`, motivo y fuente.

  Se mantienen todas las condiciones de RN-17 (depende de T072).
- [X] T074 [US7] Implementar `cambio_por_correccion(jugada, historial_de_versiones) -> dict[Modalidad, date | None]` en `dominio/comparacion.py`. Para cada corrección publicada de los bloques que usa cada modalidad, se compara `comparar_jugada` con los valores anteriores y con los nuevos, y se devuelve la fecha de la más reciente que cambió alguno de los cinco datos (P-03). Debe pasar `tests/unit/test_cambio_por_correccion.py` (depende de T065, T069 y T070)
- [X] T075 [US7] Agregar a `resultados/consultas.py`:
  - `historial_versiones(concurso)`: la secuencia de `DatosConcurso` vigentes antes y después de cada corrección publicada, a partir de las versiones `REEMPLAZADA` y `PUBLICADA` ordenadas por `publicada_en`;
  - `historial_cambios(concurso)`: las entradas de `RegistroCambio` ordenadas por `fecha_hora` descendente con el autor precargado.

  Depende de T073.
- [X] T076 [US7] Implementar en `resultados/views_admin.py`, con `administrador_requerido`:
  - `revision` (`POST`, con motivo);
  - `quitar_revision` (`POST`, con motivo, según P-01);
  - `corregir` (`POST`, con motivo y fuente; redirige al formulario de números o de premios en modo corrección);
  - `historial` (`GET`).

  Los formularios de números y premios muestran y exigen `motivo_correccion` cuando la versión en trabajo es una corrección. Agregar las rutas `<bloque>/revision/`, `<bloque>/quitar-revision/`, `<bloque>/corregir/` y `<numero>/historial/` a `resultados/urls_admin.py` (depende de T073 y T075).
- [X] T077 [P] [US7] Crear `templates/resultados/admin/historial.html`: tabla con el valor anterior, el valor nuevo (números con dos dígitos e importes con `pesos`), la fecha y hora con `fecha_hora_ar`, el autor, el motivo y la fuente. Actualizar `templates/resultados/admin/panel.html` con las acciones "Marcar en revisión", "Quitar revisión", "Corregir" y "Ver historial" según el estado, y `templates/resultados/admin/numeros.html` y `premios.html` con el campo de motivo de corrección
- [X] T078 [US7] Integrar el aviso de corrección en la comparación: `jugadas/views.py` (`detalle`) llama a `cambio_por_correccion` con `historial_versiones(jugada.concurso)` y `templates/jugadas/_comparacion.html` muestra "Actualizado por corrección del resultado oficial el {fecha}" en cada modalidad afectada (AC-5.9) (depende de T074 y T075)

**Punto de control**: US7 funciona. Las correcciones se propagan a la consulta pública y a las comparaciones sin perder la trazabilidad.

---

## Fase 9: Historia de usuario 6 — Consultar estadísticas históricas de frecuencia (Prioridad: P3)

**Objetivo**: frecuencia de los 46 números por modalidad y período, con tabla, gráfico, consulta de un número, aviso de concursos sin información y leyenda descriptiva.

**Prueba independiente**: con un conjunto conocido de sorteos publicados por las fábricas, las frecuencias de tres combinaciones de modalidad y período coinciden con un conteo manual (quickstart, escenario G; SC-006).

### Pruebas de la historia 6 ⚠️ (escribir primero; deben fallar)

- [X] T079 [P] [US6] Escribir `tests/unit/test_estadisticas.py` para `calcular_frecuencias`:
  - siempre 46 entradas, incluidas las de 0 apariciones (AC-6.5);
  - frecuencia por sorteo según RN-40;
  - porcentaje con `Decimal` de dos decimales (RN-43);
  - cantidad de sorteos, primera y última fecha;
  - `concursos_sin_informacion` (RN-45);
  - cero sorteos → `SinSorteos` (AC-6.4);
  - `desde > hasta` → error de período (AC-6.8);
  - tres casos con conteo manual escrito en la prueba (SC-006).
- [X] T080 [P] [US6] Escribir `tests/integration/test_us6_estadisticas.py`:
  - **Consulta**:
    - AC-6.1: sin sesión, Primer Sorteo y todo el período (RN-42), con la tabla y el gráfico SVG de 46 números, la cantidad de sorteos y el rango de fechas;
    - AC-6.2: el cambio de modalidad recalcula los valores;
    - AC-6.3: el período desde y hasta recalcula los valores.
  - **Mensajes y avisos**:
    - AC-6.4: "No hay sorteos publicados de {modalidad} en el período seleccionado", sin tabla ni gráfico;
    - AC-6.6: `numero=14` muestra la frecuencia y el porcentaje `12,50 %`;
    - AC-6.7: "El período incluye {n} concursos sin información disponible para esta modalidad";
    - AC-6.8: "La fecha desde no puede ser posterior a la fecha hasta. Corregí el período." y, debajo, exactamente las mismas estadísticas que la consulta anterior (modalidad, período, número, cantidad de sorteos y frecuencias, a partir de los parámetros `anterior_*`). Sin consulta anterior, se muestran las de los valores predeterminados;
    - AC-6.9: la leyenda "Estadística descriptiva de sorteos pasados. No predice resultados futuros.".
  - **Datos que se usan y que no**:
    - AC-6.11: se usan los valores corregidos vigentes;
    - RN-41: entra la información "En revisión" y nunca la de Borrador u Observado;
    - RN-46: Premio Extra no se ofrece y `modalidad=PREMIO_EXTRA` vuelve a la modalidad predeterminada con un mensaje.
  - **RN-47**: no aparecen las palabras "recomendado", "caliente" ni "frío".

### Implementación de la historia 6

- [X] T081 [US6] Implementar `dominio/estadisticas.py` (`calcular_frecuencias(sorteos, concursos_sin_informacion, desde, hasta) -> Frecuencias | SinSorteos | ErrorPeriodo`) según [contracts/dominio.md](contracts/dominio.md), sin ninguna clasificación, predicción ni recomendación (RN-47), hasta que pase `tests/unit/test_estadisticas.py` (depende de T079)
- [X] T082 [US6] Agregar a `resultados/consultas.py`:
  - `sorteos_publicados(modalidad, desde, hasta) -> list[(fecha_sorteo, Numeros)]`: solo versiones `PUBLICADA` (incluidas las que están en revisión) de concursos donde la modalidad es aplicable (RN-41);
  - `concursos_sin_informacion(modalidad, desde, hasta) -> int`: concursos del período con la modalidad aplicable y sin números publicados (RN-45).

  Depende de T020.
- [X] T083 [US6] Implementar `estadisticas/forms.py` (`EstadisticasForm`):
  - `modalidad`: solo `PRIMER_SORTEO`, `LA_SEGUNDA`, `REVANCHA` y `SIEMPRE_SALE`, con `PRIMER_SORTEO` por defecto (RN-42 y RN-46);
  - `desde` y `hasta` con formato `dd/mm/aaaa`, opcionales;
  - `numero` de 00 a 45, opcional;
  - campos ocultos `anterior_modalidad`, `anterior_desde`, `anterior_hasta` y `anterior_numero`, con la consulta que se está mostrando, según [contracts/rutas.md](contracts/rutas.md). Con ellos, AC-6.8 repite exactamente las estadísticas anteriores. Si esos valores son inválidos o faltan, se usan los predeterminados (RN-42).
- [X] T084 [US6] Implementar `estadisticas/views.py` (`index`, pública):
  - valida el formulario y, ante un período inválido, muestra el error y calcula las estadísticas con los parámetros `anterior_*`. Toda respuesta completa los campos ocultos con la consulta que efectivamente muestra;
  - llama a `sorteos_publicados`, `concursos_sin_informacion` y `calcular_frecuencias`;
  - prepara los datos del gráfico de barras SVG en el servidor (alto proporcional a la frecuencia máxima) (R-11).

  Crear `estadisticas/urls.py` (`estadisticas/`) e incluirlo en `quini6/urls.py` (depende de T081, T082 y T083).
- [X] T085 [P] [US6] Crear `templates/estadisticas/index.html`:
  - formulario de modalidad, período y número;
  - resumen con la cantidad de sorteos considerados y las fechas del primero y del último;
  - aviso de concursos sin información y resultado del número consultado;
  - gráfico SVG en línea con `role="img"`, `aria-label` y un `<title>` por barra ("14: 7 apariciones");
  - tabla equivalente de 46 filas con el número, las apariciones y el porcentaje con `porcentaje_ar` (NFR-003);
  - estado vacío de AC-6.4 y la leyenda de AC-6.9 siempre visible;
  - a 360 px, el gráfico se adapta con `viewBox` y la tabla no genera desplazamiento horizontal (NFR-002).

**Punto de control**: las siete historias funcionan de forma independiente.

---

## Fase 10: Terminación y aspectos transversales

**Propósito**: verificaciones que abarcan varias historias (SC-003, SC-004, NFR-001 a NFR-004 y NFR-008) y validación final.

- [X] T086 [P] Escribir `tests/integration/test_matriz_acceso.py` (SC-004, R-05). Matriz parametrizada (visitante, usuaria A, usuario B y administrador) × todas las rutas de Sesión, Propietario y Admin de [contracts/rutas.md](contracts/rutas.md), en `GET` y `POST`, con estos resultados esperados:
  - visitante → 302 a `/ingresar/?next=…`;
  - jugada ajena → 404 idéntico al de una jugada inexistente;
  - usuario sin permiso de administrador en una ruta Admin → 403 con "No tenés permisos para acceder a esta sección";
  - en ningún caso no autorizado se modifica la base ni aparecen datos ajenos en la respuesta.
- [X] T087 [P] Escribir `tests/integration/test_no_publicado.py` (SC-003). Con valores únicos cargados en Borrador y Observado (números y premios), esos valores no aparecen nunca en `/resultados/`, en `/resultados/<numero>/`, en las búsquedas, en el detalle de una jugada ni en `/estadisticas/`
- [X] T088 [P] Escribir `tests/integration/test_seguridad.py` (Const. IV):
  - con `Client(enforce_csrf_checks=True)`, todo `POST` sin token es rechazado;
  - las respuestas de Sesión, Propietario y Admin llevan `Cache-Control: no-store`;
  - `next` externo y `//otro.sitio` se ignoran;
  - las contraseñas se guardan hasheadas;
  - con `DEBUG` falso, el error 500 no muestra detalles técnicos.
- [X] T089 [P] Escribir `tests/integration/test_rendimiento.py` (NFR-004, R-17). Con 104 concursos publicados y 50 jugadas, usar `django_assert_max_num_queries` para que `/resultados/`, `/resultados/<numero>/`, `/mis-jugadas/`, `/mis-jugadas/<id>/` y `/estadisticas/` respeten un tope fijo de consultas (sin N+1). Ajustar los `select_related` y `prefetch_related` que hagan falta en `resultados/consultas.py` y `jugadas/views.py`
- [X] T090 Revisar la localización en `templates/` y en los mensajes de formularios y servicios (NFR-001, Const. VII): ningún texto visible en inglés (incluidos los mensajes por defecto de Django en formularios y validadores), fechas `dd/mm/aaaa`, importes `$ 1.234,56`, números con dos dígitos y textos idénticos a [contracts/mensajes.md](contracts/mensajes.md). Corregir lo que no cumpla
- [X] T091 Revisar `static/css/app.css` y todas las plantillas de `templates/` a 360 px de ancho y con el teclado: sin desplazamiento horizontal (NFR-002); contraste AA, foco visible, etiquetas de formulario y estados comunicados con texto (NFR-003); y estados de carga, éxito, error y vacío visibles en cada pantalla (NFR-008). Corregir lo que no cumpla
- [X] T092 Ejecutar `ruff check .` y `ruff format --check .` en la raíz del repositorio y corregir todos los avisos
- [ ] T093 Ejecutar `pytest` completo con SQLite. Luego, con las variables `QUINI6_DB_*` de PostgreSQL 16 en `.env`, ejecutarlo de nuevo y confirmar los mismos resultados (paso 4 de [quickstart.md](quickstart.md), R-03)
- [ ] T094 Ejecutar a mano los escenarios A a H de [quickstart.md](quickstart.md) desde la interfaz (Const. VI) y registrar el resultado de cada criterio en `specs/001-quini6-mvp/checklists/validacion-quickstart.md`. Cualquier desvío se informa al responsable y no se resuelve por suposición

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (fase 1)**: sin dependencias.
- **Base (fase 2)**: depende de la fase 1 y **bloquea todas las historias**.
- **US3 (fase 3)**: depende de la base. Se adelanta porque es un prerrequisito técnico de US2, US4, US5 y US7.
- **US2 (fase 4)**: depende de la base y de US3, porque el administrador necesita iniciar sesión.
- **US1 (fase 5)**: depende solo de la base. Se puede desarrollar **en paralelo con US3 y US2**, porque sus pruebas usan las fábricas de `tests/fabricas.py`. Para la validación manual completa necesita US2.
- **US4 (fase 6)**: depende de US3. T057 depende de T048 (US1).
- **US5 (fase 7)**: depende de US4.
- **US7 (fase 8)**: depende de US2. T078 depende de US5.
- **US6 (fase 9)**: depende solo de la base. Se puede desarrollar en paralelo con cualquier historia.
- **Terminación (fase 10)**: depende de todas las historias.

### Grafo de historias

```text
Preparación ─▶ Base ─┬─▶ US3 ─┬─▶ US2 ─────────────┬─▶ US7 ─┐
                     │        │                    │         │
                     │        └─▶ US4 ─▶ US5 ──────┘(T078)   │
                     ├─▶ US1 (paralela; T057 de US4 la toca)  ├─▶ Terminación
                     └─▶ US6 (paralela) ──────────────────────┘
```

### Compuertas (tareas que esperan una decisión del responsable)

| Compuerta | Punto | Bloquea |
|-----------|-------|---------|
| T030 | P-05, P-06 | T035, T038 (modificar concurso y validación de Premio Extra) |
| T043 | P-07 | T045 (búsqueda por fecha) |
| T058 | P-02, P-04 | T063, T064, T065 |
| T069 | P-01, P-03 | T072 (`quitar_revision`), T074, T076 (`quitar-revision`) |

Las compuertas se pueden plantear al responsable **todas juntas al inicio** para no frenar el desarrollo más adelante.

### Dentro de cada historia

- Compuerta (si existe) → pruebas (deben fallar) → dominio → modelos → servicios → formularios → vistas → rutas → plantillas.
- Las tareas sobre un mismo archivo (`resultados/servicios.py`, `dominio/comparacion.py`, `resultados/views_admin.py`, `quini6/urls.py`) son secuenciales.
- La historia termina cuando pasan sus pruebas **y** se verifican sus criterios desde la interfaz.

### Oportunidades de paralelismo

- Fase 1: T003, T004 y T005.
- Fase 2: T007, T008 y T009 juntas; luego T011 y T015 en paralelo con T010, T013 y T014; T017 en paralelo con T016.
- Con la base terminada: **US1, US3 y US6** en paralelo, por personas distintas.
- Dentro de cada historia: todas sus pruebas [P] juntas, y las plantillas [P] en paralelo con las vistas.
- Fase 10: T086 a T089 en paralelo.

---

## Ejemplos de ejecución en paralelo

### Base

```text
Tarea: "T007 Implementar dominio/tipos.py"
Tarea: "T008 Escribir tests/unit/test_numeros.py"
Tarea: "T009 Escribir tests/unit/test_importes.py"
```

### Historia 2

```text
# Pruebas primero (deben fallar):
Tarea: "T031 tests/unit/test_consistencia.py"
Tarea: "T032 tests/integration/test_servicios_resultados.py"
Tarea: "T033 tests/integration/test_us2_admin.py"

# Con las vistas listas:
Tarea: "T041 templates/resultados/admin/listado.html, concurso_form.html, panel.html"
Tarea: "T042 templates/resultados/admin/numeros.html, premios.html, publicar.html"
```

### Historia 5

```text
Tarea: "T059 tests/unit/test_comparacion.py"
Tarea: "T060 tests/unit/test_resumen.py"
Tarea: "T061 tests/integration/test_us5_comparacion.py"
# Después de T066:
Tarea: "T067 templates/jugadas/_comparacion.html"
Tarea: "T068 estilos de comparación en static/css/app.css"
```

### Historias en paralelo, después de la base

```text
Persona A: US3 (T021 a T029) → US2 (T030 a T042)
Persona B: US1 (T043 a T048)
Persona C: US6 (T079 a T085)
```

---

## Estrategia de implementación

### MVP primero (el primer incremento que se puede mostrar)

1. Fase 1 (preparación) y fase 2 (base).
2. Fase 3: US3, solo lo necesario para que existan cuentas y administradores.
3. Fase 4: US2. Los administradores cargan y publican.
4. Fase 5: US1. El público consulta.
5. **Detenerse y validar** con los escenarios A, B, C1 a C3 y D de [quickstart.md](quickstart.md). Es el MVP: resultados públicos validados y trazables, la propuesta de valor principal.
6. Con el MVP aprobado, empezar la carga manual del historial inicial de 12 meses (FR-010).

### Entrega incremental

1. Base, US3, US2 y US1 → **MVP** (consulta pública).
2. US4 → registro de jugadas personales.
3. US5 → comparación con premios por modalidad (validar con los ejemplos de referencia, SC-005).
4. US7 → correcciones con trazabilidad.
5. US6 → estadísticas, con el historial ya cargado (SC-010).
6. Terminación → matriz de acceso, no visibilidad, rendimiento, localización, accesibilidad y quickstart completo.

Cada incremento agrega valor sin romper los anteriores. La suite completa se ejecuta antes de cerrar cada fase.

### Trabajo en equipo

1. Todo el equipo completa la preparación y la base.
2. Después: una persona hace US3 y luego US2; otra, US1; otra, US6.
3. Luego US4, US5 y US7 en ese orden, porque cada una se apoya en la anterior.

---

## Notas

- [P] = archivos distintos, sin dependencias con tareas incompletas.
- La etiqueta [USn] vincula cada tarea con su historia (Const. II, trazabilidad).
- Verificar que las pruebas fallan antes de implementar.
- **Historial inicial (FR-010, SC-010)**: por decisión del responsable (13/11/2026), la carga manual de los concursos de los últimos 12 meses y la verificación de SC-010 quedan **fuera de esta lista de tareas**. Se planifican al preparar el lanzamiento. Las tareas de US2 entregan el flujo con el que se hará esa carga.
- Las fábricas de `tests/fabricas.py` y los ejemplos de referencia **nunca** se cargan en producción ([contracts/comandos.md](contracts/comandos.md)).
- No se implementa nada de D-13 B, D-14 B, D-15 B ni RN-48 sin una decisión explícita del responsable.
- Se recomienda inicializar un repositorio git antes de empezar (quickstart, requisitos previos) y hacer un *commit* por tarea o grupo lógico.
