/**
 * Avisos compartidos con Django ([003] R-31, FR-043, AC-14.3, RN-09). Se leen en el servidor con
 * `GET /api/v1/avisos/` (que los marca como leídos, como una plantilla de Django) y se muestran:
 * sin scripts, como Callout al comienzo del contenido; con scripts, como Toast.
 */
import { apiServidor } from "@/api/servidor";
import { Callout, type VarianteCallout } from "@/components/callout";
import { SoloSinScripts } from "@/components/solo-sin-scripts";
import { AvisosIniciales, type Aviso } from "@/components/toaster";
import { msg } from "@/lib/mensajes";

/** Tipo del aviso como lo marca `templates/ui/_aviso.html` (`data-aviso`). */
const TIPO_AVISO: Record<Aviso["tipo"], string> = {
  exito: "success",
  info: "info",
  advertencia: "warning",
  error: "error",
};

const VARIANTE: Record<Aviso["tipo"], VarianteCallout> = {
  exito: "success",
  info: "info",
  advertencia: "warning",
  error: "danger",
};

export async function leerAvisos(): Promise<Aviso[]> {
  const api = await apiServidor();
  const { data } = await api.GET("/api/v1/avisos/");
  return data ?? [];
}

export function Avisos({ avisos }: { avisos: Aviso[] }) {
  if (avisos.length === 0) return null;
  return (
    <>
      <SoloSinScripts>
        <div className="solo-sin-scripts mb-4 flex flex-col gap-3" data-mensajes="">
          {avisos.map((a, i) => (
            <Callout
              key={i}
              variante={VARIANTE[a.tipo]}
              rol={a.tipo === "error" ? "alert" : "status"}
              texto={a.texto}
              data-aviso={TIPO_AVISO[a.tipo]}
            />
          ))}
        </div>
      </SoloSinScripts>
      <AvisosIniciales avisos={avisos} etiquetaCerrar={msg("aviso.cerrar")} />
    </>
  );
}
