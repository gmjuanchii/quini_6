/**
 * Segmento de la Extracción histórica ([003] R-18): recibe el slot `modal`, donde la ruta
 * interceptada `(.)[id]/eliminar` muestra la confirmación como diálogo sobre el listado. TanStack
 * Query se provee solo aquí, donde está el avance en vivo (R-10, R-24).
 */
import type { ReactNode } from "react";

import { ProveedorConsultas } from "./_componentes/proveedor-consultas";

export default function LayoutExtracciones({
  children,
  modal,
}: {
  children: ReactNode;
  modal: ReactNode;
}) {
  return (
    <ProveedorConsultas>
      {children}
      {modal}
    </ProveedorConsultas>
  );
}
