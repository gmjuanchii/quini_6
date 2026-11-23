// [003] HU-03 (quickstart #4 a #6): iniciar una extracción y seguir su avance sin recargar.
// Levanta el servidor de fuentes de prueba de [002] y el trabajador con la base E2E (sin internet).
import { type ChildProcess, spawn } from "node:child_process";
import { expect, test } from "@playwright/test";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const LISTADO = "/administracion/extracciones/";
const PUERTO_FUENTES = "8765";
const procesos: ChildProcess[] = [];

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({}, info) => {
  const { python, raiz, entornoDjango } = info.config.metadata as {
    python: string;
    raiz: string;
    entornoDjango: Record<string, string>;
  };
  const base = `http://127.0.0.1:${PUERTO_FUENTES}`;
  const entorno = {
    ...process.env,
    ...entornoDjango,
    QUINI6_FUENTE_F1_URL: `${base}/f1`,
    QUINI6_FUENTE_F2_URL: `${base}/f2`,
    QUINI6_FUENTE_F3_URL: `${base}/f3`,
  };
  const opciones = { cwd: raiz, env: entorno, stdio: "ignore" as const };
  procesos.push(spawn(python, ["-m", "tests.fuentes_prueba.servidor", "--escenario", "normal", "--puerto", PUERTO_FUENTES], opciones));
  procesos.push(spawn(python, ["manage.py", "procesar_extracciones"], opciones));
});

test.afterAll(() => {
  for (const proceso of procesos) proceso.kill();
});

test("iniciar, ver el avance sin recargar y el aviso final (AC-3.1 a AC-3.3, AC-3.6)", async ({ page }, info) => {
  test.skip(info.project.name !== "escritorio", "Recorrido con el trabajador: una sola vez");
  test.setTimeout(180_000);
  await ingresarComo(page, "admin", LISTADO);
  await page.getByLabel("Fecha de inicio", { exact: true }).fill("01/11/2026"); // [003] HU-04: dd/mm/aaaa
  await page.getByLabel("Fecha de finalización", { exact: true }).fill("15/11/2026");
  const boton = page.getByRole("button", { name: msg("ext.boton_iniciar") });
  await boton.click();
  // AC-3.1: la pantalla se actualiza sin cambiar de dirección y aparece "En curso".
  await expect(page).toHaveURL(new RegExp(`${LISTADO}$`));
  const panel = page.locator("#avance-extraccion");
  await expect(panel.getByText(msg("ext.en_curso"))).toBeVisible();
  // AC-3.2: identificando y luego "N de M sorteos procesados", sin recargar.
  await expect(panel.getByText(/de \d+ sorteos procesados/)).toBeVisible({ timeout: 120_000 });
  // AC-3.3: la etiqueta cambia sola y aparece el aviso con el resultado.
  const aviso = page.locator("[data-aviso-toast]");
  await expect(aviso.first()).toBeVisible({ timeout: 150_000 });
  await expect(panel.locator("[data-insignia-estado='en-curso']")).toHaveCount(0);
  // AC-3.6: al volver más tarde se ve el estado real.
  await page.goto(LISTADO);
  await expect(page.locator("tbody tr[id^=fila-]").first().locator("[data-insignia-estado]")).not.toHaveAttribute(
    "data-insignia-estado",
    "en-curso",
  );
});
