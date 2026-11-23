"use client";

/**
 * TanStack Query solo donde hay datos en vivo ([003] R-10, R-15, R-24): el avance de la extracción
 * propia en curso (`ProgressPanel`), sin reintentos automáticos de mutaciones (R-11). Vive en el
 * segmento de la Extracción histórica y no en la estructura común, para que las demás pantallas no
 * descarguen la biblioteca (presupuesto de JavaScript inicial).
 */
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

export function ProveedorConsultas({ children }: { children: ReactNode }) {
  const [cliente] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { staleTime: 0, refetchOnWindowFocus: false },
          mutations: { retry: false },
        },
      }),
  );
  return <QueryClientProvider client={cliente}>{children}</QueryClientProvider>;
}
