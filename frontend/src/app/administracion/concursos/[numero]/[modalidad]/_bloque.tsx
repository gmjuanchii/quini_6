/**
 * Carga de números o premios de una modalidad ([001] AC-2.3 a AC-2.9, AC-2.13; [003] FR-041,
 * pantalla 6): el mismo contenido que `templates/resultados/admin/numeros.html` y `premios.html`,
 * con el formulario que describe `GET /api/v1/admin/sorteos/{numero}/{modalidad}/{bloque}/`. Si el
 * bloque ya está publicado, avisa y vuelve al panel, como la vista HTML.
 */
import { notFound, redirect } from "next/navigation";

import { llamarApi } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { BackLink } from "@/components/back-link";
import { msg } from "@/lib/mensajes";
import { rutaActual, verificarRespuesta } from "@/lib/sesion";

import { enviarAdmin } from "../../acciones";
import { API, BASE, tokenCsrf } from "../../_componentes/comunes";
import { FormularioDjango } from "../../_componentes/formulario-django";

type FormularioBloque = components["schemas"]["FormularioBloque"];

export async function PaginaBloque({
  numero,
  modalidad,
  bloque,
}: {
  numero: number;
  modalidad: string;
  bloque: "numeros" | "premios";
}) {
  const ruta = `${API}/${numero}/${modalidad}/${bloque}/`;
  const { response, datos } = await llamarApi("GET", ruta);
  if (response.status === 404) notFound();
  // Ya publicado: el aviso lo agrega `avisar/route.ts` (no mientras se dibuja la página).
  if (response.status === 409)
    redirect(`${BASE}/avisar/?clave=admin.bloque_publicado&numero=${numero}`);
  await verificarRespuesta(response);
  const f = datos as FormularioBloque;
  return (
    <>
      <BackLink href={`${BASE}/${numero}/`} texto={msg("rot.sorteo_numero", { numero })} />
      <h1>
        {msg(bloque === "numeros" ? "rot.adm_numeros_de" : "rot.adm_premios_de", {
          modalidad: f.modalidad.nombre,
        })}
      </h1>
      <p>
        {f.es_correccion ? (
          <>
            <span className="estado estado--corregido">
              {msg("rot.adm_correccion_preparacion")}
            </span>{" "}
            {msg("rot.adm_correccion_explicacion")}
          </>
        ) : (
          msg("rot.adm_borrador_explicacion")
        )}
      </p>
      {bloque === "premios" && <p>{msg("rot.adm_premios_explicacion")}</p>}
      <FormularioDjango
        accion={enviarAdmin.bind(null, { metodo: "PUT", ruta, exito: `${BASE}/${numero}/` })}
        formulario={f.formulario}
        boton={msg("rot.adm_guardar_borrador")}
        trabajando={msg("form.trabajando_guardar")}
        cancelar={`${BASE}/${numero}/`}
        csrf={await tokenCsrf()}
        siguiente={await rutaActual()}
        disposicion={bloque}
        className={bloque === "premios" ? "max-w-none" : undefined}
      />
    </>
  );
}
