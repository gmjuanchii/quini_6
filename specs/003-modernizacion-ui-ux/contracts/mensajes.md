# Catálogo de mensajes visibles: Modernización visual y de experiencia de uso

**Plan**: [../plan.md](../plan.md) | **Catálogos anteriores**: [001](../../001-quini6-mvp/contracts/mensajes.md), [002](../../002-extraccion-historica-csv/contracts/mensajes.md) | **Research**: R-13

Desde esta feature, **todos** los textos visibles viven en `dominio/mensajes.py` (clave → texto) y se exportan a `contratos/mensajes.json` para Next.js. La implementación los usa literalmente y las pruebas verifican que el módulo coincida con este catálogo y con los de [001] y [002] para las claves que no cambian. Este documento registra **solo lo que cambia o se agrega**; las claves que no figuran aquí conservan el texto de su catálogo original.

**Formato verificable** (normalizado el 21/11/2026 para la prueba `tests/unit/test_mensajes_catalogo.py`): una clave por fila; el texto es la celda "Ahora" (§ 2 y § 3) o "Texto" (§ 4) hasta la primera marca ✓, † o ‡, o la celda completa si no tiene marca. Lo que sigue a la marca es una nota. Las claves de [001] y [002] que no aparecen aquí se toman de sus catálogos con la misma regla.

Marcas: **✓** texto literal de la spec 003 (aprobado) · **†** texto propuesto por el plan y **aprobado por el responsable el 21/11/2026** (P-04; antes marcado ‡) · **‡** texto propuesto, pendiente de aprobación · sin marca: cambio mecánico por el glosario (D-04: "concurso" → "sorteo"; "extracción" de números → "números sorteados").

Variables: `{N}` número de sorteo, `{fecha}` `dd/mm/aaaa`, `{fecha_hora}` `dd/mm/aaaa HH:MM`, `{hora}` `HH:MM`, `{n}`/`{m}` cantidades, `{nn}` número con dos dígitos, `{desde}`/`{hasta}` fechas de un período, `{filtro}` texto del filtro aplicado.

## 1. Reglas de redacción (D-01, RN-10, HU-11)

1. Forma **impersonal o neutra**: sin voseo ("tenés", "ingresá"), tuteo ("tienes") ni usted ("tiene usted"); sin posesivos de segunda persona ("tu jugada" → "la jugada"). La primera persona solo en rótulos que la persona dice de sí misma ("Mis jugadas", "Registrar mi primera jugada").
2. Errores de campo: "Falta {dato}" para obligatorios vacíos; "{Dato} no es válido/a" o la regla concreta ("El número debe estar entre 00 y 45").
3. Botones: verbo en infinitivo + objeto ("Iniciar extracción", "Registrar jugada"); nunca "Aceptar" u "OK" (AC-11.2).
4. Glosario (RN-10): **Sorteo** (evento con número y fecha), **Modalidad**, **Números sorteados**, **Jugada**, **Extracción histórica**. No se usan "concurso" ni "extracción" sola para números.
5. Prueba automática `tests/unit/test_textos_prohibidos.py`: busca en `dominio/mensajes.py`, `templates/` y `frontend/src/` las formas prohibidas (lista de verbos en voseo frecuentes, "tu ", "tus ", "\bconcurso", "\bextracci[oó]n\b" fuera de "Extracción histórica") y falla si aparece alguna en texto visible (SC-007).

## 2. Textos reescritos de [001]

