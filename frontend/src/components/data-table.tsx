/**
 * DataTable ([003] AC-9.1 a AC-9.5, FR-027, RN-07, contracts/componentes.md): orden y paginación los
 * decide Django y el estado vive en la dirección. Componente de **servidor** sin JavaScript de
 * cliente: con TanStack Table en modo manual no aportaba nada que se ejecutara en el navegador y
 * sumaba unos 13 kB comprimidos a cada pantalla con tabla (R-24). Igual que
 * `templates/ui/_tabla.html`: `<table class="apilable">` con `<caption>`, `aria-sort` en la columna
 * ordenada, encabezados ordenables como **enlaces** (sin scripts), tarjetas rotuladas debajo de
 * 768 px y fila entera enlazada (el enlace de la fila lleva `data-enlace-fila`; el menú ⋮ va en
 * `.sobre-fila`).
 *
 * Las celdas llegan ya renderizadas desde el componente de servidor de la página.
 */
import Link from "next/link";
import type { ReactNode } from "react";

import { Icono } from "@/components/icono";
import { msg } from "@/lib/mensajes";
import type { Encabezado } from "@/lib/tablas";
import { cn } from "@/lib/utils";

export type Fila = {
  clave: string;
  /** `id` del `<tr>` (p. ej. `fila-extraccion-12`, como en Django). */
  id?: string;
  celdas: Record<string, ReactNode>;
  /** Fila entera clicable (AC-9.4). */
  enlace?: boolean;
  className?: string;
  datos?: Record<`data-${string}`, string>;
};

/** Clases de cada celda por columna (p. ej. `cifras` para alinear números). */
export type ClasesCelda = Record<string, string>;

export function DataTable({
  titulo,
  encabezados,
  filas,
  clasesCelda = {},
  columnaAcciones,
  className,
}: {
  titulo: string;
  encabezados: Encabezado[];
  filas: Fila[];
  clasesCelda?: ClasesCelda;
  /** Rótulo oculto de la última columna (menú ⋮), si la hay. */
  columnaAcciones?: string;
  className?: string;
}) {
  const columnas = [
    ...encabezados.map((e) => ({ id: e.id, rotulo: e.texto as string | undefined, e })),
    ...(columnaAcciones ? [{ id: "acciones", rotulo: undefined, e: undefined }] : []),
  ];

  return (
    <div className={className}>
      <table className="apilable">
        <caption className="visualmente-oculto">{titulo}</caption>
        <thead>
          <tr>
            {columnas.map(({ id, e }) => (
              <th
                key={id}
                scope="col"
                aria-sort={e?.sentido}
                className={cn(
                  "px-3 py-2 text-left font-semibold",
                  e?.alineacion === "derecha" && "text-right",
                )}
              >
                {e ? (
                  <EncabezadoOrdenable e={e} />
                ) : (
                  <span className="visualmente-oculto">{columnaAcciones}</span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila) => (
            <tr
              key={fila.clave}
              id={fila.id}
              className={cn(fila.enlace && "fila-enlace", fila.className)}
              {...fila.datos}
            >
              {columnas.map(({ id, rotulo }) => (
                <td key={id} data-rotulo={rotulo} className={clasesCelda[id]}>
                  {fila.celdas[id]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/** Contenido de un encabezado ordenable (`templates/ui/_encabezado_ordenable.html`). */
export function EncabezadoOrdenable({ e }: { e: Encabezado }) {
  if (!e.href) return <>{e.texto}</>;
  return (
    <Link
      href={e.href}
      className={cn(
        "-mx-1 inline-flex min-h-control items-center gap-1.5 rounded-control px-1 text-foreground no-underline hover:underline",
        e.alineacion === "derecha" && "flex-row-reverse",
      )}
    >
      {e.texto}
      {e.sentido === "ascending" ? (
        <>
          <Icono nombre="arrow-up" className="size-4 shrink-0" />
          <span className="visualmente-oculto">, {msg("tabla.orden_asc")}</span>
        </>
      ) : e.sentido === "descending" ? (
        <>
          <Icono nombre="arrow-down" className="size-4 shrink-0" />
          <span className="visualmente-oculto">, {msg("tabla.orden_desc")}</span>
        </>
      ) : (
        <Icono nombre="arrow-up-down" className="size-4 shrink-0 text-muted-foreground" />
      )}
    </Link>
  );
}
