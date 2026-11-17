# Catálogo de mensajes visibles

**Plan**: [../plan.md](../plan.md) | **Rutas**: [rutas.md](rutas.md)

Estos son los textos exactos que fija la especificación. La implementación los usa **literalmente** y las pruebas de integración los verifican (Const. VI y VII). Los textos marcados con † los propuso el plan a partir de la spec y el responsable del proyecto los aprobó tal como están el 13/11/2026 (spec.md, Clarifications). La marca se conserva solo para la trazabilidad.

Variables: `{N}` = número de concurso, `{fecha}` = `dd/mm/aaaa`, `{nn}` = número con dos dígitos, `{hora}` = `HH:MM`.

## Resultados públicos

| Clave | Texto | Origen |
|-------|-------|--------|
| `resultados.pendientes` | Resultados pendientes | AC-1.2, AC-2.1 |
| `resultados.sin_publicar` | Todavía no hay resultados publicados | AC-1.13 |
| `resultados.concurso_inexistente` | No hay información del concurso N.º {N} | AC-1.4 |
| `resultados.fecha_sin_concursos` † | No hay información de concursos del {fecha} | P-07 |
| `modalidad.resultado_pendiente` | Resultado pendiente | RN-20 |
| `modalidad.pendiente_validacion` | Pendiente de validación | RN-20 |
| `concurso.incompleto` | Incompleto | AC-1.5 |
| `concurso.completo` | Completo | AC-1.6 |
| `premios.pendientes` | Información de premios pendiente de publicación | AC-1.8, AC-1.9, AC-5.3, AC-5.7, RN-27. Es el único texto para un importe faltante, ya sea porque la información de premios no se publicó o porque se publicó sin el importe individual (Clarifications 13/11/2026). |
| `premios.cero_ganadores` | 0 ganadores | AC-1.10 |
| `aviso.corregido` | Corregido el {fecha} | AC-1.11, RN-24 |
| `aviso.en_revision` | Información en revisión | AC-1.12, RN-24 |

## Administración

| Clave | Texto | Origen |
|-------|-------|--------|
| `admin.concurso_duplicado` | El concurso N.º {N} ya existe | AC-2.2 |
| `admin.sin_permiso` | No tenés permisos para acceder a esta sección | AC-2.11 |
| `admin.premio_extra_requiere` † | Premio Extra requiere Primer Sorteo, La Segunda y Revancha | P-06 |
| `admin.confirmar_cotejo` † | Confirmo que cotejé esta información con la fuente oficial | RN-17 e |

## Cuentas

| Clave | Texto | Origen |
|-------|-------|--------|
| `cuenta.credenciales_incorrectas` | Correo electrónico o contraseña incorrectos | AC-3.5 |
| `cuenta.bloqueada` † | Por seguridad, bloqueamos el acceso por 15 minutos. Podés volver a intentar a las {hora}. | AC-3.6 |
| `cuenta.correo_existente` † | Ya existe una cuenta con este correo electrónico. Iniciá sesión. | AC-3.3 |
| `cuenta.contrasena_corta` † | La contraseña debe tener al menos 8 caracteres. | AC-3.2 |
| `cuenta.correo_invalido` † | Ingresá un correo electrónico válido. | AC-3.2 |

## Jugadas

| Clave | Texto | Origen |
|-------|-------|--------|
| `jugada.registrada` | Jugada registrada | AC-4.1 |
| `jugada.actualizada` | Jugada actualizada | AC-4.10 |
| `jugada.eliminada` | Jugada eliminada | AC-4.11 |
| `jugada.faltan` † | Te faltan {n} números | AC-4.2 |
| `jugada.exactamente_seis` † | La jugada admite exactamente seis números | AC-4.3 |
| `jugada.fuera_de_rango` † | Ingresá un número entre 00 y 45 | AC-4.4 |
| `jugada.repetido` | El {nn} ya está en tu jugada | AC-4.5 |
| `jugada.elegi_concurso` | Elegí el concurso de tu jugada | AC-4.6 |
| `jugada.concurso_no_disponible` | Este concurso todavía no está disponible para registrar jugadas | AC-4.7 |
| `jugada.concurso_cerrado` | Ya no se pueden registrar jugadas para este concurso porque sus resultados fueron publicados | AC-4.8 |
| `jugada.duplicada` | Ya registraste una jugada con estos números para este concurso. ¿Querés guardarla igual? | RN-06 |
| `jugada.no_existe` | La jugada no existe o no está disponible | AC-4.12 |
| `jugada.historial_vacio` | Todavía no registraste jugadas | AC-4.13 |
| `jugada.costo_vacio` | Ingresá el costo de tu jugada | AC-4.16 |
| `jugada.costo_invalido` † | Ingresá un importe válido, mayor o igual a cero y con hasta dos decimales (por ejemplo, 1500,50) | AC-4.16 |
| `jugada.fija` | Esta jugada no se puede modificar ni eliminar porque los resultados de su concurso ya fueron publicados | AC-4.17 |
| `jugada.confirmar_eliminacion` † | ¿Querés eliminar esta jugada? Esta acción no se puede deshacer. | AC-4.11 |

## Comparación

| Clave | Texto | Origen |
|-------|-------|--------|
| `comp.aciertos_sin_premio` | {n} aciertos — Sin premio | AC-5.4, AC-5.5 |
| `comp.con_premio` | Con premio — {categoría} | AC-5.6, RN-29 |
| `comp.pendiente_determinacion` | Premio pendiente de determinación | AC-5.11, RN-29 |
| `comp.en_revision` | Información en revisión: el resultado podría cambiar | AC-5.12 |
| `comp.actualizado` | Actualizado por corrección del resultado oficial el {fecha} | AC-5.9, RN-32 |
| `comp.excluida` | Excluida del Premio Extra: obtuvo 6 aciertos en {sorteo} | AC-5.25, RN-53 |
| `comp.participa` | Participa | RN-29 |
| `comp.aciertos_superan` | Los aciertos de tu jugada superan la categoría ganadora publicada. Verificá los números y el concurso de tu jugada. | RN-52 e |

Nombres de categoría: "Primer Premio", "Segundo Premio", "Tercer Premio", "Premio Revancha", "Siempre Sale ({n} aciertos)" y "Premio Extra ({n} aciertos)".

## Estadísticas

| Clave | Texto | Origen |
|-------|-------|--------|
| `est.sin_sorteos` | No hay sorteos publicados de {modalidad} en el período seleccionado | AC-6.4 |
| `est.huecos` | El período incluye {n} concursos sin información disponible para esta modalidad | AC-6.7 |
| `est.periodo_invalido` † | La fecha desde no puede ser posterior a la fecha hasta. Corregí el período. | AC-6.8 |
| `est.leyenda` | Estadística descriptiva de sorteos pasados. No predice resultados futuros. | AC-6.9 |

## Generales

| Clave | Texto | Origen |
|-------|-------|--------|
| `gral.cargando` † | Cargando… | NFR-004, NFR-008 |
| `gral.pagina_inexistente` † | La página que buscás no existe | NFR-008 |
| `gral.error` † | Ocurrió un error. Intentá de nuevo en unos minutos. | NFR-008 |
