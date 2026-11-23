import type { Metadata } from "next";

import { PaginaDeError } from "@/components/sin-permisos";
import { msg } from "@/lib/mensajes";

export const metadata: Metadata = { title: msg("gral.titulo_pagina_inexistente") };

/** 404 con el mismo diseño y texto que `templates/404.html` ([003] FR-041). */
export default function NoEncontrada() {
  return <PaginaDeError titulo="gral.titulo_pagina_inexistente" texto="gral.pagina_inexistente" />;
}
