"use client";

/**
 * Sesión vencida al enviar un formulario de Next.js ([003] FR-032, R-12, AC-14.4): como Django, que
 * responde "Ingresar" en lugar del formulario, aparece el aviso `cuenta.sesion_vencida` con el
 * ingreso en la misma página: correo, contraseña y lo escrito firmado por Django (`pendiente`). El
 * ingreso lo atiende Django (`?_interfaz=django`), que después ofrece "Volver al formulario" y
 * Next.js lo reabre precargado, sin enviar nada. Es un formulario común: funciona sin scripts.
 * `csrf` es el valor de la cookie `csrftoken` de Django, que la página lee en el servidor.
 */
import { Callout } from "@/components/callout";
import { Field } from "@/components/field";
import { PasswordField } from "@/components/password-field";
import { Button } from "@/components/ui/button";
import { msg } from "@/lib/mensajes";

export function accionIngresar(siguiente: string): string {
  return `/ingresar/?next=${encodeURIComponent(siguiente)}&_interfaz=django`;
}

export function SesionVencida({
  pendiente,
  siguiente,
  csrf,
}: {
  pendiente: string | null;
  siguiente: string;
  csrf: string;
}) {
  return (
    <Callout variante="warning" rol="alert" texto={msg("cuenta.sesion_vencida")}>
      <form
        method="post"
        action={accionIngresar(siguiente)}
        className="mt-3 flex flex-col gap-4"
        data-sesion-vencida=""
      >
        <input type="hidden" name="csrfmiddlewaretoken" value={csrf} />
        <input type="hidden" name="next" value={siguiente} />
        {pendiente && <input type="hidden" name="pendiente" value={pendiente} />}
        <Field id="sesion_email" etiqueta={msg("rot.correo")}>
          <input type="email" name="email" autoComplete="email" spellCheck={false} />
        </Field>
        <PasswordField
          id="sesion_password"
          nombre="password"
          etiqueta={msg("rot.contrasena")}
          autocompletar="current-password"
        />
        <div>
          <Button type="submit" textoTrabajando={msg("cuenta.ingresando")}>
            {msg("rot.ingresar")}
          </Button>
        </div>
      </form>
    </Callout>
  );
}
