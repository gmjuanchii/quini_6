"use client";

/**
 * Formulario de jugada ([001] AC-4.1 a AC-4.10, RN-06; [003] FR-031 a FR-034, FR-041): el mismo
 * contenido que `templates/jugadas/formulario.html`, enviado con una Server Action
 * (`useActionState`). Sin scripts es un formulario común que la Server Action procesa igual. Si la
 * jugada repite otra del mismo sorteo, Django responde 409 y se ofrece "Guardar igual".
 */
import Link from "next/link";
import { useActionState, useState } from "react";

import type { components } from "@/api/esquema";
import { BotonEnviar } from "@/components/boton-enviar";
import { Callout } from "@/components/callout";
import { Field } from "@/components/field";
import { SelectorNumeros } from "@/components/selector-numeros";
import { SesionVencida } from "@/components/sesion-vencida";
import { useSinConexion } from "@/components/sin-conexion";
import { boton } from "@/components/ui/variantes";
import { ESTADO_INICIAL, type EstadoFormulario } from "@/lib/acciones-estado";
import { fecha } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

type SorteoDisponible = components["schemas"]["SorteoDisponible"];

export function FormularioJugada({
  accion,
  sorteos,
  inicial,
  clave,
  csrf,
  siguiente,
  cancelar,
  edicion = false,
}: {
  accion: (anterior: EstadoFormulario, datos: FormData) => Promise<EstadoFormulario>;
  sorteos: SorteoDisponible[];
  inicial: { sorteo: string; numeros: string[]; costo: string };
  clave: string;
  csrf: string;
  siguiente: string;
  cancelar: string;
  edicion?: boolean;
}) {
  const [estado, enviar, enviando] = useActionState(accion, ESTADO_INICIAL);
  const { formulario, cortarSiSinConexion, aviso } = useSinConexion();
  const valores = estado.valores
    ? {
        sorteo: estado.valores.sorteo ?? "",
        numeros: (estado.valores.numeros ?? "").split(",").filter(Boolean),
        costo: estado.valores.costo ?? "",
      }
    : inicial;
  const [sorteo, setSorteo] = useState(valores.sorteo);
  const duplicado = estado.general === msg("jugada.duplicada");
  const modalidades = sorteos.find((s) => String(s.numero) === sorteo)?.modalidades ?? [];
  const textoEnviar = edicion ? msg("rot.guardar_cambios") : msg("rot.registrar_jugada_boton");
  const trabajando = edicion ? msg("form.trabajando_guardar") : msg("form.trabajando_registrar");

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
        ref={formulario}
        action={enviar}
        onSubmit={cortarSiSinConexion}
        noValidate
        id="form-jugada"
        className="my-4 grid max-w-xl gap-4 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
      >
        <input type="hidden" name="clave_idempotencia" value={clave} />
        {aviso}
        {duplicado ? (
          <Callout
            variante="warning"
            rol="alert"
            texto={msg("jugada.duplicada")}
            className="flex-wrap"
          >
            <div className="my-3 flex flex-wrap items-center gap-2">
              <BotonEnviar
                name="confirmar_duplicado"
                value="1"
                textoTrabajando={msg("form.trabajando_guardar")}
              >
                {msg("rot.guardar_igual")}
              </BotonEnviar>
              <Link className={boton({ variante: "secundario" })} href="/mis-jugadas/">
                {msg("rot.cancelar")}
              </Link>
            </div>
          </Callout>
        ) : (
          estado.general &&
          !estado.errores.sorteo &&
          Object.keys(estado.errores).length === 0 && (
            <Callout variante="danger" rol="alert" texto={estado.general} />
          )
        )}

        <Field
          id="id_sorteo"
          etiqueta={msg("jugada.campo_sorteo")}
          error={estado.errores.sorteo}
          className="campo"
        >
          <select
            name="sorteo"
            defaultValue={valores.sorteo}
            onChange={(e) => setSorteo(e.currentTarget.value)}
          >
            <option value="">{msg("jugada.opcion_sorteo")}</option>
            {sorteos.map((s) => (
              <option key={s.numero} value={s.numero}>
                {msg("rot.opcion_sorteo", { numero: s.numero, fecha: fecha(s.fecha) })}
              </option>
            ))}
          </select>
        </Field>
        <p className="ayuda -mt-2" id="vista-modalidades" aria-live="polite">
          {modalidades.length > 0
            ? msg("rot.participara_en", {
                modalidades: modalidades.map((m) => m.nombre).join(", "),
              })
            : msg("jugada.ayuda_modalidades")}
        </p>

        <SelectorNumeros
          iniciales={valores.numeros}
          errores={estado.errores.numeros ? [estado.errores.numeros] : []}
        />

        <Field
          id="id_costo"
          etiqueta={msg("rot.costo_jugada")}
          ayuda={msg("rot.costo_ayuda")}
          error={estado.errores.costo}
        >
          <input
            type="text"
            name="costo"
            inputMode="decimal"
            autoComplete="off"
            defaultValue={valores.costo}
          />
        </Field>

        <div className="my-3 flex flex-wrap items-center gap-2">
          <BotonEnviar
            variante={duplicado ? "secundario" : "principal"}
            trabajando={enviando}
            textoTrabajando={trabajando}
          >
            {textoEnviar}
          </BotonEnviar>
          <Link href={cancelar} className={cn("font-medium")}>
            {msg("rot.cancelar")}
          </Link>
        </div>
      </form>
    </>
  );
}
