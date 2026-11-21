# Catálogo de mensajes visibles: Extracción histórica de sorteos

**Plan**: [../plan.md](../plan.md) | **Rutas**: [rutas.md](rutas.md) | **Catálogo general**: [001] [contracts/mensajes.md](../../001-quini6-mvp/contracts/mensajes.md)

La implementación usa estos textos **literalmente** y las pruebas de integración los verifican (Const. VI y VII). Marcas:

- **†**: texto propuesto por el agente (en la spec, en la planificación o en el análisis) y aprobado por el responsable el 19/11/2026. La marca se conserva solo para la trazabilidad.
- Los textos que el plan había propuesto con la marca ‡ (P-01) los aprobó el responsable el 19/11/2026 en el análisis, tal como están, y pasaron a †. No quedan textos pendientes de aprobación.

Variables: `{N}` número de sorteo, `{fecha}` `dd/mm/aaaa`, `{n}` cantidad, `{texto}` texto original de la fuente (entre « »), `{fuente}` nombre de la fuente, `{modalidad}` nombre de la modalidad.

## Pantalla y período

| Clave | Texto | Origen |
|-------|-------|--------|
| `ext.titulo` | Extracción histórica de sorteos | FR-001, AC-1.1 |
| `ext.campo_inicio` | Fecha de inicio | AC-1.1 |
| `ext.campo_fin` | Fecha de finalización | AC-1.1 |
| `ext.boton_iniciar` † | Iniciar extracción | AC-1.1 |
| `ext.fecha_invalida` † | Ingresá una fecha válida (dd/mm/aaaa) | AC-1.4 |
| `ext.inicio_posterior` † | La fecha de inicio no puede ser posterior a la fecha de finalización | AC-1.3, RN-02 |
| `ext.fin_futura` † | La fecha de finalización no puede ser posterior a hoy | AC-1.5, RN-03 |
| `ext.periodo_largo` † | El período no puede superar los 12 meses | AC-1.6, RN-04 |
| `ext.anteriores` † | Extracciones anteriores | AC-1.14 |
| `ext.boton_descargar` † | Descargar CSV | AC-5.1 |
| `ext.enlace_oficial` † | Ver extracto oficial (Lotería de Santa Fe) | AC-1.13 |
| `ext.col_fecha` | Fecha | AC-1.14 (20/11/2026, D-24; antes "Inicio") |
| `ext.acciones` | Acciones de la extracción del {fecha y hora} | AC-1.18 (20/11/2026, D-24); nombre accesible del menú ⋮ |
| `ext.eliminar` | Eliminar | AC-1.18 (D-24) |
| `ext.eliminar_titulo` | Eliminar extracción | AC-1.18 (D-24) |
| `ext.eliminar_confirmar` | ¿Querés eliminar esta extracción? Se borran su resumen, el detalle de sus sorteos y su archivo CSV. Esta acción no se puede deshacer. | AC-1.18 (D-24) |
| `ext.cancelar` | Cancelar | AC-1.18 (D-24) |
| `ext.eliminada` | Extracción eliminada | AC-1.18 (D-24) |
| `ext.eliminar_en_curso` | No se puede eliminar una extracción en curso | AC-1.19 (D-24) |

## Estado y avance

| Clave | Texto | Origen |
|-------|-------|--------|
| `ext.en_curso` † | Extracción en curso | AC-1.2 |
| `ext.identificando` † | Identificando los sorteos del período… | AC-1.2 (Clarifications 19/11/2026, planificación) |
| `ext.avance` † | {n} de {m} sorteos procesados | AC-1.2; también es el nombre accesible de la barra de progreso (AC-1.21, D-26) |
| `ext.finalizada` † | Extracción finalizada | AC-1.9 |
| `ext.con_advertencias` † | Extracción finalizada con advertencias que requieren revisión | AC-1.9 |
| `ext.sin_sorteos` † | No se identificaron sorteos en el período consultado | AC-1.10 |
| `ext.sin_cobertura` † | Las fuentes no cubren el período anterior al {fecha} | AC-1.17 |
| `ext.huecos` † | Hay números de sorteo que ninguna fuente informa: {lista} | AC-1.16 ("el resumen advierte el hueco") |
| `ext.requiere_mantenimiento` † | Requiere mantenimiento | AC-2.10 |

Rótulos del resumen (RN-33): "Período consultado", "Sorteos identificados", "Recuperados", "Recuperados parcialmente", "Con inconsistencias", "No recuperados", "Fuentes utilizadas", "Sorteos aportados", "Intentos fallidos", "Sorteos que requieren revisión". Aprobados por el responsable el 19/11/2026 (análisis).

## Estados de un sorteo, de una fuente y de un dato

