// [003] HU-14, R-20: apoyo para los guiones de convivencia (Django y Next.js detrás del enrutador).
//
// Se ejecutan solo con E2E_CONVIVENCIA=1 y E2E_BASE_URL apuntando al enrutador (Caddy) con la
// pantalla en prueba en QUINI6_RUTAS_NEXT (quickstart § 2). Variables:
//   E2E_DJANGO_DIRECTO  Django sin pasar por el enrutador (por omisión http://127.0.0.1:8001)
//   E2E_URL_SIN_NEXT    un segundo enrutador con las mismas rutas conmutadas pero cuyo destino de
//                       Next.js no responde (simula "Next.js detenido", AC-14.6)
import { expect, test, type Page, type Response } from "@playwright/test";

export const CONVIVENCIA = Boolean(process.env.E2E_CONVIVENCIA);
export const DJANGO_DIRECTO = process.env.E2E_DJANGO_DIRECTO ?? "http://127.0.0.1:8001";
export const URL_SIN_NEXT = process.env.E2E_URL_SIN_NEXT ?? "";

export function soloEnConvivencia() {
  test.skip(!CONVIVENCIA, "Requiere el enrutador con Next.js (E2E_CONVIVENCIA=1, quickstart § 2)");
}

/** Quién respondió: la cabecera X-Interfaz que agrega el enrutador (diagnóstico, R-20). */
export function interfaz(respuesta: Response | null): string | null {
  return respuesta?.headers()["x-interfaz"] ?? null;
}

/** Rutas conmutadas del enrutador en prueba (las mismas de QUINI6_RUTAS_NEXT, contracts/rutas.md
 * § 3); vacía = solo la pantalla 1, como en la Fase 18. */
export const RUTAS_NEXT = (process.env.E2E_RUTAS_NEXT ?? "").split(/\s+/).filter(Boolean);

/** Quién debe atender una ruta según las reglas 1, 4 y 5 de contracts/rutas.md § 3. */
export function atiende(ruta: string): "django" | "next" | null {
  if (RUTAS_NEXT.length === 0) return null;
  const camino = new URL(ruta, "http://x").pathname;
  if (/^\/(api|static)\//.test(camino) || /^\/administracion\/extracciones\/[^/]+\/csv\/$/.test(camino)) {
    return "django";
  }
  const conmutada = RUTAS_NEXT.some((patron) =>
    patron.endsWith("*") ? camino.startsWith(patron.slice(0, -1)) : camino === patron,
  );
  return conmutada ? "next" : "django";
}

export async function irA(page: Page, ruta: string, esperadaSinRutas: "django" | "next") {
  // Con E2E_RUTAS_NEXT, la expectativa sale de las rutas conmutadas (el mismo guion sirve en cada
  // etapa de la conmutación, R-27); sin ella, la de la Fase 18 (solo la pantalla 1).
  const esperada = atiende(ruta) ?? esperadaSinRutas;
  const respuesta = await page.goto(ruta);
  expect(interfaz(respuesta), `${ruta} debía atenderla ${esperada}`).toBe(esperada);
  return respuesta;
}

/** Textos de las secciones del encabezado, para comparar las dos interfaces (AC-14.1). */
export async function seccionesDelEncabezado(page: Page): Promise<string[]> {
  return page
    .getByRole("navigation", { name: "Navegación principal" })
    .getByRole("listitem")
    .allInnerTexts();
}
