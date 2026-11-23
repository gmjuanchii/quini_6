// [003] R-07, R-23: el calendario del DateField y del DateRangePicker en ambas interfaces. Django usa
// Cally (<calendar-month>, con su contenido en el shadow DOM) y Next.js el calendario de shadcn/ui
// (react-day-picker, una tabla role="grid"). Los guiones preguntan lo mismo a las dos.
import type { Locator } from "@playwright/test";

async function esCally(dialogo: Locator): Promise<boolean> {
  return (await dialogo.locator("calendar-month").count()) > 0;
}

/** El mes visible: la grilla de días. */
export function mesDelCalendario(dialogo: Locator): Locator {
  return dialogo.locator("calendar-month").or(dialogo.getByRole("grid")).first();
}

/** Botón de un día por su nombre accesible (Cally: "3 de enero…"; react-day-picker: "viernes, 3 de
 * enero…"). */
export function diaDelCalendario(dialogo: Locator, dia: number, mes: string): Locator {
  return mesDelCalendario(dialogo).getByRole("button", { name: new RegExp(`(^|\\s)${dia} de ${mes}`) });
}

/** Nombre (o abreviatura) del primer día de la semana, en minúsculas. */
export async function primerDiaDeLaSemana(dialogo: Locator): Promise<string> {
  if (await esCally(dialogo)) {
    return dialogo.locator("calendar-month").evaluate((el) => {
      const th = el.shadowRoot!.querySelector("thead th, [part~='th']");
      return (th?.getAttribute("aria-label") || th?.textContent || "").trim().toLowerCase();
    });
  }
  // react-day-picker oculta la fila de los días de la semana a los lectores (la grilla ya nombra
  // cada día con su fecha completa): se lee del documento.
  return mesDelCalendario(dialogo).evaluate((grilla) => {
    const th = grilla.querySelector("thead th");
    return (th?.getAttribute("aria-label") || th?.textContent || "").trim().toLowerCase();
  });
}

/** Días del mes visible deshabilitados (sin contar los de los meses vecinos que se muestran). */
export async function diasDeshabilitadosDelMes(dialogo: Locator): Promise<number> {
  if (await esCally(dialogo)) {
    return dialogo.locator("calendar-month").evaluate(
      (el) =>
        Array.from(el.shadowRoot!.querySelectorAll("button[part~='day']")).filter(
          (b) => (b as HTMLButtonElement).disabled,
        ).length,
    );
  }
  return dialogo
    .getByRole("grid")
    .evaluate(
      (grilla) =>
        Array.from(grilla.querySelectorAll("td:not([data-outside]) button")).filter(
          (b) => (b as HTMLButtonElement).disabled,
        ).length,
    );
}
