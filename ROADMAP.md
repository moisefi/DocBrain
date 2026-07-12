# Roadmap

## F0 - Base tecnica

- `pyproject.toml` con uv, Ruff, MyPy y Pytest.
- Estructura `src/` por modulos.
- Docker Compose con PostgreSQL, Redis y MinIO.
- Configuracion por variables de entorno.
- Health checks.

Definition of Done:

- API arranca localmente.
- Ruff, MyPy y Pytest ejecutan en CI.
- Migraciones Alembic iniciales funcionan.

## F1 - Auth y multi-tenancy

- Registro y login.
- Argon2id.
- JWT access token.
- Refresh token rotatorio.
- Organizaciones, membresias y roles.
- TenantContext en casos de uso.

Definition of Done:

- Tests de acceso cruzado entre tenants.
- Auditoria de login y cambios de membresia.
- Reutilizacion de refresh token revoca la familia.

## F2 - Gestion documental

- Knowledge bases.
- Subida de documentos.
- Object storage.
- Versiones documentales.
- Estados de ingestion.

Definition of Done:

- Subida idempotente por hash.
- Validacion de MIME type y tamano.
- Tests de permisos por rol.

## F3 - Ingestion

- Worker Celery.
- Extractores PDF, Markdown y texto.
- Chunking con metadata.
- Embeddings.
- Persistencia en pgvector.

Definition of Done:

- Reintentos no duplican chunks activos.
- Estado de ingestion auditable.
- Tests de chunking e ingestion.

## F4 - RAG MVP

- Retrieval vectorial con filtros tenant-scoped.
- Prompt grounded.
- Streaming de respuesta.
- Citas verificables.
- Abstencion por evidencia insuficiente.

Definition of Done:

- No hay fugas entre tenants en retrieval.
- Respuestas con citas se persisten.
- Golden tests basicos pasan.

## F5 - Evaluacion y observabilidad

- Dataset de evaluacion.
- Recall@k, MRR/nDCG y citation accuracy.
- Logs estructurados.
- OpenTelemetry.
- Metricas de coste, latencia y tokens.

Definition of Done:

- Evaluacion RAG ejecuta en CI.
- Dashboard basico de metricas.
- Trazas cubren ingestion y consulta.

## F6 - Hardening

- Rate limiting.
- Politicas anti prompt injection.
- Auditoria ampliada.
- Tests de seguridad.
- Documentacion de amenazas.

Definition of Done:

- Casos adversariales cubiertos.
- Errores no exponen detalles sensibles.
- Checklist OWASP documentado.

## F7 - Produccion

- Imagen Docker.
- Despliegue objetivo AWS ECS.
- RDS + pgvector.
- ElastiCache.
- S3.
- Secrets Manager/SSM.

Definition of Done:

- Smoke tests post-deploy.
- Backups documentados.
- Runbook operativo inicial.

## F8 - Extensiones

- Hybrid search.
- Reranking medido.
- Conectores externos.
- SSO.
- Facturacion.
- MCP si aporta valor real.

