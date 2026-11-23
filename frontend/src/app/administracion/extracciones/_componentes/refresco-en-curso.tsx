"use client";

/**
 * [003] R-10: mientras alguna fila del listado esté "En curso" (de otro administrador; la propia la
 * sigue el ProgressPanel), la página se vuelve a pedir cada 3 s, como las filas de Django con HTMX.
 * Sin scripts, el listado se actualiza al recargar.
 */
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { INTERVALO_AVANCE_MS } from "@/components/progress-panel";

export function RefrescoEnCurso() {
  const router = useRouter();
  useEffect(() => {
    const id = window.setInterval(() => router.refresh(), INTERVALO_AVANCE_MS);
    return () => window.clearInterval(id);
  }, [router]);
  return null;
}
