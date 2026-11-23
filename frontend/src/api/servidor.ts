/**
 * Cliente tipado de la API v1 para el servidor de Next.js ([003] R-17, R-19).
 *
 * Llama a Django por su dirección interna (`QUINI6_API_INTERNA`), reenvía la cookie de la persona,
 * agrega `X-CSRFToken` (de la cookie `csrftoken`) y el `Origin` público, y nunca usa caché
 * (NFR-008, CHK006). En Server Actions, las `Set-Cookie` de Django vuelven al navegador.
 */
import createClient from "openapi-fetch";
import { cookies } from "next/headers";

import { cabeceraCookie, leerSetCookie } from "./cookies";
import type { paths } from "./esquema";

export const API_INTERNA = (process.env.QUINI6_API_INTERNA ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  "",
);
export const ORIGEN_PUBLICO = process.env.QUINI6_ORIGEN_PUBLICO ?? "";

/** Intenta devolver al navegador las cookies que fijó Django (solo posible en Server Actions y
 * manejadores de ruta; en un componente de servidor se ignora, y la renueva `proxy.ts`). */
async function reenviarCookies(respuesta: Response): Promise<void> {
  const lineas = respuesta.headers.getSetCookie();
  if (lineas.length === 0) return;
  const almacen = await cookies();
  for (const linea of lineas) {
    const cookie = leerSetCookie(linea);
    if (!cookie) continue;
    try {
      almacen.set({
        name: cookie.nombre,
        value: cookie.valor,
        maxAge: cookie.maxAge,
        expires: cookie.expires,
        path: cookie.path ?? "/",
        httpOnly: cookie.httpOnly,
        secure: cookie.secure,
        sameSite: cookie.sameSite,
      });
    } catch {
      return; // componente de servidor: no puede escribir cookies
    }
  }
}

export async function apiServidor() {
  const almacen = await cookies();
  const csrf = almacen.get("csrftoken")?.value;
  const cabeceras: Record<string, string> = { cookie: cabeceraCookie(almacen.getAll()) };
  if (csrf) cabeceras["X-CSRFToken"] = csrf;
  if (ORIGEN_PUBLICO) cabeceras.Origin = ORIGEN_PUBLICO;

  return createClient<paths>({
    baseUrl: API_INTERNA,
    headers: cabeceras,
    fetch: async (pedido: Request) => {
      // El cuerpo se envía completo, con `Content-Length`: Django (WSGI) no lee cuerpos enviados
      // por partes (`Transfer-Encoding: chunked`), que es lo que haría `fetch(pedido)` en Next.js.
      const cuerpo = ["GET", "HEAD"].includes(pedido.method)
        ? undefined
        : await pedido.arrayBuffer();
      const respuesta = await fetch(pedido.url, {
        method: pedido.method,
        headers: pedido.headers,
        body: cuerpo && cuerpo.byteLength > 0 ? cuerpo : undefined,
        cache: "no-store",
      });
      await reenviarCookies(respuesta);
      return respuesta;
    },
  });
}

/**
 * Llamada a una operación de la API por su ruta (sin tipos), con la misma sesión, CSRF, origen y
 * reenvío de cookies que `apiServidor()`. La usan las Server Actions de Administración de sorteos,
 * cuyos formularios se describen campo por campo desde Django (contracts/api.md, T207).
 */
export async function llamarApi(
  metodo: "GET" | "POST" | "PUT" | "DELETE",
  ruta: string,
  cuerpo?: unknown,
  extra: Record<string, string> = {},
): Promise<{ response: Response; datos: unknown }> {
  const almacen = await cookies();
  const csrf = almacen.get("csrftoken")?.value;
  const cabeceras: Record<string, string> = { cookie: cabeceraCookie(almacen.getAll()), ...extra };
  if (csrf) cabeceras["X-CSRFToken"] = csrf;
  if (ORIGEN_PUBLICO) cabeceras.Origin = ORIGEN_PUBLICO;
  if (cuerpo !== undefined) cabeceras["Content-Type"] = "application/json";
  const respuesta = await fetch(`${API_INTERNA}${ruta}`, {
    method: metodo,
    headers: cabeceras,
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    cache: "no-store",
  });
  await reenviarCookies(respuesta);
  const tipo = respuesta.headers.get("content-type") ?? "";
  const datos = tipo.includes("json") ? await respuesta.json() : null;
  return { response: respuesta, datos };
}
