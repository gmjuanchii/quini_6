# Guía de puesta en marcha y validación: QUINI_6 — MVP v0

**Plan**: [plan.md](plan.md) | **Rutas**: [contracts/rutas.md](contracts/rutas.md) | **Mensajes**: [contracts/mensajes.md](contracts/mensajes.md)

Esta guía sirve para levantar la aplicación en una computadora local y comprobar, **desde la interfaz**, que el MVP cumple sus criterios de aceptación (Const. VI). No contiene código de implementación.

---

## 1. Requisitos previos

- Python 3.12.
- Git (recomendado; el proyecto todavía no es un repositorio).
- Un navegador actual. Para NFR-002, también un teléfono o el modo de dispositivo del navegador con 360 px de ancho.
- Opcional, solo para el paso 4: PostgreSQL 16.

## 2. Preparación (PowerShell, desde la raíz del proyecto)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env        # completar SECRET_KEY; por defecto usa SQLite
python manage.py migrate
python manage.py runserver
```

Resultado esperado: la aplicación responde en `http://127.0.0.1:8000/` y muestra "Todavía no hay resultados publicados" (AC-1.13).

### Cuentas para la verificación

1. En la aplicación, crear tres cuentas desde "Crear cuenta": `admin@prueba.local`, `ana@prueba.local` y `beto@prueba.local`.
2. En otra terminal, otorgar el permiso de administrador ([contracts/comandos.md](contracts/comandos.md)):

```powershell
python manage.py otorgar_admin admin@prueba.local
```

## 3. Pruebas automatizadas

```powershell
pytest                       # suite completa
pytest tests/unit            # reglas de dominio: ejemplos de referencia y AC-5.14 a AC-5.32
pytest tests/integration     # recorridos, matriz de acceso, publicación y correcciones
ruff check .
```

Resultado esperado: todas las pruebas pasan y `ruff` no informa errores. Las pruebas automatizadas complementan la verificación manual de la sección 5, pero no la reemplazan.

## 4. (Opcional, antes de publicar a producción) Suite contra PostgreSQL

Definir las variables de conexión a PostgreSQL en `.env` (ver `.env.example`) y ejecutar `pytest` de nuevo. Resultado esperado: los mismos resultados que con SQLite (research R-03).

---

## 5. Escenarios de validación funcional

Cada escenario indica los criterios que comprueba. **Importante**: según RN-07, las jugadas se registran **antes** de publicar los números del concurso, así que el orden de los pasos importa.

### Escenario A — Consulta pública vacía y sin registro (US1)

1. Sin iniciar sesión, abrir `/resultados/` → se ve "Todavía no hay resultados publicados" y no aparece ningún pedido de inicio de sesión (AC-1.13, FR-001).
2. Abrir `/estadisticas/` → se ve "No hay sorteos publicados de Tradicional – Primer Sorteo en el período seleccionado" y la leyenda descriptiva (AC-6.4, AC-6.9).

### Escenario B — Acceso y permisos (US3, US2; SC-004)

1. Sin sesión, abrir `/mis-jugadas/` → pide iniciar sesión. Al ingresar como Ana, llega a `/mis-jugadas/` y ve "Todavía no registraste jugadas" (AC-3.8, AC-4.13).
2. Con la sesión de Ana, abrir `/administracion/concursos/` → "No tenés permisos para acceder a esta sección" (AC-2.11).
3. Cerrar sesión y usar "Atrás" en el navegador → no se ve información personal y se pide iniciar sesión (AC-3.7).
4. Intentar 5 veces el ingreso de Ana con una contraseña incorrecta → en cada intento se ve "Correo electrónico o contraseña incorrectos". En el sexto intento aparece el aviso de bloqueo con la hora de reintento (AC-3.5, AC-3.6).
5. Intentar registrar otra vez `beto@prueba.local` → no se crea una segunda cuenta y aparece la invitación a iniciar sesión (AC-3.3).

### Escenario C — Crear el concurso y registrar jugadas antes del sorteo (US2, US4)

Con estos datos se reproducen los **ejemplos de referencia** de la spec. Los números son ilustrativos.

