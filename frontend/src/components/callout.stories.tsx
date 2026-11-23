// Callout ([003] contracts/componentes.md, RN-09): las cuatro variantes con su icono.
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { Callout } from "./callout";

const meta = {
  title: "Componentes/Callout",
  component: Callout,
  args: { texto: msg("cuenta.volver_formulario_texto") },
} satisfies Meta<typeof Callout>;

export default meta;
type Historia = StoryObj<typeof meta>;

export const Informacion: Historia = { args: { variante: "info", texto: msg("est.leyenda") } };
export const Exito: Historia = { args: { variante: "success", rol: "status" } };
export const Advertencia: Historia = {
  args: { variante: "warning", texto: msg("cuenta.sesion_vencida") },
};
export const ConError: Historia = {
  args: { variante: "danger", rol: "alert", texto: msg("admin.sin_permiso") },
};
