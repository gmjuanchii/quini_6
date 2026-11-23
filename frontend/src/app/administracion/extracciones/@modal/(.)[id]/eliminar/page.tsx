/**
 * Confirmación de eliminación como diálogo ([003] AC-2.3 a AC-2.5, R-18): ruta interceptada que,
 * al elegir "Eliminar" en el menú ⋮ con scripts, muestra el contenido de `[id]/eliminar/` sobre el
 * listado sin cambiar de pantalla. Abrir la dirección directamente muestra la página aparte.
 */
import { ConfirmDialog } from "@/components/confirm-dialog";
import { msg } from "@/lib/mensajes";

import {
  CuerpoEliminar,
  extraccionAEliminar,
  textoConfirmar,
} from "../../../_componentes/eliminar";

export default async function DialogoEliminar({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const e = await extraccionAEliminar(id);
  return (
    <ConfirmDialog titulo={msg("ext.eliminar_titulo")} texto={textoConfirmar(e)}>
      <CuerpoEliminar e={e} />
    </ConfirmDialog>
  );
}
