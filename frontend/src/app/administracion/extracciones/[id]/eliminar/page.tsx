/**
 * Confirmación de eliminación en una página aparte ([003] AC-2.3, componentes.md § 4): la versión
 * sin scripts (y la que se ve al abrir la dirección directamente). Con scripts, la ruta
 * interceptada `@modal/(.)[id]/eliminar` muestra el mismo contenido en un diálogo.
 */
import type { Metadata } from "next";

import { BackLink } from "@/components/back-link";
import { msg } from "@/lib/mensajes";

import {
  CuerpoEliminar,
  extraccionAEliminar,
  LISTADO,
  textoConfirmar,
} from "../../_componentes/eliminar";

export const metadata: Metadata = { title: msg("ext.eliminar_titulo") };

export default async function EliminarExtraccion({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const e = await extraccionAEliminar(id);
  return (
    <>
      <BackLink href={LISTADO} texto={msg("nav.volver_extracciones")} />
      <section
        className="mx-auto mt-4 max-w-formulario rounded-card bg-surface p-6 shadow-1"
        role="alertdialog"
        aria-labelledby="dialogo-titulo"
        aria-describedby="dialogo-texto"
      >
        <div className="flex flex-col gap-4" data-confirmacion="">
          <h2 id="dialogo-titulo" className="text-2xl font-semibold">
            {msg("ext.eliminar_titulo")}
          </h2>
          <p id="dialogo-texto" className="font-medium">
            {textoConfirmar(e)}
          </p>
          <CuerpoEliminar e={e} />
        </div>
      </section>
    </>
  );
}
