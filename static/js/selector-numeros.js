/* Selector de números de la jugada: mejora progresiva (R-10).
   Sin JavaScript, el formulario funciona igual con las casillas; el servidor repite todas
   las validaciones (AC-4.2 a AC-4.6).
   [003] R-13, HU-11: los textos salen del catálogo; el servidor los escribe en data-msg-* del
   selector (#selector-numeros) y aquí solo se completan sus variables ({n}, {nn}, {modalidades}). */
(function () {
  "use strict";

  var form = document.getElementById("form-jugada");
  if (!form) { return; }

  var casillas = Array.prototype.slice.call(form.querySelectorAll('input[name="numeros"]'));
  var contador = document.getElementById("contador-numeros");
  var mensaje = document.getElementById("mensaje-selector");
  var escrito = form.querySelector('input[name="numero_escrito"]');
  var agregar = document.getElementById("agregar-numero");
  var concurso = form.querySelector('select[name="concurso"]');
  var vista = document.getElementById("vista-modalidades");
  var MAXIMO = 6;
  var selector = document.getElementById("selector-numeros");
  var textos = (selector && selector.dataset) || {};

  function texto(nombre, valores) {
    return (textos[nombre] || "").replace(/\{(\w+)\}/g, function (_, clave) {
      return valores && valores[clave] !== undefined ? valores[clave] : "{" + clave + "}";
    });
  }

  function dosDigitos(n) { return (n < 10 ? "0" : "") + n; }
  function marcadas() { return casillas.filter(function (c) { return c.checked; }); }
  function avisar(texto) { mensaje.textContent = texto || ""; }

  function actualizarContador() {
    var faltan = MAXIMO - marcadas().length;
    contador.textContent = faltan > 0 ? texto("msgFaltan", { n: faltan }) : texto("msgCompletos");
  }

  casillas.forEach(function (casilla) {
    casilla.addEventListener("change", function () {
      if (casilla.checked && marcadas().length > MAXIMO) {
        casilla.checked = false;
        avisar(texto("msgExactamenteSeis"));
      } else {
        avisar("");
      }
      actualizarContador();
    });
  });

  function agregarEscrito() {
    var texto = (escrito.value || "").trim();
    if (!/^\d{1,2}$/.test(texto) || parseInt(texto, 10) > 45) {
      avisar(texto("msgFueraDeRango"));
      return;
    }
    var valor = dosDigitos(parseInt(texto, 10));
    var casilla = casillas.filter(function (c) { return c.value === valor; })[0];
    if (casilla.checked) {
      avisar(texto("msgRepetido", { nn: valor }));
      return;
    }
    if (marcadas().length >= MAXIMO) {
      avisar(texto("msgExactamenteSeis"));
      return;
    }
    casilla.checked = true;
    escrito.value = "";
    avisar("");
    actualizarContador();
  }

  if (escrito && agregar) {
    agregar.hidden = false;
    agregar.addEventListener("click", agregarEscrito);
    escrito.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); agregarEscrito(); }
    });
    form.addEventListener("submit", function () {
      /* Un número escrito sin agregar se marca antes de enviar; si es inválido, lo valida el servidor. */
      if ((escrito.value || "").trim()) { agregarEscrito(); }
    });
  }

  if (concurso && vista) {
    concurso.addEventListener("change", function () {
      var opcion = concurso.options[concurso.selectedIndex];
      var modalidades = opcion && opcion.getAttribute("data-modalidades");
      vista.textContent = modalidades
        ? texto("msgParticipa", { modalidades: modalidades })
        : texto("msgAyudaModalidades");
    });
  }

  if (mensaje) { mensaje.setAttribute("role", "status"); }
  actualizarContador();
})();
