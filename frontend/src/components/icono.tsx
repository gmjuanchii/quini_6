/**
 * Iconos de la lista cerrada ([003] contracts/componentes.md § 2, R-05): los mismos de Lucide que
 * `templates/ui/iconos/`. Siempre decorativos (`aria-hidden`) y junto a un texto (AC-13.5).
 * Agregar un icono exige agregarlo primero a la tabla del contrato y a `scripts/iconos.mjs`.
 *
 * Se dibujan en línea con el contenido de esos mismos SVG (`iconos-svg.ts`, generado), igual que
 * `{% icono %}` en Django: el mismo marcado en las dos interfaces y sin la biblioteca de Lucide en
 * el JavaScript de todas las pantallas (unos 13 kB comprimidos, R-24).
 */
import { ICONOS_SVG, type NombreIcono } from "@/components/iconos-svg";
import { cn } from "@/lib/utils";

export type { NombreIcono };

export const NOMBRES_ICONOS = Object.keys(ICONOS_SVG) as NombreIcono[];

export function Icono({ nombre, className }: { nombre: NombreIcono; className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={cn("size-5 shrink-0", className)}
      aria-hidden="true"
      focusable="false"
      // Contenido fijo de los SVG versionados del proyecto (nunca datos de la persona).
      dangerouslySetInnerHTML={{ __html: ICONOS_SVG[nombre] }}
    />
  );
}
