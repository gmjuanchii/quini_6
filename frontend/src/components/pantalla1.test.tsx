// [003] T175 a T177: componentes de la pantalla 1 con los estados de contracts/componentes.md.
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { msg } from "@/lib/mensajes";
import { encabezados } from "@/lib/tablas";

import { ActionMenu } from "./action-menu";
import { BackLink } from "./back-link";
import { DataTable } from "./data-table";
import { DateField } from "./date-field";
import { DateRangePicker } from "./date-range-picker";
import { EmptyState } from "./empty-state";
import { Field } from "./field";
import { Pagination } from "./pagination";
import { ProgressPanel, type Avance } from "./progress-panel";
import { StatusBadge, type Etiqueta } from "./status-badge";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ refresh: vi.fn(), back: vi.fn(), push: vi.fn() }),
}));

afterEach(cleanup);

const CON_ERROR: Etiqueta = {
  valor: "con_error",
  slug: "con-error",
  texto: msg("etiqueta.con_error"),
  explicacion: msg("etiqueta.con_error.explicacion"),
  variante: "danger",
  requiere_revision: true,
};

describe("StatusBadge (AC-1.1, AC-1.2)", () => {
  it("texto, icono decorativo y explicación por aria-describedby", () => {
    render(<StatusBadge etiqueta={CON_ERROR} id={7} />);
    const insignia = screen.getByText(msg("etiqueta.con_error")).parentElement!;
    expect(insignia.getAttribute("tabindex")).toBe("0");
    expect(insignia.getAttribute("aria-describedby")).toBe("explicacion-7");
    expect(screen.getByRole("tooltip", { hidden: true }).textContent).toBe(CON_ERROR.explicacion);
    expect(insignia.querySelector("svg")?.getAttribute("aria-hidden")).toBe("true");
  });
});

describe("EmptyState (AC-8.1 a AC-8.4)", () => {
  it("sin resultados nombra el filtro y ofrece Limpiar filtros", () => {
    render(
      <EmptyState
        variante="sin_resultados"
        titulo={msg("vacio.filtro.titulo")}
        explicacion={msg("vacio.filtro.explicacion", { filtro: "Con error" })}
        limpiarHref="/administracion/extracciones/"
      />,
    );
    expect(screen.getByRole("heading", { name: msg("vacio.filtro.titulo") })).toBeTruthy();
    expect(
      screen.getByRole("link", { name: msg("vacio.filtro.accion") }).getAttribute("href"),
    ).toBe("/administracion/extracciones/");
  });

  it("sin datos solo muestra la acción si se la pasa (permiso del perfil)", () => {
    render(<EmptyState titulo={msg("vacio.extracciones.titulo")} />);
    expect(screen.queryByRole("link")).toBeNull();
  });
});

describe("BackLink y Field", () => {
  it("BackLink quita la flecha del texto (la pone el icono)", () => {
    render(
      <BackLink href="/administracion/extracciones/" texto={msg("nav.volver_extracciones")} />,
    );
    expect(screen.getByRole("link").textContent).toBe("Extracción histórica");
  });

  it("Field asocia etiqueta, ayuda y error", () => {
    render(
      <Field id="correo" etiqueta="Correo" ayuda="Ayuda" error="Error">
        <input />
      </Field>,
    );
    const control = screen.getByLabelText("Correo");
    expect(control.getAttribute("aria-invalid")).toBe("true");
    expect(control.getAttribute("aria-describedby")).toBe("correo_ayuda correo_error");
  });
});

