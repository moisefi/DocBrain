# API

La API se versiona bajo `/api/v1`. Los endpoints no contienen logica de
negocio; delegan en casos de uso de la capa `application`.

## Convenciones

- Autenticacion mediante `Authorization: Bearer <access_token>`.
- `organization_id` se resuelve desde ruta, token o contexto activo segun el
  endpoint.
- Respuestas de error con formato estable:

```json
{
  "code": "tenant_access_denied",
  "message": "The requested resource is not available for this organization.",
  "correlation_id": "01HX..."
}
```

## Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

Requisitos:

- Password hashing con Argon2id.
- Refresh tokens rotatorios.
- Revocacion de familias de refresh token ante reutilizacion sospechosa.

## Organizations

- `POST /organizations`
- `GET /organizations`
- `GET /organizations/{organization_id}`
- `POST /organizations/{organization_id}/members`
- `PATCH /organizations/{organization_id}/members/{user_id}`
- `DELETE /organizations/{organization_id}/members/{user_id}`

Roles iniciales:

- `owner`
- `admin`
- `editor`
- `viewer`

## Knowledge Bases

- `POST /organizations/{organization_id}/knowledge-bases`
- `GET /organizations/{organization_id}/knowledge-bases`
- `GET /organizations/{organization_id}/knowledge-bases/{knowledge_base_id}`
- `PATCH /organizations/{organization_id}/knowledge-bases/{knowledge_base_id}`
- `DELETE /organizations/{organization_id}/knowledge-bases/{knowledge_base_id}`

## Documents

- `POST /organizations/{organization_id}/knowledge-bases/{knowledge_base_id}/documents`
- `GET /organizations/{organization_id}/knowledge-bases/{knowledge_base_id}/documents`
- `GET /organizations/{organization_id}/documents/{document_id}`
- `GET /organizations/{organization_id}/documents/{document_id}/versions`
- `DELETE /organizations/{organization_id}/documents/{document_id}`

La subida crea una version documental y encola ingestion. El endpoint devuelve
`202 Accepted` cuando el procesamiento queda pendiente.

## Ingestion

- `GET /organizations/{organization_id}/documents/{document_id}/ingestion-status`
- `POST /organizations/{organization_id}/documents/{document_id}/reingest`

Los reintentos deben ser idempotentes. Solo versiones en estado `failed` o
documentos con extractor actualizado deberian reingestarse manualmente.

## Conversations

- `POST /organizations/{organization_id}/conversations`
- `GET /organizations/{organization_id}/conversations`
- `GET /organizations/{organization_id}/conversations/{conversation_id}`
- `POST /organizations/{organization_id}/conversations/{conversation_id}/messages`

La respuesta de mensajes puede ser streaming. Cada mensaje generado incluye:

- Texto de respuesta.
- Citas normalizadas.
- Chunks recuperados internamente para auditoria.
- Metricas de tokens, latencia y proveedor.
- Indicador `insufficient_evidence` cuando no hay contexto fiable.

## Usage

- `GET /organizations/{organization_id}/usage`
- `GET /organizations/{organization_id}/usage/llm`
- `GET /organizations/{organization_id}/usage/ingestion`

## Audit

- `GET /organizations/{organization_id}/audit-events`

Eventos minimos:

- Login y logout.
- Refresh token reutilizado.
- Cambios de membresia y roles.
- Subida, borrado y reingestion de documentos.
- Consultas a knowledge bases.
- Cambios de configuracion sensible.

## Health

- `GET /health/live`
- `GET /health/ready`

`ready` valida conectividad con PostgreSQL, Redis y object storage. No debe
invocar proveedores LLM externos.

