/**
 * Cabeceras internas que `proxy.ts` agrega al pedido para las páginas ([003] R-19). Módulo aparte,
 * sin dependencias, para que el proxy no cargue `next/headers` ni el cliente de la API.
 */

/** La página se dibuja como respuesta de una Server Action (con o sin scripts) — FR-032. */
export const CABECERA_ACCION = "x-quini6-accion";
