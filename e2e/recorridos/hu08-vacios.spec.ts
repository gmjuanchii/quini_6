// [003] HU-08 (quickstart #11): con la base vacía, cada perfil ve un estado vacío que orienta, y
// un filtro sin resultados se distingue de "sin datos" con "Limpiar filtros".
import { expect, type Page, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { prepararDatos } from "../apoyo/datos";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({}, info) => prepararDatos(info.config, { vacio: true }));
test.afterAll(async ({}, info) => prepararDatos(info.config));

const vacio = (page: Page) => page.locator("[data-estado-vacio]");

async function revisar(page: Page, info) {
  if (info.project.name !== "sin-scripts") await sinIncidenciasGraves(page);
  await sinDesplazamientoHorizontal(page);
}

test("visitante: Resultados sin accesos de administración (AC-8.1, AC-8.4)", async ({ page }, info) => {
  await page.goto("/resultados/");
  await expect(vacio(page)).toHaveCount(1);
  await expect(vacio(page).getByRole("heading", { level: 2 })).toHaveText(msg("vacio.resultados.titulo"));
  await expect(vacio(page).getByRole("link")).toHaveCount(0);
  await page.goto("/estadisticas/");
  await expect(vacio(page).getByRole("heading", { level: 2 })).toHaveText(
    msg("est.sin_sorteos", { modalidad: "Tradicional – Primer Sorteo" }),
  );
  await expect(vacio(page)).toContainText(msg("vacio.estadisticas.explicacion"));
  await revisar(page, info);
});

test("usuaria: 'Mis jugadas' ofrece registrar la primera jugada (AC-8.2)", async ({ page }, info) => {
  await ingresarComo(page, "usuaria", "/mis-jugadas/");
  await expect(vacio(page).getByRole("heading", { level: 2 })).toHaveText(msg("vacio.jugadas.titulo"));
  await expect(vacio(page)).toContainText(msg("vacio.jugadas.explicacion"));
  await revisar(page, info);
  await vacio(page).getByRole("link", { name: msg("vacio.jugadas.accion") }).click();
  await expect(page).toHaveURL(/\/mis-jugadas\/nueva\/$/);
});

test("administración: accesos directos en Resultados y filtros sin resultados (AC-8.3, AC-8.4)", async ({ page }, info) => {
  await ingresarComo(page, "admin", "/resultados/");
  await expect(vacio(page).getByRole("link", { name: msg("vacio.resultados.accion_cargar") })).toBeVisible();
  await expect(vacio(page).getByRole("link", { name: msg("vacio.resultados.accion_extraccion") })).toBeVisible();
  await expect(vacio(page)).toContainText(msg("vacio.resultados_nota_admin"));
  await revisar(page, info);

  await page.goto("/administracion/extracciones/");
  await expect(vacio(page).getByRole("heading", { level: 2 })).toHaveText(msg("vacio.extracciones.titulo"));

  await page.goto("/administracion/extracciones/?estado=con-error");
  await expect(vacio(page)).toHaveAttribute("data-estado-vacio", "sin_resultados");
  await expect(vacio(page)).toContainText(msg("vacio.filtro.explicacion", { filtro: msg("etiqueta.con_error") }));
  await vacio(page).getByRole("link", { name: msg("vacio.filtro.accion") }).click();
  await expect(page).toHaveURL(/\/administracion\/extracciones\/$/);
  await expect(vacio(page)).toHaveAttribute("data-estado-vacio", "sin_datos");
});

test("búsqueda sin coincidencias con 'Limpiar filtros' (AC-8.3)", async ({ page }, info) => {
  await page.goto("/resultados/buscar/?numero=9999");
  await expect(vacio(page)).toHaveAttribute("data-estado-vacio", "sin_resultados");
  await expect(vacio(page).getByRole("heading", { level: 2 })).toHaveText(msg("vacio.filtro.titulo"));
  await revisar(page, info);
  await vacio(page).getByRole("link", { name: msg("vacio.filtro.accion") }).click();
  await expect(page).toHaveURL(/\/resultados\/$/);
});
