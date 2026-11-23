"use client";

/**
 * Toast ([003] contracts/componentes.md, RN-09): Sonner con el mismo marcado y clases que
 * `templates/ui/_avisos.html`. Se cierran solos a los 6 s salvo los de error, que permanecen; todos
 * con el botón "Cerrar aviso". No roban el foco.
 *
 * Sonner se descarga recién con el primer aviso (`toaster-sonner.tsx`, R-24): hasta entonces los
 * avisos esperan en una cola y se muestran apenas la región está lista, en el mismo orden.
 */
import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";

export type TipoAviso = "exito" | "info" | "advertencia" | "error";
export type Aviso = { tipo: TipoAviso; texto: string };
export type AvisoPedido = { aviso: Aviso; etiquetaCerrar: string };

export const DURACION_AVISO_MS = 6000;

let mostrador: ((pedido: AvisoPedido) => void) | null = null;
const pendientes: AvisoPedido[] = [];
const alPedir = new Set<() => void>();

/** Lo llama la región de Sonner al estar lista: muestra lo pendiente y lo que llegue después. */
export function registrarMostrador(mostrar: (pedido: AvisoPedido) => void): () => void {
  mostrador = mostrar;
  for (const pedido of pendientes.splice(0)) mostrar(pedido);
  return () => {
    if (mostrador === mostrar) mostrador = null;
  };
}

export function mostrarAviso(aviso: Aviso, etiquetaCerrar: string): void {
  const pedido = { aviso, etiquetaCerrar };
  if (mostrador) {
    mostrador(pedido);
    return;
  }
  pendientes.push(pedido);
  for (const activar of alPedir) activar();
}

const ToasterSonner = dynamic(() => import("@/components/toaster-sonner"), { ssr: false });

export function Toaster({ etiquetaRegion }: { etiquetaRegion: string }) {
  const [activo, setActivo] = useState(false);
  useEffect(() => {
    const activar = () => setActivo(true);
    alPedir.add(activar);
    if (pendientes.length > 0) activar();
    return () => {
      alPedir.delete(activar);
    };
  }, []);
  return activo ? <ToasterSonner etiquetaRegion={etiquetaRegion} /> : null;
}

/** Muestra como Toast los avisos que la página recibió de Django (una sola vez por carga). */
export function AvisosIniciales({
  avisos,
  etiquetaCerrar,
}: {
  avisos: Aviso[];
  etiquetaCerrar: string;
}) {
  // Cada respuesta del servidor trae su propia lista: se muestra una vez (también tras navegar sin
  // recargar, cuando la estructura común se vuelve a dibujar con avisos nuevos).
  const mostrados = useRef<Aviso[] | null>(null);
  useEffect(() => {
    if (mostrados.current === avisos) return;
    mostrados.current = avisos;
    for (const aviso of avisos) mostrarAviso(aviso, etiquetaCerrar);
  }, [avisos, etiquetaCerrar]);
  return null;
}
