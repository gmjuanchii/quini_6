/**
 * Sorteo extraído en Next.js ([002] AC-2.x; [003] FR-041): el mismo contenido que
 * `templates/extracciones/sorteo.html`, con `GET /api/v1/extracciones/{id}/sorteos/{numero}/`.
 * Cada dato con su estado explícito (`Dato` de [002]: un dato desconocido nunca se muestra como 0)
 * y su marca de cálculo cuando lo calculó el sistema.
 */
import type { Metadata } from "next";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { dosDigitos, fecha, fechaHora, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { verificarRespuesta } from "@/lib/sesion";
import { cn } from "@/lib/utils";

import { claseEstadoSorteo } from "../../../_componentes/estado-sorteo";

type Dato = components["schemas"]["Dato"];
type Consolidado = components["schemas"]["DatoConsolidado"];
type Diferencia = components["schemas"]["Diferencia"];

type Props = { params: Promise<{ id: string; numero: string }> };

/** Clases del resultado de cada fuente (`extracciones/consultas.py :: _CLASE_RESULTADO`). */
const CLASE_RESULTADO: Record<string, string> = {
  Obtenido: "estado--con-premio",
  "Fuera de cobertura": "estado--sin-premio",
  "No requerida": "estado--sin-premio",
  Incompleto: "estado--pendiente",
};

async function obtener(id: string, numero: string) {
  const api = await apiServidor();
  const [sorteo, extraccion] = await Promise.all([
    api.GET("/api/v1/extracciones/{id}/sorteos/{numero}/", {
      params: { path: { id: Number(id) || 0, numero: Number(numero) || 0 } },
    }),
    api.GET("/api/v1/extracciones/{id}/", { params: { path: { id: Number(id) || 0 } } }),
  ]);
  await verificarRespuesta(sorteo.response);
  if (!sorteo.data || !extraccion.data) throw new Error("La API de extracciones no respondió");
  return { s: sorteo.data, e: extraccion.data };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { numero } = await params;
  return { title: msg("rot.sorteo_numero", { numero }) };
}

/** `templates/extracciones/_dato.html`: el valor con el formato es-AR de su tipo. */
function ValorDato({ d }: { d: Dato }) {
  if (d.estado !== "valor") return <>{d.texto}</>;
  const v = d.valor;
  if (d.tipo === "importe" && typeof v === "string") return <>{pesos(v)}</>;
  if (d.tipo === "fecha" && typeof v === "string") return <>{fecha(v)}</>;
  if (d.tipo === "numeros" && Array.isArray(v))
    return <>{v.map((n) => dosDigitos(n)).join(", ")}</>;
  return <>{String(v)}</>;
}

function SinCorroborar({ d }: { d: Consolidado }) {
  return d.sin_corroborar ? (
    <span className="estado estado--pendiente">{msg("dato.sin_corroborar")}</span>
  ) : null;
}

function ListaDiferencia({ diferencia }: { diferencia: Diferencia }) {
  return (
    <ul>
      {diferencia.valores.map((v) => (
        <li key={v.fuente}>
          <ValorDato d={v.valor} /> ({v.fuente})
        </li>
      ))}
    </ul>
  );
}

function Discrepancia({
  titulo,
  diferencia,
}: {
  titulo: string;
  diferencia: Diferencia | null | undefined;
}) {
  if (!diferencia) return null;
  return (
    <Callout variante="danger">
      <p>
        <strong>{titulo}</strong>
      </p>
      <ListaDiferencia diferencia={diferencia} />
    </Callout>
  );
}

export default async function SorteoExtraido({ params }: Props) {
  const { id, numero } = await params;
  const { s, e } = await obtener(id, numero);

  return (
    <>
      <BackLink
        href={`/administracion/extracciones/${e.id}/`}
        texto={msg("nav.volver_extraccion", { fecha_hora: fechaHora(e.iniciada_en) })}
      />
      <h1>{msg("rot.sorteo_numero", { numero: s.numero })}</h1>
      <p>
        {msg("ext.col_fecha")}: <ValorDato d={s.fecha} /> <SinCorroborar d={s.fecha} />
      </p>
      <Discrepancia
        titulo={`${msg("ext.col_fecha")}: ${s.fecha.discrepancia?.tipo ?? ""}`}
        diferencia={s.fecha.discrepancia}
      />

      <p>
        <span className={cn("estado", claseEstadoSorteo(s.estado))}>{s.estado_texto}</span>
        {s.combina_fuentes && (
          <span className="estado estado--corregido">{msg("sorteo.combina")}</span>
        )}
        {s.sin_corroborar && (
          <span className="estado estado--pendiente">{msg("dato.sin_corroborar")}</span>
        )}
        {s.reglas_no_verificadas && (
          <span className="estado estado--pendiente">{msg("sorteo.reglas_no_verificadas")}</span>
        )}
      </p>
      {s.motivos.length > 0 && (
        <ul className="m-0 list-none divide-y divide-border p-0 [&>li]:py-3">
          {s.motivos.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      )}

      <h2>{msg("rot.fuentes_consultadas")}</h2>
      {s.fuentes.length > 0 && (
        <table className="apilable">
          <caption className="visualmente-oculto">{msg("rot.caption_fuentes_sorteo")}</caption>
          <thead>
            <tr>
              <th scope="col">{msg("rot.fuente")}</th>
              <th scope="col">{msg("rot.resultado")}</th>
              <th scope="col">{msg("rot.direccion_consultada")}</th>
              <th scope="col">{msg("rot.fecha_y_hora")}</th>
            </tr>
          </thead>
          <tbody>
            {s.fuentes.map((f) => (
              <tr key={f.nombre}>
                <th scope="row" data-rotulo={msg("rot.fuente")}>
                  {f.nombre}
                </th>
                <td data-rotulo={msg("rot.resultado")}>
                  <span
                    className={cn("estado", CLASE_RESULTADO[f.resultado] ?? "estado--revision")}
                  >
                    {f.resultado}
                  </span>
                  {f.observaciones.length > 0 && (
                    <ul className="m-0 list-none divide-y divide-border p-0 [&>li]:py-3">
                      {f.observaciones.map((o) => (
                        <li key={o}>{o}</li>
                      ))}
                    </ul>
                  )}
                </td>
                <td data-rotulo={msg("rot.direccion_consultada")}>
                  {f.url ? (
                    <a
                      className="break-all"
                      href={f.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {f.url}
                    </a>
                  ) : (
                    msg("dato.no_corresponde")
                  )}
                </td>
                <td data-rotulo={msg("rot.fecha_y_hora")}>
                  {f.consultado_en ? fechaHora(f.consultado_en) : msg("dato.no_corresponde")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {s.modalidades.map((m) => (
        <section
          key={m.nombre}
          className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
        >
          <h2>{m.nombre}</h2>
          {!m.informada ? (
            <Callout variante="warning" texto={msg("modalidad.no_informada")} />
          ) : (
            <>
              <p>
                {msg("rot.numeros")}: <ValorDato d={m.numeros} />
                {m.numeros.calculo && (
                  <span className="ayuda">
                    {" "}
                    ({msg("rot.calculado", { calculo: m.numeros.calculo })})
                  </span>
                )}
                <SinCorroborar d={m.numeros} />
              </p>
              <Discrepancia
                titulo={`${msg("rot.numeros")}: ${m.numeros.discrepancia?.tipo ?? ""}`}
                diferencia={m.numeros.discrepancia}
              />
              {m.categorias.map((c) => (
                <table key={c.nombre} className="apilable">
                  <caption>
                    {c.nombre} · {c.estado_pozo}
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">{msg("rot.dato")}</th>
                      <th scope="col">{msg("rot.valor")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {c.datos.map((d) => (
                      <tr key={d.rotulo}>
                        <th scope="row" data-rotulo={msg("rot.dato")}>
                          {d.rotulo}
                        </th>
                        <td data-rotulo={msg("rot.valor")}>
                          <ValorDato d={d} /> <SinCorroborar d={d} />
                          <Discrepancia
                            titulo={d.discrepancia?.tipo ?? ""}
                            diferencia={d.discrepancia}
                          />
                          {d.diferencia_tolerada && (
                            <Callout variante="info" texto={d.diferencia_tolerada.tipo}>
                              <ListaDiferencia diferencia={d.diferencia_tolerada} />
                            </Callout>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ))}
            </>
          )}
        </section>
      ))}

      {s.observaciones.length > 0 && (
        <>
          <h2>{msg("rot.observaciones")}</h2>
          <ul className="m-0 list-none divide-y divide-border p-0 [&>li]:py-3">
            {s.observaciones.map((o, i) => (
              <li key={i}>
                {o.fuente && <>{o.fuente}: </>}
                {o.texto}
              </li>
            ))}
          </ul>
        </>
      )}
    </>
  );
}
