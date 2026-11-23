// [003] contracts/componentes.md: DateRangePicker con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { DateRangePicker } from "./date-range-picker";

const meta = {
  title: "Componentes/DateRangePicker",
  component: DateRangePicker,
  parameters: { nextjs: { appDirectory: true } },
  args: {
    leyenda: msg("fecha.periodo"),
    desde: {
      id: "h_inicio",
      nombre: "inicio",
      etiqueta: msg("ext.campo_inicio"),
      max: "2026-11-22",
    },
    hasta: { id: "h_fin", nombre: "fin", etiqueta: msg("ext.campo_fin"), max: "2026-11-22" },
    atajos: [
      {
        clave: "anio_en_curso",
        texto: msg("ext.atajo_anio_en_curso"),
        desde: "2026-01-01",
        hasta: "2026-11-22",
      },
      {
        clave: "anio_anterior",
        texto: msg("ext.atajo_anio_anterior"),
        desde: "2025-01-01",
        hasta: "2025-12-31",
      },
    ],
    hrefAtajo: (c: string) => `?atajo=${c}`,
  },
} satisfies Meta<typeof DateRangePicker>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Vacio: Historia = {};
export const ConErrores: Historia = {
  args: {
    desde: {
      id: "e_inicio",
      nombre: "inicio",
      etiqueta: msg("ext.campo_inicio"),
      valor: "10/03/2026",
    },
    hasta: {
      id: "e_fin",
      nombre: "fin",
      etiqueta: msg("ext.campo_fin"),
      valor: "01/03/2026",
      error: msg("fecha.fin_anterior", { fecha: "10/03/2026" }),
    },
  },
};
