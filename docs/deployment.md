# Deployment

## Desarrollo local

Docker Compose debe levantar los servicios necesarios para desarrollar el MVP:

- API FastAPI.
- PostgreSQL 17 con pgvector.
- Redis.
- Worker Celery.
- MinIO.
- Prometheus opcional.

Comandos previstos:

- `python -m pip install -e ".[dev]"` hasta incorporar `uv`
- `docker compose up -d`
- `alembic upgrade head`
- `pytest`
- `ruff check .`
- `mypy .`

## CI

GitHub Actions debe ejecutar:

- Ruff.
- MyPy.
- Pytest.
- Migraciones Alembic sobre base de datos temporal.
- Tests de integracion con PostgreSQL + pgvector.
- Evaluacion RAG sobre dataset pequeno.

El pipeline no debe requerir claves reales de proveedores LLM para pruebas
basicas; se usaran fakes o modelos locales cuando aplique.

## Produccion objetivo

Arquitectura AWS prevista:

- ECS Fargate para API y workers.
- RDS PostgreSQL con extension pgvector.
- ElastiCache Redis.
- S3 para documentos originales.
- ALB para trafico HTTP.
- CloudWatch/OpenTelemetry Collector para logs y trazas.
- Secrets Manager o SSM Parameter Store para secretos.

## Configuracion

Toda configuracion sensible se inyecta por variables de entorno:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `ARGON2_*`
- `OBJECT_STORAGE_*`
- `LITELLM_*`
- `OPENAI_API_KEY` o proveedor equivalente

## Estrategia de despliegue

Para el MVP:

1. Build de imagen Docker.
2. Ejecucion de migraciones.
3. Despliegue de API.
4. Despliegue de workers.
5. Health checks.
6. Smoke tests de autenticacion, ingestion y consulta.

## Backups y datos

- Backups automaticos de PostgreSQL.
- Versionado o lifecycle policies en S3.
- Separacion de buckets por entorno.
- Politica de retencion para auditoria y usage events.
