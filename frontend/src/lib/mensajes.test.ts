// [003] R-13: el catálogo de Next.js es el mismo de Django (contratos/mensajes.json).
import { describe, expect, it } from "vitest";

import { esClaveMensaje, msg } from "./mensajes";

describe("msg", () => {
  it("completa variables como mensaje() de Django", () => {
    expect(msg("jugada.faltan", { n: 2 })).toBe("Faltan 2 números");
    expect(msg("pag.pagina", { n: 1, m: 15 })).toBe("Página 1 de 15");
    expect(msg("nav.menu")).toBe("Menú");
  });

  it("una variable faltante es un error de programación", () => {
    expect(() => msg("jugada.faltan", {})).toThrow();
  });

  it("reconoce las claves del catálogo", () => {
    expect(esClaveMensaje("nav.salir")).toBe(true);
    expect(esClaveMensaje("no.existe")).toBe(false);
  });
});
