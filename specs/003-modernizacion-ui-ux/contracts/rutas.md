# Contrato de rutas y enrutamiento

**Plan**: [../plan.md](../plan.md) | **API**: [api.md](api.md) | **Research**: R-10, R-12, R-14, R-18, R-20, R-27, R-28

Las rutas de [001] y [002] **no cambian de dirección** (D-04: "concurso" cambia solo en los textos). Permisos sin cambios (spec, Actores y permisos): cada ruta conserva su nivel y la verificación en el servidor en cada GET y POST. Next.js reproduce las mismas direcciones con barra final (`trailingSlash: true`, R-18).

## 1. Rutas HTML de Django: altas y cambios de comportamiento

Nivel: **P** público · **U** usuario registrado · **A** administrador.

| Ruta | Método | Nivel | Cambio en [003] | Requisitos |
|------|--------|:-----:|-----------------|------------|
| `/preferencias/tema/` | POST | P | **Nueva.** Campo `tema` (`claro`, `oscuro`, `dispositivo`) y `next` (ruta interna; cualquier otro valor → `/`). Fija o borra la cookie `quini6_tema` y responde 303 a `next`. CSRF | FR-036, AC-12.2, R-14 |
| `/administracion/extracciones/` | GET | A | Acepta `?estado=&orden=&pagina=` (data-model § 2). Con `HX-Request`: responde solo el fragmento del listado | FR-003, FR-027, AC-1.4, AC-9.1, AC-9.2 |
| `/administracion/extracciones/` | POST | A | Verifica RN-03 (respuesta con `ext.periodo_en_curso` y enlace a la existente) y la `clave_idempotencia` (R-11) | FR-006, FR-031, AC-3.5 |
| `/administracion/extracciones/<id>/` | GET | A | Con `HX-Request`: solo el fragmento `#avance-extraccion`; si terminó, el fragmento final y la cabecera `HX-Trigger` con el aviso | FR-005, AC-3.2, AC-3.3, R-10 |
| `/administracion/extracciones/<id>/eliminar/` | GET | A | Con `HX-Request`: solo el contenido del `ConfirmDialog`. Sin él: la página de confirmación de [002] (sin scripts) | FR-008, AC-2.3, AC-2.4 |
| `/administracion/extracciones/<id>/eliminar/` | POST | A | Mensaje `ext.eliminada` con fecha y hora; si ya no existe: `ext.no_existe` y 303 al listado; idempotente con clave | FR-009, AC-2.5, Casos límite |
| `/ingresar/` | POST | P | Acepta el campo `pendiente` (R-12): tras ingresar, responde el formulario destino precargado, `no-store`. Si la ruta del token pertenece a Next.js, responde la página "Volver al formulario" (un botón que envía el token por POST a esa ruta) | FR-032, AC-14.4 |
| POST de toda vista **U** o **A** con formulario reanudable | POST | U/A | Sin sesión: responde "Ingresar" con `cuenta.sesion_vencida` y el token `pendiente` (código 200, `no-store`) en lugar de redirigir | FR-032 |
| `/resultados/` | GET | P | Estado vacío con accesos "Cargar sorteo" y "Extracción histórica" **solo** para administradores | FR-026, AC-8.4 |
| `/estadisticas/` | GET | P | Atajos de período (RN-04) calculados en el servidor | AC-4.4 |
| Todas | GET | — | `data-theme` según la cookie `quini6_tema`; enlace activo con `aria-current="page"` | FR-014, R-14 |

Las respuestas de fragmento (`HX-Request`) llevan `Vary: HX-Request` y mantienen `Cache-Control: no-store` en las rutas privadas. Un fragmento de una ruta **A** pedido sin permisos responde lo mismo que la ruta completa (403), nunca el fragmento.

Se elimina `static/js/avance-extraccion.js` (reemplazado por HTMX, R-10).

## 2. API

