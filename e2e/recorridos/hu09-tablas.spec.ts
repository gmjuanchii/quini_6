// [003] HU-09 (quickstart #2 y #12): ordenar por columna, paginar conservando filtro y orden, abrir
// el detalle con un clic en la fila y, a 360 px, tarjetas rotuladas sin desplazamiento horizontal.
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const LISTADO = "/administracion/extracciones/";

test.beforeEach(async ({ page }) => {
  await ingresarComo(page, "admin", LISTADO);
});

test("ordenar por Fecha, Período y Estado (AC-9.1)", async ({ page }, info) => {
  test.skip(info.project.name === "movil", "En el teléfono los encabezados no se muestran");
  const tabla = page.getByRole("table");
  await expect(tabla.getByRole("columnheader", { name: /^Fecha/ })).toHaveAttribute("aria-sort", "descending");
  for (const columna of ["Período", "Estado"]) {
    await tabla.getByRole("link", { name: new RegExp(`^${columna}`) }).click();
    await expect(page).toHaveURL(new RegExp(`orden=${columna === "Período" ? "periodo" : "estado"}`));
    await expect(tabla.getByRole("columnheader", { name: new RegExp(`^${columna}`) })).toHaveAttribute("aria-sort", "ascending");
    await tabla.getByRole("link", { name: new RegExp(`^${columna}`) }).click();
    await expect(tabla.getByRole("columnheader", { name: new RegExp(`^${columna}`) })).toHaveAttribute("aria-sort", "descending");
  }
  // Por estado ascendente, primero lo que requiere atención (data-model § 2).
  await tabla.getByRole("link", { name: /^Estado/ }).click();
  await expect(tabla.locator("tbody tr[id^=fila-]").first()).toContainText(msg("etiqueta.en_curso"));
});

test("paginar conservando el filtro y el orden (AC-9.2, RN-07)", async ({ page }) => {
  await page.goto(`${LISTADO}?orden=periodo`);
  const paginacion = page.getByRole("navigation", { name: "Paginación" });
  await expect(paginacion).toContainText(msg("pag.pagina", { n: 1, m: 2 }));
  await expect(page.locator("tbody tr[id^=fila-extraccion-]")).toHaveCount(20);
  await paginacion.getByRole("link", { name: msg("pag.siguiente") }).click();
  await expect(page).toHaveURL(/orden=periodo/);
  await expect(page).toHaveURL(/pagina=2/);
  await expect(paginacion).toContainText(msg("pag.pagina", { n: 2, m: 2 }));
  await expect(paginacion.locator('[aria-disabled="true"]')).toContainText(msg("pag.siguiente"));
});

test("un clic en la fila abre el detalle; el ⋮ sigue funcionando (AC-9.4)", async ({ page }, info) => {
  const fila = page.locator("tbody tr[id^=fila-extraccion-]").nth(1);
  const id = (await fila.getAttribute("id"))!.replace("fila-extraccion-", "");
  if (info.project.name !== "sin-scripts") {
    await fila.locator("summary").click();
    await expect(fila.getByRole("menuitem").first()).toBeVisible();
    await page.keyboard.press("Escape");
  }
  await fila.scrollIntoViewIfNeeded();
  // Espera a que la página reciba eventos (p. ej. que termine la transición entre documentos).
  await fila.locator("[data-enlace-fila]").click({ trial: true });
  const caja = (await fila.locator("td").first().boundingBox())!;
  await page.mouse.click(caja.x + caja.width / 2, caja.y + caja.height / 2);
  await expect(page).toHaveURL(new RegExp(`/administracion/extracciones/${id}/$`));
});

test("a 360 px, tarjetas rotuladas sin desplazamiento horizontal (AC-9.3)", async ({ page }, info) => {
  test.skip(info.project.name !== "movil", "Solo a 360 px");
  const fila = page.locator("tbody tr[id^=fila-extraccion-]").first();
  const rotulo = await fila.locator("td[data-rotulo=Fecha]").evaluate((td) => getComputedStyle(td, "::before").content);
  expect(rotulo).toContain("Fecha");
  await expect(page.getByRole("columnheader", { name: /^Fecha/ })).not.toBeInViewport();
  await sinDesplazamientoHorizontal(page);
  for (const ruta of ["/resultados/", "/administracion/concursos/"]) {
    await page.goto(ruta);
    await sinDesplazamientoHorizontal(page);
  }
});

test("sin incidencias de accesibilidad en los listados", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "axe necesita scripts");
  await sinIncidenciasGraves(page);
  await page.goto("/resultados/");
  await sinIncidenciasGraves(page);
});
