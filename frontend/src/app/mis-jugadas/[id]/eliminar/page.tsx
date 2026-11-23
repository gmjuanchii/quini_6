/**
 * Eliminar una jugada en Next.js ([001] AC-4.11, RN-08; [003] FR-008, FR-041, pantalla 3): la misma
 * confirmación que `templates/jugadas/eliminar.html` (página aparte, funciona sin scripts).
 */
import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";

import { BotonEnviar } from "@/components/boton-enviar";
import { Callout } from "@/components/callout";
import { boton } from "@/components/ui/variantes";
import { nuevaClaveIdempotencia } from "@/lib/acciones";
import { dosDigitos, fecha, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";

import { eliminarJugada } from "../../acciones";
import { JugadaNoDisponible, obtenerJugada } from "../../_componentes/comunes";

export const metadata: Metadata = { title: msg("rot.eliminar_jugada") };

export default async function EliminarJugada({ params }: { params: Promise<{ id: string }> }) {
  const j = await obtenerJugada((await params).id);
  if (!j) return <JugadaNoDisponible />;
  if (!j.modificable) redirect(`/mis-jugadas/avisar/?clave=jugada.fija&id=${j.id}`);
  return (
    <>
      <h1>{msg("rot.eliminar_jugada")}</h1>
      <section className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6">
        <p>
          {msg("rot.jugada_resumen", {
            numero: j.sorteo.numero,
            fecha: fecha(j.sorteo.fecha),
            costo: pesos(j.costo),
          })}
        </p>
        <ul className="numeros" aria-label={msg("rot.numeros_jugada")}>
          {j.numeros.map((n) => (
            <li key={n} className="bolilla">
              {dosDigitos(n)}
            </li>
          ))}
        </ul>
        <Callout variante="warning" texto={msg("jugada.confirmar_eliminacion")} />
        <form
          action={eliminarJugada.bind(null, j.id)}
          className="my-3 flex flex-wrap items-center gap-2"
          noValidate
        >
          <input type="hidden" name="clave_idempotencia" value={nuevaClaveIdempotencia()} />
          <BotonEnviar variante="destructivo" textoTrabajando={msg("form.trabajando_eliminar")}>
            {msg("ext.eliminar")}
          </BotonEnviar>
          <Link className={boton({ variante: "secundario" })} href={`/mis-jugadas/${j.id}/`}>
            {msg("rot.cancelar")}
          </Link>
        </form>
      </section>
    </>
  );
}
