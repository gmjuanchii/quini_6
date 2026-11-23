"""Catálogo único de textos visibles de QUINI_6 ([003] R-13, HU-11).

Todo texto visible sale de aquí por su clave: plantillas con ``{% msg "clave" %}``, Python con
``mensaje("clave", **valores)`` y Next.js con ``contratos/mensajes.json`` (``exportar_contratos``).
Las claves y los textos son los de specs/003-modernizacion-ui-ux/contracts/mensajes.md y, para lo
que [003] no reescribe, los catálogos de [001] y [002]; tests/unit/test_mensajes_catalogo.py
verifica que coincidan. Sin dependencias de Django (módulo puro del dominio).
"""

from __future__ import annotations

MENSAJES: dict[str, str] = {
    # admin
    "admin.ayuda_modalidades": (
        "Las modalidades se pueden agregar en cualquier momento. Solo se puede quitar una "
        "modalidad sin información cargada, y la fecha se puede cambiar mientras no haya "
        "números sorteados publicados."
    ),
    "admin.bloque_publicado": (
        "Este bloque ya está publicado. Para modificarlo, es necesario iniciar una corrección."
    ),
    "admin.concurso_duplicado": "El sorteo N.º {N} ya existe",
    "admin.confirmar_cotejo": "Confirmo que cotejé esta información con la fuente oficial",
    "admin.corregir_bloqueantes": "Hay errores bloqueantes que corregir antes de publicar.",
    "admin.crear": "Cargar sorteo",
    "admin.falta_modalidad": "Falta elegir al menos una modalidad",
    "admin.falta_numero_sorteo": "Falta el número de sorteo",
    "admin.fecha_futura": (
        "La fecha del sorteo es posterior a hoy: es necesario verificar que el sorteo ya "
        "se realizó."
    ),
    "admin.ganadores_invalidos": "La cantidad de ganadores debe ser 0 o más",
    "admin.modalidades_invalidas": "Hay modalidades no válidas",
    "admin.numero_repetido": "El {nn} está repetido en los números sorteados",
    "admin.numero_sorteo_invalido": "El número de sorteo no es válido",
    "admin.numeros_rango": "Los números deben estar entre 00 y 45",
    "admin.premio_extra_requiere": "Premio Extra requiere Primer Sorteo, La Segunda y Revancha",
    "admin.sin_concursos": "Todavía no hay sorteos cargados",
    "admin.sin_ganadores_y_categoria": (
        'Se indicó "sin ganadores" y también una categoría ganadora: corresponde elegir '
        "una sola opción."
    ),
    "admin.sin_permiso": "Sin permisos para acceder a esta sección",
    "admin.titulo_listado": "Administración de sorteos",
    "admin.volver_listado": "← Sorteos",
    # api
    "api.dato_invalido": "El dato no es válido",
    "api.detalle_no_encontrado": "El recurso buscado no existe.",
    "api.detalle_sin_sesion": "Es necesario ingresar para continuar.",
    "api.detalle_validacion": "Hay campos con errores.",
    "api.titulo_conflicto": "Conflicto",
    "api.titulo_csrf": "Formulario vencido",
    "api.titulo_no_encontrado": "No encontrado",
    "api.titulo_sin_permiso": "Sin permisos",
    "api.titulo_sin_sesion": "Sin sesión",
    "api.titulo_validacion": "Datos inválidos",
    # aviso
    "aviso.cerrar": "Cerrar aviso",
    "aviso.region": "Avisos",
    "aviso.corregido": "Corregido el {fecha}",
    "aviso.en_revision": "Información en revisión",
    # calculo
    "calculo.pozo": "importe individual × ganadores",
    "calculo.pozo_extra": "unión de Tradicional, La Segunda y Revancha",
    "calculo.vacante": "sin ganadores",
    # comp
    "comp.aciertos_sin_premio": "{n} aciertos — Sin premio",
    "comp.aciertos_superan": (
        "Los aciertos de la jugada superan la categoría ganadora publicada. Es necesario "
        "verificar los números y el sorteo de la jugada."
    ),
    "comp.actualizado": "Actualizado por corrección del resultado oficial el {fecha}",
    "comp.con_premio": "Con premio — {categoría}",
    "comp.en_revision": "Información en revisión: el resultado podría cambiar",
    "comp.excluida": "Excluida del Premio Extra: obtuvo 6 aciertos en {sorteo}",
    "comp.numeros_resaltados": (
        "Conjunto de números del Premio Extra: {n} números distintos. Los números de la "
        "jugada están resaltados."
    ),
    "comp.participa": "Participa",
    "comp.pendiente_determinacion": "Premio pendiente de determinación",
    "comp.tu_jugada": "Números de la jugada (los acertados están resaltados):",
    # concurso
    "concurso.completo": "Completo",
    "concurso.incompleto": "Incompleto",
    # cuenta
    "cuenta.bloqueada": (
        "Por seguridad, el acceso quedó bloqueado por 15 minutos. Es posible volver a "
        "intentarlo a las {hora}."
    ),
    "cuenta.contrasena_corta": "La contraseña debe tener al menos 8 caracteres.",
    "cuenta.contrasena_oculta": "Contraseña oculta",
    "cuenta.contrasena_visible": "Contraseña visible",
    "cuenta.correo_existente": "Ya existe una cuenta con este correo electrónico.",
    "cuenta.correo_invalido": "El correo electrónico no tiene un formato válido",
    "cuenta.credenciales_incorrectas": "Correo electrónico o contraseña incorrectos",
    "cuenta.falta_contrasena": "Falta la contraseña",
    "cuenta.falta_correo": "Falta el correo electrónico",
    "cuenta.ingresando": "Ingresando…",
    "cuenta.ir_a_ingreso": "¿Ya hay una cuenta? Ingresar",
    "cuenta.ir_a_registro": "¿Todavía sin cuenta? Crear cuenta",
    "cuenta.mostrar": "Mostrar",
    "cuenta.ocultar": "Ocultar",
    "cuenta.sesion_vencida": (
        "La sesión venció. Para continuar, es necesario ingresar de nuevo; lo escrito se "
        "conserva para revisarlo y enviarlo."
    ),
    "cuenta.volver_formulario": "Volver al formulario",
    "cuenta.volver_formulario_texto": (
        "Ingreso correcto. El formulario que se estaba completando se conserva para "
        "revisarlo y enviarlo."
    ),
    # dato
    "dato.calculado": "Calculado: {cálculo}",
    "dato.no_corresponde": "No corresponde",
    "dato.no_disponible": "No disponible",
    "dato.sin_corroborar": "Sin corroborar",
    "dato.sin_determinar": "Sin determinar",
    # disc
    "disc.centavos": "Diferencia de centavos o redondeo (menor al 1 %)",
    "disc.mayoria": "Resuelto por coincidencia de 2 de 3 fuentes",
    "disc.omision": "Omisión",
    "disc.valor": "Valor distinto",
    # est
    "est.atajo_todo": "Todo el historial",
    "est.ayuda_periodo": "Sin período, se consideran todos los sorteos publicados de la modalidad.",
    "est.consultar_numero": "Consultar un número",
    "est.huecos": "El período incluye {n} sorteos sin información disponible para esta modalidad",
    "est.leyenda": "Estadística descriptiva de sorteos pasados. No predice resultados futuros.",
    "est.numero_ayuda": "Entre 00 y 45",
    "est.periodo_invalido": "La fecha «Desde» no puede ser posterior a la fecha «Hasta»",
    "est.sin_sorteos": "No hay sorteos publicados de {modalidad} en el período seleccionado",
    # etiqueta
    "etiqueta.con_advertencias": "Con advertencias",
    "etiqueta.con_advertencias.explicacion": (
        "Hay sorteos del período que requieren revisión manual. El detalle los muestra."
    ),
    "etiqueta.con_error": "Con error",
    "etiqueta.con_error.explicacion": (
        "Hay sorteos del período que no se pudieron recuperar. El detalle muestra cuáles "
        "y qué respondió cada fuente."
    ),
    "etiqueta.en_curso": "En curso",
    "etiqueta.en_curso.explicacion": (
        "La extracción se está procesando. El avance se actualiza en esta pantalla."
    ),
    "etiqueta.finalizada": "Finalizada",
    "etiqueta.finalizada.explicacion": (
        "Todos los sorteos del período se recuperaron sin novedades."
    ),
    "etiqueta.sin_sorteos": "Sin sorteos",
    "etiqueta.sin_sorteos.explicacion": (
        "Las fuentes no informaron sorteos en el período consultado."
    ),
    # ext
    "ext.acciones": "Acciones de la extracción del {fecha_hora}",
    "ext.anteriores": "Extracciones anteriores",
    "ext.atajo_anio_anterior": "Año anterior",
    "ext.atajo_anio_en_curso": "Año en curso",
    "ext.avance": "{n} de {m} sorteos procesados",
    "ext.boton_descargar": "Descargar CSV",
    "ext.boton_iniciar": "Iniciar extracción",
    "ext.boton_iniciar_trabajando": "Iniciando…",
    "ext.campo_fin": "Fecha de finalización",
    "ext.campo_inicio": "Fecha de inicio",
    "ext.cancelar": "Cancelar",
    "ext.col_fecha": "Fecha",
    "ext.con_advertencias": "Extracción finalizada con advertencias que requieren revisión",
    "ext.eliminada": "Se eliminó la extracción del {fecha_hora}",
    "ext.eliminar": "Eliminar",
    "ext.eliminar_confirmar": (
        "¿Eliminar la extracción del {fecha_hora} ({desde} al {hasta})? Esta acción no se "
        "puede deshacer."
    ),
    "ext.eliminar_consecuencias": (
        "Se pierden su resumen, el detalle de sus sorteos y su archivo CSV."
    ),
    "ext.eliminar_en_curso": "No se puede eliminar una extracción en curso",
    "ext.eliminar_titulo": "Eliminar extracción",
    "ext.en_curso": "Extracción en curso",
    "ext.fecha_invalida": "La fecha no es válida. Formato: dd/mm/aaaa",
    "ext.filtro_aplicado": "Filtro aplicado: {filtro}",
    "ext.filtro_estado": "Estado",
    "ext.filtro_todos": "Todos los estados",
    "ext.filtrar": "Filtrar",
    "ext.fin_futura": "La fecha de finalización no puede ser posterior a hoy",
    "ext.finalizada": "Extracción finalizada",
    "ext.huecos": "Hay números de sorteo que ninguna fuente informa: {lista}",
    "ext.identificando": "Identificando los sorteos del período…",
    "ext.inicio_posterior": "La fecha de inicio no puede ser posterior a la fecha de finalización",
    "ext.ninguna_fuente": (
        "No se pudo consultar ninguna fuente. El detalle muestra qué respondió cada una; "
        "es posible volver a intentarlo más tarde."
    ),
    "ext.no_existe": "La extracción ya no existe",
    "ext.requiere_revision": "Requiere revisión",
    "ext.periodo_en_curso": "Ya hay una extracción en curso para el período del {desde} al {hasta}",
    "ext.periodo_largo": "El período no puede superar los 12 meses",
    "ext.requiere_mantenimiento": "Requiere mantenimiento",
    "ext.sin_cobertura": "Las fuentes no cubren el período anterior al {fecha}",
    "ext.sin_sorteos": "No se identificaron sorteos en el período consultado",
    "ext.termino_advertencias": (
        "La extracción terminó con advertencias: {n} sorteos requieren revisión"
    ),
    "ext.termino_error": "La extracción terminó con error: {n} sorteos no se pudieron recuperar",
    "ext.termino_finalizada": "La extracción terminó sin novedades",
    "ext.termino_sin_sorteos": (
        "La extracción terminó: las fuentes no informaron sorteos en el período"
    ),
    "ext.titulo": "Extracción histórica de sorteos",
    "ext.ver_detalle": "Ver detalle →",
    "ext.ver_existente": "Ver esa extracción",
    # fecha
    "fecha.abrir_calendario": "Abrir calendario",
    "fecha.falta_fin": "Falta la fecha de finalización",
    "fecha.falta_inicio": "Falta la fecha de inicio",
    "fecha.fin_anterior": "La fecha de finalización no puede ser anterior al {fecha}",
    "fecha.inexistente": "La fecha {fecha} no existe",
    "fecha.mes_anterior": "Mes anterior",
    "fecha.mes_siguiente": "Mes siguiente",
    "fecha.periodo": "Período",
    # form
    "form.no_avanza": "No se puede continuar: hay {n} campos con errores",
    "form.trabajando_consultar": "Consultando…",
    "form.trabajando_crear_cuenta": "Creando la cuenta…",
    "form.trabajando_eliminar": "Eliminando…",
    "form.trabajando_guardar": "Guardando…",
    "form.trabajando_publicar": "Publicando…",
    "form.trabajando_registrar": "Registrando…",
    # gral
    "gral.cargando": "Cargando…",
    "gral.csrf_vencido": (
        "No se pudo procesar el formulario porque venció. Es necesario volver a cargar la "
        "página e intentarlo de nuevo."
    ),
    "gral.error": "Ocurrió un error. Es posible volver a intentarlo en unos minutos.",
    "gral.fecha_invalida": "La fecha no es válida. Formato: dd/mm/aaaa",
    "gral.no_disponible": (
        "El servicio no está disponible en este momento. Es posible volver a intentarlo "
        "en unos minutos."
    ),
    "gral.titulo_acceso_restringido": "Acceso restringido",
    "gral.titulo_error": "Error",
    "gral.titulo_pagina_inexistente": "Página inexistente",
    "gral.titulo_sin_permisos": "Sin permisos",
    "gral.volver_resultados": "Volver a los resultados",
    "gral.pagina_inexistente": "La página buscada no existe",
    "gral.reintentar": "Reintentar",
    "gral.sin_conexion": (
        "No se pudo conectar. Es necesario comprobar la conexión y volver a intentarlo."
    ),
    # intento
    "intento.estructura": "Estructura no reconocida",
    "intento.fuera_cobertura": "Fuera de cobertura",
    "intento.incompleto": "Incompleto",
    "intento.no_disp_o_no_enc": "No disponible o no encontrado",
    "intento.no_disponible": "No disponible",
    "intento.no_encontrado": "No encontrado",
    "intento.no_requerida": "No requerida",
    "intento.obtenido": "Obtenido",
    # jugada
    "jugada.actualizada": "Jugada actualizada",
    "jugada.ayuda_modalidades": (
        "Al elegir el sorteo se muestran las modalidades en las que participa la jugada."
    ),
    "jugada.campo_sorteo": "Sorteo",
    "jugada.concurso_cerrado": (
        "Ya no se pueden registrar jugadas para este sorteo porque sus resultados fueron publicados"
    ),
    "jugada.concurso_no_disponible": (
        "Este sorteo todavía no está disponible para registrar jugadas"
    ),
    "jugada.confirmar_eliminacion": "¿Eliminar esta jugada? Esta acción no se puede deshacer.",
    "jugada.costo_invalido": (
        "El importe debe ser mayor o igual a cero y tener hasta dos decimales (por "
        "ejemplo, 1500,50)"
    ),
    "jugada.costo_vacio": "Falta el costo de la jugada",
    "jugada.duplicada": (
        "Ya hay una jugada registrada con estos números para este sorteo. ¿Guardarla igual?"
    ),
    "jugada.elegi_concurso": "Falta el sorteo de la jugada",
    "jugada.elegir_numeros": "Seis números (00 a 45)",
    "jugada.eliminada": "Jugada eliminada",
    "jugada.escribir_numero": "Número",
    "jugada.exactamente_seis": "La jugada admite exactamente seis números",
    "jugada.faltan": "Faltan {n} números",
    "jugada.fija": (
        "Esta jugada no se puede modificar ni eliminar porque los resultados de su sorteo "
        "ya fueron publicados"
    ),
    "jugada.fuera_de_rango": "El número debe estar entre 00 y 45",
    "jugada.historial_vacio": "Todavía no hay jugadas registradas",
    "jugada.importe_formato": "El importe debe tener hasta dos decimales (por ejemplo, 1500,50)",
    "jugada.intro": (
        "Registro de una jugada hecha fuera de la aplicación. QUINI_6 no vende apuestas "
        "ni realiza pagos."
    ),
    "jugada.no_existe": "La jugada no existe o no está disponible",
    "jugada.opcion_sorteo": "Elegir un sorteo",
    "jugada.registrada": "Jugada registrada",
    "jugada.repetido": "El {nn} ya está en la jugada",
    # modalidad
    "modalidad.no_informada": "No informada por las fuentes",
    "modalidad.pendiente_validacion": "Pendiente de validación",
    "modalidad.resultado_pendiente": "Resultado pendiente",
    # motivo
    "motivo.error_inesperado": "Error inesperado al procesar el sorteo",
    # nav
    "nav.administracion": "Administración",
    "nav.cuenta": "Cuenta de {correo}",
    "nav.crear_cuenta": "Crear cuenta",
    "nav.estadisticas": "Estadísticas",
    "nav.ingresar": "Ingresar",
    "nav.mis_jugadas": "Mis jugadas",
    "nav.logotipo": "QUINI_6, ir al inicio",
    "nav.menu": "Menú",
    "nav.principal": "Navegación principal",
    "nav.resultados": "Resultados",
    "nav.salir": "Salir",
    "nav.saltar": "Saltar al contenido",
    "nav.volver_extraccion": "← Extracción del {fecha_hora}",
    "nav.volver_extracciones": "← Extracción histórica",
    "nav.volver_jugadas": "← Mis jugadas",
    "nav.volver_sorteos": "← Sorteos",
    # obs
    "obs.categoria_fuera_catalogo": "Categoría fuera del catálogo: «{texto}». No se asignó.",
    "obs.concepto_importe": (
        "No se pudo determinar si el importe «{texto}» es pozo o premio individual."
    ),
    "obs.direccion_no_coincide": (
        "El número o la fecha de la página no coinciden con los de la dirección consultada"
    ),
    "obs.error_interprete": "La página de la fuente no se pudo interpretar",
    "obs.extracciones_iguales": (
        "{modalidad} y {modalidad}: la fuente publica los mismos seis números"
    ),
    "obs.falta": "Falta: {lista de datos}",
    "obs.importe_corregido": "Importe corregido: «{texto}» → {importe}",
    "obs.importe_invalido": "Importe con formato no reconocido: «{texto}»",
    "obs.negativo": "La fuente publica un valor negativo: «{texto}». No se usa.",
    "obs.no_correlativo": "El número y la fecha no son correlativos con el sorteo N.º {N}",
    "obs.numeros_cantidad": (
        "{modalidad}: la fuente publica {n} números en lugar de seis. No se usan."
    ),
    "obs.numeros_rango": "{modalidad}: la fuente publica «{texto}», fuera de 00 a 45. No se usan.",
    "obs.numeros_repetido": "{modalidad}: la fuente repite el número {nn}. No se usan.",
    "obs.pozo_premio_extra_texto": "Pozo Extra publicado como «{texto}»",
    "obs.premio_extra_invalida": (
        'Pozo Extra: la categoría ganadora informada no es 6, 5, 4 ni "Sin ganadores"'
    ),
    "obs.premio_extra_no_coincide": (
        "Los números de Pozo Extra de la fuente no coinciden con sus extracciones"
    ),
    "obs.rotulo_desconocido": (
        "Rótulo no reconocido: «{texto}». Ese bloque no se asignó a ninguna modalidad."
    ),
    "obs.siempre_sale_invalida": (
        "Siempre Sale: la categoría ganadora informada no es válida (debe tener entre 0 y "
        "6 aciertos y al menos un ganador)"
    ),
    "obs.sin_fuente": "Ninguna fuente informa este número de sorteo",
    # pag
    "pag.anterior": "Anterior",
    "pag.pagina": "Página {n} de {m}",
    "pag.siguiente": "Siguiente",
    # pie
    "pie.legal": (
        "Información de consulta. QUINI_6 no vende apuestas ni realiza pagos. La fuente "
        "de cada resultado es el extracto oficial indicado."
    ),
    # pozo
    "pozo.con_ganadores": "Con ganadores",
    "pozo.pendiente": "Pendiente",
    "pozo.vacante": "Vacante",
    # premios
    "premios.cero_ganadores": "0 ganadores",
    "premios.pendientes": "Información de premios pendiente de publicación",
    # resultados
    "resultados.concurso_inexistente": "No hay información del sorteo N.º {N}",
    "resultados.fecha_sin_concursos": "No hay información de sorteos del {fecha}",
    "resultados.pendientes": "Resultados pendientes",
    "resultados.sin_publicar": "Todavía no hay resultados publicados",
    # rot ([003] Etapa 2: rótulos de [002] que las plantillas tenían escritos, sin cambiar el texto)
    "rot.acciones": "Acciones",
    "rot.calculado": "Calculado: {calculo}",
    "rot.caption_fuentes_sorteo": "Resultado de la consulta a cada fuente",
    "rot.caption_resumen": "Resumen de la extracción",
    "rot.caption_sorteos_extraccion": "Sorteos de la extracción con su estado",
    "rot.dato": "Dato",
    "rot.direccion_consultada": "Dirección consultada",
    "rot.ejecutada_por": "Ejecutada por",
    "rot.estado": "Estado",
    "rot.extraccion_del": "Extracción del {fecha_hora}",
    "rot.fecha_con_valor": "Fecha: {valor}",
    "rot.fecha_del_sorteo": "Fecha del sorteo",
    "rot.fecha_y_hora": "Fecha y hora",
    "rot.fuente": "Fuente",
    "rot.fuentes_consultadas": "Fuentes consultadas",
    "rot.fuentes_utilizadas": "Fuentes utilizadas",
    "rot.intentos_fallidos": "Intentos fallidos",
    "rot.no_recuperados": "No recuperados",
    "rot.numero_sorteo": "N.º {numero}",
    "rot.numeros": "Números",
    "rot.observaciones": "Observaciones",
    "rot.periodo": "Período",
    "rot.periodo_consultado": "Período consultado",
    "rot.periodo_consultado_valor": "Período consultado: {desde} al {hasta}",
    "rot.periodo_rango": "{desde} al {hasta}",
    "rot.recuperados": "Recuperados",
    "rot.recuperados_parcialmente": "Recuperados parcialmente",
    "rot.resultado": "Resultado",
    "rot.resumen": "Resumen",
    "rot.sorteo": "Sorteo",
    "rot.sorteo_numero": "Sorteo N.º {numero}",
    "rot.sorteos": "Sorteos",
    "rot.sorteos_a_revisar": "Sorteos que requieren revisión",
    "rot.sorteos_aportados": "Sorteos aportados",
    "rot.sorteos_identificados": "Sorteos identificados",
    "rot.valor": "Valor",
    "rot.ver_en_curso": "Ver la extracción en curso",
    "rot.est_titulo": "Estadísticas de frecuencia",
    "rot.modalidad": "Modalidad",
    "rot.desde": "Desde",
    "rot.hasta": "Hasta",
    "rot.numero": "Número",
    "rot.consultar": "Consultar",
    "rot.frecuencia": "Frecuencia",
    "rot.porcentaje": "Porcentaje",
    "rot.est_considerados_uno": "{n} sorteo considerado, del {desde} al {hasta}.",
    "rot.est_considerados": "{n} sorteos considerados, del {desde} al {hasta}.",
    "rot.est_numero_consultado": (
        "El {numero} salió en {frecuencia} de {total} sorteos considerados ({porcentaje})."
    ),
    "rot.est_caption": "Apariciones de cada número en {modalidad}",
    "rot.est_grafico_titulo": "Frecuencia de cada número en {modalidad}",
    "rot.est_grafico_desc_uno": (
        "Gráfico de barras con las apariciones de cada número de 00 a 45 en {n} sorteo considerado"
    ),
    "rot.est_grafico_desc": (
        "Gráfico de barras con las apariciones de cada número de 00 a 45 en {n} sorteos "
        "considerados"
    ),
    "rot.est_grafico_resaltado": "; el {numero} aparece resaltado",
    "rot.est_barra": "{numero}: {frecuencia} apariciones",
    "rot.est_grafico_pie": (
        "Alto de cada barra proporcional a su cantidad de apariciones. La tabla siguiente tiene "
        "los mismos datos."
    ),
    "rot.res_titulo": "Resultados del Quini 6",
    "rot.res_sorteo_del": "Sorteo N.º {numero} — sorteo del {fecha}",
    "rot.res_pendientes": "Resultados pendientes",
    "rot.ver_sorteo": "Ver el sorteo",
    "rot.res_ultimos": "Últimos resultados: Sorteo N.º {numero} — sorteo del {fecha}",
    "rot.res_estado_sorteo": "Estado del sorteo:",
    "rot.res_numeros_distintos": "{n} números distintos",
    "rot.numeros_ganadores": "Números ganadores",
    "rot.en_revision": "Información en revisión",
    "rot.ver_premios": "Ver premios y detalle",
    "rot.todos_los_sorteos": "Todos los sorteos",
    "rot.caption_sorteos": "Sorteos, del más reciente al más antiguo",
    "rot.buscar_sorteo": "Buscar un sorteo",
    "rot.buscar_por_numero": "Buscar por número de sorteo",
    "rot.numero_de_sorteo": "Número de sorteo",
    "rot.buscar": "Buscar",
    "rot.buscar_por_fecha": "Buscar por fecha del sorteo",
    "rot.buscar_sorteos": "Buscar sorteos",
    "rot.sorteos_del": "Sorteos del {fecha}",
    "rot.sorteo_del": "Sorteo del {fecha}",
    "rot.registrar_jugada": "Registrar una jugada",
    "rot.sin_modalidades": "Este sorteo no tiene modalidades aplicables.",
    "rot.conjunto_premio_extra": "Conjunto de números del Premio Extra",
    "rot.conjunto_explicacion": (
        "{n} números distintos, reunidos de Tradicional – Primer Sorteo, Tradicional – La Segunda "
        "y Revancha."
    ),
    "rot.corregido_el": "Corregido el {fecha}",
    "rot.fuente_consultada": "Fuente: {fuente}, consultada el {fecha}",
    "rot.fuente_sola": "Fuente: {fuente}",
    "rot.fuente_premios_consultada": "Fuente de los premios: {fuente}, consultada el {fecha}",
    "rot.fuente_premios_sola": "Fuente de los premios: {fuente}",
    "rot.premios": "Premios",
    "rot.aciertos_condicion": "Aciertos o condición",
    "rot.ganadores": "Ganadores",
    "rot.un_ganador": "1 ganador",
    "rot.n_ganadores": "{n} ganadores",
    "rot.no_disponible": "No disponible",
    "rot.importe_categoria": "Importe destinado a la categoría",
    "rot.importe_individual": "Importe individual por ganador",
    "rot.premios_pendientes": "Información de premios pendiente de publicación",
    "rot.pozo_vacante": "Pozo vacante o acumulado",
    "rot.numeros_bolillas": "Números",
    "rot.mis_jugadas": "Mis jugadas",
    "rot.caption_jugadas": "Mis jugadas, de la más reciente a la más antigua",
    "rot.numeros_jugada": "Números de la jugada",
    "rot.participa_en": "Participa en: {modalidades}",
    "rot.participa_en_rotulo": "Participa en",
    "rot.aciertos": "Aciertos",
    "rot.costo": "Costo",
    "rot.editar_jugada": "Editar jugada",
    "rot.guardar_igual": "Guardar igual",
    "rot.cancelar": "Cancelar",
    "rot.participara_en": "Participará en: {modalidades}",
    "rot.seis_elegidos": "Seis números elegidos",
    "rot.agregar": "Agregar",
    "rot.costo_jugada": "Costo de la jugada (en pesos)",
    "rot.costo_ayuda": "Por ejemplo, 1500,50",
    "rot.guardar_cambios": "Guardar cambios",
    "rot.registrar_jugada_boton": "Registrar jugada",
    "rot.jugada_del_sorteo": "Jugada del sorteo N.º {numero}",
    "rot.editar": "Editar",
    "rot.estado_dos_puntos": "Estado:",
    "rot.comparacion_titulo": "Comparación con los resultados oficiales",
    "rot.eliminar_jugada": "Eliminar jugada",
    "rot.jugada_resumen": "Sorteo N.º {numero} — sorteo del {fecha} · {costo}",
    "rot.jugada_no_disponible": "Jugada no disponible",
    "rot.volver_mis_jugadas": "Volver a mis jugadas",
    "rot.publicado_en_revision": "Publicado · Información en revisión",
    "rot.resultado_publicado": "Resultado publicado",
    "rot.acertado": "(acertado)",
    "rot.numeros_oficiales": "Números oficiales: {numeros}",
    "rot.n_aciertos": "{n} aciertos",
    "rot.n_aciertos_conjunto": "{n} aciertos en el conjunto",
    "rot.elegibilidad": "Elegibilidad:",
    "rot.importe": "Importe:",
    "rot.opcion_sorteo": "Sorteo N.º {numero} — {fecha}",
    "rot.ingresar": "Ingresar",
    "rot.crear_cuenta": "Crear cuenta",
    "rot.crear_cuenta_intro": "Solo se pide un correo electrónico y una contraseña.",
    "rot.correo": "Correo electrónico",
    "rot.contrasena": "Contraseña",
    "rot.contrasena_ayuda": "Al menos 8 caracteres.",
    "rot.adm_sorteos": "Sorteos",
    "rot.adm_extraccion": "Extracción histórica de sorteos",
    "rot.adm_caption": "Sorteos cargados, del más reciente al más antiguo",
    "rot.adm_numeros_estado": "Números {numeros} · Premios {premios}",
    "rot.adm_premios_estado": "Premios {premios}",
    "rot.adm_modificar_sorteo": "Modificar sorteo",
    "rot.adm_ver_historial": "Ver historial",
    "rot.adm_ver_publica": "Ver página pública",
    "rot.adm_resumen": "Sorteo del {fecha} · Completitud: {completitud} · {jugadas}",
    "rot.adm_admite_jugadas": "Admite jugadas",
    "rot.adm_no_admite_jugadas": "Ya no admite jugadas",
    "rot.adm_premio_extra_explicacion": (
        "Premio Extra no tiene números propios: su conjunto surge de Primer Sorteo, La Segunda y "
        "Revancha."
    ),
    "rot.adm_bloque_estado": "{bloque}: {estado}",
    "rot.adm_publicado_el": "Publicado el {fecha_hora}",
    "rot.adm_publicado_el_fuente": "Publicado el {fecha_hora} · Fuente: {fuente}",
    "rot.adm_numeros_publicados": "Números publicados",
    "rot.adm_en_revision_motivo": "En revisión: {motivo}",
    "rot.adm_correccion_preparacion": "Corrección en preparación",
    "rot.adm_actualizado": "{estado} — actualizado el {fecha_hora}.",
    "rot.adm_numeros_preparacion": "Números en preparación",
    "rot.adm_observado_motivo": "Observado: {motivo}",
    "rot.adm_cargar": "Cargar",
    "rot.adm_publicar_correccion": "Publicar corrección",
    "rot.adm_revisar_publicar": "Revisar y publicar",
    "rot.adm_resolver": "Resolver observación",
    "rot.adm_marcar_observado": "Marcar como Observado",
    "rot.adm_motivo_observacion": "Motivo de la observación",
    "rot.adm_observar": "Observar",
    "rot.adm_marcar_revision": "Marcar en revisión",
    "rot.adm_motivo_revision": "Motivo de la revisión",
    "rot.adm_quitar_revision": "Quitar revisión",
    "rot.adm_motivo_quitar": "Motivo para quitar la revisión",
    "rot.adm_corregir": "Corregir",
    "rot.adm_motivo_correccion": "Motivo de la corrección",
    "rot.adm_iniciar_correccion": "Iniciar corrección",
    "rot.adm_fuente_correccion": "Fuente de la corrección (descripción)",
    "rot.adm_fecha_fuente": "Fecha de consulta de la fuente",
    "rot.adm_sin_modalidades": "El sorteo no tiene modalidades aplicables.",
    "rot.adm_modificar_titulo": "Modificar el sorteo N.º {numero}",
    "rot.adm_duplicado": "El sorteo N.º {numero} ya existe.",
    "rot.adm_ir_existente": "Ir al sorteo existente",
    "rot.adm_modalidades_aplicables": "Modalidades aplicables",
    "rot.adm_premio_extra_requiere": "Premio Extra requiere Primer Sorteo, La Segunda y Revancha.",
    "rot.adm_numeros_de": "Números de {modalidad}",
    "rot.adm_premios_de": "Premios de {modalidad}",
    "rot.adm_correccion_explicacion": (
        "El público sigue viendo los valores publicados hasta que publiques la corrección."
    ),
    "rot.adm_borrador_explicacion": (
        "Lo que guardes queda en Borrador y no es visible para el público."
    ),
    "rot.adm_seis_numeros": "Seis números distintos de 00 a 45",
    "rot.adm_guardar_borrador": "Guardar borrador",
    "rot.adm_premios_explicacion": (
        "Las categorías son fijas. Dejá vacío un dato para registrarlo como no disponible. "
        "Importes con coma decimal (por ejemplo, 1.500,50)."
    ),
    "rot.adm_caption_premios": "Datos por categoría (vacío = no disponible)",
    "rot.adm_categoria": "Categoría",
    "rot.adm_publicar": "Publicar",
    "rot.adm_publicar_titulo": "{accion}: {bloque} de {modalidad}",
    "rot.adm_no_se_publico": "No se publicó la información:",
    "rot.adm_info_publicar": "Información a publicar",
    "rot.adm_categoria_ganadora_sin": "Categoría ganadora: Sin ganadores",
    "rot.adm_categoria_ganadora": "Categoría ganadora: {n} aciertos",
    "rot.adm_importe_destinado": "Importe destinado",
    "rot.adm_importe_individual": "Importe individual",
    "rot.adm_no_disponible": "no disponible",
    "rot.adm_fuente_publicar": "Fuente: {fuente}",
    "rot.adm_sin_registrar": "sin registrar",
    "rot.adm_fuente_consultada": "Fuente: {fuente}, consultada el {fecha}",
    "rot.adm_motivo_correccion_valor": "Motivo de la corrección: {motivo}",
    "rot.adm_errores_publicar": "Errores que impiden publicar",
    "rot.adm_sin_bloqueantes": "No hay errores bloqueantes.",
    "rot.adm_advertencias": "Advertencias",
    "rot.adm_historial_titulo": "Historial de cambios del sorteo N.º {numero}",
    "rot.adm_historial_caption": "Cambios, del más reciente al más antiguo",
    "rot.adm_accion": "Acción",
    "rot.adm_modalidad_bloque": "Modalidad y bloque",
    "rot.adm_valor_anterior": "Valor anterior",
    "rot.adm_valor_nuevo": "Valor nuevo",
    "rot.adm_autor": "Autor",
    "rot.adm_motivo": "Motivo",
    "rot.adm_sin_cambios": "Todavía no hay cambios registrados.",
    # sorteo
    "sorteo.combina": "Combina fuentes",
    "sorteo.inconsistencias": "Con inconsistencias",
    "sorteo.no_recuperado": "No recuperado",
    "sorteo.parcial": "Recuperado parcialmente",
    "sorteo.recuperado": "Recuperado",
    "sorteo.reglas_no_verificadas": "Reglas del período no verificadas",
    # tabla
    "tabla.orden_asc": "Orden ascendente",
    "tabla.orden_desc": "Orden descendente",
    # tema
    "tema.claro": "Claro",
    "tema.dispositivo": "Según el dispositivo",
    "tema.guardar": "Guardar tema",
    "tema.oscuro": "Oscuro",
    "tema.titulo": "Tema",
    # vacio
    "vacio.estadisticas.explicacion": 'Probar con otro período o con "Todo el historial".',
    "vacio.extracciones.explicacion": (
        "Cada extracción histórica genera un archivo CSV con los sorteos del período elegido."
    ),
    "vacio.extracciones.titulo": "Todavía no hay extracciones",
    "vacio.filtro.accion": "Limpiar filtros",
    "vacio.filtro.explicacion": "Ningún elemento coincide con: {filtro}",
    "vacio.filtro.titulo": "Sin resultados para el filtro",
    "vacio.jugadas.accion": "Registrar mi primera jugada",
    "vacio.jugadas.explicacion": (
        "Cada jugada registrada muestra cuántos aciertos tuvo en cada sorteo"
    ),
    "vacio.jugadas.titulo": "Todavía no hay jugadas registradas",
    "vacio.resultados.accion_cargar": "Cargar sorteo",
    "vacio.resultados.accion_extraccion": "Extracción histórica",
    "vacio.resultados.explicacion": "Los resultados aparecen aquí cuando se publica cada sorteo.",
    "vacio.resultados.titulo": "Todavía no hay resultados publicados",
    "vacio.resultados_nota_admin": (
        "La extracción histórica genera un archivo CSV; no carga sorteos en la aplicación"
    ),
}


def mensaje(clave: str, **valores: object) -> str:
    """Texto de ``clave`` con sus variables completas (``{n}``, ``{fecha}``…).

    Una clave inexistente es un error de programación (``KeyError``), nunca un texto vacío.
    """
    texto = MENSAJES[clave]
    return texto.format_map(valores) if valores else texto
