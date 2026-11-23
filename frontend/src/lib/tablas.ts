/**
 * Tablas ordenables y paginadas ([003] AC-7.5, AC-9.1, AC-9.2, RN-07): las mismas reglas que
 * `quini6/tablas.py`. Encabezados y paginación son **enlaces** con parámetros en la dirección
 * (funcionan sin scripts, NFR-007) y el servidor de Django decide el orden en cada pedido.
 */
export type Parametros = Record<string, string | undefined>;

/** `?a=1&b=2` con `cambios`; un cambio `null`, `undefined` o `""` quita el parámetro. Nunca
 * conserva `_interfaz` (R-20). */
export function conParametros(
  parametros: Parametros,
  cambios: Record<string, string | number | null | undefined> = {},
): string {
  const pares: [string, string][] = [];
  for (const [k, v] of Object.entries(parametros)) {
    if (k in cambios || k === "_interfaz" || v === undefined || v === "") continue;
    pares.push([k, v]);
  }
  for (const [k, v] of Object.entries(cambios)) {
    if (v === null || v === undefined || v === "") continue;
    pares.push([k, String(v)]);
  }
  return pares.length ? `?${new URLSearchParams(pares).toString()}` : "?";
}

export type Sentido = "ascending" | "descending";

export type Columna = {
  id: string;
  texto: string;
  ordenable?: boolean;
  alineacion?: "derecha";
};

export type Encabezado = Columna & { href?: string; sentido?: Sentido };

/** La columna ordenada ofrece el sentido contrario; las demás empiezan en ascendente. Cambiar el
 * orden vuelve a la primera página y conserva los demás parámetros. */
export function encabezados(
  parametros: Parametros,
  columnas: Columna[],
  orden: string,
): Encabezado[] {
  const actual = orden.replace(/^-/, "");
  const descendente = orden.startsWith("-");
  return columnas.map((c) => {
    if (!c.ordenable) return { ...c };
    let sentido: Sentido | undefined;
    let siguiente = c.id;
    if (c.id === actual) {
      sentido = descendente ? "descending" : "ascending";
      siguiente = descendente ? c.id : `-${c.id}`;
    }
    return { ...c, sentido, href: conParametros(parametros, { orden: siguiente, pagina: null }) };
  });
}
