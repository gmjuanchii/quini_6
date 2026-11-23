/*
 * QUINI_6 — componentes de interfaz de la Etapa 1 ([003] R-06): Alpine.js + HTMX, siempre como
 * mejora progresiva. Sin este archivo, toda página sigue funcionando con su versión básica (NFR-007).
 * Se carga con "defer" antes que Alpine para registrar los componentes en "alpine:init".
 */
(function () {
  "use strict";

  /** Valor de una cookie (para el token CSRF y la preferencia de tema). */
  function leerCookie(nombre) {
    var partes = document.cookie ? document.cookie.split("; ") : [];
    for (var i = 0; i < partes.length; i++) {
      var igual = partes[i].indexOf("=");
      if (partes[i].slice(0, igual) === nombre) {
        return decodeURIComponent(partes[i].slice(igual + 1));
      }
    }
    return null;
  }

  window.quini6 = window.quini6 || {};
  window.quini6.leerCookie = leerCookie;

  // HTMX: token CSRF en cada pedido y sin caché de historial (páginas privadas, NFR-008).
  document.addEventListener("htmx:configRequest", function (evento) {
    var token = leerCookie("csrftoken");
    if (token) {
      evento.detail.headers["X-CSRFToken"] = token;
    }
  });
  document.addEventListener("DOMContentLoaded", function () {
    if (window.htmx) {
      window.htmx.config.historyCacheSize = 0;
      window.htmx.config.defaultSwapStyle = "outerHTML";
      window.htmx.config.scrollIntoViewOnBoost = false;
    }
  });

  // Registro de componentes Alpine (cada historia agrega los suyos).
  document.addEventListener("alpine:init", function () {
    var componentes = window.quini6.componentes || {};
    Object.keys(componentes).forEach(function (nombre) {
      window.Alpine.data(nombre, componentes[nombre]);
    });
  });

  window.quini6.componentes = window.quini6.componentes || {};
  window.quini6.registrar = function (nombre, fabrica) {
    window.quini6.componentes[nombre] = fabrica;
  };
})();

