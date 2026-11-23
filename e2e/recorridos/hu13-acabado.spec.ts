// [003] HU-13 (quickstart #16): transiciones breves que respetan "reducir movimiento" y respuesta
// visible en menos de 100 ms (AC-13.1, AC-13.2, NFR-005).
import { expect, type Locator, type Page, test } from "@playwright/test";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const LISTADO = "/administracion/extracciones/";

/** Duración más larga de las transiciones de un elemento, en milisegundos. */
async function duracion(elemento: Locator): Promise<number> {
  return elemento.evaluate((el) => {
    const valores = getComputedStyle(el).transitionDuration.split(",");
    return Math.max(...valores.map((v) => parseFloat(v) * (v.trim().endsWith("ms") ? 1 : 1000)));
  });
}

async function abrirMenu(page: Page) {
  // Una extracción terminada: la que está en curso no ofrece "Eliminar" (AC-2.6).
  const fila = page.locator("tbody tr[id^=fila-]").filter({ has: page.locator("a[data-confirmar]") }).first();
  await fila.locator("summary").click();
  return fila.getByRole("menu");
}

test.beforeEach(async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Las transiciones y los tiempos necesitan scripts");
  await ingresarComo(page, "admin", LISTADO);
});

test("con 'reducir movimiento', menú, diálogo y aviso sin transición (AC-13.2)", async ({ page }, info) => {
  test.skip(info.project.name !== "movimiento-reducido", "Solo con prefers-reduced-motion");
  const menu = await abrirMenu(page);
  expect(await duracion(menu)).toBe(0);
  await page.getByRole("menuitem", { name: msg("ext.eliminar") }).first().click();
  const dialogo = page.getByRole("alertdialog");
  await expect(dialogo).toBeVisible();
  expect(await duracion(dialogo)).toBe(0);
  await page.keyboard.press("Escape");
  await page.goto("/administracion/extracciones/999999/eliminar/");
  const aviso = page.locator("[data-aviso-toast]").first();
  await expect(aviso).toBeVisible();
  expect(await duracion(aviso)).toBe(0);
  const animacion = await page.evaluate(() => {
    const prueba = document.createElement("div");
    prueba.className = "motion-safe:animate-spin";
    document.body.append(prueba);
    return getComputedStyle(prueba).animationName;
  });
  expect(animacion).toBe("none"); // la barra y el indicador informan sin movimiento
});

test("con movimiento normal, ninguna transición supera 250 ms (AC-13.1)", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Movimiento normal");
  const menu = await abrirMenu(page);
  const tiempoMenu = await duracion(menu);
  expect(tiempoMenu).toBeGreaterThan(0);
  expect(tiempoMenu).toBeLessThanOrEqual(250);
  await page.getByRole("menuitem", { name: msg("ext.eliminar") }).first().click();
  const dialogo = page.getByRole("alertdialog");
  await expect(dialogo).toBeVisible();
  expect(await duracion(dialogo)).toBeLessThanOrEqual(250);
});

test("respuesta visible en menos de 100 ms (NFR-005)", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Una medición alcanza");
  // Del clic en el ⋮ a la apertura del menú.
  const tiempoMenu = await page.evaluate(async () => {
    const resumen = document.querySelector<HTMLElement>("tbody tr[id^=fila-] summary")!;
    const inicio = performance.now();
    resumen.click();
    await new Promise(requestAnimationFrame);
    const abierto = (resumen.parentElement as HTMLDetailsElement).open;
    return abierto ? performance.now() - inicio : Infinity;
  });
  expect(tiempoMenu).toBeLessThan(100);
  await page.keyboard.press("Escape");

  // Del clic en "Iniciar extracción" al estado de trabajo del botón (sin esperar la respuesta).
  const formulario = page.locator("form[data-trabajando][hx-post]");
  test.skip((await formulario.count()) === 0, "Hay una extracción en curso de esta cuenta");
  await page.getByRole("link", { name: msg("ext.atajo_anio_anterior") }).click();
  const tiempoBoton = await page.evaluate(async () => {
    const boton = document.querySelector<HTMLButtonElement>("form[data-trabajando][hx-post] button[data-texto-trabajando]")!;
    const formulario = boton.form!;
    formulario.addEventListener("submit", (e) => e.preventDefault(), { once: true });
    window.addEventListener("htmx:beforeRequest", (e) => e.preventDefault(), { once: true });
    const inicio = performance.now();
    boton.click();
    await new Promise(requestAnimationFrame);
    return boton.getAttribute("aria-busy") === "true" ? performance.now() - inicio : Infinity;
  });
  expect(tiempoBoton).toBeLessThan(100);
});
