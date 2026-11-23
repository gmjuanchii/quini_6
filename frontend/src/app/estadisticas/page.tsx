/**
 * Estadísticas de frecuencia en Next.js ([001] US6; [003] HU-07, FR-041, R-27, pantalla 2): el mismo
 * contenido que `templates/estadisticas/index.html`, con `GET /api/v1/estadisticas/` y los atajos de
 * `GET /api/v1/periodos/atajos/?formulario=estadisticas`. Componente de servidor (pantalla pública):
 * el gráfico es SVG del servidor y la tabla se ordena con enlaces (funciona sin scripts).
 *
 * Con un error, Django responde 422 con los errores por campo y la consulta anterior, que se sigue
 * mostrando ([001] AC-6.8).
 */
import type { Metadata } from "next";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { Callout } from "@/components/callout";
import { EmptyState } from "@/components/empty-state";
import { FrequencyChart } from "@/components/frequency-chart";
import { dosDigitos, fecha, porcentaje } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { conParametros, encabezados, type Parametros } from "@/lib/tablas";
import { cn } from "@/lib/utils";
import { EncabezadoOrdenable } from "@/components/data-table";

import { FormularioEstadisticas } from "./_componentes/formulario-estadisticas";

export const metadata: Metadata = { title: msg("rot.est_titulo") };

type Frecuencias = components["schemas"]["FrecuenciasDTO"];
type Problema = {
  detail?: string;
  errores?: { campo: string; mensaje: string }[];
  resultado?: Frecuencias;
};

const CAMPOS = [
  "modalidad",
  "desde",
  "hasta",
  "numero",
  "anterior_modalidad",
  "anterior_desde",
  "anterior_hasta",
  "anterior_numero",
] as const;

function uno(valor: string | string[] | undefined): string {
  return (Array.isArray(valor) ? valor[0] : valor) ?? "";
}

/** `AAAA-MM-DD` → `dd/mm/aaaa`, como los valores que muestra el formulario de Django. */
function dma(iso: string | null | undefined): string {
  return iso ? fecha(iso) : "";
}

/** [003] AC-7.5: orden de la tabla (solo presentación); empates por número ascendente. */
function ordenar(numeros: Frecuencias["numeros"], orden: string) {
  const filas = [...numeros];
  if (orden.replace(/^-/, "") === "frecuencia") {
    filas.sort((a, b) => a.numero - b.numero);
    filas.sort((a, b) =>
      orden.startsWith("-") ? b.frecuencia - a.frecuencia : a.frecuencia - b.frecuencia,
    );
  } else {
    filas.sort((a, b) => (orden.startsWith("-") ? b.numero - a.numero : a.numero - b.numero));
  }
  return filas;
}

function ordenValido(valor: string): string {
  return ["numero", "-numero", "frecuencia", "-frecuencia"].includes(valor) ? valor : "numero";
}

