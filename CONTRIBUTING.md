# Contributing

## Flujo de trabajo

1. Crear una rama descriptiva.
2. Mantener cambios pequenos e incrementales.
3. Actualizar documentacion cuando cambie comportamiento o arquitectura.
4. Ejecutar validaciones antes de abrir PR:
   - `ruff check .`
   - `mypy .`
   - `pytest`
5. Crear PR con descripcion tecnica, riesgos y pruebas ejecutadas.

## Criterios de cambio

- Los endpoints no deben contener logica de negocio.
- Los casos de uso no deben depender de FastAPI.
- La infraestructura implementa puertos, no reglas de negocio.
- Toda entidad tenant-scoped debe validar `organization_id`.
- Los cambios RAG deben incluir o actualizar pruebas/evaluaciones.

