/**
 * FrequencyChart ([001] R-11; [003] AC-7.5, FR-024, R-18, CHK022): gráfico de barras en SVG
 * generado en el servidor (componente de servidor, sin Recharts ni JavaScript de cliente), con el
 * mismo cálculo que `estadisticas/views.py :: _grafico` y el mismo marcado que
 * `templates/estadisticas/_grafico.html`: `role="img"` con título y descripción, colores de los
 * tokens en ambos temas y el número consultado con el acento.
 */
import { dosDigitos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";

export const ANCHO_BARRA = 10;
export const ALTO_GRAFICO = 120;
export const MARGEN_INFERIOR = 22;

export type Frecuencia = { numero: number; frecuencia: number };

export type Barra = {
  numero: number;
  frecuencia: number;
  x: number;
  xTexto: number;
  y: number;
  alto: number;
  ancho: number;
  consultado: boolean;
  rotulo: boolean;
};

/** Python `round(x, 2)` para los valores de este gráfico (siempre positivos). */
function redondear2(valor: number): number {
  return Math.round((valor + Number.EPSILON) * 100) / 100;
}

/** El mismo cálculo que `_grafico` de Django: alto proporcional al máximo. */
export function calcularGrafico(numeros: Frecuencia[], consultado: number | null) {
  const maximo = Math.max(0, ...numeros.map((f) => f.frecuencia)) || 1;
  const barras: Barra[] = numeros.map((f) => {
    const alto = redondear2((ALTO_GRAFICO * f.frecuencia) / maximo);
    return {
      numero: f.numero,
      frecuencia: f.frecuencia,
      x: f.numero * ANCHO_BARRA + 1,
      xTexto: f.numero * ANCHO_BARRA + ANCHO_BARRA / 2,
      y: redondear2(ALTO_GRAFICO - alto),
      alto,
      ancho: ANCHO_BARRA - 2,
      consultado: f.numero === consultado,
      rotulo: f.numero % 5 === 0 || f.numero === consultado,
    };
  });
  return {
    barras,
    ancho: barras.length * ANCHO_BARRA,
    alto: ALTO_GRAFICO + MARGEN_INFERIOR,
    base: ALTO_GRAFICO,
    yTexto: ALTO_GRAFICO + 14,
  };
}

export function FrequencyChart({
  numeros,
  consultado,
  modalidad,
  cantidadSorteos,
}: {
  numeros: Frecuencia[];
  consultado: number | null;
  modalidad: string;
  cantidadSorteos: number;
}) {
  const g = calcularGrafico(numeros, consultado);
  const descripcion =
    msg(cantidadSorteos === 1 ? "rot.est_grafico_desc_uno" : "rot.est_grafico_desc", {
      n: cantidadSorteos,
    }) +
    (consultado !== null
      ? msg("rot.est_grafico_resaltado", { numero: dosDigitos(consultado) })
      : "") +
    ".";
  return (
    <figure className="m-0 rounded-card border border-border bg-surface p-3 shadow-1">
      <svg
        viewBox={`0 0 ${g.ancho} ${g.alto}`}
        role="img"
        aria-labelledby="grafico-titulo grafico-descripcion"
        className="block h-auto w-full"
        preserveAspectRatio="xMidYMid meet"
      >
        <title id="grafico-titulo">{msg("rot.est_grafico_titulo", { modalidad })}</title>
        <desc id="grafico-descripcion">{descripcion}</desc>
        <line
          x1="0"
          y1={g.base}
          x2={g.ancho}
          y2={g.base}
          className="stroke-border"
          strokeWidth="0.5"
        />
        {g.barras.map((b) => (
          <g key={b.numero}>
            <rect
              className={
                b.consultado ? "barra barra--consultada fill-accent" : "barra fill-primary"
              }
              x={b.x}
              y={b.y}
              width={b.ancho}
              height={b.alto}
              rx="1"
            >
              <title>
                {msg("rot.est_barra", { numero: dosDigitos(b.numero), frecuencia: b.frecuencia })}
              </title>
            </rect>
            {b.rotulo && (
              <text
                x={b.xTexto}
                y={g.yTexto}
                textAnchor="middle"
                fontSize="9"
                className={
                  b.consultado
                    ? "cifras fill-current font-bold text-accent-text"
                    : "cifras fill-current text-muted-foreground"
                }
              >
                {dosDigitos(b.numero)}
              </text>
            )}
          </g>
        ))}
      </svg>
      <figcaption className="mt-2 text-sm text-muted-foreground">
        {msg("rot.est_grafico_pie")}
      </figcaption>
    </figure>
  );
}
