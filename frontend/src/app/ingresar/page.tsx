/**
 * Ingresar en Next.js ([001] AC-3.4 a AC-3.7; [003] HU-06, FR-040, R-19, pantalla 5): el mismo
 * contenido que `templates/cuentas/ingresar.html`. Al ingresar, Django fija la sesión compartida y
 * la persona vuelve a `next` (solo rutas del sitio, FR-017).
 */
import type { Metadata } from "next";
import { cookies } from "next/headers";

import { msg } from "@/lib/mensajes";

import { ingresar } from "./acciones";
import { Alternativa } from "./_componentes/alternativa";
import { FormularioCuenta } from "./_componentes/formulario-cuenta";

export const metadata: Metadata = { title: msg("rot.ingresar") };

function uno(valor: string | string[] | undefined): string {
  return (Array.isArray(valor) ? valor[0] : valor) ?? "";
}

export default async function Ingresar({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const siguiente = uno((await searchParams).next);
  const seguro = siguiente.startsWith("/") && !siguiente.startsWith("//") ? siguiente : "";
  const csrf = (await cookies()).get("csrftoken")?.value ?? "";
  return (
    <div className="mx-auto w-full max-w-[28rem]" data-tarjeta-cuenta="">
      <h1 className="mb-6 text-center text-3xl font-semibold">{msg("rot.ingresar")}</h1>
      <FormularioCuenta accion={ingresar} siguiente={seguro || undefined} csrf={csrf} />
      <Alternativa
        texto={msg("cuenta.ir_a_registro")}
        href={seguro ? `/registrarse/?next=${encodeURIComponent(seguro)}` : "/registrarse/"}
      />
    </div>
  );
}
