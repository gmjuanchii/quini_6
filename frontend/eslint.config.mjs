// [003] R-22: ESLint con la configuración de Next.js.
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

const config = [
  ...nextVitals,
  ...nextTs,
  { ignores: [".next/**", "storybook-static/**", "src/api/esquema.d.ts", "next-env.d.ts"] },
];

export default config;