| Clave | Antes | Ahora |
|-------|-------|-------|
| `resultados.concurso_inexistente` | No hay información del concurso N.º {N} | No hay información del sorteo N.º {N} |
| `resultados.fecha_sin_concursos` | No hay información de concursos del {fecha} | No hay información de sorteos del {fecha} |
| `admin.concurso_duplicado` | El concurso N.º {N} ya existe | El sorteo N.º {N} ya existe |
| `admin.sin_permiso` | No tenés permisos para acceder a esta sección | Sin permisos para acceder a esta sección ✓ |
| `admin.bloque_publicado` | Este bloque ya está publicado. Para modificarlo, iniciá una corrección. | Este bloque ya está publicado. Para modificarlo, es necesario iniciar una corrección. † |
| `admin.corregir_bloqueantes` | Corregí los errores bloqueantes antes de publicar. | Hay errores bloqueantes que corregir antes de publicar. † |
| `admin.ayuda_modalidades` | Podés agregar modalidades en cualquier momento. Solo podés quitar una modalidad sin información cargada y cambiar la fecha mientras ninguna extracción esté publicada. | Las modalidades se pueden agregar en cualquier momento. Solo se puede quitar una modalidad sin información cargada, y la fecha se puede cambiar mientras no haya números sorteados publicados. † |
| `admin.falta_numero_sorteo` | Ingresá el número de concurso. | Falta el número de sorteo † |
| `admin.numero_sorteo_invalido` | Ingresá un número de concurso válido. | El número de sorteo no es válido † |
| `admin.falta_modalidad` | Elegí al menos una modalidad aplicable. | Falta elegir al menos una modalidad † |
| `admin.modalidades_invalidas` | Elegí modalidades válidas. | Hay modalidades no válidas † |
| `admin.ganadores_invalidos` | Ingresá una cantidad de ganadores válida (0 o más). | La cantidad de ganadores debe ser 0 o más † |
| `admin.sin_ganadores_y_categoria` | Indicaste "sin ganadores" y también una categoría ganadora: elegí una sola opción. | Se indicó "sin ganadores" y también una categoría ganadora: corresponde elegir una sola opción. † |
| `admin.fecha_futura` | La fecha del sorteo es posterior a hoy: verificá que el sorteo ya se realizó. | La fecha del sorteo es posterior a hoy: es necesario verificar que el sorteo ya se realizó. † |
| `admin.numero_repetido` | El {nn} está repetido en la extracción | El {nn} está repetido en los números sorteados |
| `admin.numeros_rango` | Ingresá números entre 00 y 45 | Los números deben estar entre 00 y 45 † |
| `admin.crear` (botón y título) | Crear concurso | Cargar sorteo ✓ |
| `admin.titulo_listado` | Administración de concursos | Administración de sorteos |
| `admin.volver_listado` | ← Concursos | ← Sorteos ✓ |
| `admin.sin_concursos` | Todavía no hay concursos creados. | Todavía no hay sorteos cargados † |
| `cuenta.bloqueada` | Por seguridad, bloqueamos el acceso por 15 minutos. Podés volver a intentar a las {hora}. | Por seguridad, el acceso quedó bloqueado por 15 minutos. Es posible volver a intentarlo a las {hora}. † |
| `cuenta.correo_existente` | Ya existe una cuenta con este correo electrónico. Iniciá sesión. | Ya existe una cuenta con este correo electrónico. † (seguido del enlace "Ingresar") |
| `cuenta.correo_invalido` | Ingresá un correo electrónico válido. | El correo electrónico no tiene un formato válido ✓ |
| `cuenta.falta_correo` | Ingresá tu correo electrónico. | Falta el correo electrónico † |
| `cuenta.falta_contrasena` | Ingresá tu contraseña. | Falta la contraseña † |
| `cuenta.ir_a_registro` | ¿No tenés cuenta? Creá una | ¿Todavía sin cuenta? Crear cuenta ✓ |
| `cuenta.ir_a_ingreso` | ¿Ya tenés cuenta? Ingresá | ¿Ya hay una cuenta? Ingresar † |
| `jugada.faltan` | Te faltan {n} números | Faltan {n} números † |
| `jugada.fuera_de_rango` | Ingresá un número entre 00 y 45 | El número debe estar entre 00 y 45 ✓ |
| `jugada.repetido` | El {nn} ya está en tu jugada | El {nn} ya está en la jugada † |
| `jugada.elegi_concurso` | Elegí el concurso de tu jugada | Falta el sorteo de la jugada † |
| `jugada.concurso_no_disponible` | Este concurso todavía no está disponible para registrar jugadas | Este sorteo todavía no está disponible para registrar jugadas |
| `jugada.concurso_cerrado` | Ya no se pueden registrar jugadas para este concurso porque sus resultados fueron publicados | Ya no se pueden registrar jugadas para este sorteo porque sus resultados fueron publicados |
| `jugada.duplicada` | Ya registraste una jugada con estos números para este concurso. ¿Querés guardarla igual? | Ya hay una jugada registrada con estos números para este sorteo. ¿Guardarla igual? † |
| `jugada.historial_vacio` | Todavía no registraste jugadas | Todavía no hay jugadas registradas ✓ |
| `jugada.costo_vacio` | Ingresá el costo de tu jugada | Falta el costo de la jugada † |
| `jugada.costo_invalido` | Ingresá un importe válido, mayor o igual a cero y con hasta dos decimales (por ejemplo, 1500,50) | El importe debe ser mayor o igual a cero y tener hasta dos decimales (por ejemplo, 1500,50) † |
| `jugada.importe_formato` | Ingresá un importe válido, con hasta dos decimales (por ejemplo, 1500,50) | El importe debe tener hasta dos decimales (por ejemplo, 1500,50) † |
| `jugada.fija` | … porque los resultados de su concurso ya fueron publicados | Esta jugada no se puede modificar ni eliminar porque los resultados de su sorteo ya fueron publicados |
| `jugada.confirmar_eliminacion` | ¿Querés eliminar esta jugada? Esta acción no se puede deshacer. | ¿Eliminar esta jugada? Esta acción no se puede deshacer. † |
| `jugada.intro` | Registrá una jugada que hiciste fuera de la aplicación. QUINI_6 no vende apuestas ni realiza pagos. | Registro de una jugada hecha fuera de la aplicación. QUINI_6 no vende apuestas ni realiza pagos. † |
| `jugada.campo_sorteo` (etiqueta) | Concurso | Sorteo † |
| `jugada.opcion_sorteo` (opción vacía) | Elegí un concurso | Elegir un sorteo † |
| `jugada.ayuda_modalidades` | Elegí un concurso para ver en qué modalidades participará tu jugada. | Al elegir el sorteo se muestran las modalidades en las que participa la jugada. † |
| `jugada.elegir_numeros` | Elegí seis números (00 a 45) | Seis números (00 a 45) † |
| `jugada.escribir_numero` | Escribí un número | Número † |
| `comp.tu_jugada` | Tu jugada (los números acertados están resaltados): | Números de la jugada (los acertados están resaltados): † |
| `comp.numeros_resaltados` | Conjunto de números del Premio Extra: {n} números distintos. Tus números están resaltados. | Conjunto de números del Premio Extra: {n} números distintos. Los números de la jugada están resaltados. † |
| `comp.aciertos_superan` | Los aciertos de tu jugada superan la categoría ganadora publicada. Verificá los números y el concurso de tu jugada. | Los aciertos de la jugada superan la categoría ganadora publicada. Es necesario verificar los números y el sorteo de la jugada. † |
| `est.huecos` | El período incluye {n} concursos sin información disponible para esta modalidad | El período incluye {n} sorteos sin información disponible para esta modalidad |
| `est.periodo_invalido` | La fecha desde no puede ser posterior a la fecha hasta. Corregí el período. | La fecha «Desde» no puede ser posterior a la fecha «Hasta» † |
| `est.ayuda_periodo` | Si no elegís un período, se consideran todos los sorteos publicados de la modalidad. | Sin período, se consideran todos los sorteos publicados de la modalidad. † |
| `gral.fecha_invalida` | Ingresá una fecha válida con el formato dd/mm/aaaa | La fecha no es válida. Formato: dd/mm/aaaa † |
| `gral.pagina_inexistente` | La página que buscás no existe | La página buscada no existe † |
| `gral.error` | Ocurrió un error. Intentá de nuevo en unos minutos. | Ocurrió un error. Es posible volver a intentarlo en unos minutos. † |
| `gral.csrf_vencido` | No se pudo procesar el formulario porque venció. Volvé a cargar la página e intentá de nuevo | No se pudo procesar el formulario porque venció. Es necesario volver a cargar la página e intentarlo de nuevo. † |

Toda otra aparición visible de "concurso" en plantillas ("Concurso N.º {N}", "Historial del concurso N.º {N}", "Modificar concurso", "Ir al concurso existente") pasa a "sorteo" con el mismo criterio ("Sorteo N.º {N}", "Historial del sorteo N.º {N}", "Modificar sorteo", "Ir al sorteo existente").

## 3. Textos reescritos de [002]

