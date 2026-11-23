// [003] contracts/componentes.md: FrequencyChart con datos y con un número consultado.
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { FrequencyChart } from "./frequency-chart";

const numeros = Array.from({ length: 46 }, (_, n) => ({ numero: n, frecuencia: (n * 37) % 11 }));

const meta = {
  title: "Componentes/FrequencyChart",
  component: FrequencyChart,
  args: {
    numeros,
    consultado: null,
    modalidad: "Tradicional – Primer Sorteo",
    cantidadSorteos: 30,
  },
} satisfies Meta<typeof FrequencyChart>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const ConDatos: Historia = {};
export const ConNumeroConsultado: Historia = { args: { consultado: 14 } };
