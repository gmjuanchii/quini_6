// [003] R-05: copia de lucide-static los iconos de la lista cerrada de contracts/componentes.md § 2
// a templates/ui/iconos/. Se ejecuta una vez ("npm run iconos") y los SVG se versionan.
import { copyFileSync, mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

export const ICONOS = [
  "loader-circle", "circle-check", "triangle-alert", "circle-dashed", "circle-x", "info",
  "menu", "x", "circle-user-round", "sun", "moon", "monitor", "ticket", "list-ordered",
  "calendar", "ellipsis-vertical", "trash-2", "download", "arrow-right", "arrow-left",
  "arrow-up", "arrow-down", "arrow-up-down", "eye", "eye-off", "wifi-off", "rotate-cw",
  "chart-column", "filter-x", "plus",
];

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const origen = join(raiz, "node_modules", "lucide-static", "icons");
const destino = join(raiz, "templates", "ui", "iconos");

/**
 * [003] R-24: el mismo contenido para Next.js, desde los SVG versionados de templates/ui/iconos/.
 * `Icono` los dibuja en línea como `{% icono %}` en Django (mismo marcado) y la biblioteca de Lucide
 * no viaja en el JavaScript de todas las pantallas. Solo esta parte: `node scripts/iconos.mjs --next`.
 */
function generarParaNext() {
  const cuerpos = ICONOS.map((nombre) => {
    const svg = readFileSync(join(destino, `${nombre}.svg`), "utf8").trim();
    const cuerpo = svg.replace(/^<svg[^>]*>/, "").replace(/<\/svg>$/, "");
    return `  ${JSON.stringify(nombre)}: ${JSON.stringify(cuerpo)},`;
  });
  const salida = join(raiz, "frontend", "src", "components", "iconos-svg.ts");
  writeFileSync(
    salida,
    [
      "// Generado por `node scripts/iconos.mjs --next` desde templates/ui/iconos/ (no editar a mano).",
      "// [003] R-05, R-24: contenido de los SVG de Lucide de la lista cerrada (contracts/componentes.md § 2).",
      "export const ICONOS_SVG = {",
      ...cuerpos,
      "} as const;",
      "",
      "export type NombreIcono = keyof typeof ICONOS_SVG;",
      "",
    ].join("\n"),
  );
  console.log(`${ICONOS.length} iconos en frontend/src/components/iconos-svg.ts`);
}

if (process.argv.includes("--next")) {
  generarParaNext();
  process.exit(0);
}

mkdirSync(destino, { recursive: true });

for (const nombre of ICONOS) {
  const ruta = join(origen, `${nombre}.svg`);
  if (!existsSync(ruta)) {
    console.error(`No existe el icono ${nombre} en lucide-static`);
    process.exit(1);
  }
  const svg = readFileSync(ruta, "utf8")
    .replace(/<!--[\s\S]*?-->\s*/g, "")
    .replace(/\s(width|height)="24"/g, "")
    .replace(/\sclass="[^"]*"/g, "")
    .replace(/\s+/g, " ")
    .replace(/>\s+</g, "><")
    .replace(/\s+\/>/g, "/>")
    .replace(/\s+>/g, ">")
    .trim();
  writeFileSync(join(destino, `${nombre}.svg`), svg + "\n");
}
copyFileSync(join(raiz, "node_modules", "lucide-static", "LICENSE"), join(destino, "LICENCIA-lucide.txt"));
console.log(`${ICONOS.length} iconos en templates/ui/iconos/`);
generarParaNext();
