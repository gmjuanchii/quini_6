"use client";

/**
 * Selector de los seis números de una jugada ([001] R-10, AC-4.2 a AC-4.6; [003] FR-041, T190): el
 * mismo comportamiento que `static/js/selector-numeros.js`. Sin scripts son las casillas comunes del
 * formulario (el servidor valida todo). Con scripts: contador "Faltan N números", no deja marcar más
 * de seis, y el campo "Número" + "Agregar" marca un número escrito (00 a 45, sin repetir). Textos del
 * catálogo (`jugada.faltan`, `jugada.exactamente_seis`, `jugada.fuera_de_rango`, `jugada.repetido`).
 */
import { useState, type KeyboardEvent } from "react";

import { useHidratado } from "@/lib/hidratado";
import { boton } from "@/components/ui/variantes";
import { dosDigitos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

export const MAXIMO = 6;
const OPCIONES = Array.from({ length: 46 }, (_, n) => dosDigitos(n));

/** Lo que pasa al agregar un número escrito: el número a marcar o el mensaje. */
export function agregarEscrito(
  texto: string,
  marcados: string[],
): { numero: string } | { mensaje: string } {
  const t = texto.trim();
  if (!/^\d{1,2}$/.test(t) || Number(t) > 45) return { mensaje: msg("jugada.fuera_de_rango") };
  const numero = dosDigitos(Number(t));
  if (marcados.includes(numero)) return { mensaje: msg("jugada.repetido", { nn: numero }) };
  if (marcados.length >= MAXIMO) return { mensaje: msg("jugada.exactamente_seis") };
  return { numero };
}

export function SelectorNumeros({
  iniciales = [],
  errores = [],
}: {
  iniciales?: string[];
  errores?: string[];
}) {
  const hidratado = useHidratado();
  const [marcados, setMarcados] = useState<string[]>(iniciales.map((n) => dosDigitos(Number(n))));
  const [escrito, setEscrito] = useState("");
  const [mensaje, setMensaje] = useState("");
  const faltan = MAXIMO - marcados.length;

  const alternar = (numero: string, marcar: boolean) => {
    if (marcar && marcados.length >= MAXIMO) {
      setMensaje(msg("jugada.exactamente_seis"));
      return;
    }
    setMensaje("");
    setMarcados((m) => (marcar ? [...m, numero] : m.filter((x) => x !== numero)));
  };

  const agregar = () => {
    const r = agregarEscrito(escrito, marcados);
    if ("mensaje" in r) {
      setMensaje(r.mensaje);
      return;
    }
    setMarcados((m) => [...m, r.numero]);
    setEscrito("");
    setMensaje("");
  };

  return (
    <fieldset
      className={cn("campo", errores.length > 0 && "campo--error")}
      id="selector-numeros"
      aria-describedby={errores.length > 0 ? "numeros_error" : undefined}
    >
      <legend>{msg("jugada.elegir_numeros")}</legend>
      <p className="ayuda" id="contador-numeros" aria-live="polite">
        {hidratado
          ? faltan > 0
            ? msg("jugada.faltan", { n: faltan })
            : msg("rot.seis_elegidos")
          : ""}
      </p>
      {errores.length > 0 && (
        <div className="error" id="numeros_error">
          {errores.map((e) => (
            <p key={e} className="error">
              {e}
            </p>
          ))}
        </div>
      )}
      <div className="grilla-numeros">
        {OPCIONES.map((n) => (
          <label key={n} htmlFor={`id_numeros_${Number(n)}`}>
            <input
              type="checkbox"
              name="numeros"
              value={n}
              id={`id_numeros_${Number(n)}`}
              checked={marcados.includes(n)}
              onChange={(e) => alternar(n, e.currentTarget.checked)}
            />
            <span>{n}</span>
          </label>
        ))}
      </div>
      <div className="mt-3 flex flex-wrap items-end gap-3">
        <div className="campo">
          <label htmlFor="id_numero_escrito">{msg("jugada.escribir_numero")}</label>
          <input
            type="text"
            id="id_numero_escrito"
            name="numero_escrito"
            inputMode="numeric"
            autoComplete="off"
            maxLength={4}
            value={escrito}
            onChange={(e) => setEscrito(e.currentTarget.value)}
            onKeyDown={(e: KeyboardEvent<HTMLInputElement>) => {
              if (e.key === "Enter") {
                e.preventDefault();
                agregar();
              }
            }}
          />
        </div>
        <button
          type="button"
          className={boton({ variante: "secundario" })}
          id="agregar-numero"
          hidden={!hidratado}
          onClick={agregar}
        >
          {msg("rot.agregar")}
        </button>
      </div>
      <p
        className="error"
        id="mensaje-selector"
        aria-live="polite"
        role={hidratado ? "status" : undefined}
      >
        {mensaje}
      </p>
    </fieldset>
  );
}
