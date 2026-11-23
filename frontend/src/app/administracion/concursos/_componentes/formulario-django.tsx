"use client";

/**
 * Formulario de Administración de sorteos ([001] US2, US7; [003] FR-033, FR-034, FR-041): dibuja un
 * formulario de Django descrito campo por campo por la API (mismos nombres, rótulos, opciones y
 * valores que las plantillas de `templates/resultados/admin/`) y lo envía con la Server Action
 * `enviarAdmin`. Sin scripts es un formulario común. Con errores, Django devuelve el formulario con
 * lo enviado y los mensajes junto a cada campo.
 */
import Link from "next/link";
import { useActionState } from "react";

import { BotonEnviar } from "@/components/boton-enviar";
import { Callout } from "@/components/callout";
import { DateField } from "@/components/date-field";
import { Icono } from "@/components/icono";
import { SesionVencida } from "@/components/sesion-vencida";
import { useSinConexion } from "@/components/sin-conexion";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

import {
  ESTADO_ADMIN_INICIAL,
  type CampoFormulario,
  type EstadoAdmin,
  type Formulario,
} from "./estado";

type Accion = (anterior: EstadoAdmin, datos: FormData) => Promise<EstadoAdmin>;

function texto(valor: CampoFormulario["valor"]): string {
  if (Array.isArray(valor)) return valor[0] ?? "";
  if (typeof valor === "boolean") return "";
  return valor ?? "";
}

function ErrorCampo({ id, errores }: { id: string; errores: string[] }) {
  return (
    <p
      className="error flex items-start gap-1.5 text-sm font-medium text-danger-text"
      id={`${id}_error`}
      hidden={errores.length === 0}
    >
      <Icono nombre="circle-x" className="mt-0.5 size-4 shrink-0" />
      <span data-texto-error="">{errores.join(" ")}</span>
    </p>
  );
}

/** Un campo de Django con su etiqueta, ayuda y error (como `_campo.html`). */
export function CampoDjango({
  campo,
  prefijo = "id",
}: {
  campo: CampoFormulario;
  prefijo?: string;
}) {
  const id = `${prefijo}_${campo.nombre}`;
  const errores = campo.errores ?? [];
  if (campo.tipo === "date") {
    return (
      <DateField
        campo={{
          id,
          nombre: campo.nombre,
          etiqueta: campo.etiqueta,
          valor: texto(campo.valor),
          ayuda: campo.ayuda ?? undefined,
          error: errores.join(" ") || undefined,
        }}
      />
    );
  }
  if (campo.tipo === "checkbox") {
    return (
      <label className="casilla">
        <input type="checkbox" name={campo.nombre} defaultChecked={campo.valor === true} />{" "}
        {campo.etiqueta}
      </label>
    );
  }
  if (campo.tipo === "checkbox-multiple") {
    const elegidos = Array.isArray(campo.valor) ? campo.valor : [];
    return (
      <fieldset
        className={cn("campo", errores.length > 0 && "campo--error")}
        aria-describedby={errores.length ? `${campo.nombre}_error` : undefined}
      >
        <legend>{campo.etiqueta}</legend>
        {/* Como concurso_form.html: la regla de Premio Extra junto a las modalidades. */}
        {(campo.ayuda || campo.nombre === "modalidades") && (
          <p className="ayuda">{campo.ayuda || msg("rot.adm_premio_extra_requiere")}</p>
        )}
        {campo.opciones.map((o) => (
          <label key={o.valor} className="casilla">
            <input
              type="checkbox"
              name={campo.nombre}
              value={o.valor}
              defaultChecked={elegidos.includes(o.valor)}
            />{" "}
            {o.texto}
          </label>
        ))}
        {errores.length > 0 && (
          <p className="error" id={`${campo.nombre}_error`}>
            {errores.join(" ")}
          </p>
        )}
      </fieldset>
    );
  }
  const describe =
    [campo.ayuda && `${id}_ayuda`, errores.length && `${id}_error`].filter(Boolean).join(" ") ||
    undefined;
  const comunes = {
    id,
    name: campo.nombre,
    defaultValue: texto(campo.valor),
    "aria-describedby": describe,
    "aria-invalid": errores.length ? true : undefined,
  };
  return (
    <div
      className={cn("campo flex flex-col gap-1.5", errores.length > 0 && "campo--error")}
      data-campo={campo.nombre}
    >
      <label htmlFor={id} className="font-medium">
        {campo.etiqueta}
      </label>
      {campo.ayuda && (
        <p className="ayuda text-sm text-muted-foreground" id={`${id}_ayuda`}>
          {campo.ayuda}
        </p>
      )}
      {campo.tipo === "select" ? (
        <select {...comunes}>
          {campo.opciones.map((o) => (
            <option key={o.valor} value={o.valor}>
              {o.texto}
            </option>
          ))}
        </select>
      ) : campo.tipo === "textarea" ? (
        <textarea rows={2} {...comunes} />
      ) : (
        <input type="text" autoComplete="off" {...comunes} />
      )}
      <ErrorCampo id={id} errores={errores} />
    </div>
  );
}

