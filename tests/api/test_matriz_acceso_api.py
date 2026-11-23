"""[003] contracts/api.md § 4: toda operación de /api/v1/ tiene su nivel de acceso declarado.

Cada pantalla que agrega operaciones agrega sus filas a NIVEL_ESPERADO (Const. IV).
"""

import pytest

from quini6.api import api

#: (método, ruta) → nivel: P público, U usuario registrado, A administrador.
NIVEL_ESPERADO: dict[tuple[str, str], str] = {
    ("GET", "/sesion/"): "P",
    ("POST", "/sesion/"): "P",  # [003] pantalla 5 (T198)
    ("DELETE", "/sesion/"): "U",
    ("POST", "/cuentas/"): "P",
    ("GET", "/avisos/"): "P",  # [003] R-31
    ("POST", "/avisos/"): "P",
    # [003] pantallas 1 y 2: el nivel A de ?formulario=extraccion se prueba en su archivo.
    ("GET", "/periodos/atajos/"): "P",
    # [003] pantalla 1 (T173)
    ("GET", "/extracciones/"): "A",
    ("POST", "/extracciones/"): "A",
    ("GET", "/extracciones/{id}/"): "A",
    ("DELETE", "/extracciones/{id}/"): "A",
    ("GET", "/extracciones/{id}/avance/"): "A",
    ("GET", "/extracciones/{id}/sorteos/{numero}/"): "A",
    # [003] pantalla 2 (T182)
    ("GET", "/estadisticas/"): "P",
    # [003] pantalla 3 (T188)
    ("GET", "/jugadas/"): "U",
    ("POST", "/jugadas/"): "U",
    ("GET", "/jugadas/sorteos-disponibles/"): "U",
    ("GET", "/jugadas/{id}/"): "U",
    ("PUT", "/jugadas/{id}/"): "U",
    ("DELETE", "/jugadas/{id}/"): "U",
    # [003] R-12, AC-14.4
    ("POST", "/formularios/pendiente/"): "U",
    # [003] pantalla 4 (T194)
    ("GET", "/sorteos/ultimo/"): "P",
    ("GET", "/sorteos/"): "P",
    ("GET", "/sorteos/buscar/"): "P",
    ("GET", "/sorteos/{numero}/"): "P",
    # [003] pantalla 6 (T206)
    ("GET", "/admin/sorteos/"): "A",
    ("POST", "/admin/sorteos/"): "A",
    ("GET", "/admin/sorteos/nuevo/"): "A",
    ("GET", "/admin/sorteos/{numero}/"): "A",
    ("PUT", "/admin/sorteos/{numero}/"): "A",
    ("GET", "/admin/sorteos/{numero}/modificar/"): "A",
    ("GET", "/admin/sorteos/{numero}/historial/"): "A",
    ("GET", "/admin/sorteos/{numero}/{modalidad}/numeros/"): "A",
    ("PUT", "/admin/sorteos/{numero}/{modalidad}/numeros/"): "A",
    ("GET", "/admin/sorteos/{numero}/{modalidad}/premios/"): "A",
    ("PUT", "/admin/sorteos/{numero}/{modalidad}/premios/"): "A",
    ("POST", "/admin/sorteos/{numero}/{modalidad}/{bloque}/observar/"): "A",
    ("POST", "/admin/sorteos/{numero}/{modalidad}/{bloque}/resolver/"): "A",
    ("GET", "/admin/sorteos/{numero}/{modalidad}/{bloque}/publicar/"): "A",
    ("POST", "/admin/sorteos/{numero}/{modalidad}/{bloque}/publicar/"): "A",
    ("POST", "/admin/sorteos/{numero}/{modalidad}/{bloque}/revision/"): "A",
    ("POST", "/admin/sorteos/{numero}/{modalidad}/{bloque}/quitar-revision/"): "A",
    ("POST", "/admin/sorteos/{numero}/{modalidad}/{bloque}/corregir/"): "A",
}


def _operaciones():
    for prefijo, router in api._routers:
        for ruta, vista in router.path_operations.items():
            for operacion in vista.operations:
                completa = ("/" + "/".join(p for p in (prefijo, ruta) if p)).replace("//", "/")
                for metodo in operacion.methods:
                    yield metodo, completa, operacion


def test_toda_operacion_tiene_un_nivel_esperado_y_coincide():
    encontradas = {}
    for metodo, ruta, operacion in _operaciones():
        encontradas[(metodo, ruta)] = getattr(operacion.view_func, "nivel_quini6", None)
    assert encontradas, "La API no tiene operaciones"
    sin_fila = sorted(set(encontradas) - set(NIVEL_ESPERADO))
    assert not sin_fila, f"Operaciones sin fila en NIVEL_ESPERADO: {sin_fila}"
    distintos = {
        k: (v, NIVEL_ESPERADO[k]) for k, v in encontradas.items() if v != NIVEL_ESPERADO[k]
    }
    assert not distintos, distintos


@pytest.mark.parametrize(("metodo", "ruta"), [k for k, v in NIVEL_ESPERADO.items() if v != "P"])
def test_niveles_u_y_a_rechazan_a_visitantes(visitante, metodo, ruta):
    if "{" in ruta:
        pytest.skip("Las rutas con parámetros se prueban en el archivo de su pantalla")
    respuesta = visitante.generic(metodo, "/api/v1" + ruta)
    assert respuesta.status_code in (401, 403)


@pytest.mark.parametrize(("metodo", "ruta"), [k for k, v in NIVEL_ESPERADO.items() if v == "A"])
def test_nivel_a_rechaza_a_usuarios(usuario, metodo, ruta):
    if "{" in ruta:
        pytest.skip("Las rutas con parámetros se prueban en el archivo de su pantalla")
    respuesta = usuario.generic(metodo, "/api/v1" + ruta)
    assert respuesta.status_code in (403,)