/* ---------------------------------------------------------------------------------------------
 * [003] HU-02: menú de acciones (⋮) y diálogo de confirmación.
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  var registrar = window.quini6.registrar;

  // ActionMenu (AC-2.1, AC-2.2, FR-007): <details> nativo mejorado.
  registrar("menuAcciones", function () {
    return {
      id: Math.random().toString(36).slice(2),
      opciones: function () {
        return Array.prototype.slice.call(this.$refs.menu.querySelectorAll('[role="menuitem"]'));
      },
      alCambiar: function () {
        if (!this.$root.open) return;
        window.dispatchEvent(new CustomEvent("menu-abierto", { detail: this.id }));
        var self = this;
        this.$nextTick(function () {
          var primera = self.opciones()[0];
          if (primera) primera.focus();
        });
      },
      cerrar: function (devolverFoco) {
        if (!this.$root.open) return;
        this.$root.open = false;
        if (devolverFoco) this.$refs.disparador.focus();
      },
      otroAbierto: function (evento) {
        if (evento.detail !== this.id) this.cerrar(false);
      },
      mover: function (paso) {
        var opciones = this.opciones();
        if (!opciones.length) return;
        var indice = opciones.indexOf(document.activeElement);
        if (paso === "primero") indice = 0;
        else if (paso === "ultimo") indice = opciones.length - 1;
        else indice = (indice + paso + opciones.length) % opciones.length;
        opciones[indice].focus();
      },
    };
  });

  // ConfirmDialog (AC-2.3, AC-2.4, FR-008): carga la confirmación del enlace y la abre en <dialog>.
  registrar("dialogoConfirmar", function () {
    return {
      origen: null,
      init: function () {
        var self = this;
        document.addEventListener("click", function (evento) {
          var enlace = evento.target.closest && evento.target.closest("a[data-confirmar]");
          if (!enlace || evento.button !== 0 || evento.ctrlKey || evento.metaKey || evento.shiftKey) return;
          evento.preventDefault();
          var menu = enlace.closest("details");
          self.origen = menu ? menu.querySelector("summary") : enlace;
          if (menu) menu.open = false;
          self.abrir(enlace.href);
        });
      },
      abrir: function (url) {
        var self = this;
        var contenido = this.$refs.contenido;
        contenido.setAttribute("aria-busy", "true");
        fetch(url, { headers: { "HX-Request": "true" }, credentials: "same-origin" })
          .then(function (respuesta) {
            if (!respuesta.ok || respuesta.redirected) throw new Error("sin confirmación");
            return respuesta.text();
          })
          .then(function (html) {
            contenido.innerHTML = html;
            contenido.removeAttribute("aria-busy");
            if (window.htmx) window.htmx.process(contenido);
            self.$root.showModal();
            var cancelar = contenido.querySelector("[data-cancelar]");
            if (cancelar) cancelar.focus();
          })
          .catch(function () {
            window.location.href = url; // versión básica: la página aparte
          });
      },
      alHacerClic: function (evento) {
        if (evento.target === this.$root) {
          this.$root.close(); // clic en el fondo
          return;
        }
        if (evento.target.closest("[data-cancelar]")) {
          evento.preventDefault();
          this.$root.close();
        }
      },
      alCancelar: function () {
        // Escape: el navegador cierra el diálogo y se dispara "close".
      },
      alCerrar: function () {
        this.$refs.contenido.innerHTML = "";
        if (this.origen) this.origen.focus();
        this.origen = null;
      },
    };
  });
})();

/* ---------------------------------------------------------------------------------------------
 * [003] HU-03, FR-034: estado de trabajo de los botones y avisos breves (RN-09).
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  var registrar = window.quini6.registrar;
  var DURACION = 6000;
  var BORDES = { success: "border-success", info: "border-primary", warning: "border-warning", error: "border-danger" };

  function botonDe(formulario, enviador) {
    if (enviador && enviador.matches && enviador.matches("button[data-texto-trabajando]")) return enviador;
    return formulario.querySelector("button[type=submit][data-texto-trabajando], button:not([type])[data-texto-trabajando]");
  }

  function trabajando(boton) {
    if (!boton || boton.getAttribute("aria-busy") === "true") return;
    var texto = boton.querySelector("[data-texto-boton]");
    boton.dataset.textoOriginal = texto ? texto.textContent : "";
    if (!texto) {
      // Botón escrito a mano (sin <span data-texto-boton>): se reemplaza y luego se restaura todo.
      boton.dataset.htmlOriginal = boton.innerHTML;
      boton.textContent = boton.dataset.textoTrabajando;
    }
    boton.setAttribute("aria-busy", "true");
    boton.setAttribute("aria-disabled", "true");
    if (texto) texto.textContent = boton.dataset.textoTrabajando;
    var plantilla = document.getElementById("icono-cargando");
    if (plantilla) {
      var icono = plantilla.content.firstElementChild.cloneNode(true);
      icono.setAttribute("data-icono-trabajando", "");
      boton.insertBefore(icono, boton.firstChild);
    }
    // Se deshabilita después del envío para no quitar el botón de los datos del formulario.
    window.setTimeout(function () { boton.disabled = true; }, 0);
  }

  function restaurar(boton) {
    if (!boton || boton.getAttribute("aria-busy") !== "true") return;
    var texto = boton.querySelector("[data-texto-boton]");
    if (texto && boton.dataset.textoOriginal) texto.textContent = boton.dataset.textoOriginal;
    var icono = boton.querySelector("[data-icono-trabajando]");
    if (icono) icono.remove();
    if (boton.dataset.htmlOriginal !== undefined) {
      boton.innerHTML = boton.dataset.htmlOriginal;
      delete boton.dataset.htmlOriginal;
    }
    boton.removeAttribute("aria-busy");
    boton.removeAttribute("aria-disabled");
    boton.disabled = false;
  }

  // FR-034, AC-3.1, AC-6.6: al enviar, el botón muestra "…ando…" y no se puede pulsar de nuevo.
  document.addEventListener("submit", function (evento) {
    var formulario = evento.target;
    if (!formulario.matches || !formulario.matches("form[data-trabajando]")) return;
    if (formulario.dataset.invalido === "true") return; // la validación previa impidió el envío
    trabajando(botonDe(formulario, evento.submitter));
  });
  document.addEventListener("htmx:afterRequest", function (evento) {
    var formulario = evento.detail && evento.detail.elt;
    if (formulario && formulario.matches && formulario.matches("form[data-trabajando]")) {
      restaurar(botonDe(formulario));
    }
  });
  window.addEventListener("pageshow", function () {
    document.querySelectorAll("button[aria-busy=true]").forEach(restaurar);
  });
  // FR-031: tras un envío que no salió (sin conexión), el botón vuelve a su estado normal.
  document.addEventListener("quini6:restaurar", function (evento) { restaurar(evento.target); });

  /** [003] T125: el aviso sale con su transición (200 ms; 0 con "reducir movimiento"). */
  function quitar(aviso) {
    var duracion = parseFloat(getComputedStyle(aviso).transitionDuration) || 0;
    aviso.classList.add("saliendo");
    window.setTimeout(function () { aviso.remove(); }, duracion * 1000);
  }

  // Toast (RN-09): 6 s salvo errores; botón "Cerrar aviso"; sin robar el foco.
  registrar("avisos", function () {
    return {
      // [003] AC-10.3: los mensajes de la página (Callout con data-aviso) pasan a Toast al cargar.
      init: function () {
        var self = this;
        document.querySelectorAll("main [data-aviso]").forEach(function (callout) {
          var texto = callout.querySelector("[data-texto-aviso]");
          self.mostrar({ tipo: callout.getAttribute("data-aviso"), texto: texto ? texto.textContent : "" });
          callout.remove();
        });
        var region = document.querySelector("main [data-mensajes]");
        if (region && !region.children.length) region.remove();
      },
      mostrar: function (detalle) {
        var datos = (detalle && detalle.value) || detalle || {};
        if (!datos.texto) return;
        var tipo = BORDES[datos.tipo] ? datos.tipo : "info";
        var plantilla = document.getElementById("plantilla-aviso");
        var aviso = plantilla.content.firstElementChild.cloneNode(true);
        aviso.classList.add(BORDES[tipo]);
        aviso.dataset.tipo = tipo;
        aviso.querySelector("[data-texto]").textContent = datos.texto;
        var icono = document.getElementById("icono-aviso-" + tipo);
        if (icono) aviso.querySelector("[data-icono]").appendChild(icono.content.firstElementChild.cloneNode(true));
        var enlace = aviso.querySelector("[data-enlace]");
        if (datos.enlace && window.location.pathname !== new URL(datos.enlace, window.location.href).pathname) {
          enlace.href = datos.enlace;
          enlace.hidden = false;
        }
        aviso.querySelector("[data-cerrar]").addEventListener("click", function () { quitar(aviso); });
        (tipo === "error" ? this.$refs.urgentes : this.$refs.educados).appendChild(aviso);
        if (tipo !== "error") window.setTimeout(function () { quitar(aviso); }, DURACION);
      },
    };
  });
})();

