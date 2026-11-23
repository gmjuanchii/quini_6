"use client";

/**
 * Sin conexión al enviar ([003] FR-031, casos límite; quickstart #20): si el navegador está sin
 * conexión, el formulario no se envía y aparece el aviso `gral.sin_conexion` con "Reintentar", que
 * vuelve a enviar el mismo formulario (con la misma `clave_idempotencia`: no se duplica nada). El
 * mismo comportamiento y marcado (`data-sin-conexion`) que la validación previa de Django.
 */
import { useRef, useState, type FormEvent, type ReactNode } from "react";

import { Callout } from "@/components/callout";
import { Icono } from "@/components/icono";
import { boton } from "@/components/ui/variantes";
import { msg } from "@/lib/mensajes";

export function useSinConexion(): {
  formulario: React.RefObject<HTMLFormElement | null>;
  /** Para `onSubmit`: devuelve `true` si cortó el envío. */
  cortarSiSinConexion: (e: FormEvent<HTMLFormElement>) => boolean;
  aviso: ReactNode;
} {
  const formulario = useRef<HTMLFormElement>(null);
  const [sinConexion, setSinConexion] = useState(false);
  const cortarSiSinConexion = (e: FormEvent<HTMLFormElement>) => {
    if (typeof navigator === "undefined" || navigator.onLine) {
      setSinConexion(false);
      return false;
    }
    e.preventDefault();
    setSinConexion(true);
    return true;
  };
  const aviso = sinConexion ? (
    <Callout variante="danger" rol="alert" texto={msg("gral.sin_conexion")} data-sin-conexion="">
      <button
        type="button"
        className={boton({ variante: "secundario", tamano: "sm" })}
        onClick={() => {
          setSinConexion(false);
          formulario.current?.requestSubmit();
        }}
      >
        <Icono nombre="rotate-cw" />
        <span>{msg("gral.reintentar")}</span>
      </button>
    </Callout>
  ) : null;
  return { formulario, cortarSiSinConexion, aviso };
}
