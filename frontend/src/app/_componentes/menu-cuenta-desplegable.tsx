"use client";

/**
 * Parte con scripts del AccountMenu ([003] AC-5.3): el mismo comportamiento que `menuCuenta` de
 * static/js/ui.js en Django. El botón despliega un panel (no un `role="menu"`); al abrir, el foco
 * va a "Salir"; Escape cierra y devuelve el foco al botón; un clic afuera cierra. Sin scripts, el
 * botón no se muestra y el panel queda visible (componentes.md § 4).
 */
import { useEffect, useRef, useState, type ReactNode } from "react";

import { boton } from "@/components/ui/variantes";
import { cn } from "@/lib/utils";

export function MenuCuenta({
  nombre,
  correo,
  disparador,
  children,
}: {
  nombre: string;
  correo: string;
  disparador: ReactNode;
  children: ReactNode;
}) {
  const [abierto, setAbierto] = useState(false);
  const raiz = useRef<HTMLDivElement>(null);
  const botonRef = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!abierto) return;
    panel.current?.querySelector<HTMLElement>('button[type="submit"]')?.focus();
    const afuera = (e: MouseEvent) => {
      if (raiz.current && !raiz.current.contains(e.target as Node)) setAbierto(false);
    };
    document.addEventListener("click", afuera);
    return () => document.removeEventListener("click", afuera);
  }, [abierto]);

  return (
    <div
      ref={raiz}
      className="relative"
      data-menu-cuenta=""
      onKeyDown={(e) => {
        if (e.key === "Escape" && abierto) {
          e.preventDefault();
          e.stopPropagation();
          setAbierto(false);
          botonRef.current?.focus();
        }
      }}
    >
      <button
        ref={botonRef}
        type="button"
        className={cn("solo-con-scripts", boton({ variante: "fantasma" }), "max-w-full gap-2 px-3")}
        aria-label={nombre}
        title={correo}
        aria-haspopup="true"
        aria-controls="menu-cuenta"
        aria-expanded={abierto}
        onClick={() => setAbierto((a) => !a)}
      >
        {disparador}
      </button>
      <div
        id="menu-cuenta"
        ref={panel}
        className="menu-cuenta-q"
        data-abierto={abierto ? "" : undefined}
      >
        {children}
      </div>
    </div>
  );
}
