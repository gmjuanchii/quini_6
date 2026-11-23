// [003] contracts/componentes.md: DataTable con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { encabezados } from "@/lib/tablas";

import { DataTable } from "./data-table";

const columnas = [
  { id: "fecha", texto: msg("ext.col_fecha"), ordenable: true },
  { id: "ejecutada_por", texto: msg("rot.ejecutada_por") },
  { id: "periodo", texto: msg("rot.periodo"), ordenable: true },
];
const filas = Array.from({ length: 3 }, (_, i) => ({
  clave: String(i),
  enlace: true,
  celdas: {
    fecha: `2${i}/11/2026 12:15`,
    ejecutada_por: "admin@quini6.local",
    periodo: "01/11/2026 al 15/11/2026",
  },
}));

const meta = {
  title: "Componentes/DataTable",
  component: DataTable,
  args: { titulo: msg("ext.anteriores"), encabezados: encabezados({}, columnas, "-fecha"), filas },
} satisfies Meta<typeof DataTable>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const ConDatos: Historia = {};
export const OrdenAscendente: Historia = {
  args: { encabezados: encabezados({}, columnas, "periodo") },
};
export const Vacia: Historia = { args: { filas: [] } };
