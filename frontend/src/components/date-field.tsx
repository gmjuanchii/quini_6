"use client";

/**
 * DateField ([003] AC-4.1, AC-4.2, AC-4.5 a AC-4.7, FR-010, FR-013, R-07, contracts/componentes.md):
 * el mismo comportamiento que `templates/ui/_campo_fecha.html`.
 *
 * - El servidor (y la versión sin scripts) dibuja `<input type="date">` con `min`/`max` (envía
 *   `AAAA-MM-DD`).
 * - Al hidratar, el campo pasa a texto `dd/mm/aaaa` con barras automáticas ([002] D-27: nunca
 *   `showPicker()`), con el mismo ancho reservado, y el botón "Abrir calendario" muestra el
 *   calendario de shadcn/ui (`locale` es, semana desde el lunes, días fuera de rango deshabilitados),
 *   que se descarga recién al abrirlo (`calendario-diferido.tsx`, R-24).
 * - Dentro de un período, el botón abre el calendario de rango del `DateRangePicker`.
 */
import { useEffect, useRef, useState, type Ref } from "react";

import { Icono } from "@/components/icono";
import { cargarCalendario, PanelCalendarioDiferido } from "@/components/calendario-diferido";
import { boton } from "@/components/ui/variantes";
import { aDma, aIso, dateAIso, enmascarar, isoADate } from "@/lib/fechas";
import { useHidratado } from "@/lib/hidratado";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

export type DatosCampoFecha = {
  id: string;
  nombre: string;
  etiqueta: string;
  /** `AAAA-MM-DD` o lo que la persona escribió (si el servidor lo rechazó). */
  valor?: string;
  error?: string;
  ayuda?: string;
  min?: string;
  max?: string;
};

function unirRefs<T>(...refs: (Ref<T> | undefined)[]) {
  return (el: T | null) => {
    for (const r of refs) {
      if (typeof r === "function") r(el);
      else if (r) (r as { current: T | null }).current = el;
    }
  };
}

export function DateField({
  campo,
  entradaRef,
  alAbrirPeriodo,
  expandido,
  botonRef,
}: {
  campo: DatosCampoFecha;
  entradaRef?: Ref<HTMLInputElement>;
  /** Dentro de un período: el botón abre el calendario de rango (no uno propio). */
  alAbrirPeriodo?: () => void;
  expandido?: boolean;
  /** El botón "Abrir calendario" (el período lo necesita para su panel). */
  botonRef?: Ref<HTMLButtonElement>;
}) {
  const hidratado = useHidratado();
  const entrada = useRef<HTMLInputElement | null>(null);
  const fila = useRef<HTMLDivElement | null>(null);
  const botonCalendario = useRef<HTMLButtonElement | null>(null);
  const [abierto, setAbierto] = useState(false);
  // El panel se dibuja (y se descarga) recién a partir de la primera apertura (R-24).
  const [montado, setMontado] = useState(false);
  // Fecha elegida y mes visible del calendario, tomados del campo al abrirlo.
  const [calendario, setCalendario] = useState<{ seleccion?: Date; mes?: Date }>({});
  const iso = aIso(campo.valor) || (campo.valor ?? "");

  // Al pasar a texto, el valor del navegador (AAAA-MM-DD) se muestra como dd/mm/aaaa.
  useEffect(() => {
    if (hidratado && entrada.current) entrada.current.value = aDma(entrada.current.value);
  }, [hidratado]);

  const describe =
    [campo.ayuda && `${campo.id}_ayuda`, campo.error && `${campo.id}_error`]
      .filter(Boolean)
      .join(" ") || undefined;

  const elegir = (dia: Date | undefined) => {
    if (!dia || !entrada.current) return;
    entrada.current.value = aDma(dateAIso(dia));
    entrada.current.dispatchEvent(new Event("input", { bubbles: true }));
    setAbierto(false);
    entrada.current.focus();
  };

  const alternar = () => {
    if (!abierto) {
      const actual = aIso(entrada.current?.value);
      setCalendario({ seleccion: isoADate(actual), mes: isoADate(actual || campo.max) });
    }
    setMontado(true);
    setAbierto(!abierto);
  };

  const control = (
    <div ref={fila} className="flex max-w-full min-w-0 items-center gap-2">
      <input
        ref={unirRefs(entrada, entradaRef)}
        type={hidratado ? "text" : "date"}
        name={campo.nombre}
        id={campo.id}
        defaultValue={hidratado ? aDma(campo.valor) : iso}
        min={hidratado ? undefined : campo.min}
        max={hidratado ? undefined : campo.max}
        placeholder={hidratado ? "dd/mm/aaaa" : undefined}
        inputMode={hidratado ? "numeric" : undefined}
        autoComplete="off"
        className="control min-h-control !w-40 max-w-full min-w-0 shrink"
        aria-describedby={describe}
        aria-invalid={campo.error ? true : undefined}
        onInput={(e) => {
          const ev = e.nativeEvent as InputEvent;
          if (ev.inputType?.startsWith("delete")) return; // deja borrar las barras
          const el = e.currentTarget;
          if (el.type !== "text") return;
          const nuevo = enmascarar(el.value);
          if (nuevo !== el.value) el.value = nuevo;
        }}
      />
      <button
        ref={unirRefs(botonCalendario, botonRef)}
        type="button"
        className={cn("solo-con-scripts", boton({ variante: "secundario" }), "!px-2.5")}
        aria-haspopup="dialog"
        aria-expanded={alAbrirPeriodo ? (expandido ?? false) : abierto}
        onClick={alAbrirPeriodo ?? alternar}
        onPointerEnter={cargarCalendario}
        onFocus={cargarCalendario}
      >
        <Icono nombre="calendar" />
        <span className="visualmente-oculto">{msg("fecha.abrir_calendario")}</span>
      </button>
    </div>
  );

  return (
    <div
      className={cn(
        "campo flex max-w-full min-w-0 flex-col gap-1.5",
        campo.error && "campo--error",
      )}
      data-campo={campo.nombre}
      data-campo-fecha={campo.nombre}
    >
      <label htmlFor={campo.id} id={`${campo.id}_etiqueta`} className="font-medium">
        {campo.etiqueta}
      </label>
      {campo.ayuda && (
        <p className="ayuda text-sm text-muted-foreground" id={`${campo.id}_ayuda`}>
          {campo.ayuda}
        </p>
      )}
      {control}
      {!alAbrirPeriodo && montado && (
        <PanelCalendarioDiferido
          ancla={fila}
          disparadores={[botonCalendario]}
          abierto={abierto}
          alCambiar={setAbierto}
          alCerrarFoco={() => entrada.current?.focus()}
          etiquetadoPor={`${campo.id}_etiqueta`}
          className="w-auto rounded-card border border-border bg-surface p-3 shadow-2"
          calendario={{
            mode: "single",
            selected: calendario.seleccion,
            defaultMonth: calendario.mes,
            disabled: [
              ...(campo.min ? [{ before: isoADate(campo.min)! }] : []),
              ...(campo.max ? [{ after: isoADate(campo.max)! }] : []),
            ],
            onSelect: elegir,
          }}
        />
      )}
      <p
        className="error flex items-start gap-1.5 text-sm font-medium text-danger-text"
        id={`${campo.id}_error`}
        hidden={!campo.error}
      >
        <Icono nombre="circle-x" className="mt-0.5 size-4 shrink-0" />
        <span data-texto-error="">{campo.error}</span>
      </p>
    </div>
  );
}
