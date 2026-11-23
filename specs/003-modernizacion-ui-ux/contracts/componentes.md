# Contrato de componentes de interfaz

**Plan**: [../plan.md](../plan.md) | **Tokens**: [tokens.md](tokens.md) | **Research**: R-04 a R-07, R-18, R-29

Cada componente se diseña en Figma, se implementa **dos veces con el mismo nombre, estados y clases** (fragmento de Django en la Etapa 1, componente React en la Etapa 2) y toma sus clases de variante de `ui/variantes.json`. Los guiones E2E lo encuentran por su **rol y nombre accesible**, nunca por clases, así el mismo guion sirve para las dos implementaciones.

## 1. Catálogo

| Componente | Django (Etapa 1) | React (Etapa 2) | Variantes / props | Estados obligatorios | Accesibilidad y teclado | Requisitos |
|------------|------------------|-----------------|-------------------|----------------------|-------------------------|------------|
| `Button` | `ui/_boton.html` | `components/ui/button.tsx` (shadcn) | `principal`, `secundario`, `destructivo`, `fantasma`, `enlace`; `tamano`: `md` (44 px), `sm` (solo escritorio) | reposo, cursor, foco visible, pulsado, **trabajando** (indicador + texto "…ando…", `aria-busy`, no pulsable), deshabilitado | `<button>` o `<a>` según acción; icono opcional siempre con texto; nunca solo "Aceptar"/"OK" | AC-11.2, AC-13.4, AC-13.5, FR-034, NFR-005 |
| `StatusBadge` | `ui/_insignia_estado.html` | `components/status-badge.tsx` | `info`, `success`, `warning`, `danger`, `neutral` + `etiqueta` (RN-01) | — | Texto + icono + color; explicación (RN-02) en un *tooltip* accesible al cursor y al foco (`aria-describedby`); en escala de grises se distingue por texto e icono | AC-1.1, AC-1.2, FR-001, FR-002 |
| `ActionMenu` (⋮) | `ui/_menu_acciones.html` (`<details>` + Alpine) | `components/action-menu.tsx` (DropdownMenu) | `opciones` por fila | cerrado, abierto, opción enfocada | Nombre accesible "Acciones de la extracción del {fecha y hora}"; Intro/Espacio abre y enfoca la primera opción; flechas; Escape cierra y devuelve el foco; clic afuera cierra; abrir otro cierra el anterior; anclado al botón y dentro de la pantalla | AC-2.1, AC-2.2, AC-13.5, FR-007 |
| `ConfirmDialog` | `ui/_dialogo_confirmar.html` (`<dialog>`) | `components/confirm-dialog.tsx` (Dialog / AlertDialog) | `titulo`, `texto`, `consecuencias`, `accion_destructiva` | abierto, confirmando (botón trabajando) | `role="alertdialog"`, foco inicial y acción predeterminada en "Cancelar"; Escape, "Cancelar" o clic afuera cierran sin efecto y devuelven el foco al botón de origen; sin scripts = página aparte | AC-2.3 a AC-2.5, FR-008, FR-009 |
| `DateField` | `ui/_campo_fecha.html` (input + Cally) | `components/date-field.tsx` | `min`, `max`, `requerido` | vacío, completo, error, deshabilitado, calendario abierto | Ancho para `dd/mm/aaaa` (≈ 11 ch + botón); barras automáticas al escribir; botón "Abrir calendario" con nombre accesible; Escape cierra y devuelve el foco; días fuera de rango deshabilitados; semana desde el lunes; nombres en español | AC-4.1, AC-4.2, AC-4.5 a AC-4.7, FR-010, FR-013 |
| `DateRangePicker` | `ui/_periodo.html` | `components/date-range-picker.tsx` | `atajos` (RN-04), `min`, `max` | ídem + rango resaltado | Dos campos con etiqueta propia ("Fecha de inicio", "Fecha de finalización" o "Desde", "Hasta") + un calendario de rango; los atajos son botones que completan ambos campos y se pueden modificar | AC-4.3, AC-4.4, FR-011 |
| `Field` | `_campo.html` (existente, ampliado) | `components/field.tsx` | `etiqueta`, `ayuda`, `error` | reposo, foco, error | `<label for>`; ayuda y error en `aria-describedby`; `aria-invalid`; error con icono y texto junto al campo | FR-033, AC-7.3, NFR-001 |
| `PasswordField` | `ui/_campo_contrasena.html` | `components/password-field.tsx` | `autocomplete`: `current-password` / `new-password` | oculta, visible | Botón "Mostrar"/"Ocultar" con `aria-pressed`; el anuncio del cambio va en una región `aria-live="polite"` | AC-6.2, AC-6.5 |
| `Callout` | `ui/_aviso.html` | `components/callout.tsx` | `info`, `success`, `warning`, `danger` | — | Icono + texto; `role="status"` (info, éxito) o `role="alert"` (error) cuando aparece tras una acción; los fijos (advertencia de Estadísticas) sin rol dinámico | AC-10.1, AC-10.3, RN-09 |
| `Toast` | `ui/_avisos.html` (región + Alpine) | Sonner (`components/toaster.tsx`) | `success`, `info`, `warning`, `error` | entrando, visible, saliendo | Cierre automático a 6 s salvo errores; botón "Cerrar aviso" con teclado; no roba el foco; región `aria-live` | AC-2.5, AC-3.3, RN-09 |
| `EmptyState` | `ui/_estado_vacio.html` | `components/empty-state.tsx` | `sin_datos`, `sin_resultados` (nombra el filtro + "Limpiar filtros") | — | Icono decorativo, título como encabezado, explicación, acción opcional solo si el perfil tiene permiso | AC-8.1 a AC-8.4, FR-025, FR-026, RN-06 |
| `DataTable` | `ui/_tabla.html` + `ui/_paginacion.html` | `components/data-table.tsx` (componente de servidor; sin TanStack Table desde el 22/11/2026, R-24) | columnas, `ordenable`, `fila_enlace` | vacía, con datos, cargando (Skeleton), filtrada | `<table>` con `<caption>` y `aria-sort` en el encabezado ordenado; encabezados ordenables y paginación como **enlaces** (sin scripts); < 768 px: una tarjeta por fila con `<dl>` rotulado; fila entera abre el detalle salvo el menú ⋮ ("Ver detalle →" visible al cursor y al foco) | AC-9.1 a AC-9.5, FR-027, RN-07 |
| `Pagination` | `ui/_paginacion.html` | `components/pagination.tsx` | `pagina`, `paginas` | primera, intermedia, última | `<nav aria-label="Paginación">`; "Página N de M"; "Anterior" y "Siguiente" con `aria-disabled` en los extremos; conserva filtro y orden | AC-9.2, RN-07 |
| `ProgressPanel` | `extracciones/_avance.html` (existente, rediseñado) | `components/progress-panel.tsx` | `identificando`, `procesados`, `total` | identificando (indicador), con total (barra), terminado (aviso) | `<progress>` con nombre "N de M sorteos procesados"; región `role="status"`; sin animación con movimiento reducido | AC-3.2, AC-3.3, AC-13.2 |
| `Skeleton` | `ui/_esqueleto.html` | `components/ui/skeleton.tsx` | `forma`: línea, bloque, fila | — | `aria-hidden="true"`; el contenedor lleva `aria-busy="true"`; reserva el alto final | AC-13.3, NFR-004 |
| `NavBar` | `base.html` (encabezado) | `app/_componentes/nav-bar.tsx` | secciones según perfil | sección activa, cursor, foco, móvil abierto/cerrado | Logotipo enlazado al inicio; sección activa con fondo + marca inferior y `aria-current="page"`; enlaces sin subrayado, 44 × 44 px; < 768 px botón "Menú" con `aria-expanded` y Escape | AC-5.1 a AC-5.4, AC-5.7, FR-014 a FR-016, FR-018 |
| `AccountMenu` | `ui/_menu_cuenta.html` | `components/account-menu.tsx` | `correo` | cerrado, abierto | Botón con el correo abreviado (completo en `title` y al enfocar); contiene "Salir" (formulario POST) | AC-5.3, FR-015, FR-030 |
| `ThemeSelect` | `ui/_selector_tema.html` (form POST) | `components/theme-select.tsx` | `claro`, `oscuro`, `dispositivo` | opción actual | Grupo de radio con etiqueta "Tema"; sin scripts envía el formulario; con scripts aplica al instante | AC-12.1 a AC-12.3, FR-036 |
| `SkipLink` | `base.html` | `app/_componentes/skip-link.tsx` | — | oculto, visible al foco | Primer elemento enfocable; lleva el foco a `<main id="contenido">` | AC-5.5, FR-017 |
| `BackLink` | `ui/_volver.html` | `components/back-link.tsx` | `destino`, `texto` ("← Sorteos") | — | Enlace con el nombre del destino | AC-5.6, FR-017 |
| `FrequencyChart` | `estadisticas/_grafico.html` (SVG del servidor, existente, rediseñado) | `components/frequency-chart.tsx` (componente de servidor que genera el SVG; sin Recharts, R-18) | frecuencias, número consultado | cargando (Skeleton), con datos | `role="img"` con descripción; la tabla con la misma información siempre presente; colores de tokens en ambos temas | AC-7.5, FR-024 |

