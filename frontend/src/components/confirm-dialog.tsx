"use client";

/**
 * ConfirmDialog ([003] AC-2.3 a AC-2.5, FR-008, FR-009, contracts/componentes.md): AlertDialog de
 * shadcn/ui (`role="alertdialog"`). El contenido es el mismo de la página de confirmación aparte
 * (sin scripts); aquí lo muestra la ruta interceptada (R-18). Foco inicial en "Cancelar"
 * (`[data-cancelar]`); Escape, "Cancelar" o clic afuera cierran sin efecto y vuelven al listado.
 */
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { devolverFocoAlMenu } from "@/components/action-menu";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export function ConfirmDialog({
  titulo,
  texto,
  children,
}: {
  titulo: string;
  texto: string;
  /** Detalle, consecuencias y el formulario con "Cancelar" (`data-cancelar`) y la acción. */
  children: ReactNode;
}) {
  const router = useRouter();
  const cerrar = () => {
    router.back();
    devolverFocoAlMenu(); // AC-2.3: el foco vuelve al botón ⋮ de origen
  };
  return (
    <AlertDialog defaultOpen onOpenChange={(abierto) => !abierto && cerrar()}>
      <AlertDialogContent
        className="max-w-formulario"
        onClickCapture={(e) => {
          // "Cancelar" es un enlace al listado (sin scripts); en el diálogo, solo lo cierra.
          if ((e.target as HTMLElement).closest("[data-cancelar]")) {
            e.preventDefault();
            cerrar();
          }
        }}
        onOpenAutoFocus={(e) => {
          e.preventDefault();
          (e.currentTarget as HTMLElement).querySelector<HTMLElement>("[data-cancelar]")?.focus();
        }}
      >
        <div className="flex flex-col gap-4" data-confirmacion="">
          <AlertDialogTitle id="dialogo-titulo" className="text-2xl font-semibold">
            {titulo}
          </AlertDialogTitle>
          <AlertDialogDescription id="dialogo-texto" className="font-medium text-foreground">
            {texto}
          </AlertDialogDescription>
          {children}
        </div>
      </AlertDialogContent>
    </AlertDialog>
  );
}
