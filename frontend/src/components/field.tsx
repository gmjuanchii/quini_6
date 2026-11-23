/**
 * Field ([003] FR-033, AC-7.3, NFR-001, contracts/componentes.md): etiqueta con `for`, ayuda y
 * error en `aria-describedby`, `aria-invalid`, error con icono y texto junto al campo. Mismas
 * clases que `templates/_campo.html` (`.campo`, `.control`, `.ayuda`, `.error`).
 */
import { cloneElement, type ReactElement, type ReactNode } from "react";

import { Icono } from "@/components/icono";
import { cn } from "@/lib/utils";

export function idsDe(id: string, ayuda?: string, error?: string) {
  const ids = [ayuda && `${id}_ayuda`, error && `${id}_error`].filter(Boolean).join(" ");
  return ids || undefined;
}

export function Field({
  id,
  etiqueta,
  ayuda,
  error,
  children,
  className,
}: {
  id: string;
  etiqueta: ReactNode;
  ayuda?: string;
  error?: string;
  /** El control (`<input>`, `<select>`…): recibe `id`, `aria-invalid` y `aria-describedby`. */
  children: ReactElement<Record<string, unknown>>;
  className?: string;
}) {
  const control = cloneElement(children, {
    id,
    "aria-invalid": error ? true : undefined,
    "aria-describedby": idsDe(id, ayuda, error),
  });
  return (
    <div
      className={cn("campo flex flex-col gap-1.5", error && "campo--error", className)}
      data-campo={id}
    >
      <label htmlFor={id} className="font-medium">
        {etiqueta}
      </label>
      {ayuda && (
        <p id={`${id}_ayuda`} className="ayuda text-sm text-muted-foreground">
          {ayuda}
        </p>
      )}
      {control}
      <p
        id={`${id}_error`}
        className="error flex items-start gap-1.5 text-sm font-medium text-danger-text"
        hidden={!error}
      >
        <Icono nombre="circle-x" className="mt-0.5 size-4 shrink-0" />
        <span data-texto-error="">{error}</span>
      </p>
    </div>
  );
}
