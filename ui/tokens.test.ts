// [003] SC-009, NFR-002, contracts/tokens.md: contraste de los tokens en ambos temas.
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const css = readFileSync(new URL("./tokens.css", import.meta.url), "utf8");

function bloque(selector: string): Record<string, string> {
  const inicio = css.indexOf(selector);
  if (inicio < 0) throw new Error(`No se encontró el bloque ${selector}`);
  const apertura = css.indexOf("{", inicio);
  const cierre = css.indexOf("}", apertura);
  const valores: Record<string, string> = {};
  for (const [, nombre, valor] of css.slice(apertura + 1, cierre).matchAll(/--q-([a-z-]+):\s*([^;]+);/g)) {
    valores[nombre] = valor.trim();
  }
  return valores;
}

function luminancia(hex: string): number {
  const canales = [0, 2, 4].map((i) => parseInt(hex.slice(1 + i, 3 + i), 16) / 255);
  const [r, g, b] = canales.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function contraste(a: string, b: string): number {
  const [claro, oscuro] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return (claro + 0.05) / (oscuro + 0.05);
}

const TEXTO = 4.5;
const NO_TEXTO = 3;

/** [frente, fondo, mínimo] según contracts/tokens.md § 2. */
const PARES: [string, string, number][] = [
  ["foreground", "background", TEXTO],
  ["foreground", "surface", TEXTO],
  ["muted-foreground", "background", TEXTO],
  ["muted-foreground", "surface", TEXTO],
  ["primary", "surface", TEXTO],
  ["primary", "background", TEXTO],
  ["primary-foreground", "primary-solid", TEXTO],
  ["accent-text", "surface", TEXTO],
  ["accent-text", "background", TEXTO],
  ["success-text", "surface", TEXTO],
  ["danger-text", "surface", TEXTO],
  ["warning-text", "surface", TEXTO],
  ["destructive-foreground", "destructive", TEXTO],
  ["success-on-soft", "success-soft", TEXTO],
  ["warning-on-soft", "warning-soft", TEXTO],
  ["danger-on-soft", "danger-soft", TEXTO],
  ["info-on-soft", "info-soft", TEXTO],
  ["neutral-on-soft", "neutral-soft", TEXTO],
  ["accent-icon", "surface", NO_TEXTO],
  ["accent-icon", "background", NO_TEXTO],
  ["success-icon", "surface", NO_TEXTO],
  ["success-icon", "background", NO_TEXTO],
  ["danger-icon", "surface", NO_TEXTO],
  ["danger-icon", "background", NO_TEXTO],
  ["warning-icon", "surface", NO_TEXTO],
  ["warning-icon", "background", NO_TEXTO],
  ["border-input", "surface", NO_TEXTO],
  ["border-input", "background", NO_TEXTO],
  ["ring", "surface", NO_TEXTO],
  ["ring", "background", NO_TEXTO],
];

const TEMAS = {
  claro: bloque(":root {"),
  oscuro: bloque(':root[data-theme="oscuro"]'),
};

describe.each(Object.entries(TEMAS))("tema %s", (_tema, valores) => {
  it.each(PARES)("%s sobre %s alcanza %s:1", (frente, fondo, minimo) => {
    expect(valores[frente], `falta el token ${frente}`).toMatch(/^#[0-9a-f]{6}$/);
    expect(valores[fondo], `falta el token ${fondo}`).toMatch(/^#[0-9a-f]{6}$/);
    expect(contraste(valores[frente], valores[fondo])).toBeGreaterThanOrEqual(minimo);
  });
});

it("el tema oscuro del dispositivo es idéntico al tema oscuro elegido", () => {
  expect(bloque(':root:not([data-theme="claro"])')).toEqual(TEMAS.oscuro);
});

it("ambos temas definen los mismos tokens", () => {
  expect(Object.keys(TEMAS.oscuro).sort()).toEqual(Object.keys(TEMAS.claro).sort());
});
