"use client";

/**
 * PasswordField ([003] AC-6.2, AC-6.5, contracts/componentes.md): el mismo marcado que
 * `templates/ui/_campo_contrasena.html`. "Mostrar"/"Ocultar" con `aria-pressed` y el anuncio del
 * cambio en una región `aria-live`. Sin scripts el botón no se muestra y la contraseña queda oculta.
 */
import { useState } from "react";

import { Icono } from "@/components/icono";
import { boton } from "@/components/ui/variantes";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

export function PasswordField({
  id,
  nombre,
  etiqueta,
  autocompletar,
  ayuda,
  error,
}: {
  id: string;
  nombre: string;
  etiqueta: string;
  autocompletar: "current-password" | "new-password";
  ayuda?: string;
  error?: string;
}) {
  const [visible, setVisible] = useState(false);
  const [anuncio, setAnuncio] = useState("");
  const describe =
    [ayuda && `${id}_ayuda`, error && `${id}_error`].filter(Boolean).join(" ") || undefined;
  return (
    <div className={cn("campo flex flex-col gap-1.5", error && "campo--error")} data-campo={nombre}>
      <label htmlFor={id} className="font-medium">
        {etiqueta}
      </label>
      {ayuda && (
        <p className="ayuda text-sm text-muted-foreground" id={`${id}_ayuda`}>
          {ayuda}
        </p>
      )}
      <div className="flex items-center gap-2">
        <div className="min-w-0 flex-1">
          <input
            type={visible ? "text" : "password"}
            id={id}
            name={nombre}
            autoComplete={autocompletar}
            aria-describedby={describe}
            aria-invalid={error ? true : undefined}
          />
        </div>
        <button
          type="button"
          data-mostrar-contrasena=""
          className={cn("solo-con-scripts", boton({ variante: "secundario" }), "shrink-0 px-3")}
          aria-controls={id}
          aria-pressed={visible}
          onClick={() => {
            setVisible((v) => !v);
            setAnuncio(msg(visible ? "cuenta.contrasena_oculta" : "cuenta.contrasena_visible"));
          }}
        >
          <span className="flex items-center gap-2">
            <Icono nombre={visible ? "eye-off" : "eye"} />
            {msg(visible ? "cuenta.ocultar" : "cuenta.mostrar")}
          </span>
        </button>
      </div>
      <p className="visualmente-oculto" aria-live="polite">
        {anuncio}
      </p>
      <p
        className="error flex items-start gap-1.5 text-sm font-medium text-danger-text"
        id={`${id}_error`}
        hidden={!error}
      >
        <Icono nombre="circle-x" className="mt-0.5 size-4 shrink-0" />
        <span data-texto-error="">{error}</span>
      </p>
    </div>
  );
}
