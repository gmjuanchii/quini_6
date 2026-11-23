"use client";

/**
 * Contenido que solo existe sin scripts ([003] componentes.md § 4, NFR-007): el servidor lo dibuja
 * y, al hidratar, se quita del documento (no solo se oculta), como hace Django al pasar los avisos
 * de la página a Toast (RN-09).
 */
import type { ReactNode } from "react";

import { useHidratado } from "@/lib/hidratado";

export function SoloSinScripts({ children }: { children: ReactNode }) {
  return useHidratado() ? null : <>{children}</>;
}
