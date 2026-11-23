# Contrato de tokens de diseño

**Plan**: [../plan.md](../plan.md) | **Research**: [../research.md](../research.md) R-02, R-14, R-15, R-29 | **Componentes**: [componentes.md](componentes.md)

Fuente de diseño: Figma (P-02). Transcripción en código: `ui/tokens.css`, único lugar donde se definen estos valores, importado por Django (Etapa 1) y Next.js (Etapa 2). Los componentes usan **solo los tokens semánticos** de esta tabla. Cambiar un valor exige actualizar este contrato y volver a medir su contraste.

## 1. Colores base (RN-12)

| Token | Valor | Uso permitido |
|-------|-------|---------------|
| `primary` | `#1E40AF` | Encabezado, botón principal, enlaces, sección activa, foco |
| `accent` | `#F97316` | Rellenos y resaltados no críticos **sin texto encima**; nunca en el mismo botón que `primary` |
| `background` | `#F3F4F6` | Fondo de página |
| `foreground` | `#1F2937` | Texto principal |
| `success` | `#10B981` | Rellenos decorativos (barra de progreso completa); **no** para iconos ni texto (2,54:1) |
| `danger` | `#EF4444` | Bordes e iconos de error |
| `warning` | ámbar propio (ver § 2) | Distinto del naranja de acento (RN-01, R-30) |

## 2. Tokens semánticos y contraste medido

Contraste calculado con la fórmula de luminancia relativa de WCAG 2.2 el 21/11/2026. Umbrales: texto ≥ 4,5:1; iconos informativos, bordes de campos y foco ≥ 3:1 (NFR-002, SC-009). La prueba `ui/tokens.test.ts` recalcula cada par desde `ui/tokens.css`.

### Tema claro

| Token | Valor | Par medido | Contraste | Cumple |
|-------|-------|------------|----------:|:------:|
| `background` | `#F3F4F6` | — | — | — |
| `surface` (tarjetas, campos, menús) | `#FFFFFF` | — | — | — |
| `foreground` | `#1F2937` | sobre `background` / `surface` | 13,34 / 14,68 | ✅ |
| `muted-foreground` (ayudas, marcadores de posición, pie) | `#4B5563` | sobre `background` / `surface` | 6,87 / 7,56 | ✅ |
| `primary` (texto y enlaces) | `#1E40AF` | sobre `surface` / `background` | 8,72 / 7,93 | ✅ |
| `primary-foreground` | `#FFFFFF` | sobre `primary` | 8,72 | ✅ |
| `primary-hover` | `#1E3A8A` | sobre `surface` | 10,36 | ✅ |
| `accent-text` | `#C2410C` | sobre `surface` / `background` | 5,18 / 4,71 | ✅ |
| `accent-icon` | `#EA580C` | sobre `surface` / `background` | 3,56 / 3,23 | ✅ (solo iconos) |
| `success-text` | `#047857` | sobre `surface` | 5,48 | ✅ |
| `success-icon` | `#059669` | sobre `surface` / `background` | 3,77 / 3,42 | ✅ (solo iconos) |
| `danger-text` | `#B91C1C` | sobre `surface` | 6,47 | ✅ |
| `danger-icon` / `danger` | `#EF4444` | sobre `surface` / `background` | 3,76 / 3,42 | ✅ (solo iconos y bordes) |
| `destructive` (botón "Eliminar") | `#B91C1C` con texto `#FFFFFF` | texto sobre fondo | 6,47 | ✅ |
| `warning-text` / `warning-icon` | `#B45309` | sobre `surface` | 5,02 | ✅ |
| `border-input` (campos) | `#6B7280` | sobre `surface` / `background` | 4,83 / 4,39 | ✅ |
| `border` (separadores decorativos) | `#D1D5DB` | sobre `surface` | 1,47 | — (no informativo) |
| `ring` (foco) | `#1E40AF`, 2 px + separación 2 px | sobre `surface` / `background` | 8,72 / 7,93 | ✅ |

Etiquetas y avisos: fondo tenue + texto oscuro del mismo tono (RN-09, RN-12). El icono usa el mismo color que el texto.

| Variante | Fondo | Texto e icono | Contraste | Cumple |
|----------|-------|---------------|----------:|:------:|
| `success` | `#D1FAE5` | `#065F46` | 6,78 | ✅ |
| `warning` | `#FEF3C7` | `#92400E` | 6,37 | ✅ |
| `danger` | `#FEE2E2` | `#991B1B` | 6,80 | ✅ |
| `info` | `#DBEAFE` | `#1E40AF` | 7,15 | ✅ |
| `neutral` | `#E5E7EB` | `#374151` | 8,33 | ✅ |

