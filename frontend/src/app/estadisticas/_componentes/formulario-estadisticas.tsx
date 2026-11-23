"use client";

/**
 * Filtros de Estadísticas ([001] US6; [003] AC-7.1 a AC-7.4, AC-7.6, FR-010 a FR-013, FR-033): el
 * mismo formulario GET que `templates/estadisticas/index.html` (funciona sin scripts). Con scripts,
 * valida antes de enviar con los mismos textos del catálogo (`validarPeriodo`): fechas, "Hasta" no anterior a
 * "Desde" y número entre 00 y 45; si hay errores no envía, los muestra junto a cada campo, resume
 * cuántos son y lleva el foco al primero. Django repite toda la validación.
 */
import { useRef, useState, type FormEvent } from "react";

import { Callout } from "@/components/callout";
import { DateRangePicker, type AtajoPeriodo } from "@/components/date-range-picker";
import { Icono } from "@/components/icono";
import { Button } from "@/components/ui/button";
import { validarPeriodo } from "@/lib/esquemas/periodo";
import { analizarFecha } from "@/lib/fechas";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

type Errores = Partial<Record<"desde" | "hasta" | "numero", string>>;

/** [003] AC-7.6: número de 00 a 45 (mismo texto que la regla `rango_00_45` de Django). */
export function errorDeNumero(valor: string): string | undefined {
  const texto = valor.trim();
  if (!texto) return undefined;
  return /^\d{1,2}$/.test(texto) && Number(texto) <= 45 ? undefined : msg("jugada.fuera_de_rango");
}

function validar(form: HTMLFormElement): Errores {
  const datos = new FormData(form);
  const desde = String(datos.get("desde") ?? "");
  const hasta = String(datos.get("hasta") ?? "");
  const errores: Errores = {};
  // En Estadísticas el período es opcional: solo se valida lo escrito.
  for (const [campo, valor] of [
    ["desde", desde],
    ["hasta", hasta],
  ] as const) {
    if (valor && analizarFecha(valor).estado !== "valida") {
      const e = validarPeriodo({ inicio: valor, fin: valor }, { finFutura: false });
      errores[campo] = e.inicio ?? e.fin;
    }
  }
  if (!errores.desde && !errores.hasta && desde && hasta) {
    errores.hasta = validarPeriodo({ inicio: desde, fin: hasta }, { finFutura: false }).fin;
  }
  const numero = errorDeNumero(String(datos.get("numero") ?? ""));
  if (numero) errores.numero = numero;
  return Object.fromEntries(Object.entries(errores).filter(([, v]) => v)) as Errores;
}

