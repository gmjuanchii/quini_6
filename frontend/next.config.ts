// [003] R-18, R-19, R-32: Next.js detrás del enrutador, en el mismo origen que Django.
import type { NextConfig } from "next";

const origen = process.env.QUINI6_ORIGEN_PUBLICO ?? "";
const anfitrionPublico = origen.replace(/^https?:\/\//, "").replace(/\/$/, "");

/** Mismas cabeceras de seguridad que Django (R-19, CHK037) y la marca de quién respondió (R-20). */
const cabeceras = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "same-origin" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Interfaz", value: "next" },
];

const nextConfig: NextConfig = {
  // Mismas direcciones que Django, que terminan en "/" (R-18): la conmutación no cambia enlaces.
  trailingSlash: true,
  output: "standalone",
  poweredByHeader: false,
  reactStrictMode: true,
  // `next dev` no genera AGENTS.md: las convenciones del proyecto viven en CLAUDE.md y specs/.
  agentRules: false,
  experimental: {
    // forbidden() → app/forbidden.tsx con 403, igual que Django ante una ruta sin permisos.
    authInterrupts: true,
    serverActions: {
      allowedOrigins: anfitrionPublico ? [anfitrionPublico] : [],
    },
    // CHK006: la caché del enrutador del cliente no reutiliza páginas dinámicas (privadas).
    staleTimes: { dynamic: 0 },
  },
  async headers() {
    return [{ source: "/:ruta*", headers: cabeceras }];
  },
};

export default nextConfig;
