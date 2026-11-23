// [003] AC-6.2, T200: mostrar/ocultar con aria-pressed y anuncio del cambio.
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";

import { msg } from "@/lib/mensajes";

import { PasswordField } from "./password-field";

afterEach(cleanup);

it("alterna la visibilidad y lo anuncia", () => {
  render(
    <PasswordField
      id="id_password"
      nombre="password"
      etiqueta="Contraseña"
      autocompletar="current-password"
    />,
  );
  const campo = screen.getByLabelText("Contraseña") as HTMLInputElement;
  const boton = screen.getByRole("button", { name: msg("cuenta.mostrar") });
  expect(campo.type).toBe("password");
  expect(boton.getAttribute("aria-pressed")).toBe("false");
  fireEvent.click(boton);
  expect(campo.type).toBe("text");
  expect(
    screen.getByRole("button", { name: msg("cuenta.ocultar") }).getAttribute("aria-pressed"),
  ).toBe("true");
  expect(screen.getByText(msg("cuenta.contrasena_visible"))).toBeTruthy();
  expect(campo.getAttribute("autocomplete")).toBe("current-password");
});