/* ---------------------------------------------------------------------------------------------
 * [003] HU-04: campos de fecha (DateField, DateRangePicker) con el calendario Cally (R-07).
 * El servidor genera <input type="date">; aquí se convierte en un campo dd/mm/aaaa con barras
 * automáticas ([002] D-27: nunca showPicker) y un calendario propio anclado al campo.
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  var registrar = window.quini6.registrar;
  var DMA = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/;
  var ISO = /^(\d{4})-(\d{2})-(\d{2})$/;

  function dos(n) { return (n < 10 ? "0" : "") + n; }

  /** Texto → { estado: "vacia" | "valida" | "inexistente" | "formato", iso, texto }. */
  function analizarFecha(texto) {
    texto = (texto || "").trim();
    if (!texto) return { estado: "vacia" };
    var m = DMA.exec(texto), dia, mes, anio;
    if (m) { dia = +m[1]; mes = +m[2]; anio = +m[3]; }
    else if ((m = ISO.exec(texto))) { anio = +m[1]; mes = +m[2]; dia = +m[3]; }
    else return { estado: "formato" };
    var legible = dos(dia) + "/" + dos(mes) + "/" + anio;
    var fecha = new Date(Date.UTC(anio, mes - 1, dia));
    if (fecha.getUTCFullYear() !== anio || fecha.getUTCMonth() !== mes - 1 || fecha.getUTCDate() !== dia) {
      return { estado: "inexistente", texto: legible };
    }
    return { estado: "valida", iso: anio + "-" + dos(mes) + "-" + dos(dia), texto: legible };
  }

  function aIso(texto) { var f = analizarFecha(texto); return f.estado === "valida" ? f.iso : ""; }
  function aDma(iso) { var f = analizarFecha(iso); return f.estado === "valida" ? f.texto : iso || ""; }

  /** AC-4.2: 01012025 → 01/01/2025 (las barras se agregan solas); una fecha AAAA-MM-DD pegada
   * se convierte a dd/mm/aaaa. */
  function enmascarar(valor) {
    if (ISO.test(valor.trim())) return aDma(valor.trim()) || valor.trim();
    var digitos = valor.replace(/\D/g, "").slice(0, 8);
    if (digitos.length > 4) return digitos.slice(0, 2) + "/" + digitos.slice(2, 4) + "/" + digitos.slice(4);
    if (digitos.length > 2) return digitos.slice(0, 2) + "/" + digitos.slice(2);
    return digitos;
  }

  window.quini6.fechas = { analizar: analizarFecha, aIso: aIso, aDma: aDma };

  function validar(entrada) {
    if (window.quini6.validarCampo) window.quini6.validarCampo(entrada);
  }

  /** [003] R-24: Cally se carga recién cuando hace falta (al enfocar un campo de fecha o abrir
   * el calendario), no en cada página. Los <calendar-*> ya presentes se actualizan al definirse. */
  var cally = null;
  function cargarCally() {
    if (window.customElements && window.customElements.get("calendar-date")) return Promise.resolve();
    if (!cally) cally = import(document.documentElement.getAttribute("data-cally"));
    return cally;
  }
  document.addEventListener("focusin", function (evento) {
    if (evento.target.closest && evento.target.closest("[data-campo-fecha]")) cargarCally();
  });

  function enfocarCalendario(calendario) {
    window.setTimeout(function () {
      if (calendario && calendario.focus) calendario.focus();
    }, 0);
  }

  // DateField (AC-4.1, AC-4.2, AC-4.6, AC-4.7, FR-010, FR-013).
  registrar("campoFecha", function (opciones) {
    opciones = opciones || {};
    return {
      abierto: false,
      init: function () {
        var entrada = this.$refs.entrada;
        var crudo = entrada.getAttribute("value") || "";
        entrada.type = "text";
        entrada.value = aDma(crudo);
        entrada.setAttribute("inputmode", "numeric");
        entrada.setAttribute("placeholder", "dd/mm/aaaa");
        entrada.setAttribute("maxlength", "10");
      },
      alEscribir: function (evento) {
        if (evento.inputType && evento.inputType.indexOf("delete") === 0) return; // deja borrar las barras
        var entrada = evento.target;
        var nuevo = enmascarar(entrada.value);
        if (nuevo !== entrada.value) entrada.value = nuevo;
      },
      abrir: function () {
        var entrada = this.$refs.entrada;
        if (opciones.enPeriodo) {
          this.$dispatch("abrir-periodo", { entrada: entrada });
          return;
        }
        var self = this;
        cargarCally().then(function () {
          var calendario = self.$refs.calendario;
          var iso = aIso(entrada.value);
          calendario.value = iso;
          var foco = iso || entrada.getAttribute("max") || "";
          if (foco) calendario.focusedDate = foco;
          self.abierto = true;
          enfocarCalendario(calendario);
        });
      },
      cerrar: function (devolverFoco) {
        if (!this.abierto) return;
        this.abierto = false;
        if (devolverFoco) this.$refs.entrada.focus();
      },
      elegir: function (iso) {
        if (!iso) return;
        var entrada = this.$refs.entrada;
        entrada.value = aDma(iso);
        entrada.dispatchEvent(new Event("change", { bubbles: true }));
        validar(entrada);
        this.cerrar(true);
      },
    };
  });

  // DateRangePicker (AC-4.3, AC-4.4, FR-011): un único calendario de rango para los dos campos.
  registrar("periodo", function () {
    return {
      abierto: false,
      origen: null,
      entradas: function () {
        return Array.prototype.slice.call(this.$root.querySelectorAll("[data-campo-fecha] input"));
      },
      abrir: function (detalle) {
        var self = this;
        cargarCally().then(function () {
          var entradas = self.entradas();
          var desde = aIso(entradas[0].value), hasta = aIso(entradas[1].value);
          var calendario = self.$refs.calendario;
          self.origen = (detalle && detalle.entrada) || entradas[0];
          calendario.value = desde && hasta && desde <= hasta ? desde + "/" + hasta : "";
          var preferida = self.origen === entradas[1] ? hasta || desde : desde || hasta;
          var foco = preferida || calendario.getAttribute("max") || "";
          if (foco) calendario.focusedDate = foco;
          self.abierto = true;
          enfocarCalendario(calendario);
        });
      },
      cerrar: function (devolverFoco) {
        if (!this.abierto) return;
        this.abierto = false;
        if (devolverFoco && this.origen) this.origen.focus();
      },
      completar: function (desde, hasta) {
        var entradas = this.entradas();
        entradas[0].value = aDma(desde);
        entradas[1].value = aDma(hasta);
        entradas.forEach(function (entrada) {
          entrada.dispatchEvent(new Event("change", { bubbles: true }));
          validar(entrada);
        });
        return entradas;
      },
      elegir: function (valor) {
        var partes = (valor || "").split("/");
        if (partes.length !== 2) return;
        var entradas = this.completar(partes[0], partes[1]);
        this.origen = entradas[1];
        this.cerrar(true);
      },
      // AC-4.4: el atajo completa las dos fechas sin navegar y se pueden modificar.
      aplicar: function (enlace) {
        var entradas = this.completar(enlace.dataset.desde, enlace.dataset.hasta);
        entradas[0].focus();
      },
    };
  });
})();

