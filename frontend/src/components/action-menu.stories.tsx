// [003] contracts/componentes.md: ActionMenu (⋮) con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { ActionMenu } from "./action-menu";

const meta = {
  title: "Componentes/ActionMenu",
  component: ActionMenu,
  args: {
    nombre: msg("ext.acciones", { fecha_hora: "21/11/2026 12:15" }),
    opciones: [
      { texto: msg("ext.ver_detalle"), href: "#" },
      { texto: msg("ext.boton_descargar"), href: "#", icono: "download", externo: true },
      {
        texto: msg("ext.eliminar"),
        href: "#",
        icono: "trash-2",
        destructivo: true,
        confirmar: true,
      },
    ],
  },
} satisfies Meta<typeof ActionMenu>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Cerrado: Historia = {};
export const SinEliminar: Historia = {
  args: { opciones: [{ texto: msg("ext.ver_detalle"), href: "#" }] },
  name: "En curso (sin Eliminar)",
};
