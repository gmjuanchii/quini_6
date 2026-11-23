/**
 * Destino interno de `proxy.ts` cuando Django informa que la cuenta no tiene permisos para una ruta
 * de administración: la página "Sin permisos" con 403, completa sin scripts ([003] AC-14.1,
 * NFR-007). El enrutador nunca entrega esta dirección a Next.js (no está en QUINI6_RUTAS_NEXT).
 */
import type { Metadata } from "next";

import { SinPermisos } from "@/components/sin-permisos";
import { msg } from "@/lib/mensajes";

export const metadata: Metadata = {
  title: msg("gral.titulo_sin_permisos"),
  robots: { index: false },
};

export default function PaginaSinPermisos() {
  return <SinPermisos />;
}
