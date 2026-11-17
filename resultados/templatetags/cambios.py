"""Presentación de los valores del registro de cambios (AC-7.3)."""

from datetime import date
from decimal import Decimal

from django import template

from dominio.importes import formatear_pesos
from dominio.numeros import formatear
from dominio.tipos import Modalidad

register = template.Library()

_ROTULOS = {
    "ganadores": "ganadores",
    "importe_categoria": "importe destinado",
    "importe_individual": "importe individual",
    "pozo_vacante_acumulado": "pozo vacante o acumulado",
}


def _pesos(texto):
    return "no disponible" if texto is None else formatear_pesos(Decimal(texto))


@register.filter
def valor_cambio(valor):
    """Resume un ``valor_anterior`` o ``valor_nuevo`` en texto legible."""
    if not valor:
        return "—"
    if "numeros" in valor:
        return ", ".join(formatear(n) for n in valor["numeros"])
    if "categorias" in valor:
        partes = []
        if valor.get("sin_ganadores"):
            partes.append("Categoría ganadora: sin ganadores")
        elif valor.get("aciertos_categoria_ganadora") is not None:
            partes.append(f"Categoría ganadora: {valor['aciertos_categoria_ganadora']} aciertos")
        for cat in valor["categorias"]:
            datos = []
            for campo, rotulo in _ROTULOS.items():
                dato = cat.get(campo)
                if campo == "ganadores":
                    datos.append(f"{rotulo}: {'no disponible' if dato is None else dato}")
                else:
                    datos.append(f"{rotulo}: {_pesos(dato)}")
            partes.append(f"{cat['categoria']} ({', '.join(datos)})")
        return "; ".join(partes)
    if "numero" in valor:
        fecha = date.fromisoformat(valor["fecha_sorteo"]).strftime("%d/%m/%Y")
        modalidades = ", ".join(Modalidad(m).nombre for m in valor.get("modalidades", []))
        return f"N.º {valor['numero']}, sorteo del {fecha}, modalidades: {modalidades}"
    return str(valor)
