# Architecture

## Estilo arquitectonico

DocBrain adopta un monolito modular. La prioridad es mantener bajo el coste
operacional mientras se preservan limites internos claros entre dominio,
aplicacion e infraestructura.

Cada modulo expone casos de uso y modelos propios. Los endpoints FastAPI solo
validan entrada, resuelven dependencias y delegan en casos de uso.

## Capas

- `api`: routers, schemas HTTP, dependencias y manejo de errores.
- `application`: casos de uso, DTOs internos y transacciones.
- `domain`: entidades, value objects, politicas y errores de negocio.
- `infrastructure`: SQLAlchemy, LiteLLM, Redis, Celery, MinIO/S3 y pgvector.
- `observability`: logging, tracing, metricas y correlacion de requests.

## Dependencias

```mermaid
flowchart TD
    API[FastAPI API] --> APP[Application use cases]
    APP --> DOMAIN[Domain]
    APP --> PORTS[Ports]
    INFRA[Infrastructure adapters] --> PORTS
    INFRA --> DB[(PostgreSQL + pgvector)]
    INFRA --> REDIS[(Redis)]
    INFRA --> OBJECTS[(MinIO/S3)]
    INFRA --> LITELLM[LiteLLM]
    LITELLM --> PROVIDERS[OpenAI / Anthropic / Ollama]
```

La capa de dominio no depende de FastAPI, SQLAlchemy, Celery ni proveedores LLM.

## Flujo de ingestion

```mermaid
sequenceDiagram
    participant User
    participant API
    participant UC as UploadDocumentUseCase
    participant S3 as Object Storage
    participant Q as Celery Queue
    participant Worker
    participant DB as PostgreSQL/pgvector

    User->>API: POST /documents
    API->>UC: validate tenant and permissions
    UC->>S3: store original file
    UC->>DB: create document version PENDING
    UC->>Q: enqueue ingestion job
    Worker->>S3: load original
    Worker->>Worker: extract, normalize, chunk
    Worker->>Worker: generate embeddings
    Worker->>DB: persist chunks and vectors
    Worker->>DB: mark version READY or FAILED
```

## Flujo de consulta

```mermaid
sequenceDiagram
    participant User
    participant API
    participant ChatUC as AskQuestionUseCase
    participant Retriever
    participant LLM
    participant DB

    User->>API: POST /conversations/{id}/messages
    API->>ChatUC: authenticated tenant context
    ChatUC->>Retriever: retrieve authorized chunks
    Retriever->>DB: vector/hybrid search with tenant filters
    Retriever-->>ChatUC: ranked context
    ChatUC->>LLM: grounded prompt with citations contract
    LLM-->>ChatUC: answer stream
    ChatUC->>DB: persist message, citations and usage
    ChatUC-->>API: streamed answer
```

## Multi-tenancy

El `organization_id` es obligatorio en entidades de negocio compartidas. Todos
los casos de uso reciben un `TenantContext` con usuario, organizacion, roles y
correlation id.

Las consultas a datos tenant-scoped deben filtrar por `organization_id`. Las
politicas de dominio validan membresia y rol antes de ejecutar acciones
sensibles. Los tests de integracion deben cubrir intentos de acceso cruzado
entre organizaciones.

## Jobs asincronos

Celery se usa para ingestion porque la extraccion, chunking y embeddings pueden
ser lentos y reintentables. Cada job debe ser idempotente por
`document_version_id`; un reintento no debe duplicar chunks activos.

Estados de ingestion:

- `pending`
- `extracting`
- `chunking`
- `embedding`
- `ready`
- `failed`

## Observabilidad

Cada request y job debe incluir `correlation_id`, `organization_id`,
`user_id` cuando aplique y `document_id` o `conversation_id` cuando exista.

Metricas minimas:

- Latencia HTTP por endpoint.
- Duracion de ingestion por fase.
- Numero de chunks por documento.
- Latencia de retrieval y generacion.
- Tokens de entrada/salida.
- Errores por proveedor LLM.
- Consultas sin evidencia suficiente.

## Principales tradeoffs

- Monolito modular frente a microservicios: menor complejidad inicial y mejor
  velocidad de desarrollo, con limites internos verificables por tests.
- pgvector frente a vector database dedicada: menos piezas operacionales para
  el MVP y suficiente para demostrar retrieval, filtros y evaluacion.
- LiteLLM frente a SDKs directos: permite cambiar proveedor y registrar costes
  sin acoplar los casos de uso al modelo concreto.
- Celery frente a background tasks de FastAPI: mejor control de reintentos,
  workers y observabilidad de jobs largos.

