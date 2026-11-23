"use client";

/**
 * Formulario "Iniciar extracción" ([002] AC-1.1 a AC-1.6; [003] FR-010 a FR-013, FR-031 a FR-034,
 * RN-03, RN-04): DateRangePicker con dos atajos, validación previa al salir de cada campo y al
 * enviar (`validarPeriodo`, con los textos del catálogo; como el formulario de Estadísticas, sin
 * React Hook Form, R-24) y envío con una Server Action (`useActionState`). Sin scripts, es un
 * formulario común que la Server Action procesa igual y la página vuelve a mostrar con los mensajes
 * de Django por campo.
 */
import Link from "next/link";
import { startTransition, useActionState, useState } from "react";

import { BotonEnviar } from "@/components/boton-enviar";
import { Callout } from "@/components/callout";
import { DateRangePicker, type AtajoPeriodo } from "@/components/date-range-picker";
import { SesionVencida } from "@/components/sesion-vencida";
import { useSinConexion } from "@/components/sin-conexion";
import { ESTADO_INICIAL } from "@/lib/acciones-estado";
import { validarPeriodo, type ErroresPeriodo, type Periodo } from "@/lib/esquemas/periodo";
import { msg } from "@/lib/mensajes";

import { iniciarExtraccion } from "../acciones";

export function FormularioInicio({
  atajos,
  inicial,
  max,
  clave,
  csrf,
  hrefAtajo,
  siguiente,
}: {
  atajos: AtajoPeriodo[];
  /** Valores iniciales (AAAA-MM-DD): de `?atajo=` o del formulario reanudado. */
  inicial: { inicio: string; fin: string };
  /** Hoy en Buenos Aires (AAAA-MM-DD): el calendario no ofrece días futuros. */
  max: string;
  /** `clave_idempotencia` del formulario mostrado (R-11). */
  clave: string;
  csrf: string;
  hrefAtajo: Record<string, string>;
  siguiente: string;
}) {
  const [estado, accion, enviando] = useActionState(iniciarExtraccion, ESTADO_INICIAL);
  const { formulario, cortarSiSinConexion, aviso } = useSinConexion();
  // FR-033: al enviar con errores, cuántos campos los tienen (el foco va al primero).
  const [conErrores, setConErrores] = useState(0);
  const valores = estado.valores ?? inicial;
  const [errores, setErrores] = useState<ErroresPeriodo>({});

  const leer = (): Periodo => {
    const datos = new FormData(formulario.current!);
    return { inicio: String(datos.get("inicio") ?? ""), fin: String(datos.get("fin") ?? "") };
  };
  /** Al salir de un campo, solo ese campo (como `mode: "onBlur"`). */
  const validarCampo = (campo: keyof Periodo) => {
    if (!formulario.current) return;
    const todos = validarPeriodo(leer(), { max });
    setErrores((actuales) => ({ ...actuales, [campo]: todos[campo] }));
  };

  // Los mensajes del servidor tienen prioridad: son los que valen (Django valida todo).
  const error = (campo: "inicio" | "fin") => estado.errores[campo] ?? errores[campo] ?? undefined;
  const general = estado.errores[""] ?? (estado.existente ? estado.general : undefined);

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
        action={accion}
        noValidate
        className="flex flex-col gap-4"
        onSubmit={(e) => {
          if (cortarSiSinConexion(e)) return;
          e.preventDefault();
          const encontrados = validarPeriodo(leer(), { max });
          const campos = (["inicio", "fin"] as const).filter((c) => encontrados[c]);
          setErrores(encontrados);
          setConErrores(campos.length);
          if (campos.length > 0) {
            // FR-033: el foco va al primer campo con error.
            formulario.current?.querySelector<HTMLElement>(`[name="${campos[0]}"]`)?.focus();
            return;
          }
          const datos = new FormData(formulario.current!);
          datos.set("_con_scripts", "1"); // AC-3.1: el avance se ve en el listado
          startTransition(() => accion(datos));
        }}
        onBlur={(e) => {
          const nombre = (e.target as HTMLElement).getAttribute("name");
          if (nombre === "inicio" || nombre === "fin") validarCampo(nombre);
        }}
      >
        <input type="hidden" name="clave_idempotencia" value={clave} />
        {aviso}
        {conErrores > 0 && (
          <Callout variante="danger" rol="alert" texto={msg("form.no_avanza", { n: conErrores })} />
        )}
        {general && (
          <Callout variante={estado.existente ? "warning" : "danger"} rol="alert" texto={general}>
            {estado.existente && (
              <p className="mt-2">
                <Link href={estado.existente.url}>{msg("ext.ver_existente")}</Link>
              </p>
            )}
          </Callout>
        )}
        <DateRangePicker
          leyenda={msg("fecha.periodo")}
          desde={{
            id: "id_inicio",
            nombre: "inicio",
            etiqueta: msg("ext.campo_inicio"),
            valor: valores.inicio,
            max,
            error: error("inicio"),
          }}
          hasta={{
            id: "id_fin",
            nombre: "fin",
            etiqueta: msg("ext.campo_fin"),
            valor: valores.fin,
            max,
            error: error("fin"),
          }}
          atajos={atajos}
          hrefAtajo={(c) => hrefAtajo[c] ?? `?atajo=${c}`}
          alCompletar={() => setErrores(validarPeriodo(leer(), { max }))}
        />
        <div>
          <BotonEnviar trabajando={enviando} textoTrabajando={msg("ext.boton_iniciar_trabajando")}>
            {msg("ext.boton_iniciar")}
          </BotonEnviar>
        </div>
      </form>
    </>
  );
}
