/**
 * Tipos de los formularios de Administración de sorteos ([003] contracts/api.md, T207): la
 * descripción de cada formulario de Django (`FormularioDTO`) y el estado que devuelve la Server
 * Action al enviarlo.
 */
import type { components } from "@/api/esquema";

export type Formulario = components["schemas"]["FormularioDTO"];
export type CampoFormulario = components["schemas"]["CampoFormulario"];

export type EstadoAdmin = {
  /** Errores generales (los `non_field_errors` y los de los servicios de Django). */
  generales: string[];
  /** El formulario con lo enviado y sus errores por campo. */
  formulario?: Formulario;
  /** Sorteo duplicado ([001] AC-2.2): enlace al existente. */
  existente?: { id: number; url: string };
  sesionVencida?: { pendiente: string | null };
};

export const ESTADO_ADMIN_INICIAL: EstadoAdmin = { generales: [] };