export function FormularioDjango({
  accion,
  formulario,
  boton,
  trabajando,
  cancelar,
  clave,
  csrf,
  siguiente,
  className,
  variante = "principal",
  disposicion = "comun",
  advertencias = [],
  ayudaFinal,
  prefijo = "id",
}: {
  accion: Accion;
  formulario: Formulario;
  boton: string;
  trabajando: string;
  cancelar?: string;
  clave?: string;
  csrf: string;
  siguiente: string;
  className?: string;
  variante?: "principal" | "secundario";
  /** Cómo se ubican los campos: uno debajo del otro, los seis números en fila, la tabla de premios
   * por categoría o las confirmaciones de publicar (con sus advertencias). */
  disposicion?: "comun" | "numeros" | "premios" | "publicar";
  advertencias?: string[];
  /** Ayuda debajo del botón (p. ej. `admin.corregir_bloqueantes`). */
  ayudaFinal?: string;
  /** Prefijo de los `id` de los campos: único si hay varios formularios en la página. */
  prefijo?: string;
}) {
  const [estado, enviar, enviando] = useActionState(accion, ESTADO_ADMIN_INICIAL);
  const { formulario: refFormulario, cortarSiSinConexion, aviso } = useSinConexion();
  const actual = estado.formulario ?? formulario;
  const generales = [...(estado.formulario?.errores ?? []), ...estado.generales].filter(Boolean);
  return (
    <>
      {estado.sesionVencida && (
        <SesionVencida
          pendiente={estado.sesionVencida.pendiente}
          siguiente={siguiente}
          csrf={csrf}
        />
      )}
      <form
        ref={refFormulario}
        action={enviar}
        onSubmit={cortarSiSinConexion}
        noValidate
        className={cn(
          "my-4 grid max-w-xl gap-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6",
          className,
        )}
      >
        {clave && <input type="hidden" name="clave_idempotencia" value={clave} />}
        {aviso}
        {generales.length > 0 && (
          <Callout variante="danger" rol="alert">
            {estado.existente ? (
              <p className="m-0">
                {generales[0]}{" "}
                <Link href={estado.existente.url}>{msg("rot.adm_ir_existente")}</Link>
              </p>
            ) : (
              <ul>
                {generales.map((g) => (
                  <li key={g}>{g}</li>
                ))}
              </ul>
            )}
          </Callout>
        )}
        <Campos
        formulario={actual}
        disposicion={disposicion}
        advertencias={advertencias}
        prefijo={prefijo}
      />
        <div className="my-3 flex flex-wrap items-center gap-2">
          <BotonEnviar variante={variante} trabajando={enviando} textoTrabajando={trabajando}>
            {boton}
          </BotonEnviar>
          {cancelar && <Link href={cancelar}>{msg("rot.cancelar")}</Link>}
        </div>
        {ayudaFinal && <p className="ayuda">{ayudaFinal}</p>}
      </form>
    </>
  );
}

