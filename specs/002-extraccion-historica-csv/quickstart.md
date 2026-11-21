# Guía de puesta en marcha y validación: Extracción histórica de sorteos

**Plan**: [plan.md](plan.md) | **Rutas**: [contracts/rutas.md](contracts/rutas.md) | **Mensajes**: [contracts/mensajes.md](contracts/mensajes.md) | **CSV**: [contracts/csv.md](contracts/csv.md)

Esta guía sirve para comprobar **desde la pantalla y con el archivo descargado** que la feature cumple sus criterios de aceptación (Const. VI). Parte de la preparación de [001] [quickstart.md](../001-quini6-mvp/quickstart.md) (entorno, cuentas `admin@prueba.local`, `ana@prueba.local` y permiso de administrador). No contiene código de implementación.

---

## 1. Requisitos previos

- Lo mismo que [001] §1.
- Una planilla de cálculo de uso común (LibreOffice Calc, Excel o Google Sheets) para abrir el CSV.
- Para los escenarios con fuentes reales (§6): conexión a internet.

## 2. Tres procesos en tres terminales (PowerShell, desde la raíz)

```powershell
# Terminal 1: aplicación
python manage.py migrate
python manage.py runserver

# Terminal 2: trabajador de extracciones (una sola instancia, contracts/comandos.md)
python manage.py procesar_extracciones

# Terminal 3 (solo §5): servidor de fuentes de prueba
python -m tests.fuentes_prueba.servidor --escenario normal --puerto 8765
```

Para usar las fuentes de prueba, antes de iniciar las terminales 1 y 2, se agregan en `.env`:

```text
QUINI6_FUENTE_F1_URL=http://127.0.0.1:8765/f1
QUINI6_FUENTE_F2_URL=http://127.0.0.1:8765/f2
QUINI6_FUENTE_F3_URL=http://127.0.0.1:8765/f3
```

Para volver a las fuentes reales, se vacían esas tres variables y se reinician las terminales 1 y 2. Para cambiar de escenario, se reinicia solo la terminal 3 con otro `--escenario`.

Resultado esperado: si el trabajador no está en ejecución, una extracción iniciada queda "Extracción en curso" sin avanzar; al iniciarlo, continúa.

## 3. Pruebas automatizadas

```powershell
pytest tests/unit/extraccion          # reglas puras e intérpretes de cada fuente
pytest tests/integration -k extraccion # recorridos, acceso, aislamiento y CSV (sin red)
pytest                                 # suite completa, incluida la de 001
ruff check .
```

Resultado esperado: todo en verde y `ruff` sin errores. No reemplazan la verificación manual.

## 4. Cómo revisar el archivo

Abrir la planilla, importar el CSV indicando **UTF-8** y **separador coma** (en Excel: Datos → Desde texto/CSV). Comprobar con [contracts/csv.md](contracts/csv.md).

---

## 5. Escenarios con fuentes de prueba

Los escenarios están en `tests/fuentes_prueba/escenarios/`. Cada uno trae sus páginas y un `escenario.json` que se puede editar para provocar otros casos (Supuestos de la spec). Las fechas de los ejemplos son las de la spec (sorteos 3422 a 3427, noviembre de 2026).

### Escenario A — Acceso y pantalla (US1, US6) · escenario `normal`

1. Como `ana@prueba.local` (sin permiso), abrir `/administracion/extracciones/`, `/administracion/extracciones/1/` y `/administracion/extracciones/1/csv/`. **Esperado**: "No tenés permisos para acceder a esta sección" en las tres (AC-6.1, AC-6.6).
2. Sin sesión, abrir `/administracion/extracciones/`. **Esperado**: pide iniciar sesión; al ingresar como Ana, el mensaje del paso 1 (AC-6.2).
3. Como administrador, abrir "Administración". **Esperado**: el enlace «Extracción histórica de sorteos»; al entrar, los campos "Fecha de inicio" y "Fecha de finalización" y el botón "Iniciar extracción" (AC-1.1).

