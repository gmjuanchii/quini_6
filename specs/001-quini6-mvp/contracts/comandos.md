# Contrato de comandos de gestión

**Plan**: [../plan.md](../plan.md) | **Decisión**: [../research.md](../research.md) R-05b

Los comandos solo se ejecutan desde el servidor, con acceso de operador. No hay ninguna interfaz web equivalente (RN-37).

| Comando | Argumentos | Efecto | Salida | Requisito |
|---------|------------|--------|--------|-----------|
| `python manage.py otorgar_admin <correo>` | Correo de una cuenta existente. | Pone `es_administrador = True`. | "Se otorgó el permiso de administrador a <correo>." Si la cuenta no existe: "No existe una cuenta con el correo <correo>." (código de salida 1). | RN-37 |
| `python manage.py quitar_admin <correo>` | Correo de una cuenta existente. | Pone `es_administrador = False`. | Mensajes equivalentes. | RN-37 |

No se crea ningún comando de importación ni de carga masiva de resultados (FR-010). Los datos de prueba de los ejemplos de referencia existen solo como *fixtures* de `pytest` y nunca se cargan en producción.
