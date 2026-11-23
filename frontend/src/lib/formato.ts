/**
 * Formatos es-AR ([003] contracts/formatos.md, Const. VII). Mismas reglas que los filtros de Django
 * (`quini6/templatetags/formato_ar.py`); la prueba compartida es `contratos/formatos-casos.json`.
 *
 * Los importes y porcentajes llegan de la API como **cadena decimal** y se formatean desde la
 * cadena, nunca con números de punto flotante. Fechas y horas siempre en Buenos Aires (CHK008).
 */
export const ZONA_HORARIA = "America/Argentina/Buenos_Aires";

type Vacio = null | undefined | "";

function esVacio(valor: unknown): valor is Vacio {
  return valor === null || valor === undefined || valor === "";
}

/** `"2026-11-21"` → `21/11/2026`. Una fecha y hora ISO se lleva antes a Buenos Aires. */
export function fecha(valor: string | Vacio): string {
  if (esVacio(valor)) return "";
  const soloFecha = /^(\d{4})-(\d{2})-(\d{2})$/.exec(valor);
  if (soloFecha) return `${soloFecha[3]}/${soloFecha[2]}/${soloFecha[1]}`;
  return partesLocales(valor).fecha;
}

/** `"2026-11-21T12:15:00-03:00"` → `21/11/2026 12:15` (24 h, sin segundos, en Buenos Aires). */
export function fechaHora(valor: string | Vacio): string {
  if (esVacio(valor)) return "";
  if (/^\d{4}-\d{2}-\d{2}$/.test(valor)) return fecha(valor);
  const { fecha: f, hora } = partesLocales(valor);
  return `${f} ${hora}`;
}

const formateador = new Intl.DateTimeFormat("es-AR", {
  timeZone: ZONA_HORARIA,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

function partesLocales(valor: string): { fecha: string; hora: string } {
  const instante = new Date(valor);
  if (Number.isNaN(instante.getTime())) throw new Error(`Fecha y hora no válida: ${valor}`);
  const partes = Object.fromEntries(
    formateador.formatToParts(instante).map((p) => [p.type, p.value]),
  ) as Record<string, string>;
  return {
    fecha: `${partes.day}/${partes.month}/${partes.year}`,
    hora: `${partes.hour}:${partes.minute}`,
  };
}

/** Separa miles con punto: `"1234567"` → `1.234.567`. */
function miles(entero: string): string {
  return entero.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/**
 * Redondea una cadena decimal a 2 decimales con ROUND_HALF_UP (como `Decimal.quantize` de Python:
 * la mitad se aleja del cero), sin pasar por `number`.
 */
function dosDecimales(valor: string): { negativo: boolean; entero: string; decimales: string } {
  const m = /^([+-]?)(\d*)(?:\.(\d*))?$/.exec(valor.trim());
  if (!m || (m[2] === "" && (m[3] ?? "") === "")) throw new Error(`Decimal no válido: ${valor}`);
  const fraccion = (m[3] ?? "").padEnd(3, "0");
  let centavos = BigInt((m[2] || "0") + fraccion.slice(0, 2));
  if (Number(fraccion[2]) >= 5) centavos += 1n;
  const digitos = centavos.toString().padStart(3, "0");
  return {
    negativo: m[1] === "-" && centavos !== 0n,
    entero: digitos.slice(0, -2),
    decimales: digitos.slice(-2),
  };
}

function decimalAr(valor: string): string {
  const { negativo, entero, decimales } = dosDecimales(valor);
  return `${negativo ? "-" : ""}${miles(entero)},${decimales}`;
}

/** Importe desde cadena decimal: `"1500.5"` → `$ 1.500,50`; `"-10.00"` → `$ -10,00`. */
export function pesos(valor: string | Vacio): string {
  if (esVacio(valor)) return "";
  return `$ ${decimalAr(valor)}`;
}

/** Porcentaje desde cadena decimal: `"12.345"` → `12,35 %` (ROUND_HALF_UP, [001] RN-43). */
export function porcentaje(valor: string | Vacio): string {
  if (esVacio(valor)) return "";
  return `${decimalAr(valor)} %`;
}

/** Bolilla con dos dígitos: `7` → `07`. */
export function dosDigitos(valor: number | string | Vacio): string {
  if (esVacio(valor)) return "";
  return String(valor).padStart(2, "0");
}

/** Cantidad entera con separador de miles: `1500` → `1.500`. El número de sorteo no la usa. */
export function cantidad(valor: number | string | Vacio): string {
  if (esVacio(valor)) return "";
  const texto = String(valor);
  if (!/^-?\d+$/.test(texto)) throw new Error(`Cantidad no válida: ${texto}`);
  return texto.startsWith("-") ? `-${miles(texto.slice(1))}` : miles(texto);
}
