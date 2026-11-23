// [003] contracts/componentes.md: Pagination con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { Pagination } from "./pagination";

const meta = {
  title: "Componentes/Pagination",
  component: Pagination,
  args: { pagina: 1, paginas: 3, parametros: { orden: "periodo" } },
} satisfies Meta<typeof Pagination>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Primera: Historia = {};
export const Intermedia: Historia = { args: { pagina: 2 } };
export const Ultima: Historia = { args: { pagina: 3 } };
export const UnaSola: Historia = { args: { paginas: 1 }, name: "Una sola página (no se muestra)" };
