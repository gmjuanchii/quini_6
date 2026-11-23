// [003] HU-14 (quickstart #25 a #28): convivencia de Django y Next.js detrás del enrutador.
//
// - AC-14.3: el aviso de una acción que termina en la otra aplicación se muestra igual.
// - AC-14.4: sesión vencida en un formulario de Next.js → "Volver al formulario".
// - AC-14.6: si Next.js no responde, la misma pantalla la sirve Django.
// - R-20: un formulario de Django abierto antes de conmutar su ruta se envía sin errores (marca
//   ?_interfaz=django); un POST sin la marca en una ruta conmutada lo atiende Next.js.
import { expect, test } from "@playwright/test";

import { DJANGO_DIRECTO, URL_SIN_NEXT, atiende, interfaz, irA, soloEnConvivencia } from "../apoyo/convivencia";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const EXTRACCIONES = "/administracion/extracciones/";

test.beforeEach(() => soloEnConvivencia());

test("formulario de Django abierto antes de conmutar: se envía a Django y el aviso se ve en Next.js (R-20, AC-14.3)", async ({ page, baseURL }, info) => {
  test.skip(info.project.name !== "escritorio" && info.project.name !== "sin-scripts", "Elimina datos: un proyecto con y otro sin scripts");
  test.skip(atiende(EXTRACCIONES) === "django", "Requiere la Extracción histórica en Next.js (E2E_RUTAS_NEXT)");
  await ingresarComo(page, "admin", "/resultados/");

  // Una extracción terminada, según el listado de Django.
  const listado = await page.request.get(`${DJANGO_DIRECTO}${EXTRACCIONES}?estado=finalizada`, {
    headers: { cookie: (await page.context().cookies()).map((c) => `${c.name}=${c.value}`).join("; ") },
  });
  const id = /\/administracion\/extracciones\/(\d+)\/eliminar\//.exec(await listado.text())?.[1];
  expect(id, "preparar_e2e deja extracciones finalizadas").toBeTruthy();
  const ruta = `${EXTRACCIONES}${id}/eliminar/`;

  // La página de confirmación se "abrió antes de la conmutación": la sirve Django tal cual.
  await page.route(`**${ruta}`, async (route) => {
    const original = await route.fetch({ url: `${DJANGO_DIRECTO}${ruta}` });
    await route.fulfill({ response: original });
  });
  await page.goto(ruta);
  await page.unroute(`**${ruta}`);

  const envio = page.waitForResponse((r) => r.request().method() === "POST" && r.url().includes(ruta));
  await page.getByRole("button", { name: msg("ext.eliminar") }).click();
  const respuesta = await envio;
  expect(new URL(respuesta.url()).searchParams.get("_interfaz")).toBe("django");
  expect(interfaz(respuesta)).toBe("django");
  expect(respuesta.status()).toBe(303);

  // Termina en el listado, que ya sirve Next.js, con el aviso de Django (AC-14.3).
  await page.waitForURL(new RegExp(`${EXTRACCIONES}$`));
  await expect(page.getByText(/^Se eliminó la extracción del \d{2}\/\d{2}\/\d{4} \d{2}:\d{2}$/).first()).toBeAttached();
  const aviso = await page.request.get(`${baseURL}${EXTRACCIONES}`);
  expect(interfaz(aviso)).toBe("next");
});

test("un POST sin la marca en una ruta conmutada lo atiende Next.js (R-20)", async ({ page }) => {
  test.skip(atiende(EXTRACCIONES) === "django", "Requiere la Extracción histórica en Next.js (E2E_RUTAS_NEXT)");
  const sinMarca = await page.request.post(EXTRACCIONES, { maxRedirects: 0, form: { x: "1" } });
  expect(interfaz(sinMarca)).toBe("next");
  const conMarca = await page.request.post(`${EXTRACCIONES}?_interfaz=django`, { maxRedirects: 0, form: { x: "1" } });
  expect(interfaz(conMarca)).toBe("django");
});

test("si Next.js no responde, la pantalla la sirve Django (AC-14.6, FR-044)", async ({ page }) => {
  test.skip(!URL_SIN_NEXT, "Requiere E2E_URL_SIN_NEXT (enrutador con Next.js detenido)");
  const respuesta = await page.goto(`${URL_SIN_NEXT}${EXTRACCIONES}`);
  expect(interfaz(respuesta)).toBe("django");
  await expect(page).toHaveURL(/\/ingresar\/\?next=/); // la misma regla de acceso, ahora de Django
  await expect(page.getByRole("heading", { level: 1, name: "Ingresar" })).toBeVisible();
});

test("sesión vencida en un formulario de Next.js → 'Volver al formulario' (AC-14.4)", async ({ page, context }, info) => {
  test.skip(atiende("/mis-jugadas/nueva/") !== "next", "Requiere 'Mis jugadas' en Next.js (E2E_RUTAS_NEXT)");
  test.skip(info.project.name !== "escritorio" && info.project.name !== "sin-scripts", "Con y sin scripts");
  await ingresarComo(page, "usuaria", "/mis-jugadas/nueva/");
  await page.getByLabel(/^(Concurso|Sorteo)$/).selectOption({ index: 1 });
  for (const n of ["02", "11", "23", "34", "39", "44"]) await page.getByLabel(n, { exact: true }).check({ force: true });
  await page.getByLabel(/^Costo/).fill("321,00");
  const cookies = await context.cookies();
  await context.clearCookies();
  await context.addCookies(cookies.filter((c) => c.name !== "sessionid"));
  await page.getByRole("button", { name: "Registrar jugada" }).click();
  await expect(page.getByText(msg("cuenta.sesion_vencida"))).toBeVisible();
  const { correo, contrasena } = JSON.parse(
    (await import("node:fs")).readFileSync(new URL("../.credenciales.json", import.meta.url), "utf8"),
  ).usuaria;
  await page.getByLabel("Correo electrónico").fill(correo);
  await page.getByLabel("Contraseña", { exact: true }).fill(contrasena);
  await page.getByRole("button", { name: "Ingresar" }).click();
  // Django ("Ingresar") ofrece volver; el POST explícito lo atiende Next.js, que precarga sin enviar.
  await page.getByRole("button", { name: msg("cuenta.volver_formulario") }).click();
  await expect(page.getByLabel(/^Costo/)).toHaveValue("321,00");
  await expect(page.getByLabel("23", { exact: true })).toBeChecked();
});

test("las rutas que no están conmutadas siguen en Django (contracts/rutas.md § 3)", async ({ page }) => {
  for (const ruta of ["/resultados/", "/estadisticas/", "/ingresar/", "/api/v1/sesion/"]) await irA(page, ruta, "django");
});