Los fragmentos de Django se incluyen con `{% include "ui/_boton.html" with variante="destructivo" texto=… icono="trash-2" %}`; sus clases salen del filtro `{% clases %}` (R-04).

## 2. Iconos (lista cerrada, Lucide)

Un único estilo: trazo de 2 px, 20 px en controles y 16 px en etiquetas. Siempre `aria-hidden="true"` y acompañados de texto (AC-13.5).

| Uso | Icono | Uso | Icono |
|-----|-------|-----|-------|
| En curso | `loader-circle` | Calendario | `calendar` |
| Finalizada / éxito | `circle-check` | Acciones (⋮) | `ellipsis-vertical` |
| Con advertencias / advertencia | `triangle-alert` | Eliminar | `trash-2` |
| Sin sorteos | `circle-dashed` | Descargar CSV | `download` |
| Con error / error | `circle-x` | Ver detalle | `arrow-right` |
| Información | `info` | Volver | `arrow-left` |
| Menú móvil | `menu` / `x` | Orden ascendente / descendente / sin orden | `arrow-up` / `arrow-down` / `arrow-up-down` |
| Cuenta | `circle-user-round` | Mostrar / ocultar contraseña | `eye` / `eye-off` |
| Tema claro / oscuro / dispositivo | `sun` / `moon` / `monitor` | Sin conexión / reintentar | `wifi-off` / `rotate-cw` |
| Jugada (estado vacío) | `ticket` | Estadísticas (estado vacío) | `chart-column` |
| Resultados (estado vacío) | `list-ordered` | Limpiar filtros | `filter-x` |
| Cerrar aviso | `x` | Cargar sorteo | `plus` |

