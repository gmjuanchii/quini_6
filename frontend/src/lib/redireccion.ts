/**
 * Redirección 303 con una dirección **relativa** ([003] R-20): detrás del enrutador, la URL que ve un
 * manejador de ruta de Next.js es la interna (`http://localhost:3000/…`); una `Location` absoluta
 * llevaría al navegador fuera del sitio público. Las rutas del sitio siempre empiezan con `/`.
 */
import { NextResponse } from "next/server";

export function redireccionRelativa(destino: string, estado = 303): NextResponse {
  const ruta = destino.startsWith("/") && !destino.startsWith("//") ? destino : "/";
  return new NextResponse(null, {
    status: estado,
    // Quién respondió (diagnóstico del enrutador, R-20): `next.config.ts` no la agrega aquí.
    headers: { Location: ruta, "Cache-Control": "no-store", "X-Interfaz": "next" },
  });
}
