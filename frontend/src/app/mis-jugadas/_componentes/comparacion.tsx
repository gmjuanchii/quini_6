/**
 * Comparación de una jugada con los resultados oficiales ([001] US5, AC-5.x; [003] FR-041): el mismo
 * marcado que `templates/jugadas/_comparacion.html`, con los datos de `GET /api/v1/jugadas/{id}/`
 * (calculados en cada consulta por `dominio/comparacion.py`).
 */
import type { components } from "@/api/esquema";
import { Callout } from "@/components/callout";
import { dosDigitos, fecha, pesos } from "@/lib/formato";
import { msg } from "@/lib/mensajes";
import { cn } from "@/lib/utils";

type Comparacion = components["schemas"]["ComparacionModalidad"];

function claseResultado(codigo: string | undefined): string {
  if (codigo === "CON_PREMIO") return "estado--con-premio";
  if (codigo === "SIN_PREMIO") return "estado--sin-premio";
  return "estado--pendiente";
}

function Bolillas({
  numeros,
  acertados,
  rotulo,
}: {
  numeros: number[];
  acertados: number[];
  rotulo: string;
}) {
  return (
    <ul className="numeros" aria-label={rotulo}>
      {numeros.map((n) =>
        acertados.includes(n) ? (
          <li key={n} className="bolilla bolilla--acertada">
            {dosDigitos(n)}
            <span className="visualmente-oculto"> {msg("rot.acertado")}</span>
          </li>
        ) : (
          <li key={n} className="bolilla">
            {dosDigitos(n)}
          </li>
        ),
      )}
    </ul>
  );
}

export function ComparacionJugada({
  numeros,
  comparacion,
}: {
  numeros: number[];
  comparacion: Comparacion[];
}) {
  return (
    <div className="comparacion">
      {comparacion.map((r) => {
        const slug = r.modalidad.slug;
        const acertados = r.numeros_acertados ?? [];
        return (
          <section
            key={slug}
            className="comparacion__bloque"
            id={`comparacion-${slug}`}
            aria-labelledby={`comp-titulo-${slug}`}
          >
            <h3 id={`comp-titulo-${slug}`}>{r.modalidad.nombre}</h3>
            {!r.publicado ? (
              <p className="comparacion__dato">
                <span className="estado estado--pendiente">{r.estado_validacion.texto}</span>
              </p>
            ) : (
              <>
                {r.estado_validacion.codigo === "EN_REVISION" ? (
                  <p className="comparacion__dato">
                    <span className="estado estado--revision">
                      {msg("rot.publicado_en_revision")}
                    </span>
                  </p>
                ) : (
                  <p className="comparacion__dato text-sm text-muted-foreground">
                    {msg("rot.resultado_publicado")}
                  </p>
                )}
                {r.conjunto ? (
                  <>
                    <p className="comparacion__dato">
                      {msg("comp.numeros_resaltados", { n: r.conjunto.length })}
                    </p>
                    <Bolillas
                      numeros={r.conjunto}
                      acertados={acertados}
                      rotulo={msg("rot.conjunto_premio_extra")}
                    />
                  </>
                ) : (
                  <>
                    <p className="comparacion__dato">{msg("comp.tu_jugada")}</p>
                    <Bolillas
                      numeros={numeros}
                      acertados={acertados}
                      rotulo={msg("rot.numeros_jugada")}
                    />
                    <p className="comparacion__dato text-sm text-muted-foreground">
                      {msg("rot.numeros_oficiales", {
                        numeros: (r.numeros_oficiales ?? []).map((n) => dosDigitos(n)).join(", "),
                      })}
                    </p>
                  </>
                )}
                <p className="comparacion__dato">
                  <strong>
                    {msg(r.conjunto ? "rot.n_aciertos_conjunto" : "rot.n_aciertos", {
                      n: r.aciertos ?? 0,
                    })}
                  </strong>
                </p>
                {r.elegibilidad === "excluida" && (
                  <p className="comparacion__dato">
                    <span className="estado estado--sin-premio">
                      {msg("comp.excluida", { sorteo: r.excluida_por ?? "" })}
                    </span>
                  </p>
                )}
                {r.elegibilidad === "participa" && (
                  <p className="comparacion__dato">
                    {msg("rot.elegibilidad")}{" "}
                    <span className="estado estado--con-premio">{msg("comp.participa")}</span>
                  </p>
                )}
                {r.resultado_premio?.texto && (
                  <p className="comparacion__dato">
                    <span className={cn("estado", claseResultado(r.resultado_premio.codigo))}>
                      {r.resultado_premio.texto}
                    </span>
                  </p>
                )}
                {r.resultado_premio?.codigo === "CON_PREMIO" && (
                  <p className="comparacion__dato">
                    {msg("rot.importe")}{" "}
                    {r.importe_pendiente || r.importe === null ? (
                      msg("rot.premios_pendientes")
                    ) : (
                      <strong>{pesos(r.importe)}</strong>
                    )}
                  </p>
                )}
                {r.avisos.map((a) => (
                  <Callout key={a} variante="warning" texto={a} />
                ))}
              </>
            )}
            {r.actualizado_el && (
              <p className="comparacion__dato">
                <span className="estado estado--corregido">
                  {msg("comp.actualizado", { fecha: fecha(r.actualizado_el) })}
                </span>
              </p>
            )}
          </section>
        );
      })}
    </div>
  );
}
