# Product Specification

## Vision

DocBrain permite a organizaciones consultar documentacion interna mediante un
asistente IA privado que responde solo con informacion recuperada de fuentes
autorizadas y devuelve citas verificables.

El proyecto esta pensado como portfolio de AI Engineer: no basta con llamar a
un LLM. Debe demostrar ingestion documental, retrieval, evaluacion, seguridad
multi-tenant, observabilidad y criterios claros de calidad.

## Problema

Las empresas acumulan documentacion en manuales, procedimientos, politicas,
wikis y documentos operativos. Buscar informacion es lento, las respuestas de
un LLM sin contexto no son confiables y una fuga entre clientes seria critica.

DocBrain resuelve este problema con un backend que:

- Indexa documentacion por organizacion y knowledge base.
- Recupera fragmentos relevantes con filtros de permisos.
- Genera respuestas grounded con citas.
- Rechaza o marca respuestas cuando no hay evidencia suficiente.
- Mide la calidad del retrieval y de las citas.

## Usuarios

- Administrador de organizacion: gestiona miembros, roles y knowledge bases.
- Editor: sube documentos y revisa estados de ingestion.
- Usuario interno: consulta documentacion autorizada mediante conversaciones.
- Operador tecnico: revisa auditoria, metricas, errores y costes.

## Alcance del MVP

### Incluido

- Autenticacion con Argon2id, JWT access token y refresh token rotatorio.
- Organizaciones, membresias y roles basicos.
- Knowledge bases aisladas por tenant.
- Subida de PDF, Markdown y texto plano.
- Almacenamiento de originales en MinIO/S3.
- Pipeline asincrono: extraccion, normalizacion, chunking, embeddings,
  persistencia en pgvector y estado de ingestion.
- Retrieval hibrido: vector search + filtros por tenant + metadata.
- Reranking opcional cuando aporte mejora medible.
- Chat con streaming, citas y umbral minimo de evidencia.
- Auditoria de login, subida, ingestion, consulta y cambios de permisos.
- Observabilidad con logs estructurados, trazas y metricas.
- Evaluacion RAG con preguntas doradas y regresiones automatizadas.

### Fuera del MVP

- Frontend completo.
- SSO/SAML.
- Workflows complejos de aprobacion documental.
- Fine-tuning.
- Agentes autonomos.
- Conectores externos tipo Google Drive, Notion o SharePoint.
- Facturacion real.

## Modulos

- `auth`: identidad, passwords, sesiones y refresh tokens.
- `organizations`: tenants, membresias y roles.
- `knowledge_bases`: colecciones documentales por tenant.
- `documents`: metadatos, versiones y almacenamiento de originales.
- `ingestion`: jobs asincronos, extraccion, chunking y embeddings.
- `retrieval`: busqueda, filtros, reranking y seleccion de contexto.
- `llm`: prompts, LiteLLM, streaming y politicas de respuesta.
- `conversations`: hilos, mensajes y citas.
- `audit`: eventos sensibles y trazabilidad.
- `usage`: consumo, latencia, tokens y costes estimados.
- `evaluation`: datasets, golden questions y metricas RAG.

## Requisitos funcionales

- Un usuario solo puede acceder a datos de organizaciones donde tiene
  membresia activa.
- Cada documento pertenece a una unica knowledge base.
- Cada chunk conserva trazabilidad hacia documento, version, pagina/seccion y
  offsets cuando el extractor lo permita.
- Una respuesta debe incluir citas cuando use informacion documental.
- Si el retrieval no supera el umbral de evidencia, el sistema debe responder
  que no tiene informacion suficiente.
- Los jobs de ingestion deben ser idempotentes y reintentables.

## Requisitos no funcionales

- Tipado estricto con MyPy.
- Separacion entre endpoints, casos de uso e infraestructura.
- Tests unitarios para reglas de negocio.
- Tests de integracion para API, base de datos y pipeline principal.
- Evaluacion RAG reproducible en CI.
- Logs sin secretos ni contenido sensible innecesario.
- Limites de tamano, tipo y frecuencia para subida de documentos.

## Criterios de calidad AI

- Recall@k sobre dataset de evaluacion.
- MRR o nDCG para ranking de chunks.
- Citation accuracy: las citas deben respaldar la frase generada.
- Faithfulness: la respuesta no debe introducir informacion no recuperada.
- Abstention rate controlado cuando no hay evidencia suficiente.
- Latencia p95 separada para retrieval, reranking y generacion.
- Coste estimado por consulta.

## Criterios de exito del portfolio

El proyecto debe permitir explicar en una entrevista:

- Como se garantiza aislamiento entre tenants.
- Como se evita mezclar logica de negocio con FastAPI.
- Como se disena y evalua un pipeline RAG.
- Como se monitoriza calidad, coste y latencia de un sistema LLM.
- Que tradeoffs se han tomado entre simplicidad, seguridad y escalabilidad.

