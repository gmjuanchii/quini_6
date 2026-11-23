"use client";

/**
 * Calendario cargado bajo demanda ([003] R-07, R-24): el panel (Popover de Radix), react-day-picker y
 * el idioma `es` de date-fns se descargan recién al abrir el calendario, o al acercar el puntero o el
 * foco a "Abrir calendario" para que aparezca sin espera, como Cally en Django (`data-cally`, T146).
 * Sin esto, toda pantalla con un campo de fecha sumaba unos 60 kB comprimidos de JavaScript inicial.
 */
import dynamic from "next/dynamic";

/** Empieza a descargar el panel (idempotente: el navegador lo pide una sola vez). */
export const cargarCalendario = () => import("@/components/panel-calendario");

/** Se dibuja recién a partir de la primera apertura (antes no descarga nada). */
export const PanelCalendarioDiferido = dynamic(cargarCalendario, { ssr: false });