describe("Pagination (AC-9.2, RN-07)", () => {
  it("conserva filtro y orden; extremos con aria-disabled", () => {
    render(
      <Pagination pagina={1} paginas={3} parametros={{ estado: "finalizada", orden: "periodo" }} />,
    );
    const nav = screen.getByRole("navigation", { name: "Paginación" });
    expect(within(nav).getByText(msg("pag.pagina", { n: 1, m: 3 }))).toBeTruthy();
    expect(
      within(nav)
        .getByRole("link", { name: msg("pag.siguiente") })
        .getAttribute("href"),
    ).toBe("?estado=finalizada&orden=periodo&pagina=2");
    expect(nav.querySelector('[aria-disabled="true"]')?.textContent).toBe(msg("pag.anterior"));
  });

  it("una sola página: no se muestra", () => {
    const { container } = render(<Pagination pagina={1} paginas={1} parametros={{}} />);
    expect(container.innerHTML).toBe("");
  });
});

describe("DataTable (AC-9.1, AC-9.3, AC-9.4)", () => {
  it("caption, aria-sort, encabezados como enlaces y rótulos para las tarjetas", () => {
    render(
      <DataTable
        titulo="Extracciones anteriores"
        encabezados={encabezados(
          {},
          [
            { id: "fecha", texto: "Fecha", ordenable: true },
            { id: "ejecutada_por", texto: "Ejecutada por" },
          ],
          "-fecha",
        )}
        filas={[
          {
            clave: "1",
            id: "fila-extraccion-1",
            enlace: true,
            celdas: { fecha: "21/11/2026 12:15", ejecutada_por: "a@b" },
          },
        ]}
      />,
    );
    const tabla = screen.getByRole("table", { name: "Extracciones anteriores" });
    const [fecha, ejecutada] = within(tabla).getAllByRole("columnheader");
    expect(fecha!.getAttribute("aria-sort")).toBe("descending");
    expect(within(fecha!).getByRole("link").getAttribute("href")).toBe("?orden=fecha");
    expect(ejecutada!.getAttribute("aria-sort")).toBeNull();
    const fila = tabla.querySelector("tbody tr")!;
    expect(fila.id).toBe("fila-extraccion-1");
    expect(fila.className).toContain("fila-enlace");
    expect(fila.querySelector("td")!.getAttribute("data-rotulo")).toBe("Fecha");
  });
});

describe("ActionMenu (AC-2.1, AC-2.2)", () => {
  const opciones = [
    { texto: msg("ext.ver_detalle"), href: "/x/1/" },
    { texto: msg("ext.eliminar"), href: "/x/1/eliminar/", destructivo: true, confirmar: true },
  ];

  it("details con summary nombrado y opciones role=menuitem", () => {
    render(
      <ActionMenu nombre="Acciones de la extracción del 21/11/2026 12:15" opciones={opciones} />,
    );
    const detalles = document.querySelector("details.menu-acciones")!;
    expect(detalles.querySelector("summary")!.getAttribute("aria-label")).toContain("Acciones");
    const items = within(detalles as HTMLElement).getAllByRole("menuitem", { hidden: true });
    expect(items).toHaveLength(2);
    expect(items[1]!.hasAttribute("data-confirmar")).toBe(true);
  });

  it("flechas recorren y Escape cierra devolviendo el foco", () => {
    render(<ActionMenu nombre="Acciones" opciones={opciones} />);
    const detalles = document.querySelector("details")! as HTMLDetailsElement;
    detalles.open = true;
    fireEvent(detalles, new Event("toggle"));
    const items = within(detalles).getAllByRole("menuitem");
    expect(document.activeElement).toBe(items[0]);
    fireEvent.keyDown(screen.getByRole("menu"), { key: "ArrowDown" });
    expect(document.activeElement).toBe(items[1]);
    fireEvent.keyDown(items[1]!, { key: "Escape" });
    expect(detalles.open).toBe(false);
    expect(document.activeElement).toBe(detalles.querySelector("summary"));
  });
});

function conQuery(nodo: ReactNode) {
  return <QueryClientProvider client={new QueryClient()}>{nodo}</QueryClientProvider>;
}

const EN_CURSO: Etiqueta = {
  ...CON_ERROR,
  valor: "en_curso",
  slug: "en-curso",
  texto: msg("etiqueta.en_curso"),
  variante: "info",
  requiere_revision: false,
};

