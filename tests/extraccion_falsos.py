"""Dobles de prueba de la extracción histórica ([002] T018). Las pruebas nunca consultan
internet: el cliente falso responde por dirección con copias de páginas reales
(``tests/fixtures/fuentes/``) o con textos armados a partir de ellas."""

from __future__ import annotations

import threading
from datetime import UTC, date, datetime
from pathlib import Path

from dominio.extraccion.tipos import Fuente
from extracciones.cliente_http import RespuestaHttp
from extracciones.fuentes.fichas import FICHAS

FIXTURES = Path(__file__).parent / "fixtures" / "fuentes"
MESES = (
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre"
).split()
DIAS = "lunes martes miércoles jueves viernes sábado domingo".split()

#: Momento fijo de las consultas falsas (las pruebas comparan textos de procedencia).
MOMENTO = datetime(2026, 11, 19, 13, 15, 2, tzinfo=UTC)


def leer(relativa: str) -> str:
    return (FIXTURES / relativa).read_text(encoding="utf-8")


class LimitadorSinEspera:
    """Limitador que nunca espera (pruebas)."""

    def esperar_turno(self, sitio: str) -> None:
        return None


class ClienteHttpFalso:
    """Responde por dirección con (código, texto) o con un error simulado.

    Registra las direcciones pedidas. Las no declaradas responden ``defecto``.
    """

    def __init__(self, defecto: tuple[int | None, str] = (404, "")):
        self.respuestas: dict[str, tuple[int | None, str | None, str | None]] = {}
        self.defecto = defecto
        self.pedidas: list[str] = []
        self._candado = threading.Lock()

    def responder(self, url: str, codigo: int | None = 200, texto: str = "", error=None):
        self.respuestas[url] = (codigo, texto, error)
        return self

    def archivo(self, url: str, relativa: str, codigo: int = 200):
        return self.responder(url, codigo, leer(relativa))

    def demora(self, url: str):
        """Límite de espera vencido (NFR-006)."""
        return self.responder(url, None, None, "TimeoutError: timed out")

    def obtener(self, fuente: Fuente, url: str) -> RespuestaHttp:
        with self._candado:
            self.pedidas.append(url)
        codigo, texto, error = self.respuestas.get(url, (*self.defecto, None))
        if error:
            return RespuestaHttp(None, None, error, MOMENTO)
        return RespuestaHttp(codigo, texto, None, MOMENTO)


# -- Páginas armadas a partir de las copias reales -------------------------------------


#: Copias reales disponibles como base de las páginas armadas.
FECHAS_BASE = {
    2211: date(2014, 12, 17),
    3398: date(2026, 8, 9),
    3426: date(2026, 11, 15),
    3427: date(2026, 11, 18),
}
HOY = date(2026, 11, 19)


def _fecha_larga(fecha: date) -> str:
    return f"{DIAS[fecha.weekday()]} {fecha.day:02d} de {MESES[fecha.month - 1]} de {fecha.year}"


def pagina(fuente: Fuente, numero: int, fecha: date, base: int = 3426) -> str:
    """Página de detalle de ``fuente`` con el número y la fecha cambiados (datos del ``base``)."""
    carpeta = fuente.value.lower()
    texto = leer(f"{carpeta}/sorteo-{base}.html")
    fecha_base = FECHAS_BASE[base]
    texto = texto.replace(str(base), str(numero))
    texto = texto.replace(fecha_base.strftime("%d/%m/%Y"), fecha.strftime("%d/%m/%Y"))
    texto = texto.replace(fecha_base.strftime("%d-%m-%Y"), fecha.strftime("%d-%m-%Y"))
    texto = texto.replace(_fecha_larga(fecha_base), _fecha_larga(fecha))
    return texto


def listado_f2(sorteos: dict[int, date]) -> str:
    enlaces = "".join(
        f'<p><a href="/sorteos/{n}" class="btn">Quini Sorteo {n} <br /> {f:%d/%m/%Y}</a></p>'
        for n, f in sorted(sorteos.items(), reverse=True)
    )
    return f"<html><body><h1>Quini 6 Últimos 20 sorteos</h1>{enlaces}</body></html>"


def listado_f1(sorteos: dict[int, date]) -> str:
    base = FICHAS[Fuente.F1].url_base
    enlaces = "".join(
        f"<p><a href='{base}/quini6/sorteo-{n}-del-dia-{f:%d-%m-%Y}.htm'>"
        f"Sorteo {n}<br/>del {f:%d-%m-%Y}</a></p>"
        for n, f in sorted(sorteos.items())
    )
    return f"<html><body><h1>Sorteos Anteriores</h1>{enlaces}</body></html>"


def listado_f3(sorteos: dict[int, date]) -> str:
    filas = "".join(
        f'<tr><th scope="row">{f.day}/{f.month}/{f.year}</th><td>01 02 03 04 05 06</td>'
        f'<td><a href="/sorteos/{n}">Ver</a></td></tr>'
        for n, f in sorted(sorteos.items(), reverse=True)
    )
    return f"<html><body><table><tbody>{filas}</tbody></table></body></html>"


def url_sorteo(fuente: Fuente, numero: int, fecha: date | None = None) -> str:
    return FICHAS[fuente].url_sorteo(numero, fecha)


def url_listado(fuente: Fuente) -> str:
    return FICHAS[fuente].url_listado()


def cliente_con_sorteos(
    sorteos: dict[int, date], fuentes=(Fuente.F2,), base: int = 3426
) -> ClienteHttpFalso:
    """Cliente con listados y páginas de detalle coherentes para las ``fuentes`` indicadas."""
    cliente = ClienteHttpFalso()
    listados = {Fuente.F1: listado_f1, Fuente.F2: listado_f2, Fuente.F3: listado_f3}
    for fuente in fuentes:
        cliente.responder(url_listado(fuente), 200, listados[fuente](sorteos))
        for numero, fecha in sorteos.items():
            url = url_sorteo(fuente, numero, fecha if fuente is Fuente.F1 else None)
            cliente.responder(url, 200, pagina(fuente, numero, fecha, base))
    return cliente


def fichas_de(*fuentes: Fuente):
    return {f: FICHAS[f] for f in fuentes}


def procesar_pendientes(cliente, fichas=None) -> None:
    """Ejecuta el trabajador una vez con el cliente indicado ([002] T018)."""
    from extracciones import servicios
    from extracciones.management.commands.procesar_extracciones import extracciones_pendientes

    for extraccion in extracciones_pendientes():
        servicios.procesar_extraccion(extraccion, cliente, fichas or FICHAS)
