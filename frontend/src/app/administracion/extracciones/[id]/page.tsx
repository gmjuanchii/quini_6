/**
 * Detalle de una extracción en Next.js ([002] AC-1.7 a AC-1.10; [003] AC-1.2, AC-1.5, AC-3.4,
 * FR-041): el mismo contenido que `templates/extracciones/extraccion.html`, con
 * `GET /api/v1/extracciones/{id}/`. Sin scripts, "Descargar CSV" y "Eliminar" son un enlace y un
 * formulario comunes (componentes.md § 4).
 */
import type { Metadata } from "next";
import Link from "next/link";

import { apiServidor } from "@/api/servidor";
import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { Icono } from "@/components/icono";
import { ProgressPanel } from "@/components/progress-panel";
import { StatusBadge } from "@/components/status-badge";
import { boton } from "@/components/ui/variantes";
import { fecha, fechaHora } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { verificarRespuesta } from "@/lib/sesion";
import { cn } from "@/lib/utils";

import { claseEstadoSorteo } from "../_componentes/estado-sorteo";

const BASE = "/administracion/extracciones/";

type Props = { params: Promise<{ id: string }> };

async function obtener(id: string) {
  const api = await apiServidor();
  const respuesta = await api.GET("/api/v1/extracciones/{id}/", {
    params: { path: { id: Number(id) || 0 } },
  });
  await verificarRespuesta(respuesta.response);
  if (!respuesta.data) throw new Error("La API de extracciones no respondió");
  return respuesta.data;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const api = await apiServidor();
  const { data } = await api.GET("/api/v1/extracciones/{id}/", {
    params: { path: { id: Number(id) || 0 } },
  });
  return {
    title: data
      ? msg("rot.extraccion_del", { fecha_hora: fechaHora(data.iniciada_en) })
      : msg("ext.titulo"),
  };
}

