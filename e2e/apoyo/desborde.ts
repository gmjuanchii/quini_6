// [003] NFR-003, SC-006: sin desplazamiento horizontal de la página.
import { expect, type Page } from "@playwright/test";

export async function sinDesplazamientoHorizontal(page: Page) {
  const { ancho, visible } = await page.evaluate(() => ({
    ancho: document.documentElement.scrollWidth,
    visible: document.documentElement.clientWidth,
  }));
  expect(ancho, "La página no debe desplazarse horizontalmente").toBeLessThanOrEqual(visible);
}
