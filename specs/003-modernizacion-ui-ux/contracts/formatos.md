# Contrato de formatos es-AR

**Plan**: [../plan.md](../plan.md) | **Research**: R-16, R-32 (CHK007, CHK008) | **Constitución**: VII

Reglas únicas de presentación que deben cumplir **las dos** implementaciones: los filtros de Django (`quini6/templatetags/formato_ar.py`, que delegan en `dominio/importes.py` y `dominio/numeros.py`, sin cambios) y `frontend/src/lib/formato.ts` (Etapa 2). La API entrega los valores en formato técnico (ISO 8601, cadena decimal, enteros) y la interfaz los formatea.

La tabla de casos es la prueba compartida: `tests/unit/test_formatos_contrato.py` y `frontend/src/lib/formato.test.ts` leen el mismo archivo `contratos/formatos-casos.json`, generado desde esta tabla, y exigen la misma salida.

## Reglas

| Dato | Entrada de la API | Salida | Reglas |
|------|-------------------|--------|--------|
| Fecha | `"2026-11-21"` | `21/11/2026` | `dd/mm/aaaa`, siempre con ceros a la izquierda |
| Fecha y hora | `"2026-11-21T12:15:00-03:00"` | `21/11/2026 12:15` | Se convierte a `America/Argentina/Buenos_Aires` antes de formatear, sea cual sea la zona del servidor o del navegador; 24 h, sin segundos |
| Importe | `"1234567.5"` o `"1234567.50"` | `$ 1.234.567,50` | Se formatea **desde la cadena**, nunca convirtiendo a número de punto flotante; separador de miles `.`, decimal `,`, siempre dos decimales; `$` + espacio |
| Importe negativo | `"-10.00"` | `$ -10,00` | Comportamiento vigente de `formatear_pesos` de [001] (registrado el 21/11/2026, T031); Next.js lo copia |
| Porcentaje | `"12.5"` | `12,50 %` | Dos decimales con redondeo `ROUND_HALF_UP` ([001] RN-43); espacio antes de `%` |
| Número de bolilla | `7` | `07` | Siempre dos dígitos (Const. VII) |
| Número de sorteo | `3250` | `3250` | Sin separador de miles (es un identificador) |
| Cantidades | `1500` | `1.500` | Separador de miles `.` |
| Dato desconocido de [002] | `{ "estado": "no_disponible" }` | `No disponible` | Texto del catálogo según el estado; nunca `0` ni vacío |
| Vacío (`null` donde el contrato lo admite) | `null` | (vacío) | Igual que los filtros actuales |

## Casos mínimos de la tabla compartida

| Tipo | Entrada | Salida esperada |
|------|---------|-----------------|
| fecha | `2024-02-29` | `29/02/2024` |
| fecha_hora | `2026-01-01T02:30:00Z` | `31/12/2025 23:30` |
| importe | `0` | `$ 0,00` |
| importe | `1500.5` | `$ 1.500,50` |
| importe | `999999999999.99` | `$ 999.999.999.999,99` |
| importe | `-10.00` | `$ -10,00` |
| porcentaje | `12.345` | `12,35 %` |
| porcentaje | `12.344` | `12,34 %` |
| bolilla | `0` | `00` |
| cantidad | `1000000` | `1.000.000` |
| cantidad | `7` | `7` |

"Hoy" (para atajos de período y fechas máximas) lo calcula siempre Django en `America/Argentina/Buenos_Aires`; Next.js no lo calcula por su cuenta. El proceso de Next.js corre además con `TZ=America/Argentina/Buenos_Aires`.
