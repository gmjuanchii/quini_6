// [003] contracts/componentes.md: PasswordField (oculta, con ayuda, con error).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { PasswordField } from "./password-field";

const meta = {
  title: "Componentes/PasswordField",
  component: PasswordField,
  args: {
    id: "historia",
    nombre: "password",
    etiqueta: msg("rot.contrasena"),
    autocompletar: "current-password",
  },
} satisfies Meta<typeof PasswordField>;
export default meta;
type Historia = StoryObj<typeof meta>;

export const Oculta: Historia = {};
export const Nueva: Historia = {
  args: { autocompletar: "new-password", ayuda: msg("rot.contrasena_ayuda") },
};
export const ConError: Historia = { args: { error: msg("cuenta.falta_contrasena") } };
