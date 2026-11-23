/**
 * NavBar ([003] contracts/componentes.md; AC-5.1 a AC-5.5, AC-5.7, FR-014 a FR-018, AC-14.1): el
 * mismo encabezado que `templates/base.html` (textos, iconos, variantes y orden), con la sección
 * activa marcada con `aria-current="page"`. Las secciones dependen del perfil que informa Django.
 */
import { Logotipo } from "@/components/marca";
import { boton } from "@/components/ui/variantes";
import type { ClaveMensaje } from "@/lib/mensajes";
import { msg } from "@/lib/mensajes";
import type { Sesion } from "@/lib/sesion";

import { AccountMenu } from "./account-menu";
import { NavegacionMovil } from "./navegacion-movil";

type Seccion = { href: string; clave: ClaveMensaje; activa: (ruta: string) => boolean };

const empiezaCon = (prefijo: string) => (ruta: string) => ruta.startsWith(prefijo);

const PUBLICAS: Seccion[] = [
  {
    href: "/resultados/",
    clave: "nav.resultados",
    activa: (r) => r === "/" || r.startsWith("/resultados/"),
  },
  { href: "/estadisticas/", clave: "nav.estadisticas", activa: empiezaCon("/estadisticas/") },
];
const REGISTRADAS: Seccion[] = [
  { href: "/mis-jugadas/", clave: "nav.mis_jugadas", activa: empiezaCon("/mis-jugadas/") },
];
const ADMINISTRACION: Seccion[] = [
  {
    href: "/administracion/concursos/",
    clave: "nav.administracion",
    activa: empiezaCon("/administracion/"),
  },
];

/** Mismas clases que `clase_enlace` de templates/base.html. */
export const CLASE_ENLACE =
  "flex min-h-control min-w-control items-center rounded-control px-3 font-medium text-foreground no-underline transition-colors hover:bg-muted active:bg-border aria-[current=page]:bg-info-soft aria-[current=page]:text-info-on-soft aria-[current=page]:shadow-[inset_0_-3px_0_var(--color-primary)]";

export function NavBar({ sesion, ruta }: { sesion: Sesion; ruta: string }) {
  const secciones = [
    ...PUBLICAS,
    ...(sesion.correo ? REGISTRADAS : []),
    ...(sesion.correo && sesion.es_administrador ? ADMINISTRACION : []),
  ];
  const rutaSinConsulta = ruta.split("?")[0] ?? "/";

  return (
    <header className="encabezado-q border-b border-border bg-surface">
      <NavegacionMovil
        logotipo={
          // Enlace común (no `Link`): la dirección puede atenderla Django o Next.js según las
          // rutas conmutadas (R-20); se navega con una carga completa, como entre aplicaciones.
          // eslint-disable-next-line @next/next/no-html-link-for-pages
          <a
            href="/"
            aria-label={msg("nav.logotipo")}
            className="flex min-h-control items-center rounded-control text-primary no-underline"
          >
            <Logotipo className="h-8 w-auto" />
          </a>
        }
        textoMenu={msg("nav.menu")}
        etiquetaNavegacion={msg("nav.principal")}
      >
        <ul data-secciones="" className="flex flex-col gap-1 py-2 md:flex-row md:py-0" role="list">
          {secciones.map((s) => (
            <li key={s.href}>
              <a
                href={s.href}
                className={CLASE_ENLACE}
                aria-current={s.activa(rutaSinConsulta) ? "page" : undefined}
              >
                {msg(s.clave)}
              </a>
            </li>
          ))}
        </ul>
        <div className="flex flex-col gap-2 border-t border-border py-2 md:ml-auto md:flex-row md:items-center md:border-0 md:py-0">
          {sesion.correo ? (
            <AccountMenu correo={sesion.correo} />
          ) : (
            <>
              <a href="/ingresar/" className={boton({ variante: "fantasma" })}>
                <span>{msg("nav.ingresar")}</span>
              </a>
              <a href="/registrarse/" className={boton({ variante: "principal" })}>
                <span>{msg("nav.crear_cuenta")}</span>
              </a>
            </>
          )}
        </div>
      </NavegacionMovil>
    </header>
  );
}
