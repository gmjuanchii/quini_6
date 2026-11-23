// [003] R-24: mide con Lighthouse CI las pantallas de la línea base (públicas y privadas).
// Requiere Django corriendo con los datos de preparar_e2e (por ejemplo, la base E2E en el puerto 8001).
// Uso: node scripts/lhci.mjs [--base http://127.0.0.1:8001] [--ingreso http://127.0.0.1:8001]
// Detrás del enrutador (Etapa 2), /ingresar/ lo atiende Next.js: --ingreso indica el Django directo
// donde se obtiene la sesión, que sirve igual en el enrutador porque es la misma sesión de Django (R-19).
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "@playwright/test";

const argumento = (nombre, porDefecto) =>
  process.argv.includes(nombre) ? process.argv[process.argv.indexOf(nombre) + 1] : porDefecto;
const base = argumento("--base", "http://127.0.0.1:8001");
const ingreso = argumento("--ingreso", base);
const rutas = ["/resultados/", "/estadisticas/", "/mis-jugadas/", "/administracion/extracciones/"];

function cookies(respuesta) {
  return Object.fromEntries(
    (respuesta.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0].split("=")).map(([k, ...v]) => [k, v.join("=")]),
  );
}

async function sesion() {
  const { correo, contrasena } = JSON.parse(readFileSync("e2e/.credenciales.json", "utf8")).admin;
  const pagina = await fetch(`${ingreso}/ingresar/`);
  const csrf = cookies(pagina).csrftoken;
  const token = (await pagina.text()).match(/name="csrfmiddlewaretoken" value="([^"]+)"/)[1];
  const respuesta = await fetch(`${ingreso}/ingresar/`, {
    method: "POST",
    redirect: "manual",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Cookie: `csrftoken=${csrf}`, Referer: `${ingreso}/ingresar/` },
    body: new URLSearchParams({ csrfmiddlewaretoken: token, email: correo, password: contrasena }),
  });
  const sessionid = cookies(respuesta).sessionid;
  if (!sessionid) throw new Error("No se pudo ingresar con la cuenta de administración de preparar_e2e");
  return `sessionid=${sessionid}; csrftoken=${csrf}`;
}

const cookie = await sesion();
const salida = ".lighthouseci";
mkdirSync(salida, { recursive: true });
// La cookie y las URL van en un archivo de configuración generado (no versionado), así no
// dependen de las comillas de la consola en Windows.
const configuracion = JSON.parse(readFileSync("lighthouserc.json", "utf8"));
configuracion.ci.collect.url = rutas.map((r) => `${base}${r}`);
configuracion.ci.collect.chromePath = chromium.executablePath();
configuracion.ci.collect.settings.extraHeaders = { Cookie: cookie };
const generado = join(salida, "lighthouserc.generado.json");
writeFileSync(generado, JSON.stringify(configuracion, null, 2));
for (const archivo of readdirSync(salida).filter((f) => f.startsWith("lhr-"))) rmSync(join(salida, archivo));
execFileSync(process.platform === "win32" ? "npx.cmd" : "npx", ["lhci", "collect", `--config=${generado}`], {
  stdio: "inherit",
  shell: process.platform === "win32",
});

// Resumen: mediana por URL de LCP, CLS, TBT (indicador de laboratorio de la interactividad) y JS.
const porUrl = {};
for (const archivo of readdirSync(salida).filter((f) => f.startsWith("lhr-") && f.endsWith(".json"))) {
  const lhr = JSON.parse(readFileSync(join(salida, archivo), "utf8"));
  const ruta = new URL(lhr.finalDisplayedUrl ?? lhr.finalUrl).pathname;
  const js = lhr.audits["resource-summary"]?.details?.items?.find((i) => i.resourceType === "script")?.transferSize ?? 0;
  (porUrl[ruta] ??= []).push({
    lcp: lhr.audits["largest-contentful-paint"].numericValue,
    cls: lhr.audits["cumulative-layout-shift"].numericValue,
    tbt: lhr.audits["total-blocking-time"].numericValue,
    js,
  });
}
const mediana = (v) => [...v].sort((a, b) => a - b)[Math.floor(v.length / 2)];
const filas = Object.entries(porUrl).map(([ruta, corridas]) => ({
  ruta,
  lcp: Math.round(mediana(corridas.map((c) => c.lcp))),
  cls: mediana(corridas.map((c) => c.cls)).toFixed(3),
  tbt: Math.round(mediana(corridas.map((c) => c.tbt))),
  js: (mediana(corridas.map((c) => c.js)) / 1024).toFixed(1),
  corridas: corridas.length,
}));
writeFileSync(join(salida, "resumen.json"), JSON.stringify(filas, null, 2));
console.table(filas);
