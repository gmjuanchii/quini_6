# Verificación del cierre de la Etapa 1

**Plan**: [plan.md](plan.md) § Etapa 1 (criterio de terminado, CHK012) | **Escenarios**: [quickstart.md](quickstart.md) § 4 | **Tareas**: T144, T145, T147 | **Fecha**: 22/11/2026

## 1. Pruebas automáticas (T144)

| Verificación | Resultado |
|--------------|-----------|
| `ruff check .` | Sin observaciones |
| `pytest` en SQLite | 1380 pasaron, 2 omitidas |
| `pytest` en PostgreSQL 16 | A cargo del CI por decisión del responsable (22/11/2026): el trabajo `python` de `.github/workflows/ci.yml` lo corre contra el servicio `postgres:16` |
| `npm run e2e` (5 proyectos: `escritorio`, `movil`, `sin-scripts`, `oscuro`, `movimiento-reducido`) | 270 pasaron y 6 fallaron en la corrida completa; los 6 eran de los guiones (selectores que quedaron viejos al agregar los encabezados ordenables y el calendario), no de la aplicación; corregidos y vueltos a correr en verde |
| axe (0 críticos y 0 graves) | Incluido en cada guion de HU-01 a HU-13, en ambos temas (HU-12 recorre siete pantallas en claro y en oscuro) |
| Sin desplazamiento horizontal a 360 px y con el texto al 200 % | `zoom-teclado.spec.ts` recorre ocho pantallas en escritorio y teléfono |

## 2. Escenarios de quickstart § 4 (T145)

Cada escenario tiene su guion automático; la columna "Manual" queda para la revisión con teclado y NVDA del responsable (Const. VI), que no se puede automatizar.

| # | Escenario | Evidencia automática | Manual (teclado + NVDA) |
|---|-----------|----------------------|-------------------------|
| 1 | Estados de extracción | `hu01-estados.spec.ts`, `test_003_us1_estados.py` | Pendiente (incluye escala de grises) |
| 2 | Filtro, orden y paginación | `hu01`, `hu09-tablas.spec.ts`, `test_003_us9_tablas.py` | Pendiente |
| 3 | Menú ⋮ y confirmación | `hu02-eliminar.spec.ts`, `test_003_us2_eliminar.py` | Pendiente |
| 4 | Avance en vivo | `hu03-avance.spec.ts` (servidor de fuentes de prueba) | Pendiente |
| 5 | Período repetido | `test_003_us3_periodo_unico.py` | Pendiente |
| 6 | Volver más tarde | `hu03-avance.spec.ts` | Pendiente |
| 7 | Fechas | `hu04-fechas.spec.ts`, `test_003_us4_fechas.py` | Pendiente |
| 8 | Navegación | `hu05-navegacion.spec.ts`, `test_003_us5_navegacion.py` | Pendiente |
| 9 | Ingreso | `hu06-ingreso.spec.ts`, `test_003_us6_ingreso.py` | Pendiente (gestor de contraseñas real) |
| 10 | Estadísticas | `hu07-estadisticas.spec.ts`, `test_003_us7_estadisticas.py` | Pendiente |
| 11 | Estados vacíos | `hu08-vacios.spec.ts` (`preparar_e2e --vacio`), `test_003_us8_vacios.py` | Pendiente |
| 12 | Tablas a 360 px | `hu09-tablas.spec.ts`, `test_003_us9_columnas.py` | Pendiente |
| 13 | Avisos y pie | `hu10-avisos.spec.ts`, `test_003_us10_avisos.py` | Pendiente (anuncios del lector) |
| 14 | Lenguaje | `hu11-lenguaje.spec.ts`, `test_textos_prohibidos.py`, `test_botones_con_verbo.py` | Pendiente |
| 15 | Tema | `hu12-tema.spec.ts`, `test_003_us12_tema.py` | Pendiente |
| 16 | Movimiento | `hu13-acabado.spec.ts` (proyecto `movimiento-reducido`) | Pendiente |
| 17 | Sin conexión | `robustez.spec.ts` | Pendiente |
| 18 | Sesión vencida | `robustez.spec.ts`, `test_003_formulario_pendiente.py` | Pendiente |
| 19 | Sin scripts | `sin-scripts.spec.ts` y el proyecto `sin-scripts` de cada guion | Pendiente |
| 20 | Zoom y teclado | `zoom-teclado.spec.ts` | Pendiente (NVDA) |
| 21 | Datos sin cambios | § 3 | No hace falta |

## 3. Datos sin cambios respecto de `main` (T147, NFR-009, SC-011)

Con la misma base (copia de `e2e.sqlite3` preparada por `preparar_e2e`), se pidieron las páginas a la versión de `main` (copia de trabajo aparte) y a esta rama, y se extrajeron solo los valores de negocio, sin depender del marcado ni de los textos:

| Pantalla | Comparado | Resultado |
|----------|-----------|-----------|
| Resultados | Números sorteados, importes y porcentajes del detalle de los 21 sorteos | Idénticos |
| Estadísticas | Las 46 filas (número, frecuencia, porcentaje) de las 4 modalidades, con y sin número consultado, y la frase del número consultado | Idénticas |
| Mis jugadas | Lista y los 3 detalles: números, aciertos resaltados, importes | Idénticos |
| CSV de extracción | SHA-256 de los 25 archivos CSV de las extracciones terminadas | Idénticos byte a byte |

## 4. Textos que conviene confirmar

Cambios de redacción hechos por la regla de forma neutra (D-01) o el glosario (D-04), sin clave propia en `contracts/mensajes.md`:

- "Elegiste los seis números" → "Seis números elegidos" (contador del selector de números).
- "Solo te pedimos un correo electrónico y una contraseña." → "Solo se pide un correo electrónico y una contraseña." (Crear cuenta).
- "Indicá el motivo…", "Indicá la fuente…", "Indicá la fecha…" → "Falta el motivo…", "Falta la fuente…", "Falta la fecha…" (administración de sorteos; § 1.2 del contrato).
- "La extracción debe tener exactamente seis números", "La extracción tiene exactamente seis números" → "Los números sorteados…" (glosario).
- "Premio Extra no se ofrece en las estadísticas porque no es una extracción independiente" → "…porque no tiene números sorteados propios".
- Pendiente de aprobación: `obs.premio_extra_no_coincide` ([002], aprobado) usa "extracciones" por números sorteados; queda como excepción en `test_textos_prohibidos.py` hasta que el responsable apruebe un texto nuevo.

## 5. Última corrida (22/11/2026)

Con todos los cambios finales: `ruff check .` limpio; `pytest` 1380 en verde; `npm run e2e` 276 en verde y 129 omitidos por proyecto (cada guion declara en qué proyectos corre), 0 fallidos.
