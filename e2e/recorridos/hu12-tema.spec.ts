// [003] HU-12 (quickstart #15): tema según el dispositivo, elección al instante sin perder lo escrito,
// la preferencia se conserva al navegar, funciona sin scripts y no hay incidencias en ningún tema.
import { expect, type Page, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const fondo = (page: Page) =>
  page.evaluate(() => getComputedStyle(document.body).backgroundColor);
const tema = (page: Page) => page.locator("html").getAttribute("data-theme");

test("sin cookie, el tema sigue al dispositivo (AC-12.1)", async ({ page }, info) => {
  await page.goto("/resultados/");
  expect(await tema(page)).toBeNull();
  const oscuro = info.project.name === "oscuro";
  // Fondo oscuro (#0f172a) o claro (#f3f4f6) según prefers-color-scheme.
  expect(await fondo(page)).toBe(oscuro ? "rgb(15, 23, 42)" : "rgb(243, 244, 246)");
  await expect(page.getByRole("radio", { name: msg("tema.dispositivo") })).toBeChecked();
});

test("elegir 'Claro' cambia al instante sin perder lo escrito y se conserva (AC-12.2, AC-12.3)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Con scripts");
  await page.goto("/estadisticas/");
  await page.getByLabel("Número", { exact: true }).fill("14");
  await page.getByRole("radio", { name: msg("tema.oscuro") }).check();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "oscuro");
  expect(await fondo(page)).toBe("rgb(15, 23, 42)");
  await page.getByRole("radio", { name: msg("tema.claro") }).check();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "claro");
  await expect(page.getByLabel("Número", { exact: true })).toHaveValue("14"); // no recargó
  await expect(page.getByRole("button", { name: msg("tema.guardar") })).toBeHidden();
  await page.goto("/resultados/");
  await expect(page.locator("html")).toHaveAttribute("data-theme", "claro");
  await page.getByRole("radio", { name: msg("tema.dispositivo") }).check();
  expect(await tema(page)).toBeNull();
  await page.reload();
  expect(await tema(page)).toBeNull();
});

test("sin scripts, el formulario cambia el tema (componentes.md § 4)", async ({ page }, info) => {
  test.skip(info.project.name !== "sin-scripts", "Versión básica");
  await page.goto("/estadisticas/");
  await page.getByRole("radio", { name: msg("tema.oscuro") }).check();
  await page.getByRole("button", { name: msg("tema.guardar") }).click();
  await expect(page).toHaveURL(/\/estadisticas\/$/);
  await expect(page.locator("html")).toHaveAttribute("data-theme", "oscuro");
  await page.getByRole("radio", { name: msg("tema.dispositivo") }).check();
  await page.getByRole("button", { name: msg("tema.guardar") }).click();
  expect(await tema(page)).toBeNull();
});

const PANTALLAS: Array<[("admin" | "usuaria" | null), string]> = [
  [null, "/resultados/"],
  [null, "/estadisticas/"],
  [null, "/ingresar/"],
  ["usuaria", "/mis-jugadas/"],
  ["usuaria", "/mis-jugadas/nueva/"],
  ["admin", "/administracion/extracciones/"],
  ["admin", "/administracion/concursos/"],
];

for (const elegido of ["claro", "oscuro"] as const) {
  test(`sin incidencias de accesibilidad en tema ${elegido} (AC-12.4)`, async ({ page, context }, info) => {
    test.skip(info.project.name !== "escritorio", "Una pasada por tema alcanza");
    let actual: string | null = null;
    for (const [perfil, ruta] of PANTALLAS) {
      if (perfil !== actual && perfil) {
        await context.clearCookies();
        await ingresarComo(page, perfil, ruta);
        actual = perfil;
      }
      await context.addCookies([{ name: "quini6_tema", value: elegido, url: info.project.use.baseURL! }]);
      await page.goto(ruta);
      await expect(page.locator("html")).toHaveAttribute("data-theme", elegido);
      await sinIncidenciasGraves(page);
    }
  });
}
