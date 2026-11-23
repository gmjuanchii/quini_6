/**
 * Button ([003] contracts/componentes.md, R-04): shadcn/ui con las clases de `ui/variantes.json`
 * (las mismas de `templates/ui/_boton.html`). Estado "trabajando": `trabajando` + `textoTrabajando`
 * → indicador, texto "…ando…", `aria-busy` y no pulsable (FR-034).
 *
 * Acepta también `variant`/`size` de shadcn/ui para los componentes copiados (calendario, diálogo),
 * traducidos a las variantes propias.
 */
import * as React from "react";
import { Slot } from "radix-ui";

import { Icono, type NombreIcono } from "@/components/icono";
import { cn } from "@/lib/utils";

import { boton, type VariantesBoton } from "./variantes";

type VarianteShadcn = "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
type TamanoShadcn = "default" | "xs" | "sm" | "lg" | "icon" | "icon-xs" | "icon-sm" | "icon-lg";

const DESDE_SHADCN: Record<VarianteShadcn, NonNullable<VariantesBoton["variante"]>> = {
  default: "principal",
  destructive: "destructivo",
  outline: "secundario",
  secondary: "secundario",
  ghost: "fantasma",
  link: "enlace",
};

/** Clases de botón con los nombres de shadcn/ui (los usa `calendar.tsx`). */
export function buttonVariants({
  variant = "default",
  size = "default",
  className,
}: { variant?: VarianteShadcn | null; size?: TamanoShadcn | null; className?: string } = {}) {
  const icono = size?.startsWith("icon");
  return cn(
    boton({
      variante: DESDE_SHADCN[variant ?? "default"],
      tamano: size === "default" || size === "lg" ? "md" : "sm",
    }),
    icono && "min-w-9 px-0",
    className,
  );
}

export type ButtonProps = React.ComponentProps<"button"> &
  VariantesBoton & {
    asChild?: boolean;
    variant?: VarianteShadcn | null;
    size?: TamanoShadcn | null;
    icono?: NombreIcono;
    /** FR-034: muestra el indicador y `textoTrabajando`, con `aria-busy` y sin poder pulsarse. */
    trabajando?: boolean;
    textoTrabajando?: string;
  };

function Button({
  className,
  variante,
  tamano,
  variant,
  size,
  asChild = false,
  icono,
  trabajando = false,
  textoTrabajando,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot.Root : "button";
  const clases =
    variant || size
      ? buttonVariants({ variant, size, className })
      : cn(boton({ variante, tamano }), className);

  if (asChild) {
    return (
      <Comp data-slot="button" className={clases} {...props}>
        {children}
      </Comp>
    );
  }

  return (
    <Comp
      data-slot="button"
      className={clases}
      disabled={disabled || trabajando}
      aria-busy={trabajando || undefined}
      data-texto-trabajando={textoTrabajando}
      {...props}
    >
      {trabajando ? (
        <Icono nombre="loader-circle" className="size-5 shrink-0 motion-safe:animate-spin" />
      ) : (
        icono && <Icono nombre={icono} />
      )}
      {trabajando && textoTrabajando ? <span>{textoTrabajando}</span> : children}
    </Comp>
  );
}

export { Button };
