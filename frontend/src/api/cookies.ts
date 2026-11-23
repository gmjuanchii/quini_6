/**
 * Cookies de Django que viajan por el servidor de Next.js ([003] R-19).
 *
 * Next.js no maneja la sesión: reenvía a Django la cookie de la persona y, cuando Django responde
 * `Set-Cookie` (sesión renovada, `csrftoken`, ingreso), la devuelve al navegador tal cual.
 */

export type CookieDjango = {
  nombre: string;
  valor: string;
  maxAge?: number;
  expires?: Date;
  path?: string;
  httpOnly?: boolean;
  secure?: boolean;
  sameSite?: "lax" | "strict" | "none";
};

/** Interpreta una línea `Set-Cookie` (`nombre=valor; Path=/; HttpOnly; …`). */
export function leerSetCookie(linea: string): CookieDjango | null {
  const [par, ...atributos] = linea.split(";").map((p) => p.trim());
  if (!par || !par.includes("=")) return null;
  const separador = par.indexOf("=");
  const cookie: CookieDjango = {
    nombre: par.slice(0, separador),
    valor: par.slice(separador + 1).replace(/^"(.*)"$/, "$1"),
  };
  for (const atributo of atributos) {
    const [clave = "", ...resto] = atributo.split("=");
    const valor = resto.join("=");
    switch (clave.toLowerCase()) {
      case "max-age":
        cookie.maxAge = Number(valor);
        break;
      case "expires":
        cookie.expires = new Date(valor);
        break;
      case "path":
        cookie.path = valor;
        break;
      case "httponly":
        cookie.httpOnly = true;
        break;
      case "secure":
        cookie.secure = true;
        break;
      case "samesite":
        cookie.sameSite = valor.toLowerCase() as CookieDjango["sameSite"];
        break;
    }
  }
  return cookie;
}

/** Cabecera `Cookie` a partir de pares nombre/valor. */
export function cabeceraCookie(pares: { name: string; value: string }[]): string {
  return pares.map(({ name, value }) => `${name}=${value}`).join("; ");
}
