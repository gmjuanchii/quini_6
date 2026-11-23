"use client";

/**
 * ProgressPanel ([003] AC-3.2, AC-3.3, AC-13.3, R-10, contracts/componentes.md): el mismo bloque que
 * `templates/extracciones/_avance.html`. Mientras la extracción está en curso, TanStack Query pide
 * `GET /api/v1/extracciones/{id}/avance/` cada 3 s; al terminar muestra el aviso final (Sonner),
 * deja de pedir y actualiza la página (listado y detalle). Sin scripts, el avance se actualiza al
 * recargar la página.
 */
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import { apiNavegador } from "@/api/navegador";
import type { components } from "@/api/esquema";
import { Icono } from "@/components/icono";
import { StatusBadge } from "@/components/status-badge";
import { mostrarAviso, type TipoAviso } from "@/components/toaster";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

export type Avance = components["schemas"]["AvanceDatos"];

const TIPO: Record<NonNullable<Avance["aviso_final"]>["tipo"], TipoAviso> = {
  success: "exito",
  warning: "advertencia",
  error: "error",
  info: "info",
};

export const INTERVALO_AVANCE_MS = 3000;

export function ProgressPanel({
  id,
  inicial,
  periodo,
}: {
  id: number;
  inicial: Avance;
  /** "Período consultado: dd/mm/aaaa al dd/mm/aaaa" (ya formateado en el servidor). */
  periodo: string;
}) {
  const router = useRouter();
  const { data } = useQuery({
    queryKey: ["extraccion", id, "avance"],
    queryFn: async () => {
      const { data: avance, error } = await apiNavegador.GET("/api/v1/extracciones/{id}/avance/", {
        params: { path: { id } },
      });
      if (!avance) throw error ?? new Error("Sin avance");
      return avance;
    },
    initialData: inicial,
    refetchInterval: (q) => (q.state.data?.en_curso ? INTERVALO_AVANCE_MS : false),
  });
  const avance = data ?? inicial;

  const estabaEnCurso = useRef(inicial.en_curso);
  useEffect(() => {
    if (estabaEnCurso.current && !avance.en_curso) {
      estabaEnCurso.current = false;
      if (avance.aviso_final) {
        mostrarAviso(
          { tipo: TIPO[avance.aviso_final.tipo], texto: avance.aviso_final.texto },
          msg("aviso.cerrar"),
        );
      }
      router.refresh();
    }
  }, [avance, router]);

  return (
    <div
      id="avance-extraccion"
      className={cn(
        "flex min-h-28 flex-col gap-2 rounded-card border-l-4 bg-surface p-4 shadow-1",
        avance.en_curso ? "border-primary" : "border-border",
      )}
      role="status"
      aria-live="polite"
      data-en-curso={avance.en_curso ? "1" : undefined}
    >
      <div className="flex flex-wrap items-center gap-3">
        <StatusBadge etiqueta={avance.etiqueta} id="avance" />
        <p className="font-semibold">
          {avance.en_curso ? msg("ext.en_curso") : (avance.aviso_final?.texto ?? "")}
        </p>
      </div>
      <p className="text-sm text-muted-foreground">{periodo}</p>
      {avance.en_curso ? (
        avance.identificando ? (
          <p className="flex items-center gap-2">
            <Icono nombre="loader-circle" className="size-4 shrink-0 motion-safe:animate-spin" />
            <span>{msg("ext.identificando")}</span>
          </p>
        ) : (
          <>
            <p id="avance-texto">
              {msg("ext.avance", { n: avance.procesados, m: avance.total ?? 0 })}
            </p>
            {avance.total ? (
              <progress
                className="barra-avance h-3 w-full accent-primary"
                value={avance.procesados}
                max={avance.total}
                aria-labelledby="avance-texto"
              />
            ) : null}
          </>
        )
      ) : (
        <p>
          <Link href={`/administracion/extracciones/${id}/`}>{msg("ext.ver_detalle")}</Link>
        </p>
      )}
    </div>
  );
}
