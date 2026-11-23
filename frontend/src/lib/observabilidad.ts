/**
 * Errores y métricas en Sentry ([003] R-25, P-01): la misma configuración que Django
 * (`quini6/observabilidad.py`). Se activa solo con `QUINI6_SENTRY_DSN` (servidor) o
 * `NEXT_PUBLIC_QUINI6_SENTRY_DSN` (navegador) con valor, es decir, solo en producción. Sin datos
 * personales, 10 % de las trazas, sin reproducción de sesiones y con el mismo filtro de eventos.
 */
const CORREO = /[\w.+-]+@[\w-]+(\.[\w-]+)+/g;
const OCULTO = "[filtrado]";
const CABECERAS_SENSIBLES = new Set([
  "cookie",
  "authorization",
  "x-csrftoken",
  "set-cookie",
  "idempotency-key",
]);

function sinCorreos<T>(valor: T): T {
  if (typeof valor === "string") return valor.replace(CORREO, OCULTO) as T;
  if (Array.isArray(valor)) return valor.map(sinCorreos) as T;
  if (valor && typeof valor === "object") {
    return Object.fromEntries(Object.entries(valor).map(([k, v]) => [k, sinCorreos(v)])) as T;
  }
  return valor;
}

type Evento = {
  request?: {
    cookies?: unknown;
    data?: unknown;
    query_string?: unknown;
    headers?: Record<string, string>;
  };
  user?: unknown;
  [clave: string]: unknown;
};

export function filtrarEvento<E extends object>(original: E): E {
  const evento = original as unknown as Evento;
  const pedido = evento.request;
  if (pedido) {
    delete pedido.cookies;
    delete pedido.data;
    delete pedido.query_string;
    if (pedido.headers) {
      pedido.headers = Object.fromEntries(
        Object.entries(pedido.headers).filter(([k]) => !CABECERAS_SENSIBLES.has(k.toLowerCase())),
      );
    }
  }
  delete evento.user;
  return sinCorreos(original);
}

export const OPCIONES_SENTRY = {
  sendDefaultPii: false,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,
} as const;
