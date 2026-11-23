# Línea base de rendimiento y accesibilidad

**Plan**: [plan.md](plan.md) | **Research**: R-24 | **Tareas**: T035 (referencia histórica), T146 (línea base definitiva al cerrar la Etapa 1)

## Referencia histórica — Fase 0 (21/11/2026)

Medida con `npm run lhci` (`scripts/lhci.mjs`): Lighthouse 12 con el perfil móvil por defecto (4G lento simulado, CPU ×4), 5 corridas por pantalla, mediana, datos de `preparar_e2e` en `e2e.sqlite3`, sesión de administración para las pantallas privadas.

| Pantalla | LCP (ms) | CLS | TBT (ms) | JavaScript transferido (kB) |
|----------|---------:|----:|---------:|----------------------------:|
| `/resultados/` | 2953 | 0,000 | 124 | 187,1 |
| `/estadisticas/` | 2965 | 0,000 | 78 | 187,1 |
| `/mis-jugadas/` | 2605 | 0,000 | 62 | 187,1 |
| `/administracion/extracciones/` | 2941 | 0,000 | 62 | 190,9 |

**Condiciones y advertencias** (por eso es solo referencia):

- Servidor de desarrollo de Django (`runserver`, `QUINI6_DEBUG=1`): sin compresión ni caché de archivos estáticos (en producción, WhiteNoise sirve los archivos comprimidos y con nombre versionado). El JavaScript se mide **sin comprimir**; el presupuesto de R-24 se refiere a JavaScript comprimido.
- Se midió con las bibliotecas de la Etapa 1 ya cargadas en `base.html` (T025: HTMX, Alpine.js con `anchor` y `focus`, Cally), que explican casi todo el JavaScript.
- TBT es el indicador de laboratorio de la interactividad; INP se mide con usuarios reales y no está disponible en Lighthouse de laboratorio.

## Línea base definitiva — cierre de la Etapa 1 (22/11/2026)

T146: mismo procedimiento que la referencia (`npm run lhci`, perfil móvil, 5 corridas, mediana, datos de `preparar_e2e`, `runserver` en el puerto 8001), sobre la versión de Django de la Etapa 1 que la Etapa 2 reemplaza.

| Pantalla | LCP (ms) | CLS | TBT (ms) | JavaScript transferido (kB) |
|----------|---------:|----:|---------:|----------------------------:|
| `/resultados/` | 2330 | 0,000 | 348 | 176,7 |
| `/estadisticas/` | 2135 | 0,000 | 416 | 176,7 |
| `/mis-jugadas/` | 2151 | 0,000 | 207 | 176,7 |
| `/administracion/extracciones/` | 1994 | 0,000 | — (ver nota) | 176,7 |

**Lectura frente a R-24** (presupuesto: LCP ≤ 2,5 s, CLS ≤ 0,05, TBT ≤ 200 ms, JavaScript ≤ 200 kB):

- LCP, CLS y JavaScript dentro del presupuesto. La primera medición dio CLS 0,087 (Estadísticas) y 0,122 (Extracción histórica): el botón "Abrir calendario" aparecía recién al iniciar Alpine y, en el ancho del teléfono, los dos campos de fecha pasaban a dos líneas. Se corrigió mostrándolo desde la primera pintura con `html.js` (`solo-con-scripts` en `estilos/django.css`). Cally ya no se carga en todas las páginas: se importa al enfocar un campo de fecha o abrir el calendario (`static/js/ui.js`, `data-cally` en `<html>`), lo que bajó el JavaScript inicial de 214 kB a 176,7 kB.
- **TBT por encima del presupuesto** en Resultados y Estadísticas (348 y 416 ms; en la referencia de la Fase 0, 124 y 78 ms). La causa principal medida es la evaluación de Alpine.js (≈ 300 ms con la CPU ×4 simulada) y el estilo y la maquetación de la página. Es la línea de comparación para la Etapa 2; el presupuesto es de advertencia (`warn` en `lighthouserc.json`).
- **Extracción histórica sin TBT**: Lighthouse informa "la página tardó demasiado en cargarse" porque la fila "En curso" de los datos de prueba se consulta cada 3 s con HTMX (R-10) y la red nunca queda inactiva. Para medirla haría falta una base sin extracciones en curso.
- Mismas advertencias que la referencia: servidor de desarrollo sin compresión (en producción, WhiteNoise comprime y el JavaScript transferido es menor).

## Etapa 2 — Next.js detrás del enrutador (22/11/2026)

T180, T186, T192 y T197: mismo procedimiento (`npm run lhci -- --base http://localhost:8088 --ingreso http://127.0.0.1:8001`, perfil móvil, 5 corridas, mediana, datos de `preparar_e2e`, mismo equipo), con las seis pantallas conmutadas en `QUINI6_RUTAS_NEXT`, Next.js compilado (`next build` + `next start`, comprimido con gzip) y Django en el puerto 8001.

| Pantalla | LCP (ms) | CLS | TBT (ms) | JavaScript transferido (kB, comprimido) | Primera medición (kB) |
|----------|---------:|----:|---------:|----------------------------------------:|----------------------:|
| `/resultados/` (pública) | 1781 | 0,000 | 218 | 168,5 | 238,3 |
| `/estadisticas/` (pública) | 1686 | 0,000 | 152 | 172,9 | 284,0 |
| `/mis-jugadas/` (privada) | 1519 | 0,000 | 128 | 166,7 | 238,3 |
| `/administracion/extracciones/` (privada) | 1700 | 0,000 | — (ver nota) | 187,9 | 303,1 |

**Lectura frente a R-24**:

- **LCP** mejor que la línea base de Django en las cuatro pantallas (entre −294 y −632 ms) y por debajo de 2,5 s. **CLS** 0 en todas.
- **TBT** mejor que Django en las tres medibles (218/152/128 ms frente a 348/416/207). Resultados queda 18 ms por encima de la advertencia de 200 ms (`warn`); TBT es el indicador de laboratorio, INP se mide con usuarios reales.
- **JavaScript**: privadas dentro de ≤ 200 kB. Públicas: el piso de Next.js 16 + React 19 es ≈ 130 kB en una página vacía, así que ≤ 120 kB no se alcanza con el stack elegido; **desviación aprobada por el responsable el 22/11/2026** (R-24): lo más bajo posible sobre ese piso. Lo que queda por encima del piso es lo que la pantalla usa (catálogo de textos, formularios, estructura común).
- La columna de JavaScript **no se compara con Django**: la línea base de la Etapa 1 se midió sin comprimir (servidor de desarrollo) y esta, comprimida.
- **Optimizaciones** que llevaron de la primera medición a la final: research.md § "Ajustes al correr los guiones contra Next.js".
- **Extracción histórica sin TBT**, como en la Etapa 1: la fila "En curso" de los datos de prueba se consulta cada 3 s y la red nunca queda inactiva.
