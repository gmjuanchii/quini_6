"use client";

/**
 * Filtro por estado ([003] AC-1.4, FR-003): `<select>` de un formulario GET. Con scripts, elegir
 * una opción envía el formulario (como `onchange` en Django); sin scripts, el botón "Filtrar".
 */
export function FiltroEstado({
  id,
  valor,
  opciones,
}: {
  id: string;
  valor: string;
  opciones: { valor: string; texto: string }[];
}) {
  return (
    <select
      id={id}
      name="estado"
      defaultValue={valor}
      className="min-h-control rounded-control border border-border-input bg-surface px-3 text-foreground"
      onChange={(e) => e.currentTarget.form?.requestSubmit()}
    >
      {opciones.map((o) => (
        <option key={o.valor} value={o.valor}>
          {o.texto}
        </option>
      ))}
    </select>
  );
}
