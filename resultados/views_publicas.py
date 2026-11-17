"""Consulta pública de resultados (US1, FR-001 a FR-005). Sin sesión."""

from datetime import datetime

from django.shortcuts import redirect, render

from resultados import consultas
from resultados.models import Concurso

PAGINA_INEXISTENTE = "La página que buscás no existe"


def inicio(request):
    return redirect("/resultados/")


def _listado():
    concursos = consultas.con_versiones(Concurso.objects.order_by("-fecha_sorteo", "-numero"))
    return [
        {
            "concurso": c,
            "completitud": consultas.TEXTO_COMPLETITUD[consultas.completitud(c)],
        }
        for c in concursos
    ]


def resultados(request):
    ultimos, pendiente = consultas.ultimos_resultados()
    return render(
        request,
        "resultados/index.html",
        {
            "ultimos": consultas.vista_publica_concurso(ultimos) if ultimos else None,
            "pendiente": pendiente,
            "concursos": _listado(),
        },
    )


def buscar(request):
    numero = (request.GET.get("numero") or "").strip()
    fecha_texto = (request.GET.get("fecha") or "").strip()
    contexto = {"numero": numero, "fecha": fecha_texto}
    if numero:
        if not numero.isdigit():
            contexto["error"] = "Ingresá un número de concurso válido."
        elif Concurso.objects.filter(numero=int(numero)).exists():
            return redirect(f"/resultados/{int(numero)}/")
        else:
            contexto["mensaje"] = f"No hay información del concurso N.º {int(numero)}"
    elif fecha_texto:
        try:
            fecha = datetime.strptime(fecha_texto, "%d/%m/%Y").date()
        except ValueError:
            contexto["error"] = "Ingresá una fecha válida con el formato dd/mm/aaaa."
        else:
            concursos = consultas.con_versiones(
                Concurso.objects.filter(fecha_sorteo=fecha).order_by("-numero")
            )
            contexto["resultados"] = [
                {
                    "concurso": c,
                    "completitud": consultas.TEXTO_COMPLETITUD[consultas.completitud(c)],
                }
                for c in concursos
            ]
            if not contexto["resultados"]:
                contexto["mensaje"] = (
                    f"No hay información de concursos del {fecha.strftime('%d/%m/%Y')}"
                )
    else:
        return redirect("/resultados/")
    return render(request, "resultados/busqueda.html", contexto)


def detalle(request, numero: int):
    concurso = consultas.cargar_concurso(numero)
    if concurso is None:
        return render(request, "404.html", {"mensaje": PAGINA_INEXISTENTE}, status=404)
    return render(
        request,
        "resultados/detalle.html",
        {
            "vista": consultas.vista_publica_concurso(concurso),
            "concurso": concurso,
            "admite_jugadas": consultas.admite_jugadas(concurso),
        },
    )
