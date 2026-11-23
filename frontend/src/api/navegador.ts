/**
 * Cliente tipado de la API v1 para el navegador ([003] R-17): mismo origen (`/api/v1/`), cookie de
 * sesión de Django y `X-CSRFToken` en las mutaciones. Sin tokens en el navegador (R-19).
 */
import createClient from "openapi-fetch";

import type { paths } from "./esquema";

function tokenCsrf(): string | undefined {
  if (typeof document === "undefined") return undefined;
  return document.cookie
    .split("; ")
    .find((par) => par.startsWith("csrftoken="))
    ?.slice("csrftoken=".length);
}

export const apiNavegador = createClient<paths>({
  baseUrl: "",
  credentials: "same-origin",
});

apiNavegador.use({
  onRequest({ request }) {
    const token = tokenCsrf();
    if (token && !["GET", "HEAD", "OPTIONS"].includes(request.method)) {
      request.headers.set("X-CSRFToken", token);
    }
    return request;
  },
});