| Clave | Antes | Ahora |
|-------|-------|-------|
| `ext.fecha_invalida` | Ingresá una fecha válida (dd/mm/aaaa) | La fecha no es válida. Formato: dd/mm/aaaa † (misma clave que `gral.fecha_invalida`) |
| `ext.eliminar_confirmar` | ¿Querés eliminar esta extracción? Se borran su resumen, el detalle de sus sorteos y su archivo CSV. Esta acción no se puede deshacer. | ¿Eliminar la extracción del {fecha_hora} ({desde} al {hasta})? Esta acción no se puede deshacer. ✓ + `ext.eliminar_consecuencias` |
| `ext.eliminada` | Extracción eliminada | Se eliminó la extracción del {fecha_hora} ✓ |
| `ext.boton_iniciar_trabajando` | — | Iniciando… ✓ |
| `ext.acciones` | Acciones de la extracción del {fecha y hora} | Acciones de la extracción del {fecha_hora} † (solo cambia el nombre de la variable) |

Los rótulos del resumen, los estados de sorteo, de fuente y de dato, y las observaciones de [002] no cambian (ya usan forma neutra).

## 4. Textos nuevos de [003]

### Etiquetas de estado (RN-01, RN-02)

| Clave | Texto | Origen |
|-------|-------|--------|
| `etiqueta.en_curso` | En curso ✓ | RN-01 |
| `etiqueta.en_curso.explicacion` | La extracción se está procesando. El avance se actualiza en esta pantalla. † | RN-01, RN-02 |
| `etiqueta.finalizada` | Finalizada ✓ | RN-01 |
| `etiqueta.finalizada.explicacion` | Todos los sorteos del período se recuperaron sin novedades. † | RN-01, RN-02 |
| `etiqueta.con_advertencias` | Con advertencias ✓ | RN-01 |
| `etiqueta.con_advertencias.explicacion` | Hay sorteos del período que requieren revisión manual. El detalle los muestra. ✓ | RN-01, RN-02, AC-1.2 |
| `etiqueta.sin_sorteos` | Sin sorteos ✓ | RN-01 |
| `etiqueta.sin_sorteos.explicacion` | Las fuentes no informaron sorteos en el período consultado. † | RN-01, RN-02 |
| `etiqueta.con_error` | Con error ✓ | RN-01 |
| `etiqueta.con_error.explicacion` | Hay sorteos del período que no se pudieron recuperar. El detalle muestra cuáles y qué respondió cada fuente. † | RN-01, RN-02 |

### Extracción histórica

| Clave | Texto | Origen |
|-------|-------|--------|
| `ext.filtro_estado` | Estado | AC-1.4 |
| `ext.filtro_todos` | Todos los estados ✓ | AC-1.4 |
| `ext.filtrar` | Filtrar ‡ | AC-1.4 (botón del filtro; con scripts el filtro se aplica al elegir) |
| `ext.requiere_revision` | Requiere revisión ‡ | AC-1.3 (marca de la fila, leída por lectores de pantalla) |
| `ext.filtro_aplicado` | Filtro aplicado: {filtro} † | AC-1.4 |
| `ext.ver_detalle` | Ver detalle → ✓ | AC-9.4 |
| `ext.eliminar_consecuencias` | Se pierden su resumen, el detalle de sus sorteos y su archivo CSV. † | AC-2.3 |
| `ext.periodo_en_curso` | Ya hay una extracción en curso para el período del {desde} al {hasta} ✓ | AC-3.5, RN-03 |
| `ext.ver_existente` | Ver esa extracción † | AC-3.5 |
| `ext.no_existe` | La extracción ya no existe ✓ | Casos límite |
| `ext.termino_finalizada` | La extracción terminó sin novedades † | AC-3.3 |
| `ext.termino_advertencias` | La extracción terminó con advertencias: {n} sorteos requieren revisión ✓ | AC-3.3 |
| `ext.termino_error` | La extracción terminó con error: {n} sorteos no se pudieron recuperar † | AC-3.3, AC-3.4 |
| `ext.termino_sin_sorteos` | La extracción terminó: las fuentes no informaron sorteos en el período † | AC-3.3 |
| `ext.ninguna_fuente` | No se pudo consultar ninguna fuente. El detalle muestra qué respondió cada una; es posible volver a intentarlo más tarde. ✓ | AC-3.4 |
| `ext.atajo_anio_en_curso` | Año en curso ✓ | RN-04 |
| `ext.atajo_anio_anterior` | Año anterior ✓ | RN-04 |

### Fechas y formularios

| Clave | Texto | Origen |
|-------|-------|--------|
| `fecha.abrir_calendario` | Abrir calendario † | AC-4.2 (nombre accesible) |
| `fecha.fin_anterior` | La fecha de finalización no puede ser anterior al {fecha} ✓ | AC-4.5 |
| `fecha.falta_fin` | Falta la fecha de finalización ✓ | FR-033 |
| `fecha.falta_inicio` | Falta la fecha de inicio † | FR-033 |
| `fecha.inexistente` | La fecha {fecha} no existe † | AC-4.5 (31/02, 29/02 en año no bisiesto) |
| `fecha.mes_anterior` | Mes anterior ‡ | AC-4.6 (botón del calendario, con teclado y lector de pantalla) |
| `fecha.mes_siguiente` | Mes siguiente ‡ | AC-4.6 (botón del calendario, con teclado y lector de pantalla) |
| `fecha.periodo` | Período ‡ | AC-4.3 (nombre del grupo de fechas y de su calendario) |
| `est.atajo_todo` | Todo el historial ✓ | RN-04 |
| `est.numero_ayuda` | Entre 00 y 45 ✓ | AC-7.3 |
| `est.consultar_numero` | Consultar un número ✓ | AC-7.4 |
| `form.no_avanza` | No se puede continuar: hay {n} campos con errores † | FR-033 (resumen al pulsar el botón) |
| `form.trabajando_registrar` | Registrando… † | FR-034 (mismo patrón que "Iniciando…" de AC-3.1) |
| `form.trabajando_guardar` | Guardando… † | FR-034 (mismo patrón que "Iniciando…" de AC-3.1) |
| `form.trabajando_eliminar` | Eliminando… † | FR-034 (mismo patrón que "Iniciando…" de AC-3.1) |
| `form.trabajando_publicar` | Publicando… † | FR-034 (mismo patrón que "Iniciando…" de AC-3.1) |
| `form.trabajando_consultar` | Consultando… † | FR-034 (mismo patrón que "Iniciando…" de AC-3.1) |
| `form.trabajando_crear_cuenta` | Creando la cuenta… † | FR-034 (mismo patrón que "Iniciando…" de AC-3.1) |

