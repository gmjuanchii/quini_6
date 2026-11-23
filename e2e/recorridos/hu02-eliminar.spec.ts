// [003] HU-02 (quickstart #3): menú ⋮ anclado y confirmación de eliminación.
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const LISTADO = "/administracion/extracciones/";

test.beforeEach(async ({ page }) => {
  await ingresarComo(page, "admin", `${LISTADO}?estado=finalizada`);
});

function primerMenu(page) {
  return page.locator("details.menu-acciones").first();
}

test("el menú se abre pegado a su botón y se recorre con el teclado (AC-2.1, AC-2.2)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Con scripts: anclaje y teclado");
  const menu = primerMenu(page);
  const boton = menu.locator("summary");
  await boton.focus();
  await page.keyboard.press("Enter");
  const opciones = menu.getByRole("menuitem");
  await expect(opciones.first()).toBeFocused();
  // Anclado: pegado al botón (debajo, o encima si no hay lugar) y dentro de la pantalla.
  const b = (await boton.boundingBox())!;
  const m = (await menu.getByRole("menu").boundingBox())!;
  const vista = page.viewportSize()!;
  const debajo = Math.abs(m.y - (b.y + b.height)) <= 8;
  const encima = Math.abs(m.y + m.height - b.y) <= 8;
  expect(debajo || encima, "el menú queda pegado a su botón").toBe(true);
  expect(m.x).toBeGreaterThanOrEqual(0);
  expect(m.y).toBeGreaterThanOrEqual(0);
  expect(m.x + m.width).toBeLessThanOrEqual(vista.width);
  expect(m.y + m.height).toBeLessThanOrEqual(vista.height);
  await page.keyboard.press("ArrowDown");
  await expect(opciones.nth(1)).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(menu.getByRole("menu")).toBeHidden();
  await expect(boton).toBeFocused();
});

test("abrir otro menú cierra el anterior y un clic afuera lo cierra (AC-2.1, AC-2.2)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Con scripts");
  const menus = page.locator("details.menu-acciones");
  await menus.nth(0).locator("summary").click();
  await expect(menus.nth(0)).toHaveAttribute("open", "");
  // El menú abierto tapa los botones de las filas de abajo: el otro se abre con el teclado.
  await menus.nth(3).locator("summary").focus();
  await page.keyboard.press("Enter");
  await expect(menus.nth(3)).toHaveAttribute("open", "");
  await expect(menus.nth(0)).not.toHaveAttribute("open", "");
  await page.locator("h1").click();
  await expect(menus.nth(3)).not.toHaveAttribute("open", "");
});

test("confirmar con Cancelar predeterminado, cancelar y eliminar (AC-2.3 a AC-2.5)", async ({ page }, info) => {
  const menu = primerMenu(page);
  await menu.locator("summary").click();
  await menu.getByRole("menuitem", { name: msg("ext.eliminar") }).click();
  if (info.project.name !== "sin-scripts") {
    const dialogo = page.getByRole("alertdialog");
    await expect(dialogo).toBeVisible();
    await expect(dialogo.getByRole("link", { name: msg("ext.cancelar") })).toBeFocused();
    await expect(dialogo.getByText(msg("ext.eliminar_consecuencias"))).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(dialogo).toBeHidden();
    await expect(menu.locator("summary")).toBeFocused();
    await menu.locator("summary").click();
    await menu.getByRole("menuitem", { name: msg("ext.eliminar") }).click();
    await expect(dialogo).toBeVisible();
  } else {
    await expect(page.getByRole("alertdialog")).toBeVisible();
  }
  const filasAntes = await page.locator("tbody tr[id^=fila-]").count();
  await page.getByRole("button", { name: msg("ext.eliminar") }).click();
  await expect(page.getByText(/^Se eliminó la extracción del /).first()).toBeVisible();
  await expect(page.getByText("Deshacer")).toHaveCount(0);
  if (info.project.name === "sin-scripts") return;
  await page.goto(`${LISTADO}?estado=finalizada`);
  await expect(page.locator("tbody tr[id^=fila-]")).toHaveCount(filasAntes - 1);
});

test("una extracción en curso no ofrece Eliminar (AC-2.6)", async ({ page }) => {
  await page.goto(`${LISTADO}?estado=en-curso`);
  const menu = page.locator("details.menu-acciones").first();
  await menu.locator("summary").click();
  await expect(menu.getByRole("menuitem", { name: msg("ext.eliminar") })).toHaveCount(0);
});

test("sin incidencias graves de accesibilidad con la confirmación abierta", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Con scripts");
  const menu = primerMenu(page);
  await menu.locator("summary").click();
  await menu.getByRole("menuitem", { name: msg("ext.eliminar") }).click();
  await expect(page.getByRole("alertdialog")).toBeVisible();
  await sinIncidenciasGraves(page);
});
