/** Carga de premios de una modalidad ([001] US2; [003] FR-041, pantalla 6). Ver `../_bloque.tsx`. */
import type { Metadata } from "next";

import { msg } from "@/lib/mensajes";

import { PaginaBloque } from "../_bloque";

export const metadata: Metadata = { title: msg("rot.premios") };

export default async function Pagina({
  params,
}: {
  params: Promise<{ numero: string; modalidad: string }>;
}) {
  const { numero, modalidad } = await params;
  return <PaginaBloque numero={Number(numero) || 0} modalidad={modalidad} bloque="premios" />;
}
