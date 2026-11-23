/**
 * Logotipo provisional ([003] RN-08, P-02): el mismo SVG de `ui/marca/logotipo.svg`, en línea para
 * que tome el color del tema con `currentColor` (como `{% marca "logotipo" %}` en Django).
 */
export function Logotipo({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 124 32"
      role="img"
      aria-label="QUINI_6"
      className={className}
    >
      <rect width="32" height="32" rx="8" fill="currentColor" />
      <text
        x="16"
        y="22"
        textAnchor="middle"
        fontFamily="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
        fontSize="15"
        fontWeight="800"
        style={{ fill: "var(--color-primary-foreground, #ffffff)" }}
      >
        Q6
      </text>
      <text
        x="40"
        y="22.5"
        fontFamily="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
        fontSize="19"
        fontWeight="800"
        letterSpacing="-0.3"
        fill="currentColor"
      >
        QUINI_6
      </text>
    </svg>
  );
}
