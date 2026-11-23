// [003] R-25: el mismo filtro que Django (tests/unit/test_observabilidad.py).
import { expect, it } from "vitest";

import { filtrarEvento } from "./observabilidad";

it("quita correos, cookies, autenticación y formularios", () => {
  const evento = filtrarEvento({
    request: {
      cookies: { sessionid: "x" },
      data: { costo: "100" },
      query_string: "next=/x",
      headers: { Cookie: "a", Authorization: "b", "X-CSRFToken": "c", "User-Agent": "d" },
    },
    user: { email: "ana@correo.com" },
    message: "Falló para ana@correo.com",
  });
  expect(evento.request).toEqual({ headers: { "User-Agent": "d" } });
  expect(evento.user).toBeUndefined();
  expect(evento.message).toBe("Falló para [filtrado]");
});
