# Contrato de rutas web (interfaz de usuario)

**Plan**: [../plan.md](../plan.md) | **Modelo**: [../data-model.md](../data-model.md) | **Mensajes**: [mensajes.md](mensajes.md)

La aplicación renderiza HTML en el servidor. Este contrato fija qué rutas existen, quién puede usarlas y cómo responden cuando el acceso no está permitido. **No se agregan rutas que no estén en esta tabla** (Const. I). Toda ruta aparece aquí con el requisito que la justifica (Const. II).

## Niveles de acceso

| Nivel | Significado | Respuesta si no se cumple |
|-------|-------------|---------------------------|
| **Público** | Sin sesión (FR-001, RN-34). | — |
| **Sesión** | Usuario autenticado (RN-35). | Redirección 302 a `/ingresar/?next=<ruta solicitada>` (AC-3.8). |
| **Propietario** | Sesión y la jugada pertenece a la cuenta (RN-36). | 404 con "La jugada no existe o no está disponible". Es la misma respuesta para una jugada inexistente o ajena (AC-4.12). |
| **Admin** | Sesión y `es_administrador` (RN-37, FR-011). | Sin sesión: redirección a `/ingresar/?next=…` (AC-2.12). Con sesión sin permiso: 403 con "No tenés permisos para acceder a esta sección" (AC-2.11). |

Reglas comunes:

- Todo `POST` exige un token CSRF.
- Las respuestas de los niveles Sesión, Propietario y Admin llevan `Cache-Control: no-store` (AC-3.7).
- El permiso se verifica en **cada** solicitud, tanto `GET` como `POST` (Const. IV).

## Rutas públicas

| Método | Ruta | Propósito | Requisitos / CA |
|--------|------|-----------|-----------------|
| GET | `/` | Lleva a `/resultados/`. | FR-001 |
| GET | `/resultados/` | Últimos resultados según RN-25: el concurso de "últimos resultados" y, por separado, el concurso actual pendiente si existe. También el listado de todos los concursos registrados, ordenado por fecha del sorteo de forma descendente. | FR-002, FR-003; AC-1.1, AC-1.2, AC-1.13 |
| GET | `/resultados/buscar/?numero=N` | Búsqueda por número. Si existe, lleva a `/resultados/N/`. Si no, muestra "No hay información del concurso N.º X". | AC-1.3, AC-1.4 |
| GET | `/resultados/buscar/?fecha=dd/mm/aaaa` | Búsqueda por fecha del sorteo. Muestra los concursos de esa fecha o el mensaje de P-07. | AC-1.3 |
| GET | `/resultados/<numero>/` | Detalle público del concurso: completitud, cada modalidad aplicable con su estado público, números, premios por categoría, fuente, revisión y corrección. Premio Extra se muestra con su conjunto de números solo cuando Primer Sorteo, La Segunda y Revancha están publicadas; si no, con el estado derivado de RN-20 y nunca con un conjunto parcial. Sus premios se muestran si están publicados (RN-18). Si el concurso admite jugadas, ofrece el botón "Registrar una jugada". | FR-004, FR-005; AC-1.5 a AC-1.12, AC-1.14 a AC-1.16, AC-3.9 |
| GET | `/estadisticas/?modalidad=<código>&desde=dd/mm/aaaa&hasta=dd/mm/aaaa&numero=NN&anterior_modalidad=<código>&anterior_desde=dd/mm/aaaa&anterior_hasta=dd/mm/aaaa&anterior_numero=NN` | Frecuencias de los 46 números (tabla y gráfico), cantidad de sorteos considerados, rango de fechas, aviso de concursos sin información y consulta de un número. Todos los parámetros son opcionales. Los parámetros `anterior_*` son campos ocultos del formulario con la consulta que se estaba mostrando: si `desde` es posterior a `hasta`, se muestra el error y se repiten exactamente las estadísticas de la consulta anterior (AC-6.8). Si no hay consulta anterior, se usan los valores predeterminados (RN-42). Las modalidades ofrecidas son Primer Sorteo, La Segunda, Revancha y Siempre Sale (RN-46). | FR-026 a FR-028; AC-6.1 a AC-6.9, AC-6.11 |

## Cuentas

| Método | Ruta | Acceso | Propósito | Requisitos / CA |
|--------|------|--------|-----------|-----------------|
| GET, POST | `/registrarse/?next=…` | Público | Crear una cuenta (correo y contraseña). Al terminar, inicia la sesión y lleva a `next` o a `/mis-jugadas/`. | FR-015, FR-017; AC-3.1 a AC-3.3, AC-3.9 |
| GET, POST | `/ingresar/?next=…` | Público | Iniciar sesión. Aplica el bloqueo de NFR-005 y, al terminar, lleva a `next` validado. | FR-016 a FR-018; AC-3.4 a AC-3.6, AC-3.8, AC-3.9 |
| POST | `/salir/` | Sesión | Cerrar sesión y volver a `/resultados/`. | FR-016; AC-3.7 |

## Jugadas personales

