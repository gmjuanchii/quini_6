"use client";

/**
 * Menú móvil del NavBar ([003] AC-5.4): por debajo de 768 px, botón "Menú" con `aria-expanded` que
 * despliega las secciones; Escape lo cierra y devuelve el foco al botón. Sin scripts, la lista
 * queda siempre visible y el botón no se muestra (NFR-007, componentes.md § 4).
 */
import { useRef, useState, type ReactNode } from "react";

import { Icono } from "@/components/icono";
import { boton } from "@/components/ui/variantes";
import { cn } from "@/lib/utils";

export function NavegacionMovil({
  logotipo,
  textoMenu,
  etiquetaNavegacion,
  children,
}: {
  logotipo: ReactNode;
  textoMenu: string;
  etiquetaNavegacion: string;
  children: ReactNode;
}) {
  const [abierto, setAbierto] = useState(false);
  const botonRef = useRef<HTMLButtonElement>(null);

  return (
    <div
      className="contenedor flex min-h-16 flex-wrap items-center gap-x-6 gap-y-2 py-2"
      onKeyDown={(e) => {
        if (e.key === "Escape" && abierto) {
          setAbierto(false);
          botonRef.current?.focus();
        }
      }}
    >
      {logotipo}
      <button
        ref={botonRef}
        type="button"
        data-boton-menu=""
        className={cn("solo-con-scripts", boton({ variante: "secundario" }), "ml-auto md:hidden")}
        aria-controls="nav-principal"
        aria-expanded={abierto}
        onClick={() => setAbierto((a) => !a)}
      >
        <Icono nombre={abierto ? "x" : "menu"} />
        <span>{textoMenu}</span>
      </button>
      <nav
        id="nav-principal"
        aria-label={etiquetaNavegacion}
        className="nav-q w-full md:flex md:w-auto md:flex-1 md:items-center md:gap-6"
        data-abierta={abierto ? "" : undefined}
      >
        {children}
      </nav>
    </div>
  );
}
