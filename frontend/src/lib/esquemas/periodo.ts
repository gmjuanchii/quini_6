/**
 * Validación previa del período ([003] FR-012, FR-033, R-13): los textos del catálogo
 * (`fecha.falta_inicio`, `fecha.falta_fin`, `fecha.inexistente`, `gral.fecha_invalida`,
 * `fecha.fin_anterior`, `ext.fin_futura`). Es solo una ayuda: Django repite la validación completa
 * ([002] RN-01 a RN-04) y sus mensajes son los que valen.
 *
 * Función propia en lugar de Zod + React Hook Form (R-24): toda la regla era un único
 * `superRefine` y las dos bibliotecas sumaban entre 16 y 43 kB comprimidos a las pantallas con
 * período.
 */
import { analizarFecha } from "@/lib/fechas";
import { msg } from "@/lib/mensajes";

export type Periodo = { inicio: string; fin: string };
export type ErroresPeriodo = Partial<Record<keyof Periodo, string>>;
export type OpcionesPeriodo = {
  /** Hoy en Buenos Aires (AAAA-MM-DD): la fecha de finalización no puede ser posterior. */
  max?: string;
  finFutura?: boolean;
};

function errorDeFecha(valor: string, faltaClave: "fecha.falta_inicio" | "fecha.falta_fin") {
  const f = analizarFecha(valor);
  if (f.estado === "vacia") return msg(faltaClave);
  if (f.estado === "formato") return msg("gral.fecha_invalida");
  if (f.estado === "inexistente") return msg("fecha.inexistente", { fecha: f.texto });
  return undefined;
}

/** Los errores de cada campo (vacío si el período es válido). */
export function validarPeriodo(
  { inicio, fin }: Periodo,
  { max, finFutura = true }: OpcionesPeriodo = {},
): ErroresPeriodo {
  const errorInicio = errorDeFecha(inicio, "fecha.falta_inicio");
  const errorFin = errorDeFecha(fin, "fecha.falta_fin");
  if (errorInicio || errorFin) {
    return { ...(errorInicio && { inicio: errorInicio }), ...(errorFin && { fin: errorFin }) };
  }
  const a = analizarFecha(inicio);
  const b = analizarFecha(fin);
  if (a.estado !== "valida" || b.estado !== "valida") return {};
  if (b.iso < a.iso) return { fin: msg("fecha.fin_anterior", { fecha: a.texto }) };
  if (finFutura && max && b.iso > max) return { fin: msg("ext.fin_futura") };
  return {};
}
