// [003] R-14: cada historia se ve con los mismos estilos de la aplicación y en ambos temas.
import type { Decorator, Preview } from "@storybook/nextjs-vite";

import { msg } from "../src/lib/mensajes";

import "../src/app/globals.css";

const conTema: Decorator = (Historia, contexto) => {
  const tema = contexto.globals.tema as "claro" | "oscuro";
  document.documentElement.setAttribute("data-theme", tema);
  document.documentElement.lang = "es-AR";
  document.documentElement.classList.add("js");
  return (
    <div className="bg-background p-6 text-foreground">
      <Historia />
    </div>
  );
};

const preview: Preview = {
  globalTypes: {
    tema: {
      description: msg("tema.titulo"),
      toolbar: {
        title: msg("tema.titulo"),
        icon: "mirror",
        items: [
          { value: "claro", title: msg("tema.claro") },
          { value: "oscuro", title: msg("tema.oscuro") },
        ],
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: { tema: "claro" },
  decorators: [conTema],
  parameters: {
    a11y: { test: "error" },
    layout: "fullscreen",
  },
};

export default preview;
