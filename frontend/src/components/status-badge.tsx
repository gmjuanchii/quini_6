/**
 * StatusBadge ([003] AC-1.1, AC-1.2, FR-001, FR-002, contracts/componentes.md): el mismo marcado y
 * clases que `templates/ui/_insignia_estado.html`. Texto + icono + color; la explicación (RN-02)
 * aparece al cursor y al foco, y el lector de pantalla la lee por `aria-describedby`. Funciona sin
 * scripts (solo CSS).
 */
import { Icono, type NombreIcono } from "@/components/icono";
import { insignia } from "@/components/ui/variantes";
import { cn } from "@/lib/utils";

export type Etiqueta = {
  valor: "en_curso" | "finalizada" | "con_advertencias" | "sin_sorteos" | "con_error";
  slug: string;
  texto: string;
  explicacion: string;
  variante: "info" | "success" | "warning" | "neutral" | "danger";
  requiere_revision: boolean;
};

/** data-model § 2: icono de cada etiqueta. */
export const ICONO_ETIQUETA: Record<Etiqueta["valor"], NombreIcono> = {
  en_curso: "loader-circle",
  finalizada: "circle-check",
  con_advertencias: "triangle-alert",
  sin_sorteos: "circle-dashed",
  con_error: "circle-x",
};

export function StatusBadge({ etiqueta, id }: { etiqueta: Etiqueta; id: string | number }) {
  const icono = ICONO_ETIQUETA[etiqueta.valor];
  return (
    <span className="group relative inline-flex" data-insignia-estado={etiqueta.slug}>
      <span
        tabIndex={0}
        className={cn(
          insignia({ variante: etiqueta.variante }),
          "cursor-help focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
        )}
        aria-describedby={`explicacion-${id}`}
      >
        <Icono
          nombre={icono}
          className={cn("size-4 shrink-0", icono === "loader-circle" && "motion-safe:animate-spin")}
        />
        <span>{etiqueta.texto}</span>
      </span>
      <span
        role="tooltip"
        id={`explicacion-${id}`}
        className="absolute top-full left-0 z-20 mt-2 hidden w-64 max-w-[calc(100vw-2rem)] rounded-control bg-foreground px-3 py-2 text-sm font-normal text-background shadow-2 group-focus-within:block group-hover:block"
      >
        {etiqueta.explicacion}
      </span>
    </span>
  );
}
