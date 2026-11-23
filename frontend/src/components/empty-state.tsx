/**
 * EmptyState ([003] RN-06, AC-8.1 a AC-8.4, FR-025, FR-026, contracts/componentes.md): mismo
 * marcado que `templates/ui/_estado_vacio.html`. `sin_resultados` nombra el filtro y ofrece
 * "Limpiar filtros"; `sin_datos` ofrece una acción solo si el perfil la tiene permitida.
 */
import Link from "next/link";

import { Icono, type NombreIcono } from "@/components/icono";
import { boton, vacio } from "@/components/ui/variantes";
import { msg } from "@/lib/mensajes";

type Accion = { texto: string; href: string; icono?: NombreIcono };

export function EmptyState({
  variante = "sin_datos",
  icono,
  titulo,
  explicacion,
  nota,
  limpiarHref,
  accion,
  accionSecundaria,
}: {
  variante?: "sin_datos" | "sin_resultados";
  icono?: NombreIcono;
  titulo: string;
  explicacion?: string;
  nota?: string;
  limpiarHref?: string;
  accion?: Accion;
  accionSecundaria?: Accion;
}) {
  const nombreIcono = icono ?? (variante === "sin_resultados" ? "filter-x" : "info");
  return (
    <div
      className={vacio({ variante })}
      data-estado-vacio={variante}
      data-icono-vacio={nombreIcono}
    >
      <span className="flex size-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
        <Icono nombre={nombreIcono} className="size-8" />
      </span>
      <h2 className="m-0 text-xl font-semibold">{titulo}</h2>
      {explicacion && <p className="m-0 max-w-prose text-muted-foreground">{explicacion}</p>}
      {variante === "sin_resultados" && limpiarHref && (
        <div className="mt-2">
          <Link href={limpiarHref} className={boton({ variante: "secundario" })}>
            <Icono nombre="filter-x" />
            <span>{msg("vacio.filtro.accion")}</span>
          </Link>
        </div>
      )}
      {variante === "sin_datos" && (accion || accionSecundaria) && (
        <div className="mt-2 flex flex-wrap justify-center gap-3">
          {accion && (
            <Link href={accion.href} className={boton({ variante: "principal" })}>
              <Icono nombre={accion.icono ?? "plus"} />
              <span>{accion.texto}</span>
            </Link>
          )}
          {accionSecundaria && (
            <Link href={accionSecundaria.href} className={boton({ variante: "secundario" })}>
              <span>{accionSecundaria.texto}</span>
            </Link>
          )}
        </div>
      )}
      {nota && <p className="m-0 max-w-prose text-sm text-muted-foreground">{nota}</p>}
    </div>
  );
}
