"""[003] AC-14.6: infra/no-disponible.html usa los textos del catálogo y no carga nada externo."""

import re
from pathlib import Path

from dominio.mensajes import mensaje

PAGINA = Path(__file__).resolve().parents[2] / "infra" / "no-disponible.html"


def test_textos_del_catalogo():
    contenido = PAGINA.read_text(encoding="utf-8")
    assert mensaje("gral.no_disponible") in contenido
    assert mensaje("pie.legal") in contenido
    assert 'lang="es-AR"' in contenido


def test_sin_recursos_externos_y_con_ambos_temas():
    contenido = PAGINA.read_text(encoding="utf-8")
    assert not re.search(r'\b(?:src|href)=["\'](?:https?:)?//', contenido)
    assert "<link" not in contenido and "<script" not in contenido
    assert "@media (prefers-color-scheme: dark)" in contenido


def test_colores_iguales_a_los_tokens():
    """Los valores en línea son los de ui/tokens.css (tema claro, primer bloque)."""
    tokens = (PAGINA.parents[1] / "ui" / "tokens.css").read_text(encoding="utf-8")
    pagina = PAGINA.read_text(encoding="utf-8")
    claro_pagina = dict(re.findall(r"(--q-[\w-]+):\s*(#[0-9a-f]{6})", pagina.split("@media")[0]))
    claro_tokens = dict(re.findall(r"(--q-[\w-]+):\s*(#[0-9a-f]{6})", tokens.split("}")[0]))
    assert claro_pagina and all(claro_tokens[k] == v for k, v in claro_pagina.items())


def test_500_estatica_con_los_textos_del_catalogo():
    """templates/500.html no usa etiquetas (debe funcionar aunque falle todo lo demás): sus textos
    se comparan aquí con el catálogo, igual que los de Next.js (frontend/src/app/error.tsx)."""
    contenido = (PAGINA.parents[1] / "templates" / "500.html").read_text(encoding="utf-8")
    for clave in ("gral.titulo_error", "gral.error", "gral.volver_resultados"):
        assert mensaje(clave) in contenido, clave
