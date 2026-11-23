// [003] T144 (T205 adelantada, hallazgo D1): recorridos de administración de sorteos de
// specs/001-quini6-mvp/quickstart.md (escenarios C, D y F) contra la interfaz de la Etapa 1.
// [003] T205: ampliado con lo especificado en T204 (premios, revisión y corrección), para que el
// mismo guion valide la pantalla 6 en Django y en Next.js.
import { expect, type Page, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const BASE = "/administracion/concursos";

function bloqueNumeros(page: Page) {
  const seccion = page.getByRole("region", { name: "Tradicional – Primer Sorteo" });
  return seccion.locator("div").filter({ has: page.getByRole("heading", { name: /^Números/ }) }).last();
}

test("crear, cargar, observar, resolver, publicar y ver el historial de un sorteo", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Recorrido largo: una pasada alcanza");
  test.setTimeout(90_000);
  const numero = String(5000 + Math.floor(Math.random() * 4000));
  await ingresarComo(page, "admin", `${BASE}/`);

  // Escenario C: crear el sorteo y el duplicado.
  await page.getByRole("link", { name: msg("admin.crear") }).first().click();
  await page.getByLabel("Número de sorteo").fill(numero);
  await page.getByRole("textbox", { name: "Fecha del sorteo" }).fill("15/01/2025");
  await page.getByLabel("Tradicional – Primer Sorteo").check();
  await page.getByRole("button", { name: msg("admin.crear") }).click();
  await expect(page).toHaveURL(new RegExp(`${BASE}/${numero}/$`));
  await expect(page.locator("[data-aviso-toast]")).toContainText(`Se creó el sorteo N.º ${numero}.`);
  await sinIncidenciasGraves(page);

  await page.goto(`${BASE}/nuevo/`);
  await page.getByLabel("Número de sorteo").fill(numero);
  await page.getByRole("textbox", { name: "Fecha del sorteo" }).fill("15/01/2025");
  await page.getByLabel("Tradicional – Primer Sorteo").check();
  await page.getByRole("button", { name: msg("admin.crear") }).click();
  await expect(page.getByRole("alert").filter({ hasText: msg("admin.concurso_duplicado", { N: numero }) })).toBeVisible();

  // Escenario D: borrador, observación, resolución y publicación.
  await page.goto(`${BASE}/${numero}/`);
  await bloqueNumeros(page).getByRole("link", { name: "Cargar" }).click();
  for (const [i, n] of ["03", "08", "14", "21", "32", "40"].entries()) {
    await page.getByLabel(`Número ${i + 1}`, { exact: true }).fill(n);
  }
  await page.getByLabel("Fuente (descripción)").fill("Extracto oficial de prueba");
  await page.getByRole("textbox", { name: "Fecha de consulta de la fuente" }).fill("16/01/2025");
  await page.getByRole("button", { name: "Guardar borrador" }).click();
  await expect(page).toHaveURL(new RegExp(`${BASE}/${numero}/$`));
  await expect(bloqueNumeros(page)).toContainText("Borrador");

  const observar = bloqueNumeros(page).locator("details").filter({ hasText: "Marcar como Observado" });
  await observar.locator("summary").click();
  await observar.getByLabel(/Motivo/).fill("Revisar la fuente");
  await observar.getByRole("button", { name: "Observar" }).click();
  await expect(bloqueNumeros(page)).toContainText("Observado: Revisar la fuente");
  await bloqueNumeros(page).getByRole("button", { name: "Resolver observación" }).click();
  await expect(bloqueNumeros(page)).toContainText("Borrador");

  await bloqueNumeros(page).getByRole("link", { name: "Revisar y publicar" }).click();
  await page.getByLabel(msg("admin.confirmar_cotejo")).check();
  await page.getByRole("button", { name: "Publicar" }).click();
  await expect(page).toHaveURL(new RegExp(`${BASE}/${numero}/$`));
  await expect(bloqueNumeros(page).getByRole("list", { name: "Números publicados" })).toContainText("14");

  // Escenario F: el historial registra lo hecho.
  await page.getByRole("link", { name: "Ver historial" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText(`sorteo N.º ${numero}`);
  await expect(page.getByRole("table")).toContainText("Crear sorteo");
  await expect(page.getByRole("table")).toContainText("Publicar");
  await sinIncidenciasGraves(page);
});

function bloque(page: Page, nombre: RegExp) {
  const seccion = page.getByRole("region", { name: "Tradicional – Primer Sorteo" });
  return seccion.locator("div").filter({ has: page.getByRole("heading", { name: nombre }) }).last();
}

test("premios, revisión y corrección de un bloque publicado ([001] US2, US7; [003] T204)", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Recorrido largo: una pasada alcanza");
  test.setTimeout(120_000);
  const numero = String(1000 + Math.floor(Math.random() * 3000));
  await ingresarComo(page, "admin", `${BASE}/nuevo/`);
  await page.getByLabel("Número de sorteo").fill(numero);
  await page.getByRole("textbox", { name: "Fecha del sorteo" }).fill("15/01/2025");
  await page.getByLabel("Tradicional – Primer Sorteo").check();
  await page.getByRole("button", { name: msg("admin.crear") }).click();
  await expect(page).toHaveURL(new RegExp(`${BASE}/${numero}/$`));

  // Premios: categorías fijas, vacío = no disponible.
  await bloque(page, /^Premios/).getByRole("link", { name: "Cargar" }).click();
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Premios de Tradicional – Primer Sorteo");
  await page.getByLabel("Primer Premio: Ganadores").fill("0");
  await page.getByLabel("Segundo Premio: Ganadores").fill("3");
  await page.getByLabel("Fuente (descripción)").fill("Extracto oficial de prueba");
  await page.getByRole("textbox", { name: "Fecha de consulta de la fuente" }).fill("16/01/2025");
  await page.getByRole("button", { name: "Guardar borrador" }).click();
  await expect(page).toHaveURL(new RegExp(`${BASE}/${numero}/$`));
  await expect(bloque(page, /^Premios/)).toContainText("Borrador");

  // Números publicados, luego en revisión, sin revisión y en corrección.
  await bloque(page, /^Números/).getByRole("link", { name: "Cargar" }).click();
  for (const [i, n] of ["01", "09", "17", "25", "33", "41"].entries()) {
    await page.getByLabel(`Número ${i + 1}`, { exact: true }).fill(n);
  }
  await page.getByLabel("Fuente (descripción)").fill("Extracto oficial de prueba");
  await page.getByRole("textbox", { name: "Fecha de consulta de la fuente" }).fill("16/01/2025");
  await page.getByRole("button", { name: "Guardar borrador" }).click();
  await bloque(page, /^Números/).getByRole("link", { name: "Revisar y publicar" }).click();
  await page.getByLabel(msg("admin.confirmar_cotejo")).check();
  await page.getByRole("button", { name: "Publicar" }).click();
  await expect(bloque(page, /^Números/).getByRole("list", { name: "Números publicados" })).toContainText("17");

  const revision = bloque(page, /^Números/).locator("details").filter({ hasText: "Marcar en revisión" });
  await revision.locator("summary").click();
  await revision.getByLabel(/Motivo/).fill("Dudas sobre la fuente");
  await revision.getByRole("button", { name: "Marcar en revisión" }).click();
  await expect(bloque(page, /^Números/)).toContainText("En revisión: Dudas sobre la fuente");

  const quitar = bloque(page, /^Números/).locator("details").filter({ hasText: "Quitar revisión" });
  await quitar.locator("summary").click();
  await quitar.getByLabel(/Motivo/).fill("Fuente verificada");
  await quitar.getByRole("button", { name: "Quitar revisión" }).click();
  await expect(bloque(page, /^Números/)).not.toContainText("En revisión:");

  const corregir = bloque(page, /^Números/).locator("details").filter({ hasText: "Corregir" });
  await corregir.locator("summary").click();
  await corregir.getByLabel(/Motivo/).fill("Error de carga");
  await corregir.getByLabel("Fuente de la corrección (descripción)").fill("Extracto corregido");
  await corregir.getByRole("textbox", { name: "Fecha de consulta de la fuente" }).fill("17/01/2025");
  await corregir.getByRole("button", { name: "Iniciar corrección" }).click();
  await expect(page.getByText("Se inició la corrección").first()).toBeVisible();
  await page.goto(`${BASE}/${numero}/`);
  await expect(bloque(page, /^Números/)).toContainText("Corrección en preparación");
  await sinIncidenciasGraves(page);
});

test("una cuenta sin permisos ve 'Sin permisos' en administración ([001] AC-2.11)", async ({ page }) => {
  await ingresarComo(page, "usuaria", "/resultados/");
  await page.goto(`${BASE}/`);
  await expect(page.getByText(msg("admin.sin_permiso"))).toBeVisible();
});
