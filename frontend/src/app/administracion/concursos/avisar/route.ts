/**
 * Aviso y vuelta al panel de un sorteo ([001] US2; [003] FR-043, R-31): como la vista HTML, si el
 * bloque ya está publicado se avisa y se vuelve al panel. La página redirige aquí para que el aviso no
 * se agregue mientras se dibuja. Solo admite la clave `admin.bloque_publicado` y un número.
 */
import type { NextRequest } from "next/server";

import { redireccionRelativa } from "@/lib/redireccion";

import { apiServidor } from "@/api/servidor";

export async function GET(pedido: NextRequest) {
  const parametros = pedido.nextUrl.searchParams;
  const numero = Number(parametros.get("numero"));
  if (parametros.get("clave") === "admin.bloque_publicado") {
    const api = await apiServidor();
    await api.POST("/api/v1/avisos/", {
      body: { tipo: "error", clave: "admin.bloque_publicado", valores: {} },
    });
  }
  const destino =
    Number.isInteger(numero) && numero > 0
      ? `/administracion/concursos/${numero}/`
      : "/administracion/concursos/";
  return redireccionRelativa(destino);
}
