// [003] HU-01 (quickstart #1 y #2): distinguir el estado de cada extracción y filtrar por estado.
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const LISTADO = "/administracion/extracciones/";
const ETIQUETAS = ["en_curso", "finalizada", "con_advertencias", "sin_sorteos", "con_error"];

test.beforeEach(async ({ page }) => {
  await ingresarComo(page, "admin", LISTADO);
});

test("cada estado se identifica por su texto y su icono (AC-1.1)", async ({ page }) => {
  const tabla = page.getByRole("table");
  for (const etiqueta of ETIQUETAS) {
    const insignia = tabla.locator("[data-insignia-estado]").filter({ hasText: msg(`etiqueta.${etiqueta}`) }).first();
    await expect(insignia, etiqueta).toBeVisible();
    await expect(insignia.locator("svg").first()).toBeAttached();
  }
});

test("la explicación se lee al enfocar la etiqueta con el teclado (AC-1.2)", async ({ page }) => {
  const insignia = page
    .getByRole("table")
    .locator("[data-insignia-estado='con-advertencias'] [tabindex='0']")
    .first();
  await insignia.focus();
  await expect(insignia).toHaveAccessibleDescription(msg("etiqueta.con_advertencias.explicacion"));
  await expect(page.getByRole("tooltip").filter({ hasText: msg("etiqueta.con_advertencias.explicacion") }).first()).toBeVisible();
});

test("las que requieren revisión se destacan (AC-1.3)", async ({ page }) => {
  const marcadas = page.locator("tr[data-requiere-revision]");
  await expect(marcadas.first()).toBeVisible();
  const textos = await marcadas.allInnerTexts();
  for (const texto of textos) {
    expect(texto.includes(msg("etiqueta.con_advertencias")) || texto.includes(msg("etiqueta.con_error"))).toBe(true);
  }
});

async function filtrar(page, etiqueta: string, sinScripts: boolean) {
  await page.getByLabel(msg("ext.filtro_estado")).selectOption({ label: etiqueta });
  // Sin scripts, el filtro se aplica con el botón (NFR-007); con scripts, al elegir.
  if (sinScripts) await page.getByRole("button", { name: msg("ext.filtrar") }).click();
}

test("filtrar por estado y volver a todos (AC-1.4)", async ({ page }, info) => {
  const sinScripts = info.project.name === "sin-scripts";
  await filtrar(page, msg("etiqueta.con_advertencias"), sinScripts);
  await expect(page).toHaveURL(/estado=con-advertencias/);
  await expect(page.getByText(msg("ext.filtro_aplicado", { filtro: msg("etiqueta.con_advertencias") }))).toBeVisible();
  const estados = await page.getByRole("table").locator("[data-insignia-estado]").evaluateAll((nodos) =>
    nodos.map((n) => n.getAttribute("data-insignia-estado")),
  );
  expect(new Set(estados)).toEqual(new Set(["con-advertencias"]));
  await filtrar(page, msg("ext.filtro_todos"), sinScripts);
  await expect(page.getByRole("table").locator("[data-insignia-estado='finalizada']").first()).toBeVisible();
});

test("el detalle muestra la misma etiqueta y su explicación (AC-1.5)", async ({ page }) => {
  await page.goto(`${LISTADO}?estado=con-error`);
  await page.locator("tbody tr[id^=fila-] [data-enlace-fila]").first().click(); // no el encabezado ordenable
  await expect(page.locator("main [data-insignia-estado='con-error']").first()).toBeVisible();
  await expect(page.locator("main p", { hasText: msg("etiqueta.con_error.explicacion") })).toBeVisible();
});

test("sin incidencias graves de accesibilidad ni desplazamiento horizontal", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "axe se ejecuta dentro de la página");
  await sinIncidenciasGraves(page);
  await sinDesplazamientoHorizontal(page);
});
