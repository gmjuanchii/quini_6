/**
 * Proxy de Next.js ([003] R-19, CHK006, CHK026, AC-14.1). **No decide permisos**: presenta, antes
 * de empezar a responder, lo que informa Django en `GET /api/v1/sesion/` (la autorización real es
 * siempre la respuesta de Django a cada operación de la API).
 *
 * - Rutas privadas sin cookie `sessionid`, o con una sesión que Django ya no reconoce →
 *   `/ingresar/?next=<ruta>` (la pantalla "Ingresar" de Django).
 * - `/administracion/*` con una cuenta que Django informa sin permisos de administración → la
 *   página "Sin permisos" con **403** y completa en el HTML. Se hace aquí y no con `forbidden()`
 *   en la página porque Next.js 16 responde esa interrupción con un armazón que solo se completa
 *   con scripts (incumpliría NFR-007); `forbidden()` queda como respaldo en `lib/sesion.ts`.
 * - Con sesión, o sin `csrftoken`, devuelve al navegador las `Set-Cookie` de Django: renueva la
 *   sesión como una página de Django (`SESSION_SAVE_EVERY_REQUEST`) y entrega `csrftoken` para los
 *   formularios POST.
 * - Rutas privadas con `Cache-Control: no-store` (NFR-008).
 * - Pasa a las páginas la ruta pedida en `x-quini6-ruta` (sección activa, `next` al ingresar).
 * - "Volver al formulario" ([003] AC-14.4, R-12): un POST común (no una Server Action) con el campo
 *   `pendiente` se verifica con Django (`POST /api/v1/formularios/pendiente/`) y la página recibe lo
 *   escrito en `x-quini6-reanudar`; se muestra precargada, sin enviar nada.
 * - Una Server Action (con o sin scripts) lleva `x-quini6-accion: 1` hasta la página, para que la
 *   sesión vencida se informe en el formulario y no con una redirección ([003] FR-032, NFR-007).
 */
import { NextResponse, type NextRequest } from "next/server";

import { cabeceraCookie, leerSetCookie } from "@/api/cookies";
import { CABECERA_REANUDAR, codificarCampos, type Campos } from "@/lib/reanudar";
import { CABECERA_ACCION } from "@/lib/sesion-cabeceras";

