/**
 * Panel de un sorteo en Next.js ([001] US2, US7; [003] FR-041, pantalla 6): el mismo contenido que
 * `templates/resultados/admin/panel.html`, con `GET /api/v1/admin/sorteos/{numero}/`. Las acciones
 * de cada bloque son las que informa Django (`acciones`); observar, poner o quitar la revisión y
 * corregir piden un motivo en un `<details>` (funciona sin scripts).
 */
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { BackLink } from "@/components/back-link";
import { Callout } from "@/components/callout";
import { boton } from "@/components/ui/variantes";
import { dosDigitos, fecha, fechaHora } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { rutaActual } from "@/lib/sesion";
import { cn } from "@/lib/utils";

import { enviarAdmin } from "../acciones";
import {
  API,
  BASE,
  leerAdmin,
  tokenCsrf,
  type BloqueAdmin,
  type PanelSorteo,
} from "../_componentes/comunes";
import type { Formulario } from "../_componentes/estado";
import { FormularioDjango } from "../_componentes/formulario-django";

type Props = { params: Promise<{ numero: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  return { title: msg("rot.sorteo_numero", { numero: (await params).numero }) };
}

function Bolillas({ numeros, rotulo }: { numeros: number[]; rotulo: string }) {
  return (
    <ul className="numeros" aria-label={rotulo}>
      {numeros.map((n) => (
        <li key={n} className="bolilla">
          {dosDigitos(n)}
        </li>
      ))}
    </ul>
  );
}

function motivo(etiqueta: string, conFuente = false): Formulario {
  const campos: Formulario["campos"] = [
    {
      nombre: "motivo",
      etiqueta,
      tipo: "textarea",
      valor: "",
      opciones: [],
      requerido: true,
      errores: [],
    },
  ];
  if (conFuente) {
    campos.push(
      {
        nombre: "fuente_descripcion",
        etiqueta: msg("rot.adm_fuente_correccion"),
        tipo: "text",
        valor: "",
        opciones: [],
        requerido: true,
        errores: [],
      },
      {
        nombre: "fuente_fecha_consulta",
        etiqueta: msg("rot.adm_fecha_fuente"),
        tipo: "date",
        valor: "",
        opciones: [],
        requerido: true,
        errores: [],
      },
    );
  }
  return { campos, filas: [], errores: [] };
}

async function Bloque({ numero, slug, b }: { numero: number; slug: string; b: BloqueAdmin }) {
  const url = `${BASE}/${numero}/${slug}/${b.bloque}`;
  const api = `${API}/${numero}/${slug}/${b.bloque}`;
  const panel = `${BASE}/${numero}/`;
  const csrf = await tokenCsrf();
  const siguiente = await rutaActual();
  // Como la vista HTML: al iniciar una corrección se va al formulario del bloque; lo demás, al panel.
  const accion = (operacion: string) =>
    enviarAdmin.bind(null, {
      metodo: "POST",
      ruta: `${api}/${operacion}/`,
      exito: operacion === "corregir" ? `${url}/` : panel,
    });
  const motivoForm = (
    operacion: string,
    titulo: string,
    rotulo: string,
    textoBoton: string,
    conFuente = false,
  ) => (
    // Una instancia por operación: al cambiar las acciones del bloque no se reutiliza el formulario
    // (ni el estado) de otra.
    <details key={operacion}>
      <summary>{titulo}</summary>
      <FormularioDjango
        accion={accion(operacion)}
        formulario={motivo(rotulo, conFuente)}
        boton={textoBoton}
        trabajando={msg("form.trabajando_guardar")}
        variante="secundario"
        csrf={csrf}
        siguiente={siguiente}
        className="border-0 p-0 shadow-none"
        prefijo={`${slug}-${b.bloque}-${operacion}`}
      />
    </details>
  );
  const t = b.trabajo;
  return (
    <div className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6">
      <h3>
        {b.nombre}: <span className={cn("estado", b.estado.clase)}>{b.estado.texto}</span>
      </h3>
      {b.vigente && (
        <>
          <p className="text-sm text-muted-foreground">
            {b.vigente.fuente_descripcion
              ? msg("rot.adm_publicado_el_fuente", {
                  fecha_hora: fechaHora(b.vigente.publicada_en),
                  fuente: b.vigente.fuente_descripcion,
                })
              : msg("rot.adm_publicado_el", { fecha_hora: fechaHora(b.vigente.publicada_en) })}
          </p>
          {b.bloque === "numeros" && (
            <Bolillas numeros={b.vigente.numeros} rotulo={msg("rot.adm_numeros_publicados")} />
          )}
        </>
      )}
      {b.en_revision && (
        <Callout
          variante="warning"
          texto={msg("rot.adm_en_revision_motivo", { motivo: b.motivo_revision })}
        />
      )}
      {t && (
        <>
          <p>
            {msg("rot.adm_actualizado", {
              estado: t.es_correccion ? msg("rot.adm_correccion_preparacion") : b.estado.texto,
              fecha_hora: fechaHora(t.actualizada_en),
            })}
          </p>
          {b.bloque === "numeros" && (
            <Bolillas numeros={t.numeros} rotulo={msg("rot.adm_numeros_preparacion")} />
          )}
          {t.estado === "OBSERVADO" && (
            <Callout
              variante="danger"
              texto={msg("rot.adm_observado_motivo", { motivo: t.motivo_observacion })}
            />
          )}
        </>
      )}
      <div className="my-3 flex flex-wrap items-center gap-2">
        {(b.acciones.includes("editar") || b.acciones.includes("cargar")) && (
          <Link className={boton({ variante: "secundario" })} href={`${url}/`}>
            {b.acciones.includes("editar") ? msg("rot.editar") : msg("rot.adm_cargar")}
          </Link>
        )}
        {b.acciones.includes("publicar") && (
          <Link className={boton({ variante: "secundario" })} href={`${url}/publicar/`}>
            {t?.es_correccion
              ? msg("rot.adm_publicar_correccion")
              : msg("rot.adm_revisar_publicar")}
          </Link>
        )}
        {b.acciones.includes("resolver") && (
          <FormularioDjango
            accion={accion("resolver")}
            formulario={{ campos: [], filas: [], errores: [] }}
            boton={msg("rot.adm_resolver")}
            trabajando={msg("form.trabajando_guardar")}
            variante="secundario"
            csrf={csrf}
            siguiente={siguiente}
            className="my-0 border-0 p-0 shadow-none"
          />
        )}
      </div>
      {b.acciones.includes("observar") &&
        motivoForm(
          "observar",
          msg("rot.adm_marcar_observado"),
          msg("rot.adm_motivo_observacion"),
          msg("rot.adm_observar"),
        )}
      {b.acciones.includes("revision") &&
        motivoForm(
          "revision",
          msg("rot.adm_marcar_revision"),
          msg("rot.adm_motivo_revision"),
          msg("rot.adm_marcar_revision"),
        )}
      {b.acciones.includes("quitar_revision") &&
        motivoForm(
          "quitar-revision",
          msg("rot.adm_quitar_revision"),
          msg("rot.adm_motivo_quitar"),
          msg("rot.adm_quitar_revision"),
        )}
      {b.acciones.includes("corregir") &&
        motivoForm(
          "corregir",
          msg("rot.adm_corregir"),
          msg("rot.adm_motivo_correccion"),
          msg("rot.adm_iniciar_correccion"),
          true,
        )}
    </div>
  );
}

export default async function Panel({ params }: Props) {
  const numero = Number((await params).numero) || 0;
  const p = await leerAdmin<PanelSorteo>(`/${numero}/`);
  if (!p) notFound();
  return (
    <>
      <BackLink href={`${BASE}/`} texto={msg("nav.volver_sorteos")} />
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <h1>{msg("rot.sorteo_numero", { numero })}</h1>
        <div className="my-3 flex flex-wrap items-center gap-2">
          <Link className={boton({ variante: "secundario" })} href={`${BASE}/${numero}/modificar/`}>
            {msg("rot.adm_modificar_sorteo")}
          </Link>
          <Link className={boton({ variante: "secundario" })} href={`${BASE}/${numero}/historial/`}>
            {msg("rot.adm_ver_historial")}
          </Link>
          <a className={boton({ variante: "secundario" })} href={`/resultados/${numero}/`}>
            {msg("rot.adm_ver_publica")}
          </a>
        </div>
      </div>
      <p>
        {msg("rot.adm_resumen", {
          fecha: fecha(p.fecha),
          completitud: p.completitud.texto,
          jugadas: p.admite_jugadas
            ? msg("rot.adm_admite_jugadas")
            : msg("rot.adm_no_admite_jugadas"),
        })}
      </p>
      {p.filas.length > 0 ? (
        p.filas.map((f) => (
          <section
            key={f.modalidad.slug}
            className="my-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
            aria-labelledby={`mod-${f.modalidad.slug}`}
          >
            <h2 id={`mod-${f.modalidad.slug}`}>{f.modalidad.nombre}</h2>
            {!f.modalidad.tiene_extraccion_propia && (
              <p className="text-sm text-muted-foreground">
                {msg("rot.adm_premio_extra_explicacion")}
              </p>
            )}
            {f.bloques.map((b) => (
              <Bloque key={b.bloque} numero={numero} slug={f.modalidad.slug} b={b} />
            ))}
          </section>
        ))
      ) : (
        <div className="rounded-card bg-surface px-6 py-8 text-center text-muted-foreground shadow-1">
          <p>{msg("rot.adm_sin_modalidades")}</p>
        </div>
      )}
    </>
  );
}
