/** Páginas de error de Next.js con el mismo diseño y textos que `templates/403.html`, `404.html`
 * y `500.html` de Django ([003] FR-041, AC-14.5). */
import { Callout } from "@/components/callout";
import { msg, type ClaveMensaje } from "@/lib/mensajes";

export function PaginaDeError({ titulo, texto }: { titulo: ClaveMensaje; texto: ClaveMensaje }) {
  return (
    <>
      <h1>{msg(titulo)}</h1>
      <Callout variante="danger" texto={msg(texto)} />
      <p>
        {/* Enlace común: "Resultados" puede atenderlo Django o Next.js (R-20). */}
        {/* eslint-disable-next-line @next/next/no-html-link-for-pages */}
        <a href="/resultados/">{msg("gral.volver_resultados")}</a>
      </p>
    </>
  );
}

/** 403: "Sin permisos para acceder a esta sección" (`admin.sin_permiso`). */
export function SinPermisos() {
  return <PaginaDeError titulo="gral.titulo_acceso_restringido" texto="admin.sin_permiso" />;
}
