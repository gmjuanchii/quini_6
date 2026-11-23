/**
 * Estado de un formulario enviado con una Server Action ([003] R-11, R-12, CHK011). Separado de
 * `lib/acciones.ts` (solo servidor) para que lo usen los componentes de cliente.
 */
export type EstadoFormulario = {
  /** Mensaje por nombre de campo (`aria-describedby` del Field). */
  errores: Record<string, string>;
  /** Mensaje general (`detail` del problema). */
  general?: string;
  /** FR-032: la sesión venció; se ofrece "Ingresar" con lo escrito firmado por Django. */
  sesionVencida?: { pendiente: string | null; siguiente: string };
  /** 409 con el elemento que impide la acción (p. ej. [003] RN-03: la extracción idéntica). */
  existente?: { id: number; url: string };
  /** Lo enviado, para volver a mostrarlo sin scripts (el formulario se dibuja en el servidor). */
  valores?: Record<string, string>;
};

export const ESTADO_INICIAL: EstadoFormulario = { errores: {} };
