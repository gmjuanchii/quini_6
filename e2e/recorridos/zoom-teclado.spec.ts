// [003] T143 (SC-005, SC-006): con el texto al 200 % ninguna pantalla se desborda ni oculta
// contenido, y las tareas principales se completan solo con el teclado.
import { expect, type Page, test } from "@playwright/test";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

async function conZoom(page: Page) {
  await page.evaluate(() => {
    document.documentElement.style.fontSize = "200%";
  });
}

async function sinDesborde(page: Page, ruta: string) {
  const medidas = await page.evaluate(() => ({
    ancho: document.documentElement.scrollWidth,
    visible: document.documentElement.clientWidth,
  }));
  expect(medidas.ancho, `${ruta}: desplazamiento horizontal con el texto al 200 %`).toBeLessThanOrEqual(medidas.visible);
}

const PANTALLAS: Array<["admin" | "usuaria" | null, string]> = [
  [null, "/resultados/"],
  [null, "/estadisticas/"],
  [null, "/ingresar/"],
  [null, "/registrarse/"],
  ["usuaria", "/mis-jugadas/"],
  ["usuaria", "/mis-jugadas/nueva/"],
  ["admin", "/administracion/extracciones/"],
  ["admin", "/administracion/concursos/"],
];

test("texto al 200 % sin desplazamiento horizontal (SC-006)", async ({ page, context }, info) => {
  test.skip(info.project.name !== "escritorio" && info.project.name !== "movil", "Escritorio y teléfono");
  let actual: string | null = null;
  for (const [perfil, ruta] of PANTALLAS) {
    if (perfil && perfil !== actual) {
      await context.clearCookies();
      await ingresarComo(page, perfil, ruta);
      actual = perfil;
    }
    await page.goto(ruta);
    await conZoom(page);
    await sinDesborde(page, ruta);
    await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible();
  }
});

test("consultar un número de las estadísticas solo con el teclado (SC-005)", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Teclado en escritorio");
  await page.goto("/estadisticas/");
  await page.getByLabel("Número", { exact: true }).focus();
  await page.keyboard.type("14");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("button", { name: "Consultar" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/numero=14/);
  await expect(page.locator("#numero-consultado")).toContainText("El 14 salió en");
});

test("ingresar y abrir el detalle de una extracción solo con el teclado (SC-005)", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Teclado en escritorio");
  const { correo, contrasena } = JSON.parse(
    (await import("node:fs")).readFileSync(new URL("../.credenciales.json", import.meta.url), "utf8"),
  ).admin;
  await page.goto("/ingresar/?next=/administracion/extracciones/");
  await page.getByLabel("Correo electrónico").focus();
  await page.keyboard.type(correo);
  await page.keyboard.press("Tab");
  await page.keyboard.type(contrasena);
  await page.keyboard.press("Enter");
  await page.waitForURL(/\/administracion\/extracciones\/$/);
  const enlace = page.locator("tbody tr[id^=fila-] [data-enlace-fila]").first();
  await enlace.focus();
  await expect(enlace).toBeVisible(); // "Ver detalle →" aparece al recibir el foco
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/\/administracion\/extracciones\/\d+\/$/);
  await expect(page.getByRole("link", { name: msg("nav.volver_extracciones").replace("← ", "") })).toBeVisible();
});
