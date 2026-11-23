/**
 * Registrar una jugada en Next.js ([001] AC-4.1 a AC-4.9; [003] FR-032, FR-041, pantalla 3). Con
 * `?concurso=N` (desde el detalle de un sorteo) el sorteo queda elegido; si no admite jugadas, se
 * avisa como en Django. Si la página se abre con un formulario pendiente ("Volver al formulario",
 * AC-14.4), muestra lo escrito sin enviarlo.
 */
import type { Metadata } from "next";

import { apiServidor } from "@/api/servidor";
import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { nuevaClaveIdempotencia } from "@/lib/acciones";
import { msg } from "@/lib/mensajes";
import { formularioReanudado } from "@/lib/reanudar";
import { rutaActual } from "@/lib/sesion";

import { registrarJugada } from "../acciones";
import { sorteosDisponibles, tokenCsrf } from "../_componentes/comunes";
import { FormularioJugada } from "../_componentes/formulario-jugada";

export const metadata: Metadata = { title: msg("rot.registrar_jugada") };

export default async function NuevaJugada({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const sorteos = await sorteosDisponibles();
  const pedido = String((Array.isArray(sp.concurso) ? sp.concurso[0] : sp.concurso) ?? "").trim();
  const elegido = sorteos.find((s) => String(s.numero) === pedido);
  // [001] AC-4.7, AC-4.8: el sorteo pedido no admite jugadas (mismos textos que Django): si existe,
  // ya está cerrado; si no, no está disponible.
  let errorSorteo: string | undefined;
  if (pedido && !elegido) {
    const api = await apiServidor();
    const { response } = await api.GET("/api/v1/sorteos/{numero}/", {
      params: { path: { numero: Number(pedido) || 0 } },
    });
    errorSorteo = msg(response.ok ? "jugada.concurso_cerrado" : "jugada.concurso_no_disponible");
  }
  const reanudado = await formularioReanudado();
  const inicial = {
    sorteo: reanudado?.sorteo?.[0] ?? (elegido ? String(elegido.numero) : ""),
    numeros: reanudado?.numeros ?? [],
    costo: reanudado?.costo?.[0] ?? "",
  };
  return (
    <>
      <BackLink href="/mis-jugadas/" texto={msg("nav.volver_jugadas")} />
      <h1>{msg("rot.registrar_jugada")}</h1>
      <p>{msg("jugada.intro")}</p>
      {errorSorteo && <Callout variante="danger" rol="alert" texto={errorSorteo} />}
      <FormularioJugada
        accion={registrarJugada}
        sorteos={sorteos}
        inicial={inicial}
        clave={nuevaClaveIdempotencia()}
        csrf={await tokenCsrf()}
        siguiente={await rutaActual()}
        cancelar="/mis-jugadas/"
      />
    </>
  );
}
