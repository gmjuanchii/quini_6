// [003] AC-14.1, AC-14.2, R-19 (quickstart #22, #23): prueba obligatoria de sesión compartida
// (T169, "T208" del pedido de planificación). Bloquea la migración de pantallas (T171).
//
// Con /administracion/extracciones/* servida por Next.js en el entorno de pruebas: ingresar en
// Django, abrir la pantalla de Next.js sin volver a ingresar y con el mismo encabezado, volver a
// Django, salir y comprobar que Next.js ya no muestra datos privados. Con una cuenta sin permisos
// de administración, "Sin permisos" en ambas interfaces.
import { expect, test } from "@playwright/test";

import { sinIncidenciasGraves } from "../apoyo/accesibilidad";
import { irA, seccionesDelEncabezado, soloEnConvivencia } from "../apoyo/convivencia";
import { sinDesplazamientoHorizontal } from "../apoyo/desborde";
import { msg } from "../apoyo/mensajes";
import { ingresarComo } from "../apoyo/sesion";

const EXTRACCIONES = "/administracion/extracciones/";

test.beforeEach(() => soloEnConvivencia());

test("una sola sesión para Django y Next.js; salir alcanza a ambas (AC-14.1, AC-14.2)", async ({ page }, info) => {
  await ingresarComo(page, "admin", "/resultados/");
  await irA(page, "/resultados/", "django");
  const correo = await page.getByTitle(/@e2e\.local$/).first().getAttribute("title");
  const seccionesDjango = await seccionesDelEncabezado(page);

  // Next.js: ya autenticado, con el mismo encabezado y sin volver a ingresar.
  await irA(page, EXTRACCIONES, "next");
  await expect(page).toHaveURL(new RegExp(`${EXTRACCIONES}$`));
  await expect(page.getByRole("heading", { level: 1, name: msg("ext.titulo") })).toBeVisible();
  await expect(page.getByTitle(correo!).first()).toBeAttached();
  expect(await seccionesDelEncabezado(page)).toEqual(seccionesDjango);
  if (info.project.name !== "movil" || (await page.locator("[data-boton-menu]").isHidden())) {
    await expect(
      page.getByRole("navigation", { name: "Navegación principal" }).getByRole("link", { name: msg("nav.administracion") }),
    ).toHaveAttribute("aria-current", "page");
  }
  if (info.project.name !== "sin-scripts") await sinIncidenciasGraves(page);
  await sinDesplazamientoHorizontal(page);

  // De vuelta en Django, la sesión sigue.
  await irA(page, "/mis-jugadas/", "django");
  await expect(page).toHaveURL(/\/mis-jugadas\/$/);

  // Salir desde Next.js (formulario POST que atiende Django) cierra la sesión en ambas.
  await irA(page, EXTRACCIONES, "next");
  if (info.project.name !== "sin-scripts") {
    if (await page.locator("[data-boton-menu]").isVisible()) await page.locator("[data-boton-menu]").click();
    await page.getByRole("button", { name: msg("nav.cuenta", { correo: correo! }) }).click();
  }
  await page.getByRole("button", { name: msg("nav.salir") }).click();
  await page.waitForURL(/\/resultados\/$/);

  await page.goto(EXTRACCIONES);
  await expect(page).toHaveURL(/\/ingresar\/\?next=/);
  await expect(page.getByText(correo!)).toHaveCount(0);
  await page.goto("/mis-jugadas/");
  await expect(page).toHaveURL(/\/ingresar\/\?next=/);
});

test("una cuenta sin permisos de administración ve 'Sin permisos' en ambas (AC-14.1)", async ({ page }) => {
  await ingresarComo(page, "sinjugadas", "/resultados/");

  const enDjango = await irA(page, "/administracion/concursos/", "django");
  expect(enDjango?.status()).toBe(403);
  await expect(page.getByText(msg("admin.sin_permiso"))).toBeVisible();

  const enNext = await irA(page, EXTRACCIONES, "next");
  expect(enNext?.status()).toBe(403);
  await expect(page.getByText(msg("admin.sin_permiso"))).toBeVisible();
  await expect(page.getByRole("heading", { level: 1, name: msg("gral.titulo_acceso_restringido") })).toBeVisible();
});

test("las páginas privadas de Next.js no se guardan en caché (NFR-008)", async ({ page }) => {
  await ingresarComo(page, "admin", "/resultados/");
  const respuesta = await irA(page, EXTRACCIONES, "next");
  expect(respuesta?.headers()["cache-control"]).toContain("no-store");
});
