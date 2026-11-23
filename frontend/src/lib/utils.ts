import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Une clases de Tailwind sin duplicados ni conflictos (shadcn/ui). */
export function cn(...entradas: ClassValue[]): string {
  return twMerge(clsx(entradas));
}
