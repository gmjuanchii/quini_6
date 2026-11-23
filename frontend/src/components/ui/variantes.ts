/**
 * Variantes de los componentes a partir de `ui/variantes.json` ([003] R-04): las mismas clases que
 * el filtro `{% clases %}` de Django. Nunca se escriben aquí clases de variante a mano.
 */
import { cva, type VariantProps } from "class-variance-authority";

import definiciones from "../../../../ui/variantes.json";

type Definicion = {
  base: string;
  variantes: Record<string, string>;
  tamanos: Record<string, string>;
};

function definicion<K extends Exclude<keyof typeof definiciones, "$comentario">>(componente: K) {
  return definiciones[componente] as unknown as Definicion;
}

const d = {
  boton: definicion("boton"),
  insignia: definicion("insignia"),
  aviso: definicion("aviso"),
  toast: definicion("toast"),
  vacio: definicion("vacio"),
};

export const boton = cva(d.boton.base, {
  variants: {
    variante: d.boton.variantes as Record<
      "principal" | "secundario" | "destructivo" | "fantasma" | "enlace",
      string
    >,
    tamano: d.boton.tamanos as Record<"md" | "sm", string>,
  },
  defaultVariants: { variante: "principal", tamano: "md" },
});

export const insignia = cva(d.insignia.base, {
  variants: {
    variante: d.insignia.variantes as Record<
      "info" | "success" | "warning" | "danger" | "neutral",
      string
    >,
  },
  defaultVariants: { variante: "neutral" },
});

export const aviso = cva(d.aviso.base, {
  variants: {
    variante: d.aviso.variantes as Record<"info" | "success" | "warning" | "danger", string>,
  },
  defaultVariants: { variante: "info" },
});

export const toast = cva(d.toast.base, {
  variants: {
    variante: d.toast.variantes as Record<"success" | "info" | "warning" | "error", string>,
  },
  defaultVariants: { variante: "info" },
});

export const vacio = cva(d.vacio.base, {
  variants: {
    variante: d.vacio.variantes as Record<"sin_datos" | "sin_resultados", string>,
  },
  defaultVariants: { variante: "sin_datos" },
});

export type VariantesBoton = VariantProps<typeof boton>;
export type VariantesAviso = VariantProps<typeof aviso>;
