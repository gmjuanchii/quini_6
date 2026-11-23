// [003] HU-05 (quickstart #8): sección activa, saltar al contenido, menú de cuenta, menú móvil y
// caminos de regreso.
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const nav = (page) => page.getByRole("navigation", { name: "Navegación principal" });

test("Tab muestra 'Saltar al contenido' y lleva el foco al contenido (AC-5.5)", async ({ page }) => {
  await page.goto("/estadisticas/");
  await page.keyboard.press("Tab");
  const saltar = page.getByRole("link", { name: msg("nav.saltar") });
  await expect(saltar).toBeFocused();
  await expect(saltar).toBeInViewport();
  await page.keyboard.press("Enter");
  await expect(page.locator("main#contenido")).toBeFocused();
});

test("la sección actual se anuncia y el logotipo lleva al inicio (AC-5.1, AC-5.7)", async ({ page }, info) => {
  await page.goto("/estadisticas/");
  if (info.project.name !== "movil" || (await page.locator("[data-boton-menu]").isHidden())) {
    await expect(nav(page).getByRole("link", { name: "Estadísticas" })).toHaveAttribute("aria-current", "page");
    await expect(nav(page).getByRole("link", { name: "Resultados" })).not.toHaveAttribute("aria-current", "page");
  }
  await expect(page.locator('link[rel="icon"]')).toHaveAttribute("href", /marca\/favicon\.svg$/);
  await page.getByRole("link", { name: msg("nav.logotipo") }).click();
  await expect(page).toHaveURL(/\/resultados\/$/);
  if (info.project.name !== "sin-scripts") await sinIncidenciasGraves(page); // axe necesita scripts
  await sinDesplazamientoHorizontal(page);
});

test("menú de cuenta con el teclado: Salir adentro, Escape devuelve el foco (AC-5.3)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts" || info.project.name === "movil", "Escritorio con scripts");
  await ingresarComo(page, "usuaria", "/resultados/");
  const boton = page.getByRole("button", { name: /^Cuenta de / });
  await expect(boton).toHaveAttribute("aria-expanded", "false");
  await expect(page.getByRole("button", { name: msg("nav.salir") })).toBeHidden();
  await boton.focus();
  await page.keyboard.press("Enter");
  await expect(boton).toHaveAttribute("aria-expanded", "true");
  await expect(page.getByRole("button", { name: msg("nav.salir") })).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("button", { name: msg("nav.salir") })).toBeHidden();
  await expect(boton).toBeFocused();
  await sinIncidenciasGraves(page);
});

test("en el teléfono, 'Menú' se abre con Intro y se cierra con Escape (AC-5.4)", async ({ page }, info) => {
  test.skip(info.project.name !== "movil", "Solo a 360 px");
  await ingresarComo(page, "usuaria", "/resultados/");
  const menu = page.getByRole("button", { name: msg("nav.menu") });
  await expect(menu).toHaveAttribute("aria-expanded", "false");
  await expect(nav(page)).toBeHidden();
  await menu.focus();
  await page.keyboard.press("Enter");
  await expect(menu).toHaveAttribute("aria-expanded", "true");
  await expect(nav(page).getByRole("link", { name: "Mis jugadas" })).toBeVisible();
  // Los enlaces tienen al menos 44 × 44 px (AC-5.2).
  const caja = (await nav(page).getByRole("link", { name: "Mis jugadas" }).boundingBox())!;
  expect(caja.height).toBeGreaterThanOrEqual(44);
  await page.keyboard.press("Escape");
  await expect(nav(page)).toBeHidden();
  await expect(menu).toBeFocused();
  await sinDesplazamientoHorizontal(page);
});

test("sin scripts, las secciones y 'Salir' quedan visibles (componentes.md § 4)", async ({ page }, info) => {
  test.skip(info.project.name !== "sin-scripts", "Versión básica");
  await ingresarComo(page, "usuaria", "/resultados/");
  await expect(nav(page).getByRole("link", { name: "Mis jugadas" })).toBeVisible();
  await expect(page.getByRole("button", { name: msg("nav.salir") })).toBeVisible();
  await expect(page.getByRole("button", { name: msg("nav.menu") })).toBeHidden();
});

test("caminos de regreso en las páginas internas (AC-5.6)", async ({ page }) => {
  await ingresarComo(page, "admin", "/administracion/extracciones/");
  const volver = page.locator("a[data-volver]");
  await expect(volver).toHaveText(msg("nav.volver_sorteos").replace("← ", ""));
  await page.locator("tbody tr[id^=fila-]").first().getByRole("link").first().click();
  await expect(volver).toHaveText(msg("nav.volver_extracciones").replace("← ", ""));
  await volver.click();
  await expect(page).toHaveURL(/\/administracion\/extracciones\/$/);
});
