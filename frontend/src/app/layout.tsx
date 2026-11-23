/**
 * Estructura común de Next.js ([003] HU-14, AC-14.1, FR-039, R-14, R-18): el mismo encabezado,
 * avisos, pie y tema que `templates/base.html`, con la sesión que informa Django.
 *
 * Todas las páginas son dinámicas: dependen de la cookie de la persona (sesión, tema) y nunca se
 * guardan en caché (NFR-008, CHK006).
 */
import type { Metadata, Viewport } from "next";
import { cookies } from "next/headers";
import { Suspense, type ReactNode } from "react";

import { Toaster } from "@/components/toaster";
import { msg } from "@/lib/mensajes";
import { obtenerSesion, rutaActual } from "@/lib/sesion";
import { COOKIE_TEMA, temaDe } from "@/lib/tema";

import { Avisos, leerAvisos } from "./_componentes/avisos";
import { AvisosAlNavegar } from "./_componentes/avisos-al-navegar";
import { NavBar } from "./_componentes/nav-bar";
import { Pie } from "./_componentes/pie";
import { SkipLink } from "./_componentes/skip-link";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: { default: "QUINI_6", template: "%s · QUINI_6" },
  icons: { icon: { url: "/static/marca/favicon.svg", type: "image/svg+xml" } },
};

export const viewport: Viewport = { width: "device-width", initialScale: 1 };

export default async function Layout({ children }: { children: ReactNode }) {
  const tema = temaDe((await cookies()).get(COOKIE_TEMA)?.value);
  const [sesion, avisos, ruta] = await Promise.all([obtenerSesion(), leerAvisos(), rutaActual()]);

  return (
    <html
      lang="es-AR"
      data-theme={tema === "dispositivo" ? undefined : tema}
      suppressHydrationWarning
    >
      <head>
        {/* Con scripts, los menús empiezan cerrados sin saltos (sin scripts, todo visible). */}
        <script
          dangerouslySetInnerHTML={{ __html: 'document.documentElement.classList.add("js");' }}
        />
      </head>
      <body>
        <SkipLink />
        <NavBar sesion={sesion} ruta={ruta} />
        <main id="contenido" className="contenedor principal" tabIndex={-1}>
          <Avisos avisos={avisos} />
          {children}
        </main>
        <Pie tema={tema} ruta={ruta} />
        <Toaster etiquetaRegion={msg("aviso.region")} />
        <Suspense fallback={null}>
          <AvisosAlNavegar />
        </Suspense>
      </body>
    </html>
  );
}
