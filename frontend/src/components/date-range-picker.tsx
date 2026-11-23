"use client";

/**
 * DateRangePicker ([003] AC-4.3, AC-4.4, FR-011, RN-04, R-07, contracts/componentes.md): igual que
 * `templates/ui/_periodo.html`. Dos DateField con etiqueta propia y un único calendario de rango
 * (`mode="range"`); los atajos son enlaces `?atajo=<clave>` que sin scripts recargan el formulario
 * con las fechas precargadas por el servidor y, con scripts, completan ambos campos sin navegar
 * (se pueden modificar antes de enviar).
 */
import Link from "next/link";
import { useRef, useState } from "react";
import type { DateRange } from "react-day-picker";

import { DateField, type DatosCampoFecha } from "@/components/date-field";
import { PanelCalendarioDiferido } from "@/components/calendario-diferido";
import { boton } from "@/components/ui/variantes";
import { aDma, aIso, dateAIso, isoADate } from "@/lib/fechas";

export type AtajoPeriodo = { clave: string; texto: string; desde: string; hasta: string };

export function DateRangePicker({
  leyenda,
  desde,
  hasta,
  atajos = [],
  hrefAtajo,
  alCompletar,
}: {
  leyenda: string;
  desde: DatosCampoFecha;
  hasta: DatosCampoFecha;
  atajos?: AtajoPeriodo[];
  /** Dirección del atajo sin scripts (conserva los demás parámetros de la página). */
  hrefAtajo: (clave: string) => string;
  /** Avisa los valores nuevos (dd/mm/aaaa) para validarlos. */
  alCompletar?: (desde: string, hasta: string) => void;
}) {
  const entradaDesde = useRef<HTMLInputElement>(null);
  const entradaHasta = useRef<HTMLInputElement>(null);
  const origen = useRef<HTMLInputElement | null>(null);
  const fila = useRef<HTMLDivElement | null>(null);
  const botonDesde = useRef<HTMLButtonElement | null>(null);
  const botonHasta = useRef<HTMLButtonElement | null>(null);
  const [abierto, setAbierto] = useState(false);
  // El panel se dibuja (y se descarga) recién a partir de la primera apertura (R-24).
  const [montado, setMontado] = useState(false);
  const [desdeQue, setDesdeQue] = useState<"desde" | "hasta" | null>(null);
  const [inicioElegido, setInicioElegido] = useState<Date | undefined>();
  // Rango de los campos y mes visible, tomados al abrir el calendario.
  const [rangoCampos, setRangoCampos] = useState<DateRange | undefined>();
  const [mes, setMes] = useState<Date | undefined>();

  const completar = (isoDesde: string, isoHasta: string) => {
    if (!entradaDesde.current || !entradaHasta.current) return;
    entradaDesde.current.value = aDma(isoDesde);
    entradaHasta.current.value = aDma(isoHasta);
    for (const el of [entradaDesde.current, entradaHasta.current]) {
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
    alCompletar?.(entradaDesde.current.value, entradaHasta.current.value);
  };

  const max = hasta.max ?? desde.max;
  const min = desde.min ?? hasta.min;

  const abrir = (cual: "desde" | "hasta") => {
    // El mismo botón otra vez: cierra (como el botón de un campo suelto).
    if (abierto && desdeQue === cual) {
      setAbierto(false);
      setDesdeQue(null);
      return;
    }
    const entrada = cual === "desde" ? entradaDesde.current : entradaHasta.current;
    origen.current = entrada;
    const a = isoADate(aIso(entradaDesde.current?.value));
    const b = isoADate(aIso(entradaHasta.current?.value));
    setRangoCampos(a && b && a <= b ? { from: a, to: b } : undefined);
    setMes(isoADate(aIso(entrada?.value) || aIso(entradaDesde.current?.value) || max));
    setInicioElegido(undefined);
    setDesdeQue(cual);
    setMontado(true);
    setAbierto(true);
  };

  const rangoActual: DateRange | undefined = inicioElegido
    ? { from: inicioElegido, to: undefined }
    : rangoCampos;

  const elegir = (dia: Date) => {
    if (!inicioElegido) {
      setInicioElegido(dia);
      return;
    }
    const [a, b] = dia < inicioElegido ? [dia, inicioElegido] : [inicioElegido, dia];
    completar(dateAIso(a), dateAIso(b));
    setInicioElegido(undefined);
    origen.current = entradaHasta.current;
    setDesdeQue(null);
    setAbierto(false);
  };

  return (
    <fieldset className="periodo m-0 flex min-w-0 flex-col gap-3 border-0 p-0" data-periodo="">
      <legend className="visualmente-oculto" id={`${desde.id}_periodo`}>
        {leyenda}
      </legend>
      <div ref={fila} className="flex flex-wrap items-start gap-x-4 gap-y-3">
        <DateField
          campo={desde}
          entradaRef={entradaDesde}
          botonRef={botonDesde}
          alAbrirPeriodo={() => abrir("desde")}
          expandido={abierto && desdeQue === "desde"}
        />
        <DateField
          campo={hasta}
          entradaRef={entradaHasta}
          botonRef={botonHasta}
          alAbrirPeriodo={() => abrir("hasta")}
          expandido={abierto && desdeQue === "hasta"}
        />
      </div>
      {montado && (
        <PanelCalendarioDiferido
          ancla={fila}
          disparadores={[botonDesde, botonHasta]}
          abierto={abierto}
          alCambiar={(a) => {
            setAbierto(a);
            if (!a) setDesdeQue(null);
          }}
          alCerrarFoco={() => origen.current?.focus()}
          etiquetadoPor={`${desde.id}_periodo`}
          className="calendario-popover w-auto rounded-card border border-border bg-surface p-3 shadow-2"
          calendario={{
            mode: "range",
            selected: rangoActual,
            defaultMonth: mes,
            disabled: [
              ...(min ? [{ before: isoADate(min)! }] : []),
              ...(max ? [{ after: isoADate(max)! }] : []),
            ],
            onSelect: (_rango: DateRange | undefined, dia: Date) => elegir(dia),
          }}
        />
      )}
      {atajos.length > 0 && (
        <ul className="flex flex-wrap gap-2" role="list">
          {atajos.map((a) => (
            <li key={a.clave}>
              <Link
                href={hrefAtajo(a.clave)}
                className={boton({ variante: "secundario", tamano: "sm" })}
                data-atajo={a.clave}
                data-desde={a.desde}
                data-hasta={a.hasta}
                scroll={false}
                onClick={(e) => {
                  // AC-4.4: completa las dos fechas sin navegar y se pueden modificar.
                  e.preventDefault();
                  completar(a.desde, a.hasta);
                  entradaDesde.current?.focus();
                }}
              >
                {a.texto}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </fieldset>
  );
}
