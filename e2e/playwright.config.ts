// [003] R-23: recorridos de punta a punta. El mismo guion corre contra Django (Etapa 1) y, detrás
// del enrutador, contra Next.js (Etapas 2 y 3): E2E_BASE_URL elige el destino.
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig, devices } from "@playwright/test";

const raiz = resolve(dirname(fileURLToPath(import.meta.url)), "..");

const baseURL = process.env.E2E_BASE_URL ?? "http://127.0.0.1:8001";
const python =
  process.env.E2E_PYTHON ??
  (process.platform === "win32" ? resolve(raiz, ".venv", "Scripts", "python.exe") : "python");
const entornoDjango = {
  QUINI6_DEBUG: "1",
  QUINI6_E2E: "1",
  QUINI6_DB_SQLITE: process.env.QUINI6_DB_SQLITE ?? "e2e.sqlite3",
};

export default defineConfig({
  testDir: "./recorridos",
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : [["list"]],
  globalSetup: "./apoyo/preparacion-global.ts",
  use: {
    baseURL,
    locale: "es-AR",
    timezoneId: "America/Argentina/Buenos_Aires",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "escritorio", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    { name: "movil", use: { ...devices["Desktop Chrome"], viewport: { width: 360, height: 740 }, isMobile: false } },
    { name: "sin-scripts", use: { ...devices["Desktop Chrome"], javaScriptEnabled: false } },
    { name: "oscuro", use: { ...devices["Desktop Chrome"], colorScheme: "dark" } },
    { name: "movimiento-reducido", use: { ...devices["Desktop Chrome"], reducedMotion: "reduce" } },
  ],
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: `"${python}" manage.py runserver 127.0.0.1:8001 --noreload`,
        cwd: raiz,
        url: "http://127.0.0.1:8001/resultados/",
        reuseExistingServer: !process.env.CI,
        env: entornoDjango,
        timeout: 120_000,
      },
  metadata: { entornoDjango, python, raiz },
});
