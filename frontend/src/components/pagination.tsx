/**
 * Pagination ([003] AC-9.2, RN-07, contracts/componentes.md): igual que `templates/ui/_paginacion.html`.
 * Enlaces con los parámetros actuales (filtro y orden), así funciona sin scripts. Solo se muestra si
 * hay más de una página.
 */
import Link from "next/link";

import { Icono } from "@/components/icono";
import { msg } from "@/lib/mensajes";
import { conParametros, type Parametros } from "@/lib/tablas";
import { cn } from "@/lib/utils";

const ENLACE =
  "inline-flex min-h-control items-center gap-2 rounded-control border border-border bg-surface px-3 font-medium text-foreground no-underline hover:bg-muted";

export function Pagination({
  pagina,
  paginas,
  parametros,
}: {
  pagina: number;
  paginas: number;
  parametros: Parametros;
}) {
  if (paginas <= 1) return null;
  const anterior = pagina > 1;
  const siguiente = pagina < paginas;
  return (
    <nav aria-label="Paginación" className="flex flex-wrap items-center justify-between gap-3">
      {anterior ? (
        <Link
          href={conParametros(parametros, { pagina: pagina - 1 })}
          className={ENLACE}
          rel="prev"
        >
          <Icono nombre="arrow-left" />
          <span>{msg("pag.anterior")}</span>
        </Link>
      ) : (
        <a className={cn(ENLACE, "pointer-events-none opacity-50")} aria-disabled="true">
          <Icono nombre="arrow-left" />
          <span>{msg("pag.anterior")}</span>
        </a>
      )}
      <p className="m-0 text-sm text-muted-foreground">
        {msg("pag.pagina", { n: pagina, m: paginas })}
      </p>
      {siguiente ? (
        <Link
          href={conParametros(parametros, { pagina: pagina + 1 })}
          className={ENLACE}
          rel="next"
        >
          <span>{msg("pag.siguiente")}</span>
          <Icono nombre="arrow-right" />
        </Link>
      ) : (
        <a className={cn(ENLACE, "pointer-events-none opacity-50")} aria-disabled="true">
          <span>{msg("pag.siguiente")}</span>
          <Icono nombre="arrow-right" />
        </a>
      )}
    </nav>
  );
}
