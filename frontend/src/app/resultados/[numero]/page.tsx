/**
 * Detalle público de un sorteo en Next.js ([001] US1, AC-1.x; [003] FR-041, pantalla 4): el mismo
 * contenido que `templates/resultados/detalle.html`, con `GET /api/v1/sorteos/{numero}/`. Solo lo
 * publicado (Const. VIII). Un sorteo inexistente muestra la página inexistente.
 */
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import { BackLink } from "@/components/back-link";
import { boton } from "@/components/ui/variantes";
import { fecha } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

import { claseCompletitud, SeccionModalidad } from "../_componentes/resultados";

type Props = { params: Promise<{ numero: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { numero } = await params;
  return { title: msg("rot.sorteo_numero", { numero }) };
}

export default async function DetalleSorteo({ params }: Props) {
  const { numero } = await params;
  const api = await apiServidor();
  const { data, response } = await api.GET("/api/v1/sorteos/{numero}/", {
    params: { path: { numero: Number(numero) || 0 } },
  });
  if (response.status === 404) notFound();
  if (!data) throw new Error("La API de resultados no respondió");
  return (
    <>
      <BackLink href="/resultados/" texto={msg("nav.volver_sorteos")} />
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <h1>{msg("rot.sorteo_numero", { numero: data.numero })}</h1>
        <span className={cn("estado", claseCompletitud(data.completitud.codigo))}>
          {data.completitud.texto}
        </span>
      </div>
      <p>{msg("rot.sorteo_del", { fecha: fecha(data.fecha) })}</p>
      {data.admite_jugadas && (
        <p>
          <Link
            className={boton({ variante: "principal" })}
            href={`/mis-jugadas/nueva/?concurso=${data.numero}`}
          >
            {msg("rot.registrar_jugada")}
          </Link>
        </p>
      )}
      {data.modalidades.length > 0 ? (
        data.modalidades.map((m) => <SeccionModalidad key={m.slug} m={m} />)
      ) : (
        <div className="rounded-card bg-surface px-6 py-8 text-center text-muted-foreground shadow-1">
          <p>{msg("rot.sin_modalidades")}</p>
        </div>
      )}
    </>
  );
}