### Navegación, cuenta y tema

| Clave | Texto | Origen |
|-------|-------|--------|
| `nav.saltar` | Saltar al contenido ✓ | AC-5.5 |
| `nav.menu` | Menú ✓ | AC-5.4 |
| `nav.cuenta` | Cuenta de {correo} † | AC-5.3 (nombre accesible) |
| `nav.salir` | Salir ✓ | AC-5.3 |
| `nav.volver_sorteos` | ← Sorteos ✓ | AC-5.6 (detalle de un sorteo, público y de administración) |
| `nav.volver_extracciones` | ← Extracción histórica ✓ | AC-5.6 (detalle de una extracción) |
| `nav.volver_extraccion` | ← Extracción del {fecha_hora} † | AC-5.6 (detalle de un sorteo extraído) |
| `nav.volver_jugadas` | ← Mis jugadas † | AC-5.6 (detalle de una jugada) |
| `nav.logotipo` | QUINI_6, ir al inicio † | AC-5.7 (nombre accesible del logotipo) |
| `cuenta.mostrar` | Mostrar ✓ | AC-6.2 |
| `cuenta.ocultar` | Ocultar ✓ | AC-6.2 |
| `cuenta.contrasena_visible` | Contraseña visible † | AC-6.2 (anuncio) |
| `cuenta.contrasena_oculta` | Contraseña oculta † | AC-6.2 (anuncio) |
| `cuenta.ingresando` | Ingresando… ✓ | AC-6.6 |
| `cuenta.volver_formulario` | Volver al formulario ✓ | AC-14.4 |
| `cuenta.volver_formulario_texto` | Ingreso correcto. El formulario que se estaba completando se conserva para revisarlo y enviarlo. † | AC-14.4 |
| `gral.no_disponible` | El servicio no está disponible en este momento. Es posible volver a intentarlo en unos minutos. † | AC-14.6, FR-044 |
| `cuenta.sesion_vencida` | La sesión venció. Para continuar, es necesario ingresar de nuevo; lo escrito se conserva para revisarlo y enviarlo. † | FR-032 |
| `tema.titulo` | Tema † | AC-12.2 |
| `tema.claro` | Claro ✓ | AC-12.2 |
| `tema.oscuro` | Oscuro ✓ | AC-12.2 |
| `tema.dispositivo` | Según el dispositivo ✓ | AC-12.2 |
| `tema.guardar` | Guardar tema † | AC-12.2 (botón visible solo sin scripts) |

### Estructura común de ambas interfaces (Etapa 2, T162, T163)

Textos que las plantillas de Django ya mostraban escritos en la plantilla, sin clave. Pasan al catálogo **sin cambiar su redacción** para que Next.js muestre exactamente lo mismo (FR-041, AC-14.5); Django los toma de aquí desde el 22/11/2026.

| Clave | Texto | Origen |
|-------|-------|--------|
| `nav.principal` | Navegación principal | `templates/base.html` (nombre accesible de la navegación) |
| `nav.resultados` | Resultados | `templates/base.html` |
| `nav.estadisticas` | Estadísticas | `templates/base.html` |
| `nav.mis_jugadas` | Mis jugadas | `templates/base.html` |
| `nav.administracion` | Administración | `templates/base.html` |
| `nav.ingresar` | Ingresar | `templates/base.html` |
| `nav.crear_cuenta` | Crear cuenta | `templates/base.html` |
| `gral.titulo_pagina_inexistente` | Página inexistente | `templates/404.html` |
| `gral.titulo_acceso_restringido` | Acceso restringido | `templates/403.html` |
| `gral.titulo_sin_permisos` | Sin permisos | `templates/403.html` (título de la pestaña) |
| `gral.titulo_error` | Error | `templates/500.html` |
| `gral.volver_resultados` | Volver a los resultados | `templates/403.html`, `404.html`, `500.html` |
| `aviso.region` | Avisos ‡ | Nombre accesible de la región de Toasts de Next.js (Sonner exige uno; sin él anuncia "Notifications") |

### Estados vacíos (RN-06)

| Clave | Texto | Origen |
|-------|-------|--------|
| `vacio.jugadas.titulo` | Todavía no hay jugadas registradas ✓ | AC-8.2 |
| `vacio.jugadas.explicacion` | Cada jugada registrada muestra cuántos aciertos tuvo en cada sorteo ✓ | AC-8.2 |
| `vacio.jugadas.accion` | Registrar mi primera jugada ✓ | AC-8.2 |
| `vacio.resultados.titulo` | Todavía no hay resultados publicados ✓ | AC-8.4 (= `resultados.sin_publicar` de [001]) |
| `vacio.resultados.explicacion` | Los resultados aparecen aquí cuando se publica cada sorteo. † | AC-8.4 |
| `vacio.resultados.accion_cargar` | Cargar sorteo ✓ | AC-8.4 (solo administración) |
| `vacio.resultados.accion_extraccion` | Extracción histórica ✓ | AC-8.4 (solo administración) |
| `vacio.resultados_nota_admin` | La extracción histórica genera un archivo CSV; no carga sorteos en la aplicación ✓ | Supuestos (AC-8.4) |
| `vacio.extracciones.titulo` | Todavía no hay extracciones † | AC-8.1 |
| `vacio.extracciones.explicacion` | Cada extracción histórica genera un archivo CSV con los sorteos del período elegido. † | AC-8.1 |
| `vacio.estadisticas.explicacion` | Probar con otro período o con "Todo el historial". † | AC-8.1 (el título es `est.sin_sorteos` de [001]) |
| `vacio.filtro.titulo` | Sin resultados para el filtro ✓ | AC-8.3 |
| `vacio.filtro.explicacion` | Ningún elemento coincide con: {filtro} ✓ | AC-8.3 |
| `vacio.filtro.accion` | Limpiar filtros ✓ | AC-8.3 |

### Tablas, paginación y avisos

