// [003] T184, CHK022: el mismo cálculo que estadisticas/views.py :: _grafico (valores obtenidos de
// Django con los mismos datos) y el mismo marcado accesible.
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { calcularGrafico, FrequencyChart } from "./frequency-chart";

afterEach(cleanup);

const porTres = Array.from({ length: 46 }, (_, n) => ({ numero: n, frecuencia: (n * 7) % 3 }));

describe("calcularGrafico", () => {
  it("dimensiones y barras como Django", () => {
    const g = calcularGrafico(porTres, 7);
    expect([g.ancho, g.alto, g.base, g.yTexto]).toEqual([460, 142, 120, 134]);
    expect(g.barras[0]).toEqual({
      numero: 0,
      frecuencia: 0,
      x: 1,
      xTexto: 5,
      y: 120,
      alto: 0,
      ancho: 8,
      consultado: false,
      rotulo: true,
    });
    expect(g.barras[1]).toMatchObject({ x: 11, y: 60, alto: 60, rotulo: false });
    expect(g.barras[2]).toMatchObject({ y: 0, alto: 120 });
    expect(g.barras[7]).toMatchObject({ consultado: true, rotulo: true, y: 60 });
  });

  it("alto proporcional al máximo", () => {
    const numeros = Array.from({ length: 46 }, (_, n) => ({
      numero: n,
      frecuencia: [1, 2, 3][n % 3]!,
    }));
    expect(
      calcularGrafico(numeros, null)
        .barras.slice(0, 3)
        .map((b) => [b.alto, b.y]),
    ).toEqual([
      [40, 80],
      [80, 40],
      [120, 0],
    ]);
  });

  it("sin apariciones no divide por cero", () => {
    const ceros = Array.from({ length: 46 }, (_, n) => ({ numero: n, frecuencia: 0 }));
    expect(calcularGrafico(ceros, null).barras.every((b) => b.alto === 0)).toBe(true);
  });
});

describe("FrequencyChart", () => {
  it("role=img con título, descripción y el consultado resaltado", () => {
    render(
      <FrequencyChart
        numeros={porTres}
        consultado={7}
        modalidad="Tradicional – Primer Sorteo"
        cantidadSorteos={3}
      />,
    );
    const grafico = screen.getByRole("img");
    expect(grafico.getAttribute("aria-labelledby")).toBe("grafico-titulo grafico-descripcion");
    expect(document.getElementById("grafico-titulo")!.textContent).toBe(
      "Frecuencia de cada número en Tradicional – Primer Sorteo",
    );
    expect(document.getElementById("grafico-descripcion")!.textContent).toBe(
      "Gráfico de barras con las apariciones de cada número de 00 a 45 en 3 sorteos considerados; el 07 aparece resaltado.",
    );
    expect(document.querySelectorAll("rect.barra")).toHaveLength(46);
    expect(document.querySelector("rect.barra--consultada")!.getAttribute("x")).toBe("71");
  });
});