| Método | Ruta | Acceso | Propósito | Requisitos / CA |
|--------|------|--------|-----------|-----------------|
| GET | `/mis-jugadas/` | Sesión | Historial: jugadas ordenadas por fecha del sorteo de forma descendente, con su estado resumido (P-04). Si no hay jugadas, muestra el estado vacío. | FR-020; AC-4.13, AC-4.15, AC-5.13 |
| GET, POST | `/mis-jugadas/nueva/?concurso=<numero>` | Sesión | Registrar una jugada. Solo ofrece concursos que admiten jugadas (RN-07). Si `concurso` viene en la dirección, aparece preseleccionado. Advierte sobre duplicados (RN-06) con un segundo envío que lleva `confirmar_duplicado=1`. | FR-019; AC-4.1 a AC-4.9, AC-4.14, AC-4.16, AC-3.9 |
| GET | `/mis-jugadas/<id>/` | Propietario | Detalle de la jugada y su comparación por modalidad (RN-29). | FR-020, FR-023 a FR-025; AC-5.1 a AC-5.33, AC-4.17 |
| GET, POST | `/mis-jugadas/<id>/editar/` | Propietario | Editar los números, el concurso y el costo. Si el concurso ya tiene alguna extracción publicada, la jugada no cambia y se muestra el mensaje de RN-08. | FR-021; AC-4.10, AC-4.17 |
| GET, POST | `/mis-jugadas/<id>/eliminar/` | Propietario | GET muestra la confirmación. POST elimina. Aplica la misma restricción de RN-08. | FR-021; AC-4.11, AC-4.17 |

Las rutas de jugadas usan el `id` interno. Que el `id` se pueda adivinar no permite acceder a jugadas ajenas, porque toda consulta se filtra por la cuenta en sesión.

## Administración de resultados

| Método | Ruta | Acceso | Propósito | Requisitos / CA |
|--------|------|--------|-----------|-----------------|
| GET | `/administracion/concursos/` | Admin | Listado de concursos con el estado RN-16 de cada bloque. | FR-006, FR-009 |
| GET, POST | `/administracion/concursos/nuevo/` | Admin | Crear un concurso con número, fecha y modalidades aplicables. | FR-006; AC-2.1, AC-2.2 |
| GET, POST | `/administracion/concursos/<numero>/modificar/` | Admin | Modificar la fecha y las modalidades. **P-05, a confirmar.** | RN-05 |
| GET | `/administracion/concursos/<numero>/` | Admin | Panel del concurso: cada modalidad con sus bloques de números y premios, su estado, sus versiones y las acciones disponibles. | FR-007, FR-009 |
| GET, POST | `/administracion/concursos/<numero>/<modalidad>/numeros/` | Admin | Cargar o editar el borrador de números (o el de corrección) con la fuente. | FR-007; AC-2.3, AC-2.4, AC-7.2 |
| GET, POST | `/administracion/concursos/<numero>/<modalidad>/premios/` | Admin | Cargar o editar el borrador de premios: categorías predefinidas, ganadores, importes, pozo, categoría ganadora (Siempre Sale y Premio Extra) y fuente. | FR-007; AC-2.13 |
| POST | `/administracion/concursos/<numero>/<modalidad>/<bloque>/observar/` | Admin | Pasar a Observado, con motivo. | AC-2.8 |
| POST | `/administracion/concursos/<numero>/<modalidad>/<bloque>/resolver/` | Admin | Pasar de Observado a Borrador. | RN-16 |
| GET, POST | `/administracion/concursos/<numero>/<modalidad>/<bloque>/publicar/` | Admin | GET muestra los errores bloqueantes, las advertencias de RN-22 y la casilla de cotejo. POST publica si se cumple RN-17. | FR-008, FR-009; AC-2.5 a AC-2.7, AC-2.9 |
| POST | `/administracion/concursos/<numero>/<modalidad>/<bloque>/revision/` | Admin | Marcar "En revisión", con motivo. | FR-012; AC-7.1 |
| POST | `/administracion/concursos/<numero>/<modalidad>/<bloque>/quitar-revision/` | Admin | Quitar la marca, con motivo. **P-01 (b), a confirmar.** | RN-16 |
| POST | `/administracion/concursos/<numero>/<modalidad>/<bloque>/corregir/` | Admin | Iniciar una corrección: crea una versión en trabajo a partir de la publicada y exige motivo y fuente. | FR-012; AC-7.2 |
| GET | `/administracion/concursos/<numero>/historial/` | Admin | Historial de cambios: valor anterior, valor nuevo, fecha, autor, motivo y fuente. | FR-013; AC-7.3 |

`<bloque>` ∈ {`numeros`, `premios`}. `<modalidad>` ∈ {`primer-sorteo`, `la-segunda`, `revancha`, `siempre-sale`, `premio-extra`}. `premio-extra/numeros` no existe y responde 404 (RN-15).

## Páginas de error

| Código | Cuándo | Texto principal |
|--------|--------|-----------------|
| 403 | Sesión sin permiso de administrador en una ruta de administración. | "No tenés permisos para acceder a esta sección" |
| 404 | Jugada ajena o inexistente. | "La jugada no existe o no está disponible" |
| 404 | Cualquier otra ruta inexistente. | "La página que buscás no existe" |
| 500 | Error inesperado. | "Ocurrió un error. Intentá de nuevo en unos minutos." (sin detalles técnicos) |
