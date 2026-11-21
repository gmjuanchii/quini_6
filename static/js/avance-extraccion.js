/* Avance de una extracción en curso ([002] R-10, AC-1.2). Mejora progresiva, sin dependencias.
 * Cada 5 s pide la misma dirección y reemplaza solo el bloque de avance (región aria-live).
 * Cuando la respuesta ya no trae la marca "en curso", muestra la página completa con el resumen.
 * Sin JavaScript, el avance se actualiza al recargar. */
(function () {
  "use strict";
  var ID = "avance-extraccion";
  var INTERVALO = 5000;
  if (!document.getElementById(ID) || !window.fetch || !window.DOMParser) { return; }

  function actualizar() {
    fetch(window.location.href, { credentials: "same-origin", cache: "no-store" })
      .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
      .then(function (html) {
        var nuevo = new DOMParser().parseFromString(html, "text/html");
        var bloqueNuevo = nuevo.getElementById(ID);
        var bloqueActual = document.getElementById(ID);
        if (bloqueNuevo && bloqueNuevo.hasAttribute("data-en-curso")) {
          if (bloqueActual && bloqueActual.innerHTML !== bloqueNuevo.innerHTML) {
            bloqueActual.innerHTML = bloqueNuevo.innerHTML;
          }
          window.setTimeout(actualizar, INTERVALO);
          return;
        }
        var principalNuevo = nuevo.getElementById("contenido");
        var principalActual = document.getElementById("contenido");
        if (principalNuevo && principalActual) {
          principalActual.innerHTML = principalNuevo.innerHTML;
          principalActual.focus();
        } else {
          window.location.reload();
        }
      })
      .catch(function () { window.setTimeout(actualizar, INTERVALO); });
  }

  window.setTimeout(actualizar, INTERVALO);
})();
