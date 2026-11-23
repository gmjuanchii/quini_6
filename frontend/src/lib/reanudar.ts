/**
 * Formulario reanudado ([003] R-12, AC-14.4): cuando "Volver al formulario" de Django envía el token
 * `pendiente` por POST a una página de Next.js, `proxy.ts` lo verifica con
 * `POST /api/v1/formularios/pendiente/` y pasa lo escrito a la página en la cabecera interna
 * `x-quini6-reanudar` (JSON en base64url). La página lo usa como valores iniciales y **no envía
 * nada**: la persona revisa y envía.
 */
import { headers } from "next/headers";

export const CABECERA_REANUDAR = "x-quini6-reanudar";

export type Campos = Record<string, string[]>;

export function codificarCampos(campos: Campos): string {
  return Buffer.from(JSON.stringify(campos), "utf8").toString("base64url");
}

export async function formularioReanudado(): Promise<Campos | null> {
  const valor = (await headers()).get(CABECERA_REANUDAR);
  if (!valor) return null;
  try {
    const campos = JSON.parse(Buffer.from(valor, "base64url").toString("utf8")) as unknown;
    return campos && typeof campos === "object" ? (campos as Campos) : null;
  } catch {
    return null;
  }
}
