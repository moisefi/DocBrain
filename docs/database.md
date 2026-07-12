# Database

PostgreSQL 17 es la fuente de verdad del sistema. pgvector se usa para
almacenar embeddings y ejecutar recuperacion vectorial con filtros por tenant.

## Entidades principales

### Identity

- `users`
- `password_credentials`
- `refresh_token_families`
- `refresh_tokens`

### Tenancy

- `organizations`
- `memberships`
- `roles`

### Knowledge

- `knowledge_bases`
- `documents`
- `document_versions`
- `document_chunks`
- `chunk_embeddings`

### Conversations

- `conversations`
- `messages`
- `message_citations`
- `retrieval_runs`
- `retrieval_run_chunks`

### Operations

- `ingestion_jobs`
- `audit_events`
- `usage_events`
- `llm_calls`
- `evaluation_runs`
- `evaluation_cases`

## Reglas de multi-tenancy

Tablas tenant-scoped:

- `memberships`
- `knowledge_bases`
- `documents`
- `document_versions`
- `document_chunks`
- `conversations`
- `messages`
- `audit_events`
- `usage_events`
- `evaluation_runs`

Cada tabla tenant-scoped incluye `organization_id`. Las foreign keys deben
mantener consistencia con la organizacion propietaria.

## Modelo documental

Un `document` representa el recurso logico. Un `document_version` representa el
contenido procesable en un momento concreto.

Campos relevantes de `document_versions`:

- `id`
- `organization_id`
- `document_id`
- `storage_bucket`
- `storage_key`
- `content_hash`
- `mime_type`
- `status`
- `error_code`
- `created_at`

`content_hash` permite evitar ingestion duplicada.

## Chunks

Campos relevantes de `document_chunks`:

- `id`
- `organization_id`
- `document_version_id`
- `chunk_index`
- `content`
- `token_count`
- `page_number`
- `section_title`
- `start_offset`
- `end_offset`
- `metadata`

Campos relevantes de `chunk_embeddings`:

- `chunk_id`
- `organization_id`
- `embedding_model`
- `embedding vector`
- `created_at`

El indice vectorial debe combinar `organization_id`, `embedding_model` y vector
para evitar recuperacion accidental entre tenants o modelos incompatibles.

## Conversaciones y citas

Cada `message_citation` debe guardar:

- `message_id`
- `document_id`
- `document_version_id`
- `chunk_id`
- `quoted_text`
- `page_number`
- `score`

Esto permite auditar si una respuesta esta respaldada por el contenido citado.

## Auditoria

`audit_events` debe ser append-only desde la aplicacion. Campos minimos:

- `organization_id`
- `actor_user_id`
- `action`
- `resource_type`
- `resource_id`
- `ip_address`
- `user_agent`
- `correlation_id`
- `metadata`
- `created_at`

## Indices iniciales

- `memberships(user_id, organization_id)`
- `knowledge_bases(organization_id)`
- `documents(organization_id, knowledge_base_id)`
- `document_versions(organization_id, document_id, status)`
- `document_chunks(organization_id, document_version_id)`
- `chunk_embeddings(organization_id, embedding_model)`
- indice vectorial pgvector sobre `chunk_embeddings.embedding`
- `messages(organization_id, conversation_id, created_at)`
- `audit_events(organization_id, created_at)`

## Migraciones

Todas las modificaciones de esquema se versionan con Alembic. Las migraciones
que afecten a datos tenant-scoped deben incluir pruebas de integridad y, cuando
aplique, estrategia de backfill.

