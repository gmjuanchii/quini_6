/**
 * Callout ([003] contracts/componentes.md, RN-09): mismo marcado y clases que
 * `templates/ui/_aviso.html`. `rol` = `status` (info, éxito) o `alert` (error) cuando aparece tras
 * una acción; los avisos fijos van sin rol dinámico.
 */
import type { ReactNode } from "react";

import { Icono, type NombreIcono } from "@/components/icono";
import { aviso } from "@/components/ui/variantes";
import { cn } from "@/lib/utils";

export type VarianteCallout = "info" | "success" | "warning" | "danger";

const ICONO: Record<VarianteCallout, NombreIcono> = {
  success: "circle-check",
  warning: "triangle-alert",
  danger: "circle-x",
  info: "info",
};

export function Callout({
  variante = "info",
  texto,
  titulo,
  rol,
  id,
  className,
  children,
  ...datos
}: {
  variante?: VarianteCallout;
  /** Texto principal; puede faltar si el contenido va en `children`. */
  texto?: string;
  titulo?: string;
  rol?: "status" | "alert";
  id?: string;
  className?: string;
  children?: ReactNode;
} & Record<`data-${string}`, string | undefined>) {
  return (
    <div className={cn(aviso({ variante }), className)} role={rol} id={id} {...datos}>
      <Icono nombre={ICONO[variante]} />
      <div className="min-w-0 flex-1">
        {titulo && <p className="font-semibold">{titulo}</p>}
        {texto && <p data-texto-aviso="">{texto}</p>}
        {children}
      </div>
    </div>
  );
}
