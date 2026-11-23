// [003] contracts/componentes.md: Field con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { Field } from "./field";

const meta = {
  title: "Componentes/Field",
  component: Field,
  args: {
    id: "historia",
    etiqueta: msg("ext.campo_inicio"),
    children: <input className="control min-h-control" />,
  },
} satisfies Meta<typeof Field>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Reposo: Historia = {};
export const ConAyuda: Historia = { args: { ayuda: "dd/mm/aaaa" } };
export const ConError: Historia = { args: { error: msg("fecha.falta_inicio") } };
