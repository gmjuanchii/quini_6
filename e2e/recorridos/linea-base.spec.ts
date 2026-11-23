// [003] plan § Fase 0: valida el arnés contra la aplicación (sin aserciones de diseño).
import { expect, test } from "@playwright/test";
import { ingresarComo } from "../apoyo/sesion";

test("una usuaria consulta Resultados, Estadísticas y Mis jugadas", async ({ page }) => {
  await ingresarComo(page, "usuaria");
  await page.goto("/resultados/");
  await expect(page.locator("main")).toBeVisible();
  await page.goto("/estadisticas/");
  await expect(page.locator("main")).toBeVisible();
  await page.goto("/mis-jugadas/");
  await expect(page.locator("main")).toBeVisible();
});
