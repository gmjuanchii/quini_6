/**
 * Administración de sorteos en Next.js ([001] US2; [003] AC-9.3, AC-9.5, FR-041, pantalla 6): el
 * mismo listado que `templates/resultados/admin/listado.html`, con `GET /api/v1/admin/sorteos/`.
 */
import type { Metadata } from "next";
import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { boton } from "@/components/ui/variantes";
import { fecha } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

import { BASE, leerAdmin, type BloqueAdmin, type SorteoAdmin } from "./_componentes/comunes";

export const metadata: Metadata = { title: msg("admin.titulo_listado") };

function Estado({ b }: { b: BloqueAdmin | undefined }) {
  if (!b) return null;
  return <span className={cn("estado", b.estado.clase)}>{b.estado.texto}</span>;
}

export default async function ListadoSorteos() {
  const sorteos = (await leerAdmin<SorteoAdmin[]>("/")) ?? [];
  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <h1>{msg("rot.adm_sorteos")}</h1>
        <Link className={boton({ variante: "principal" })} href={`${BASE}/nuevo/`}>
          {msg("admin.crear")}
        </Link>
      </div>
      <p>
        <Link href="/administracion/extracciones/">{msg("rot.adm_extraccion")}</Link>
      </p>
      {sorteos.length > 0 ? (
        <div className="overflow-x-auto rounded-card border border-border bg-surface shadow-1 max-md:overflow-visible max-md:border-0 max-md:bg-transparent max-md:shadow-none">
          <table className="apilable">
            <caption className="visualmente-oculto">{msg("rot.adm_caption")}</caption>
            <thead>
              <tr>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.sorteo")}
                </th>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.fecha_del_sorteo")}
                </th>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.estado")}
                </th>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.modalidad")}
                </th>
              </tr>
            </thead>
            <tbody>
              {sorteos.map((s) => (
                <tr key={s.numero} className="fila-enlace">
                  <td
                    data-rotulo={msg("rot.sorteo")}
                    className="cifras align-top whitespace-nowrap"
                  >
                    <Link
                      href={`${BASE}/${s.numero}/`}
                      data-enlace-fila=""
                      className="font-semibold text-primary"
                    >
                      {msg("rot.numero_sorteo", { numero: s.numero })}
                    </Link>
                  </td>
                  <td
                    data-rotulo={msg("rot.fecha_del_sorteo")}
                    className="cifras align-top whitespace-nowrap"
                  >
                    {fecha(s.fecha)}
                  </td>
                  <td data-rotulo={msg("rot.estado")} className="align-top">
                    <strong>{s.completitud.texto}</strong>
                  </td>
                  <td data-rotulo={msg("rot.modalidad")} className="align-top">
                    <ul className="m-0 flex list-none flex-col gap-1 p-0">
                      {s.filas.map((f) => (
                        <li key={f.modalidad.slug}>
                          <span className="font-medium">{f.modalidad.nombre}</span>:{" "}
                          {f.modalidad.tiene_extraccion_propia ? (
                            <>
                              {msg("rot.numeros")} <Estado b={f.bloques[0]} /> ·{" "}
                              {msg("rot.premios")} <Estado b={f.bloques[1]} />
                            </>
                          ) : (
                            <>
                              {msg("rot.premios")} <Estado b={f.bloques[0]} />
                            </>
                          )}
                        </li>
                      ))}
                    </ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          icono="list-ordered"
          titulo={msg("admin.sin_concursos")}
          accion={{ texto: msg("vacio.resultados.accion_cargar"), href: `${BASE}/nuevo/` }}
        />
      )}
    </>
  );
}