Todas las operaciones bajo `/api/v1/`, detalladas en [api.md](api.md). Siempre las atiende Django.

## 3. Propiedad de cada ruta en el enrutador (Caddy, R-20)

Reglas evaluadas en este orden:

| Prioridad | Patrón | Destino | Etapa |
|:---------:|--------|---------|-------|
| 1 | `/api/*`, `/static/*`, `/administracion/extracciones/*/csv/` | Django | Siempre |
| 2 | `/_next/*` | Next.js | Desde la Etapa 2 |
| 3 | `QUINI6_RUTAS_NEXT`, método `POST` con el parámetro `?_interfaz=django` (lo agregan todos los formularios de Django) | Django (formularios abiertos antes de una conmutación, R-20) | Mientras la pantalla tenga plantillas |
| 4 | `QUINI6_RUTAS_NEXT` (resto, incluidos los POST sin la marca) | Next.js, con **vuelta automática a Django** si Next.js no responde (`lb_policy first` + comprobación de salud) | Etapa 3 (conmutación) |
| 4b | `QUINI6_RUTAS_NEXT_SIN_RESPALDO` (pantallas cuyas plantillas ya se retiraron) | Next.js sin segundo destino; si no responde, `infra/no-disponible.html`; un POST con la marca recibe la página de formulario vencido | Etapa 3 (después del retiro) |
| 5 | Todo lo demás | Django | Siempre (hasta el retiro) |

No hay activación parcial por grupo de personas ni cookie de vista previa (NFR-008, decisión del 21/11/2026). Antes de conmutar, cada pantalla se prueba en el entorno de pruebas con su ruta en `QUINI6_RUTAS_NEXT`.

Valor de `QUINI6_RUTAS_NEXT` por pantalla conmutada (R-27); cada fila agrega sus patrones a los anteriores:

| Orden | Pantalla | Patrones que se agregan |
|:-----:|----------|-------------------------|
| 0 + 1 | Estructura común + Extracción histórica | `/administracion/extracciones/` `/administracion/extracciones/*` (la regla 1 sigue enviando el CSV a Django) |
| 2 | Estadísticas | `/estadisticas/` |
| 3 | Mis jugadas | `/mis-jugadas/` `/mis-jugadas/*` |
| 4 | Resultados y búsqueda | `/` `/resultados/` `/resultados/*` |
| 5 | Ingresar y Crear cuenta | `/ingresar/` `/registrarse/` `/salir/` `/preferencias/*` |
| 6 | Administración de sorteos | `/administracion/concursos/` `/administracion/concursos/*` |

Las páginas de error (403, 404, 500) las genera la aplicación dueña de cada ruta, con el mismo diseño y textos.

Caddy agrega a cada respuesta la cabecera `X-Interfaz: django` o `X-Interfaz: next` para verificar quién respondió (diagnóstico; no contiene datos).

**Reversa** (pedido §3.5): quitar los patrones de la pantalla de `QUINI6_RUTAS_NEXT` y ejecutar `caddy reload`. Las plantillas de Django de esa pantalla existen hasta el final de su estabilización (R-28), así que la reversa es inmediata y no requiere desplegar código.

## 4. Rutas de Next.js (Etapa 2)

Mismas direcciones que la tabla de [001] y [002] para cada pantalla migrada, más:

| Ruta de Next.js | Uso |
|-----------------|-----|
| `app/administracion/extracciones/@modal/(.)[id]/eliminar/page.tsx` | Ruta interceptada: `ConfirmDialog` con navegación del cliente; la página completa `[id]/eliminar/page.tsx` sirve sin scripts (R-18) |

No se agregan rutas públicas para comprobar la salud de los servicios: el enrutador y el despliegue consultan directamente los puertos internos de Django y de Next.js.

Ninguna ruta de Next.js decide permisos: muestra lo que Django responde (`401` → "Ingresar", `403` → página de sin permisos, `404` → página inexistente, idéntica para jugadas ajenas o inexistentes).
