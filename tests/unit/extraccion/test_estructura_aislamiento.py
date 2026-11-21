"""[002] RN-41, R-07: prueba estructural de imports (T062).

Ningún módulo de ``extracciones/`` ni de ``dominio/extraccion/`` importa ``resultados`` ni
``jugadas``; ``dominio/extraccion/`` y ``extracciones/fuentes/`` no importan Django.
"""

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]


def modulos(*carpetas):
    for carpeta in carpetas:
        yield from sorted((RAIZ / carpeta).rglob("*.py"))


def importados(ruta: Path) -> set[str]:
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
            nombres.add(nodo.module.split(".")[0])
    return nombres


@pytest.mark.parametrize(
    "ruta", list(modulos("extracciones", "dominio/extraccion")), ids=lambda p: p.name
)
def test_rn_41_no_importa_resultados_ni_jugadas(ruta):
    assert not importados(ruta) & {"resultados", "jugadas"}


@pytest.mark.parametrize(
    "ruta", list(modulos("dominio/extraccion", "extracciones/fuentes")), ids=lambda p: p.name
)
def test_r_07_dominio_y_fuentes_sin_django(ruta):
    assert "django" not in importados(ruta)


def test_hay_modulos_para_revisar():
    assert len(list(modulos("extracciones"))) > 10
