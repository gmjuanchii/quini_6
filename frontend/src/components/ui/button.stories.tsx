// Button ([003] contracts/componentes.md): variantes, tamaños y estado "trabajando" (FR-034).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { Button } from "./button";

const meta = {
  title: "Componentes/Button",
  component: Button,
  args: { children: msg("ext.boton_iniciar") },
} satisfies Meta<typeof Button>;

export default meta;
type Historia = StoryObj<typeof meta>;

export const Principal: Historia = { args: { variante: "principal" } };
export const Secundario: Historia = { args: { variante: "secundario", children: msg("ext.cancelar") } };
export const Destructivo: Historia = {
  args: { variante: "destructivo", icono: "trash-2", children: msg("ext.eliminar") },
};
export const Fantasma: Historia = { args: { variante: "fantasma", children: msg("nav.ingresar") } };
export const Pequeno: Historia = { args: { variante: "secundario", tamano: "sm", children: msg("tema.guardar") } };
export const Trabajando: Historia = {
  args: { trabajando: true, textoTrabajando: msg("ext.boton_iniciar_trabajando") },
};
export const Deshabilitado: Historia = { args: { disabled: true } };
