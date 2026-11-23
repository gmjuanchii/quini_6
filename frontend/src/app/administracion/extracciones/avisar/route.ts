/**
 * Aviso y vuelta al listado ([003] FR-043, AC-10.1, R-31): cuando una página de la Extracción
 * histórica no puede mostrarse (la extracción ya no existe o sigue en curso), la vista HTML de
 * Django agrega un aviso y vuelve al listado. Una página de Next.js no puede agregar el aviso
 * mientras se dibuja: la estructura común lee los avisos al mismo tiempo y podría consumirlo en la
 * respuesta que se descarta. Por eso la página redirige aquí, que lo agrega y luego redirige (303).
 *
 * Solo admite las claves de esta lista (nunca texto libre) y siempre vuelve al listado.
 */
import type { NextRequest } from "next/server";

import { redireccionRelativa } from "@/lib/redireccion";

import { apiServidor } from "@/api/servidor";

const LISTADO = "/administracion/extracciones/";

/** Avisos permitidos: clave del catálogo → tipo (RN-09). */
const AVISOS = {
  "ext.no_existe": "error",
  "ext.eliminar_en_curso": "error",
} as const;

export async function GET(pedido: NextRequest) {
  const clave = pedido.nextUrl.searchParams.get("clave") ?? "";
  if (Object.hasOwn(AVISOS, clave)) {
    const api = await apiServidor();
    const tipo = AVISOS[clave as keyof typeof AVISOS];
    await api.POST("/api/v1/avisos/", { body: { tipo, clave, valores: {} } });
  }
  return redireccionRelativa(LISTADO);
}
