"use server";

/**
 * Server Actions de Ingresar y Crear cuenta ([001] AC-3.1 a AC-3.7; [003] FR-020, FR-040, R-12,
 * R-19, pantalla 5): llaman a `POST /api/v1/sesion/` y `POST /api/v1/cuentas/`; las `Set-Cookie` de
 * Django (sesión y `csrftoken`) vuelven al navegador por `apiServidor()` (sesión compartida).
 */
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { apiServidor } from "@/api/servidor";
import type { EstadoFormulario } from "@/lib/acciones-estado";

export type EstadoCuenta = EstadoFormulario & {
  /** [003] R-12, AC-14.4: tras ingresar, el formulario que quedó pendiente (sin enviarlo). */
  reanudar?: { ruta: string; pendiente: string };
};

const DESTINO_PREDETERMINADO = "/mis-jugadas/";

type Problema = { detail?: string; errores?: { campo: string; mensaje: string }[] };

/** FR-017: solo rutas de este mismo sitio. */
function destinoSeguro(valor: FormDataEntryValue | null): string {
  const texto = typeof valor === "string" ? valor : "";
  return texto.startsWith("/") && !texto.startsWith("//") ? texto : DESTINO_PREDETERMINADO;
}

function texto(datos: FormData, nombre: string): string {
  const valor = datos.get(nombre);
  return typeof valor === "string" ? valor : "";
}

function errores(problema: Problema): EstadoCuenta {
  const porCampo: Record<string, string> = {};
  for (const e of problema.errores ?? []) {
    porCampo[e.campo] = porCampo[e.campo] ? `${porCampo[e.campo]} ${e.mensaje}` : e.mensaje;
  }
  const general = (problema.errores ?? []).length === 0 ? problema.detail : undefined;
  return { errores: porCampo, general };
}

export async function ingresar(_anterior: EstadoCuenta, datos: FormData): Promise<EstadoCuenta> {
  const api = await apiServidor();
  const pendiente = texto(datos, "pendiente") || undefined;
  const { data, error, response } = await api.POST("/api/v1/sesion/", {
    body: { correo: texto(datos, "email"), contrasena: texto(datos, "password"), pendiente },
  });
  if (!response.ok || !data)
    return { ...errores((error ?? {}) as Problema), valores: { email: texto(datos, "email") } };
  revalidatePath("/", "layout");
  if (data.reanudar && pendiente)
    return { errores: {}, reanudar: { ruta: data.reanudar.ruta, pendiente } };
  redirect(destinoSeguro(datos.get("next")));
}

export async function crearCuenta(_anterior: EstadoCuenta, datos: FormData): Promise<EstadoCuenta> {
  const api = await apiServidor();
  const clave = texto(datos, "clave_idempotencia");
  const { error, response } = await api.POST("/api/v1/cuentas/", {
    body: { correo: texto(datos, "email"), contrasena: texto(datos, "password") },
    headers: clave ? { "Idempotency-Key": clave } : {},
  });
  if (!response.ok) {
    const problema = (error ?? {}) as Problema;
    // [001] AC-3.2: el correo ya existe → aviso general con el enlace "Ingresar".
    const existente =
      problema.errores?.length === 1 && problema.detail === problema.errores[0]?.mensaje;
    const estado = existente ? { errores: {}, general: problema.detail } : errores(problema);
    return { ...estado, valores: { email: texto(datos, "email") } };
  }
  revalidatePath("/", "layout");
  redirect(destinoSeguro(datos.get("next")));
}