/* ---------------------------------------------------------------------------------------------
 * [003] FR-033, R-13: validación previa de los formularios <form novalidate data-validar-formulario>.
 * Cada campo declara sus reglas en data-validar con los textos ya resueltos por el servidor, que
 * repite la misma validación: ninguna regla existe solo en el navegador.
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  var CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function reglasDe(campo) {
    try {
      return JSON.parse(campo.getAttribute("data-validar")) || [];
    } catch (error) {
      return [];
    }
  }

  function fechas() { return window.quini6.fechas; }

  /** Primer mensaje que corresponde al valor del campo, o "" si es válido. */
  function errorDe(campo) {
    var valor = (campo.value || "").trim();
    var reglas = reglasDe(campo);
    for (var i = 0; i < reglas.length; i++) {
      var regla = reglas[i];
      if (regla.regla === "requerido") {
        if (!valor) return regla.texto;
        continue;
      }
      if (!valor) continue;
      if (regla.regla === "fecha") {
        var fecha = fechas().analizar(valor);
        if (fecha.estado === "formato") return regla.texto;
        if (fecha.estado === "inexistente") return regla.texto_inexistente.replace("{fecha}", fecha.texto);
      } else if (regla.regla === "max" || regla.regla === "min") {
        var iso = fechas().aIso(valor);
        if (iso && (regla.regla === "max" ? iso > regla.valor : iso < regla.valor)) return regla.texto;
      } else if (regla.regla === "fin_no_anterior_a") {
        var otro = document.getElementById(regla.campo);
        var inicio = otro ? fechas().aIso(otro.value) : "";
        var fin = fechas().aIso(valor);
        if (inicio && fin && fin < inicio) return regla.texto.replace("{fecha}", fechas().aDma(inicio));
      } else if (regla.regla === "rango_00_45") {
        if (!/^\d{1,2}$/.test(valor) || +valor > 45) return regla.texto;
      } else if (regla.regla === "correo") {
        if (!CORREO.test(valor)) return regla.texto;
      }
    }
    return "";
  }

  /** Mismo marcado que el error del servidor (templates/_campo.html). */
  function mostrar(campo, texto) {
    var lugar = document.getElementById(campo.id + "_error");
    if (!lugar) return;
    var envoltorio = campo.closest("[data-campo]");
    var ids = (campo.getAttribute("aria-describedby") || "").split(/\s+/).filter(function (id) {
      return id && id !== lugar.id;
    });
    var span = lugar.querySelector("[data-texto-error]");
    if (texto) {
      if (span) span.textContent = texto;
      lugar.hidden = false;
      campo.setAttribute("aria-invalid", "true");
      ids.push(lugar.id);
      if (envoltorio) envoltorio.classList.add("campo--error");
    } else {
      if (span) span.textContent = "";
      lugar.hidden = true;
      campo.removeAttribute("aria-invalid");
      if (envoltorio) envoltorio.classList.remove("campo--error");
    }
    if (ids.length) campo.setAttribute("aria-describedby", ids.join(" "));
    else campo.removeAttribute("aria-describedby");
  }

  function validarCampo(campo) {
    var texto = errorDe(campo);
    mostrar(campo, texto);
    return !texto;
  }
  window.quini6.validarCampo = validarCampo;

  function enFormularioValidado(campo) {
    return Boolean(campo.matches && campo.matches("[data-validar]") && campo.form &&
      campo.form.hasAttribute("data-validar-formulario"));
  }

  // Al salir del campo: solo si tiene algo escrito o ya mostraba un error ("Falta…" se avisa al
  // enviar), y no cuando el foco pasa al botón de su propio calendario.
  document.addEventListener("focusout", function (evento) {
    var campo = evento.target;
    if (!enFormularioValidado(campo)) return;
    var destino = evento.relatedTarget;
    var envoltorio = campo.closest("[data-campo]");
    if (destino && envoltorio && envoltorio.contains(destino) && destino.type !== "submit") return;
    if ((campo.value || "").trim() || campo.getAttribute("aria-invalid") === "true") validarCampo(campo);
    campo.form.querySelectorAll("[data-validar]").forEach(function (otro) {
      if (otro === campo || !(otro.value || "").trim()) return;
      var depende = reglasDe(otro).some(function (r) {
        return r.regla === "fin_no_anterior_a" && r.campo === campo.id;
      });
      if (depende) validarCampo(otro);
    });
  });

  // Al enviar: si hay errores no se envía, se resume la cantidad y el foco va al primero.
  document.addEventListener(
    "submit",
    function (evento) {
      var formulario = evento.target;
      if (!formulario.matches || !formulario.matches("form[data-validar-formulario]")) return;
      var campos = Array.prototype.slice.call(formulario.querySelectorAll("[data-validar]"));
      var conError = campos.filter(function (campo) { return !campo.disabled && !validarCampo(campo); });
      var resumen = formulario.querySelector("[data-resumen-validacion]");
      if (resumen) resumen.remove();
      if (!conError.length) {
        formulario.dataset.invalido = "false";
        return;
      }
      evento.preventDefault();
      evento.stopImmediatePropagation(); // tampoco lo envía HTMX ni cambia el botón a "…ando…"
      formulario.dataset.invalido = "true";
      var plantilla = document.getElementById("plantilla-no-avanza");
      if (plantilla) {
        resumen = plantilla.content.firstElementChild.cloneNode(true);
        resumen.setAttribute("data-resumen-validacion", "");
        var texto = resumen.querySelector("[data-texto-aviso]") || resumen;
        texto.textContent = texto.textContent.replace("{n}", conError.length);
        formulario.insertBefore(resumen, formulario.firstElementChild);
      }
      conError[0].focus();
    },
    true
  );
})();

