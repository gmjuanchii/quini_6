// [003] T190: mismo comportamiento que static/js/selector-numeros.js ([001] AC-4.2 a AC-4.6).
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { msg } from "@/lib/mensajes";

import { agregarEscrito, SelectorNumeros } from "./selector-numeros";

afterEach(cleanup);

describe("agregarEscrito", () => {
  it("valida rango, repetidos y el máximo", () => {
    expect(agregarEscrito("7", [])).toEqual({ numero: "07" });
    expect(agregarEscrito("46", [])).toEqual({ mensaje: msg("jugada.fuera_de_rango") });
    expect(agregarEscrito("x", [])).toEqual({ mensaje: msg("jugada.fuera_de_rango") });
    expect(agregarEscrito("07", ["07"])).toEqual({ mensaje: msg("jugada.repetido", { nn: "07" }) });
    expect(agregarEscrito("08", ["01", "02", "03", "04", "05", "06"])).toEqual({
      mensaje: msg("jugada.exactamente_seis"),
    });
  });
});

describe("SelectorNumeros", () => {
  it("contador, no más de seis y Agregar", () => {
    render(<SelectorNumeros iniciales={["01", "02", "03", "04", "05"]} />);
    expect(screen.getByText(msg("jugada.faltan", { n: 1 }))).toBeTruthy();
    fireEvent.click(screen.getByLabelText("06"));
    expect(screen.getByText(msg("rot.seis_elegidos"))).toBeTruthy();
    fireEvent.click(screen.getByLabelText("07"));
    expect((screen.getByLabelText("07") as HTMLInputElement).checked).toBe(false);
    expect(document.getElementById("mensaje-selector")!.textContent).toBe(
      msg("jugada.exactamente_seis"),
    );
    fireEvent.click(screen.getByLabelText("06"));
    fireEvent.change(screen.getByLabelText(msg("jugada.escribir_numero")), {
      target: { value: "45" },
    });
    fireEvent.click(screen.getByRole("button", { name: msg("rot.agregar") }));
    expect((screen.getByLabelText("45") as HTMLInputElement).checked).toBe(true);
  });

  it("errores del servidor junto al grupo", () => {
    render(<SelectorNumeros errores={[msg("jugada.faltan", { n: 6 })]} />);
    expect(document.getElementById("selector-numeros")!.getAttribute("aria-describedby")).toBe(
      "numeros_error",
    );
  });
});
