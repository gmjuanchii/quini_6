/**
 * AccountMenu ([003] contracts/componentes.md, AC-5.3, FR-015, FR-030): botón con el correo
 * abreviado (completo en `title` y en el nombre accesible) que despliega "Salir", un formulario POST
 * a `/salir/` que atiende Django (hasta la pantalla 5) y cierra la sesión en ambas interfaces
 * (AC-14.2). Mismo marcado que `templates/ui/_menu_cuenta.html`.
 */
import { CampoCsrf } from "@/components/campos-ocultos";
import { Icono } from "@/components/icono";
import { boton } from "@/components/ui/variantes";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

import { MenuCuenta } from "./menu-cuenta-desplegable";

export function AccountMenu({ correo }: { correo: string }) {
  return (
    <MenuCuenta
      nombre={msg("nav.cuenta", { correo })}
      correo={correo}
      disparador={
        <>
          <Icono nombre="circle-user-round" />
          <span className="max-w-[16ch] truncate">{correo}</span>
        </>
      }
    >
      <div className="flex flex-col gap-1 rounded-control border border-border bg-surface p-2 md:min-w-56 md:shadow-2">
        <p className="truncate px-3 py-2 text-sm text-muted-foreground" title={correo}>
          {correo}
        </p>
        <form method="post" action="/salir/" className="m-0">
          <CampoCsrf />
          <button
            type="submit"
            className={cn(boton({ variante: "fantasma" }), "w-full justify-start px-3")}
          >
            {msg("nav.salir")}
          </button>
        </form>
      </div>
    </MenuCuenta>
  );
}
