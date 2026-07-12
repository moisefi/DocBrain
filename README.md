# DocBrain

DocBrain es un backend SaaS multi-tenant para consulta inteligente de
documentacion empresarial mediante RAG verificable.

El objetivo del proyecto es demostrar competencias de AI Engineering y Backend
Engineering en un caso realista: ingestion de documentos, recuperacion
semantica, respuestas con citas, aislamiento estricto entre organizaciones,
observabilidad y evaluacion continua de calidad.

## Propuesta tecnica

- RAG privado sobre documentacion interna.
- Respuestas fundamentadas con citas verificables por fragmento.
- Multi-tenant obligatorio desde el modelo de datos hasta los casos de uso.
- Pipeline de ingestion asincrono con estados auditables.
- Abstraccion de modelos mediante LiteLLM.
- Evaluacion automatizada de retrieval, grounding y calidad de citas.
- Observabilidad de negocio, infraestructura y comportamiento LLM.

## Stack previsto

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Pydantic v2
- Alembic
- PostgreSQL 17 + pgvector
- Redis + Celery
- MinIO en desarrollo, S3 en produccion
- LiteLLM
- OpenTelemetry + Prometheus
- Docker Compose
- Ruff, MyPy y Pytest

## MVP

El MVP no intenta ser una plataforma enterprise completa. Debe demostrar un
flujo end-to-end robusto:

1. Registro, login y refresh tokens rotatorios.
2. Organizaciones, membresias y roles.
3. Knowledge bases aisladas por tenant.
4. Subida de documentos PDF/Markdown/Text.
5. Ingestion asincrona con extraccion, chunking, embeddings y almacenamiento.
6. Chat con retrieval, reranking, respuesta grounded y citas.
7. Auditoria de acciones sensibles.
8. Metricas y trazas del pipeline RAG.
9. Suite de tests unitarios, integracion y evaluacion RAG.

## Documentacion

- [Product Specification](PRODUCT_SPEC.md)
- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Database](docs/database.md)
- [RAG](docs/rag.md)
- [Security](SECURITY.md)
- [Deployment](docs/deployment.md)
- [Roadmap](ROADMAP.md)

