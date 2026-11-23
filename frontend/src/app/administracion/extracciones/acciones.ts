"use server";

/**
 * Server Actions de la Extracción histórica ([003] FR-041, R-11, R-18): llaman a las operaciones de
 * `contracts/api.md` § Extracción histórica con `lib/acciones.ts` (Idempotency-Key, errores por
 * campo, sesión vencida, avisos). Django valida y autoriza todo.
 */
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import { ejecutarAccion, type EstadoFormulario, type Problema } from "@/lib/acciones";
import { msg } from "@/lib/mensajes";

const LISTADO = "/administracion/extracciones/";

function texto(datos: FormData, nombre: string): string {
  const valor = datos.get(nombre);
  return typeof valor === "string" ? valor : "";
}

/** [002] AC-1.1 a AC-1.6, AC-1.11; [003] RN-03, AC-3.5. Éxito → detalle de la extracción nueva. */
export async function iniciarExtraccion(
  _anterior: EstadoFormulario,
  datos: FormData,
): Promise<EstadoFormulario> {
  const estado = await ejecutarAccion(
    datos,
    (api, headers) =>
      api.POST("/api/v1/extracciones/", {
        body: { inicio: texto(datos, "inicio"), fin: texto(datos, "fin") },
        headers,
      }),
    // [003] AC-3.1, FR-004: con scripts, el avance aparece en el listado sin cambiar de pantalla;
    // sin scripts, el detalle de la extracción nueva (como Django).
    { destino: (creada) => (texto(datos, "_con_scripts") ? LISTADO : `${LISTADO}${creada.id}/`) },
  );
  // [002] AC-1.11: si ya tiene una en curso (409 con `ext.en_curso`), se muestra esa, como la
  // vista HTML.
  if (estado.existente && estado.general === msg("ext.en_curso")) redirect(estado.existente.url);
  return { ...estado, valores: { inicio: texto(datos, "inicio"), fin: texto(datos, "fin") } };
}

/** [002] AC-1.18, AC-1.19; [003] AC-2.5. El aviso `ext.eliminada` lo agrega Django (FR-043). */
export async function eliminarExtraccion(id: number, datos: FormData): Promise<void> {
  const api = await apiServidor();
  const clave = datos.get("clave_idempotencia");
  const headers: Record<string, string> =
    typeof clave === "string" && clave ? { "Idempotency-Key": clave } : {};
  const { response, error } = await api.DELETE("/api/v1/extracciones/{id}/", {
    params: { path: { id } },
    headers,
  });
  if (!response.ok && response.status !== 401) {
    // 404 ext.no_existe / 409 ext.eliminar_en_curso: como la vista HTML, aviso y vuelta al listado.
    const problema = (error ?? {}) as Problema;
    if (problema.detail) {
      await api.POST("/api/v1/avisos/", {
        body: {
          tipo: "error",
          clave: response.status === 404 ? "ext.no_existe" : "ext.eliminar_en_curso",
          valores: {},
        },
      });
    }
  }
  revalidatePath("/", "layout");
  redirect(response.status === 401 ? `/ingresar/?next=${encodeURIComponent(LISTADO)}` : LISTADO);
}
