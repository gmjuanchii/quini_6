/**
 * Fechas escritas por la persona ([003] AC-4.2, AC-4.5, FR-012, R-07): las mismas reglas que
 * `static/js/ui.js` (Django) y `dominio.periodos.error_de_fecha`. Acepta `dd/mm/aaaa` y
 * `AAAA-MM-DD` ([002] RN-02); el servidor repite toda validación.
 */
const DMA = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
const ISO = /^(\d{4})-(\d{2})-(\d{2})$/;

export type FechaAnalizada =
  | { estado: "vacia" }
  | { estado: "formato" }
  | { estado: "inexistente"; texto: string }
  | { estado: "valida"; iso: string; texto: string };

function dos(n: number): string {
  return String(n).padStart(2, "0");
}

export function analizarFecha(valor: string | null | undefined): FechaAnalizada {
  const texto = (valor ?? "").trim();
  if (!texto) return { estado: "vacia" };
  let dia: number;
  let mes: number;
  let anio: number;
  let m = DMA.exec(texto);
  if (m) {
    [dia, mes, anio] = [Number(m[1]), Number(m[2]), Number(m[3])];
  } else if ((m = ISO.exec(texto))) {
    [anio, mes, dia] = [Number(m[1]), Number(m[2]), Number(m[3])];
  } else {
    return { estado: "formato" };
  }
  const legible = `${dos(dia)}/${dos(mes)}/${anio}`;
  const fecha = new Date(Date.UTC(anio, mes - 1, dia));
  if (
    fecha.getUTCFullYear() !== anio ||
    fecha.getUTCMonth() !== mes - 1 ||
    fecha.getUTCDate() !== dia
  ) {
    return { estado: "inexistente", texto: legible };
  }
  return { estado: "valida", iso: `${anio}-${dos(mes)}-${dos(dia)}`, texto: legible };
}

export function aIso(texto: string | null | undefined): string {
  const f = analizarFecha(texto);
  return f.estado === "valida" ? f.iso : "";
}

export function aDma(valor: string | null | undefined): string {
  const f = analizarFecha(valor);
  return f.estado === "valida" ? f.texto : (valor ?? "");
}

/** AC-4.2: `01012025` → `01/01/2025` (las barras se agregan solas); `AAAA-MM-DD` pegada se
 * convierte a `dd/mm/aaaa`. */
export function enmascarar(valor: string): string {
  if (ISO.test(valor.trim())) return aDma(valor.trim()) || valor.trim();
  const digitos = valor.replace(/\D/g, "").slice(0, 8);
  if (digitos.length > 4)
    return `${digitos.slice(0, 2)}/${digitos.slice(2, 4)}/${digitos.slice(4)}`;
  if (digitos.length > 2) return `${digitos.slice(0, 2)}/${digitos.slice(2)}`;
  return digitos;
}

/** `AAAA-MM-DD` → `Date` local a las 00:00 (para el calendario, sin corrimiento de zona). */
export function isoADate(iso: string | null | undefined): Date | undefined {
  const m = ISO.exec((iso ?? "").trim());
  if (!m) return undefined;
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
}

export function dateAIso(fecha: Date): string {
  return `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}`;
}
