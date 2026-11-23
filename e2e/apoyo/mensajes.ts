// [003] R-13: los guiones usan los textos del catálogo único (contratos/mensajes.json).
import { readFileSync } from "node:fs";

const MENSAJES: Record<string, string> = JSON.parse(
  readFileSync(new URL("../../contratos/mensajes.json", import.meta.url), "utf8"),
);

export function msg(clave: string, valores: Record<string, string | number> = {}): string {
  const texto = MENSAJES[clave];
  if (texto === undefined) throw new Error(`Clave inexistente en el catálogo: ${clave}`);
  return texto.replace(/\{([^}]+)\}/g, (_, nombre: string) => String(valores[nombre] ?? `{${nombre}}`));
}
