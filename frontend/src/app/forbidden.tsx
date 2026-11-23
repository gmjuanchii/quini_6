import type { Metadata } from "next";

import { SinPermisos } from "@/components/sin-permisos";
import { msg } from "@/lib/mensajes";

export const metadata: Metadata = { title: msg("gral.titulo_sin_permisos") };

/** 403 cuando Django responde que la cuenta no tiene permisos ([003] AC-14.1, R-19). */
export default function Prohibido() {
  return <SinPermisos />;
}