export default async function Estadisticas({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const api = await apiServidor();
  const atajos = await api.GET("/api/v1/periodos/atajos/", {
    params: { query: { formulario: "estadisticas" } },
  });
  const listaAtajos = atajos.data ?? [];

  // [003] AC-4.4: `?atajo=<clave>` (sin scripts) precarga el período y lo consulta.
  const consulta: Record<string, string> = Object.fromEntries(CAMPOS.map((c) => [c, uno(sp[c])]));
  const atajo = listaAtajos.find((a) => a.clave === uno(sp.atajo));
  if (atajo && !consulta.desde && !consulta.hasta) {
    consulta.desde = fecha(atajo.desde);
    consulta.hasta = fecha(atajo.hasta);
  }

  const { data, error } = await api.GET("/api/v1/estadisticas/", { params: { query: consulta } });
  const problema = (error ?? {}) as Problema;
  const resultado = data ?? problema.resultado;
  if (!resultado) throw new Error("La API de estadísticas no respondió");
  const errores = Object.fromEntries((problema.errores ?? []).map((e) => [e.campo, e.mensaje]));

  const c = resultado.consulta;
  const valores = {
    desde: dma(c.desde),
    hasta: dma(c.hasta),
    numero: c.numero !== null && c.numero !== undefined ? dosDigitos(c.numero) : "",
  };
  const orden = ordenValido(uno(sp.orden));
  const ocultos: Record<string, string> = {
    anterior_modalidad: c.modalidad,
    anterior_desde: valores.desde,
    anterior_hasta: valores.hasta,
    anterior_numero: valores.numero,
    orden,
  };
  // Enlaces de orden: la consulta mostrada (válida), nunca la entrada con errores.
  const parametros: Parametros = { modalidad: c.modalidad, ...valores };
  const hrefAtajo = Object.fromEntries(
    listaAtajos.map((a) => [
      a.clave,
      conParametros({ modalidad: c.modalidad }, { atajo: a.clave }),
    ]),
  );
  const hayDatos = resultado.cantidad_sorteos > 0;
  const n = resultado.cantidad_sorteos;
  const consultado = resultado.numero_consultado;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="m-0 text-3xl font-semibold">{msg("rot.est_titulo")}</h1>
      <Callout variante="info" texto={msg("est.leyenda")} id="est-leyenda" />
      {problema.detail && <Callout variante="danger" rol="alert" texto={problema.detail} />}
      {resultado.avisos.map((a) => (
        <Callout key={a} variante="warning" texto={a} />
      ))}

      <FormularioEstadisticas
        modalidades={resultado.modalidades}
        modalidad={c.modalidad}
        desde={valores.desde}
        hasta={valores.hasta}
        numero={errores.numero ? (consulta.numero ?? "") : valores.numero}
        errores={errores}
        atajos={listaAtajos}
        hrefAtajo={hrefAtajo}
        ocultos={ocultos}
      />

      {resultado.sorteos_sin_informacion > 0 && (
        <Callout
          variante="warning"
          texto={msg("est.huecos", { n: resultado.sorteos_sin_informacion })}
        />
      )}

      {hayDatos ? (
        <>
          <section className="flex flex-col gap-2" aria-labelledby="titulo-resumen">
            <h2 id="titulo-resumen" className="m-0 text-xl font-semibold">
              {c.modalidad_nombre}
            </h2>
            <p className="m-0">
              {msg(n === 1 ? "rot.est_considerados_uno" : "rot.est_considerados", {
                n,
                desde: dma(resultado.primera_fecha),
                hasta: dma(resultado.ultima_fecha),
              })}
            </p>
            {consultado && (
              <p
                className="m-0 rounded-card border-l-4 border-accent bg-surface p-4 font-medium shadow-1"
                id="numero-consultado"
              >
                {msg("rot.est_numero_consultado", {
                  numero: dosDigitos(consultado.numero),
                  frecuencia: consultado.frecuencia,
                  total: n,
                  porcentaje: porcentaje(consultado.porcentaje),
                })}
              </p>
            )}
          </section>

          <FrequencyChart
            numeros={resultado.numeros}
            consultado={c.numero ?? null}
            modalidad={c.modalidad_nombre}
            cantidadSorteos={n}
          />

          <div className="overflow-hidden rounded-card border border-border bg-surface shadow-1">
            <table className="w-full border-collapse text-sm">
              <caption className="px-3 py-3 text-left font-semibold">
                {msg("rot.est_caption", { modalidad: c.modalidad_nombre })}
              </caption>
              <thead className="bg-muted">
                <tr>
                  {encabezados(
                    parametros,
                    [
                      { id: "numero", texto: msg("rot.numero"), ordenable: true },
                      {
                        id: "frecuencia",
                        texto: msg("rot.frecuencia"),
                        ordenable: true,
                        alineacion: "derecha",
                      },
                      { id: "porcentaje", texto: msg("rot.porcentaje"), alineacion: "derecha" },
                    ],
                    orden,
                  ).map((e) => (
                    <th
                      key={e.id}
                      scope="col"
                      aria-sort={e.sentido}
                      className={cn(
                        "px-3 py-2 text-left font-semibold",
                        e.alineacion === "derecha" && "text-right",
                      )}
                    >
                      <EncabezadoOrdenable e={e} />
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {ordenar(resultado.numeros, orden).map((f) => (
                  <tr key={f.numero} id={`frecuencia-${dosDigitos(f.numero)}`}>
                    <th
                      scope="row"
                      className={cn(
                        "cifras border-t border-border px-3 py-2 text-left font-semibold",
                        f.numero === c.numero && "bg-info-soft text-info-on-soft",
                      )}
                    >
                      {dosDigitos(f.numero)}
                    </th>
                    <td className="cifras border-t border-border px-3 py-2 text-right">
                      {f.frecuencia}
                    </td>
                    <td className="cifras border-t border-border px-3 py-2 text-right">
                      {porcentaje(f.porcentaje)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : (
        <EmptyState
          icono="chart-column"
          titulo={msg("est.sin_sorteos", { modalidad: c.modalidad_nombre })}
          explicacion={msg("vacio.estadisticas.explicacion")}
        />
      )}
    </div>
  );
}
