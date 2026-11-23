/**
 * `true` en el navegador ya hidratado; `false` en el servidor y durante la hidratación (así el
 * primer render es idéntico al del servidor). Módulo propio y sin dependencias: lo usa la estructura
 * común (`SoloSinScripts`) y no debe arrastrar el campo de fecha ni su calendario a todas las
 * pantallas ([003] R-24).
 */
import { useSyncExternalStore } from "react";

const sinSuscripcion = () => () => {};

export function useHidratado(): boolean {
  return useSyncExternalStore(
    sinSuscripcion,
    () => true,
    () => false,
  );
}
