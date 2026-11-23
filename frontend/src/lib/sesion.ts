/**
 * Sesión compartida con Django ([003] R-19, AC-14.1, AC-14.2).
 *
 * Next.js **no decide permisos**: muestra lo que responde Django. `401` → "Ingresar" (de Django
 * mientras no se migre la pantalla 5), `403` → "Sin permisos", `404` → página inexistente.
 *
 * Importante (NFR-007): en Next.js 16, `forbidden()` y `notFound()` lanzados desde una página
 * responden un armazón que solo se completa con scripts. Por eso el acceso por ruta se presenta en
 * `proxy.ts` (403 completo en el HTML); aquí quedan como respaldo, y una pantalla que reciba `404`
 * de una operación propia debe mostrar `<PaginaDeError>` en la misma página (pantallas 3 y 4).
 */
import { headers } from "next/headers";
import { forbidden, notFound, redirect } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { CABECERA_ACCION } from "@/lib/sesion-cabeceras";

export type Sesion = components["schemas"]["Sesion"];
export type Nivel = "P" | "U" | "A";

/** Cabecera que `proxy.ts` agrega a cada pedido con la ruta pedida (nunca la del navegador). */
export const CABECERA_RUTA = "x-quini6-ruta";

export async function rutaActual(): Promise<string> {
  return (await headers()).get(CABECERA_RUTA) ?? "/";
}

export function direccionIngresar(ruta: string): string {
  return `/ingresar/?next=${encodeURIComponent(ruta)}`;
}

/** `GET /api/v1/sesion/` con la cookie de la persona (renueva la sesión como una página de Django,
 * CHK026). Si Django no responde, el error llega a `error.tsx`. */
export async function obtenerSesion(): Promise<Sesion> {
  const api = await apiServidor();
  const { data, response } = await api.GET("/api/v1/sesion/");
  if (!data) throw new Error(`GET /api/v1/sesion/ respondió ${response.status}`);
  return data;
}

/**
 * La página se dibuja como respuesta de una Server Action. Sin scripts, Next.js vuelve a dibujar la
 * página después de la acción; si la sesión venció, la acción ya devolvió el estado "La sesión
 * venció…" con su `pendiente` y la página no debe redirigir a "Ingresar", porque perdería lo
 * escrito ([003] FR-032, NFR-007). No otorga nada: sin sesión, Django no entrega datos.
 */
export async function enRespuestaDeAccion(): Promise<boolean> {
  return (await headers()).get(CABECERA_ACCION) === "1";
}

/**
 * Ante `401`, `403` o `404` de Django, la misma respuesta que daría su vista HTML. Con
 * `continuarEnAccion`, un `401` al dibujar la respuesta de una Server Action no redirige: la lectura
 * sigue sin datos y el formulario informa la sesión vencida (solo en las páginas que pueden dibujar
 * su formulario sin esos datos).
 */
export async function verificarRespuesta(
  respuesta: Response,
  { continuarEnAccion = false }: { continuarEnAccion?: boolean } = {},
): Promise<void> {
  if (respuesta.status === 401) {
    if (continuarEnAccion && (await enRespuestaDeAccion())) return;
    redirect(direccionIngresar(await rutaActual()));
  }
  if (respuesta.status === 403) forbidden();
  if (respuesta.status === 404) notFound();
}

/**
 * Para páginas que todavía no consultan una operación propia de su nivel: la sesión debe ser de
 * una persona registrada (U) o administradora (A), según responde Django.
 */
export async function exigirSesion(nivel: Exclude<Nivel, "P">): Promise<Sesion> {
  const sesion = await obtenerSesion();
  if (!sesion.correo) redirect(direccionIngresar(await rutaActual()));
  if (nivel === "A" && !sesion.es_administrador) forbidden();
  return sesion;
}
