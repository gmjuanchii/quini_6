"""Servidor de fuentes de prueba para la verificación manual ([002] R-11, quickstart §5).

**Nunca se despliega.** Sirve copias editadas de páginas de F1, F2 y F3 desde
``tests/fuentes_prueba/escenarios/<escenario>/`` según su ``escenario.json``::

    {
      "descripcion": "…",
      "rutas": {
        "/f2/sorteos": {"pagina": "f2/listado.html"},
        "/f2/sorteos/3423": {"codigo": 500, "pagina": "f2/error-500.html"},
        "/f3/sorteos/3425": {"pagina": "f3/sorteo-3425.html", "demora": 15}
      }
    }

``codigo`` es 200 por omisión y ``demora`` (segundos) es 0. Una dirección no declarada responde
404. Quien verifica puede editar las páginas y el JSON para provocar otros casos.

Uso (desde la raíz del proyecto)::

    python -m tests.fuentes_prueba.servidor --escenario normal --puerto 8765

y en ``.env``: ``QUINI6_FUENTE_F1_URL=http://127.0.0.1:8765/f1`` (ídem F2 y F3).
"""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ESCENARIOS = Path(__file__).resolve().parent / "escenarios"
PUERTO = 8765


def cargar_escenario(nombre: str) -> tuple[Path, dict]:
    carpeta = ESCENARIOS / nombre
    datos = json.loads((carpeta / "escenario.json").read_text(encoding="utf-8"))
    return carpeta, datos


def crear_servidor(nombre: str, puerto: int = PUERTO) -> ThreadingHTTPServer:
    carpeta, escenario = cargar_escenario(nombre)
    rutas: dict[str, dict] = escenario["rutas"]

    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, formato, *args):
            print(f"[{nombre}] {self.address_string()} {formato % args}")

        def do_GET(self):
            ruta = urlsplit(self.path).path
            regla = rutas.get(ruta)
            if regla is None:
                self._responder(404, b"")
                return
            if regla.get("demora"):
                time.sleep(float(regla["demora"]))
            cuerpo = b""
            if regla.get("pagina"):
                cuerpo = (carpeta / regla["pagina"]).read_bytes()
            self._responder(int(regla.get("codigo", 200)), cuerpo)

        def _responder(self, codigo: int, cuerpo: bytes):
            self.send_response(codigo)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            try:
                self.wfile.write(cuerpo)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass  # el cliente cortó por su límite de espera

    return ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)


def main(argumentos=None) -> None:
    parser = argparse.ArgumentParser(description="Servidor de fuentes de prueba (spec 002).")
    parser.add_argument("--escenario", default="normal", help="Carpeta de escenarios/")
    parser.add_argument("--puerto", type=int, default=PUERTO)
    opciones = parser.parse_args(argumentos)
    servidor = crear_servidor(opciones.escenario, opciones.puerto)
    _, escenario = cargar_escenario(opciones.escenario)
    print(f"Escenario «{opciones.escenario}»: {escenario.get('descripcion', '')}")
    print(f"Escuchando en http://127.0.0.1:{opciones.puerto}/ (Ctrl+C para terminar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
