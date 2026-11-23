// [003] contracts/componentes.md: EmptyState con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { EmptyState } from "./empty-state";

const meta = {
  title: "Componentes/EmptyState",
  component: EmptyState,
  args: {
    titulo: msg("vacio.extracciones.titulo"),
    explicacion: msg("vacio.extracciones.explicacion"),
    icono: "download",
  },
} satisfies Meta<typeof EmptyState>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const SinDatos: Historia = {};
export const SinDatosConAccion: Historia = {
  args: {
    titulo: msg("vacio.jugadas.titulo"),
    explicacion: msg("vacio.jugadas.explicacion"),
    icono: "ticket",
    accion: { texto: msg("vacio.jugadas.accion"), href: "#" },
  },
};
export const SinResultados: Historia = {
  args: {
    variante: "sin_resultados",
    titulo: msg("vacio.filtro.titulo"),
    explicacion: msg("vacio.filtro.explicacion", { filtro: msg("etiqueta.con_error") }),
    limpiarHref: "#",
    icono: undefined,
  },
};
