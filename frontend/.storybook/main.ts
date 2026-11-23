// [003] pedido § 7.3, contracts/componentes.md § 3: catálogo de componentes con todos sus estados y
// revisión de accesibilidad (addon a11y, axe) en ambos temas.
import { fileURLToPath } from "node:url";

import type { StorybookConfig } from "@storybook/nextjs-vite";

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(ts|tsx)"],
  addons: ["@storybook/addon-a11y"],
  framework: { name: "@storybook/nextjs-vite", options: {} },
  core: { disableTelemetry: true },
  viteFinal: async (vite) => {
    vite.resolve ??= {};
    vite.resolve.alias = {
      ...(vite.resolve.alias as Record<string, string>),
      "@contratos": fileURLToPath(new URL("../../contratos", import.meta.url)),
    };
    return vite;
  },
};

export default config;