### Escenario B — Validación del período (US1)

Con el administrador, probar y comprobar que la extracción no comienza:

| Inicio | Fin | Esperado | CA |
|--------|-----|----------|----|
| 15/11/2026 | 01/11/2026 | "La fecha de inicio no puede ser posterior a la fecha de finalización", con las fechas conservadas | AC-1.3 |
| (vacío) o 31/02/2026 | 15/11/2026 | "Ingresá una fecha válida (dd/mm/aaaa)" junto al campo | AC-1.4 |
| 01/11/2026 | una fecha posterior a hoy | "La fecha de finalización no puede ser posterior a hoy" | AC-1.5 |
| 01/01/2026 | 01/01/2027 | "El período no puede superar los 12 meses" | AC-1.6 |
| 01/01/2026 | 31/12/2026 | La extracción comienza (con fin no posterior a hoy) | AC-1.6 |

### Escenario C — Recorrido completo (US1, US5) · escenario `normal`

1. Extraer del 01/11/2026 al 15/11/2026. **Esperado**: "Extracción en curso", el período y "Identificando los sorteos del período…"; luego "N de M sorteos procesados", que avanza solo (AC-1.2).
2. Recargar la página y volver a abrir la pantalla de extracciones. **Esperado**: el mismo avance y ningún formulario para iniciar otra (AC-1.11).
3. Al terminar. **Esperado**: 5 sorteos identificados, incluidos el 3422 y el 3426; los cuatro estados suman 5; fuentes utilizadas con sus sorteos aportados (AC-1.7, AC-1.8, AC-2.1). Resultado "Extracción finalizada" o "con advertencias" según los estados, con la lista de sorteos a revisar (AC-1.9).
4. Abrir el detalle de un sorteo. **Esperado**: cada fuente con su resultado, dirección y fecha y hora; cada dato con sus fuentes; el enlace "Ver extracto oficial (Lotería de Santa Fe)" (AC-1.12, AC-1.13, AC-4.6, AC-4.8).
5. Pulsar "Descargar CSV" dos veces. **Esperado**: el nombre incluye 2026-11-01 y 2026-11-15; los dos archivos son idénticos (AC-5.1, AC-5.10).
6. Abrir el archivo (§4). **Esperado**: acentos correctos en "Tradicional – Primer Sorteo", encabezados de [contracts/csv.md](contracts/csv.md), fechas `2026-11-15`, importes `1100000000.00`, sin columna de precio del cartón, sin filas repetidas, cada sorteo con el mismo estado que en la pantalla y procedencia con fuente, dirección y fecha y hora (AC-5.2 a AC-5.6).
7. Iniciar sesión con otro administrador y abrir la extracción desde "Extracciones anteriores". **Esperado**: el listado muestra quién la ejecutó, cuándo, el período y el estado; el resumen, el detalle y un archivo idéntico al del paso 5 (AC-1.14, AC-1.15).

### Escenario D — Período sin sorteos, huecos y cobertura (US1)

1. Escenario `normal`, período sin sorteos en las páginas de prueba. **Esperado**: "No se identificaron sorteos en el período consultado" y sin botón de descarga (AC-1.10).
2. Escenario `fallas`, donde ninguna fuente informa el 3423. **Esperado**: el 3423 "No recuperado" con "Ninguna fuente informa este número de sorteo" y el hueco advertido en el resumen (AC-1.16).
3. Escenario `normal`, del 01/06/2014 al 31/12/2014. **Esperado**: "Las fuentes no cubren el período anterior al 17/12/2014" y solo los sorteos cubiertos (AC-1.17).

### Escenario E — Fallas de las fuentes (US2) · escenario `fallas`

