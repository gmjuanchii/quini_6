"use client";

/** Error inesperado con el texto de `templates/500.html` ([003] FR-041). */
import { PaginaDeError } from "@/components/sin-permisos";

export default function ErrorInesperado() {
  return <PaginaDeError titulo="gral.titulo_error" texto="gral.error" />;
}
