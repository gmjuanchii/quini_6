// [003] HU-10 (quickstart #13): cada tipo de mensaje con el mismo icono, rol y ubicación; los avisos
// de éxito se cierran solos a los 6 s y los de error no; el pie legal se lee en el teléfono y en oscuro.
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const toasts = (page) => page.locator("[data-aviso-toast]");

async function registrarJugada(page) {
  await page.goto("/mis-jugadas/nueva/");
  await page.getByLabel(/^(Concurso|Sorteo)$/).selectOption({ index: 1 });
  // Números al azar: otra corrida no debe encontrar la misma jugada (pediría confirmar el duplicado).
  const elegidos = new Set<string>();
  while (elegidos.size < 6) elegidos.add(String(Math.floor(Math.random() * 46)).padStart(2, "0"));
  for (const n of elegidos) {
    await page.getByLabel(n, { exact: true }).check({ force: true });
  }
  await page.getByLabel(/^Costo/).fill("100");
  await page.getByRole("button", { name: "Registrar jugada" }).click();
  await page.waitForURL(/\/mis-jugadas\/(\d+\/)?$/);
}

test("éxito: Toast anunciado que se cierra solo a los 6 s (RN-09, AC-10.3)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Sin scripts queda como aviso en la página");
  await ingresarComo(page, "usuaria", "/mis-jugadas/");
  await registrarJugada(page);
  const exito = toasts(page).filter({ hasText: "Jugada registrada" });
  await expect(exito).toBeVisible();
  await expect(page.getByRole("status").filter({ has: exito })).toHaveCount(1);
  await expect(page.locator("main [data-aviso]")).toHaveCount(0); // pasó de la página al Toast
  await expect(exito).toBeHidden({ timeout: 8_000 });
});

test("error: Toast con rol de alerta que permanece hasta cerrarlo (RN-09)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "Sin scripts queda como aviso en la página");
  await ingresarComo(page, "admin", "/administracion/extracciones/");
  await page.goto("/administracion/extracciones/999999/eliminar/");
  const error = toasts(page).filter({ hasText: msg("ext.no_existe") });
  await expect(error).toBeVisible();
  await expect(page.getByRole("alert").filter({ has: error })).toHaveCount(1);
  await page.waitForTimeout(6_500);
  await expect(error).toBeVisible();
  await error.getByRole("button", { name: msg("aviso.cerrar") }).focus();
  await page.keyboard.press("Enter");
  await expect(error).toBeHidden();
});

test("sin scripts, los mensajes se ven al comienzo del contenido (componentes.md § 4)", async ({ page }, info) => {
  test.skip(info.project.name !== "sin-scripts", "Versión básica");
  await ingresarComo(page, "admin", "/administracion/extracciones/");
  await page.goto("/administracion/extracciones/999999/eliminar/");
  const aviso = page.locator("main [data-aviso=error]");
  await expect(aviso).toHaveAttribute("role", "alert");
  await expect(aviso).toContainText(msg("ext.no_existe"));
  await expect(aviso.locator("svg")).toBeVisible();
});

test("información: el aviso de Estadísticas con icono (AC-10.1)", async ({ page }) => {
  await page.goto("/estadisticas/");
  await expect(page.locator("#est-leyenda svg")).toBeVisible();
  await expect(page.locator("#est-leyenda")).not.toHaveAttribute("role", /alert/);
});

test("el pie legal se lee en el teléfono y en oscuro (AC-10.2)", async ({ page }, info) => {
  await page.goto("/resultados/");
  const pie = page.locator("[data-pie-legal]");
  await expect(pie).toContainText("QUINI_6 no vende apuestas ni realiza pagos");
  const tamano = await pie.evaluate((el) => parseFloat(getComputedStyle(el).fontSize));
  expect(tamano).toBeGreaterThanOrEqual(14);
  await sinDesplazamientoHorizontal(page);
  if (info.project.name !== "sin-scripts") await sinIncidenciasGraves(page);
});