| Clave | Texto | Origen |
|-------|-------|--------|
| `tabla.orden_asc` | Orden ascendente † | AC-9.1 (anuncio) |
| `tabla.orden_desc` | Orden descendente † | AC-9.1 (anuncio) |
| `pag.pagina` | Página {n} de {m} ✓ | AC-9.2 |
| `pag.anterior` | Anterior ✓ | RN-07 |
| `pag.siguiente` | Siguiente ✓ | RN-07 |
| `aviso.cerrar` | Cerrar aviso † | RN-09 |
| `gral.sin_conexion` | No se pudo conectar. Es necesario comprobar la conexión y volver a intentarlo. ✓ | Casos límite, FR-031 |
| `gral.reintentar` | Reintentar ✓ | FR-031 |
| `pie.legal` | Información de consulta. QUINI_6 no vende apuestas ni realiza pagos. La fuente de cada resultado es el extracto oficial indicado. | AC-10.2 (texto sin cambios; ahora con contraste ≥ 4,5:1 y 14 px) |

### Rótulos de pantalla catalogados para Next.js (Etapa 2, T175 a T178)

Textos que las plantillas de Django de [002] tenían escritos directamente. Se catalogan **sin cambiar la redacción** para que Next.js los tome del catálogo único (Convenciones de tasks.md); no son textos nuevos.