describe("ProgressPanel (AC-3.2, AC-3.3)", () => {
  it("identificando: indicador y sin barra", () => {
    const avance: Avance = {
      en_curso: true,
      identificando: true,
      procesados: 0,
      total: null,
      etiqueta: EN_CURSO,
      aviso_final: null,
    };
    render(
      conQuery(
        <ProgressPanel
          id={1}
          inicial={avance}
          periodo="Período consultado: 01/11/2026 al 15/11/2026"
        />,
      ),
    );
    expect(screen.getByRole("status").getAttribute("aria-live")).toBe("polite");
    expect(screen.getByText(msg("ext.identificando"))).toBeTruthy();
    expect(document.querySelector("progress")).toBeNull();
  });

  it("con total: barra nombrada por el texto del avance", () => {
    const avance: Avance = {
      en_curso: true,
      identificando: false,
      procesados: 1,
      total: 5,
      etiqueta: EN_CURSO,
      aviso_final: null,
    };
    render(conQuery(<ProgressPanel id={1} inicial={avance} periodo="" />));
    const barra = document.querySelector("progress")!;
    expect(barra.getAttribute("value")).toBe("1");
    expect(barra.getAttribute("max")).toBe("5");
    expect(barra.getAttribute("aria-labelledby")).toBe("avance-texto");
    expect(document.getElementById("avance-texto")!.textContent).toBe(
      msg("ext.avance", { n: 1, m: 5 }),
    );
  });
});

describe("DateField y DateRangePicker (AC-4.1 a AC-4.4)", () => {
  it("con scripts: texto dd/mm/aaaa con barras automáticas y botón Abrir calendario", () => {
    render(
      <DateField
        campo={{
          id: "id_inicio",
          nombre: "inicio",
          etiqueta: "Fecha de inicio",
          valor: "2025-01-15",
          max: "2026-11-22",
        }}
      />,
    );
    const campo = screen.getByLabelText("Fecha de inicio") as HTMLInputElement;
    expect(campo.type).toBe("text");
    expect(campo.value).toBe("15/01/2025");
    fireEvent.input(campo, { target: { value: "01012025" } });
    expect(campo.value).toBe("01/01/2025");
    expect(screen.getByRole("button", { name: msg("fecha.abrir_calendario") })).toBeTruthy();
  });

  it("error junto al campo", () => {
    render(
      <DateField
        campo={{
          id: "id_fin",
          nombre: "fin",
          etiqueta: "Fecha de finalización",
          error: msg("fecha.falta_fin"),
        }}
      />,
    );
    const campo = screen.getByLabelText("Fecha de finalización");
    expect(campo.getAttribute("aria-invalid")).toBe("true");
    expect(document.getElementById("id_fin_error")!.textContent).toBe(msg("fecha.falta_fin"));
  });

  it("los atajos completan ambos campos sin navegar (AC-4.4)", () => {
    render(
      <DateRangePicker
        leyenda="Período"
        desde={{ id: "id_inicio", nombre: "inicio", etiqueta: "Fecha de inicio" }}
        hasta={{ id: "id_fin", nombre: "fin", etiqueta: "Fecha de finalización" }}
        atajos={[
          {
            clave: "anio_anterior",
            texto: msg("ext.atajo_anio_anterior"),
            desde: "2025-01-01",
            hasta: "2025-12-31",
          },
        ]}
        hrefAtajo={(c) => `?atajo=${c}`}
      />,
    );
    const atajo = screen.getByRole("link", { name: msg("ext.atajo_anio_anterior") });
    expect(atajo.getAttribute("href")).toBe("?atajo=anio_anterior");
    fireEvent.click(atajo);
    expect((screen.getByLabelText("Fecha de inicio") as HTMLInputElement).value).toBe("01/01/2025");
    expect((screen.getByLabelText("Fecha de finalización") as HTMLInputElement).value).toBe(
      "31/12/2025",
    );
  });
});
