# Contrato de rutas web: Extracción histórica de sorteos

**Plan**: [../plan.md](../plan.md) | **Modelo**: [../data-model.md](../data-model.md) | **Mensajes**: [mensajes.md](mensajes.md)

Este contrato **amplía** [001] [contracts/rutas.md](../../001-quini6-mvp/contracts/rutas.md) con las rutas de esta feature. Rige la misma regla: no se agregan rutas que no estén en una tabla de contrato (Const. I), y cada ruta indica el requisito que la justifica (Const. II).

## Nivel de acceso

Todas las rutas son de nivel **Admin** de [001]: sin sesión, redirección a `/ingresar/?next=…`; con sesión sin permiso de administrador, 403 con "No tenés permisos para acceder a esta sección" (RN-42, AC-6.1, AC-6.2, AC-6.6). Se verifica en cada `GET` y `POST`, todas las respuestas llevan `Cache-Control: no-store` (NFR-004) y todo `POST` exige el token CSRF. Se implementa con el decorador existente `administrador_requerido`.

## Rutas

| Método | Ruta | Propósito | Requisitos / CA |
|--------|------|-----------|-----------------|
| GET | `/administracion/extracciones/` | Pantalla «Extracción histórica de sorteos». Si el administrador tiene una extracción en curso, muestra su avance en lugar del formulario y un enlace a ella, sin permitir iniciar otra. Si no, muestra el formulario con "Fecha de inicio", "Fecha de finalización" y el botón "Iniciar extracción". Debajo, el listado "Extracciones anteriores" de todos los administradores, de la más reciente a la más antigua, con la columna "Fecha" (fecha y hora de inicio, con enlace a su página), quién la ejecutó, período y estado, y, en las terminadas, un menú de acciones (⋮, `<details>` sin JavaScript) con "Eliminar". Los campos de fecha son `type="date"`: la fecha se escribe con el teclado y el navegador agrega las barras; el calendario se abre con el ícono del campo, sin script que lo fuerce al hacer clic (D-27); el servidor acepta `AAAA-MM-DD` y `dd/mm/aaaa`. | FR-001, FR-002, FR-015; AC-1.1, AC-1.11, AC-1.14, AC-1.18, AC-1.20 |
| POST | `/administracion/extracciones/` | Inicia una extracción. Si el período no cumple RN-01 a RN-04, vuelve a mostrar la pantalla con el error junto al campo y las fechas ingresadas (200). Si el administrador ya tiene una en curso, no crea otra y lleva a esa. Si es válido, crea la extracción y redirige (303) a su página. | FR-002, FR-003; AC-1.2 a AC-1.6, AC-1.11 |
| GET | `/administracion/extracciones/<id>/` | Página de una extracción, propia o de otro administrador. **En curso**: "Extracción en curso", período y "Identificando los sorteos del período…" o "N de M sorteos procesados" con una barra de progreso en la misma proporción (D-26), en un bloque que se actualiza solo con JavaScript ([002] R-10). **Terminada**: resultado global, avisos de cobertura y de huecos, resumen de RN-33 con las fuentes utilizadas, lista de sorteos que requieren revisión, lista de todos los sorteos con su estado y enlace a su detalle, y el botón "Descargar CSV" si hay al menos un sorteo identificado. **Sin sorteos**: solo el mensaje de AC-1.10. | FR-003, FR-012, FR-013, FR-015; AC-1.2, AC-1.7 a AC-1.10, AC-1.15 a AC-1.17, AC-1.21, AC-2.1, AC-2.10 |
| GET | `/administracion/extracciones/<id>/sorteos/<numero>/` | Detalle de un sorteo: resultado de cada fuente con dirección y fecha y hora de consulta; por modalidad y categoría, cada dato con su valor normalizado o su estado y la marca "Sin corroborar", sin repetir las fuentes junto a cada dato (D-23); discrepancias con cada valor y su fuente; observaciones; las indicaciones "Combina fuentes" y "Reglas del período no verificadas"; y el enlace "Ver extracto oficial (Lotería de Santa Fe)". Disponible desde que el sorteo se procesó, aunque la extracción siga en curso. | FR-006, FR-007, FR-012; AC-1.12, AC-1.13, AC-2.2 a AC-2.7, AC-3.x, AC-4.x |
| GET | `/administracion/extracciones/<id>/eliminar/` | Confirmación "Eliminar extracción": período, quién la ejecutó y el aviso de que no se puede deshacer, con los botones "Eliminar" y "Cancelar". Si la extracción está en curso, redirige (303) a la pantalla con "No se puede eliminar una extracción en curso". | FR-015; AC-1.18, AC-1.19 (20/11/2026, D-24) |
| POST | `/administracion/extracciones/<id>/eliminar/` | Elimina la extracción terminada con sus sorteos e intentos y redirige (303) a `/administracion/extracciones/` con "Extracción eliminada". Si está en curso, no la elimina y redirige con "No se puede eliminar una extracción en curso". | FR-015; AC-1.18, AC-1.19 (D-24) |
| GET | `/administracion/extracciones/<id>/csv/` | Descarga el archivo guardado, siempre con el mismo contenido (`Content-Type: text/csv; charset=utf-8`, `Content-Disposition: attachment; filename="quini6-extraccion-{id}-{desde}-a-{hasta}.csv"`). Si la extracción está en curso o terminó sin sorteos, responde 404. | FR-014, FR-015; AC-5.1 a AC-5.10, AC-1.15 |

Respuestas de error:

- `<id>` inexistente, o `<numero>` que no pertenece a los identificados de esa extracción: 404 con "La página que buscás no existe" ([001]).
- No hay rutas para editar ni cancelar extracciones (Supuestos de la spec). Desde el 20/11/2026 hay una ruta para eliminar las terminadas (D-24).

## Acceso desde la sección de administración (AC-1.1)

La página `/administracion/concursos/` ([001]) agrega el enlace «Extracción histórica de sorteos» hacia `/administracion/extracciones/`, y la pantalla de extracciones tiene un enlace de regreso a «Concursos». No se agrega ningún elemento a la navegación principal.

## Lo que estas rutas no hacen (RN-41)

Ninguna ruta de esta feature crea ni modifica concursos, modalidades, versiones, registros de cambio ni jugadas. Las vistas de `extracciones` no importan modelos de `resultados` ni de `jugadas`.
