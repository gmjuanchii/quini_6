"use client";

/**
 * Formularios de Ingresar y Crear cuenta ([001] AC-3.1 a AC-3.7; [003] HU-06, AC-6.1 a AC-6.7):
 * tarjeta centrada, autocompletado, validación previa del correo (mismos textos que Django) y
 * "Ingresando…". Sin scripts son formularios comunes que la Server Action procesa igual.
 */
import Link from "next/link";
import { useActionState, useState, type FormEvent } from "react";

import { BotonEnviar } from "@/components/boton-enviar";
import { Callout } from "@/components/callout";
import { Field } from "@/components/field";
import { PasswordField } from "@/components/password-field";
import { msg } from "@/lib/mensajes";

import type { EstadoCuenta } from "../acciones";

const CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validar(form: HTMLFormElement): Record<string, string> {
  const datos = new FormData(form);
  const errores: Record<string, string> = {};
  const correo = String(datos.get("email") ?? "").trim();
  if (!correo) errores.correo = msg("cuenta.falta_correo");
  else if (!CORREO.test(correo)) errores.correo = msg("cuenta.correo_invalido");
  const contrasena = String(datos.get("password") ?? "");
  if (!contrasena) errores.contrasena = msg("cuenta.falta_contrasena");
  return errores;
}

export function FormularioCuenta({
  accion,
  registro = false,
  siguiente,
  pendiente,
  clave,
  csrf,
}: {
  accion: (anterior: EstadoCuenta, datos: FormData) => Promise<EstadoCuenta>;
  registro?: boolean;
  siguiente?: string;
  pendiente?: string;
  clave?: string;
  csrf: string;
}) {
  const [estado, enviar, enviando] = useActionState(accion, { errores: {} } as EstadoCuenta);
  const [previos, setPrevios] = useState<Record<string, string>>({});
  // Los de la validación previa reemplazan a los del servidor ("" = el campo ya está bien).
  const errores: Record<string, string | undefined> = { ...estado.errores };
  for (const [campo, mensaje] of Object.entries(previos)) errores[campo] = mensaje || undefined;
  const consulta = siguiente ? `?next=${encodeURIComponent(siguiente)}` : "";

  if (estado.reanudar) {
    // [003] AC-14.4: el formulario pendiente se reabre con un POST explícito de la persona.
    return (
      <form
        method="post"
        action={estado.reanudar.ruta}
        className="flex flex-col gap-5 rounded-card border border-border bg-surface p-6 shadow-1"
        data-volver-formulario=""
      >
        <Callout variante="success" rol="status" texto={msg("cuenta.volver_formulario_texto")} />
        <input type="hidden" name="csrfmiddlewaretoken" value={csrf} />
        <input type="hidden" name="pendiente" value={estado.reanudar.pendiente} />
        <BotonEnviar className="w-full" textoTrabajando={msg("gral.cargando")}>
          {msg("cuenta.volver_formulario")}
        </BotonEnviar>
      </form>
    );
  }

  return (
    <form
      action={enviar}
      noValidate
      className="flex flex-col gap-5 rounded-card border border-border bg-surface p-6 shadow-1"
      onBlur={(e) => {
        // [003] AC-6.4, FR-033: el mensaje junto al campo al salir de él (Django lo repite). Un
        // campo vacío no se marca al salir: "Falta…" se informa al enviar (y así el formulario no
        // se mueve bajo el puntero justo cuando se pulsa "Ingresar").
        const elemento = e.target as unknown as HTMLInputElement;
        const nombre = elemento.getAttribute("name");
        if (nombre !== "email" && nombre !== "password") return;
        const campo = nombre === "email" ? "correo" : "contrasena";
        const encontrados = elemento.value ? validar(e.currentTarget) : {};
        setPrevios((p) => ({ ...p, [campo]: encontrados[campo] ?? "" }));
      }}
      onSubmit={(e: FormEvent<HTMLFormElement>) => {
        const encontrados = validar(e.currentTarget);
        setPrevios(encontrados);
        if (Object.keys(encontrados).length > 0) {
          e.preventDefault();
          const primero = encontrados.correo ? "email" : "password";
          const campo = e.currentTarget.querySelector<HTMLElement>(`[name="${primero}"]`);
          campo?.focus();
          window.setTimeout(() => campo?.focus(), 0); // después de dibujar los mensajes
        }
      }}
    >
      {estado.general && (
        <Callout variante="danger" rol="alert" texto={registro ? undefined : estado.general}>
          {registro && (
            <p className="min-w-0 flex-1">
              {estado.general} <Link href={`/ingresar/${consulta}`}>{msg("rot.ingresar")}</Link>
            </p>
          )}
        </Callout>
      )}
      {clave && <input type="hidden" name="clave_idempotencia" value={clave} />}
      {siguiente && <input type="hidden" name="next" value={siguiente} />}
      {pendiente && <input type="hidden" name="pendiente" value={pendiente} />}
      <Field id="id_email" etiqueta={msg("rot.correo")} error={errores.correo}>
        <input
          type="email"
          name="email"
          maxLength={254}
          autoComplete="email"
          spellCheck={false}
          defaultValue={estado.valores?.email ?? ""}
        />
      </Field>
      <PasswordField
        id="id_password"
        nombre="password"
        etiqueta={msg("rot.contrasena")}
        autocompletar={registro ? "new-password" : "current-password"}
        ayuda={registro ? msg("rot.contrasena_ayuda") : undefined}
        error={errores.contrasena}
      />
      <BotonEnviar
        className="w-full"
        trabajando={enviando}
        textoTrabajando={registro ? msg("form.trabajando_crear_cuenta") : msg("cuenta.ingresando")}
      >
        {registro ? msg("rot.crear_cuenta") : msg("rot.ingresar")}
      </BotonEnviar>
    </form>
  );
}
