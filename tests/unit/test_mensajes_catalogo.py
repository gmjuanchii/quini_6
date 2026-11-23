"""[003] R-13, HU-11: el catálogo único de textos coincide con los contratos de mensajes."""

import pytest

from dominio.mensajes import MENSAJES, mensaje
from tests.contrato_mensajes import catalogo_esperado


def test_el_catalogo_tiene_exactamente_las_claves_de_los_contratos():
    esperado = catalogo_esperado()
    faltan = sorted(set(esperado) - set(MENSAJES))
    sobran = sorted(set(MENSAJES) - set(esperado))
    assert not faltan, f"Claves del contrato que faltan en dominio/mensajes.py: {faltan}"
    assert not sobran, f"Claves de dominio/mensajes.py que no están en ningún contrato: {sobran}"


def test_cada_texto_es_identico_al_del_contrato():
    esperado = catalogo_esperado()
    distintos = {k: (MENSAJES[k], v) for k, v in esperado.items() if MENSAJES.get(k) != v}
    assert not distintos, distintos


def test_mensaje_completa_las_variables():
    assert mensaje("jugada.faltan", n=2) == "Faltan 2 números"
    assert mensaje("pag.pagina", n=1, m=15) == "Página 1 de 15"


def test_mensaje_sin_variables_devuelve_el_texto():
    assert mensaje("nav.menu") == "Menú"


def test_clave_inexistente_es_un_error():
    with pytest.raises(KeyError):
        mensaje("no.existe")
