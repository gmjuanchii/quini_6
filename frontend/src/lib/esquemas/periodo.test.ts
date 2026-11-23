// [003] FR-012, AC-4.5: mismos mensajes que la validación de Django (tests/unit/test_periodos.py).
import { describe, expect, it } from "vitest";

import { aDma, aIso, analizarFecha, enmascarar } from "@/lib/fechas";
import { msg } from "@/lib/mensajes";

import { validarPeriodo } from "./periodo";

function errores(inicio: string, fin: string, max = "2026-11-22") {
  return validarPeriodo({ inicio, fin }, { max });
}

describe("fechas", () => {
  it("analiza dd/mm/aaaa y AAAA-MM-DD", () => {
    expect(analizarFecha("1/2/2026")).toEqual({
      estado: "valida",
      iso: "2026-02-01",
      texto: "01/02/2026",
    });
    expect(analizarFecha("2026-02-29")).toEqual({ estado: "inexistente", texto: "29/02/2026" });
    expect(analizarFecha("ayer").estado).toBe("formato");
    expect(aIso("31/12/2025")).toBe("2025-12-31");
    expect(aDma("2025-12-31")).toBe("31/12/2025");
  });

  it("AC-4.2: agrega las barras al escribir", () => {
    expect(enmascarar("01012025")).toBe("01/01/2025");
    expect(enmascarar("0101")).toBe("01/01");
    expect(enmascarar("2025-01-31")).toBe("31/01/2025");
  });
});

describe("validarPeriodo", () => {
  it("faltan las dos fechas", () => {
    expect(errores("", "")).toEqual({
      inicio: msg("fecha.falta_inicio"),
      fin: msg("fecha.falta_fin"),
    });
  });

  it("fecha inexistente y formato inválido", () => {
    expect(errores("31/02/2026", "x")).toEqual({
      inicio: msg("fecha.inexistente", { fecha: "31/02/2026" }),
      fin: msg("gral.fecha_invalida"),
    });
  });

  it("fin anterior al inicio y fin futura", () => {
    expect(errores("10/03/2026", "01/03/2026")).toEqual({
      fin: msg("fecha.fin_anterior", { fecha: "10/03/2026" }),
    });
    expect(errores("01/11/2026", "2026-12-01")).toEqual({ fin: msg("ext.fin_futura") });
  });

  it("período válido", () => {
    expect(errores("01/11/2026", "2026-11-15")).toEqual({});
  });
});