/* ---------------------------------------------------------------------------------------------
 * [003] HU-05: menú "Menú" de pantallas chicas (AC-5.4) y menú de cuenta (AC-5.3).
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  var registrar = window.quini6.registrar;

  registrar("navegacion", function () {
    return {
      abierto: false,
      alternar: function () {
        this.abierto = !this.abierto;
      },
      cerrar: function (devolverFoco) {
        if (!this.abierto) return;
        this.abierto = false;
        if (devolverFoco) this.$refs.boton.focus();
      },
    };
  });

  registrar("menuCuenta", function () {
    return {
      abierto: false,
      alternar: function () {
        this.abierto = !this.abierto;
        if (this.abierto) {
          var self = this;
          this.$nextTick(function () { self.$refs.salir.focus(); });
        }
      },
      cerrar: function (devolverFoco) {
        if (!this.abierto) return;
        this.abierto = false;
        if (devolverFoco) this.$refs.boton.focus();
      },
    };
  });
})();

/* ---------------------------------------------------------------------------------------------
 * [003] HU-06, AC-6.2: mostrar u ocultar la contraseña y anunciar el cambio.
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  window.quini6.registrar("campoContrasena", function () {
    return {
      visible: false,
      anuncio: "",
      alternar: function (evento) {
        var boton = (evento && evento.currentTarget) || this.$root.querySelector("[data-mostrar-contrasena]");
        var entrada = this.$root.querySelector("input");
        this.visible = !this.visible;
        entrada.type = this.visible ? "text" : "password";
        this.anuncio = this.visible ? boton.dataset.textoVisible : boton.dataset.textoOculta;
      },
    };
  });
})();

/* ---------------------------------------------------------------------------------------------
 * [003] HU-12, R-14: tema claro, oscuro o según el dispositivo. Aplica data-theme al instante y
 * escribe la misma cookie que el servidor (POST /preferencias/tema/), sin recargar ni perder lo
 * escrito en la página.
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";
  var COOKIE = "quini6_tema";
  var DURACION = 400 * 24 * 60 * 60;

  window.quini6.registrar("selectorTema", function () {
    return {
      aplicar: function (valor) {
        var raiz = document.documentElement;
        var seguro = window.location.protocol === "https:" ? "; Secure" : "";
        if (valor === "claro" || valor === "oscuro") {
          raiz.setAttribute("data-theme", valor);
          document.cookie = COOKIE + "=" + valor + "; Path=/; Max-Age=" + DURACION + "; SameSite=Lax" + seguro;
        } else {
          raiz.removeAttribute("data-theme");
          document.cookie = COOKIE + "=; Path=/; Max-Age=0; SameSite=Lax" + seguro;
        }
      },
    };
  });
})();

/* ---------------------------------------------------------------------------------------------
 * [003] FR-031, Casos límite: sin conexión el formulario no se envía; se avisa junto al formulario y
 * "Reintentar" lo vuelve a enviar con la misma clave_idempotencia (un único efecto en el servidor).
 * ------------------------------------------------------------------------------------------- */
