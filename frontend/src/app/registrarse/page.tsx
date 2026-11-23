/**
 * Crear cuenta en Next.js ([001] AC-3.1 a AC-3.3; [003] HU-06, FR-031, pantalla 5): el mismo
 * contenido que `templates/cuentas/registrarse.html`. Al crearla, Django ingresa con la cuenta nueva.
 */
import type { Metadata } from "next";
import { cookies } from "next/headers";

import { msg } from "@/lib/mensajes";
import { nuevaClaveIdempotencia } from "@/lib/acciones";

import { crearCuenta } from "../ingresar/acciones";
import { Alternativa } from "../ingresar/_componentes/alternativa";
import { FormularioCuenta } from "../ingresar/_componentes/formulario-cuenta";

export const metadata: Metadata = { title: msg("rot.crear_cuenta") };

function uno(valor: string | string[] | undefined): string {
  return (Array.isArray(valor) ? valor[0] : valor) ?? "";
}

export default async function Registrarse({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const siguiente = uno((await searchParams).next);
  const seguro = siguiente.startsWith("/") && !siguiente.startsWith("//") ? siguiente : "";
  const csrf = (await cookies()).get("csrftoken")?.value ?? "";
  return (
    <div className="mx-auto w-full max-w-[28rem]" data-tarjeta-cuenta="">
      <h1 className="mb-2 text-center text-3xl font-semibold">{msg("rot.crear_cuenta")}</h1>
      <p className="mb-6 text-center text-muted-foreground">{msg("rot.crear_cuenta_intro")}</p>
      <FormularioCuenta
        accion={crearCuenta}
        registro
        siguiente={seguro || undefined}
        clave={nuevaClaveIdempotencia()}
        csrf={csrf}
      />
      <Alternativa
        texto={msg("cuenta.ir_a_ingreso")}
        href={seguro ? `/ingresar/?next=${encodeURIComponent(seguro)}` : "/ingresar/"}
      />
    </div>
  );
}
