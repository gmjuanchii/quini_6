// [003] R-23: ingreso por perfil con las credenciales que escribe preparar_e2e.
import { readFileSync } from "node:fs";
import type { Page } from "@playwright/test";

export type Perfil = "admin" | "admin2" | "usuaria" | "sinjugadas";

function credenciales(): Record<Perfil, { correo: string; contrasena: string }> {
  return JSON.parse(readFileSync(new URL("../.credenciales.json", import.meta.url), "utf8"));
}

export async function ingresarComo(page: Page, perfil: Perfil, destino = "/resultados/") {
  const { correo, contrasena } = credenciales()[perfil];
  await page.goto(`/ingresar/?next=${encodeURIComponent(destino)}`);
  await page.getByLabel("Correo electrónico").fill(correo);
  await page.getByLabel("Contraseña", { exact: true }).fill(contrasena);
  await page.getByRole("button", { name: "Ingresar" }).click();
  await page.waitForURL((url) => !url.pathname.startsWith("/ingresar/"));
  await sinTransicionEntreDocumentos(page);
}

/**
 * Espera a que termine la transición entre documentos (`@view-transition` de `ui/base.css`):
 * mientras dura, la página no recibe clics y un clic forzado (las casillas de números son de 1 px)
 * cae en la capa de la transición. Sin scripts, toda navegación es entre documentos.
 */
export async function sinTransicionEntreDocumentos(page: Page) {
  // Sondeo con evaluate: con los scripts desactivados, page.waitForFunction no avanza.
  for (let intento = 0; intento < 40; intento++) {
    const activa = await page.evaluate(() => {
      try {
        return document.documentElement.matches(":active-view-transition");
      } catch {
        return false; // navegador sin la seudoclase: no hay nada que esperar
      }
    });
    if (!activa) return;
    await page.waitForTimeout(50);
  }
}