(function () {
  "use strict";

  function avisarSinConexion(formulario) {
    var plantilla = document.getElementById("plantilla-sin-conexion");
    if (!formulario || !plantilla) return;
    var anterior = formulario.querySelector("[data-sin-conexion]");
    if (anterior) anterior.remove();
    var aviso = plantilla.content.firstElementChild.cloneNode(true);
    aviso.querySelector("[data-reintentar]").addEventListener("click", function () {
      aviso.remove();
      if (formulario.requestSubmit) formulario.requestSubmit();
      else formulario.submit();
    });
    formulario.insertBefore(aviso, formulario.firstElementChild);
    document.querySelectorAll("button[aria-busy=true]").forEach(function (boton) {
      boton.dispatchEvent(new CustomEvent("quini6:restaurar", { bubbles: true }));
    });
    var reintentar = aviso.querySelector("[data-reintentar]");
    if (reintentar) reintentar.focus();
  }
  window.quini6.avisarSinConexion = avisarSinConexion;

  // Se registra después de la validación previa: solo llega aquí un formulario sin errores.
  document.addEventListener(
    "submit",
    function (evento) {
      var formulario = evento.target;
      if (!formulario.matches || !formulario.matches("form") || navigator.onLine !== false) return;
      if (formulario.method && formulario.method.toLowerCase() === "get") return;
      evento.preventDefault();
      evento.stopImmediatePropagation();
      avisarSinConexion(formulario);
    },
    true
  );

  document.addEventListener("htmx:sendError", function (evento) {
    var origen = evento.detail && evento.detail.elt;
    var formulario = origen && (origen.matches("form") ? origen : origen.closest("form"));
    if (formulario) avisarSinConexion(formulario);
  });
})();
