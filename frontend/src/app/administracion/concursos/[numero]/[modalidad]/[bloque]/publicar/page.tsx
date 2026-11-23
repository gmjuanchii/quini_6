/**
 * Revisar y publicar un bloque en Next.js ([001] AC-2.5 a AC-2.12, RN-17, RN-22; [003] FR-041,
 * pantalla 6): el mismo contenido que `templates/resultados/admin/publicar.html`, con
 * `GET /api/v1/admin/sorteos/{numero}/{modalidad}/{bloque}/publicar/` (lo que impide publicar y lo
 * que exige confirmación). Publicar lo decide Django.
 */
import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";

import { llamarApi } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { dosDigitos, fecha, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { rutaActual, verificarRespuesta } from "@/lib/sesion";

import { enviarAdmin } from "../../../../acciones";
import { API, BASE, tokenCsrf } from "../../../../_componentes/comunes";
import { FormularioDjango } from "../../../../_componentes/formulario-django";

type Revision = components["schemas"]["RevisionPublicacion"];
type Props = { params: Promise<{ numero: string; modalidad: string; bloque: string }> };

export const metadata: Metadata = { title: msg("rot.adm_publicar") };

function importe(valor: string | null) {
  return valor === null ? msg("rot.adm_no_disponible") : pesos(valor);
}

export default async function Publicar({ params }: Props) {
  const { numero: n, modalidad, bloque } = await params;
  const numero = Number(n) || 0;
  const ruta = `${API}/${numero}/${modalidad}/${bloque}/publicar/`;
  const { response, datos } = await llamarApi("GET", ruta);
  if (response.status === 404) notFound();
  if (response.status === 422) redirect(`${BASE}/${numero}/`); // nada en Borrador u Observado
  await verificarRespuesta(response);
  const r = datos as Revision;
  const nombreBloque = (
    bloque === "numeros" ? msg("rot.numeros") : msg("rot.premios")
  ).toLowerCase();
  return (
    <>
      <BackLink href={`${BASE}/${numero}/`} texto={msg("rot.sorteo_numero", { numero })} />
      <h1>
        {msg("rot.adm_publicar_titulo", {
          accion: r.es_correccion ? msg("rot.adm_publicar_correccion") : msg("rot.adm_publicar"),
          bloque: nombreBloque,
          modalidad: r.modalidad.nombre,
        })}
      </h1>
      <section className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6">
        <h2>{msg("rot.adm_info_publicar")}</h2>
        {bloque === "numeros" ? (
          <ul className="numeros">
            {r.numeros.map((x) => (
              <li key={x} className="bolilla">
                {dosDigitos(x)}
              </li>
            ))}
          </ul>
        ) : (
          <>
            {r.sin_ganadores ? (
              <p>{msg("rot.adm_categoria_ganadora_sin")}</p>
            ) : r.aciertos_categoria_ganadora !== null &&
              r.aciertos_categoria_ganadora !== undefined ? (
              <p>{msg("rot.adm_categoria_ganadora", { n: r.aciertos_categoria_ganadora })}</p>
            ) : null}
            <table className="apilable">
              <thead>
                <tr>
                  <th scope="col">{msg("rot.adm_categoria")}</th>
                  <th scope="col">{msg("rot.ganadores")}</th>
                  <th scope="col">{msg("rot.adm_importe_destinado")}</th>
                  <th scope="col">{msg("rot.adm_importe_individual")}</th>
                  <th scope="col">{msg("rot.pozo_vacante")}</th>
                </tr>
              </thead>
              <tbody>
                {r.categorias.map((c) => (
                  <tr key={c.nombre}>
                    <th scope="row">{c.nombre}</th>
                    <td data-rotulo={msg("rot.ganadores")}>
                      {c.ganadores ?? msg("rot.adm_no_disponible")}
                    </td>
                    <td data-rotulo={msg("rot.adm_importe_destinado")}>
                      {importe(c.importe_categoria)}
                    </td>
                    <td data-rotulo={msg("rot.adm_importe_individual")}>
                      {importe(c.importe_individual)}
                    </td>
                    <td data-rotulo={msg("rot.pozo_vacante")}>
                      {importe(c.pozo_vacante_acumulado)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}
        <p className="text-sm text-muted-foreground">
          {r.fuente_fecha_consulta
            ? msg("rot.adm_fuente_consultada", {
                fuente: r.fuente_descripcion || msg("rot.adm_sin_registrar"),
                fecha: fecha(r.fuente_fecha_consulta),
              })
            : msg("rot.adm_fuente_publicar", {
                fuente: r.fuente_descripcion || msg("rot.adm_sin_registrar"),
              })}
        </p>
        {r.es_correccion && (
          <p className="text-sm text-muted-foreground">
            {msg("rot.adm_motivo_correccion_valor", { motivo: r.motivo_correccion })}
          </p>
        )}
      </section>
      {r.bloqueantes.length > 0 ? (
        <Callout variante="danger" titulo={msg("rot.adm_errores_publicar")}>
          <ul className="mb-0">
            {r.bloqueantes.map((b) => (
              <li key={b}>{b}</li>
            ))}
          </ul>
        </Callout>
      ) : (
        <Callout variante="success" texto={msg("rot.adm_sin_bloqueantes")} />
      )}
      <FormularioDjango
        accion={enviarAdmin.bind(null, { metodo: "POST", ruta, exito: `${BASE}/${numero}/` })}
        formulario={r.formulario}
        boton={r.es_correccion ? msg("rot.adm_publicar_correccion") : msg("rot.adm_publicar")}
        trabajando={msg("form.trabajando_publicar")}
        cancelar={`${BASE}/${numero}/`}
        csrf={await tokenCsrf()}
        siguiente={await rutaActual()}
        disposicion="publicar"
        advertencias={r.advertencias}
        ayudaFinal={r.bloqueantes.length > 0 ? msg("admin.corregir_bloqueantes") : undefined}
      />
    </>
  );
}