| Situación preparada | Esperado en el detalle o el resumen | CA |
|---------------------|-------------------------------------|----|
| Una fuente responde 500 o no responde | "No disponible" (en F2: "No disponible o no encontrado") y los datos de las demás | AC-2.2, AC-2.3 |
| F1 o F3 responden 404 | "No encontrado" | AC-2.3 |
| Página con otra estructura | "Estructura no reconocida" y ningún dato tomado de ella | AC-2.4 |
| La misma fuente irreconocible en todos los sorteos | "Requiere mantenimiento" en el resumen | AC-2.10 |
| Página sin la tabla de una modalidad | "Incompleto" y qué falta | AC-2.5 |
| Sorteo anterior a 2787 (F3) | F3 "Fuera de cobertura", no contado como falla | AC-2.6 |
| Las tres fuentes fallan para un sorteo | "No recuperado", con el motivo de cada fuente, sin números ni importes; en el archivo, una sola fila | AC-2.7, AC-5.8 |
| Demora mayor a 10 s | "No disponible" y el avance sigue | AC-2.8 |
| Respuesta 403 o página anti-robots | "No disponible" | AC-2.9 |

### Escenario F — Normalización (US3) · escenario `normalizacion`

| Situación preparada | Esperado | CA |
|---------------------|----------|----|
| Rótulos "SORTEO TRADICIONAL", "TRADICIONAL", "Tradicional Primer Sorteo" y "LA SEGUNDA DEL QUINI 6 REVANCHA" | "Tradicional – Primer Sorteo" y "Revancha" | AC-3.1 |
| "02 01 39 13 10 38" frente a "01 - 02 - 10 - 13 - 38 - 39" | 01, 02, 10, 13, 38, 39, sin discrepancia | AC-3.2 |
| Premio Extra | Sin números propios en el archivo; con premios | AC-3.3 |
| "Vacante · 1.100.000.000" | 0 ganadores, pozo $ 1.100.000.000,00, importe individual "No corresponde", "Vacante" | AC-3.4 |
| 18 ganadores · 3.013.912 | Importe individual $ 3.013.912,00, pozo "No disponible", "Con ganadores" | AC-3.5, AC-3.6 |
| Ganadores ausentes en todas | Ganadores e importe "No disponible", "Pendiente" | AC-3.7 |
| "494,443,71" | "No disponible", observación con el texto original, sorteo no "Recuperado" | AC-3.8 |
| Número repetido, fuera de rango o cinco números | Números no usados y observación con el motivo | AC-3.9 |
| Siempre Sale 5 aciertos, 17 ganadores | Así en la categoría ganadora | AC-3.10 |
| Sorteo anterior al 18/06/2024 | "Reglas del período no verificadas" | AC-3.11 |
| Modalidad ausente en todas | "No informada por las fuentes" y sorteo no "Recuperado" | AC-3.12 |
| Premio Extra con números que no coinciden | Observación de AC-3.13 | AC-3.13 |
| 0 ganadores con "0,00" | Importe individual "No corresponde" | AC-3.14 |
| F1 con pozo de Premio Extra "55 millones de pesos" | Pozo $ 55.000.000,00 | RN-17 |
| Una categoría vacante, una con ganadores sin importe y una sin información | En el archivo se distinguen "No corresponde", "No disponible" y "Sin determinar"; ninguna celda vacía como cero | AC-5.7 |
| Texto de una fuente que empieza con "=" | En la planilla se ve como texto | AC-5.9 |

### Escenario G — Discrepancias (US4) · escenario `discrepancias`

| Situación preparada | Esperado | CA |
|---------------------|----------|----|
| 5.015 frente a 5.547,85 | "Con inconsistencias", ambos valores con su fuente, "Sin determinar" y la columna `discrepancias` con los dos | AC-4.1 |
| Vacante en una fuente y la categoría ausente en otra | Discrepancia "Omisión" | AC-4.2 |
| Pozo de una categoría con ganadores | Sin discrepancia | AC-4.3 |
| Fechas distintas para el mismo número | "Con inconsistencias" y las dos fechas | AC-4.4 |
| 12.060 frente a 12.060,13 | "Diferencia de centavos o redondeo", sin elegir valor | AC-4.5 |
| Números en una fuente y premios en otra | "Combina fuentes", cada dato con su fuente; puede quedar "Recuperado" | AC-4.7 |
| Un dato informado por una sola fuente | "Sin corroborar" en pantalla y en el archivo | AC-4.8 |

