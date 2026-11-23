// [003] contracts/componentes.md: BackLink con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { BackLink } from "./back-link";

const meta = {
  title: "Componentes/BackLink",
  component: BackLink,
  args: { href: "#", texto: msg("nav.volver_extracciones") },
} satisfies Meta<typeof BackLink>;
export default meta;
export const Reposo: StoryObj<typeof meta> = {};
