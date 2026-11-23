// [003] contracts/componentes.md: DateField con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { DateField } from "./date-field";

const campo = {
  id: "historia",
  nombre: "fecha",
  etiqueta: msg("ext.campo_inicio"),
  max: "2026-11-22",
};
const meta = {
  title: "Componentes/DateField",
  component: DateField,
  args: { campo },
} satisfies Meta<typeof DateField>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Vacio: Historia = {};
export const Completo: Historia = { args: { campo: { ...campo, valor: "2025-01-15" } } };
export const ConError: Historia = {
  args: {
    campo: {
      ...campo,
      valor: "31/02/2025",
      error: msg("fecha.inexistente", { fecha: "31/02/2025" }),
    },
  },
};
