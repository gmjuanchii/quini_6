// [003] R-23: datos deterministas antes de cada corrida (manage.py preparar_e2e vacía la base E2E).
import { execFileSync } from "node:child_process";
import type { FullConfig } from "@playwright/test";

export default function preparacionGlobal(config: FullConfig) {
  if (process.env.E2E_SIN_PREPARAR) return;
  const { entornoDjango, python, raiz } = config.metadata as {
    entornoDjango: Record<string, string>;
    python: string;
    raiz: string;
  };
  const opciones = { cwd: raiz, env: { ...process.env, ...entornoDjango }, stdio: "inherit" as const };
  execFileSync(python, ["manage.py", "migrate", "-v", "0"], opciones);
  execFileSync(python, ["manage.py", "preparar_e2e"], opciones);
}
