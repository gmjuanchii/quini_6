// [003] HU-11 (quickstart #14, SC-007): recorre las pantallas con cada perfil y falla si el texto
// visible tiene voseo, tuteo, posesivos de segunda persona, "concurso" o "extracción" suelta.
import { expect, type Page, test } from "@playwright/test";
import { ingresarComo, type Perfil } from "../apoyo/sesion";

const VOSEO =
  /\b(tenés|podés|querés|elegís|buscás|ingresá|elegí|creá|corregí|verificá|intentá|registrá|registraste|iniciá|escribí|volvé|indicaste|hiciste|indicá)\b/giu;
const SEGUNDA_PERSONA = /(?<![\p{L}])(tus?|te)(?![\p{L}])/giu;
const CONCURSO = /(?<![\p{L}])concursos?(?![\p{L}])/giu;
const EXTRACCION = /(?<![\p{L}])extracci[oó]n(es)?(?![\p{L}])/giu;
const EXTRACCION_PERMITIDA =
  /extracci[oó]n(es)? hist[oó]rica|extracci[oó]n finalizada|extracci[oó]n en curso|(la|una|otra|cada|esta|esa|de la|del|iniciar|eliminar) extracci[oó]n|(hay|las) extracciones|extracciones (anteriores|terminadas)|extracci[oó]n del \d/giu;

function prohibidas(texto: string): string[] {
  const encontradas = [VOSEO, SEGUNDA_PERSONA, CONCURSO].flatMap((p) => texto.match(p) ?? []);
  return [...encontradas, ...(texto.replace(EXTRACCION_PERMITIDA, " ").match(EXTRACCION) ?? [])];
}

async function revisar(page: Page, ruta: string) {
  await page.goto(ruta);
  const texto = await page.locator("body").innerText();
  expect(prohibidas(texto), `${ruta}: ${prohibidas(texto).join(", ")}`).toEqual([]);
}

/** Enlace del primer elemento de una tabla o lista, para entrar a los detalles. */
async function primerDetalle(page: Page, ruta: string, selector: string): Promise<string | null> {
  await page.goto(ruta);
  const enlace = page.locator(selector).first();
  return (await enlace.count()) ? enlace.getAttribute("href") : null;
}

const PUBLICAS = ["/resultados/", "/estadisticas/", "/estadisticas/?numero=46", "/resultados/buscar/?numero=9999", "/ingresar/", "/registrarse/", "/resultados/99999/"];

test("visitante: pantallas públicas sin formas prohibidas", async ({ page }) => {
  for (const ruta of PUBLICAS) await revisar(page, ruta);
  const sorteo = await primerDetalle(page, "/resultados/", "[data-enlace-fila]");
  if (sorteo) await revisar(page, sorteo);
});

const PRIVADAS: Record<Perfil, string[]> = {
  usuaria: ["/mis-jugadas/", "/mis-jugadas/nueva/", "/administracion/concursos/"],
  sinjugadas: ["/mis-jugadas/"],
  admin: ["/administracion/concursos/", "/administracion/concursos/nuevo/", "/administracion/extracciones/", "/administracion/extracciones/?estado=con-error"],
  admin2: [],
};

for (const perfil of ["usuaria", "sinjugadas", "admin"] as Perfil[]) {
  test(`${perfil}: pantallas privadas sin formas prohibidas`, async ({ page }) => {
    await ingresarComo(page, perfil);
    for (const ruta of PRIVADAS[perfil]) await revisar(page, ruta);
    if (perfil === "usuaria") {
      const jugada = await primerDetalle(page, "/mis-jugadas/", "[data-enlace-fila]");
      if (jugada) {
        await revisar(page, jugada);
        await revisar(page, `${jugada}eliminar/`);
      }
    }
    if (perfil === "admin") {
      const sorteo = await primerDetalle(page, "/administracion/concursos/", "[data-enlace-fila]");
      if (sorteo) {
        await revisar(page, sorteo);
        await revisar(page, `${sorteo}historial/`);
        await revisar(page, `${sorteo}modificar/`);
      }
      const extraccion = await primerDetalle(page, "/administracion/extracciones/", "[data-enlace-fila]");
      if (extraccion) await revisar(page, extraccion);
    }
  });
}
