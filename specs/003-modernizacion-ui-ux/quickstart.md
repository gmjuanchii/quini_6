# Guía de validación (Quickstart): Modernización visual y de experiencia de uso

**Plan**: [plan.md](plan.md) | **Spec**: [spec.md](spec.md) | **Rutas**: [contracts/rutas.md](contracts/rutas.md) | **Mensajes**: [contracts/mensajes.md](contracts/mensajes.md)

Escenarios que prueban, desde la aplicación, que la feature funciona (Const. VI). Los mismos escenarios están automatizados en `e2e/` con Playwright; esta guía es la versión manual para el responsable. Los textos esperados son los del catálogo de mensajes.

## 1. Requisitos previos

- Python 3.12, **Node 24 LTS**, Docker Desktop (para PostgreSQL 16 y Caddy), un navegador actualizado y un lector de pantalla (NVDA en Windows).
- Repositorio en la rama `003-modernizacion-ui-ux`.

## 2. Puesta en marcha (PowerShell)

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
npm ci                                   # ui, e2e y (Etapa 2) frontend
Copy-Item .env.example .env              # completar QUINI6_DB_* del contenedor
docker compose up -d db                  # PostgreSQL 16 (R-21)
python manage.py migrate
$env:QUINI6_E2E = "1"; python manage.py preparar_e2e   # datos de prueba deterministas (R-23)
npm run css:watch                        # terminal 2: Tailwind para las plantillas
python manage.py runserver               # terminal 3: http://127.0.0.1:8000/
python manage.py procesar_extracciones   # terminal 4: trabajador de [002]
```

Etapa 2 (además): `npm run dev -w frontend` (http://127.0.0.1:3000) y `docker compose up -d proxy`; el sitio se abre en **http://localhost:8080/** a través de Caddy.

**Entorno de pruebas de una pantalla de Next.js** (T168, R-20, R-27): `QUINI6_RUTAS_NEXT` lleva **solo** los patrones de la pantalla en prueba ([contracts/rutas.md](contracts/rutas.md) § 3); vacía, todo lo atiende Django. Next.js necesita `QUINI6_API_INTERNA` (Django sin pasar por Caddy) y `QUINI6_ORIGEN_PUBLICO` (la dirección del enrutador):

```powershell
$env:QUINI6_RUTAS_NEXT = "/administracion/extracciones/ /administracion/extracciones/*"
$env:QUINI6_ORIGEN_PUBLICO = "http://localhost:8080"     # también en Django (CSRF_TRUSTED_ORIGINS)
docker compose up -d proxy                                # Caddy toma QUINI6_RUTAS_NEXT al iniciar
$env:QUINI6_API_INTERNA = "http://127.0.0.1:8000"; $env:TZ = "America/Argentina/Buenos_Aires"
npm run build -w frontend; npm run start -w frontend      # http://127.0.0.1:3000 (detrás de Caddy)
```

Para cambiar las rutas conmutadas: actualizar `QUINI6_RUTAS_NEXT` y `docker compose up -d proxy` (recrea el contenedor con la variable nueva). La cabecera `X-Interfaz` de cada respuesta dice quién respondió (`django` o `next`).

**Guiones de convivencia** (`sesion-compartida`, `hu14-convivencia`): corren solo con `E2E_CONVIVENCIA=1`, contra el enrutador y con la base E2E (Django en el puerto 8001 con `QUINI6_DB_SQLITE=e2e.sqlite3`, `QUINI6_E2E=1`). Para la vuelta automática (AC-14.6) se usa un segundo enrutador con las mismas rutas y un destino de Next.js que no responde:

```powershell
$env:E2E_CONVIVENCIA = "1"; $env:E2E_BASE_URL = "http://localhost:8080"
$env:E2E_DJANGO_DIRECTO = "http://127.0.0.1:8001"        # Django sin pasar por el enrutador
$env:E2E_URL_SIN_NEXT = "http://localhost:8089"          # enrutador con QUINI6_NEXT_UPSTREAM=host.docker.internal:3999
npm run e2e -- recorridos/sesion-compartida.spec.ts recorridos/hu14-convivencia.spec.ts
```

Si el puerto 8080 está ocupado por otro servicio, publicar Caddy en otro puerto (por ejemplo `docker run -p 8088:8080 … caddy:2` con las mismas variables y montajes de `compose.yaml`) y usar ese puerto en `QUINI6_ORIGEN_PUBLICO` y `E2E_BASE_URL`.

Cuentas que crea `preparar_e2e` (solo desarrollo): una persona administradora, una usuaria con jugadas, una usuaria sin jugadas; sorteos publicados de 2025 y 2026; y extracciones en los cinco estados (más de 20, para la paginación). Las contraseñas las imprime el comando.

**Migración 0003**: si `migrate` se detiene en `extraccion_periodo_unico_en_curso`, hay dos extracciones en curso con el mismo período de distintos administradores; esperar a que terminen y repetir.

## 3. Pruebas automáticas

```powershell
pytest                                   # dominio, vistas, API, contratos (SQLite)
ruff check .
npm run test -w ui                       # contraste de tokens (SC-009)
npm run e2e                              # Playwright + axe contra http://127.0.0.1:8000 (Etapa 1)
$env:E2E_BASE_URL = "http://localhost:8080"; npm run e2e   # mismo guion detrás del proxy (Etapas 2 y 3)
npm run lint -w frontend; npm run typecheck -w frontend; npm run test -w frontend
npm run storybook:build -w frontend      # historias de todos los componentes (pedido § 7.3)
npm run lhci                             # presupuesto de rendimiento (R-24)
npm run lhci -- --base http://localhost:8080 --ingreso http://127.0.0.1:8001   # detrás del enrutador
```

**Guiones contra Next.js (Etapa 2)**: además de `E2E_BASE_URL` y `E2E_CONVIVENCIA`, `E2E_RUTAS_NEXT` lleva el mismo valor que `QUINI6_RUTAS_NEXT` del enrutador; con él, cada guion deduce qué aplicación debe atender cada ruta (contracts/rutas.md § 3), así el mismo guion sirve en cada etapa de la conmutación. Para probar todas las pantallas a la vez:

```powershell
$rutas = "/administracion/extracciones/ /administracion/extracciones/* /estadisticas/ /mis-jugadas/ /mis-jugadas/* / /resultados/ /resultados/* /ingresar/ /registrarse/ /salir/ /preferencias/* /administracion/concursos/ /administracion/concursos/*"
$env:QUINI6_RUTAS_NEXT = $rutas; $env:E2E_RUTAS_NEXT = $rutas
# Django (8001, base E2E), Next.js (3000, QUINI6_API_INTERNA=http://127.0.0.1:8001) y Caddy con esas rutas
$env:E2E_BASE_URL = "http://localhost:8080"; $env:E2E_CONVIVENCIA = "1"; npm run e2e
```

**Sentry (solo producción, P-01)**: `QUINI6_SENTRY_DSN` (Django y servidor de Next.js) y `NEXT_PUBLIC_QUINI6_SENTRY_DSN` (navegador, al compilar). Vacías, no se carga nada.

Resultado esperado: todo en verde; axe sin incidencias críticas ni graves (SC-004).

## 4. Escenarios manuales (Etapa 1 y, sin cambios, cada pantalla migrada)

| # | Escenario | Pasos | Resultado esperado | Criterios |
|---|-----------|-------|--------------------|-----------|
| 1 | Estados de extracción | Como administración, abrir "Extracción histórica"; activar escala de grises del sistema | Cada fila con etiqueta de texto + icono + color; "Con advertencias" y "Con error" se destacan; en grises se distinguen por texto e icono; al enfocar una etiqueta se lee su explicación | AC-1.1 a AC-1.3, AC-1.5 |
| 2 | Filtro, orden y paginación | Filtrar "Con advertencias"; ordenar por "Estado"; ir a la página 2; "Limpiar filtros" | Solo esa etiqueta con "Filtro aplicado"; flecha de orden; "Página 2 de N"; filtro y orden se conservan; sin filtro vuelven todas | AC-1.4, AC-9.1, AC-9.2, AC-8.3 |
| 3 | Menú ⋮ y confirmación | Abrir ⋮ con ratón y con Intro; recorrer con flechas; Escape; elegir "Eliminar"; Escape; repetir y confirmar | Menú pegado al botón; foco vuelve al ⋮; confirmación nombra fecha, hora y período, con "Cancelar" enfocado; al confirmar, la fila desaparece y aparece "Se eliminó la extracción del …" sin "Deshacer"; una extracción en curso no ofrece "Eliminar" | AC-2.1 a AC-2.6 |
| 4 | Avance en vivo | Elegir "Año anterior" e "Iniciar extracción" sin recargar | Botón "Iniciando…" no pulsable; fila "En curso"; "Identificando…" y luego barra "N de M sorteos procesados"; al terminar, la etiqueta cambia sola y aparece el aviso con el resultado | AC-3.1 a AC-3.3, SC-003 |
| 5 | Período repetido | Con la sesión de otra persona administradora, iniciar el mismo período mientras el anterior sigue en curso; luego uno que se superpone en parte | El primero muestra "Ya hay una extracción en curso para el período del … al …" con acceso a ella; el segundo se inicia | AC-3.5, RN-03 |
| 6 | Volver más tarde | Cerrar la pestaña con una extracción en curso y volver | Se ve el estado real | AC-3.6 |
| 7 | Fechas | En Estadísticas: escribir 01012025; abrir el calendario; elegir un rango; usar "Año en curso"; probar 31/02/2025, 29/02/2025, 29/02/2024 y un fin anterior al inicio | Barras automáticas; calendario en español desde el lunes, sin tapar el campo; rango resaltado; atajo completa ambas fechas; mensajes junto al campo; 29/02/2024 aceptado; en la extracción histórica no hay "Todo el historial" y los días futuros están deshabilitados | AC-4.1 a AC-4.7 |
| 8 | Navegación | Recorrer todas las secciones con ratón, teclado y a 360 px; pulsar Tab al abrir | Sección actual con dos rasgos y anunciada como actual; "Saltar al contenido"; botón "Menú" con Escape; menú de cuenta con el correo y "Salir"; "←" con el nombre del destino en cada página interna; logotipo y favicon propios | AC-5.1 a AC-5.7 |
| 9 | Ingreso | Ingresar con el gestor de contraseñas; "Mostrar"/"Ocultar"; correo mal escrito y salir del campo; credenciales incorrectas | Tarjeta centrada; mensajes de [contracts/mensajes.md](contracts/mensajes.md); "Ingresando…"; sin enlace de recuperación; "¿Todavía sin cuenta? Crear cuenta" separado | AC-6.1 a AC-6.7 |
| 10 | Estadísticas | Abrir a 1280 px y 360 px; elegir "Tradicional – Primer Sorteo"; escribir 46; consultar; ordenar la tabla | Opciones completas; misma línea base / filas sin superponerse; "El número debe estar entre 00 y 45" sin enviar; gráfico + tabla ordenable; aviso informativo con icono antes de los resultados | AC-7.1 a AC-7.6, AC-10.1 |
| 11 | Estados vacíos | Con la base vacía (`python manage.py flush` en una base de prueba) recorrer como visitante, usuaria y administración | Estados vacíos con icono, título, explicación y acción según el perfil; en Resultados, solo la administración ve "Cargar sorteo" y "Extracción histórica" con la aclaración del CSV | AC-8.1 a AC-8.4 |
| 12 | Tablas a 360 px | Abrir "Extracción histórica" y "Mis jugadas" a 360 px | Tarjetas rotuladas, sin desplazamiento horizontal; clic en la fila abre el detalle | AC-9.3, AC-9.4, SC-006 |
| 13 | Avisos y pie | Provocar éxito, advertencia, error e información; mirar el pie a 360 px | Mismo icono, color, forma y ubicación por tipo; anunciados por el lector; avisos breves se cierran a los 6 s salvo errores; pie legible | AC-10.2, AC-10.3 |
| 14 | Lenguaje | Recorrer todas las pantallas | Forma neutra, botones con verbo, "sorteo" en lugar de "concurso" | AC-11.1 a AC-11.3, SC-007 |
| 15 | Tema | Con el sistema en oscuro y sin elección previa, abrir; elegir "Claro"; cerrar y volver; probar sin scripts | Tema oscuro inicial; cambio inmediato sin perder lo escrito; se recuerda; sin scripts el selector funciona recargando | AC-12.1 a AC-12.4 |
| 16 | Movimiento | Activar "reducir movimiento" en el sistema y repetir 3 y 4 | Sin transiciones ni desplazamientos; la barra informa sin animación | AC-13.1 a AC-13.5 |
| 17 | Sin conexión | Durante "Registrar jugada", desconectar la red, enviar, reconectar y "Reintentar" | "No se pudo conectar…" con "Reintentar"; queda **una** jugada | FR-031 |
| 18 | Sesión vencida | Completar "Registrar jugada", esperar 31 minutos (o borrar la cookie `sessionid`), enviar, ingresar | Aviso de sesión vencida; tras ingresar, el formulario aparece completo y no se envía solo; con otra cuenta, la jugada queda para esa cuenta | FR-032 |
| 19 | Sin scripts | Desactivar JavaScript y repetir 2, 3, 7 y 9 | Todo funciona en su versión básica: página de confirmación aparte, calendario del navegador, recarga para ver el avance | NFR-007 |
| 20 | Zoom y teclado | Zoom de texto al 200 % y recorrido solo con teclado y con NVDA de SC-005 | Sin contenido ni funciones perdidas; todas las tareas principales se completan | SC-005, SC-006 |
| 21 | Datos sin cambios | Comparar una pantalla de Resultados, Estadísticas, Mis jugadas y un CSV de extracción contra `main` | Mismos datos; CSV con la misma estructura | NFR-009, SC-011 |

## 5. Validación específica de las Etapas 2 y 3

| # | Escenario | Resultado esperado | Referencia |
|---|-----------|--------------------|------------|
| 22 | **Sesión compartida (T208)**: ingresar, abrir una pantalla renovada, volver a una sin renovar, salir | Con la sesión iniciada en ambas sin volver a ingresar y con el mismo encabezado; tras salir, ninguna pantalla muestra datos privados; una cuenta sin permisos ve "Sin permisos para acceder a esta sección" en ambas | AC-14.1, AC-14.2, R-19 |
| 23 | Conmutar una pantalla: agregar su patrón a `QUINI6_RUTAS_NEXT`, `docker compose exec proxy caddy reload --config /etc/caddy/Caddyfile` | La pantalla se ve y funciona igual que antes (mismos datos, textos y permisos); el guion E2E de su historia pasa igual. Apoyo técnico: cabecera `X-Interfaz: next` | AC-14.5, R-20, [contracts/rutas.md](contracts/rutas.md) |
| 24 | Reversa: quitar el patrón y recargar Caddy | La pantalla vuelve a su versión anterior sin desplegar código, con las mismas direcciones y sin perder datos | FR-042, Pedido §3.5 |
| 25 | Avisos entre versiones: ingresar desde "Ingresar" (sin renovar) y volver a "Mis jugadas" (renovada); registrar una jugada y terminar en una pantalla sin renovar | El aviso de cada acción aparece en la pantalla de destino | AC-14.3, R-31 |
| 26 | Sesión vencida entre versiones: completar "Registrar jugada" en la versión renovada, borrar la cookie `sessionid`, enviar e ingresar | Tras ingresar aparece "Volver al formulario"; al elegirlo, el formulario se ve completo y no se envió | AC-14.4, R-12 |
| 27 | Caída de la versión renovada: detener Next.js con una pantalla conmutada | La pantalla se sigue viendo con su versión anterior; si sus plantillas ya se retiraron, se ve la página de servicio no disponible con el pie legal | AC-14.6, FR-044 |
| 28 | Formulario abierto durante el cambio: abrir un formulario, conmutar (o revertir) su pantalla y enviarlo | Se procesa normalmente, sin errores ni datos perdidos | R-20, R-32 |
| 29 | Presupuesto: `npm run lhci` sobre la pantalla migrada | LCP, CLS, INP y JavaScript inicial dentro de R-24 y no peores que la línea base de Django | R-24 |
| 30 | Storybook: `npm run storybook -w frontend` | Cada componente de [contracts/componentes.md](contracts/componentes.md) con todos sus estados y sin incidencias del addon a11y | Pedido §7.3 |