Descartado: texto `#B45309` sobre `#FEF3C7` (4,51:1, en el límite; se usa `#92400E`).

### Tema oscuro (mismo significado de color, AC-12.4)

| Token | Valor | Par medido | Contraste | Cumple |
|-------|-------|------------|----------:|:------:|
| `background` | `#0F172A` | — | — | — |
| `surface` | `#1E293B` | — | — | — |
| `foreground` | `#F3F4F6` | sobre `background` / `surface` | 16,22 / 13,29 | ✅ |
| `muted-foreground` | `#94A3B8` | sobre `background` / `surface` | 6,96 / 5,71 | ✅ |
| `primary` (texto y enlaces) | `#93C5FD` | sobre `surface` / `background` | 8,11 / 9,90 | ✅ |
| `primary` (botón) con `primary-foreground` | `#60A5FA` con texto `#0F172A` | texto sobre fondo | 7,02 | ✅ |
| `accent-text` / `accent-icon` | `#FDBA74` / `#FB923C` | sobre `surface` | 8,67 / 6,46 | ✅ |
| `success-text` / `success-icon` | `#6EE7B7` / `#34D399` | sobre `surface` | 9,60 / 7,61 | ✅ |
| `danger-text` / `danger-icon` | `#FCA5A5` / `#F87171` | sobre `surface` | 7,71 / 5,29 | ✅ |
| `destructive` con texto | `#F87171` con texto `#0F172A` | texto sobre fondo | 6,45 | ✅ |
| `warning-text` / `warning-icon` | `#FCD34D` / `#FBBF24` | sobre `surface` | 10,15 / 8,76 | ✅ |
| `border-input` | `#94A3B8` | sobre `surface` | 5,71 | ✅ |
| `ring` | `#93C5FD` | sobre `surface` / `background` | 8,11 / 9,90 | ✅ |

| Variante | Fondo | Texto e icono | Contraste | Cumple |
|----------|-------|---------------|----------:|:------:|
| `success` | `#064E3B` | `#A7F3D0` | 7,58 | ✅ |
| `warning` | `#78350F` | `#FDE68A` | 7,28 | ✅ |
| `danger` | `#7F1D1D` | `#FECACA` | 6,93 | ✅ |
| `info` | `#1E3A8A` | `#BFDBFE` | 7,29 | ✅ |
| `neutral` | `#374151` | `#E5E7EB` | 8,33 | ✅ |

Descartado en oscuro: botón destructivo `#DC2626` con texto blanco (4,83:1, margen escaso); se usa `#F87171` con texto oscuro.

## 3. Tipografía

| Token | Valor |
|-------|-------|
| `font-sans` | Pila `sans` por defecto de Tailwind (fuentes del sistema; sin descargas) |
| `text-xs` / `sm` / `base` / `lg` / `2xl` / `3xl` | 12 / 14 / 16 / 18 / 24 / 32 px |
| Cuerpo | 16 px, interlineado 1,5 |
| Texto secundario mínimo (incluido el pie, AC-10.2) | 14 px |
| Cifras de bolillas e importes | `font-variant-numeric: tabular-nums` |

## 4. Espaciado, radios, sombras, alturas, movimiento

| Token | Valor |
|-------|-------|
| Espaciado | múltiplos de 4 px (escala de Tailwind) |
| `radius-control` / `radius-card` | 8 px / 12 px |
| `shadow-1` / `shadow-2` | `0 1px 2px rgb(0 0 0 / .06)` / `0 4px 12px rgb(0 0 0 / .08)` (oscuro: bordes `border` en lugar de sombra perceptible) |
| `control-height` | 44 px (mínimo táctil, NFR-001) |
| `content-max` | 72 rem; formularios de una columna: 28 rem (AC-6.1) |
| `duration-fast` / `duration-normal` | 150 ms / 200 ms (máximo 250 ms, AC-13.1) |
| `ease-standard` | `cubic-bezier(.2, 0, 0, 1)` |
| Movimiento reducido | Duraciones a 0 ms y sin desplazamientos (AC-13.2) |
| Punto de quiebre de navegación y tablas | 768 px (`md`) |
