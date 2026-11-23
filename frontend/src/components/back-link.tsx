/**
 * BackLink ([003] AC-5.6, FR-017, contracts/componentes.md): camino de regreso con el nombre del
 * destino, igual que `templates/ui/_volver.html`. La "← " del texto del catálogo la reemplaza el
 * icono (decorativo).
 */
import Link from "next/link";

import { Icono } from "@/components/icono";

export function sinFlecha(texto: string): string {
  return texto.replace(/^←\s*/, "");
}

export function BackLink({ href, texto }: { href: string; texto: string }) {
  return (
    <p className="mb-4">
      <Link
        data-volver=""
        href={href}
        className="inline-flex min-h-control items-center gap-1.5 rounded-control font-medium text-primary no-underline hover:underline focus-visible:underline"
      >
        <Icono nombre="arrow-left" className="size-4 shrink-0" />
        <span>{sinFlecha(texto)}</span>
      </Link>
    </p>
  );
}
