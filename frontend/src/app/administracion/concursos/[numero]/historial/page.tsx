/**
 * Historial de cambios de un sorteo en Next.js ([001] US7; [003] FR-041, pantalla 6): el mismo
 * contenido que `templates/resultados/admin/historial.html`.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";

import type { components } from "@/api/esquema";
import { BackLink } from "@/components/back-link";
import { fechaHora } from "@/lib/formato";
import { msg } from "@/lib/mensajes";

import { BASE, leerAdmin } from "../../_componentes/comunes";

type Cambio = components["schemas"]["CambioRegistrado"];

export const metadata: Metadata = { title: msg("rot.adm_ver_historial") };

export default async function Historial({ params }: { params: Promise<{ numero: string }> }) {
  const numero = Number((await params).numero) || 0;
  const cambios = await leerAdmin<Cambio[]>(`/${numero}/historial/`);
  if (!cambios) notFound();
  const columnas: [string, (c: Cambio) => string][] = [
    [msg("rot.fecha_y_hora"), (c) => fechaHora(c.momento)],
    [msg("rot.adm_accion"), (c) => c.accion],
    [msg("rot.adm_modalidad_bloque"), (c) => c.modalidad_y_bloque],
    [msg("rot.adm_valor_anterior"), (c) => c.valor_anterior],
    [msg("rot.adm_valor_nuevo"), (c) => c.valor_nuevo],
    [msg("rot.adm_autor"), (c) => c.autor],
    [msg("rot.adm_motivo"), (c) => c.motivo],
    [msg("rot.fuente"), (c) => c.fuente],
  ];
  return (
    <>
      <BackLink href={`${BASE}/${numero}/`} texto={msg("rot.sorteo_numero", { numero })} />
      <h1>{msg("rot.adm_historial_titulo", { numero })}</h1>
      {cambios.length > 0 ? (
        <table className="apilable">
          <caption>{msg("rot.adm_historial_caption")}</caption>
          <thead>
            <tr>
              {columnas.map(([t]) => (
                <th key={t} scope="col">
                  {t}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {cambios.map((c, i) => (
              <tr key={i}>
                {columnas.map(([t, valor]) => (
                  <td key={t} data-rotulo={t}>
                    {valor(c)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="rounded-card bg-surface px-6 py-8 text-center text-muted-foreground shadow-1">
          <p>{msg("rot.adm_sin_cambios")}</p>
        </div>
      )}
    </>
  );
}
