// [003] R-04: las clases de cva son las mismas que arma {% clases %} en Django.
import { describe, expect, it } from "vitest";

import definiciones from "../../../../ui/variantes.json";

import { aviso, boton, insignia } from "./variantes";

describe("variantes compartidas", () => {
  it("botón: base + variante + tamaño md por omisión, como {% clases 'boton' %}", () => {
    const esperado = [
      definiciones.boton.base,
      definiciones.boton.variantes.destructivo,
      definiciones.boton.tamanos.md,
    ].join(" ");
    expect(boton({ variante: "destructivo" })).toBe(esperado);
  });

  it("aviso e insignia usan sus variantes del JSON", () => {
    expect(aviso({ variante: "danger" })).toContain(definiciones.aviso.variantes.danger);
    expect(insignia({ variante: "warning" })).toContain(definiciones.insignia.variantes.warning);
  });
});
