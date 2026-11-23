"use server";

/**
 * Server Actions de Mis jugadas ([003] FR-041, R-11, R-18): `POST`, `PUT` y `DELETE` de
 * `/api/v1/jugadas/` con `lib/acciones.ts`. Django valida, autoriza (solo las jugadas propias) y deja
 * el aviso en la sesión ("Jugada registrada", …), que se muestra en el destino (FR-043).
 */
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import { ejecutarAccion, type EstadoFormulario, type Problema } from "@/lib/acciones";

const LISTADO = "/mis-jugadas/";

function cuerpo(datos: FormData) {
  const numeros = datos.getAll("numeros").map(String);
  const escrito = String(datos.get("numero_escrito") ?? "").trim();
  // Como el formulario de Django: un número escrito sin agregar se suma a los elegidos.
  if (escrito) numeros.push(escrito);
  return {
    sorteo: String(datos.get("sorteo") ?? ""),
    numeros,
    costo: String(datos.get("costo") ?? ""),
    confirmar_duplicado: datos.get("confirmar_duplicado") === "1",
  };
}

function conValores(estado: EstadoFormulario, datos: FormData): EstadoFormulario {
  return {
    ...estado,
    valores: {
      sorteo: String(datos.get("sorteo") ?? ""),
      numeros: datos.getAll("numeros").map(String).join(","),
      costo: String(datos.get("costo") ?? ""),
    },
  };
}

/** [001] AC-4.1 a AC-4.9, RN-06. Éxito → "Mis jugadas". */
export async function registrarJugada(
  _anterior: EstadoFormulario,
  datos: FormData,
): Promise<EstadoFormulario> {
  const estado = await ejecutarAccion(
    datos,
    (api, headers) => api.POST("/api/v1/jugadas/", { body: cuerpo(datos), headers }),
    { destino: LISTADO },
  );
  return conValores(estado, datos);
}

/** [001] AC-4.10, RN-08. Éxito → "Mis jugadas"; jugada fija → su detalle con el aviso. */
export async function modificarJugada(
  id: number,
  _anterior: EstadoFormulario,
  datos: FormData,
): Promise<EstadoFormulario> {
  const estado = await ejecutarAccion(
    datos,
    (api, headers) =>
      api.PUT("/api/v1/jugadas/{id}/", { params: { path: { id } }, body: cuerpo(datos), headers }),
    { destino: LISTADO },
  );
  return conValores(estado, datos);
}

/** [001] AC-4.11, RN-08. */
export async function eliminarJugada(id: number, datos: FormData): Promise<void> {
  const api = await apiServidor();
  const clave = datos.get("clave_idempotencia");
  const headers: Record<string, string> =
    typeof clave === "string" && clave ? { "Idempotency-Key": clave } : {};
  const { response, error } = await api.DELETE("/api/v1/jugadas/{id}/", {
    params: { path: { id } },
    headers,
  });
  let destino = LISTADO;
  if (response.status === 409) {
    // Como la vista HTML: la jugada quedó fija; aviso y vuelta a su detalle.
    if ((error as Problema | undefined)?.detail) {
      await api.POST("/api/v1/avisos/", {
        body: { tipo: "error", clave: "jugada.fija", valores: {} },
      });
    }
    destino = `${LISTADO}${id}/`;
  } else if (response.status === 401) {
    destino = `/ingresar/?next=${encodeURIComponent(`${LISTADO}${id}/eliminar/`)}`;
  }
  revalidatePath("/", "layout");
  redirect(destino);
}
