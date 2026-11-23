/**
 * Clases del estado de un sorteo extraído y del resultado de cada fuente: las mismas que
 * `extracciones/consultas.py` (`_CLASE_ESTADO_SORTEO`, `_CLASE_RESULTADO`), estilos de
 * `ui/dominio.css`. Solo presentación: el texto del estado lo da Django.
 */
const CLASE_ESTADO_SORTEO: Record<string, string> = {
  RECUPERADO: "estado--con-premio",
  PARCIAL: "estado--pendiente",
  CON_INCONSISTENCIAS: "estado--revision",
  NO_RECUPERADO: "estado--revision",
};

export function claseEstadoSorteo(estado: string): string {
  return CLASE_ESTADO_SORTEO[estado] ?? "estado--revision";
}
