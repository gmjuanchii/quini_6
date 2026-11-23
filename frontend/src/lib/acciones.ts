/**
 * Envoltorio de las Server Actions de Next.js ([003] R-11, R-12, R-18, R-31, CHK011).
 *
 * - Reenvía la `clave_idempotencia` del formulario (generada por el servidor al mostrarlo) como
 *   `Idempotency-Key`: repetir el envío no repite el efecto (FR-031).
 * - `422`/`409` → errores por campo y mensaje general del catálogo (los textos los da Django).
 * - `401` → estado "sesión vencida" con el token `pendiente` de Django, para ir a "Ingresar" sin
 *   perder lo escrito (FR-032, R-12); `403` → "Sin permisos"; `404` → página inexistente.
 * - Éxito → agrega el aviso con `POST /api/v1/avisos/` y redirige: el aviso aparece en la
 *   aplicación de destino, sea Django o Next.js (FR-043).
 */
import { randomUUID } from "node:crypto";

import { revalidatePath } from "next/cache";
import { forbidden, notFound, redirect } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";

import { rutaActual } from "./sesion";

export type NuevoAviso = components["schemas"]["NuevoAviso"];

export { ESTADO_INICIAL, type EstadoFormulario } from "./acciones-estado";
import type { EstadoFormulario } from "./acciones-estado";

export type Problema = {
  detail?: string;
  errores?: { campo: string; codigo: string; mensaje: string }[];
  pendiente?: string;
  existente?: { id: number; url: string };
};

type Llamada<T> = (
  api: Awaited<ReturnType<typeof apiServidor>>,
  cabeceras: Record<string, string>,
) => Promise<{ response: Response; data?: T; error?: unknown }>;

/** Clave nueva para el campo oculto `clave_idempotencia` de cada formulario mostrado (R-11). */
export function nuevaClaveIdempotencia(): string {
  return randomUUID();
}

export async function ejecutarAccion<T>(
  datos: FormData,
  llamar: Llamada<T>,
  exito: { destino: string | ((datos: T) => string); aviso?: NuevoAviso },
): Promise<EstadoFormulario> {
  const api = await apiServidor();
  const clave = datos.get("clave_idempotencia");
  const cabeceras: Record<string, string> =
    typeof clave === "string" && clave ? { "Idempotency-Key": clave } : {};

  const { response, data, error } = await llamar(api, cabeceras);
  const problema = (error ?? {}) as Problema;

  if (response.ok) {
    if (exito.aviso) await api.POST("/api/v1/avisos/", { body: exito.aviso });
    const destino = typeof exito.destino === "function" ? exito.destino(data as T) : exito.destino;
    // El aviso lo lee la estructura común: se vuelve a dibujar completa en el destino (FR-043).
    revalidatePath("/", "layout");
    redirect(destino);
  }
  if (response.status === 401) {
    return {
      errores: {},
      sesionVencida: { pendiente: problema.pendiente ?? null, siguiente: await rutaActual() },
    };
  }
  if (response.status === 403) forbidden();
  if (response.status === 404) notFound();
  if (response.status === 409 || response.status === 422) {
    const errores: Record<string, string> = {};
    // `campo: ""` = error general del formulario (los `non_field_errors` de Django).
    for (const e of problema.errores ?? []) {
      const campo = e.campo ?? "";
      errores[campo] = errores[campo] ? `${errores[campo]} ${e.mensaje}` : e.mensaje;
    }
    return { errores, general: problema.detail, existente: problema.existente };
  }
  throw new Error(`La API respondió ${response.status}`);
}
