// [003] HU-04 (quickstart #7): campos de fecha, calendario propio, atajos y mensajes junto al campo.
import { expect, type Page, test } from "@playwright/test";
import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { diaDelCalendario, diasDeshabilitadosDelMes, mesDelCalendario, primerDiaDeLaSemana } from "../apoyo/calendario";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const EXTRACCION = "/administracion/extracciones/";

function dos(n: number) {
  return String(n).padStart(2, "0");
}

/** "Hoy" del servidor (America/Argentina/Buenos_Aires), igual que RN-04. */
function hoy() {
  const partes = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Argentina/Buenos_Aires" }).formatToParts(new Date());
  const valor = (tipo: string) => Number(partes.find((p) => p.type === tipo)!.value);
  return { anio: valor("year"), mes: valor("month"), dia: valor("day") };
}

const inicio = (page: Page) => page.getByLabel("Fecha de inicio", { exact: true });
const fin = (page: Page) => page.getByLabel("Fecha de finalización", { exact: true });
const errorDe = (page: Page, id: string) => page.locator(`#${id}_error`);

test.describe("con scripts", () => {
  test.beforeEach(async ({ page }, info) => {
    test.skip(info.project.name === "sin-scripts", "El calendario propio necesita scripts");
    await ingresarComo(page, "admin", EXTRACCION);
  });

  test("escribir 01012025 agrega las barras (AC-4.2, [002] D-27)", async ({ page }) => {
    await expect(inicio(page)).toHaveAttribute("type", "text");
    await inicio(page).click();
    await page.keyboard.type("01012025");
    await expect(inicio(page)).toHaveValue("01/01/2025");
    await fin(page).fill("2025-03-02"); // una fecha AAAA-MM-DD pegada se convierte
    await expect(fin(page)).toHaveValue("02/03/2025");
  });

  test("el calendario: lunes primero, en español, Escape devuelve el foco (AC-4.2, AC-4.6)", async ({ page }) => {
    await inicio(page).fill("15/01/2025");
    const boton = page.locator("[data-campo-fecha='inicio']").getByRole("button", { name: msg("fecha.abrir_calendario") });
    await boton.click();
    const dialogo = page.getByRole("dialog");
    await expect(dialogo).toBeVisible();
    await expect(diaDelCalendario(dialogo, 15, "enero")).toBeVisible(); // en español
    const primerDia = await primerDiaDeLaSemana(dialogo);
    expect(primerDia.startsWith("l"), `la semana empieza el lunes (${primerDia})`).toBe(true);
    // AC-4.6: no tapa los campos que se completan.
    const campo = (await inicio(page).boundingBox())!;
    const caja = (await dialogo.boundingBox())!;
    const tapa = caja.y < campo.y + campo.height && caja.y + caja.height > campo.y;
    expect(tapa, "el calendario no tapa el campo").toBe(false);
    await page.keyboard.press("Escape");
    await expect(dialogo).toBeHidden();
    await expect(inicio(page)).toBeFocused();
  });

  test("elegir un rango en el mismo calendario (AC-4.3)", async ({ page }) => {
    await inicio(page).fill("01/01/2025");
    await page.locator("[data-campo-fecha='inicio']").getByRole("button", { name: msg("fecha.abrir_calendario") }).click();
    const dialogo = page.getByRole("dialog");
    await expect(mesDelCalendario(dialogo)).toBeVisible();
    await diaDelCalendario(dialogo, 3, "enero").click();
    await diaDelCalendario(dialogo, 17, "enero").click();
    await expect(inicio(page)).toHaveValue("03/01/2025");
    await expect(fin(page)).toHaveValue("17/01/2025");
    await expect(page.getByRole("dialog")).toBeHidden();
  });

  test("el atajo completa las fechas y se pueden modificar (AC-4.4)", async ({ page }) => {
    const { anio, mes, dia } = hoy();
    await page.getByRole("link", { name: msg("ext.atajo_anio_en_curso") }).click();
    await expect(page).toHaveURL(new RegExp(`${EXTRACCION}$`)); // sin navegar
    await expect(inicio(page)).toHaveValue(`01/01/${anio}`);
    await expect(fin(page)).toHaveValue(`${dos(dia)}/${dos(mes)}/${anio}`);
    await expect(page.getByRole("link", { name: msg("est.atajo_todo") })).toHaveCount(0);
    await inicio(page).fill(`02/01/${anio}`);
    await expect(inicio(page)).toHaveValue(`02/01/${anio}`);
  });

  test("mensajes junto al campo al salir (AC-4.5)", async ({ page }) => {
    for (const fecha of ["31/02/2025", "29/02/2025"]) {
      await inicio(page).fill(fecha);
      await fin(page).focus();
      await expect(errorDe(page, "id_inicio")).toHaveText(msg("fecha.inexistente", { fecha }));
      await expect(inicio(page)).toHaveAttribute("aria-invalid", "true");
    }
    await inicio(page).fill("29/02/2024");
    await fin(page).focus();
    await expect(errorDe(page, "id_inicio")).toBeHidden();
    await inicio(page).fill("01/01/2025");
    await fin(page).fill("01/12/2024");
    await inicio(page).focus();
    await expect(errorDe(page, "id_fin")).toHaveText(msg("fecha.fin_anterior", { fecha: "01/01/2025" }));
  });

  test("al enviar con errores no se envía y el foco va al primero (FR-033)", async ({ page }) => {
    await page.getByRole("button", { name: msg("ext.boton_iniciar") }).click();
    await expect(page.getByRole("alert").filter({ hasText: msg("form.no_avanza", { n: 2 }) })).toBeVisible();
    await expect(errorDe(page, "id_inicio")).toHaveText(msg("fecha.falta_inicio"));
    await expect(inicio(page)).toBeFocused();
    await expect(page).toHaveURL(new RegExp(`${EXTRACCION}$`));
  });

  test("los días futuros están deshabilitados en la extracción (AC-4.7)", async ({ page }) => {
    const { anio, mes, dia } = hoy();
    await fin(page).fill(`${dos(dia)}/${dos(mes)}/${anio}`);
    await page.locator("[data-campo-fecha='fin']").getByRole("button", { name: msg("fecha.abrir_calendario") }).click();
    const dialogo = page.getByRole("dialog");
    await expect(mesDelCalendario(dialogo)).toBeVisible();
    const deshabilitados = await diasDeshabilitadosDelMes(dialogo);
    const diasDelMes = new Date(anio, mes, 0).getDate();
    expect(deshabilitados).toBe(diasDelMes - dia);
  });

  test("en el teléfono el campo no desborda y no hay incidencias de accesibilidad (AC-4.1)", async ({ page }) => {
    await sinDesplazamientoHorizontal(page);
    const ancho = (await inicio(page).boundingBox())!.width;
    expect(ancho, "el campo no ocupa todo el ancho").toBeLessThan(page.viewportSize()!.width * 0.8);
    await sinIncidenciasGraves(page);
  });
});

test.describe("sin scripts", () => {
  test.beforeEach(async ({ page }, info) => {
    test.skip(info.project.name !== "sin-scripts", "Versión básica");
    await ingresarComo(page, "admin", EXTRACCION);
  });

  test("calendario del navegador y atajos como enlaces (componentes.md § 4)", async ({ page }) => {
    await expect(inicio(page)).toHaveAttribute("type", "date");
    await expect(page.getByRole("button", { name: msg("fecha.abrir_calendario") }).first()).toBeHidden();
    await page.getByRole("link", { name: msg("ext.atajo_anio_anterior") }).click();
    const anio = hoy().anio - 1;
    await expect(page).toHaveURL(/\?atajo=anio_anterior$/);
    await expect(inicio(page)).toHaveValue(`${anio}-01-01`);
    await expect(fin(page)).toHaveValue(`${anio}-12-31`);
  });

  test("el servidor repite la validación con el mismo mensaje (FR-012)", async ({ page }) => {
    await page.getByRole("button", { name: msg("ext.boton_iniciar") }).click();
    await expect(errorDe(page, "id_inicio")).toHaveText(msg("fecha.falta_inicio"));
    await expect(errorDe(page, "id_fin")).toHaveText(msg("fecha.falta_fin"));
  });
});
