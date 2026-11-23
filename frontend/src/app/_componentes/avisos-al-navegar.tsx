"use client";

/**
 * Avisos al navegar sin recargar ([003] FR-043, R-31, RN-09): en una navegación del cliente (un
 * enlace, una redirección que el enrutador de Next.js sigue sin recargar) la estructura común no se
 * vuelve a dibujar en el servidor, así que los avisos que Django dejó en la sesión se piden aquí, al
 * cambiar de dirección, y se muestran como Toast. Django entrega cada aviso una sola vez: nunca se
 * repite uno que ya mostró la página.
 */
import { usePathname, useSearchParams } from "next/navigation";
import { useEffect } from "react";

import { apiNavegador } from "@/api/navegador";
import { mostrarAviso } from "@/components/toaster";
import { msg } from "@/lib/mensajes";

export function AvisosAlNavegar() {
  const ruta = usePathname();
  const parametros = useSearchParams();
  const direccion = `${ruta}?${parametros.toString()}`;

  useEffect(() => {
    // También al montar: si la página llegó por una redirección que el enrutador siguió antes de
    // hidratar, sus avisos siguen en la sesión (los que ya mostró el servidor no vuelven: Django
    // entrega cada uno una sola vez).
    // Lo leído se muestra siempre: Django ya lo marcó como leído y no lo volvería a entregar.
    void apiNavegador.GET("/api/v1/avisos/").then(({ data }) => {
      for (const aviso of data ?? []) mostrarAviso(aviso, msg("aviso.cerrar"));
    });
  }, [direccion]);

  return null;
}
