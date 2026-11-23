// [003] R-23: pruebas unitarias y de componentes de Next.js.
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@contratos": fileURLToPath(new URL("../contratos", import.meta.url)),
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "jsdom",
    include: ["src/**/*.test.{ts,tsx}"],
    // Zona del proceso distinta de Buenos Aires: el formateo debe pasar la zona explícita (CHK008).
    env: { TZ: "UTC", __NEXT_TRAILING_SLASH: "true" }, // como next.config.ts (trailingSlash)
  },
});
