// [003] contracts/formatos.md: los mismos casos que tests/unit/test_formatos_contrato.py.
import { describe, expect, it } from "vitest";

import casos from "@contratos/formatos-casos.json";

import { cantidad, dosDigitos, fecha, fechaHora, pesos, porcentaje } from "./formato";

const funciones: Record<string, (entrada: string) => string> = {
  fecha,
  fecha_hora: fechaHora,
  importe: pesos,
  porcentaje,
  bolilla: dosDigitos,
  cantidad,
};

describe("contratos/formatos-casos.json", () => {
  it.each(casos)("$tipo: $entrada → $salida", ({ tipo, entrada, salida }) => {
    const funcion = funciones[tipo];
    expect(funcion, `tipo sin función: ${tipo}`).toBeDefined();
    expect(funcion!(entrada)).toBe(salida);
  });
});

describe("reglas de formatos.md", () => {
  it("importes desde la cadena, sin punto flotante", () => {
    expect(pesos("1234567.5")).toBe("$ 1.234.567,50");
    expect(pesos("0.1")).toBe("$ 0,10");
    expect(pesos("9007199254740993.01")).toBe("$ 9.007.199.254.740.993,01");
    expect(pesos("1.005")).toBe("$ 1,01");
    expect(pesos("-1.005")).toBe("$ -1,01");
    expect(pesos("-0.001")).toBe("$ 0,00");
  });

  it("fecha y hora en Buenos Aires sin importar la zona del proceso", () => {
    expect(fechaHora("2026-11-21T12:15:00-03:00")).toBe("21/11/2026 12:15");
    expect(fecha("2026-01-01T02:30:00Z")).toBe("31/12/2025");
  });

  it("vacíos", () => {
    for (const f of [fecha, fechaHora, pesos, porcentaje, dosDigitos, cantidad]) {
      expect(f(null)).toBe("");
      expect(f(undefined)).toBe("");
    }
  });

  it("número de bolilla y cantidades", () => {
    expect(dosDigitos(45)).toBe("45");
    expect(cantidad(1500)).toBe("1.500");
  });
});
