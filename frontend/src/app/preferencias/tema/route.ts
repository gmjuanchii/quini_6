/**
 * Preferencia de tema en Next.js ([003] HU-12, FR-036, R-14, pantalla 5): la misma validación de
 * `next` y la misma cookie que `quini6/tema.py` (POST, funciona sin scripts; 303 a la página).
 */
import type { NextRequest } from "next/server";

import { redireccionRelativa } from "@/lib/redireccion";

import { COOKIE_TEMA } from "@/lib/tema";

const TEMAS = ["claro", "oscuro"];
const DURACION = 400 * 24 * 60 * 60; // 400 días (data-model § 4)

function destino(valor: FormDataEntryValue | null): string {
  const texto = typeof valor === "string" ? valor : "";
  return texto.startsWith("/") && !texto.startsWith("//") ? texto : "/";
}

export async function POST(pedido: NextRequest) {
  const datos = await pedido.formData();
  const respuesta = redireccionRelativa(destino(datos.get("next")));
  const elegido = String(datos.get("tema") ?? "");
  if (TEMAS.includes(elegido)) {
    respuesta.cookies.set({
      name: COOKIE_TEMA,
      value: elegido,
      maxAge: DURACION,
      path: "/",
      sameSite: "lax",
      httpOnly: false, // el selector la cambia sin recargar (R-14)
      secure: pedido.nextUrl.protocol === "https:",
    });
  } else if (elegido === "dispositivo") {
    respuesta.cookies.delete({ name: COOKIE_TEMA, path: "/" });
  }
  return respuesta;
}
