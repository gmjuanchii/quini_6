/**
 * Detalle de una jugada en Next.js ([001] US5, AC-5.x, RN-08; [003] FR-041, pantalla 3): el mismo
 * contenido que `templates/jugadas/detalle.html`, con `GET /api/v1/jugadas/{id}/`.
 */
import type { Metadata } from "next";
import Link from "next/link";

import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { boton } from "@/components/ui/variantes";
import { dosDigitos, fecha, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

import { ComparacionJugada } from "../_componentes/comparacion";
import { JugadaNoDisponible, obtenerJugada } from "../_componentes/comunes";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const j = await obtenerJugada((await params).id);
  return {
    title: j
      ? msg("rot.jugada_del_sorteo", { numero: j.sorteo.numero })
      : msg("rot.jugada_no_disponible"),
  };
}

export default async function DetalleJugada({ params }: Props) {
  const j = await obtenerJugada((await params).id);
  if (!j) return <JugadaNoDisponible />;
  return (
    <>
      <BackLink href="/mis-jugadas/" texto={msg("nav.volver_jugadas")} />
      <h1>{msg("rot.jugada_del_sorteo", { numero: j.sorteo.numero })}</h1>
      <section className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6">
        <dl className="datos">
          <dt>{msg("rot.sorteo")}</dt>
          <dd>
            <a href={`/resultados/${j.sorteo.numero}/`}>
              {msg("rot.numero_sorteo", { numero: j.sorteo.numero })}
            </a>
          </dd>
          <dt>{msg("rot.fecha_del_sorteo")}</dt>
          <dd>{fecha(j.sorteo.fecha)}</dd>
          <dt>{msg("rot.costo")}</dt>
          <dd>{pesos(j.costo)}</dd>
          <dt>{msg("rot.participa_en_rotulo")}</dt>
          <dd>{j.modalidades.join(", ")}</dd>
        </dl>
        <ul className="numeros" aria-label={msg("rot.numeros_jugada")}>
          {j.numeros.map((n) => (
            <li key={n} className="bolilla">
              {dosDigitos(n)}
            </li>
          ))}
        </ul>
        {j.modificable ? (
          <div className="my-3 flex flex-wrap items-center gap-2">
            <Link
              className={boton({ variante: "secundario" })}
              href={`/mis-jugadas/${j.id}/editar/`}
            >
              {msg("rot.editar")}
            </Link>
            <Link
              className={boton({ variante: "secundario" })}
              href={`/mis-jugadas/${j.id}/eliminar/`}
            >
              {msg("ext.eliminar")}
            </Link>
          </div>
        ) : (
          <Callout variante="info" texto={msg("jugada.fija")} />
        )}
      </section>
      <p>
        {msg("rot.estado_dos_puntos")}{" "}
        <span className={cn("estado resumen", j.resumen.clase)}>{j.resumen.texto}</span>
      </p>
      {j.comparacion.length > 0 && (
        <>
          <h2>{msg("rot.comparacion_titulo")}</h2>
          <ComparacionJugada numeros={j.numeros} comparacion={j.comparacion} />
        </>
      )}
    </>
  );
}
