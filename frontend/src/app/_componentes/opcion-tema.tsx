"use client";

/** Opción del ThemeSelect: con scripts aplica el tema al instante (igual que `selectorTema` de
 * static/js/ui.js en Django). */
import { aplicarTema, type Tema } from "@/lib/tema";

export function OpcionTema({ valor, marcada }: { valor: Tema; marcada: boolean }) {
  return (
    <input
      type="radio"
      name="tema"
      value={valor}
      defaultChecked={marcada}
      className="size-4 accent-[var(--q-primary)]"
      onChange={(e) => aplicarTema(e.target.value as Tema)}
    />
  );
}
