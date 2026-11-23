/**
 * Entrada de cada pantalla ([003] R-15, AC-13.1): aparición por opacidad en 200 ms con CSS
 * (tw-animate-css), así el contenido también se ve sin scripts (NFR-007). "Reducir movimiento" la
 * anula desde ui/base.css (AC-13.2).
 */
import type { ReactNode } from "react";

export default function Plantilla({ children }: { children: ReactNode }) {
  return <div className="animate-in fade-in duration-200">{children}</div>;
}
