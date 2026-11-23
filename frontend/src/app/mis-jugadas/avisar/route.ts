/**
 * Aviso y vuelta al detalle de una jugada ([001] RN-08; [003] FR-043, R-31): como la vista HTML, si
 * la jugada ya no se puede modificar se avisa y se vuelve a su detalle. La página redirige aquí para
 * que el aviso no se agregue mientras se dibuja (la estructura común lo leería en la respuesta que se
 * descarta). Solo admite la clave `jugada.fija` y un identificador numérico.
 */
import type { NextRequest } from "next/server";

import { redireccionRelativa } from "@/lib/redireccion";

import { apiServidor } from "@/api/servidor";

export async function GET(pedido: NextRequest) {
  const parametros = pedido.nextUrl.searchParams;
  const id = Number(parametros.get("id"));
  if (parametros.get("clave") === "jugada.fija") {
    const api = await apiServidor();
    await api.POST("/api/v1/avisos/", {
      body: { tipo: "error", clave: "jugada.fija", valores: {} },
    });
  }
  const destino = Number.isInteger(id) && id > 0 ? `/mis-jugadas/${id}/` : "/mis-jugadas/";
  return redireccionRelativa(destino);
}
