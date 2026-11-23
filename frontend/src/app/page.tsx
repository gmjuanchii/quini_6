/** Inicio ([001] contracts/rutas.md): como en Django, lleva a "Resultados". */
import { redirect } from "next/navigation";

export default function Inicio() {
  redirect("/resultados/");
}
