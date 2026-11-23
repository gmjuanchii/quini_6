/**
 * Piezas de las pantallas de Resultados ([001] US1; [003] FR-041, pantalla 4): el mismo marcado que
 * `templates/resultados/_bolillas.html`, `_listado.html`, `_busqueda_form.html` y `_modalidad.html`.
 * Componentes de servidor: la pantalla pública no necesita JavaScript propio (R-24).
 */
import Link from "next/link";

import type { components } from "@/api/esquema";
import { DateField } from "@/components/date-field";
import { boton } from "@/components/ui/variantes";
import { dosDigitos, fecha, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

export type SorteoResumen = components["schemas"]["SorteoResumen"];
export type SorteoPublico = components["schemas"]["SorteoPublico"];
type Modalidad = components["schemas"]["ModalidadPublica"];
type FuentePublica = components["schemas"]["FuentePublica"];

export function claseCompletitud(codigo: string): string {
  return codigo === "COMPLETO" ? "estado--con-premio" : "estado--pendiente";
}

export function Bolillas({ numeros, rotulo }: { numeros: number[]; rotulo?: string }) {
  return (
    <ul className="numeros" aria-label={rotulo ?? msg("rot.numeros_bolillas")}>
      {numeros.map((n) => (
        <li key={n} className="bolilla">
          {dosDigitos(n)}
        </li>
      ))}
    </ul>
  );
}

export function ListadoSorteos({ sorteos }: { sorteos: SorteoResumen[] }) {
  return (
    <div className="overflow-x-auto rounded-card border border-border bg-surface shadow-1 max-md:overflow-visible max-md:border-0 max-md:bg-transparent max-md:shadow-none">
      <table className="apilable">
        <caption className="visualmente-oculto">{msg("rot.caption_sorteos")}</caption>
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
            <th scope="col" className="px-3 py-2">
              <span className="visualmente-oculto">{msg("rot.acciones")}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {sorteos.map((s) => (
            <tr key={s.numero} className="fila-enlace">
              <td
                data-rotulo={msg("rot.sorteo")}
                className="cifras font-semibold whitespace-nowrap"
              >
                {msg("rot.numero_sorteo", { numero: s.numero })}
              </td>
              <td data-rotulo={msg("rot.fecha_del_sorteo")} className="cifras whitespace-nowrap">
                {fecha(s.fecha)}
              </td>
              <td data-rotulo={msg("rot.estado")}>
                <span className={cn("estado", claseCompletitud(s.completitud.codigo))}>
                  {s.completitud.texto}
                </span>
              </td>
              <td className="whitespace-nowrap md:text-right">
                <Link
                  href={`/resultados/${s.numero}/`}
                  data-enlace-fila=""
                  className="ver-detalle text-sm font-medium text-primary no-underline hover:underline"
                >
                  {msg("ext.ver_detalle")}
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function BusquedaForm({
  numero = "",
  fechaBuscada = "",
  errorFecha,
}: {
  numero?: string;
  fechaBuscada?: string;
  errorFecha?: string;
}) {
  return (
    <section
      className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
      aria-labelledby="titulo-buscar"
    >
      <h2 id="titulo-buscar">{msg("rot.buscar_sorteo")}</h2>
      <div className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
        <form
          method="get"
          action="/resultados/buscar/"
          className="flex max-w-full min-w-0 flex-wrap items-end gap-3"
          role="search"
          aria-label={msg("rot.buscar_por_numero")}
          noValidate
        >
          <div className="campo">
            <label htmlFor="buscar-numero">{msg("rot.numero_de_sorteo")}</label>
            <input
              type="text"
              id="buscar-numero"
              name="numero"
              inputMode="numeric"
              defaultValue={numero}
            />
          </div>
          <button type="submit" className={boton({ variante: "secundario" })}>
            {msg("rot.buscar")}
          </button>
        </form>
        <form
          method="get"
          action="/resultados/buscar/"
          className="flex max-w-full min-w-0 flex-wrap items-end gap-3"
          role="search"
          aria-label={msg("rot.buscar_por_fecha")}
          noValidate
        >
          <DateField
            campo={{
              id: "buscar-fecha",
              nombre: "fecha",
              etiqueta: msg("rot.fecha_del_sorteo"),
              valor: fechaBuscada,
              error: errorFecha,
            }}
          />
          <button type="submit" className={boton({ variante: "secundario" })}>
            {msg("rot.buscar")}
          </button>
        </form>
      </div>
    </section>
  );
}

function textoFuente(
  fuente: FuentePublica,
  conFecha: "rot.fuente_consultada" | "rot.fuente_premios_consultada",
) {
  const sola = conFecha === "rot.fuente_consultada" ? "rot.fuente_sola" : "rot.fuente_premios_sola";
  return fuente.fecha_consulta
    ? msg(conFecha, { fuente: fuente.descripcion, fecha: fecha(fuente.fecha_consulta) })
    : msg(sola, { fuente: fuente.descripcion });
}

function Marcas({ revision, corregido }: { revision: boolean; corregido: string | null }) {
  return (
    <>
      {revision && (
        <p>
          <span className="estado estado--revision">{msg("rot.en_revision")}</span>
        </p>
      )}
      {corregido && (
        <p>
          <span className="estado estado--corregido">
            {msg("rot.corregido_el", { fecha: fecha(corregido) })}
          </span>
        </p>
      )}
    </>
  );
}

function Ganadores({ n }: { n: number | null }) {
  if (n === null) return <>{msg("rot.no_disponible")}</>;
  return <>{n === 1 ? msg("rot.un_ganador") : msg("rot.n_ganadores", { n })}</>;
}

/** `templates/resultados/_modalidad.html`: números (o el conjunto de Premio Extra) y premios. */
export function SeccionModalidad({ m }: { m: Modalidad }) {
  const premiosPublicados =
    m.estado_premios.codigo === "PUBLICADO" || m.estado_premios.codigo === "EN_REVISION";
  return (
    <section
      className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
      id={`modalidad-${m.slug}`}
      aria-labelledby={`titulo-${m.slug}`}
    >
      <h2 id={`titulo-${m.slug}`}>{m.nombre}</h2>
      {m.es_premio_extra ? (
        m.conjunto ? (
          <>
            <h3>{msg("rot.conjunto_premio_extra")}</h3>
            <p className="text-sm text-muted-foreground">
              {msg("rot.conjunto_explicacion", { n: m.conjunto.length })}
            </p>
            <Bolillas numeros={m.conjunto} rotulo={msg("rot.conjunto_premio_extra")} />
            <Marcas revision={m.revision_numeros} corregido={m.corregido_numeros} />
          </>
        ) : (
          <p>
            <span className="estado estado--pendiente">{m.estado_numeros.texto}</span>
          </p>
        )
      ) : m.numeros ? (
        <>
          <Bolillas numeros={m.numeros} rotulo={msg("rot.numeros_ganadores")} />
          <Marcas revision={m.revision_numeros} corregido={m.corregido_numeros} />
          {m.fuente_numeros && (
            <p className="text-sm text-muted-foreground">
              {textoFuente(m.fuente_numeros, "rot.fuente_consultada")}
            </p>
          )}
        </>
      ) : (
        <p>
          <span className="estado estado--pendiente">{m.estado_numeros.texto}</span>
        </p>
      )}

      <h3>{msg("rot.premios")}</h3>
      {premiosPublicados ? (
        <>
          <Marcas revision={m.revision_premios} corregido={m.corregido_premios} />
          {m.categorias.map((c) => (
            <div
              key={c.codigo}
              className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
            >
              <h4>{c.nombre}</h4>
              <dl className="datos">
                <dt>{msg("rot.aciertos_condicion")}</dt>
                <dd>{c.condicion}</dd>
                <dt>{msg("rot.ganadores")}</dt>
                <dd>
                  <Ganadores n={c.ganadores} />
                </dd>
                <dt>{msg("rot.importe_categoria")}</dt>
                <dd>
                  {c.importe_categoria === null
                    ? msg("rot.no_disponible")
                    : pesos(c.importe_categoria)}
                </dd>
                <dt>{msg("rot.importe_individual")}</dt>
                <dd>
                  {c.importe_individual === null
                    ? msg("rot.premios_pendientes")
                    : pesos(c.importe_individual)}
                </dd>
                {c.pozo_vacante_acumulado !== null && (
                  <>
                    <dt>{msg("rot.pozo_vacante")}</dt>
                    <dd>{pesos(c.pozo_vacante_acumulado)}</dd>
                  </>
                )}
              </dl>
            </div>
          ))}
          {m.fuente_premios && (
            <p className="text-sm text-muted-foreground">
              {textoFuente(m.fuente_premios, "rot.fuente_premios_consultada")}
            </p>
          )}
        </>
      ) : (
        <p>
          <span className="estado estado--pendiente">{msg("rot.premios_pendientes")}</span>
        </p>
      )}
    </section>
  );
}
