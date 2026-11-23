/**
 * Salir en Next.js ([001] AC-3.8; [003] R-14, R-19, pantalla 5): el formulario "Salir" del
 * encabezado (POST, funciona sin scripts) cierra la sesión de Django con `DELETE /api/v1/sesion/`;
 * la `Set-Cookie` que la borra vuelve al navegador. Luego, 303 a "Resultados", como Django.
 */

import { redireccionRelativa } from "@/lib/redireccion";

import { apiServidor } from "@/api/servidor";

export async function POST() {
  const api = await apiServidor();
  await api.DELETE("/api/v1/sesion/");
  return redireccionRelativa("/resultados/");
}
