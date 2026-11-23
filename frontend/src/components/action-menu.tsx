"use client";

/**
 * ActionMenu ⋮ ([003] AC-2.1, AC-2.2, FR-007, contracts/componentes.md): el mismo marcado que
 * `templates/ui/_menu_acciones.html` — `<details class="menu-acciones">` con `<summary>` (nombre
 * accesible "Acciones de la extracción del {fecha y hora}") y una lista `role="menu"` de enlaces
 * `role="menuitem"`. Sin scripts es el `<details>` nativo (NFR-007).
 *
 * Con scripts, el mismo comportamiento que el componente de Alpine de Django: al abrir, el foco va a
 * la primera opción; flechas, Inicio y Fin recorren; Escape cierra y devuelve el foco al botón; un
 * clic afuera cierra; abrir otro cierra el anterior; se abre debajo o encima del botón según quepa,
 * siempre dentro de la pantalla. (Como el AccountMenu, no se usa el DropdownMenu de Radix: cambiaría
 * el marcado y los guiones E2E dejarían de servir para ambas interfaces; research.md, Fase 19.)
 *
 * "Eliminar" (`data-confirmar`) lleva a la confirmación, que con scripts se muestra como diálogo
 * (ruta interceptada, R-18); al cerrarlo, el foco vuelve a este botón.
 */
import Link from "next/link";
import { useEffect, useRef, useState, type KeyboardEvent } from "react";

import { Icono, type NombreIcono } from "@/components/icono";
import { boton } from "@/components/ui/variantes";
import { cn } from "@/lib/utils";

export type OpcionMenu = {
  texto: string;
  href: string;
  icono?: NombreIcono;
  destructivo?: boolean;
  /** Abre la confirmación ([003] AC-2.3). */
  confirmar?: boolean;
  /** Ruta que no atiende Next.js (p. ej. el CSV que sirve Django): enlace común, sin `Link`. */
  externo?: boolean;
};

const EVENTO_ABIERTO = "quini6:menu-abierto";

/** Botón del último menú desde el que se abrió una confirmación (para devolverle el foco). */
let ultimoDisparador: HTMLElement | null = null;

export function devolverFocoAlMenu(): void {
  const destino = ultimoDisparador;
  if (!destino) return;
  window.setTimeout(() => {
    if (destino.isConnected) destino.focus();
  }, 0);
}

export function ActionMenu({ nombre, opciones }: { nombre: string; opciones: OpcionMenu[] }) {
  const detalles = useRef<HTMLDetailsElement>(null);
  const disparador = useRef<HTMLElement>(null);
  const lista = useRef<HTMLUListElement>(null);
  const [encima, setEncima] = useState(false);
  const [aLaIzquierda, setALaIzquierda] = useState(false);

  const items = () =>
    Array.from(lista.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? []);

  const cerrar = (devolverFoco: boolean) => {
    if (!detalles.current?.open) return;
    detalles.current.open = false;
    if (devolverFoco) disparador.current?.focus();
  };

  useEffect(() => {
    const otro = (e: Event) => {
      if ((e as CustomEvent).detail !== detalles.current) cerrar(false);
    };
    const afuera = (e: MouseEvent) => {
      if (detalles.current?.open && !detalles.current.contains(e.target as Node)) cerrar(false);
    };
    window.addEventListener(EVENTO_ABIERTO, otro);
    document.addEventListener("click", afuera);
    return () => {
      window.removeEventListener(EVENTO_ABIERTO, otro);
      document.removeEventListener("click", afuera);
    };
  }, []);

  const alCambiar = () => {
    const d = detalles.current;
    if (!d?.open) return;
    window.dispatchEvent(new CustomEvent(EVENTO_ABIERTO, { detail: d }));
    // Debajo del botón si cabe; si no, encima. Alineado al borde derecho del botón, o al izquierdo
    // si así no entra (siempre dentro de la pantalla).
    const b = disparador.current?.getBoundingClientRect();
    const caja = lista.current?.getBoundingClientRect();
    if (b && caja) {
      setEncima(b.bottom + caja.height + 8 > window.innerHeight && b.top - caja.height - 8 >= 0);
      setALaIzquierda(b.right - caja.width < 8);
    }
    items()[0]?.focus();
  };

  const mover = (paso: 1 | -1 | "primero" | "ultimo") => {
    const todos = items();
    if (todos.length === 0) return;
    const actual = todos.indexOf(document.activeElement as HTMLElement);
    let siguiente: number;
    if (paso === "primero") siguiente = 0;
    else if (paso === "ultimo") siguiente = todos.length - 1;
    else siguiente = (actual + paso + todos.length) % todos.length;
    todos[siguiente]?.focus();
  };

  const teclado = (e: KeyboardEvent<HTMLUListElement>) => {
    const acciones: Record<string, () => void> = {
      ArrowDown: () => mover(1),
      ArrowUp: () => mover(-1),
      Home: () => mover("primero"),
      End: () => mover("ultimo"),
    };
    const accion = acciones[e.key];
    if (accion) {
      e.preventDefault();
      accion();
    }
  };

  return (
    <details
      ref={detalles}
      className="menu-acciones relative inline-block"
      onToggle={alCambiar}
      onKeyDown={(e) => {
        if (e.key === "Escape" && detalles.current?.open) {
          e.preventDefault();
          e.stopPropagation();
          cerrar(true);
        }
      }}
    >
      <summary
        ref={disparador}
        aria-label={nombre}
        title={nombre}
        className={cn(
          boton({ variante: "fantasma" }),
          "min-w-control cursor-pointer list-none px-2 [&::-webkit-details-marker]:hidden",
        )}
      >
        <Icono nombre="ellipsis-vertical" />
      </summary>
      <div
        className={cn(
          "absolute z-30 py-1",
          aLaIzquierda ? "left-0" : "right-0",
          encima ? "bottom-full" : "top-full",
        )}
      >
        <ul
          ref={lista}
          role="menu"
          aria-label={nombre}
          onKeyDown={teclado}
          className="menu-acciones__lista !static !m-0 min-w-48 rounded-control border border-border bg-surface py-1 shadow-2"
        >
          {opciones.map((o) => {
            const clases = cn(
              "flex min-h-control items-center gap-2 px-3 font-medium no-underline hover:bg-muted focus-visible:bg-muted",
              o.destructivo ? "text-danger-text" : "text-foreground",
            );
            const contenido = (
              <>
                {o.icono && <Icono nombre={o.icono} className="size-4 shrink-0" />}
                <span>{o.texto}</span>
              </>
            );
            const comunes = {
              role: "menuitem",
              className: clases,
              "data-confirmar": o.confirmar ? "" : undefined,
              onClick: () => {
                if (o.confirmar) ultimoDisparador = disparador.current;
                cerrar(false);
              },
            } as const;
            return (
              <li key={o.href} role="none">
                {o.externo ? (
                  <a href={o.href} {...comunes}>
                    {contenido}
                  </a>
                ) : (
                  <Link href={o.href} {...comunes}>
                    {contenido}
                  </Link>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </details>
  );
}