export default async function DetalleExtraccion({ params }: Props) {
  const { id } = await params;
  const e = await obtener(id);
  const r = e.resumen;
  const sinSorteos = e.etiqueta.valor === "sin_sorteos";
  const cobertura = r?.cobertura_desde;

  return (
    <>
      <BackLink href={BASE} texto={msg("nav.volver_extracciones")} />
      <h1>{msg("ext.titulo")}</h1>
      {/* [003] AC-1.5: la misma etiqueta que en el listado y, debajo, su explicación (RN-02). */}
      <div className="mt-2 flex flex-col gap-2">
        <div>
          <StatusBadge etiqueta={e.etiqueta} id="detalle" />
        </div>
        <p className="text-muted-foreground">{e.etiqueta.explicacion}</p>
      </div>
      {e.ninguna_fuente && (
        <Callout variante="danger" texto={msg("ext.ninguna_fuente")} className="mt-4" />
      )}

      {e.en_curso ? (
        <ProgressPanel
          id={e.id}
          inicial={e.avance}
          periodo={msg("rot.periodo_consultado_valor", {
            desde: fecha(e.desde),
            hasta: fecha(e.hasta),
          })}
        />
      ) : sinSorteos ? (
        <div
          className="rounded-card bg-surface px-6 py-8 text-center text-muted-foreground shadow-1"
          role="status"
        >
          <p>{msg("ext.sin_sorteos")}</p>
        </div>
      ) : (
        <>
          <Callout variante="info" rol="status">
            <p>
              <strong>{e.estado_texto}</strong>
            </p>
          </Callout>
          {cobertura && (
            <Callout
              variante="warning"
              texto={msg("ext.sin_cobertura", { fecha: fecha(cobertura) })}
            />
          )}
          {r && r.huecos.length > 0 && (
            <Callout variante="warning" texto={msg("ext.huecos", { lista: r.huecos.join(", ") })} />
          )}
          {e.url_csv && (
            <p>
              <a className={boton({ variante: "principal" })} href={e.url_csv}>
                {msg("ext.boton_descargar")}
              </a>
            </p>
          )}
          {r && (
            <>
              <h2>{msg("rot.resumen")}</h2>
              <table className="apilable">
                <caption className="visualmente-oculto">{msg("rot.caption_resumen")}</caption>
                <tbody>
                  <Fila
                    rotulo={msg("rot.periodo_consultado")}
                    valor={msg("rot.periodo_rango", {
                      desde: fecha(e.desde),
                      hasta: fecha(e.hasta),
                    })}
                  />
                  <Fila rotulo={msg("rot.sorteos_identificados")} valor={r.identificados} />
                  <Fila rotulo={msg("rot.recuperados")} valor={r.recuperados} />
                  <Fila rotulo={msg("rot.recuperados_parcialmente")} valor={r.parciales} />
                  <Fila rotulo={msg("sorteo.inconsistencias")} valor={r.inconsistencias} />
                  <Fila rotulo={msg("rot.no_recuperados")} valor={r.no_recuperados} />
                </tbody>
              </table>

              <h3>{msg("rot.fuentes_utilizadas")}</h3>
              <table className="apilable">
                <caption className="visualmente-oculto">{msg("rot.fuentes_utilizadas")}</caption>
                <thead>
                  <tr>
                    <th scope="col">{msg("rot.fuente")}</th>
                    <th scope="col">{msg("rot.sorteos_aportados")}</th>
                    <th scope="col">{msg("rot.intentos_fallidos")}</th>
                  </tr>
                </thead>
                <tbody>
                  {r.fuentes.map((f) => (
                    <tr key={f.fuente || f.nombre}>
                      <th scope="row" data-rotulo={msg("rot.fuente")}>
                        {f.nombre}
                        {f.requiere_mantenimiento && (
                          <span className="estado estado--revision">
                            {msg("ext.requiere_mantenimiento")}
                          </span>
                        )}
                      </th>
                      <td data-rotulo={msg("rot.sorteos_aportados")}>{f.aportados}</td>
                      <td data-rotulo={msg("rot.intentos_fallidos")}>
                        {f.fallidos.length > 0 ? (
                          <ul className="m-0 list-none divide-y divide-border p-0 [&>li]:py-3">
                            {f.fallidos.map((x) => (
                              <li key={x.texto}>
                                {x.texto}: {x.cantidad}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          0
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {r.a_revisar.length > 0 && (
                <>
                  <h3>{msg("rot.sorteos_a_revisar")}</h3>
                  <ul className="m-0 list-none divide-y divide-border p-0 [&>li]:py-3">
                    {r.a_revisar.map((s) => (
                      <li key={s.numero}>
                        <Link href={`${BASE}${e.id}/sorteos/${s.numero}/`}>
                          {msg("rot.sorteo_numero", { numero: s.numero })}
                        </Link>
                        {s.fecha && <> · {fecha(s.fecha)}</>} ·{" "}
                        <span className={cn("estado", claseEstadoSorteo(s.estado))}>
                          {s.estado_texto}
                        </span>
                        {s.motivos.length > 0 && (
                          <ul className="break-words">
                            {s.motivos.map((m) => (
                              <li key={m}>{m}</li>
                            ))}
                          </ul>
                        )}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </>
          )}
        </>
      )}

      {e.sorteos.length > 0 && (
        <>
          <h2>{msg("rot.sorteos")}</h2>
          {/* [003] HU-09: tabla apilable con los nombres de RN-05 y fila entera clicable. */}
          <div className="overflow-x-auto rounded-card border border-border bg-surface shadow-1 max-md:overflow-visible max-md:border-0 max-md:bg-transparent max-md:shadow-none">
            <table className="apilable">
              <caption className="visualmente-oculto">
                {msg("rot.caption_sorteos_extraccion")}
              </caption>
              <thead>
                <tr>
                  <th scope="col" className="px-3 py-2 text-left">
                    {msg("rot.sorteo")}
                  </th>
                  <th scope="col" className="px-3 py-2 text-left">
                    {msg("rot.fecha_del_sorteo")}
                  </th>
                  <th scope="col" className="px-3 py-2 text-left">
                    {msg("rot.estado")}
                  </th>
                </tr>
              </thead>
              <tbody>
                {e.sorteos.map((s) => (
                  <tr key={s.numero} className="fila-enlace">
                    <td data-rotulo={msg("rot.sorteo")} className="cifras whitespace-nowrap">
                      <Link
                        href={`${BASE}${e.id}/sorteos/${s.numero}/`}
                        data-enlace-fila=""
                        className="font-semibold text-primary"
                      >
                        {msg("rot.numero_sorteo", { numero: s.numero })}
                      </Link>
                    </td>
                    <td
                      data-rotulo={msg("rot.fecha_del_sorteo")}
                      className="cifras whitespace-nowrap"
                    >
                      {s.fecha ? fecha(s.fecha) : msg("intento.no_disponible")}
                    </td>
                    <td data-rotulo={msg("rot.estado")}>
                      <span className={cn("estado", claseEstadoSorteo(s.estado))}>
                        {s.estado_texto}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Sin scripts no hay menú ⋮: "Eliminar" también está aquí (componentes.md § 4). */}
      {e.eliminable && (
        <p className="solo-sin-scripts mt-6">
          <Link href={`${BASE}${e.id}/eliminar/`} className={boton({ variante: "destructivo" })}>
            <Icono nombre="trash-2" />
            <span>{msg("ext.eliminar")}</span>
          </Link>
        </p>
      )}
    </>
  );
}

function Fila({ rotulo, valor }: { rotulo: string; valor: string | number }) {
  return (
    <tr>
      <th scope="row">{rotulo}</th>
      <td>{valor}</td>
    </tr>
  );
}
