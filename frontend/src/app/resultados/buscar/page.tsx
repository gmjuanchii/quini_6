/**
 * Búsqueda de sorteos en Next.js ([001] AC-1.x; [003] AC-8.3, FR-012, FR-041, pantalla 4): el mismo
 * comportamiento que `resultados/views_publicas.py :: buscar` con `GET /api/v1/sorteos/buscar/`: un
 * número existente lleva a su detalle; sin número ni fecha, a "Resultados".
 */
import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { EmptyState } from "@/components/empty-state";
import { msg } from "@/lib/mensajes";

import { BusquedaForm, ListadoSorteos } from "../_componentes/resultados";

export const metadata: Metadata = { title: msg("rot.buscar_sorteos") };

type Problema = { detail?: string; errores?: { campo: string; mensaje: string }[] };

function uno(valor: string | string[] | undefined): string {
  return ((Array.isArray(valor) ? valor[0] : valor) ?? "").trim();
}

export default async function Buscar({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const numero = uno(sp.numero);
  const fecha = uno(sp.fecha);
  const api = await apiServidor();
  const { data, error } = await api.GET("/api/v1/sorteos/buscar/", {
    params: { query: { numero, fecha } },
  });
  if (data?.redirigir) redirect(data.redirigir);
  const problema = (error ?? {}) as Problema;
  const errorCampo = problema.errores?.[0];
  // Como Django: el número inválido es un aviso general; la fecha, además, junto al campo.
  const general = errorCampo?.campo === "numero" ? errorCampo.mensaje : problema.detail;
  return (
    <>
      <BackLink href="/resultados/" texto={msg("nav.volver_sorteos")} />
      <h1>{msg("rot.buscar_sorteos")}</h1>
      {general && <Callout variante="danger" rol="alert" texto={general} />}
      {data?.mensaje && (
        <EmptyState
          variante="sin_resultados"
          titulo={msg("vacio.filtro.titulo")}
          explicacion={data.mensaje}
          limpiarHref="/resultados/"
        />
      )}
      {data && data.elementos.length > 0 && (
        <>
          <h2>{msg("rot.sorteos_del", { fecha })}</h2>
          <ListadoSorteos sorteos={data.elementos} />
        </>
      )}
      <BusquedaForm
        numero={numero}
        fechaBuscada={fecha}
        errorFecha={errorCampo?.campo === "fecha" ? errorCampo.mensaje : undefined}
      />
    </>
  );
}
