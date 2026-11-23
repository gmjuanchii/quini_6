/**
 * Piezas comunes de Mis jugadas ([001] US4, US5; [003] FR-041, pantalla 3): lectura de una jugada
 * propia y la página "Jugada no disponible" (`templates/jugadas/no_existe.html`). Una jugada ajena o
 * inexistente recibe el mismo 404 de Django (Const. IV) y se informa en la misma página (NFR-007:
 * `notFound()` de Next.js necesitaría scripts para completarse; research.md, Fase 18).
 */
import { cookies } from "next/headers";
import Link from "next/link";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { Callout } from "@/components/callout";
import { msg } from "@/lib/mensajes";
import { verificarRespuesta } from "@/lib/sesion";

export type Jugada = components["schemas"]["JugadaDTO"];

/** La sesión venció mientras se dibuja la respuesta de una Server Action (FR-032). */
export const SESION_VENCIDA = "sesion-vencida" as const;

async function leerJugada(id: string, continuarEnAccion: boolean) {
  const api = await apiServidor();
  const { data, response } = await api.GET("/api/v1/jugadas/{id}/", {
    params: { path: { id: Number(id) || 0 } },
  });
  if (response.status === 404) return null;
  await verificarRespuesta(response, { continuarEnAccion });
  if (response.status === 401) return SESION_VENCIDA;
  if (!data) throw new Error("La API de jugadas no respondió");
  return data;
}

export async function obtenerJugada(id: string): Promise<Jugada | null> {
  const j = await leerJugada(id, false);
  return j === SESION_VENCIDA ? null : j; // sin continuarEnAccion, un 401 ya redirigió
}

/** Para el formulario de modificación: con la sesión vencida al enviarlo sin scripts, la página se
 * dibuja con lo escrito (estado de la acción) en lugar de redirigir (FR-032). */
export async function obtenerJugadaParaEditar(
  id: string,
): Promise<Jugada | null | typeof SESION_VENCIDA> {
  return leerJugada(id, true);
}

/** Sorteos que admiten jugadas. Sin scripts y con la sesión vencida al enviar el formulario, la
 * página se dibuja sin ellos y el formulario muestra "La sesión venció…" (FR-032). */
export async function sorteosDisponibles() {
  const api = await apiServidor();
  const { data, response } = await api.GET("/api/v1/jugadas/sorteos-disponibles/");
  await verificarRespuesta(response, { continuarEnAccion: true });
  return data ?? [];
}

export async function tokenCsrf(): Promise<string> {
  return (await cookies()).get("csrftoken")?.value ?? "";
}

export function JugadaNoDisponible() {
  return (
    <>
      <h1>{msg("rot.jugada_no_disponible")}</h1>
      <Callout variante="danger" texto={msg("jugada.no_existe")} />
      <p>
        <Link href="/mis-jugadas/">{msg("rot.volver_mis_jugadas")}</Link>
      </p>
    </>
  );
}
