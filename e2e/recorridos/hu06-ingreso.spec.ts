// [003] HU-06 (quickstart #9): tarjeta centrada, mostrar u ocultar la contraseña, errores antes de
// enviar, credenciales incorrectas, "Ingresando…" y paso entre "Ingresar" y "Crear cuenta".
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";

const correo = (page) => page.getByLabel("Correo electrónico");
const contrasena = (page) => page.getByLabel("Contraseña", { exact: true });

test("tarjeta centrada en escritorio y sin desbordes en el teléfono (AC-6.1)", async ({ page }, info) => {
  await page.goto("/ingresar/");
  const tarjeta = page.locator("[data-tarjeta-cuenta]");
  const caja = (await tarjeta.boundingBox())!;
  const ancho = page.viewportSize()!.width;
  if (info.project.name === "escritorio") {
    expect(caja.width).toBeLessThanOrEqual(28 * 16 + 1);
    expect(Math.abs(caja.x + caja.width / 2 - ancho / 2)).toBeLessThan(20); // centrada
  }
  await sinDesplazamientoHorizontal(page);
  if (info.project.name !== "sin-scripts") await sinIncidenciasGraves(page);
});

test("'Mostrar' y 'Ocultar' la contraseña con anuncio (AC-6.2)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Sin scripts no hay botón");
  await page.goto("/ingresar/");
  await contrasena(page).fill("secreta-123");
  const mostrar = page.getByRole("button", { name: msg("cuenta.mostrar") });
  await expect(mostrar).toHaveAttribute("aria-pressed", "false");
  await mostrar.click();
  await expect(contrasena(page)).toHaveAttribute("type", "text");
  await expect(page.getByText(msg("cuenta.contrasena_visible"))).toBeAttached();
  const ocultar = page.getByRole("button", { name: msg("cuenta.ocultar") });
  await expect(ocultar).toHaveAttribute("aria-pressed", "true");
  await ocultar.click();
  await expect(contrasena(page)).toHaveAttribute("type", "password");
  await expect(contrasena(page)).toHaveValue("secreta-123");
});

test("sin scripts, el campo de contraseña no ofrece 'Mostrar' (componentes.md § 4)", async ({ page }, info) => {
  test.skip(info.project.name !== "sin-scripts", "Versión básica");
  await page.goto("/ingresar/");
  await expect(page.getByRole("button", { name: msg("cuenta.mostrar") })).toBeHidden();
});

test("correo inválido al salir del campo, antes de enviar (AC-6.4)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "La validación previa necesita scripts");
  await page.goto("/ingresar/");
  await correo(page).fill("ana@");
  await contrasena(page).focus();
  await expect(page.locator("#id_email_error")).toHaveText(msg("cuenta.correo_invalido"));
  await expect(correo(page)).toHaveAttribute("aria-invalid", "true");
  await page.getByRole("button", { name: "Ingresar" }).click();
  await expect(page).toHaveURL(/\/ingresar\/$/); // no se envió
  await expect(correo(page)).toBeFocused();
});

test("credenciales incorrectas sin revelar cuál falló (AC-6.3, [001] AC-3.5)", async ({ page }) => {
  await page.goto("/ingresar/");
  await correo(page).fill("nadie@e2e.local");
  await contrasena(page).fill("no-es-la-clave");
  await page.getByRole("button", { name: "Ingresar" }).click();
  await expect(page.getByRole("alert").filter({ hasText: msg("cuenta.credenciales_incorrectas") })).toBeVisible();
  await expect(page.getByText(/olvid|recuper/i)).toHaveCount(0);
});

test("el botón muestra 'Ingresando…' mientras se envía (AC-6.6)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "El estado de trabajo necesita scripts");
  await page.goto("/ingresar/");
  await correo(page).fill("nadie@e2e.local");
  await contrasena(page).fill("no-es-la-clave");
  // Para observar el estado intermedio: la Server Action (fetch) se retiene; el formulario común de
  // Django recibe un 204, que deja la página donde está sin navegar (si se retuviera, Playwright
  // esperaría la navegación pendiente antes de leer la página).
  await page.route("**/ingresar/**", (ruta) => {
    const pedido = ruta.request();
    if (pedido.method() !== "POST") return ruta.continue();
    if (pedido.headers()["next-action"]) return undefined;
    return ruta.fulfill({ status: 204 });
  });
  await page.getByRole("button", { name: "Ingresar" }).click();
  const boton = page.locator("button[data-texto-trabajando]");
  await expect(boton).toHaveText(msg("cuenta.ingresando"));
  await expect(boton).toBeDisabled();
});

test("ir a 'Crear cuenta' y volver conservando el destino (AC-6.7)", async ({ page }) => {
  await page.goto("/ingresar/?next=/mis-jugadas/");
  await page.getByRole("link", { name: "Crear cuenta" }).last().click();
  await expect(page).toHaveURL(/\/registrarse\/\?next=%2Fmis-jugadas%2F|\/registrarse\/\?next=\/mis-jugadas\//);
  await expect(contrasena(page)).toHaveAttribute("autocomplete", "new-password");
  await page.locator("[data-alternativa]").getByRole("link", { name: "Ingresar" }).click();
  await expect(page).toHaveURL(/\/ingresar\/\?next=/);
  await expect(contrasena(page)).toHaveAttribute("autocomplete", "current-password");
});
