// [003] SC-004: auditoría automática con axe; falla ante incidencias críticas o graves.
import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

import { sinTransicionEntreDocumentos } from "./sesion";

export async function sinIncidenciasGraves(page: Page) {
  // El análisis es del estado en reposo: sin el puntero sobre una fila o un botón (hover) y sin la
  // transición entre documentos en curso (durante el fundido, axe medía contrastes intermedios).
  await page.mouse.move(0, 0);
  await sinTransicionEntreDocumentos(page);
  const resultado = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze();
  const graves = resultado.violations.filter((v) => v.impact === "critical" || v.impact === "serious");
  expect(
    graves.map((v) => `${v.id} (${v.impact}): ${v.nodes.map((n) => n.target.join(" ")).join(", ")}`),
    "Incidencias críticas o graves de accesibilidad",
  ).toEqual([]);
}
