"use server";

/**
 * Server Action de Administración de sorteos ([001] US2, US7; [003] FR-041, pantalla 6): envía lo
 * escrito con los nombres de campo de los formularios de Django (`{campos}`) a la operación de
 * `/api/v1/admin/sorteos/…` indicada. Django valida, autoriza y deja el aviso (FR-043); con errores,
 * devuelve el formulario con lo enviado y sus mensajes, que la pantalla vuelve a mostrar.
 */
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { llamarApi } from "@/api/servidor";
import type { EstadoAdmin } from "./_componentes/estado";

export type Destino = {
  metodo: "POST" | "PUT";
  ruta: string;
  /** Dirección al terminar bien (el panel del sorteo, normalmente). */
  exito: string;
  /** Para crear: el panel del sorteo nuevo (`{numero}` se completa con la respuesta). */
  exitoConNumero?: boolean;
};

type Problema = {
  detail?: string;
  errores?: { campo: string; mensaje: string }[];
  formulario?: EstadoAdmin["formulario"];
  existente?: { id: number; url: string };
  pendiente?: string;
};

/** `FormData` → `{campos}`: los campos repetidos (casillas múltiples) van como lista. */
function campos(datos: FormData): Record<string, string | string[]> {
  const resultado: Record<string, string | string[]> = {};
  for (const nombre of new Set(datos.keys())) {
    if (nombre.startsWith("$") || nombre === "clave_idempotencia") continue;
    const valores = datos.getAll(nombre).map(String);
    resultado[nombre] =
      valores.length > 1 || nombre === "modalidades" ? valores : (valores[0] ?? "");
  }
  return resultado;
}

export async function enviarAdmin(
  destino: Destino,
  _anterior: EstadoAdmin,
  datos: FormData,
): Promise<EstadoAdmin> {
  const clave = datos.get("clave_idempotencia");
  const extra: Record<string, string> =
    typeof clave === "string" && clave ? { "Idempotency-Key": clave } : {};
  const { response, datos: respuesta } = await llamarApi(
    destino.metodo,
    destino.ruta,
    { campos: campos(datos) },
    extra,
  );
  if (response.ok) {
    const numero = (respuesta as { numero?: number } | null)?.numero;
    revalidatePath("/", "layout");
    redirect(
      destino.exitoConNumero && numero ? `/administracion/concursos/${numero}/` : destino.exito,
    );
  }
  const problema = (respuesta ?? {}) as Problema;
  if (response.status === 401) {
    return { generales: [], sesionVencida: { pendiente: problema.pendiente ?? null } };
  }
  const generales = (problema.errores ?? []).filter((e) => !e.campo).map((e) => e.mensaje);
  if (problema.existente) generales.unshift(problema.detail ?? "");
  return {
    generales: generales.length ? generales : problema.formulario ? [] : [problema.detail ?? ""],
    formulario: problema.formulario,
    existente: problema.existente,
  };
}
