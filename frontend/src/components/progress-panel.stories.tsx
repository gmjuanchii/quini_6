// [003] contracts/componentes.md: ProgressPanel con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { ProgressPanel, type Avance } from "./progress-panel";

const etiqueta = {
  valor: "en_curso",
  slug: "en-curso",
  texto: msg("etiqueta.en_curso"),
  explicacion: msg("etiqueta.en_curso.explicacion"),
  variante: "info",
  requiere_revision: false,
} as const;
const base: Avance = {
  en_curso: true,
  identificando: true,
  procesados: 0,
  total: null,
  etiqueta,
  aviso_final: null,
};

const meta = {
  title: "Componentes/ProgressPanel",
  component: ProgressPanel,
  parameters: { nextjs: { appDirectory: true } },
  args: {
    id: 1,
    inicial: base,
    periodo: msg("rot.periodo_consultado_valor", { desde: "01/11/2026", hasta: "15/11/2026" }),
  },
} satisfies Meta<typeof ProgressPanel>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Identificando: Historia = {};
export const ConTotal: Historia = {
  args: { inicial: { ...base, identificando: false, procesados: 3, total: 8 } },
};
export const Terminada: Historia = {
  args: {
    inicial: {
      ...base,
      en_curso: false,
      identificando: false,
      procesados: 8,
      total: 8,
      etiqueta: {
        ...etiqueta,
        valor: "finalizada",
        slug: "finalizada",
        texto: msg("etiqueta.finalizada"),
        variante: "success",
      },
      aviso_final: { tipo: "success", texto: msg("ext.termino_finalizada"), enlace: "#" },
    },
  },
};
