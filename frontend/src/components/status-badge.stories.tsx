// [003] contracts/componentes.md: StatusBadge con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { StatusBadge, type Etiqueta } from "./status-badge";

const etiqueta = (valor: Etiqueta["valor"], variante: Etiqueta["variante"]): Etiqueta => ({
  valor,
  slug: valor.replace("_", "-"),
  texto: msg(`etiqueta.${valor}` as never),
  explicacion: msg(`etiqueta.${valor}.explicacion` as never),
  variante,
  requiere_revision: valor === "con_error" || valor === "con_advertencias",
});

const meta = {
  title: "Componentes/StatusBadge",
  component: StatusBadge,
  args: { id: "historia", etiqueta: etiqueta("en_curso", "info") },
} satisfies Meta<typeof StatusBadge>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const EnCurso: Historia = {};
export const Finalizada: Historia = { args: { etiqueta: etiqueta("finalizada", "success") } };
export const ConAdvertencias: Historia = {
  args: { etiqueta: etiqueta("con_advertencias", "warning") },
};
export const SinSorteos: Historia = { args: { etiqueta: etiqueta("sin_sorteos", "neutral") } };
export const ConError: Historia = { args: { etiqueta: etiqueta("con_error", "danger") } };
