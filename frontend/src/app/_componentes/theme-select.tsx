/**
 * ThemeSelect ([003] contracts/componentes.md, AC-12.1 a AC-12.3, FR-036, R-14): el mismo
 * formulario POST `/preferencias/tema/` de `templates/ui/_selector_tema.html` (lo atiende Django
 * hasta la pantalla 5). Sin scripts, "Guardar tema" lo envía; con scripts, cada opción aplica el
 * tema al instante y escribe la misma cookie, sin recargar.
 */
import { CampoCsrf } from "@/components/campos-ocultos";
import { Icono, type NombreIcono } from "@/components/icono";
import { boton } from "@/components/ui/variantes";
import { msg, type ClaveMensaje } from "@/lib/mensajes";
import type { Tema } from "@/lib/tema";

import { OpcionTema } from "./opcion-tema";

const OPCIONES: { valor: Tema; clave: ClaveMensaje; icono: NombreIcono }[] = [
  { valor: "claro", clave: "tema.claro", icono: "sun" },
  { valor: "oscuro", clave: "tema.oscuro", icono: "moon" },
  { valor: "dispositivo", clave: "tema.dispositivo", icono: "monitor" },
];

const CLASE_OPCION =
  "inline-flex min-h-control cursor-pointer items-center gap-2 rounded-control px-2 text-sm text-foreground hover:bg-muted has-[:checked]:bg-info-soft has-[:checked]:text-info-on-soft has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-ring";

export function ThemeSelect({ actual, ruta }: { actual: Tema; ruta: string }) {
  return (
    <form method="post" action="/preferencias/tema/" className="m-0">
      <CampoCsrf />
      <input type="hidden" name="next" value={ruta} />
      <fieldset className="m-0 flex flex-wrap items-center gap-x-4 gap-y-2 border-0 p-0">
        <legend className="float-left mr-2 p-0 text-sm font-medium">{msg("tema.titulo")}</legend>
        {OPCIONES.map((o) => (
          <label key={o.valor} className={CLASE_OPCION}>
            <OpcionTema valor={o.valor} marcada={actual === o.valor} />
            <Icono nombre={o.icono} className="size-4 shrink-0" />
            {msg(o.clave)}
          </label>
        ))}
        <span className="solo-sin-scripts">
          <button type="submit" className={boton({ variante: "secundario", tamano: "sm" })}>
            <span>{msg("tema.guardar")}</span>
          </button>
        </span>
      </fieldset>
    </form>
  );
}
