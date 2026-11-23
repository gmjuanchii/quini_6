"use client";

/**
 * El `Calendar` de shadcn/ui con el idioma y la semana de Argentina ([003] R-07: `locale` es, semana
 * desde el lunes). Se importa solo desde `calendario-diferido.tsx` (carga bajo demanda, R-24).
 */
import type { ComponentProps } from "react";
import { es } from "react-day-picker/locale";

import { Calendar } from "@/components/ui/calendar";

export default function CalendarioEs(props: ComponentProps<typeof Calendar>) {
  return <Calendar locale={es} weekStartsOn={1} {...props} />;
}
