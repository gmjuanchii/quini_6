/**
 * Confirmación de eliminación de una extracción ([002] AC-1.18; [003] AC-2.3 a AC-2.6, FR-008,
 * FR-009): el mismo contenido que `templates/extracciones/_eliminar_contenido.html`. Lo usan la
 * página aparte (sin scripts) y el diálogo de la ruta interceptada (con scripts). "Cancelar" tiene
 * el foco inicial; "Eliminar" tiene estilo destructivo. Sin "Deshacer" (D-03).
 */
import { redirect } from "next/navigation";
import Link from "next/link";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { BotonEnviar } from "@/components/boton-enviar";
import { Callout } from "@/components/callout";
import { boton } from "@/components/ui/variantes";
import { nuevaClaveIdempotencia } from "@/lib/acciones";
import { fecha, fechaHora } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { verificarRespuesta } from "@/lib/sesion";

import { eliminarExtraccion } from "../acciones";

export const LISTADO = "/administracion/extracciones/";

type Extraccion = components["schemas"]["Extraccion"];

/** La extracción a eliminar; si ya no existe o sigue en curso, avisa y vuelve al listado (como
 * la vista HTML de Django). */
export async function extraccionAEliminar(id: string): Promise<Extraccion> {
  const api = await apiServidor();
  const { data, response } = await api.GET("/api/v1/extracciones/{id}/", {
    params: { path: { id: Number(id) || 0 } },
  });
  // El aviso lo agrega `avisar/route.ts` (no mientras se dibuja la página, FR-043).
  if (response.status === 404) redirect(`${LISTADO}avisar/?clave=ext.no_existe`);
  await verificarRespuesta(response);
  if (!data) throw new Error("La API de extracciones no respondió");
  if (!data.eliminable) redirect(`${LISTADO}avisar/?clave=ext.eliminar_en_curso`);
  return data;
}

export function textoConfirmar(e: Extraccion): string {
  return msg("ext.eliminar_confirmar", {
    fecha_hora: fechaHora(e.iniciada_en),
    desde: fecha(e.desde),
    hasta: fecha(e.hasta),
  });
}

/** Detalle, consecuencias y el formulario (sin el título ni el texto, que pone cada contenedor). */
export function CuerpoEliminar({ e }: { e: Extraccion }) {
  const accion = eliminarExtraccion.bind(null, e.id);
  return (
    <>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        <dt className="text-muted-foreground">{msg("ext.col_fecha")}</dt>
        <dd>{fechaHora(e.iniciada_en)}</dd>
        <dt className="text-muted-foreground">{msg("rot.ejecutada_por")}</dt>
        <dd className="truncate" title={e.creada_por}>
          {e.creada_por}
        </dd>
        <dt className="text-muted-foreground">{msg("rot.periodo_consultado")}</dt>
        <dd>{msg("rot.periodo_rango", { desde: fecha(e.desde), hasta: fecha(e.hasta) })}</dd>
      </dl>
      <Callout variante="warning" texto={msg("ext.eliminar_consecuencias")} />
      <form
        action={accion}
        className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end"
        noValidate
      >
        <input type="hidden" name="clave_idempotencia" value={nuevaClaveIdempotencia()} />
        <Link
          href={LISTADO}
          data-cancelar=""
          autoFocus
          className={boton({ variante: "secundario" })}
        >
          {msg("ext.cancelar")}
        </Link>
        <BotonEnviar
          variante="destructivo"
          icono="trash-2"
          textoTrabajando={msg("form.trabajando_eliminar")}
        >
          {msg("ext.eliminar")}
        </BotonEnviar>
      </form>
    </>
  );
}
