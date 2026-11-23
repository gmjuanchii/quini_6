/**
 * Lecturas de Administración de sorteos ([003] contracts/api.md, T207) para las páginas de
 * servidor: `GET /api/v1/admin/sorteos/…` con la sesión de la persona; 401/403 como Django.
 */
import { cookies } from "next/headers";

import { llamarApi } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { verificarRespuesta } from "@/lib/sesion";

export type PanelSorteo = components["schemas"]["PanelSorteo"];
export type SorteoAdmin = components["schemas"]["SorteoAdmin"];
export type BloqueAdmin = components["schemas"]["BloqueAdmin"];

export const BASE = "/administracion/concursos";
export const API = "/api/v1/admin/sorteos";

/** `null` si no existe (la página muestra "Página inexistente", como Django). */
export async function leerAdmin<T>(ruta: string): Promise<T | null> {
  const { response, datos } = await llamarApi("GET", `${API}${ruta}`);
  if (response.status === 404) return null;
  await verificarRespuesta(response);
  if (!response.ok) throw new Error(`La API de administración respondió ${response.status}`);
  return datos as T;
}

export async function tokenCsrf(): Promise<string> {
  return (await cookies()).get("csrftoken")?.value ?? "";
}