| Clave | Texto | Origen |
|-------|-------|--------|
| `sorteo.recuperado` | Recuperado | RN-31 |
| `sorteo.parcial` | Recuperado parcialmente | RN-31 |
| `sorteo.inconsistencias` † | Con inconsistencias | RN-31, AC-4.1 |
| `sorteo.no_recuperado` † | No recuperado | RN-31, AC-2.7 |
| `sorteo.combina` † | Combina fuentes | RN-29, AC-4.7 |
| `sorteo.reglas_no_verificadas` † | Reglas del período no verificadas | RN-25, AC-3.11 |
| `intento.obtenido` | Obtenido | RN-08 |
| `intento.incompleto` † | Incompleto | RN-08, AC-2.5 |
| `intento.no_encontrado` † | No encontrado | RN-08, AC-2.3 |
| `intento.no_disponible` † | No disponible | RN-08, AC-2.2 |
| `intento.no_disp_o_no_enc` † | No disponible o no encontrado | RN-08, AC-2.3 |
| `intento.estructura` † | Estructura no reconocida | RN-08, AC-2.4 |
| `intento.fuera_cobertura` † | Fuera de cobertura | RN-08, AC-2.6 |
| `intento.no_requerida` | No requerida | RN-08, RN-09, AC-2.11 (20/11/2026) |
| `dato.no_disponible` † | No disponible | RN-20 |
| `dato.no_corresponde` † | No corresponde | RN-20, AC-3.4 |
| `dato.sin_determinar` † | Sin determinar | RN-20, AC-4.1 |
| `dato.sin_corroborar` † | Sin corroborar | RN-32, AC-4.8 |
| `pozo.con_ganadores` | Con ganadores | RN-19 |
| `pozo.vacante` | Vacante | RN-19 |
| `pozo.pendiente` † | Pendiente | RN-19, AC-3.7 |
| `modalidad.no_informada` † | No informada por las fuentes | RN-25, AC-3.12 |
| `disc.valor` | Valor distinto | RN-27 |
| `disc.omision` † | Omisión | RN-28, AC-4.2 |
| `disc.centavos` | Diferencia de centavos o redondeo (menor al 1 %) | RN-30, AC-4.5 (20/11/2026); nota informativa, no es discrepancia |
| `disc.mayoria` | Resuelto por coincidencia de 2 de 3 fuentes | RN-07, AC-4.10, AC-4.11 (20/11/2026, D-21); nota informativa, no es discrepancia |
| `dato.calculado` | Calculado: {cálculo} | RN-12, RN-18, D-16, D-19 (20/11/2026) |
| `calculo.pozo` | importe individual × ganadores | RN-18, AC-3.5 |
| `calculo.vacante` | sin ganadores | RN-18, AC-3.4 |
| `calculo.pozo_extra` | unión de Tradicional, La Segunda y Revancha | RN-12, AC-3.17 |

## Observaciones y motivos del detalle

| Clave | Texto | Origen |
|-------|-------|--------|
| `obs.importe_invalido` † | Importe con formato no reconocido: «{texto}» | RN-16, AC-3.8 |
| `obs.importe_corregido` | Importe corregido: «{texto}» → {importe} | RN-16, AC-3.16 y AC-3.18 (20/11/2026; D-18 y D-20); informativa |
| `obs.premio_extra_no_coincide` † | Los números de Pozo Extra de la fuente no coinciden con sus extracciones | RN-12, AC-3.13 |
| `obs.sin_fuente` † | Ninguna fuente informa este número de sorteo | RN-05, AC-1.16 |
| `obs.numeros_cantidad` † | {modalidad}: la fuente publica {n} números en lugar de seis. No se usan. | RN-24, AC-3.9 |
| `obs.numeros_repetido` † | {modalidad}: la fuente repite el número {nn}. No se usan. | RN-24, AC-3.9 |
| `obs.numeros_rango` † | {modalidad}: la fuente publica «{texto}», fuera de 00 a 45. No se usan. | RN-24, AC-3.9 |
| `obs.rotulo_desconocido` † | Rótulo no reconocido: «{texto}». Ese bloque no se asignó a ninguna modalidad. | RN-10, RN-11 |
| `obs.categoria_fuera_catalogo` † | Categoría fuera del catálogo: «{texto}». No se asignó. | RN-14 |
| `obs.concepto_importe` † | No se pudo determinar si el importe «{texto}» es pozo o premio individual. | RN-17 |
| `obs.falta` † | Falta: {lista de datos} | AC-2.5 ("indica qué falta") |
| `obs.no_correlativo` † | El número y la fecha no son correlativos con el sorteo N.º {N} | RN-23 |
| `obs.siempre_sale_invalida` † | Siempre Sale: la categoría ganadora informada no es válida (debe tener entre 0 y 6 aciertos y al menos un ganador) | RN-26 |
| `obs.premio_extra_invalida` † | Pozo Extra: la categoría ganadora informada no es 6, 5, 4 ni "Sin ganadores" | RN-26 |
| `obs.negativo` † | La fuente publica un valor negativo: «{texto}». No se usa. | RN-26 |
| `obs.extracciones_iguales` † | {modalidad} y {modalidad}: la fuente publica los mismos seis números | RN-26 (advertencia) |
| `obs.direccion_no_coincide` † | El número o la fecha de la página no coinciden con los de la dirección consultada | RN-21 |
| `obs.pozo_premio_extra_texto` † | Pozo Extra publicado como «{texto}» | RN-17 (Clarifications 19/11/2026, planificación); informativa |
| `obs.error_interprete` † | La página de la fuente no se pudo interpretar | RN-10, [002] I-09 (a) |
| `motivo.error_inesperado` † | Error inesperado al procesar el sorteo | RN-31, NFR-006, [002] I-09 (b); aprobado el 19/11/2026 (análisis) |

Los motivos de un sorteo "No recuperado" son el resultado de cada fuente: "{fuente}: {resultado del intento}" (AC-2.7).

## Mensajes heredados de [001]

| Clave | Texto | Uso |
|-------|-------|-----|
| `admin.sin_permiso` | No tenés permisos para acceder a esta sección | AC-6.1, AC-6.6 |
| `gral.pagina_inexistente` | La página que buscás no existe | Extracción o sorteo inexistente |
| `gral.cargando` | Cargando… | NFR-011 |
| `gral.error` | Ocurrió un error. Intentá de nuevo en unos minutos. | Error inesperado |
