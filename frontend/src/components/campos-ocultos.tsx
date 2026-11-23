/**
 * Campos ocultos de los formularios POST que atiende Django desde una página de Next.js (`/salir/`,
 * `/preferencias/tema/` hasta la pantalla 5) y de los formularios de Server Actions.
 */
import { cookies } from "next/headers";

import { nuevaClaveIdempotencia } from "@/lib/acciones";

/** `csrfmiddlewaretoken` con el valor de la cookie `csrftoken` de Django (R-19). La cookie la
 * entrega `proxy.ts` en la primera visita. */
export async function CampoCsrf() {
  const token = (await cookies()).get("csrftoken")?.value ?? "";
  return <input type="hidden" name="csrfmiddlewaretoken" value={token} />;
}

/** `clave_idempotencia` nueva por formulario mostrado (R-11, CHK011). */
export function CampoIdempotencia() {
  return <input type="hidden" name="clave_idempotencia" value={nuevaClaveIdempotencia()} />;
}