function Campos({
  formulario,
  disposicion,
  advertencias,
  prefijo,
}: {
  prefijo: string;
  formulario: Formulario;
  disposicion: "comun" | "numeros" | "premios" | "publicar";
  advertencias: string[];
}) {
  const porNombre = new Map(formulario.campos.map((c) => [c.nombre, c]));
  if (disposicion === "numeros") {
    const numeros = formulario.campos.filter((c) => /^n[1-6]$/.test(c.nombre));
    const resto = formulario.campos.filter((c) => !/^n[1-6]$/.test(c.nombre));
    return (
      <>
        <fieldset>
          <legend>{msg("rot.adm_seis_numeros")}</legend>
          <div className="flex flex-wrap items-start gap-x-4 gap-y-2">
            {numeros.map((c) => (
              <div key={c.nombre} className="w-18">
                <CampoDjango campo={c} prefijo={prefijo} />
              </div>
            ))}
          </div>
        </fieldset>
        {resto.map((c) => (
          <CampoDjango key={c.nombre} campo={c} prefijo={prefijo} />
        ))}
      </>
    );
  }
  if (disposicion === "premios") {
    const enFilas = new Set(formulario.filas.flatMap((f) => f.campos));
    const ganadora = porNombre.get("aciertos_categoria_ganadora");
    const resto = formulario.campos.filter(
      (c) => !enFilas.has(c.nombre) && c.nombre !== "aciertos_categoria_ganadora",
    );
    const encabezados =
      formulario.filas[0]?.campos.map((n) => porNombre.get(n)?.etiqueta ?? n) ?? [];
    return (
      <>
        {ganadora && <CampoDjango campo={ganadora} prefijo={prefijo} />}
        <table className="apilable">
          <caption>{msg("rot.adm_caption_premios")}</caption>
          <thead>
            <tr>
              <th scope="col">{msg("rot.adm_categoria")}</th>
              {encabezados.map((e) => (
                <th key={e} scope="col">
                  {e}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {formulario.filas.map((f) => (
              <tr key={f.codigo}>
                <th scope="row">{f.nombre}</th>
                {f.campos.map((nombre) => {
                  const c = porNombre.get(nombre);
                  if (!c) return <td key={nombre} />;
                  const errores = c.errores ?? [];
                  return (
                    <td
                      key={nombre}
                      data-rotulo={c.etiqueta}
                      className={cn("campo", errores.length > 0 && "campo--error")}
                    >
                      <label htmlFor={`id_${nombre}`} className="visualmente-oculto">
                        {f.nombre}: {c.etiqueta}
                      </label>
                      <input
                        type="text"
                        id={`id_${nombre}`}
                        name={nombre}
                        defaultValue={texto(c.valor)}
                        autoComplete="off"
                      />
                      {errores.length > 0 && <p className="error">{errores.join(" ")}</p>}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
        {resto.map((c) => (
          <CampoDjango key={c.nombre} campo={c} prefijo={prefijo} />
        ))}
      </>
    );
  }
  if (disposicion === "publicar") {
    const confirmar = porNombre.get("confirmar_advertencias");
    const cotejo = porNombre.get("cotejo");
    return (
      <>
        {advertencias.length > 0 && (
          <>
            <Callout variante="warning" titulo={msg("rot.adm_advertencias")}>
              <ul className="mb-0">
                {advertencias.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </Callout>
            {confirmar && <CampoDjango campo={confirmar} prefijo={prefijo} />}
          </>
        )}
        {cotejo && <CampoDjango campo={cotejo} prefijo={prefijo} />}
      </>
    );
  }
  return (
    <>
      {formulario.campos.map((c) => (
        <CampoDjango key={c.nombre} campo={c} prefijo={prefijo} />
      ))}
    </>
  );
}
