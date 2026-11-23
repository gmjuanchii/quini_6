/**
 * [003] R-25 (P-01): Sentry en el navegador, solo si `NEXT_PUBLIC_QUINI6_SENTRY_DSN` tiene valor al
 * compilar (producción). Sin DSN no se carga nada (presupuesto de JavaScript, R-24).
 */
import { filtrarEvento, OPCIONES_SENTRY } from "@/lib/observabilidad";

const dsn = process.env.NEXT_PUBLIC_QUINI6_SENTRY_DSN;
if (dsn) {
  void import("@sentry/nextjs").then((Sentry) =>
    Sentry.init({ dsn, ...OPCIONES_SENTRY, beforeSend: (evento) => filtrarEvento(evento) }),
  );
}
