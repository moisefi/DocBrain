# AGENTS

## Reglas

- Presentar un plan antes de cambios grandes.
- Trabajar con cambios pequenos e incrementales.
- Mantener el proyecto ejecutable.
- Ejecutar Ruff, MyPy y Pytest antes de finalizar cambios de codigo.
- Para cambios solo de documentacion, revisar consistencia y enlaces.

## Arquitectura

- Monolito modular.
- No mezclar logica de negocio con endpoints.
- Casos de uso desacoplados de infraestructura.
- Dominio sin dependencias de FastAPI, SQLAlchemy, Celery ni proveedores LLM.
- Infraestructura implementa puertos definidos por la aplicacion.

## Seguridad

- Argon2id.
- JWT + refresh token rotatorio.
- Multi-tenant obligatorio.
- Secrets por variables de entorno o gestor de secretos.
- Validacion de permisos en casos de uso.
- Auditoria para acciones sensibles.

## IA

- LiteLLM como capa de abstraccion.
- pgvector para recuperacion.
- LangGraph solo cuando aporte valor demostrable.
- RAG con citas verificables.
- Evaluacion con golden questions, retrieval metrics y citation accuracy.
- Mitigaciones contra prompt injection.

## Definition of Done

- Tests OK cuando haya codigo ejecutable.
- Lint OK cuando haya codigo ejecutable.
- Typecheck OK cuando haya codigo ejecutable.
- Documentacion actualizada.
- Riesgos y tradeoffs documentados cuando afecten arquitectura.

