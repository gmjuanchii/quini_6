# Contrato de comandos de gestión: Extracción histórica de sorteos

**Plan**: [../plan.md](../plan.md) | **Decisión**: [../research.md](../research.md) R-01 | **Comandos de [001]**: [contracts/comandos.md](../../001-quini6-mvp/contracts/comandos.md)

El comando se ejecuta solo en el servidor, con acceso de operador. No tiene una interfaz web equivalente: las extracciones se inician desde la pantalla de administración (FR-001).

| Comando | Argumentos | Efecto | Salida | Requisito |
|---------|------------|--------|--------|-----------|
| `python manage.py procesar_extracciones` | `--una-vez` (opcional): procesa las extracciones en curso que haya y termina. Sin el argumento, queda esperando nuevas extracciones (revisa cada 2 s). | Toma las extracciones en curso por orden de inicio y las procesa de a una: identificación, consultas, normalización, consolidación, clasificación, resumen y CSV. Reanuda una extracción interrumpida (I-07). Solo escribe en las tablas de `extracciones` (RN-41). | Una línea por extracción iniciada y terminada, con su número y su resultado global. Los errores inesperados de un sorteo se registran y la extracción continúa (NFR-006), según [002] I-09: un intérprete que falla deja su intento "Estructura no reconocida"; cualquier otra falla deja el sorteo "No recuperado" con el motivo "Error inesperado al procesar el sorteo". | FR-003 a FR-015, NFR-005, NFR-006 |

Restricción operativa: debe haber **una sola instancia** en ejecución, para garantizar el ritmo máximo por sitio de NFR-005 ([002] R-01). En producción corre como un servicio del sistema junto a `gunicorn`. En desarrollo se ejecuta en una segunda terminal ([quickstart.md](../quickstart.md)).

Variables de entorno de la feature (solo para el servidor de fuentes de prueba, [002] R-11): `QUINI6_FUENTE_F1_URL`, `QUINI6_FUENTE_F2_URL` y `QUINI6_FUENTE_F3_URL`. Se documentan en `.env.example`, comentadas y sin valor.
