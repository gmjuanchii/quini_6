/**
 * "¿Todavía sin cuenta? Crear cuenta" / "¿Ya hay una cuenta? Ingresar" ([003] AC-6.7): el mismo
 * marcado que `templates/cuentas/_alternativa.html` (pregunta y acción separadas del texto del
 * catálogo, como el filtro `pregunta_y_accion`).
 */
import Link from "next/link";

import { boton } from "@/components/ui/variantes";

export function preguntaYAccion(texto: string): [string, string] {
  const i = texto.indexOf("? ");
  return i === -1 ? ["", texto] : [texto.slice(0, i + 1), texto.slice(i + 2)];
}

export function Alternativa({ texto, href }: { texto: string; href: string }) {
  const [pregunta, accion] = preguntaYAccion(texto);
  return (
    <p
      data-alternativa=""
      className="mt-6 flex flex-wrap items-center justify-center gap-x-2 gap-y-1 text-center text-muted-foreground"
    >
      {pregunta}{" "}
      <Link href={href} className={boton({ variante: "secundario", tamano: "sm" })}>
        {accion}
      </Link>
    </p>
  );
}
