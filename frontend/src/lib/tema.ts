/**
 * Preferencia de tema ([003] HU-12, R-14, data-model § 4): la misma cookie `quini6_tema` que
 * `quini6/tema.py`. Es lo único que se recuerda en el navegador (NFR-008).
 */
export const COOKIE_TEMA = "quini6_tema";
export const DURACION_TEMA = 400 * 24 * 60 * 60; // 400 días

export type Tema = "claro" | "oscuro" | "dispositivo";

/** `claro`, `oscuro` o `dispositivo` (sin cookie o con un valor inválido), como `tema_de()`. */
export function temaDe(valor: string | undefined): Tema {
  return valor === "claro" || valor === "oscuro" ? valor : "dispositivo";
}

/** Aplica el tema al instante y guarda la cookie (solo en el navegador). */
export function aplicarTema(valor: Tema): void {
  const raiz = document.documentElement;
  const seguro = window.location.protocol === "https:" ? "; Secure" : "";
  if (valor === "claro" || valor === "oscuro") {
    raiz.setAttribute("data-theme", valor);
    document.cookie = `${COOKIE_TEMA}=${valor}; Path=/; Max-Age=${DURACION_TEMA}; SameSite=Lax${seguro}`;
  } else {
    raiz.removeAttribute("data-theme");
    document.cookie = `${COOKIE_TEMA}=; Path=/; Max-Age=0; SameSite=Lax${seguro}`;
  }
}
