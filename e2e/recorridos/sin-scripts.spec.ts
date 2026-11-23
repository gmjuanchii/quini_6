// [003] T142 (quickstart #19, NFR-007): sin scripts todo sigue funcionando con su versión básica.
import { expect, test } from "@playwright/test";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

test.beforeEach(async ({}, info) => {
  test.skip(info.project.name !== "sin-scripts", "Solo sin scripts");
});

test("filtro y paginación de Extracción histórica por la dirección", async ({ page }) => {
  await ingresarComo(page, "admin", "/administracion/extracciones/");
  await page.getByLabel(msg("ext.filtro_estado")).selectOption("finalizada");
  await page.getByRole("button", { name: msg("ext.filtrar") }).click();
  await expect(page).toHaveURL(/estado=finalizada/);
  await expect(page.getByText(msg("ext.filtro_aplicado", { filtro: msg("etiqueta.finalizada") }))).toBeVisible();
  await page.goto("/administracion/extracciones/?orden=periodo");
  const paginacion = page.getByRole("navigation", { name: "Paginación" });
  await paginacion.getByRole("link", { name: msg("pag.siguiente") }).click();
  await expect(page).toHaveURL(/orden=periodo/);
  await expect(page).toHaveURL(/pagina=2/);
});

test("eliminar con confirmación en una página aparte", async ({ page }) => {
  await ingresarComo(page, "admin", "/administracion/extracciones/");
  const fila = page.locator("tbody tr[id^=fila-]").filter({ has: page.locator("a[data-confirmar]") }).first();
  await fila.locator("summary").click();
  await fila.getByRole("menuitem", { name: msg("ext.eliminar") }).click();
  await expect(page).toHaveURL(/\/eliminar\/$/);
  await expect(page.getByRole("button", { name: msg("ext.eliminar") })).toBeVisible();
  await page.getByRole("link", { name: msg("ext.cancelar") }).click();
  await expect(page).toHaveURL(/\/administracion\/extracciones\/$/);
});

test("el calendario del navegador y los atajos como enlaces", async ({ page }) => {
  await ingresarComo(page, "admin", "/administracion/extracciones/");
  await expect(page.getByLabel(msg("ext.campo_inicio"), { exact: true })).toHaveAttribute("type", "date");
  await page.getByRole("link", { name: msg("ext.atajo_anio_anterior") }).click();
  await expect(page).toHaveURL(/atajo=anio_anterior/);
  const anterior = new Date().getFullYear() - 1;
  await expect(page.getByLabel(msg("ext.campo_inicio"), { exact: true })).toHaveValue(`${anterior}-01-01`);
});

test("ingresar y registrar una jugada", async ({ page }) => {
  await ingresarComo(page, "usuaria", "/mis-jugadas/nueva/");
  await page.getByLabel(/^(Concurso|Sorteo)$/).selectOption({ index: 1 });
  const elegidos = new Set<string>();
  while (elegidos.size < 6) elegidos.add(String(Math.floor(Math.random() * 46)).padStart(2, "0"));
  // Sin scripts, la casilla visible es la etiqueta (la entrada está oculta a la vista).
  for (const n of elegidos) await page.locator("label", { has: page.locator(`input[value="${n}"]`) }).click();
  await page.getByLabel(/^Costo/).fill("100");
  await page.getByRole("button", { name: "Registrar jugada" }).click();
  await expect(page).toHaveURL(/\/mis-jugadas\/$/);
  await expect(page.locator("main [data-aviso=success]")).toContainText(msg("jugada.registrada"));
});

test("cambiar el tema con el formulario", async ({ page }) => {
  await page.goto("/resultados/");
  await page.getByRole("radio", { name: msg("tema.oscuro") }).check();
  await page.getByRole("button", { name: msg("tema.guardar") }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "oscuro");
  await page.getByRole("radio", { name: msg("tema.dispositivo") }).check();
  await page.getByRole("button", { name: msg("tema.guardar") }).click();
  await expect(page.locator("html")).not.toHaveAttribute("data-theme", /./);
});
