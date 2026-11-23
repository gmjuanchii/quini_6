/**
 * Resultados del Quini 6 en Next.js ([001] US1, RN-25; [003] AC-8.4, FR-026, FR-041, pantalla 4): el
 * mismo contenido que `templates/resultados/index.html`, con `GET /api/v1/sorteos/ultimo/` y
 * `GET /api/v1/sorteos/`. Componente de servidor sin JavaScript propio (R-24); los accesos del
 * estado vacío solo aparecen si Django informa una sesión de administración (RN-06).
 */
import type { Metadata } from "next";
import Link from "next/link";

import { apiServidor } from "@/api/servidor";
import { EmptyState } from "@/components/empty-state";
import { boton } from "@/components/ui/variantes";
import { fecha } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { obtenerSesion } from "@/lib/sesion";
import { cn } from "@/lib/utils";

import {
  Bolillas,
  BusquedaForm,
  claseCompletitud,
  ListadoSorteos,
} from "./_componentes/resultados";

export const metadata: Metadata = { title: msg("rot.res_titulo") };

export default async function Resultados() {
  const api = await apiServidor();
  const [ultimo, listado, sesion] = await Promise.all([
    api.GET("/api/v1/sorteos/ultimo/"),
    api.GET("/api/v1/sorteos/"),
    obtenerSesion(),
  ]);
  if (!ultimo.data || !listado.data) throw new Error("La API de resultados no respondió");
  const { ultimo: u, pendiente } = ultimo.data;
  const sorteos = listado.data.elementos;

  if (!u && !pendiente && sorteos.length === 0) {
    return (
      <>
        <h1>{msg("rot.res_titulo")}</h1>
        {sesion.es_administrador ? (
          <EmptyState
            icono="list-ordered"
            titulo={msg("vacio.resultados.titulo")}
            explicacion={msg("vacio.resultados.explicacion")}
            accion={{
              texto: msg("vacio.resultados.accion_cargar"),
              href: "/administracion/concursos/nuevo/",
            }}
            accionSecundaria={{
              texto: msg("vacio.resultados.accion_extraccion"),
              href: "/administracion/extracciones/",
            }}
            nota={msg("vacio.resultados_nota_admin")}
          />
        ) : (
          <EmptyState
            icono="list-ordered"
            titulo={msg("vacio.resultados.titulo")}
            explicacion={msg("vacio.resultados.explicacion")}
          />
        )}
      </>
    );
  }

  return (
    <>
      <h1>{msg("rot.res_titulo")}</h1>
      {pendiente && (
        <section
          className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
          id="concurso-actual"
          aria-labelledby="titulo-actual"
        >
          <h2 id="titulo-actual">
            {msg("rot.res_sorteo_del", { numero: pendiente.numero, fecha: fecha(pendiente.fecha) })}
          </h2>
          <p>
            <span className="estado estado--pendiente">{msg("rot.res_pendientes")}</span>
          </p>
          <p>
            <Link href={`/resultados/${pendiente.numero}/`}>{msg("rot.ver_sorteo")}</Link>
          </p>
        </section>
      )}
      {u ? (
        <section
          className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
          id="ultimos-resultados"
          aria-labelledby="titulo-ultimos"
        >
          <h2 id="titulo-ultimos">
            {msg("rot.res_ultimos", { numero: u.numero, fecha: fecha(u.fecha) })}
          </h2>
          <p>
            {msg("rot.res_estado_sorteo")}{" "}
            <span className={cn("estado", claseCompletitud(u.completitud.codigo))}>
              {u.completitud.texto}
            </span>
          </p>
          {u.modalidades.map((m) => (
            <div key={m.slug}>
              <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
                <h3>{m.nombre}</h3>
                {m.es_premio_extra ? (
                  m.conjunto ? (
                    <span>{msg("rot.res_numeros_distintos", { n: m.conjunto.length })}</span>
                  ) : (
                    <span className="estado estado--pendiente">{m.estado_numeros.texto}</span>
                  )
                ) : m.numeros ? (
                  <Bolillas numeros={m.numeros} rotulo={msg("rot.numeros_ganadores")} />
                ) : (
                  <span className="estado estado--pendiente">{m.estado_numeros.texto}</span>
                )}
              </div>
              {m.revision_numeros && (
                <p>
                  <span className="estado estado--revision">{msg("rot.en_revision")}</span>
                </p>
              )}
            </div>
          ))}
          <p>
            <Link className={boton({ variante: "principal" })} href={`/resultados/${u.numero}/`}>
              {msg("rot.ver_premios")}
            </Link>
          </p>
        </section>
      ) : (
        <p className="text-muted-foreground">{msg("vacio.resultados.titulo")}</p>
      )}
      <BusquedaForm />
      <section aria-labelledby="titulo-listado">
        <h2 id="titulo-listado">{msg("rot.todos_los_sorteos")}</h2>
        {sorteos.length > 0 && <ListadoSorteos sorteos={sorteos} />}
      </section>
    </>
  );
}
