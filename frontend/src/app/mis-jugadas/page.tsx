/**
 * Mis jugadas en Next.js ([001] US4, US5; [003] AC-8.2, AC-9.3 a AC-9.5, FR-041, pantalla 3): el
 * mismo contenido que `templates/jugadas/lista.html`, con `GET /api/v1/jugadas/` (solo las jugadas
 * propias, Const. IV).
 */
import type { Metadata } from "next";
import Link from "next/link";

import { apiServidor } from "@/api/servidor";
import { EmptyState } from "@/components/empty-state";
import { boton } from "@/components/ui/variantes";
import { dosDigitos, fecha, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { verificarRespuesta } from "@/lib/sesion";
import { cn } from "@/lib/utils";

export const metadata: Metadata = { title: msg("rot.mis_jugadas") };

export default async function MisJugadas() {
  const api = await apiServidor();
  const { data, response } = await api.GET("/api/v1/jugadas/");
  await verificarRespuesta(response);
  const jugadas = data ?? [];
  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <h1>{msg("rot.mis_jugadas")}</h1>
        {jugadas.length > 0 && (
          <Link className={boton({ variante: "principal" })} href="/mis-jugadas/nueva/">
            {msg("rot.registrar_jugada")}
          </Link>
        )}
      </div>
      {jugadas.length > 0 ? (
        <div className="overflow-x-auto rounded-card border border-border bg-surface shadow-1 max-md:overflow-visible max-md:border-0 max-md:bg-transparent max-md:shadow-none">
          <table className="apilable">
            <caption className="visualmente-oculto">{msg("rot.caption_jugadas")}</caption>
            <thead>
              <tr>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.sorteo")}
                </th>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.fecha_del_sorteo")}
                </th>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.numeros")}
                </th>
                <th scope="col" className="px-3 py-2 text-left">
                  {msg("rot.aciertos")}
                </th>
                <th scope="col" className="px-3 py-2 text-right">
                  {msg("rot.costo")}
                </th>
                <th scope="col" className="px-3 py-2">
                  <span className="visualmente-oculto">{msg("rot.acciones")}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {jugadas.map((j) => (
                <tr key={j.id} id={`jugada-${j.id}`} className="fila-enlace">
                  <td
                    data-rotulo={msg("rot.sorteo")}
                    className="cifras font-semibold whitespace-nowrap"
                  >
                    {msg("rot.numero_sorteo", { numero: j.sorteo.numero })}
                  </td>
                  <td
                    data-rotulo={msg("rot.fecha_del_sorteo")}
                    className="cifras whitespace-nowrap"
                  >
                    {fecha(j.sorteo.fecha)}
                  </td>
                  <td data-rotulo={msg("rot.numeros")}>
                    <ul className="numeros" aria-label={msg("rot.numeros_jugada")}>
                      {j.numeros.map((n) => (
                        <li key={n} className="bolilla">
                          {dosDigitos(n)}
                        </li>
                      ))}
                    </ul>
                    <p className="m-0 text-xs text-muted-foreground">
                      {msg("rot.participa_en", { modalidades: j.modalidades.join(", ") })}
                    </p>
                  </td>
                  <td data-rotulo={msg("rot.aciertos")}>
                    <span className={cn("estado resumen", j.estado.clase)}>{j.estado.texto}</span>
                  </td>
                  <td
                    data-rotulo={msg("rot.costo")}
                    className="cifras a-la-derecha whitespace-nowrap"
                  >
                    {pesos(j.costo)}
                  </td>
                  <td className="whitespace-nowrap md:text-right">
                    <Link
                      href={`/mis-jugadas/${j.id}/`}
                      data-enlace-fila=""
                      className="ver-detalle text-sm font-medium text-primary no-underline hover:underline"
                    >
                      {msg("ext.ver_detalle")}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          icono="ticket"
          titulo={msg("vacio.jugadas.titulo")}
          explicacion={msg("vacio.jugadas.explicacion")}
          accion={{ texto: msg("vacio.jugadas.accion"), href: "/mis-jugadas/nueva/" }}
        />
      )}
    </>
  );
}