| Clave | Texto | Origen |
|-------|-------|--------|
| `rot.acciones` | Acciones | `templates/extracciones/` ([002]) |
| `rot.calculado` | Calculado: {calculo} | `templates/extracciones/` ([002]) |
| `rot.caption_fuentes_sorteo` | Resultado de la consulta a cada fuente | `templates/extracciones/` ([002]) |
| `rot.caption_resumen` | Resumen de la extracción | `templates/extracciones/` ([002]) |
| `rot.caption_sorteos_extraccion` | Sorteos de la extracción con su estado | `templates/extracciones/` ([002]) |
| `rot.dato` | Dato | `templates/extracciones/` ([002]) |
| `rot.direccion_consultada` | Dirección consultada | `templates/extracciones/` ([002]) |
| `rot.ejecutada_por` | Ejecutada por | `templates/extracciones/` ([002]) |
| `rot.estado` | Estado | `templates/extracciones/` ([002]) |
| `rot.extraccion_del` | Extracción del {fecha_hora} | `templates/extracciones/` ([002]) |
| `rot.fecha_con_valor` | Fecha: {valor} | `templates/extracciones/` ([002]) |
| `rot.fecha_del_sorteo` | Fecha del sorteo | `templates/extracciones/` ([002]) |
| `rot.fecha_y_hora` | Fecha y hora | `templates/extracciones/` ([002]) |
| `rot.fuente` | Fuente | `templates/extracciones/` ([002]) |
| `rot.fuentes_consultadas` | Fuentes consultadas | `templates/extracciones/` ([002]) |
| `rot.fuentes_utilizadas` | Fuentes utilizadas | `templates/extracciones/` ([002]) |
| `rot.intentos_fallidos` | Intentos fallidos | `templates/extracciones/` ([002]) |
| `rot.no_recuperados` | No recuperados | `templates/extracciones/` ([002]) |
| `rot.numero_sorteo` | N.º {numero} | `templates/extracciones/` ([002]) |
| `rot.numeros` | Números | `templates/extracciones/` ([002]) |
| `rot.observaciones` | Observaciones | `templates/extracciones/` ([002]) |
| `rot.periodo` | Período | `templates/extracciones/` ([002]) |
| `rot.periodo_consultado` | Período consultado | `templates/extracciones/` ([002]) |
| `rot.periodo_consultado_valor` | Período consultado: {desde} al {hasta} | `templates/extracciones/` ([002]) |
| `rot.periodo_rango` | {desde} al {hasta} | `templates/extracciones/` ([002]) |
| `rot.recuperados` | Recuperados | `templates/extracciones/` ([002]) |
| `rot.recuperados_parcialmente` | Recuperados parcialmente | `templates/extracciones/` ([002]) |
| `rot.resultado` | Resultado | `templates/extracciones/` ([002]) |
| `rot.resumen` | Resumen | `templates/extracciones/` ([002]) |
| `rot.sorteo` | Sorteo | `templates/extracciones/` ([002]) |
| `rot.sorteo_numero` | Sorteo N.º {numero} | `templates/extracciones/` ([002]) |
| `rot.sorteos` | Sorteos | `templates/extracciones/` ([002]) |
| `rot.sorteos_a_revisar` | Sorteos que requieren revisión | `templates/extracciones/` ([002]) |
| `rot.sorteos_aportados` | Sorteos aportados | `templates/extracciones/` ([002]) |
| `rot.sorteos_identificados` | Sorteos identificados | `templates/extracciones/` ([002]) |
| `rot.valor` | Valor | `templates/extracciones/` ([002]) |
| `rot.ver_en_curso` | Ver la extracción en curso | `templates/extracciones/` ([002]) |
| `rot.est_titulo` | Estadísticas de frecuencia | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.modalidad` | Modalidad | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.desde` | Desde | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.hasta` | Hasta | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.numero` | Número | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.consultar` | Consultar | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.frecuencia` | Frecuencia | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.porcentaje` | Porcentaje | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_considerados_uno` | {n} sorteo considerado, del {desde} al {hasta}. | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_considerados` | {n} sorteos considerados, del {desde} al {hasta}. | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_numero_consultado` | El {numero} salió en {frecuencia} de {total} sorteos considerados ({porcentaje}). | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_caption` | Apariciones de cada número en {modalidad} | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_grafico_titulo` | Frecuencia de cada número en {modalidad} | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_grafico_desc_uno` | Gráfico de barras con las apariciones de cada número de 00 a 45 en {n} sorteo considerado | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_grafico_desc` | Gráfico de barras con las apariciones de cada número de 00 a 45 en {n} sorteos considerados | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_grafico_resaltado` | ; el {numero} aparece resaltado | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_barra` | {numero}: {frecuencia} apariciones | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.est_grafico_pie` | Alto de cada barra proporcional a su cantidad de apariciones. La tabla siguiente tiene los mismos datos. | `templates/estadisticas/` ([001], [003] HU-07) |
| `rot.res_titulo` | Resultados del Quini 6 | `templates/resultados/` ([001]) |
| `rot.res_sorteo_del` | Sorteo N.º {numero} — sorteo del {fecha} | `templates/resultados/` ([001]) |
| `rot.res_pendientes` | Resultados pendientes | `templates/resultados/` ([001]) |
| `rot.ver_sorteo` | Ver el sorteo | `templates/resultados/` ([001]) |
| `rot.res_ultimos` | Últimos resultados: Sorteo N.º {numero} — sorteo del {fecha} | `templates/resultados/` ([001]) |
| `rot.res_estado_sorteo` | Estado del sorteo: | `templates/resultados/` ([001]) |
| `rot.res_numeros_distintos` | {n} números distintos | `templates/resultados/` ([001]) |
| `rot.numeros_ganadores` | Números ganadores | `templates/resultados/` ([001]) |
| `rot.en_revision` | Información en revisión | `templates/resultados/` ([001]) |
| `rot.ver_premios` | Ver premios y detalle | `templates/resultados/` ([001]) |
| `rot.todos_los_sorteos` | Todos los sorteos | `templates/resultados/` ([001]) |
| `rot.caption_sorteos` | Sorteos, del más reciente al más antiguo | `templates/resultados/` ([001]) |
| `rot.buscar_sorteo` | Buscar un sorteo | `templates/resultados/` ([001]) |
| `rot.buscar_por_numero` | Buscar por número de sorteo | `templates/resultados/` ([001]) |
| `rot.numero_de_sorteo` | Número de sorteo | `templates/resultados/` ([001]) |
| `rot.buscar` | Buscar | `templates/resultados/` ([001]) |
| `rot.buscar_por_fecha` | Buscar por fecha del sorteo | `templates/resultados/` ([001]) |
| `rot.buscar_sorteos` | Buscar sorteos | `templates/resultados/` ([001]) |
| `rot.sorteos_del` | Sorteos del {fecha} | `templates/resultados/` ([001]) |
| `rot.sorteo_del` | Sorteo del {fecha} | `templates/resultados/` ([001]) |
| `rot.registrar_jugada` | Registrar una jugada | `templates/resultados/` ([001]) |
| `rot.sin_modalidades` | Este sorteo no tiene modalidades aplicables. | `templates/resultados/` ([001]) |
| `rot.conjunto_premio_extra` | Conjunto de números del Premio Extra | `templates/resultados/` ([001]) |
| `rot.conjunto_explicacion` | {n} números distintos, reunidos de Tradicional – Primer Sorteo, Tradicional – La Segunda y Revancha. | `templates/resultados/` ([001]) |
| `rot.corregido_el` | Corregido el {fecha} | `templates/resultados/` ([001]) |
| `rot.fuente_consultada` | Fuente: {fuente}, consultada el {fecha} | `templates/resultados/` ([001]) |
| `rot.fuente_sola` | Fuente: {fuente} | `templates/resultados/` ([001]) |
| `rot.fuente_premios_consultada` | Fuente de los premios: {fuente}, consultada el {fecha} | `templates/resultados/` ([001]) |
| `rot.fuente_premios_sola` | Fuente de los premios: {fuente} | `templates/resultados/` ([001]) |
| `rot.premios` | Premios | `templates/resultados/` ([001]) |
| `rot.aciertos_condicion` | Aciertos o condición | `templates/resultados/` ([001]) |
| `rot.ganadores` | Ganadores | `templates/resultados/` ([001]) |
| `rot.un_ganador` | 1 ganador | `templates/resultados/` ([001]) |
| `rot.n_ganadores` | {n} ganadores | `templates/resultados/` ([001]) |
| `rot.no_disponible` | No disponible | `templates/resultados/` ([001]) |
| `rot.importe_categoria` | Importe destinado a la categoría | `templates/resultados/` ([001]) |
| `rot.importe_individual` | Importe individual por ganador | `templates/resultados/` ([001]) |
| `rot.premios_pendientes` | Información de premios pendiente de publicación | `templates/resultados/` ([001]) |
| `rot.pozo_vacante` | Pozo vacante o acumulado | `templates/resultados/` ([001]) |
| `rot.numeros_bolillas` | Números | `templates/resultados/` ([001]) |
| `rot.mis_jugadas` | Mis jugadas | `templates/jugadas/` ([001]) |
| `rot.caption_jugadas` | Mis jugadas, de la más reciente a la más antigua | `templates/jugadas/` ([001]) |
| `rot.numeros_jugada` | Números de la jugada | `templates/jugadas/` ([001]) |
| `rot.participa_en` | Participa en: {modalidades} | `templates/jugadas/` ([001]) |
| `rot.participa_en_rotulo` | Participa en | `templates/jugadas/` ([001]) |
| `rot.aciertos` | Aciertos | `templates/jugadas/` ([001]) |
| `rot.costo` | Costo | `templates/jugadas/` ([001]) |
| `rot.editar_jugada` | Editar jugada | `templates/jugadas/` ([001]) |
| `rot.guardar_igual` | Guardar igual | `templates/jugadas/` ([001]) |
| `rot.cancelar` | Cancelar | `templates/jugadas/` ([001]) |
| `rot.participara_en` | Participará en: {modalidades} | `templates/jugadas/` ([001]) |
| `rot.seis_elegidos` | Seis números elegidos | `templates/jugadas/` ([001]) |
| `rot.agregar` | Agregar | `templates/jugadas/` ([001]) |
| `rot.costo_jugada` | Costo de la jugada (en pesos) | `templates/jugadas/` ([001]) |
| `rot.costo_ayuda` | Por ejemplo, 1500,50 | `templates/jugadas/` ([001]) |
| `rot.guardar_cambios` | Guardar cambios | `templates/jugadas/` ([001]) |
| `rot.registrar_jugada_boton` | Registrar jugada | `templates/jugadas/` ([001]) |
| `rot.jugada_del_sorteo` | Jugada del sorteo N.º {numero} | `templates/jugadas/` ([001]) |
| `rot.editar` | Editar | `templates/jugadas/` ([001]) |
| `rot.estado_dos_puntos` | Estado: | `templates/jugadas/` ([001]) |
| `rot.comparacion_titulo` | Comparación con los resultados oficiales | `templates/jugadas/` ([001]) |
| `rot.eliminar_jugada` | Eliminar jugada | `templates/jugadas/` ([001]) |
| `rot.jugada_resumen` | Sorteo N.º {numero} — sorteo del {fecha} · {costo} | `templates/jugadas/` ([001]) |
| `rot.jugada_no_disponible` | Jugada no disponible | `templates/jugadas/` ([001]) |
| `rot.volver_mis_jugadas` | Volver a mis jugadas | `templates/jugadas/` ([001]) |
| `rot.publicado_en_revision` | Publicado · Información en revisión | `templates/jugadas/` ([001]) |
| `rot.resultado_publicado` | Resultado publicado | `templates/jugadas/` ([001]) |
| `rot.acertado` | (acertado) | `templates/jugadas/` ([001]) |
| `rot.numeros_oficiales` | Números oficiales: {numeros} | `templates/jugadas/` ([001]) |
| `rot.n_aciertos` | {n} aciertos | `templates/jugadas/` ([001]) |
| `rot.n_aciertos_conjunto` | {n} aciertos en el conjunto | `templates/jugadas/` ([001]) |
| `rot.elegibilidad` | Elegibilidad: | `templates/jugadas/` ([001]) |
| `rot.importe` | Importe: | `templates/jugadas/` ([001]) |
| `rot.opcion_sorteo` | Sorteo N.º {numero} — {fecha} | `templates/jugadas/` ([001]) |
| `rot.ingresar` | Ingresar | `templates/cuentas/` ([001], [003] HU-06) |
| `rot.crear_cuenta` | Crear cuenta | `templates/cuentas/` ([001], [003] HU-06) |
| `rot.crear_cuenta_intro` | Solo se pide un correo electrónico y una contraseña. | `templates/cuentas/` ([001], [003] HU-06) |
| `rot.correo` | Correo electrónico | `templates/cuentas/` ([001], [003] HU-06) |
| `rot.contrasena` | Contraseña | `templates/cuentas/` ([001], [003] HU-06) |
| `rot.contrasena_ayuda` | Al menos 8 caracteres. | `templates/cuentas/` ([001], [003] HU-06) |
| `rot.adm_sorteos` | Sorteos | `templates/resultados/admin/` ([001]) |
| `rot.adm_extraccion` | Extracción histórica de sorteos | `templates/resultados/admin/` ([001]) |
| `rot.adm_caption` | Sorteos cargados, del más reciente al más antiguo | `templates/resultados/admin/` ([001]) |
| `rot.adm_numeros_estado` | Números {numeros} · Premios {premios} | `templates/resultados/admin/` ([001]) |
| `rot.adm_premios_estado` | Premios {premios} | `templates/resultados/admin/` ([001]) |
| `rot.adm_modificar_sorteo` | Modificar sorteo | `templates/resultados/admin/` ([001]) |
| `rot.adm_ver_historial` | Ver historial | `templates/resultados/admin/` ([001]) |
| `rot.adm_ver_publica` | Ver página pública | `templates/resultados/admin/` ([001]) |
| `rot.adm_resumen` | Sorteo del {fecha} · Completitud: {completitud} · {jugadas} | `templates/resultados/admin/` ([001]) |
| `rot.adm_admite_jugadas` | Admite jugadas | `templates/resultados/admin/` ([001]) |
| `rot.adm_no_admite_jugadas` | Ya no admite jugadas | `templates/resultados/admin/` ([001]) |
| `rot.adm_premio_extra_explicacion` | Premio Extra no tiene números propios: su conjunto surge de Primer Sorteo, La Segunda y Revancha. | `templates/resultados/admin/` ([001]) |
| `rot.adm_bloque_estado` | {bloque}: {estado} | `templates/resultados/admin/` ([001]) |
| `rot.adm_publicado_el` | Publicado el {fecha_hora} | `templates/resultados/admin/` ([001]) |
| `rot.adm_publicado_el_fuente` | Publicado el {fecha_hora} · Fuente: {fuente} | `templates/resultados/admin/` ([001]) |
| `rot.adm_numeros_publicados` | Números publicados | `templates/resultados/admin/` ([001]) |
| `rot.adm_en_revision_motivo` | En revisión: {motivo} | `templates/resultados/admin/` ([001]) |
| `rot.adm_correccion_preparacion` | Corrección en preparación | `templates/resultados/admin/` ([001]) |
| `rot.adm_actualizado` | {estado} — actualizado el {fecha_hora}. | `templates/resultados/admin/` ([001]) |
| `rot.adm_numeros_preparacion` | Números en preparación | `templates/resultados/admin/` ([001]) |
| `rot.adm_observado_motivo` | Observado: {motivo} | `templates/resultados/admin/` ([001]) |
| `rot.adm_cargar` | Cargar | `templates/resultados/admin/` ([001]) |
| `rot.adm_publicar_correccion` | Publicar corrección | `templates/resultados/admin/` ([001]) |
| `rot.adm_revisar_publicar` | Revisar y publicar | `templates/resultados/admin/` ([001]) |
| `rot.adm_resolver` | Resolver observación | `templates/resultados/admin/` ([001]) |
| `rot.adm_marcar_observado` | Marcar como Observado | `templates/resultados/admin/` ([001]) |
| `rot.adm_motivo_observacion` | Motivo de la observación | `templates/resultados/admin/` ([001]) |
| `rot.adm_observar` | Observar | `templates/resultados/admin/` ([001]) |
| `rot.adm_marcar_revision` | Marcar en revisión | `templates/resultados/admin/` ([001]) |
| `rot.adm_motivo_revision` | Motivo de la revisión | `templates/resultados/admin/` ([001]) |
| `rot.adm_quitar_revision` | Quitar revisión | `templates/resultados/admin/` ([001]) |
| `rot.adm_motivo_quitar` | Motivo para quitar la revisión | `templates/resultados/admin/` ([001]) |
| `rot.adm_corregir` | Corregir | `templates/resultados/admin/` ([001]) |
| `rot.adm_motivo_correccion` | Motivo de la corrección | `templates/resultados/admin/` ([001]) |
| `rot.adm_iniciar_correccion` | Iniciar corrección | `templates/resultados/admin/` ([001]) |
| `rot.adm_fuente_correccion` | Fuente de la corrección (descripción) | `templates/resultados/admin/` ([001]) |
| `rot.adm_fecha_fuente` | Fecha de consulta de la fuente | `templates/resultados/admin/` ([001]) |
| `rot.adm_sin_modalidades` | El sorteo no tiene modalidades aplicables. | `templates/resultados/admin/` ([001]) |
| `rot.adm_modificar_titulo` | Modificar el sorteo N.º {numero} | `templates/resultados/admin/` ([001]) |
| `rot.adm_duplicado` | El sorteo N.º {numero} ya existe. | `templates/resultados/admin/` ([001]) |
| `rot.adm_ir_existente` | Ir al sorteo existente | `templates/resultados/admin/` ([001]) |
| `rot.adm_modalidades_aplicables` | Modalidades aplicables | `templates/resultados/admin/` ([001]) |
| `rot.adm_premio_extra_requiere` | Premio Extra requiere Primer Sorteo, La Segunda y Revancha. | `templates/resultados/admin/` ([001]) |
| `rot.adm_numeros_de` | Números de {modalidad} | `templates/resultados/admin/` ([001]) |
| `rot.adm_premios_de` | Premios de {modalidad} | `templates/resultados/admin/` ([001]) |
| `rot.adm_correccion_explicacion` | El público sigue viendo los valores publicados hasta que publiques la corrección. | `templates/resultados/admin/` ([001]) |
| `rot.adm_borrador_explicacion` | Lo que guardes queda en Borrador y no es visible para el público. | `templates/resultados/admin/` ([001]) |
| `rot.adm_seis_numeros` | Seis números distintos de 00 a 45 | `templates/resultados/admin/` ([001]) |
| `rot.adm_guardar_borrador` | Guardar borrador | `templates/resultados/admin/` ([001]) |
| `rot.adm_premios_explicacion` | Las categorías son fijas. Dejá vacío un dato para registrarlo como no disponible. Importes con coma decimal (por ejemplo, 1.500,50). | `templates/resultados/admin/` ([001]) |
| `rot.adm_caption_premios` | Datos por categoría (vacío = no disponible) | `templates/resultados/admin/` ([001]) |
| `rot.adm_categoria` | Categoría | `templates/resultados/admin/` ([001]) |
| `rot.adm_publicar` | Publicar | `templates/resultados/admin/` ([001]) |
| `rot.adm_publicar_titulo` | {accion}: {bloque} de {modalidad} | `templates/resultados/admin/` ([001]) |
| `rot.adm_no_se_publico` | No se publicó la información: | `templates/resultados/admin/` ([001]) |
| `rot.adm_info_publicar` | Información a publicar | `templates/resultados/admin/` ([001]) |
| `rot.adm_categoria_ganadora_sin` | Categoría ganadora: Sin ganadores | `templates/resultados/admin/` ([001]) |
| `rot.adm_categoria_ganadora` | Categoría ganadora: {n} aciertos | `templates/resultados/admin/` ([001]) |
| `rot.adm_importe_destinado` | Importe destinado | `templates/resultados/admin/` ([001]) |
| `rot.adm_importe_individual` | Importe individual | `templates/resultados/admin/` ([001]) |
| `rot.adm_no_disponible` | no disponible | `templates/resultados/admin/` ([001]) |
| `rot.adm_fuente_publicar` | Fuente: {fuente} | `templates/resultados/admin/` ([001]) |
| `rot.adm_sin_registrar` | sin registrar | `templates/resultados/admin/` ([001]) |
| `rot.adm_fuente_consultada` | Fuente: {fuente}, consultada el {fecha} | `templates/resultados/admin/` ([001]) |
| `rot.adm_motivo_correccion_valor` | Motivo de la corrección: {motivo} | `templates/resultados/admin/` ([001]) |
| `rot.adm_errores_publicar` | Errores que impiden publicar | `templates/resultados/admin/` ([001]) |
| `rot.adm_sin_bloqueantes` | No hay errores bloqueantes. | `templates/resultados/admin/` ([001]) |
| `rot.adm_advertencias` | Advertencias | `templates/resultados/admin/` ([001]) |
| `rot.adm_historial_titulo` | Historial de cambios del sorteo N.º {numero} | `templates/resultados/admin/` ([001]) |
| `rot.adm_historial_caption` | Cambios, del más reciente al más antiguo | `templates/resultados/admin/` ([001]) |
| `rot.adm_accion` | Acción | `templates/resultados/admin/` ([001]) |
| `rot.adm_modalidad_bloque` | Modalidad y bloque | `templates/resultados/admin/` ([001]) |
| `rot.adm_valor_anterior` | Valor anterior | `templates/resultados/admin/` ([001]) |
| `rot.adm_valor_nuevo` | Valor nuevo | `templates/resultados/admin/` ([001]) |
| `rot.adm_autor` | Autor | `templates/resultados/admin/` ([001]) |
| `rot.adm_motivo` | Motivo | `templates/resultados/admin/` ([001]) |
| `rot.adm_sin_cambios` | Todavía no hay cambios registrados. | `templates/resultados/admin/` ([001]) |

### API v1 (Problem Details, [003] R-16)

Textos de `title` y `detail` de las respuestas de error de `/api/v1/` ([api.md](api.md) § 1). Next.js los puede mostrar tal cual.

| Clave | Texto | Origen |
|-------|-------|--------|
| `api.titulo_validacion` | Datos inválidos † | api.md § 3 |
| `api.detalle_validacion` | Hay campos con errores. † | api.md § 3 |
| `api.dato_invalido` | El dato no es válido ‡ | R-16 (error de tipo o formato que no tiene un mensaje propio del dominio) |
| `api.titulo_sin_sesion` | Sin sesión ‡ | R-16 (401) |
| `api.detalle_sin_sesion` | Es necesario ingresar para continuar. ‡ | R-16 (401) |
| `api.titulo_sin_permiso` | Sin permisos ‡ | R-16 (403; el detalle es `admin.sin_permiso`) |
| `api.titulo_csrf` | Formulario vencido ‡ | R-16 (403 por CSRF; el detalle es `gral.csrf_vencido`) |
| `api.titulo_no_encontrado` | No encontrado ‡ | R-16 (404) |
| `api.detalle_no_encontrado` | El recurso buscado no existe. ‡ | R-16 (404) |
| `api.titulo_conflicto` | Conflicto ‡ | R-16 (409) |

## 5. Nombres de columnas (RN-05)

| Dato | Nombre único | Pantallas |
|------|--------------|-----------|
| Fecha y hora de inicio de una extracción | Fecha | Extracción histórica ([002] D-24) |
| Período de una extracción | Período | Extracción histórica |
| Etiqueta de estado | Estado | Extracción histórica |
| Fecha de un sorteo | Fecha del sorteo | Resultados, Mis jugadas, Administración, detalle de extracción |
| Número de un sorteo | Sorteo | Resultados, Mis jugadas, Administración, detalle de extracción |
| Modalidad | Modalidad | Todas |
| Frecuencia de un número | Frecuencia | Estadísticas |
| Porcentaje | Porcentaje | Estadísticas |
| Aciertos de una jugada | Aciertos | Mis jugadas |
