// [003] HU-07 (quickstart #10): opciones completas, filtros alineados, número fuera de rango al
// instante, tabla ordenable y aviso informativo visible.
import { expect, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";

const numero = (page) => page.getByLabel("Número", { exact: true });

test("las opciones de modalidad se leen completas (AC-7.1)", async ({ page }) => {
  await page.goto("/estadisticas/");
  const modalidad = page.getByLabel("Modalidad");
  await expect(modalidad.locator("option")).toHaveText([
    "Tradicional – Primer Sorteo",
    "Tradicional – La Segunda",
    "Revancha",
    "Siempre Sale",
  ]);
  // El control cerrado muestra el texto entero: su ancho alcanza para la opción elegida.
  const recortado = await modalidad.evaluate((el: HTMLSelectElement) => el.scrollWidth > el.clientWidth + 1);
  expect(recortado).toBe(false);
});

test("filtros alineados en escritorio y sin superponerse a 360 px (AC-7.2)", async ({ page }, info) => {
  await page.goto("/estadisticas/");
  const campos = [page.getByLabel("Modalidad"), page.getByLabel("Desde", { exact: true }), page.getByLabel("Hasta", { exact: true })];
  const cajas = await Promise.all(campos.map(async (c) => (await c.boundingBox())!));
  if (info.project.name === "escritorio") {
    const bases = cajas.map((c) => Math.round(c.y + c.height));
    expect(Math.max(...bases) - Math.min(...bases)).toBeLessThanOrEqual(2);
    const consultar = (await page.getByRole("button", { name: "Consultar" }).boundingBox())!;
    const campoNumero = (await numero(page).boundingBox())!;
    expect(Math.abs(consultar.y + consultar.height - (campoNumero.y + campoNumero.height))).toBeLessThanOrEqual(2);
  }
  // Ninguna caja se superpone con otra.
  for (let i = 0; i < cajas.length; i++) {
    for (let j = i + 1; j < cajas.length; j++) {
      const a = cajas[i];
      const b = cajas[j];
      const separadas = a.x + a.width <= b.x || b.x + b.width <= a.x || a.y + a.height <= b.y || b.y + b.height <= a.y;
      expect(separadas).toBe(true);
    }
  }
  await sinDesplazamientoHorizontal(page);
});

test("46 muestra el error al salir del campo y no consulta (AC-7.6)", async ({ page }, info) => {
  test.skip(info.project.name === "sin-scripts", "La validación previa necesita scripts");
  await page.goto("/estadisticas/");
  await numero(page).fill("46");
  await numero(page).press("Tab");
  await expect(page.locator("#est-numero_error")).toHaveText(msg("jugada.fuera_de_rango"));
  await page.getByRole("button", { name: "Consultar" }).click();
  await expect(page).toHaveURL(/\/estadisticas\/$/);
  await expect(numero(page)).toBeFocused();
});

test("sin scripts, 46 se rechaza en el servidor junto al campo (AC-7.6)", async ({ page }, info) => {
  test.skip(info.project.name !== "sin-scripts", "Versión básica");
  await page.goto("/estadisticas/?numero=46");
  await expect(page.locator("#est-numero_error")).toHaveText(msg("jugada.fuera_de_rango"));
});

test("ordenar por frecuencia y volver por número (AC-7.5)", async ({ page }) => {
  await page.goto("/estadisticas/");
  const tabla = page.getByRole("table");
  await tabla.getByRole("link", { name: /^Frecuencia/ }).click();
  await expect(page).toHaveURL(/orden=frecuencia/);
  await expect(tabla.getByRole("columnheader", { name: /Frecuencia/ })).toHaveAttribute("aria-sort", "ascending");
  await tabla.getByRole("link", { name: /^Frecuencia/ }).click();
  await expect(tabla.getByRole("columnheader", { name: /Frecuencia/ })).toHaveAttribute("aria-sort", "descending");
  const valores = await tabla.locator("tbody tr td:first-of-type").allTextContents();
  const numeros = valores.map(Number);
  expect([...numeros].sort((a, b) => b - a)).toEqual(numeros);
  await tabla.getByRole("link", { name: /^Número/ }).click();
  await expect(tabla.locator("tbody tr th").first()).toHaveText("00");
});

test("el aviso informativo se ve antes de los resultados (AC-10.1)", async ({ page }, info) => {
  await page.goto("/estadisticas/");
  const aviso = page.locator("#est-leyenda");
  await expect(aviso).toContainText(msg("est.leyenda"));
  await expect(aviso.locator("svg")).toBeVisible();
  if (info.project.name !== "sin-scripts") await sinIncidenciasGraves(page);
  await sinDesplazamientoHorizontal(page);
});
