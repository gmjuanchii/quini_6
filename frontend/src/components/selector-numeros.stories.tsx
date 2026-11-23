// [003] contracts/componentes.md: selector de números de la jugada (vacío, completo, con error).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { SelectorNumeros } from "./selector-numeros";

const meta = { title: "Componentes/SelectorNumeros", component: SelectorNumeros } satisfies Meta<
  typeof SelectorNumeros
>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Vacio: Historia = {};
export const Completo: Historia = { args: { iniciales: ["03", "08", "14", "21", "32", "40"] } };
export const ConError: Historia = { args: { errores: [msg("jugada.faltan", { n: 6 })] } };
