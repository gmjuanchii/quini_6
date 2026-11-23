/**
 * Modificar un sorteo en Next.js ([001] AC-2.14, RN-14; [003] FR-041, pantalla 6).
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { BackLink } from "@/components/back-link";
import { msg } from "@/lib/mensajes";
import { rutaActual } from "@/lib/sesion";

import { enviarAdmin } from "../../acciones";
import { API, BASE, leerAdmin, tokenCsrf } from "../../_componentes/comunes";
import type { Formulario } from "../../_componentes/estado";
import { FormularioDjango } from "../../_componentes/formulario-django";

export const metadata: Metadata = { title: msg("rot.adm_modificar_sorteo") };

export default async function ModificarSorteo({ params }: { params: Promise<{ numero: string }> }) {
  const numero = Number((await params).numero) || 0;
  const datos = await leerAdmin<{ formulario: Formulario }>(`/${numero}/modificar/`);
  if (!datos) notFound();
  return (
    <>
      <BackLink href={`${BASE}/`} texto={msg("nav.volver_sorteos")} />
      <h1>{msg("rot.adm_modificar_titulo", { numero })}</h1>
      <p className="ayuda">{msg("admin.ayuda_modalidades")}</p>
      <FormularioDjango
        accion={enviarAdmin.bind(null, {
          metodo: "PUT",
          ruta: `${API}/${numero}/`,
          exito: `${BASE}/${numero}/`,
        })}
        formulario={datos.formulario}
        boton={msg("rot.guardar_cambios")}
        trabajando={msg("form.trabajando_guardar")}
        cancelar={`${BASE}/${numero}/`}
        csrf={await tokenCsrf()}
        siguiente={await rutaActual()}
      />
    </>
  );
}
