/**
 * Extracción histórica en Next.js ([003] HU-14, FR-041, R-27, pantalla 1): el mismo contenido que
 * `templates/extracciones/inicio.html` + `_pantalla.html`, con los datos de
 * `GET /api/v1/extracciones/` (filtro, orden y página en la dirección, AC-1.4, AC-9.1, AC-9.2) y los
 * atajos de `GET /api/v1/periodos/atajos/?formulario=extraccion` (RN-04).
 *
 * Componente de servidor: funciona sin scripts (NFR-007). Con scripts, el avance de la propia
 * extracción se actualiza solo (ProgressPanel, R-10) y "Eliminar" abre el diálogo (ruta interceptada).
 */
import type { Metadata } from "next";
import { cookies } from "next/headers";
import Link from "next/link";

import { apiServidor } from "@/api/servidor";
import type { components } from "@/api/esquema";
import { ActionMenu, type OpcionMenu } from "@/components/action-menu";
import { BackLink } from "@/components/back-link";
import { DataTable, type Fila } from "@/components/data-table";
import { EmptyState } from "@/components/empty-state";
import { Pagination } from "@/components/pagination";
import { ProgressPanel } from "@/components/progress-panel";
import { StatusBadge } from "@/components/status-badge";
import { boton } from "@/components/ui/variantes";
import { nuevaClaveIdempotencia } from "@/lib/acciones";
import { fecha, fechaHora } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { rutaActual, verificarRespuesta } from "@/lib/sesion";
import { conParametros, encabezados, type Parametros } from "@/lib/tablas";
import { cn } from "@/lib/utils";

import { FiltroEstado } from "./_componentes/filtro-estado";
import { FormularioInicio } from "./_componentes/formulario-inicio";
import { RefrescoEnCurso } from "./_componentes/refresco-en-curso";

export const metadata: Metadata = { title: msg("ext.titulo") };

type Resumen = components["schemas"]["ExtraccionResumen"];

const BASE = "/administracion/extracciones/";

/** data-model § 2: las cinco etiquetas en el orden de los filtros (RN-01). */
const ETIQUETAS = [
  ["en-curso", "etiqueta.en_curso"],
  ["finalizada", "etiqueta.finalizada"],
  ["con-advertencias", "etiqueta.con_advertencias"],
  ["sin-sorteos", "etiqueta.sin_sorteos"],
  ["con-error", "etiqueta.con_error"],
] as const;

function uno(valor: string | string[] | undefined): string | undefined {
  return Array.isArray(valor) ? valor[0] : valor;
}

/** [003] AC-2.1, AC-2.6: opciones del menú ⋮ ("Eliminar" solo si terminó). */
function opciones(e: Resumen): OpcionMenu[] {
  const lista: OpcionMenu[] = [{ texto: msg("ext.ver_detalle"), href: `${BASE}${e.id}/` }];
  if (e.url_csv) {
    lista.push({
      texto: msg("ext.boton_descargar"),
      href: e.url_csv,
      icono: "download",
      externo: true,
    });
  }
  if (e.eliminable) {
    lista.push({
      texto: msg("ext.eliminar"),
      href: `${BASE}${e.id}/eliminar/`,
      icono: "trash-2",
      destructivo: true,
      confirmar: true,
    });
  }
  return lista;
}

function fila(e: Resumen): Fila {
  const revision = e.etiqueta.requiere_revision;
  return {
    clave: String(e.id),
    id: `fila-extraccion-${e.id}`,
    enlace: true,
    className: cn(
      revision && "border-l-4",
      revision && (e.etiqueta.variante === "danger" ? "border-l-danger" : "border-l-warning"),
    ),
    datos: revision ? { "data-requiere-revision": "" } : undefined,
    celdas: {
      fecha: (
        <>
          {fechaHora(e.iniciada_en)}
          {revision && (
            <span className="visualmente-oculto"> · {msg("ext.requiere_revision")}</span>
          )}
        </>
      ),
      ejecutada_por: (
        <span className="block max-w-[12rem] truncate max-md:max-w-full" title={e.creada_por}>
          {e.creada_por}
        </span>
      ),
      periodo: msg("rot.periodo_rango", { desde: fecha(e.desde), hasta: fecha(e.hasta) }),
      estado: (
        <span className="sobre-fila inline-block">
          <StatusBadge etiqueta={e.etiqueta} id={e.id} />
        </span>
      ),
      acciones: (
        <div className="flex items-center justify-between gap-2 md:justify-end">
          <Link
            href={`${BASE}${e.id}/`}
            data-enlace-fila=""
            className="ver-detalle text-sm font-medium text-primary no-underline hover:underline"
          >
            {msg("ext.ver_detalle")}
          </Link>
          <span className="sobre-fila">
            <ActionMenu nombre={e.nombre_acciones} opciones={opciones(e)} />
          </span>
        </div>
      ),
    },
  };
}

