// [003] R-06, R-07: copia a static/vendor/ las bibliotecas de interacción de la Etapa 1.
// Se sirven desde el propio sitio (sin CDN). static/vendor/ no se versiona.
import { copyFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const destino = join(raiz, "static", "vendor");
mkdirSync(destino, { recursive: true });

const archivos = [
  ["node_modules/htmx.org/dist/htmx.min.js", "htmx.min.js"],
  ["node_modules/alpinejs/dist/cdn.min.js", "alpine.min.js"],
  ["node_modules/@alpinejs/anchor/dist/cdn.min.js", "alpine-anchor.min.js"],
  ["node_modules/@alpinejs/focus/dist/cdn.min.js", "alpine-focus.min.js"],
  ["node_modules/cally/dist/cally.js", "cally.js"],
];

for (const [origen, nombre] of archivos) {
  const ruta = join(raiz, origen);
  if (!existsSync(ruta)) {
    console.error(`No se encontró ${origen}. Ejecutar "npm ci" antes de "npm run vendor".`);
    process.exit(1);
  }
  copyFileSync(ruta, join(destino, nombre));
  console.log(`static/vendor/${nombre}`);
}