const API_INTERNA = (process.env.QUINI6_API_INTERNA ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const PRIVADAS = /^\/(mis-jugadas|administracion)(\/|$)/;
const ADMINISTRACION = /^\/administracion(\/|$)/;
const RUTA_SIN_PERMISOS = "/acceso/sin-permisos/";

type SesionDjango = { correo: string | null; es_administrador: boolean };

function irAIngresar(pedido: NextRequest, setCookies: string[] = []) {
  // En el proxy la URL del pedido es la pública (Host del enrutador) y la redirección debe ser
  // absoluta; en los manejadores de ruta, en cambio, se usa `redireccionRelativa`.
  const destino = new URL("/ingresar/", pedido.url);
  destino.searchParams.set("next", pedido.nextUrl.pathname + pedido.nextUrl.search);
  const respuesta = NextResponse.redirect(destino, 303);
  respuesta.headers.set("X-Interfaz", "next");
  for (const linea of setCookies) respuesta.headers.append("set-cookie", linea);
  return respuesta;
}

async function consultarSesion(pedido: NextRequest) {
  try {
    const respuesta = await fetch(`${API_INTERNA}/api/v1/sesion/`, {
      headers: { cookie: cabeceraCookie(pedido.cookies.getAll()) },
      cache: "no-store",
    });
    const sesion = respuesta.ok ? ((await respuesta.json()) as SesionDjango) : null;
    return { sesion, setCookies: respuesta.headers.getSetCookie() };
  } catch {
    return { sesion: null, setCookies: [] as string[] }; // Django no responde: la página mostrará el error
  }
}

const ORIGEN_PUBLICO = process.env.QUINI6_ORIGEN_PUBLICO ?? "";

/** Lo escrito de un formulario pendiente, verificado por Django; `null` si no corresponde. */
/** Los campos de un POST de formulario común (no una Server Action con scripts); `null` si no lo es. */
async function formularioComun(pedido: NextRequest): Promise<FormData | null> {
  const tipo = pedido.headers.get("content-type") ?? "";
  if (
    pedido.method !== "POST" ||
    pedido.headers.has("next-action") ||
    !/application\/x-www-form-urlencoded|multipart\/form-data/.test(tipo)
  ) {
    return null;
  }
  try {
    return await pedido.clone().formData();
  } catch {
    return null;
  }
}

/** Una Server Action: con scripts (cabecera `Next-Action`) o sin ellos (campos `$ACTION_…`). */
function esServerAction(pedido: NextRequest, datos: FormData | null): boolean {
  if (pedido.headers.has("next-action")) return true;
  return datos !== null && [...datos.keys()].some((k) => k.startsWith("$ACTION"));
}

async function leerPendiente(pedido: NextRequest, datos: FormData | null): Promise<Campos | null> {
  if (!datos || esServerAction(pedido, datos)) return null;
  const valor = datos.get("pendiente");
  const token = typeof valor === "string" ? valor : null;
  if (!token) return null;
  const csrf = pedido.cookies.get("csrftoken")?.value ?? "";
  const cabeceras: Record<string, string> = {
    cookie: cabeceraCookie(pedido.cookies.getAll()),
    "content-type": "application/json",
    "X-CSRFToken": csrf,
  };
  if (ORIGEN_PUBLICO) cabeceras.Origin = ORIGEN_PUBLICO;
  try {
    const respuesta = await fetch(`${API_INTERNA}/api/v1/formularios/pendiente/`, {
      method: "POST",
      headers: cabeceras,
      body: JSON.stringify({ pendiente: token, ruta: pedido.nextUrl.pathname }),
      cache: "no-store",
    });
    if (!respuesta.ok) return null;
    return ((await respuesta.json()) as { campos: Campos }).campos;
  } catch {
    return null;
  }
}

export async function proxy(pedido: NextRequest) {
  const ruta = pedido.nextUrl.pathname;
  const privada = PRIVADAS.test(ruta);
  const tieneSesion = pedido.cookies.has("sessionid");

  // Una Server Action sin sesión no se redirige: la operación de Django responde 401 con lo escrito
  // firmado (`pendiente`) y el formulario ofrece "Ingresar" sin perderlo ([003] FR-032, R-12).
  const datos = await formularioComun(pedido);
  const accion = esServerAction(pedido, datos);
  if (privada && !tieneSesion && !accion) return irAIngresar(pedido);

  const { sesion, setCookies } =
    tieneSesion || !pedido.cookies.has("csrftoken")
      ? await consultarSesion(pedido)
      : { sesion: null, setCookies: [] as string[] };

  if (privada && sesion && !sesion.correo && !accion) return irAIngresar(pedido, setCookies);

  // Las cookies nuevas también las ve esta misma solicitud (p. ej. el primer csrftoken).
  const cabeceras = new Headers(pedido.headers);
  cabeceras.set("x-quini6-ruta", ruta + pedido.nextUrl.search);
  const cookiesPedido = new Map(pedido.cookies.getAll().map((c) => [c.name, c.value]));
  for (const linea of setCookies) {
    const cookie = leerSetCookie(linea);
    if (!cookie) continue;
    if (cookie.maxAge === 0 || cookie.valor === "") cookiesPedido.delete(cookie.nombre);
    else cookiesPedido.set(cookie.nombre, cookie.valor);
  }
  cabeceras.set(
    "cookie",
    cabeceraCookie([...cookiesPedido].map(([name, value]) => ({ name, value }))),
  );

  // Sin scripts, Next.js dibuja la página después de ejecutar la acción: con la sesión vencida, la
  // página no debe redirigir a "Ingresar" (perdería lo escrito), sino mostrar el estado que devolvió
  // la acción ("La sesión venció…" con su `pendiente`). Nunca la cabecera que envíe el navegador.
  if (accion) cabeceras.set(CABECERA_ACCION, "1");
  else cabeceras.delete(CABECERA_ACCION);

  const reanudar = await leerPendiente(pedido, datos);
  if (reanudar) cabeceras.set(CABECERA_REANUDAR, codificarCampos(reanudar));
  else cabeceras.delete(CABECERA_REANUDAR); // nunca la que envíe el navegador

  const sinPermisos = ADMINISTRACION.test(ruta) && sesion?.correo && !sesion.es_administrador;
  const respuesta = sinPermisos
    ? NextResponse.rewrite(new URL(RUTA_SIN_PERMISOS, pedido.url), {
        status: 403,
        request: { headers: cabeceras },
      })
    : NextResponse.next({ request: { headers: cabeceras } });
  for (const linea of setCookies) respuesta.headers.append("set-cookie", linea);
  if (privada) respuesta.headers.set("Cache-Control", "no-store");
  return respuesta;
}

export const config = {
  matcher: ["/((?!_next/|api/|static/|favicon).*)"],
};