export default async function ExtraccionHistorica({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const sp = await searchParams;
  const estado = uno(sp.estado) ?? "";
  const orden = uno(sp.orden) ?? "";
  const pagina = uno(sp.pagina) ?? "1";
  const api = await apiServidor();
  const [listado, atajos] = await Promise.all([
    api.GET("/api/v1/extracciones/", { params: { query: { estado, orden, pagina } } }),
    api.GET("/api/v1/periodos/atajos/", { params: { query: { formulario: "extraccion" } } }),
  ]);
  await verificarRespuesta(listado.response);
  if (!listado.data || !atajos.data) throw new Error("La API de extracciones no respondió");
  const datos = listado.data;
  const propia = datos.en_curso_propia;
  const filtro = ETIQUETAS.find(([slug]) => slug === datos.filtro);
  const nombreFiltro = filtro ? msg(filtro[1]) : "";

  // Parámetros que se conservan en orden, filtro, página y atajos (AC-9.2).
  const parametros: Parametros = {
    estado: datos.filtro ?? "",
    orden: datos.orden !== "-fecha" ? datos.orden : "",
  };
  const atajo = atajos.data.find((a) => a.clave === uno(sp.atajo));
  const hoy = atajos.data.find((a) => a.clave === "anio_en_curso")?.hasta ?? "";
  const hrefAtajo = Object.fromEntries(
    atajos.data.map((a) => [a.clave, conParametros(parametros, { atajo: a.clave })]),
  );
  const otrasEnCurso = datos.elementos.some((e) => e.en_curso && e.id !== propia?.id);
  const csrf = (await cookies()).get("csrftoken")?.value ?? "";

  return (
    <>
      <BackLink href="/administracion/concursos/" texto={msg("nav.volver_sorteos")} />
      <h1>{msg("ext.titulo")}</h1>
      <div id="pantalla-extracciones" className="flex flex-col gap-4">
        {propia ? (
          <>
            <ProgressPanel
              id={propia.id}
              inicial={propia.avance}
              periodo={msg("rot.periodo_consultado_valor", {
                desde: fecha(propia.desde),
                hasta: fecha(propia.hasta),
              })}
            />
            <p>
              <Link className={boton({ variante: "secundario" })} href={`${BASE}${propia.id}/`}>
                {msg("rot.ver_en_curso")}
              </Link>
            </p>
          </>
        ) : (
          <FormularioInicio
            atajos={atajos.data}
            inicial={{ inicio: atajo?.desde ?? "", fin: atajo?.hasta ?? "" }}
            max={hoy}
            clave={nuevaClaveIdempotencia()}
            csrf={csrf}
            hrefAtajo={hrefAtajo}
            siguiente={await rutaActual()}
          />
        )}

        <h2 className="mt-4 text-2xl font-semibold">{msg("ext.anteriores")}</h2>

        {/* [003] AC-1.4, FR-003: filtro por estado en la dirección (funciona sin scripts). */}
        <form method="get" action={BASE} className="flex flex-wrap items-end gap-3" noValidate>
          {parametros.orden && <input type="hidden" name="orden" value={parametros.orden} />}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="filtro-estado" className="font-medium">
              {msg("ext.filtro_estado")}
            </label>
            <FiltroEstado
              id="filtro-estado"
              valor={datos.filtro ?? ""}
              opciones={[
                { valor: "", texto: msg("ext.filtro_todos") },
                ...ETIQUETAS.map(([slug, clave]) => ({ valor: slug, texto: msg(clave) })),
              ]}
            />
          </div>
          <button type="submit" className={boton({ variante: "secundario" })}>
            {msg("ext.filtrar")}
          </button>
          {filtro && (
            <p
              className="flex min-h-control items-center text-sm text-muted-foreground"
              role="status"
            >
              {msg("ext.filtro_aplicado", { filtro: nombreFiltro })}
            </p>
          )}
        </form>

        {datos.elementos.length > 0 ? (
          <>
            {otrasEnCurso && <RefrescoEnCurso />}
            <DataTable
              titulo={msg("ext.anteriores")}
              encabezados={encabezados(
                parametros,
                [
                  { id: "fecha", texto: msg("ext.col_fecha"), ordenable: true },
                  { id: "ejecutada_por", texto: msg("rot.ejecutada_por") },
                  { id: "periodo", texto: msg("rot.periodo"), ordenable: true },
                  { id: "estado", texto: msg("rot.estado"), ordenable: true },
                ],
                datos.orden,
              )}
              filas={datos.elementos.map(fila)}
              clasesCelda={{
                fecha: "cifras !text-left",
                periodo: "cifras !text-left",
                acciones: "whitespace-nowrap md:text-right",
              }}
              columnaAcciones={msg("rot.acciones")}
              className="rounded-card border border-border bg-surface shadow-1 max-md:-mx-4 max-md:overflow-x-clip max-md:rounded-none max-md:border-0 max-md:bg-transparent max-md:px-4 max-md:shadow-none"
            />
            <Pagination pagina={datos.pagina} paginas={datos.paginas} parametros={parametros} />
          </>
        ) : filtro ? (
          <EmptyState
            variante="sin_resultados"
            titulo={msg("vacio.filtro.titulo")}
            explicacion={msg("vacio.filtro.explicacion", { filtro: nombreFiltro })}
            limpiarHref={BASE}
          />
        ) : (
          <EmptyState
            variante="sin_datos"
            icono="download"
            titulo={msg("vacio.extracciones.titulo")}
            explicacion={msg("vacio.extracciones.explicacion")}
          />
        )}
      </div>
    </>
  );
}
