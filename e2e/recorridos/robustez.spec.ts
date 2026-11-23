// [003] Fase 16 (quickstart #17 y #18): sin conexión no se pierde ni se duplica nada, la sesión
// vencida conserva lo escrito y los textos largos no desbordan a 360 px (FR-030 a FR-032).
import { expect, type Page, test } from "@playwright/test";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const NUEVA = "/mis-jugadas/nueva/";

function numerosAlAzar(): string[] {
  const elegidos = new Set<string>();
  while (elegidos.size < 6) elegidos.add(String(Math.floor(Math.random() * 46)).padStart(2, "0"));
  return [...elegidos];
}

async function completarJugada(page: Page, numeros: string[], costo: string) {
  await page.getByLabel(/^(Concurso|Sorteo)$/).selectOption({ index: 1 });
  for (const n of numeros) await page.getByLabel(n, { exact: true }).check({ force: true });
  await page.getByLabel(/^Costo/).fill(costo);
}

async function cantidadDeJugadas(page: Page): Promise<number> {
  await page.goto("/mis-jugadas/");
  return page.locator("tbody tr[id^=jugada-]").count();
}

test("sin conexión no se envía; 'Reintentar' crea una sola jugada (FR-031)", async ({ page, context }, info) => {
  test.skip(info.project.name !== "escritorio", "Una pasada alcanza");
  await ingresarComo(page, "usuaria", "/mis-jugadas/");
  const antes = await cantidadDeJugadas(page);
  await page.goto(NUEVA);
  await completarJugada(page, numerosAlAzar(), "1234,56");
  await context.setOffline(true);
  await page.getByRole("button", { name: "Registrar jugada" }).click();
  const aviso = page.locator("[data-sin-conexion]");
  await expect(aviso).toContainText(msg("gral.sin_conexion"));
  await expect(page).toHaveURL(new RegExp(`${NUEVA}$`));
  await context.setOffline(false);
  await aviso.getByRole("button", { name: msg("gral.reintentar") }).click();
  await page.waitForURL(/\/mis-jugadas\/$/);
  // Volver atrás y reenviar el mismo formulario (misma clave) no duplica la jugada.
  await page.goBack();
  if (page.url().endsWith(NUEVA)) {
    await page.getByRole("button", { name: "Registrar jugada" }).click().catch(() => {});
  }
  expect(await cantidadDeJugadas(page)).toBe(antes + 1);
});

test("sesión vencida: ingresar y ver el formulario precargado sin enviarse (FR-032)", async ({ page, context }, info) => {
  test.skip(info.project.name !== "escritorio" && info.project.name !== "sin-scripts", "Escritorio con y sin scripts");
  await ingresarComo(page, "usuaria", NUEVA);
  const antes = await cantidadDeJugadas(page);
  await page.goto(NUEVA);
  const numeros = numerosAlAzar();
  await completarJugada(page, numeros, "777,70");
  const cookies = await context.cookies();
  await context.clearCookies();
  await context.addCookies(cookies.filter((c) => c.name !== "sessionid"));
  await page.getByRole("button", { name: "Registrar jugada" }).click();
  await expect(page.getByText(msg("cuenta.sesion_vencida"))).toBeVisible();
  const { correo, contrasena } = JSON.parse(
    (await import("node:fs")).readFileSync(new URL("../.credenciales.json", import.meta.url), "utf8"),
  ).usuaria;
  await page.getByLabel("Correo electrónico").fill(correo);
  await page.getByLabel("Contraseña", { exact: true }).fill(contrasena);
  await page.getByRole("button", { name: "Ingresar" }).click();
  // [003] AC-14.4: si el formulario vive en Next.js e "Ingresar" en Django, un paso más y explícito.
  const volver = page.getByRole("button", { name: msg("cuenta.volver_formulario") });
  await expect(volver.or(page.getByLabel(/^Costo/))).toBeVisible();
  if (await volver.isVisible()) await volver.click();
  await expect(page.getByLabel(/^Costo/)).toHaveValue("777,70");
  for (const n of numeros) await expect(page.getByLabel(n, { exact: true })).toBeChecked();
  expect(await cantidadDeJugadas(page)).toBe(antes); // nada se envió solo
});

test("un correo de 80 caracteres no desborda a 360 px (FR-030)", async ({ page }, info) => {
  test.skip(info.project.name !== "movil", "Solo a 360 px");
  const local = `persona-con-un-correo-muy-largo-${Date.now()}`.padEnd(66, "x");
  const correo = `${local}@e2e.local`.slice(0, 80);
  await page.goto("/registrarse/");
  await page.getByLabel("Correo electrónico").fill(correo);
  await page.getByLabel("Contraseña", { exact: true }).fill("clave-segura-123");
  await page.getByRole("button", { name: "Crear cuenta" }).click();
  await page.waitForURL(/\/mis-jugadas\//);
  await sinDesplazamientoHorizontal(page);
  await page.getByRole("button", { name: msg("nav.menu") }).click();
  await sinDesplazamientoHorizontal(page);
  const cuenta = page.getByRole("button", { name: msg("nav.cuenta", { correo }) });
  await expect(cuenta).toHaveAttribute("title", correo);
});
