/**
 * Cargar sorteo en Next.js ([001] AC-2.1, AC-2.2; [003] FR-031, FR-041, pantalla 6): el formulario
 * de `ConcursoForm`, descrito por `GET /api/v1/admin/sorteos/nuevo/`, enviado a
 * `POST /api/v1/admin/sorteos/` con `Idempotency-Key`. Éxito → el panel del sorteo nuevo.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";

import { BackLink } from "@/components/back-link";
import { nuevaClaveIdempotencia } from "@/lib/acciones";
import { msg } from "@/lib/mensajes";
import { rutaActual } from "@/lib/sesion";

import { enviarAdmin } from "../acciones";
import { API, BASE, leerAdmin, tokenCsrf } from "../_componentes/comunes";
import type { Formulario } from "../_componentes/estado";
import { FormularioDjango } from "../_componentes/formulario-django";

export const metadata: Metadata = { title: msg("admin.crear") };

export default async function NuevoSorteo() {
  const datos = await leerAdmin<{ formulario: Formulario }>("/nuevo/");
  if (!datos) notFound();
  return (
    <>
      <BackLink href={`${BASE}/`} texto={msg("nav.volver_sorteos")} />
      <h1>{msg("admin.crear")}</h1>
      <FormularioDjango
        accion={enviarAdmin.bind(null, {
          metodo: "POST",
          ruta: `${API}/`,
          exito: `${BASE}/`,
          exitoConNumero: true,
        })}
        formulario={datos.formulario}
        boton={msg("admin.crear")}
        trabajando={msg("form.trabajando_guardar")}
        cancelar={`${BASE}/`}
        clave={nuevaClaveIdempotencia()}
        csrf={await tokenCsrf()}
        siguiente={await rutaActual()}
      />
    </>
  );
}