### Escenario I — Ajustes de pantalla (D-22 a D-25 y D-27) · escenario `normal`

1. En «Extracción histórica de sorteos», pulsar el ícono de calendario de "Fecha de inicio". **Esperado**: se despliega un calendario sin días posteriores a hoy. Hacer clic en el campo y escribir 01112026 con el teclado numérico. **Esperado**: el calendario no se abre solo y el campo muestra 01/11/2026 (AC-1.20, D-27).
2. Extraer del 01/11/2026 al 15/11/2026 y abrir el detalle del 3426. **Esperado**: no figuran "Se acumula según la fuente", "Importe trasladado", la columna "Fuentes" ni las fuentes junto a la fecha y los números; las fuentes solo están en "Fuentes consultadas" y el CSV es versión 3.0, sin las columnas `se_acumula_segun_fuente` e `importe_trasladado` (D-22, D-23).
3. En "Extracciones anteriores", la primera columna se llama "Fecha". Abrir el menú ⋮ de la extracción terminada, elegir "Eliminar" y luego "Cancelar". **Esperado**: nada cambia. Repetir y confirmar con "Eliminar". **Esperado**: "Extracción eliminada", la fila desaparece y su página responde "La página que buscás no existe" (AC-1.18). Mientras una extracción está en curso, su fila no muestra el menú (AC-1.19).

### Escenario J — Barra de progreso (D-26) · escenario `normal`

1. Extraer del 01/11/2026 al 15/11/2026 con JavaScript habilitado. **Esperado**: mientras dice "Identificando los sorteos del período…" no hay barra; después, junto a "N de 5 sorteos procesados" se ve una barra que se llena en esa proporción y avanza cada 5 s sin recargar; al terminar se muestra el resumen (AC-1.21).
2. Repetir con JavaScript deshabilitado. **Esperado**: la barra y el texto avanzan al recargar.

### Escenario H — Sin ingesta (US6)

1. Antes de extraer, crear y publicar a mano el concurso 3425 con valores distintos de los de las fuentes de prueba ([001] US2) y registrar una jugada de Ana en el 3424 antes de publicar sus números. Comprobar que el 3426 no existe en la aplicación.
2. Extraer del 01/11/2026 al 15/11/2026.
3. **Esperado**: la consulta pública muestra "No hay información del concurso N.º 3426" y el listado de concursos no lo incluye (AC-6.3); el 3425 muestra los mismos valores, sin "Corregido el …" ni "Información en revisión", y su historial no tiene entradas nuevas (AC-6.4); la jugada de Ana y su comparación no cambian (AC-6.5).

## 6. Escenarios con las fuentes reales

Con las variables de fuentes vacías y conexión a internet.

1. **SC-003**: extraer un período reciente con al menos 10 sorteos. Para 10 sorteos, comparar cada valor del archivo con la página citada en `procedencia`. **Esperado**: 100 % de coincidencia.
2. **SC-007**: medir con un reloj una extracción de un mes (menos de 2 min hasta poder descargar) y una de 12 meses (menos de 10 min).
3. **SC-006**: pedir a 3 administradores que, sin ayuda, digan si una extracción terminó con advertencias y qué sorteos requieren revisión. **Esperado**: los 3 en menos de 1 minuto.
4. **SC-008**: abrir los archivos en dos planillas distintas. **Esperado**: acentos correctos y ninguna fórmula ejecutada.
5. **NFR-002 y NFR-003**: recorrer la pantalla, la página de la extracción y el detalle a 360 px de ancho, sin desplazamiento horizontal, y comprobar que cada estado se lee como texto además del color.