Agregar un icono exige agregarlo a esta tabla.

## 3. Reglas de composición

- **Un solo botón principal por pantalla** (RN-11); en móvil, los botones principales ocupan el ancho y quedan al alcance del pulgar.
- `accent` nunca en el mismo botón que `primary` (RN-12).
- Ninguna acción principal es solo un icono (AC-13.5); el ⋮ es secundario y tiene nombre accesible.
- Estados de carga: toda acción de más de 1 s muestra estado de trabajo o Skeleton (FR-034); la respuesta visible aparece en menos de 100 ms (NFR-005).
- Textos largos: `truncate` + texto completo accesible (FR-030).
- Un componente nuevo se agrega a este catálogo, a Figma y (Etapa 2) a Storybook con todos sus estados.

## 4. Versión sin scripts de cada componente interactivo (NFR-007)

Ambas implementaciones deben ofrecer la misma versión básica (decisión del 21/11/2026, CHK005).

| Componente | Sin scripts (Django y Next.js) |
|------------|--------------------------------|
| `ActionMenu` | Django: `<details>`. Next.js: cada fila es un enlace a su detalle, donde "Descargar CSV" y "Eliminar" son un enlace y un formulario comunes |
| `ConfirmDialog` | Página de confirmación aparte (Next.js: la ruta completa `[id]/eliminar/`, que la ruta interceptada muestra como diálogo cuando hay scripts) |
| `DateField`, `DateRangePicker` | `<input type="date">` del navegador con `min`/`max`; los atajos son botones de un formulario GET que el servidor responde con las fechas completas |
| `Toast` | Los avisos se muestran como `Callout` dentro de la página |
| `ThemeSelect` | Formulario `POST /preferencias/tema/` |
| `NavBar` (menú móvil), `AccountMenu` | Lista de enlaces visible y formulario "Salir" visible |
| `PasswordField` | Contraseña siempre oculta |
| `DataTable`, `Pagination` | Encabezados y paginación como enlaces con parámetros en la dirección |
| `ProgressPanel` | El avance se actualiza al recargar la página |
| `FrequencyChart` | SVG generado en el servidor (igual con o sin scripts) |
| Validación previa | La valida el servidor y devuelve el formulario con los mensajes por campo |
