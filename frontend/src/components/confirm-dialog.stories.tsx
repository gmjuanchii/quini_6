// [003] contracts/componentes.md: ConfirmDialog con todos sus estados (Storybook, pedido § 7.3).
import type { Meta, StoryObj } from "@storybook/nextjs-vite";

import { msg } from "@/lib/mensajes";

import { Callout } from "./callout";
import { ConfirmDialog } from "./confirm-dialog";
import { Button } from "./ui/button";

const meta = {
  title: "Componentes/ConfirmDialog",
  component: ConfirmDialog,
  parameters: { nextjs: { appDirectory: true } },
  args: {
    titulo: msg("ext.eliminar_titulo"),
    texto: msg("ext.eliminar_confirmar", {
      fecha_hora: "21/11/2026 12:15",
      desde: "01/11/2026",
      hasta: "15/11/2026",
    }),
    children: (
      <>
        <Callout variante="warning" texto={msg("ext.eliminar_consecuencias")} />
        <div className="flex justify-end gap-3">
          <a href="#" data-cancelar="">
            {msg("ext.cancelar")}
          </a>
          <Button variante="destructivo" icono="trash-2">
            {msg("ext.eliminar")}
          </Button>
        </div>
      </>
    ),
  },
} satisfies Meta<typeof ConfirmDialog>;
export default meta;
export const Abierto: StoryObj<typeof meta> = {};