1. Como administrador, crear el concurso **N.º 9001** con una fecha pasada posterior al 18/06/2024 y las cinco modalidades. En `/resultados/` aparece con "Resultados pendientes" (AC-2.1, AC-1.2).
2. Intentar crear otra vez el N.º 9001 → "El concurso N.º 9001 ya existe" (AC-2.2).
3. Crear de la misma forma los concursos **N.º 9002** y **N.º 9003**.
4. Como Ana, desde el detalle público del concurso 9001, elegir "Registrar una jugada" → el formulario se abre con el concurso preseleccionado y muestra sus cinco modalidades (AC-3.9, AC-4.6).
5. En el formulario, comprobar:
   - con 4 números elegidos → "Te faltan 2 números" (AC-4.2);
   - al intentar elegir un séptimo → "La jugada admite exactamente seis números" (AC-4.3);
   - al escribir `46` o `abc` → se rechaza con el rango permitido (AC-4.4);
   - al escribir dos veces `07` → "El 07 ya está en tu jugada" (AC-4.5);
   - con el costo vacío → "Ingresá el costo de tu jugada" (AC-4.16).
6. Registrar estas jugadas, todas con costo `1500,50`:
   - concurso 9001: `03 08 14 21 32 40` (Ejemplo 1);
   - concurso 9002: `01 07 12 19 28 44` (Ejemplo 2);
   - concurso 9003: `02 09 16 23 31 42` (Ejemplo 3).

   Resultado esperado en cada caso: "Jugada registrada". El historial muestra "$ 1.500,50", los números con dos dígitos y el estado "Resultado pendiente" (AC-4.1, AC-4.9, AC-4.16).
7. Registrar otra vez la jugada del Ejemplo 1 en el concurso 9001 → aparece la advertencia de duplicado. Al confirmar, el historial muestra dos jugadas separadas (AC-4.14). Eliminar la copia con confirmación → "Jugada eliminada" (AC-4.11).
8. Como Beto, abrir la dirección del detalle de una jugada de Ana → "La jugada no existe o no está disponible" (AC-4.12).

### Escenario D — Carga, validación y publicación (US2)

1. En el concurso 9001, cargar los números del Primer Sorteo **sin fuente** y guardar → queda en "Borrador". El público ve "Pendiente de validación", nunca los números (AC-2.4, D-12).
2. Intentar publicar → se informa que falta la fuente (AC-2.5).
3. Marcar como "Observado" con un motivo → la publicación queda bloqueada. Resolver la observación → vuelve a "Borrador" (AC-2.8).
4. Completar la fuente, marcar la casilla de cotejo y publicar → el público ve los números y la fuente, y el concurso figura como "Incompleto" (AC-2.6, AC-1.5, AC-1.15).
5. Como Ana, intentar editar la jugada del concurso 9001 → no aparecen las opciones de editar ni de eliminar, sino el aviso de jugada fija. Si se usa la dirección directa de edición, aparece el mismo aviso (AC-4.17). Intentar registrar una jugada nueva en el 9001 → "Ya no se pueden registrar jugadas para este concurso porque sus resultados fueron publicados" (AC-4.8).
6. Cargar y publicar el resto de las extracciones de los tres concursos con los números de los ejemplos de referencia de la spec. Al cargar La Segunda con los mismos números que otra modalidad, aparece una advertencia que hay que confirmar (AC-2.9).
7. Publicar los premios de las modalidades del concurso 9001, y dejar una categoría con ganadores sin importe individual → el público ve "Información de premios pendiente de publicación" en lugar de ese importe (AC-1.7, AC-1.9). Con todo publicado, el concurso figura como "Completo" (AC-1.6).
8. Antes de publicar la Revancha de un concurso (dejándola en Borrador), abrir su detalle público → Premio Extra muestra "Pendiente de validación" y ningún conjunto de números; si sus premios ya están publicados, se ven igual (AC-1.14).

### Escenario E — Comparación de jugadas (US5; SC-005)

Como Ana, abrir el detalle de cada jugada y compararlo con la tabla de la spec ("Ejemplos de referencia para la comparación de jugadas").

