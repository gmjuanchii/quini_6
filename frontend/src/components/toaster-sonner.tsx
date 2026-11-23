"use client";

/**
 * La región de Toast con Sonner ([003] contracts/componentes.md, RN-09): el mismo marcado y clases
 * que `templates/ui/_avisos.html`. Se importa solo desde `toaster.tsx`, recién con el primer aviso
 * (R-24): una pantalla sin avisos no descarga Sonner.
 */
import { useEffect } from "react";
import { Toaster as Sonner, toast as sonner } from "sonner";

import { Icono, type NombreIcono } from "@/components/icono";
import {
  DURACION_AVISO_MS,
  registrarMostrador,
  type AvisoPedido,
  type TipoAviso,
} from "@/components/toaster";
import { boton, toast as claseToast } from "@/components/ui/variantes";
import { cn } from "@/lib/utils";

const VARIANTE = {
  exito: "success",
  info: "info",
  advertencia: "warning",
  error: "error",
} as const;
const ICONO: Record<TipoAviso, { nombre: NombreIcono; clase: string }> = {
  exito: { nombre: "circle-check", clase: "text-success-icon" },
  info: { nombre: "info", clase: "text-primary" },
  advertencia: { nombre: "triangle-alert", clase: "text-warning-icon" },
  error: { nombre: "circle-x", clase: "text-danger-icon" },
};

function mostrar({ aviso, etiquetaCerrar }: AvisoPedido): void {
  sonner.custom(
    (id) => (
      // Como `templates/ui/_avisos.html`: el rol (status o alert) en el contenedor y el aviso adentro.
      <div role={aviso.tipo === "error" ? "alert" : "status"}>
        <div className={cn(claseToast({ variante: VARIANTE[aviso.tipo] }))} data-aviso-toast="">
          <Icono
            nombre={ICONO[aviso.tipo].nombre}
            className={cn("size-5 shrink-0", ICONO[aviso.tipo].clase)}
          />
          <div className="min-w-0 flex-1">
            <p className="m-0">{aviso.texto}</p>
          </div>
          <button
            type="button"
            className={cn(boton({ variante: "fantasma", tamano: "sm" }), "-m-2 min-w-9 px-2")}
            aria-label={etiquetaCerrar}
            onClick={() => sonner.dismiss(id)}
          >
            <Icono nombre="x" className="size-4" />
          </button>
        </div>
      </div>
    ),
    {
      // El mismo aviso mostrado dos veces seguidas (p. ej. por una redirección repetida) se
      // reemplaza en lugar de duplicarse.
      id: `${aviso.tipo}:${aviso.texto}`,
      duration: aviso.tipo === "error" ? Infinity : DURACION_AVISO_MS,
    },
  );
}

export default function ToasterSonner({ etiquetaRegion }: { etiquetaRegion: string }) {
  // Los efectos de los hijos corren antes: Sonner ya escucha cuando se muestran los pendientes.
  useEffect(() => registrarMostrador(mostrar), []);
  return (
    <Sonner
      position="bottom-right"
      gap={8}
      visibleToasts={5}
      // Uno debajo del otro, como en Django: apilados, un aviso taparía el "Cerrar aviso" del otro
      // (tamaño mínimo del objetivo, WCAG 2.5.8).
      expand
      toastOptions={{ unstyled: true }}
      // Nombre de la región en español (Sonner usa "Notifications" por omisión).
      containerAriaLabel={etiquetaRegion}
      hotkey={[]}
    />
  );
}
