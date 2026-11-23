/**
 * Catálogo único de textos visibles ([003] R-13, contracts/mensajes.md).
 *
 * Es el mismo `dominio/mensajes.py` de Django, exportado a `contratos/mensajes.json` con
 * `python manage.py exportar_contratos`. Nunca se escribe un texto visible fuera del catálogo.
 */
import catalogo from "@contratos/mensajes.json";

export type ClaveMensaje = keyof typeof catalogo;

const MENSAJES: Record<string, string> = catalogo;

/** Texto de `clave` con sus variables (`{n}`, `{fecha}`…), como `mensaje()` de Django. */
export function msg(clave: ClaveMensaje, valores?: Record<string, string | number>): string {
  const texto = MENSAJES[clave];
  if (texto === undefined) throw new Error(`Clave de mensaje inexistente: ${clave}`);
  if (!valores) return texto;
  return texto.replace(/\{(\w+)\}/g, (_completo, nombre: string) => {
    if (!(nombre in valores)) throw new Error(`Falta la variable ${nombre} de ${clave}`);
    return String(valores[nombre]);
  });
}

export function esClaveMensaje(clave: string): clave is ClaveMensaje {
  return Object.hasOwn(MENSAJES, clave);
}
