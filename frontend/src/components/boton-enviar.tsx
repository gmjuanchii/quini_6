"use client";

/**
 * Botón de envío con el estado "trabajando" mientras la Server Action responde ([003] FR-034,
 * AC-13.4): indicador + texto "…ando…", `aria-busy` y no pulsable (sin doble envío, FR-031).
 */
import { useFormStatus } from "react-dom";

import { Button, type ButtonProps } from "@/components/ui/button";

export function BotonEnviar({
  textoTrabajando,
  trabajando,
  ...props
}: ButtonProps & { textoTrabajando: string }) {
  const { pending } = useFormStatus();
  return (
    <Button
      type="submit"
      trabajando={pending || trabajando}
      textoTrabajando={textoTrabajando}
      {...props}
    />
  );
}