export function FormularioEstadisticas({
  modalidades,
  modalidad,
  desde,
  hasta,
  numero,
  errores: erroresServidor,
  atajos,
  hrefAtajo,
  ocultos,
}: {
  modalidades: { valor: string; nombre: string }[];
  modalidad: string;
  desde: string;
  hasta: string;
  numero: string;
  errores: Errores;
  atajos: AtajoPeriodo[];
  hrefAtajo: Record<string, string>;
  ocultos: Record<string, string>;
}) {
  const formulario = useRef<HTMLFormElement>(null);
  const [errores, setErrores] = useState<Errores>(erroresServidor);
  const [cantidad, setCantidad] = useState(0);
  const [enviando, setEnviando] = useState(false);

  const alEnviar = (e: FormEvent<HTMLFormElement>) => {
    const encontrados = validar(e.currentTarget);
    const n = Object.keys(encontrados).length;
    if (n === 0) {
      setEnviando(true);
      return; // GET común: Django y la página repiten la consulta
    }
    e.preventDefault();
    setErrores(encontrados);
    setCantidad(n);
    const primero = (["desde", "hasta", "numero"] as const).find((c) => encontrados[c]);
    e.currentTarget.querySelector<HTMLElement>(`[name="${primero}"]`)?.focus();
  };

  const alSalir = (campo: keyof Errores) => {
    if (!formulario.current) return;
    const todos = validar(formulario.current);
    setErrores((actuales) => ({ ...actuales, [campo]: todos[campo] }));
  };

  return (
    <form
      ref={formulario}
      method="get"
      action="/estadisticas/"
      noValidate
      onSubmit={alEnviar}
      onBlur={(e) => {
        const nombre = (e.target as HTMLElement).getAttribute("name");
        if (nombre === "desde" || nombre === "hasta" || nombre === "numero") alSalir(nombre);
      }}
      className="flex flex-col gap-5 rounded-card border border-border bg-surface p-4 shadow-1 sm:p-6"
    >
      {cantidad > 0 && (
        <Callout variante="danger" rol="alert" texto={msg("form.no_avanza", { n: cantidad })} />
      )}
      <div className="flex flex-col gap-4 md:flex-row md:flex-wrap md:items-start md:gap-x-6">
        <div className="campo flex min-w-0 flex-col gap-1.5">
          <label htmlFor="est-modalidad" className="font-medium">
            {msg("rot.modalidad")}
          </label>
          <select
            id="est-modalidad"
            name="modalidad"
            defaultValue={modalidad}
            className="min-h-control !w-auto max-w-full"
          >
            {modalidades.map((m) => (
              <option key={m.valor} value={m.valor}>
                {m.nombre}
              </option>
            ))}
          </select>
        </div>
        <div className="min-w-0">
          <DateRangePicker
            leyenda={msg("fecha.periodo")}
            desde={{
              id: "est-desde",
              nombre: "desde",
              etiqueta: msg("rot.desde"),
              valor: desde,
              error: errores.desde,
            }}
            hasta={{
              id: "est-hasta",
              nombre: "hasta",
              etiqueta: msg("rot.hasta"),
              valor: hasta,
              error: errores.hasta,
            }}
            atajos={atajos}
            hrefAtajo={(c) => hrefAtajo[c] ?? `?atajo=${c}`}
          />
        </div>
      </div>
      <p className="m-0 text-sm text-muted-foreground">{msg("est.ayuda_periodo")}</p>

      {/* AC-7.4: "Consultar un número", separado de los filtros del período. */}
      <fieldset
        className="m-0 min-w-0 border-0 border-t border-border p-0 pt-5"
        data-consultar-numero=""
      >
        <legend className="float-left mb-3 w-full p-0 pt-5 text-lg font-semibold">
          {msg("est.consultar_numero")}
        </legend>
        <div
          className={cn("campo clear-left flex flex-col gap-1.5", errores.numero && "campo--error")}
          data-campo="numero"
        >
          <label htmlFor="est-numero" className="font-medium">
            {msg("rot.numero")}
          </label>
          <div className="flex flex-wrap items-center gap-3">
            <input
              type="text"
              id="est-numero"
              name="numero"
              inputMode="numeric"
              maxLength={2}
              autoComplete="off"
              defaultValue={numero}
              className="cifras min-h-control !w-[7ch]"
              aria-describedby={`est-numero_ayuda${errores.numero ? " est-numero_error" : ""}`}
              aria-invalid={errores.numero ? true : undefined}
            />
            <Button
              type="submit"
              icono="chart-column"
              trabajando={enviando}
              textoTrabajando={msg("form.trabajando_consultar")}
            >
              {msg("rot.consultar")}
            </Button>
          </div>
          <p className="ayuda m-0 text-sm text-muted-foreground" id="est-numero_ayuda">
            {msg("est.numero_ayuda")}
          </p>
          <p
            className="error m-0 flex items-start gap-1.5 text-sm font-medium text-danger-text"
            id="est-numero_error"
            hidden={!errores.numero}
          >
            <Icono nombre="circle-x" className="mt-0.5 size-4 shrink-0" />
            <span data-texto-error="">{errores.numero}</span>
          </p>
        </div>
      </fieldset>
      {Object.entries(ocultos).map(([nombre, valor]) => (
        <input key={nombre} type="hidden" name={nombre} value={valor} />
      ))}
    </form>
  );
}
