"use client";

/**
 * Panel del calendario ([003] R-07, R-24, contracts/componentes.md): el Popover de shadcn/ui (Radix,
 * `role="dialog"`) con el calendario en español. Se importa solo desde `calendario-diferido.tsx`:
 * el Popover, react-day-picker y date-fns se descargan recién al abrir el calendario (o al acercar el
 * puntero o el foco a "Abrir calendario"), así las pantallas con fechas no suman unos 60 kB
 * comprimidos de JavaScript inicial.
 *
 * Se ancla al campo con `virtualRef` (el campo y su botón ya están en la página, dibujados por el
 * servidor). El botón no es un `PopoverTrigger`: un clic en él no cuenta como "afuera", para que
 * cierre en lugar de cerrar y volver a abrir.
 */
import type { ComponentProps, RefObject } from "react";

import { Popover, PopoverAnchor, PopoverContent } from "@/components/ui/popover";
import CalendarioEs from "@/components/ui/calendario-es";

export type PropsPanelCalendario = {
  /** Elemento que ubica el panel (el campo o la fila de los dos campos del período). */
  ancla: RefObject<HTMLElement | null>;
  /** Botones "Abrir calendario": un clic en ellos no cierra el panel por "clic afuera". */
  disparadores: RefObject<HTMLElement | null>[];
  abierto: boolean;
  alCambiar: (abierto: boolean) => void;
  /** Al cerrar, el foco vuelve aquí (el campo de origen). */
  alCerrarFoco: () => void;
  etiquetadoPor: string;
  className?: string;
  calendario: ComponentProps<typeof CalendarioEs>;
};

export default function PanelCalendario({
  ancla,
  disparadores,
  abierto,
  alCambiar,
  alCerrarFoco,
  etiquetadoPor,
  className,
  calendario,
}: PropsPanelCalendario) {
  return (
    <Popover open={abierto} onOpenChange={alCambiar}>
      <PopoverAnchor virtualRef={ancla as RefObject<HTMLElement>} />
      <PopoverContent
        align="start"
        aria-labelledby={etiquetadoPor}
        className={className}
        onInteractOutside={(e) => {
          const objetivo = e.target as Node | null;
          if (disparadores.some((d) => d.current?.contains(objetivo))) e.preventDefault();
        }}
        onCloseAutoFocus={(e) => {
          e.preventDefault();
          alCerrarFoco();
        }}
      >
        <CalendarioEs {...calendario} autoFocus />
      </PopoverContent>
    </Popover>
  );
}
