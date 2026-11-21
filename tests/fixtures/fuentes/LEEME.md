# Copias de páginas de las fuentes (pruebas de la spec 002)

Copias **recortadas** de páginas reales, relevadas el **19/11/2026** (tarea T006 de
`specs/002-extraccion-historica-csv/tasks.md`), con una consulta cada 2 s por sitio como máximo.
Se quitaron los scripts (salvo el bloque `application/ld+json` de F3), los anuncios, los estilos,
los íconos y los pies de página. La estructura de las partes que leen los intérpretes no se tocó.

Las pruebas nunca consultan internet: usan estas copias con el cliente HTTP falso de
`tests/extraccion_falsos.py`. Los datos **no fueron validados** contra el extracto oficial.

| Copia | Dirección original |
|-------|--------------------|
| `f1/listado.html` | https://www.quini-6-resultados.com.ar/quini6/sorteos-anteriores.aspx |
| `f1/sorteo-3426.html` | https://www.quini-6-resultados.com.ar/quini6/sorteo-3426-del-dia-15-11-2026.htm |
| `f1/sorteo-3427.html` | https://www.quini-6-resultados.com.ar/quini6/sorteo-3427-del-dia-18-11-2026.htm |
| `f2/listado.html` | https://numerosganadores.com.ar/sorteos |
| `f2/sorteo-3426.html` | https://numerosganadores.com.ar/sorteos/3426 |
| `f2/sorteo-3427.html` | https://numerosganadores.com.ar/sorteos/3427 |
| `f2/sorteo-2211.html` | https://numerosganadores.com.ar/sorteos/2211 |
| `f2/sorteo-3398.html` | https://numerosganadores.com.ar/sorteos/3398 |
| `f2/inexistente-500.html` | https://numerosganadores.com.ar/sorteos/9999 (respondió 500) |
| `f3/listado.html` | https://quiniya.com.ar/sorteos |
| `f3/sorteo-3426.html` | https://quiniya.com.ar/sorteos/3426 |
| `f3/sorteo-3427.html` | https://quiniya.com.ar/sorteos/3427 |
| `f3/sorteo-3398.html` | https://quiniya.com.ar/sorteos/3398 (importe "494,443,71") |
| `f3/sorteo-2787.html` | https://quiniya.com.ar/sorteos/2787 (primer sorteo de F3) |

F3 respondió 404 **sin contenido** a https://quiniya.com.ar/sorteos/9999, por eso no hay copia.

Las variantes editadas para provocar casos de las historias están en `f2/variantes/`.