| Jugada | Lo que debe verse |
|--------|-------------------|
| Ejemplo 1 | Primer Sorteo: "Con premio — Primer Premio". La Segunda: "Con premio — Segundo Premio". Revancha: "4 aciertos — Sin premio". Premio Extra: "Excluida del Premio Extra: obtuvo 6 aciertos en Tradicional – Primer Sorteo" (AC-5.14, AC-5.15, AC-5.20, AC-5.25, AC-5.32). |
| Ejemplo 2 | Primer Sorteo: "Con premio — Tercer Premio". Revancha: "Con premio — Premio Revancha". Premio Extra: excluida por Revancha (AC-5.16, AC-5.19). |
| Ejemplo 3 | Ninguna extracción con 6 aciertos. Premio Extra: "Participa — 6 aciertos — Con premio — Premio Extra (6 aciertos)", con un conjunto de 13 números (AC-5.24, AC-5.26). |

Siempre Sale (con la jugada del Ejemplo 2, que tiene 5 aciertos):

- sin la categoría ganadora publicada → "Premio pendiente de determinación" (AC-5.23);
- con una categoría ganadora de 5 → "Con premio — Siempre Sale (5 aciertos)" (AC-5.22);
- con una categoría ganadora de 4 → "Premio pendiente de determinación" con el aviso de RN-52 e (AC-5.30).

En cada caso, comprobar que el importe aparece solo si se publicó. Si no, aparece la leyenda de premios pendientes (AC-5.3, AC-5.7). En el historial, cada jugada muestra su estado resumido (AC-5.13, P-04).

### Escenario F — Corrección con trazabilidad (US7; SC-008)

1. Como administrador, marcar "En revisión" el Primer Sorteo del concurso 9003 → el público ve los números con "Información en revisión". Ana ve "Información en revisión: el resultado podría cambiar" (AC-7.1, AC-5.12).
2. Iniciar una corrección, cambiar un número e indicar motivo y fuente, **sin publicarla** → el público sigue viendo los valores anteriores (AC-7.2).
3. Publicar la corrección → el público ve el valor nuevo y "Corregido el {fecha}". Si la comparación de Ana cambió, muestra "Actualizado por corrección del resultado oficial el {fecha}". Las estadísticas reflejan el valor nuevo (AC-7.4, AC-5.9, AC-6.11).
4. Abrir el historial del concurso → se ven el valor anterior, el valor nuevo, la fecha, el autor, el motivo y la fuente (AC-7.3).

### Escenario G — Estadísticas (US6; SC-006)

1. Abrir `/estadisticas/` → aparecen los 46 números en una tabla y en un gráfico, con la cantidad de sorteos considerados y las fechas del primero y del último (AC-6.1). Los números que nunca salieron aparecen con 0 (AC-6.5).
2. Cambiar a La Segunda y luego definir un período → los valores se recalculan (AC-6.2, AC-6.3). Contar a mano las apariciones de tres números y comparar (SC-006).
3. Consultar el número `14` → se ven su cantidad de apariciones y su porcentaje con dos decimales en formato argentino (AC-6.6).
4. Poner una fecha desde posterior a la fecha hasta → aparece el mensaje de corrección y debajo se siguen viendo exactamente las mismas estadísticas que antes: misma modalidad, mismo período, misma cantidad de sorteos y mismas frecuencias (AC-6.8).5. Comprobar que Premio Extra no se ofrece como modalidad (RN-46).
6. Crear un concurso sin publicar dentro del período → aparece el aviso "El período incluye 1 concursos sin información disponible para esta modalidad" (AC-6.7).

### Escenario H — Calidad transversal

- Recorrer todas las pantallas con 360 px de ancho, sin desplazamiento horizontal (NFR-002).
- No hay textos en inglés. Las fechas tienen formato `dd/mm/aaaa`, los importes `$ 1.234,56` y los números dos dígitos (NFR-001).
- Los estados se distinguen por su texto y no solo por el color (NFR-003).

---

## 6. Datos de prueba

Los datos de los ejemplos de referencia existen como *fixtures* de `pytest` (`tests/`) para las pruebas automatizadas. Para la verificación manual se cargan **desde la interfaz de administración**, como indica esta guía, lo que además ejercita el flujo de US2. No hay ningún mecanismo de importación (FR-010).
