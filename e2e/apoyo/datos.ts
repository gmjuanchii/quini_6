// [003] R-23, T097: vuelve a preparar la base E2E desde un guion (por ejemplo, vacía para HU-08).
import { execFileSync } from "node:child_process";
import type { FullConfig } from "@playwright/test";

export function prepararDatos(config: FullConfig, opciones: { vacio?: boolean } = {}) {
  const { entornoDjango, python, raiz } = config.metadata as {
    entornoDjango: Record<string, string>;
    python: string;
    raiz: string;
  };
  const argumentos = ["manage.py", "preparar_e2e", ...(opciones.vacio ? ["--vacio"] : [])];
  execFileSync(python, argumentos, { cwd: raiz, env: { ...process.env, ...entornoDjango }, stdio: "ignore" });
}
