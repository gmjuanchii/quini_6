/** SkipLink ([003] AC-5.5, FR-017): primer elemento enfocable; lleva el foco a `<main>`. */
import { msg } from "@/lib/mensajes";

export function SkipLink() {
  return (
    <a className="saltar" href="#contenido">
      {msg("nav.saltar")}
    </a>
  );
}
