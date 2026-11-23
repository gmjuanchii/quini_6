// [003] AC-9.1, AC-9.2: mismas reglas que quini6/tablas.py (tests/unit/test_templatetags_ui.py).
import { describe, expect, it } from "vitest";

import { conParametros, encabezados } from "./tablas";

describe("conParametros", () => {
  it("aplica cambios, quita vacíos y nunca conserva _interfaz", () => {
    expect(
      conParametros({ estado: "con-error", orden: "", _interfaz: "django" }, { pagina: 2 }),
    ).toBe("?estado=con-error&pagina=2");
    expect(conParametros({ pagina: "3" }, { pagina: null })).toBe("?");
  });
});

describe("encabezados", () => {
  const columnas = [
    { id: "fecha", texto: "Fecha", ordenable: true },
    { id: "ejecutada_por", texto: "Ejecutada por" },
    { id: "estado", texto: "Estado", ordenable: true },
  ];

  it("la columna ordenada ofrece el sentido contrario y vuelve a la página 1", () => {
    const [fecha, ejecutada, estado] = encabezados(
      { pagina: "2", estado: "en-curso" },
      columnas,
      "-fecha",
    );
    expect(fecha).toMatchObject({ sentido: "descending", href: "?estado=en-curso&orden=fecha" });
    expect(ejecutada?.href).toBeUndefined();
    expect(estado).toMatchObject({ sentido: undefined, href: "?estado=en-curso&orden=estado" });
  });

  it("ascendente pasa a descendente", () => {
    expect(encabezados({}, columnas, "estado")[2]).toMatchObject({
      sentido: "ascending",
      href: "?orden=-estado",
    });
  });
});
