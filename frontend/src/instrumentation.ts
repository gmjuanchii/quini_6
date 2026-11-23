/**
 * [003] R-25 (P-01): Sentry en el servidor de Next.js, solo si `QUINI6_SENTRY_DSN` tiene valor.
 */
import { filtrarEvento, OPCIONES_SENTRY } from "@/lib/observabilidad";

export async function register() {
  const dsn = process.env.QUINI6_SENTRY_DSN;
  if (!dsn) return;
  const Sentry = await import("@sentry/nextjs");
  Sentry.init({
    dsn,
    environment: process.env.QUINI6_SENTRY_ENTORNO ?? "produccion",
    ...OPCIONES_SENTRY,
    beforeSend: (evento) => filtrarEvento(evento),
  });
}
