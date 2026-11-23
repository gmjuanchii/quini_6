/** Pie ([003] AC-10.2): texto legal (14 px, contraste ≥ 4,5:1) y selector de tema, como Django. */
import { msg } from "@/lib/mensajes";
import type { Tema } from "@/lib/tema";

import { ThemeSelect } from "./theme-select";

export function Pie({ tema, ruta }: { tema: Tema; ruta: string }) {
  return (
    <footer className="mt-12 border-t border-border bg-surface">
      <div className="contenedor flex flex-col gap-4 py-6">
        <p className="m-0 text-sm text-muted-foreground" data-pie-legal="">
          {msg("pie.legal")}
        </p>
        <ThemeSelect actual={tema} ruta={ruta} />
      </div>
    </footer>
  );
}
