/**
 * Editar una jugada en Next.js ([001] AC-4.10, RN-08; [003] FR-032, FR-041, pantalla 3). Si la
 * jugada ya no se puede modificar, avisa y vuelve a su detalle, como la vista HTML (el aviso lo
 * agrega `avisar/route.ts`, no esta página mientras se dibuja).
 */
import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { BackLink } from "@/components/back-link";
import { nuevaClaveIdempotencia } from "@/lib/acciones";
import { msg } from "@/lib/mensajes";
import { formularioReanudado } from "@/lib/reanudar";
import { rutaActual } from "@/lib/sesion";

import { modificarJugada } from "../../acciones";
import {
  JugadaNoDisponible,
  obtenerJugadaParaEditar,
  SESION_VENCIDA,
  sorteosDisponibles,
  tokenCsrf,
} from "../../_componentes/comunes";
import { FormularioJugada } from "../../_componentes/formulario-jugada";

export const metadata: Metadata = { title: msg("rot.editar_jugada") };

export default async function EditarJugada({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const j = await obtenerJugadaParaEditar(id);
  if (!j) return <JugadaNoDisponible />;
  if (j === SESION_VENCIDA) {
    // Sin scripts, respuesta de "Guardar cambios" con la sesión vencida: el formulario muestra lo
    // escrito (estado de la acción) y "La sesión venció…" con "Ingresar" (FR-032).
    return (
      <>
        <BackLink href="/mis-jugadas/" texto={msg("nav.volver_jugadas")} />
        <h1>{msg("rot.editar_jugada")}</h1>
        <FormularioJugada
          accion={modificarJugada.bind(null, Number(id) || 0)}
          sorteos={await sorteosDisponibles()}
          inicial={{ sorteo: "", numeros: [], costo: "" }}
          clave={nuevaClaveIdempotencia()}
          csrf={await tokenCsrf()}
          siguiente={await rutaActual()}
          cancelar="/mis-jugadas/"
          edicion
        />
      </>
    );
  }
  if (!j.modificable) redirect(`/mis-jugadas/avisar/?clave=jugada.fija&id=${j.id}`);
  const disponibles = await sorteosDisponibles();
  // Como Django: el sorteo actual se ofrece aunque ya no esté entre los disponibles.
  const sorteos = disponibles.some((s) => s.numero === j.sorteo.numero)
    ? disponibles
    : [{ numero: j.sorteo.numero, fecha: j.sorteo.fecha, modalidades: [] }, ...disponibles];
  const reanudado = await formularioReanudado();
  const costo = j.costo.replace(".", ",");
  return (
    <>
      <BackLink href="/mis-jugadas/" texto={msg("nav.volver_jugadas")} />
      <h1>{msg("rot.editar_jugada")}</h1>
      <p>{msg("jugada.intro")}</p>
      <FormularioJugada
        accion={modificarJugada.bind(null, j.id)}
        sorteos={sorteos}
        inicial={{
          sorteo: reanudado?.sorteo?.[0] ?? String(j.sorteo.numero),
          numeros: reanudado?.numeros ?? j.numeros.map(String),
          costo: reanudado?.costo?.[0] ?? costo,
        }}
        clave={nuevaClaveIdempotencia()}
        csrf={await tokenCsrf()}
        siguiente={await rutaActual()}
        cancelar={`/mis-jugadas/${j.id}/`}
        edicion
      />
    </>
  );
}
