# RAG

DocBrain usa Retrieval-Augmented Generation para responder preguntas sobre
documentacion privada sin depender de memoria del modelo.

## Objetivos

- Responder solo con informacion recuperada de documentos autorizados.
- Incluir citas que permitan verificar la respuesta.
- Rechazar preguntas cuando no exista evidencia suficiente.
- Medir la calidad del retrieval y del grounding de forma reproducible.

## Pipeline de ingestion

1. Validar tipo, tamano y permisos del documento.
2. Guardar original en object storage.
3. Extraer texto y estructura.
4. Normalizar contenido.
5. Dividir en chunks con metadata.
6. Generar embeddings.
7. Persistir chunks y vectores.
8. Marcar version como `ready` o `failed`.

## Extraccion

Extractores iniciales:

- PDF con paginas y offsets cuando sea posible.
- Markdown conservando encabezados.
- Texto plano.

Cada extractor devuelve un documento normalizado con bloques, metadata y
posiciones. Si no se puede extraer texto suficiente, la ingestion falla con un
codigo auditable.

## Chunking

El chunking debe conservar contexto sin mezclar documentos. Configuracion
inicial:

- Tamano objetivo: 500-900 tokens.
- Overlap: 80-150 tokens.
- Separadores preferidos: encabezados, parrafos, listas y paginas.
- Metadata obligatoria: documento, version, pagina/seccion, indice y hash.

El chunking no debe romper tablas o listas de forma innecesaria si el extractor
puede detectarlas.

## Embeddings

Los embeddings se generan mediante LiteLLM o adaptador compatible. El modelo de
embedding queda guardado junto al vector para evitar comparar vectores de
modelos distintos.

La reingestion por cambio de modelo debe crear nuevos embeddings y mantener
trazabilidad con la version documental.

## Retrieval

Estrategia inicial:

1. Aplicar filtros obligatorios por `organization_id`, `knowledge_base_id` y
   permisos.
2. Ejecutar vector search en pgvector.
3. Combinar con busqueda textual cuando aporte mejora medible.
4. Aplicar metadata filtering.
5. Reranking opcional sobre candidatos top-k.
6. Seleccionar contexto final con limite de tokens.

Parametros iniciales:

- `candidate_k`: 30
- `final_k`: 5-8
- `min_relevance_score`: definido por evaluacion
- `max_context_tokens`: dependiente del modelo generativo

## Prompt contract

El prompt del sistema debe exigir:

- Usar solo el contexto recuperado.
- Citar afirmaciones documentales.
- No inventar datos ausentes.
- Indicar falta de evidencia cuando el contexto no baste.
- Mantener separada la respuesta del listado de citas.

El caso de uso valida que la respuesta final incluya citas cuando el modelo use
contenido documental. Si no hay chunks relevantes, no se llama al LLM salvo para
redactar una abstencion controlada.

## Citas

Cada cita debe apuntar a:

- Documento.
- Version.
- Chunk.
- Pagina o seccion si existe.
- Texto citado o span representativo.
- Score de retrieval/reranking.

Las citas deben respaldar frases concretas, no solo documentos generales.

## Mitigacion de prompt injection

- Separar instrucciones del sistema, pregunta del usuario y contexto recuperado.
- Tratar documentos como datos no confiables.
- Ignorar instrucciones encontradas dentro de documentos.
- No revelar prompts, secretos, tokens ni configuracion interna.
- Registrar intentos de extraccion de informacion sensible.

## Evaluacion

El repositorio debe incluir un dataset pequeno pero realista:

- Preguntas con respuesta presente.
- Preguntas ambiguas.
- Preguntas sin respuesta en la documentacion.
- Preguntas que requieren combinar varios chunks.
- Casos adversariales con instrucciones maliciosas dentro del documento.

Metricas:

- Recall@k.
- MRR o nDCG.
- Citation accuracy.
- Faithfulness.
- Answer relevance.
- Abstention accuracy.
- Latencia p95 por fase.
- Coste estimado por pregunta.

## Tests esperados

- Unit tests de chunking.
- Unit tests de filtros tenant-scoped.
- Integration tests de ingestion.
- Integration tests de retrieval con pgvector.
- Golden tests de respuestas con citas.
- Regression tests para evitar fugas entre tenants.

## Criterio de aceptacion

Una respuesta RAG es aceptable si:

- Recupera al menos una cita relevante.
- La respuesta no contradice las fuentes.
- Cada afirmacion factual importante esta respaldada.
- El sistema se abstiene cuando no hay evidencia suficiente.
- No se filtra informacion de otra organizacion.

